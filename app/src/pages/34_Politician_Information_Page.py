import pandas as pd
import requests
from modules.nav import SideBarLinks
import streamlit as st
import logging
logger = logging.getLogger(__name__)
from modules.theme import custom_style

st.set_page_config(layout='wide')
custom_style()
# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

with st.container(height = 300):
    st.write("### Politician Contact Info:")
    response = requests.get(f"http://web-api:4000/pol/politician/{st.session_state['Politician Index']}")
    data = response.json()
    df1 = pd.DataFrame(data)
    st.write(f"**Full name**: {df1.loc[0, 'full_name']}")
    st.write(f"**Department:** {df1.loc[0, 'department']}")
    st.write(f"**Email Address:** {df1.loc[0, 'email_address']}")
    st.write(f"**Phone Number:** {df1.loc[0, 'phone_number']}")

if st.button("Previous"):
    st.switch_page("pages/33_View_Favorites.py")