import pandas as pd
import requests
from modules.nav import SideBarLinks
import streamlit as st
import logging
logger = logging.getLogger(__name__)


st.set_page_config(layout='wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.title(
    f"Hello, {st.session_state['first_name']}, Choose Policies to Explore")
st.write("---")
st.write("\n \n")


if st.button("View Historial Data"):
    st.switch_page("pages/32_Historical_Data.py")

if st.button("View Proposed Drafts"):
    st.switch_page("pages/33_View_Favorites.py")
