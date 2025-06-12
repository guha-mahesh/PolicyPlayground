from modules.theme import *
import numpy as np
import pandas as pd
import requestfunctions.getmethods as getmethods
import requests
from modules.nav import SideBarLinks
import streamlit as st
import logging
from modules.graphs import *

logger = logging.getLogger(__name__)


custom_style()
banner("View Saved Notes", "View, analyze, and modify saved notes")

# Display the appropriate sidebar links for the role of the logged in user
SideBarLinks()

politicians = getmethods.getPoliticians(st.session_state["user_id"]).json()
blue_banner("Select a Note", "Choose a note to view information from")
col1, col2 = st.columns(2)

# Left panel
with col1:
    st.write("Select Politician:")
    selected_politician = st.selectbox(
    label="Select Politician:", options=politicians, index=0, 
    format_func=lambda pol: pol["full_name"], label_visibility="hidden")

    currentConvo = {"title": "", "content": ""}
    if selected_politician != None:
        conversations = getmethods.getNotes(
            st.session_state["user_id"], selected_politician["politician_id"]).json()
    else:
        conversations = []
    st.session_state["notes_empty"] = True

    try:
        currentConvo = conversations[0]
        st.session_state["current_convo"] = currentConvo
        currentPolicy = getmethods.getPolicy(currentConvo["saved_id"]).json()[0]
        st.session_state["notes_empty"] = False
    except IndexError or KeyError:
        st.session_state["notes_empty"] = True


# Right panel
with col2:
    st.write("List of conversations:")
    with st.container(height=300):
        if st.session_state["notes_empty"]:
            st.write("No conversations found")
        else:
            for convo in conversations:
                if st.button(label=convo["title"], key=convo["conversation_id"], use_container_width=True):
                    currentConvo = convo
                    st.session_state["current_convo"] = currentConvo
                    currentPolicy = getmethods.getPolicy(currentConvo["saved_id"]).json()[0]

                    st.session_state['cur_policy'] = {
                        'Selected Country': currentPolicy['Country'],
                        'Discount Rate': currentPolicy['discountRate'],
                        'Federal Balance': currentPolicy['FederalReserveBalanceSheet'],
                        'Treasury Holdings': currentPolicy['TreasurySecurities'],
                        'Military Spending': currentPolicy['MilitarySpending'],
                        'Education Spending': currentPolicy['EducationSpending'],
                        'Health Spending': currentPolicy['HealthSpending'],
                        'SP500': currentPolicy['SP500'],
                        'GDP': currentPolicy['GDP']
                        }


if not (st.session_state["notes_empty"]):
    currentPolicy = getmethods.getPolicy(currentConvo["saved_id"]).json()[0]
    st.session_state['cur_policy'] = {
    'Selected Country': currentPolicy['Country'],
    'Discount Rate': currentPolicy['discountRate'],
    'Federal Balance': currentPolicy['FederalReserveBalanceSheet'],
    'Treasury Holdings': currentPolicy['TreasurySecurities'],
    'Military Spending': currentPolicy['MilitarySpending'],
    'Education Spending': currentPolicy['EducationSpending'],
    'Health Spending': currentPolicy['HealthSpending'],
    'SP500': currentPolicy['SP500'],
    'GDP': currentPolicy['GDP']
    }
    banner2(currentConvo["title"], "Future prediction & additional information")
    with st.container(border=True):
        st.markdown("#### Description")
        st.write(currentConvo["content"])

    with st.container(border=True):
        st.subheader("SP500 Prediction")
        sp500graph()
        st.subheader("GDP Prediction")
        GDPgraph()

col2_1, col2_2 = st.columns(2)

if not (st.session_state["notes_empty"]):
    with col2_1:
        st.markdown(f"""
            <div style='
                background: #18435a;
                padding: 1.5rem;
                border-radius: 10px;
                margin: 1rem 0;
            '>
                <h4 style='color: #FFFFFF; margin: 0 0 0.5rem 0;'>Monetary Policy</h4>
                <p style='color: #e2e8f0; margin: 0;'>• Discount Rate: {currentPolicy["discountRate"]}%</p>
                <p style='color: #e2e8f0; margin: 0;'>• Fed Balance: ${currentPolicy["FederalReserveBalanceSheet"]:,}B</p>
                <p style='color: #e2e8f0; margin: 0;'>• Treasury Holdings: ${currentPolicy["TreasurySecurities"]:,}B</p>
                <p style='color: #e2e8f0; margin: 0;'>• Federal Funds Rate: {currentPolicy["FederalFundsRate"]}%</p>
                <p style='color: #e2e8f0; margin: 0;'>• Money Supply: ${currentPolicy["MoneySupply"]:,}B</p>
                <p style='color: #e2e8f0; margin: 0;'>• Reserve Requirement: {currentPolicy["ReserveRequirementRatio"]}%</p>
            </div>
    """, unsafe_allow_html=True)
    with col2_2:
        st.markdown(f"""
        <div style='
            background: #18435a;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
        '>
            <h4 style='color: #FFFFFF; margin: 0 0 0.5rem 0;'>Fiscal Policy</h4>
            <p style='color: #e2e8f0; margin: 0;'>• Military Spending: {currentPolicy["MilitarySpending"]}%</p>
            <p style='color: #e2e8f0; margin: 0;'>• Education Spending: {currentPolicy["EducationSpending"]}%</p>
            <p style='color: #e2e8f0; margin: 0;'>• Health Spending: {currentPolicy["HealthSpending"]}%</p>
            <p style='color: #e2e8f0; margin: 0;'>• Infrastructure Spending: {currentPolicy["InfrastructureSpending"]}%</p>
            <p style='color: #e2e8f0; margin: 0;'>• Debt-to-GDP Ratio: {currentPolicy["DebtToGDPRatio"]}%</p>
            <p style='color: #e2e8f0; margin: 0;'>• Corporate Tax Rate: {currentPolicy["CorporateTaxRate"]}%</p>
        </div>
        """, unsafe_allow_html=True)

    col2_3, col2_4 = st.columns([3, 1], vertical_alignment="center")

    with col2_3:
        with st.container(border=True):
            st.markdown("#### Politician Information")
            st.write(f'**Name: {selected_politician["full_name"]}**')
            st.write("Email: " + (f'{selected_politician["email_address"]}' or "N/A"))
            st.write("Phone Number: " + (f'{selected_politician["phone_number"]}' or "N/A"))
            st.write("Department: " + (f'{selected_politician["department"]}' or "N/A"))
            

    with col2_4:
        if st.button(label="Modify", use_container_width=True):
            st.session_state["current_politician"] = selected_politician
            st.switch_page("pages/44_Lobbyist3.py")
