from modules.nav import SideBarLinks
import streamlit as st
import logging
import requests

logger = logging.getLogger(__name__)

st.set_page_config(layout='wide')

SideBarLinks()

gdp_pred = st.session_state["Predictions"]['Currencies']

st.write("### Currency Predictions")

# Format as a table for better readability
predictions_table = [{"Currency": key, "Prediction": val}
                     for key, val in gdp_pred.items()]
st.table(predictions_table)

if st.button("Try a New Set"):
    st.switch_page('pages/00_Policy_Maker_Home.py')
