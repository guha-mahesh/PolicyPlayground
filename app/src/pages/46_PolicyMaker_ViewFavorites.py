import json
import requests
import streamlit as st
from modules.nav import SideBarLinks


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
            st.write("")
            st.write("**Monetary Policy:**")
            st.write(f'**Discount Rate:** {policyJson["discountRate"]}%')
            st.write(f'**Federal Reserve Balance Sheet:** ${policyJson["FederalReserveBalanceSheet"]} Billion')
            st.write(f'**Treasury Holdings:** ${policyJson["TreasurySecurities"]} Billion')
            st.write(f'**Federal Funds Rate:** {policyJson["FederalFundsRate"]}%')
            st.write(f'**Money Supply:** ${policyJson["MoneySupply"]} Billion')
            st.write(f'**Reserve Requirement Ratio:** {policyJson["ReserveRequirementRatio"]}%')
            st.write("**Fiscal Policy:**")
            st.write(f'**Military Spending:** {policyJson["MilitarySpending"]}%')
            st.write(f'**Education Spending:** {policyJson["EducationSpending"]}%')
            st.write(f'**Health Spending:** {policyJson["HealthSpending"]}%')
            st.write(f'**Infrastructure Spending:** {policyJson["InfrastructureSpending"]}%')
            st.write(f'**Debt-to-GDP Ratio:** {policyJson["DebtToGDPRatio"]}%')
            st.write(f'**Corporate Tax Rate:** {policyJson["CorporateTaxRate"]}%')
        with col2:
            st.button(label="Modify", key=id, use_container_width=True)

