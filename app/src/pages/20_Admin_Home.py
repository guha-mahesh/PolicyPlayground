from modules.theme import custom_style
import requests
from modules.nav import SideBarLinks
import streamlit as st
import logging
logger = logging.getLogger(__name__)
import os
import dotenv


custom_style()
SideBarLinks()


dotenv.load_dotenv()
API_URL = os.getenv("URL", "smth.onrender idkyet")




st.title("Admin Home\n")
st.write("\n")

if st.button("Train Model"):
    url = f"{API_URL}/model/models"
    train_response = requests.post(url)
    if train_response.status_code == 200:
        st.success("✅ Models trained successfully!")
