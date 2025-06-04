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

st.text_input(label="Enter Name")

col1, col2 = st.columns(2, vertical_alignment="bottom")
politicians = getmethods.getPoliticians()
#requests.get("http://web-api:4000/politicians/{polName}")

# add a button to use the values entered into the number field to send to the
# prediction function via the REST API
if st.button("Save Politician", type="primary", use_container_width=True):
    results = requests.get(f"http://web-api:4000/prediction/{var_01}/{var_02}")
    json_results = results.json()
    st.dataframe(json_results)