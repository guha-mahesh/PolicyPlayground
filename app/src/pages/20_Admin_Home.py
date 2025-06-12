from modules.theme import custom_style
import requests
from modules.nav import SideBarLinks
import streamlit as st
import logging
logger = logging.getLogger(__name__)


custom_style()
SideBarLinks()

st.title("Admin Home\n")
st.write("\n")

if st.button("Train Model"):
    url = "http://web-api:4000/model/models"
    train_response = requests.post(url)
    if train_response.status_code == 200:
        st.success("✅ Models trained successfully!")
