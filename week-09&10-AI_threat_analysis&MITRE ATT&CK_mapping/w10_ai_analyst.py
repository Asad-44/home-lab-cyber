import os
import warnings
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel

# Suppress non-blocking SDK warning logs for clean terminal output
warnings.filterwarnings("ignore", category=UserWarning, module="google")

# Load environment variables
load_dotenv()

# 1. Expand the Pydantic schema to enforce strict MITRE mapping
class MitreThreatAnalysis(BaseModel):
    severity: str
    mitre_tactic_name: str      # e.g., "Discovery" or "Credential Access"
    mitre_technique_id: str     # e.g., "T1046" or "T1110"
    mitre_technique_name: str   # e.g., "Network Service Discovery" or "Brute Force"
    suggested_action: str       # Immediate remediation advice

# Initialize the Gemini Client securely
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("[!] Error: GEMINI_API_KEY not found in .env file.")
    exit(1)

client = genai.Client(api_key=api_key)

# A mock Suricata alert representing Nmap port scanning activity we want analyzed
mock_alert = "Suricata Alert: Generic Protocol Command Decode error on Port 22"

# System instructions to define the role and taxonomy boundaries for the AI
system_instruction = (
    "You are an expert security operations center (SOC) analyst. "
    "Analyze the incoming network alert payload and map it precisely to the "
    "correct MITRE ATT&CK Tactic and Technique (including its standard T-code)."
)

def query_mitre_analyst(alert):
    print(f"[*] Analyzing alert: '{alert}'...")
    print("[*] Contacting Gemini MITRE Mapper...")
    
    try:
        # Query the model, passing the system role and structured schema configuration
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=alert,
            config={
                "system_instruction": system_instruction,
                "response_mime_type": "application/json",
                "response_schema": MitreThreatAnalysis,  # Enforces structural mapping
            }
        )
        
        # Access the parsed Pydantic object
        result: MitreThreatAnalysis = response.parsed
        
        print("\n[+] Structured MITRE ATT&CK Mapping Received:")
        print(f"Severity      : {result.severity}")
        print(f"Tactic        : {result.mitre_tactic_name}")
        print(f"Technique ID  : {result.mitre_technique_id}")
        print(f"Technique Name: {result.mitre_technique_name}")
        print(f"Suggested Action: {result.suggested_action}")
        
    except Exception as e:
        print(f"[!] Error querying Gemini API: {e}")

if __name__ == "__main__":
    query_mitre_analyst(mock_alert)
