import logging

logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests
import requestfunctions.getmethods as getmethods

st.set_page_config(layout="wide")

# Display the appropriate sidebar links for the role of the logged in user
SideBarLinks()

st.title('Enter Policy Features')

# create a 2 column layout
col1, col2 = st.columns(2)
politicians = getmethods.getPoliticians()

# add one number input for variable 1 into column 1
with col1:
   st.selectbox(label="Enter Scope:", options=politicians)
   st.selectbox(label="Enter Policy Type:", options=politicians)
   st.selectbox(label="Select Politician:", options=politicians)
   st.button(label="Predict")
# add another number input for variable 2 into column 2
with col2:
    st.text('Recommendations')
    with st.container(height=250):
        st.text("Lorem ipsum Lorem ipsum Lorem ipsum" \
        " Lorem ipsum Lorem ipsum Lorem ipsum" \
        " Lorem ipsum Lorem ipsum Lorem ipsum")
    st.text('Similar Policies')
    with st.container(height=250):
        st.text('Policy 1')


# add a button to use the values entered into the number field to send to the
# prediction function via the REST API
if st.button("Save Note", type="primary", use_container_width=True):
    results = requests.get(f"http://web-api:4000/prediction/{var_01}/{var_02}")
    json_results = results.json()
    st.dataframe(json_results)