import requests
from modules.nav import SideBarLinks
import streamlit as st
import logging
logger = logging.getLogger(__name__)
from modules.theme import custom_style



st.set_page_config(layout='wide')
custom_style()
SideBarLinks()

if st.button("Train Model"):
    url = "http://web-api:4000/model/models"
    train_response = requests.post(url)
    if train_response.status_code == 200:
        st.success("✅ Models trained successfully!")
