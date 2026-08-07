import json
import time

# Path to Suricata's unified JSON output
LOG_FILE = "/var/log/suricata/eve.json"

def monitor_alerts():
    print("[*] Initializing Suricata Alert Monitor...")
    
    try:
        # Open the log file in read-only mode
        with open(LOG_FILE, "r") as f:
            # Move the file pointer to the very end of the file (tail behavior)
            # This prevents the script from printing thousands of old historical logs on startup
            f.seek(0, 2)
            print("[*] Monitoring active. Waiting for new alerts...\n")
            
            while True:
                line = f.readline()
                
                # If there is no new line, sleep briefly to prevent CPU hogging and try again
                if not line:
                    time.sleep(0.1)
                    continue
                
                try:
                    # Parse the raw text line into a Python dictionary
                    event = json.loads(line)
                    
                    # We are only interested in events where the type is "alert"
                    if event.get("event_type") == "alert":
                        timestamp = event.get("timestamp", "N/A")
                        src_ip = event.get("src_ip", "N/A")
                        dest_ip = event.get("dest_ip", "N/A")
                        signature = event.get("alert", {}).get("signature", "Unknown Signature")
                        
                        # Format the raw ISO timestamp (e.g., 2026-03-30T14:32:10.123456) for clean reading
                        clean_time = timestamp.split(".")[0].replace("T", " ")
                        
                        # Print the clean, formatted alert
                        print(f"[{clean_time}] ⚠️  ALERT: {signature} | Source: {src_ip} -> Destination: {dest_ip}")
                        
                except json.JSONDecodeError:
                    # Handles rare cases where a line is only partially written to disk
                    continue
                    
    except FileNotFoundError:
        print(f"[!] Error: {LOG_FILE} not found. Ensure Suricata is running.")
    except PermissionError:
        print(f"[!] Error: Permission denied. Run this script using 'sudo'.")
    except KeyboardInterrupt:
        print("\n[*] Stopping Alert Monitor. Exiting cleanly.")

if __name__ == "__main__":
    monitor_alerts()