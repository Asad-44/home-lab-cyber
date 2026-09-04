import streamlit as st
import requests

# 1. Define Backend API Configurations
BACKEND_URL = "http://127.0.0.1:8000"

# Set up page styling and tab headers
st.set_page_config(
    page_title="Active Defender Dashboard",
    page_icon="🛡️",
    layout="centered"
)

# 2. Main Title and Subheader
st.title("Active Defender Security Dashboard 🛡️")
st.write("Orchestrate Threat Intelligence Analysis and Automated Firewall Remediation.")

st.markdown("---")

# 3. Check Backend Connection Status
try:
    response = requests.get(f"{BACKEND_URL}/")
    if response.status_code == 200:
        st.sidebar.success("🟢 API Backend: ONLINE")
    else:
        st.sidebar.warning("🟡 API Backend: UNSTABLE (Status Code mismatch)")
except requests.exceptions.ConnectionError:
    st.sidebar.error("🔴 API Backend: OFFLINE")
    st.sidebar.info("Please start your FastAPI server in WSL using: `uvicorn main:app --reload`")

# 4. User Input Section
st.subheader("IP Remediation Panel")
st.write("Submit an IP address below. The backend will analyze its reputation on AbuseIPDB and block it on the target VM if its threat score exceeds 50%.")

target_ip = st.text_input("Target IP Address:", placeholder="e.g., 185.220.101.5")

# 5. Interactive Action Button
if st.button("Analyze & Approve Block", type="primary"):
    if not target_ip:
        st.warning("Please enter a valid IP address first.")
    else:
        # Show a loading spinner during API and SSH execution
        with st.spinner("Processing threat intelligence and applying firewall rule..."):
            try:
                # Construct the payload
                payload = {"ip": target_ip}
                
                # Make the POST request to our FastAPI server
                api_response = requests.post(f"{BACKEND_URL}/remediate", json=payload)
                
                if api_response.status_code == 200:
                    data = api_response.json()
                    st.success("Analysis and Remediation Sequence Completed!")
                    
                    # Create two column layouts to display the returned data cleanly
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Abuse Score", data.get("abuse_confidence_score"))
                        st.write(f"**Country Code:** {data.get('country_code')}")
                        st.write(f"**ISP:** {data.get('isp')}")
                    with col2:
                        remediation_status = "Rule Applied ✅" if data.get("remediation_triggered") else "No Action Required 🛡️"
                        st.write(f"**Remediation Status:** {remediation_status}")
                    
                    # Display the raw command log from our Netmiko SSH execution
                    st.markdown("### Firewall Execution Log:")
                    st.code(data.get("firewall_action_log"), language="bash")
                    
                else:
                    st.error(f"Error from Backend: {api_response.status_code}")
                    st.json(api_response.json())
                    
            except requests.exceptions.ConnectionError:
                st.error("Failed to connect to the backend server. Is your FastAPI server active?")
