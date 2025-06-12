import pandas as pd
import requests
from modules.nav import SideBarLinks
import streamlit as st
import logging
from modules.theme import *

logger = logging.getLogger(__name__)

custom_style()


SideBarLinks()
banner("Published Policies", "View all published policies")


def adjust_currencies_for_country(base_currencies, user_country, discount_rate):
    """Adjust currency predictions based on the country's monetary policy"""

    if user_country == "United Kingdom":

        rate_effect = (discount_rate - 5.25) * 0.02

        adjusted_currencies = {}

        usd_per_gbp = 1 / base_currencies["British Pound"]
        adjusted_currencies["US Dollar"] = usd_per_gbp * (1 + rate_effect)

        for currency, rate in base_currencies.items():
            if currency != "British Pound":

                rate_per_gbp = rate / base_currencies["British Pound"]

                if currency == "Euro":
                    adjusted_currencies[currency] = rate_per_gbp * \
                        (1 + rate_effect * 0.3)
                elif currency == "Japanese Yen":
                    adjusted_currencies[currency] = rate_per_gbp * \
                        (1 + rate_effect * 0.1)
                elif currency == "Australian Dollar":
                    adjusted_currencies[currency] = rate_per_gbp * \
                        (1 - rate_effect * 0.1)
                else:
                    adjusted_currencies[currency] = rate_per_gbp

    elif user_country == "Germany":

        rate_effect = (discount_rate - 4.5) * 0.025

        adjusted_currencies = {}

        usd_per_eur = 1 / base_currencies["Euro"]
        adjusted_currencies["US Dollar"] = usd_per_eur * (1 + rate_effect)

        for currency, rate in base_currencies.items():
            if currency != "Euro":

                rate_per_eur = rate / base_currencies["Euro"]

                if currency == "British Pound":
                    adjusted_currencies[currency] = rate_per_eur * \
                        (1 - rate_effect * 0.4)
                elif currency == "Chinese Yuan":
                    adjusted_currencies[currency] = rate_per_eur * \
                        (1 + rate_effect * 0.2)
                elif currency == "Japanese Yen":
                    adjusted_currencies[currency] = rate_per_eur * \
                        (1 + rate_effect * 0.15)
                else:
                    adjusted_currencies[currency] = rate_per_eur

    else:

        adjusted_currencies = base_currencies.copy()

    return adjusted_currencies


try:

    response = requests.get("http://web-api:4000/politician/publisher")
    if response.status_code == 200:
        published_policies = response.json()

        if published_policies:
            st.markdown("""
                <div style='background: 
                    <h3 style='color: 
                    <p style='color: 
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

                            user_country = st.session_state.get(
                                'nationality', 'United States')
                            if user_country not in ["United States", "United Kingdom", "Germany"]:
                                user_country = "United States"

                            api_url2 = f"http://host.docker.internal:4000/model/currency/{policy['discountRate']},{policy['TreasurySecurities']},{policy['FederalReserveBalanceSheet']}"

                            try:
                                headers = {
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                                    'Accept': 'application/json',
                                    'Connection': 'keep-alive'
                                }

                                response2 = requests.get(
                                    api_url2, headers=headers, timeout=10)

                                if response2.status_code == 200:
                                    data2 = response2.json()
                                    base_currencies = data2['prediction']

                                    if user_country in ["United Kingdom", "Germany"]:
                                        adjusted_currencies = adjust_currencies_for_country(
                                            base_currencies, user_country, policy['discountRate']
                                        )
                                    else:
                                        adjusted_currencies = base_currencies

                                    st.session_state['predictionsCurrency'] = adjusted_currencies
                                else:
                                    st.error(
                                        f"Failed to get currency predictions: {response2.status_code}")
                                    st.session_state['predictionsCurrency'] = {
                                    }

                            except Exception as e:
                                st.error(
                                    f"Error getting currency predictions: {str(e)}")
                                st.session_state['predictionsCurrency'] = {}

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
