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


economic_topics = ["Taxation", "Govt spending", "Public deficit", "Interest rates", "Inflation", "Money supply", "Government bonds", "Unemployment", "Tariffs", "Trade agreements", "Minimum wage", "Retirement", "Debt management"]
scopes = ['Neighborhood', 'City', 'County', 'State', 'Province',
    'Region', 'National', 'Cross-Border', 'Continental', 'International', 'Global']
durations = ['Temporary', 'Short-Term',
             'Medium-Term', 'Long-Term', 'Permanent', 'Trial']
politicians = ["Alice Danton", "Bryce Linwood", "Cara Solis", "Damon Krill", "Evelyn Marsh", "Felix Grant", "Gina Torres", "Hector Wells", "Isla Reed", "Jasper Cole"]
intensities = [
    'Not Enforced', 'Symbolic Only', 'Minimal', 'Light Enforcement', 'Moderate Enforcement',
    'Strict Enforcement', 'Punitive', 'Community-Enforced', 'Surveillance-Based']
durations = ['Temporary', 'Short-Term',
             'Medium-Term', 'Long-Term', 'Permanent', 'Trial']


with col1:
   scopes_choice = st.selectbox("Enter Scope:", scopes)
   intensity_choice = st.selectbox("Enter Policy Type:", intensities)
   duration_choice = st.selectbox("Select Politician:", durations)
   
with col2:
    st.text('Recommendations')
    with st.container(height=250):
        st.text("")


    st.text('Similar Policies')
    with st.container(height=250):
        st.text('Policy 1')

with col1:
    params = {}
    if st.button(label="Predict"):
        if scopes_choice:
            params['scopes'] = scopes_choice
        if intensity_choice:
            params['intensity'] = intensity_choice
        if duration_choice:
            params['duration'] = duration_choice
    response = requests.get("http://web-api:4000/pol/get_desc", params=params)
    data = response.json()
    st.write(data)

# add a button to use the values entered into the number field to send to the
# prediction function via the REST API
if st.button("Save Note", type="primary", use_container_width=True):
    results = requests.get(f"http://web-api:4000/prediction/{var_01}/{var_02}")
    json_results = results.json()
    st.dataframe(json_results)