import pandas as pd
import requests
from modules.nav import SideBarLinks
import streamlit as st
import logging
logger = logging.getLogger(__name__)


st.set_page_config(layout='wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.markdown("""
    <div style='background: linear-gradient(90deg, #1e3a8a 0%, #1e40af 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem;'>
        <h1 style='color: white; margin: 0;'>Published Policies 📢</h1>
        <p style='color: #94a3b8; margin: 0.5rem 0 0 0;'>View all published policies</p>
    </div>
""", unsafe_allow_html=True)

try:
    # Get published policies
    response = requests.get("http://web-api:4000/politician/publisher")
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
                with st.expander(f"Expand {policy['title']}", expanded=False):
                    col1, col2 = st.columns(
                        [4, 1], vertical_alignment="bottom")
                    with col1:
                        st.write(
                            f'**Published Date:** {policy["publish_date"]}')
                        st.write(f'**Country:** {policy["Country"]}')
                        st.write(
                            f'**Discount Rate:** {policy["discountRate"]}%')
                        st.write(
                            f'**Federal Reserve Balance Sheet:** ${policy["FederalReserveBalanceSheet"]} Billion')
                        st.write(
                            f'**Treasury Holdings:** ${policy["TreasurySecurities"]} Billion')
                        st.write(
                            f'**Military Spending:** {policy["MilitarySpending"]}%')
                        st.write(
                            f'**Education Spending:** {policy["EducationSpending"]}%')
                        st.write(
                            f'**Health Spending:** {policy["HealthSpending"]}%')
                        st.write(
                            f'**SP500 Prediction:** {policy["SP500"]:,.2f}')
                        st.write(f'**GDP Prediction:** {policy["GDP"]:,.2f}')

                    with col2:
                        if st.button("View Analysis", key=f"analyze_{policy['publish_id']}", use_container_width=True):

                            st.session_state['published_policy'] = {
                                'Selected Country': policy['Country'],
                                'Discount Rate': policy['discountRate'],
                                'Federal Balance': policy['FederalReserveBalanceSheet'],
                                'Treasury Holdings': policy['TreasurySecurities'],
                                'Military Spending': policy['MilitarySpending'],
                                'Education Spending': policy['EducationSpending'],
                                'Health Spending': policy['HealthSpending'],
                                'SP500': policy['SP500'],
                                'GDP': policy['GDP'],
                                'Predictions': policy['Predictions']
                            }
                            st.switch_page("pages/35_Economist_ViewPred.py")

                    st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.info("No published policies found.")
    else:
        st.error("Failed to fetch published policies")
except Exception as e:
    st.error(f"Error: {str(e)}")

st.write("---")
