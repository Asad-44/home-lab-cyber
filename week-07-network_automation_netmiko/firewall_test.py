import os
import re
from dotenv import load_dotenv
from netmiko import ConnectHandler

# Load configurations from the .env file
load_dotenv()

# Retrieve remote VM credentials securely from environment variables
UBUNTU_IP = os.getenv("UBUNTU_IP")
UBUNTU_USER = os.getenv("UBUNTU_USER")
UBUNTU_PASSWORD = os.getenv("UBUNTU_PASSWORD")

# Define the connection parameters for the remote Linux system
device = {
    "device_type": "linux",
    "host": UBUNTU_IP,
    "username": UBUNTU_USER,
    "password": UBUNTU_PASSWORD,
    "port": 22,  # Standard SSH Port (not 22222, as we are connecting to the Target VM, not the Attacker VM)
}

def run_remote_automation():
    # Validation check to ensure all credentials exist
    if not all([UBUNTU_IP, UBUNTU_USER, UBUNTU_PASSWORD]):
        print("[!] Error: Missing credentials in .env file.")
        return

    print(f"[*] Establishing SSH connection to {UBUNTU_IP}...")
    
    try:
        # Establish the connection
        with ConnectHandler(**device) as net_connect:
            print("[+] Connection established successfully.")
            
            # --- Test 1: Run a simple, read-only system command ---
            print("\n[*] Retrieving target system uptime...")
            uptime_output = net_connect.send_command("uptime", expect_string=r"\$")
            print(f"Uptime Result:\n{uptime_output}\n")
            
            # --- Test 2: Run a privileged firewall command requiring 'sudo' ---
            print("[*] Retrieving target iptables firewall configuration...")
            
            # Send the command using timing (ignores strict prompt matching)
            output = net_connect.send_command_timing("sudo iptables -L -n -v")
            
            # If the remote terminal asks for a password, send it
            if "password" in output.lower():
                output += net_connect.send_command_timing(UBUNTU_PASSWORD)
                
            print("\nActive Firewall Rules (iptables):")
            print(output)
            
    except Exception as e:
        print(f"[!] SSH Connection or execution failed: {e}")

if __name__ == "__main__":
    run_remote_automation()
