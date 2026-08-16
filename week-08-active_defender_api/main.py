import os
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, IPvAnyAddress
from netmiko import ConnectHandler

# Load configurations from the .env file
load_dotenv()

# Initialize the integrated FastAPI application
app = FastAPI(
    title="Active Defender API",
    description="Production-Grade Threat Intelligence and Network Security Remediation Engine.",
    version="3.0.0"
)

# Pydantic Model with strict IP address validation to prevent command injection
class IPPayload(BaseModel):
    ip: IPvAnyAddress  # Automatically rejects malformed inputs and command injections

# Helper: Query Threat Intelligence from AbuseIPDB
def get_abuse_score(ip: str):
    api_key = os.getenv("ABUSEIPDB_API_KEY")
    if not api_key:
        raise ValueError("AbuseIPDB API Key is missing in .env configuration.")
        
    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {
        "Key": api_key,
        "Accept": "application/json"
    }
    params = {
        "ipAddress": ip,
        "maxAgeInDays": "90"
    }
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    data = response.json().get("data", {})
    return {
        "score": data.get("abuseConfidenceScore", 0),
        "country": data.get("countryCode", "Unknown"),
        "isp": data.get("isp", "Unknown")
    }

# Helper: Block IP Remotely on the Target VM via Netmiko using Password
def apply_firewall_block(malicious_ip: str):
    ubuntu_ip = os.getenv("UBUNTU_IP")
    ubuntu_user = os.getenv("UBUNTU_USER")
    ubuntu_password = os.getenv("UBUNTU_PASSWORD")
    
    if not all([ubuntu_ip, ubuntu_user, ubuntu_password]):
        raise ValueError("SSH credentials or IP missing in .env configuration.")
        
    device = {
        "device_type": "linux",
        "host": ubuntu_ip,
        "username": ubuntu_user,
        "password": ubuntu_password,  # Authenticating with password
        "port": 22
    }
    
    # Sanitized commands (We still keep your duplication check and validation!)
    check_command = f"sudo iptables -C INPUT -s {malicious_ip} -j DROP"
    block_command = f"sudo iptables -A INPUT -s {malicious_ip} -j DROP"
    
    print(f"[*] Connecting to target VM at {ubuntu_ip} to apply firewall rule...")
    
    # Establish SSH Connection
    with ConnectHandler(**device) as net_connect:
        # Step 1: Check if rule already exists (uses timing to bypass escape codes)
        check_output = net_connect.send_command_timing(check_command)
        if "password" in check_output.lower():
            check_output += net_connect.send_command_timing(ubuntu_password)
            
        if "bad rule" not in check_output.lower() and "no match" not in check_output.lower():
            return "Rule already exists. Skipping duplication."
            
        # Step 2: Apply the block command
        block_output = net_connect.send_command_timing(block_command)
        if "password" in block_output.lower():
            block_output += net_connect.send_command_timing(ubuntu_password)
            
        return block_output if block_output else f"Successfully blocked IP {malicious_ip}"

@app.get("/")
def read_root():
    return {"status": "online", "message": "Active Defender API (v3.0) is running."}

@app.post("/remediate")
def remediate_ip(payload: IPPayload):
    # Pydantic validates the input, then we safely convert the IP object to a string
    target_ip = str(payload.ip)
    remediation_triggered = False
    firewall_log = ""
    
    # Step 1: Query Threat Intelligence
    try:
        intel = get_abuse_score(target_ip)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Threat Intelligence Query Failed: {e}")
        
    # Step 2: Evaluate and Decide
    if intel["score"] >= 50:
        remediation_triggered = True
        
        # Step 3: Execute Action
        try:
            firewall_log = apply_firewall_block(target_ip)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Remediation SSH Execution Failed: {e}")
            
    return {
        "status": "success",
        "ip_analyzed": target_ip,
        "abuse_confidence_score": f"{intel['score']}%",
        "country_code": intel["country"],
        "isp": intel["isp"],
        "remediation_triggered": remediation_triggered,
        "firewall_action_log": firewall_log if remediation_triggered else "No action taken (Reputation score is safe)."
    }
