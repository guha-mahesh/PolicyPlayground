import logging

logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests
import requestfunctions.getmethods as getmethods

st.set_page_config(layout="wide")

# Display the appropriate sidebar links for the role of the logged in user
SideBarLinks()

st.title("Enter new Politician")

name = st.text_input(label="Enter Name")
contact = st.text_input(label="Enter Contact Info")

returnJson = {"full_name" : name, "contact" : contact, "user_id" : st.session_state["user_id"]}

# add a button to use the values entered into the number field to send to the
# prediction function via the REST API
if st.button("Save Politician", type="primary", use_container_width=True):
    getmethods.savePolitician(returnJson)
    st.switch_page('pages/40_Lobbyist.py')