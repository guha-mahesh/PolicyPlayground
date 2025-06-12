import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests
import pandas as pd

st.set_page_config(layout = 'wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()



try:
    # Get published policies
    response = requests.get("http://web-api:4000/politician/published")
    if response.status_code == 200:
        published_policies = response.json()
        
        if published_policies:
            st.markdown("""
                <div style='background: #1e293b; padding: 1.5rem; border-radius: 8px; margin: 2rem 0;'>
                    <h3 style='color: #e2e8f0; margin: 0 0 1rem 0;'>Published Policies</h3>
                    <p style='color: #94a3b8; margin: 0;'>Click on a policy to view its details</p>
                </div>
            """, unsafe_allow_html=True)

            for policy in published_policies:
                with st.expander(f"Published Policy #{policy['publish_id']} - {policy['Country']}", expanded=False):
                    col1, col2 = st.columns([4, 1], vertical_alignment="bottom")
                    with col1:
                        st.write(f'**Published Date:** {policy["publish_date"]}')
                        st.write(f'**Country:** {policy["Country"]}')
                        st.write(f'**Discount Rate:** {policy["discountRate"]}%')
                        st.write(f'**Federal Reserve Balance Sheet:** ${policy["FederalReserveBalanceSheet"]} Billion')
                        st.write(f'**Treasury Holdings:** ${policy["TreasurySecurities"]} Billion')
                        st.write(f'**Military Spending:** {policy["MilitarySpending"]}%')
                        st.write(f'**Education Spending:** {policy["EducationSpending"]}%')
                        st.write(f'**Health Spending:** {policy["HealthSpending"]}%')
                        st.write(f'**SP500 Prediction:** {policy["SP500"]:,.2f}')
                        st.write(f'**GDP Prediction:** {policy["GDP"]:,.2f}')
                    
                    with col2:
                        if st.button("View Analysis", key=f"analyze_{policy['publish_id']}", use_container_width=True):
                            st.switch_page("pages/44_Policy_Maker_viewPred.py")
                        if st.button("Unpublish", key=f"unpublish_{policy['publish_id']}", use_container_width=True):
                            try:
                                unpublish_response = requests.post(f"http://web-api:4000/politician/unpublish/{policy['publish_id']}")
                                if unpublish_response.status_code == 200:
                                    st.success("Policy unpublished successfully!")
                                    st.rerun()
                                else:
                                    st.error("Failed to unpublish policy")
                            except Exception as e:
                                st.error(f"Error unpublishing policy: {str(e)}")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.info("No published policies found.")
    else:
        st.error("Failed to fetch published policies")
except Exception as e:
    st.error(f"Error: {str(e)}")

st.write("---")

