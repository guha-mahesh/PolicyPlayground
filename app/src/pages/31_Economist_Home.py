from modules.theme import custom_style
import pandas as pd
import requests
from modules.nav import SideBarLinks
import streamlit as st
import logging
logger = logging.getLogger(__name__)


st.set_page_config(layout='wide')
custom_style()


# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()


st.markdown("""
    <div style='background: linear-gradient(90deg, #1e3a8a 0%, #1e40af 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem;'>
        <h1 style='color: white; margin: 0;'>Start Exploring Policy</h1>
        <p style='color: #94a3b8; margin: 0.5rem 0 0 0;'>Analyze past policies and their impacts</p>
    </div>
""", unsafe_allow_html=True)
st.write(f"### Weclome, {st.session_state['first_name']}.\n")

col1, col2 = st.columns(2)
with col1:
    with st.container(height=300):
        if st.button("View Historial Data", use_container_width=True):
            st.switch_page("pages/32_Historical_Data.py")
        if st.button("View Proposed Drafts", use_container_width=True):
            st.switch_page("pages/33_View_Favorites.py")

with col2:
    with st.container(height=300):
        st.image('https://media.istockphoto.com/id/1313070791/photo/business-analysis-and-financial-background.jpg?s=612x612&w=0&k=20&c=AvcbvrDfdxXDtc_5UGxoja8h3zOLfpf0_l06Rd4c1OM=', use_container_width=True)
