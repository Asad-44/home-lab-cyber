import os
import requests
from dotenv import load_dotenv

# Load variables from the .env file
load_dotenv()

# Retrieve the API key from the environment
API_KEY = os.getenv("ABUSEIPDB_API_KEY")
TARGET_IP = "8.8.8.8"  # The IP address we want to query (Google's Public DNS)

def check_ip_reputation(ip):
    # Ensure the API key is present
    if not API_KEY:
        print("[!] Error: ABUSEIPDB_API_KEY not found in .env file.")
        return

    # AbuseIPDB v2 API endpoint for checking an IP
    url = "https://api.abuseipdb.com/api/v2/check"

    # Set up the headers as specified in the AbuseIPDB API documentation
    headers = {
        "Key": API_KEY,
        "Accept": "application/json"
    }

    # Set up the query parameters
    params = {
        "ipAddress": ip,
        "maxAgeInDays": "90"  # Check reports over the last 90 days
    }

    print(f"[*] Querying AbuseIPDB for IP: {ip}...")

    try:
        # Perform the GET request
        response = requests.get(url, headers=headers, params=params)
        
        # Raise an exception if the response contains an HTTP error status code
        response.raise_for_status()
        
        # Parse the JSON response
        json_data = response.json()
        
        # Extract the nested threat intelligence data
        data = json_data.get("data", {})
        
        # Extract the specific fields needed for our milestone
        confidence_score = data.get("abuseConfidenceScore", 0)
        country_code = data.get("countryCode", "Unknown")
        total_reports = data.get("totalReports", 0)
        
        # Print the clean output
        print(f"\n[+] Threat Intelligence Results:")
        print(f"IP: {ip} | Abuse Score: {confidence_score}% | Country: {country_code} | Total Reports: {total_reports}")

    except requests.exceptions.HTTPError as http_err:
        print(f"[!] HTTP error occurred: {http_err}")
        print("[!] Please verify your API key is correct and valid.")
    except requests.exceptions.RequestException as req_err:
        print(f"[!] Network error occurred: {req_err}")

if __name__ == "__main__":
    check_ip_reputation(TARGET_IP)
