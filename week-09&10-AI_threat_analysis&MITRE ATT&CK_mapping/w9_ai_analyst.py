import os
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# 1. Define the exact JSON structure we want the AI to return
class AnalysisResult(BaseModel):
    severity: str          # Expected: Low, Medium, High, or Critical
    suggested_action: str  # Expected: Short, actionable remediation step

# 2. Initialize the Gemini Client securely
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("[!] Error: GEMINI_API_KEY not found in .env file.")
    exit(1)

client = genai.Client(api_key=api_key)

# A mock threat scenario we want analyzed
prompt_scenario = "Our database server (192.168.100.41) is receiving over 5,000 connection attempts per minute from multiple unknown external IPs."

def query_ai_analyst(prompt):
    print("[*] Sending threat scenario to Gemini AI Analyst...")
    
    try:
        # Query the model, passing our Pydantic schema in the config
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": AnalysisResult,  # Enforces Pydantic structure
            }
        )
        
        # Access the pre-parsed Pydantic object directly
        result: AnalysisResult = response.parsed
        
        print("\n[+] Structured AI Analysis Received:")
        print(f"Severity level: {result.severity}")
        print(f"Action plan   : {result.suggested_action}")
        
    except Exception as e:
        print(f"[!] Error querying Gemini API: {e}")

if __name__ == "__main__":
    query_ai_analyst(prompt_scenario)
