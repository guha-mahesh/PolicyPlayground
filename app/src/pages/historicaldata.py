import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests

st.set_page_config(layout = 'wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

"""st.title(f"Welcome Political Strategist, {st.session_state['first_name']}.")
st.write('')
st.write('')
st.write('### What would you like to do today?')

if st.button('View World Bank Data Visualization', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/01_World_Bank_Viz.py')

if st.button('View World Map Demo', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/02_Map_Demo.py')"""

st.title(f"Historical Data Viewer")

col1, col2 = st.columns(2)

with col1:
  year_start = ["2002", "2003", "2004"]
  start_choice = st.selectbox("Choose Start Year", year_start)
  #st.write("You selected:", choice)
  
  topic = ["Monetary", "Taxes"]
  topic_choice = st.selectbox("Choose a Topic", topic)

  politician = ["LeBron", "Carter"]
  politician_choice = st.selectbox("Choose a politican", politician)

with col2:
  year_end = ["2015", "2016"]
  end_choice = st.selectbox("Choose End Year", year_end)

  country = ["US", "EU"]
  country_choice = st.selectbox("Choose a Country", country)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
  st.button("Apply")

st.write(requests.get('http://web-api:4000/pol/get').json())


