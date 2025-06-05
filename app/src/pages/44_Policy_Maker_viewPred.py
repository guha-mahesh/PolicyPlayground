from modules.nav import SideBarLinks
import streamlit as st
import logging
import requests
logger = logging.getLogger(__name__)


st.set_page_config(layout='wide')


SideBarLinks()

st.title(f"Your Predictions")

sp500_pred = round(float(st.session_state['Predictions']["SP500"]), 2)
gdp_pred = round(float(st.session_state['Predictions']["GDP/C"]), 2)


col1, col2 = st.columns(2)

with col1:
    st.metric(label="📈 S&P 500 Prediction", value=f"{sp500_pred:,}")

with col2:
    st.metric(label="💰 GDP per Capita Prediction", value=f"${gdp_pred:,.2f}")

if st.button("Try a New Set"):
    st.switch_page('pages/00_Policy_Maker_Home.py')

if st.button("View Currency Forecasts"):
    st.switch_page('pages/00_Policy_Maker_Home.py')
