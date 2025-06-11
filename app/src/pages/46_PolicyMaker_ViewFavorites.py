import json
import requests
import streamlit as st
from modules.nav import SideBarLinks
import logging

logger = logging.getLogger(__name__)

SideBarLinks()
user_id = st.session_state['user_id']
url = f"http://web-api:4000/politician/allpolicy/{user_id}"

saved_policies = requests.get(url).json()
count = 0
for item in saved_policies:
    count += 1
    id = int(item["saved_id"])
    policy_url = f"http://web-api:4000/politician/policy/{id}"

    st.markdown(f"<h4 style='margin-bottom:0;'>Policy #{count}</h4>", unsafe_allow_html=True)
    with st.expander(label=f'Expand Policy #{count}', expanded=False):
        policyJson = requests.get(policy_url).json()[0]
        col1, col2 = st.columns([4, 1], vertical_alignment="bottom")
        with col1:
            st.write(f'**Country:** {policyJson["Country"]}')
            st.write(f'**Discount Rate:** {policyJson["discountRate"]}%')
            st.write(f'**Federal Reserve Balance Sheet:** ${policyJson["FederalReserveBalanceSheet"]} Billion')
            st.write(f'**Treasury Holdings:** ${policyJson["TreasurySecurities"]} Billion')
            st.write(f'**Military Spending:** {policyJson["MilitarySpending"]}%')
            st.write(f'**Education Spending:** {policyJson["EducationSpending"]}%')
            st.write(f'**Health Spending:** {policyJson["HealthSpending"]}%')
        with col2:
            st.button(label="Modify", key=f"modify_{id}", use_container_width=True)
            if st.button(label="Publish", key=f"publish_{id}", use_container_width=True):
                try:
                    # Log the request data
                    request_data = {"saved_id": id, "user_id": user_id}
                    logger.info(f"Sending publish request with data: {request_data}")
                    
                    response = requests.post(
                        "http://web-api:4000/politician/publish",
                        json=request_data,
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    # Log the response
                    logger.info(f"Response status code: {response.status_code}")
                    logger.info(f"Response content: {response.text}")
                    
                    if response.status_code == 201:
                        st.success("Policy published successfully!")
                    elif response.status_code == 400:
                        error_msg = response.json().get("error", "Failed to publish policy")
                        st.error(f"Error: {error_msg}")
                    else:
                        st.error(f"Failed to publish policy. Status code: {response.status_code}")
                        st.error(f"Response: {response.text}")
                except requests.exceptions.RequestException as e:
                    logger.error(f"Request error: {str(e)}")
                    st.error(f"Network error: {str(e)}")
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {str(e)}")
                    st.error(f"Invalid response from server: {str(e)}")
                except Exception as e:
                    logger.error(f"Unexpected error: {str(e)}")
                    st.error(f"Error publishing policy: {str(e)}")

