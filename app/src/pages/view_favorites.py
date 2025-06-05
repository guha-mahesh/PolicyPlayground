import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests
import pandas as pd

st.set_page_config(layout = 'wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()


st.title(f"View Favorite Policies 🔎")
st.write("---")
st.write("\n \n")

response = requests.get("http://web-api:4000/pol/getfav/"+ str(st.session_state["user_id"]))
data = response.json()
df = pd.DataFrame(data)
st.dataframe(df)

policies = ["option"]   
fav_choices = st.selectbox("Choose A Policy to Look at", policies)



col1, col2 = st.columns(2)

with col1: 
    with st.container(height=250):
        st.write("desc")

with col2:
    with st.container(height=250):
        st.write("info")
