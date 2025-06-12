from modules.theme import *
import pandas as pd
import requests
from modules.nav import SideBarLinks
import streamlit as st
import logging
logger = logging.getLogger(__name__)


custom_style()


# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()
welcome_banner("Analyze and explore policies and their impacts")


col1, col2 = st.columns(2)
with col1:
    with st.container(height=300):
        if st.button("View Historial Data", use_container_width=True):
            st.switch_page("pages/32_Historical_Data.py")
        if st.button("View Proposed Drafts", use_container_width=True):
            st.switch_page("pages/saved_drafts.py")

with col2:
    with st.container(height=300):
        st.image('https://media.istockphoto.com/id/1313070791/photo/business-analysis-and-financial-background.jpg?s=612x612&w=0&k=20&c=AvcbvrDfdxXDtc_5UGxoja8h3zOLfpf0_l06Rd4c1OM=', use_container_width=True)
