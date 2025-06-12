import requestfunctions.getmethods as getmethods
import requests
from modules.nav import SideBarLinks
import streamlit as st
import logging
import json
from modules.theme import *


logger = logging.getLogger(__name__)


custom_style()
# Display the appropriate sidebar links for the role of the logged in user
SideBarLinks()

currentConvo = st.session_state["current_convo"]
if 'new_note_title' not in st.session_state:
    st.session_state['new_note_title'] = ""
if 'new_note_content' not in st.session_state:
    st.session_state['new_note_content'] = ""

currentPolicy = getmethods.getPolicy(currentConvo["saved_id"]).json()[0]

# create a 2 column layout
col1, col2 = st.columns(2)

# add one number input for variable 1 into column 1
with col1:
    st.title("Modify Note")

# add another number input for variable 2 into column 2
with col2:
    title = st.text_input(label="Enter Title", value=currentConvo["title"])

content = st.text_area(label="Enter Description", value=currentConvo["content"], height=None, max_chars=None,
                       key=None, help=None, on_change=None, args=None, kwargs=None,
                       placeholder=None, disabled=False, label_visibility="visible")

st.session_state['new_note_title'] = title
st.session_state['new_note_content'] = content
col1, col2 = st.columns(2, vertical_alignment="bottom")
response = getmethods.getPoliticians(st.session_state["user_id"])

if response.ok:
    try:
        politicians = response.json()
    except json.decoder.JSONDecodeError:
        st.error("Error: Received empty or invalid JSON from server.")
        politicians = []
else:
    st.error(f"Error: {response.status_code} {response.reason}")
    politicians = []

# with col1:
#     selected_politician = st.selectbox(label="Select Politician:", index=politicians.index(st.session_state["current_politician"]), options=politicians, format_func=lambda pol: pol["full_name"])

# with col2:
#     if st.button("New Politician"):
#         st.switch_page('pages/42_NewPolitician.py')

current_politician = st.session_state["current_politician"]
st.write(
    f'**Politician:** {st.session_state["current_politician"]["full_name"]}')


st.subheader('Policy Changes')
country_options = ["Use My Nationality", "United States", "Japan", "Germany",
                   "United Kingdom", "France", "Russia", "Canada"]
selected_country = st.selectbox(
    "Select Country for GDP Analysis (Optional)",
    options=country_options,
    index=0,
    help="Choose a country for GDP prediction, or use your nationality"
)

ls = ["United States", "Japan", "Germany",
      "United Kingdom", "France", "Russia", "Canada"]
if selected_country == "Use My Nationality":
    if st.session_state['nationality'] in ls:
        country = st.session_state['nationality']
    else:
        country = "United States"
else:
    country = selected_country

st.text('Monetary Policy:')
col1, col2, col3 = st.columns(3)
with col1:
    frdr = st.slider(
        "Federal Reserve Discount Rate (%)",
        min_value=0.0,
        max_value=15.0,
        value=float(currentPolicy["discountRate"]),
        step=0.25,
        key="discount_slider"
    )

with col2:
    fbss = st.slider(
        "Fed Balance Sheet Size (Billions $)",
        min_value=1000,
        max_value=10000,
        value=int(currentPolicy["FederalReserveBalanceSheet"]),
        step=100,
        key="balance_slider"
    )

with col3:
    tsh = st.slider(
        "Treasury Securities Holdings (Billions $)",
        min_value=500,
        max_value=6000,
        value=int(currentPolicy["TreasurySecurities"]),
        step=100,
        key="treasury_slider"
    )

col4, col5, col6 = st.columns(3)
with col4:
    fed_funds_rate = st.slider(
        "Federal Funds Rate (%)",
        min_value=0.0,
        max_value=10.0,
        value=float(currentPolicy["FederalFundsRate"]),
        step=0.25,
        key="fed_funds_slider"
    )

with col5:
    money_supply = st.slider(
        "Money Supply (Billions $)",
        min_value=0,
        max_value=50000,
        value=int(currentPolicy["MoneySupply"]),
        step=500,
        key="money_supply_slider"
    )

with col6:
    reserve_ratio = st.slider(
        "Reserve Requirement Ratio (%)",
        min_value=0.0,
        max_value=20.0,
        value=float(currentPolicy["ReserveRequirementRatio"]),
        step=0.25,
        key="reserve_ratio_slider"
    )

st.text('Fiscal Policy:')
col1, col2, col3 = st.columns(3)
with col1:
    military = st.slider(
        "Military Spending (% of Government Expenditure)",
        min_value=0.0,
        max_value=20.0,
        value=float(currentPolicy["MilitarySpending"]),
        step=0.1,
        key="military_slider"
    )

with col2:
    education = st.slider(
        "Education Spending (% of GDP)",
        min_value=0.0,
        max_value=20.0,
        value=float(currentPolicy["EducationSpending"]),
        step=0.1,
        key="education_slider"
    )

with col3:
    health = st.slider(
        "Health Spending (% of GDP)",
        min_value=0.0,
        max_value=15.0,
        value=float(currentPolicy["HealthSpending"]),
        step=0.1,
        key="health_slider"
    )

col7, col8, col9 = st.columns(3)
with col7:
    infrastructure = st.slider(
        "Infrastructure Spending (% of GDP)",
        min_value=0.0,
        max_value=20.0,
        value=float(currentPolicy["InfrastructureSpending"]),
        step=0.1,
        key="infrastructure_slider"
    )

with col8:
    debt_gdp_ratio = st.slider(
        "Debt-to-GDP Ratio (%)",
        min_value=0.0,
        max_value=150.0,
        value=float(currentPolicy["DebtToGDPRatio"]),
        step=1.0,
        key="debt_gdp_slider"
    )

with col9:
    corporate_tax_rate = st.slider(
        "Corporate Tax Rate (%)",
        min_value=0.0,
        max_value=50.0,
        value=float(currentPolicy["CorporateTaxRate"]),
        step=0.5,
        key="corp_tax_slider"
    )


if st.button("Save Note", type="primary", use_container_width=True):
    if current_politician == None:
        st.write("Please select a Politician")
    else:
        sp500 = getmethods.predictSP(frdr, fbss, tsh).json()["prediction"]
        GDP = getmethods.predictGDP(military, education, health, country).json()["prediction"]
        save_policy = {
            "discountRate": frdr,
            "federalReserveBalanceSheet": fbss,
            "treasurySecurities": tsh,
            "militarySpending": military,
            "educationSpending": education,
            "healthSpending": health,
            "country": country,
            "user_id": st.session_state["user_id"],
            "market_index": sp500,
            "GDP": GDP,
            "federalFundsRate": fed_funds_rate,
            "moneySupply": money_supply,
            "reserveRequirementRatio": reserve_ratio,
            "infrastructureSpending": infrastructure,
            "debtToGDPRatio": debt_gdp_ratio,
            "corporateTaxRate": corporate_tax_rate,
            "title": title,
            "saved_id": st.session_state["saved_id"]
        }
        json1 = getmethods.modifyPolicy(save_policy).json()
        saved_id = json1["saved_id"]
        noteJson = {"content": content, "title": title, "user_id": st.session_state["user_id"],
                    "conversation_id": currentConvo["conversation_id"]}
        getmethods.modifyNotes(noteJson)
        st.session_state['new_note_title'] = ""
        st.session_state['new_note_content'] = ""
        st.switch_page("pages/43_Lobbyist2.py")

