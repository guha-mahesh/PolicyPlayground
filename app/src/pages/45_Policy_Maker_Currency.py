from modules.nav import SideBarLinks
import streamlit as st
import logging
import requests
logger = logging.getLogger(__name__)


st.set_page_config(layout='wide')


SideBarLinks()
