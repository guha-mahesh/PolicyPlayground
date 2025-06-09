import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests
import pandas as pd

st.set_page_config(layout = 'wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()


st.title("Choose Policies to Explore")
st.write("---")
st.write("\n \n")


if st.button("View Historial Data"):
    st.switch_page("pages/historicaldata.py")

if st.button("View Proposed Drafts"):
    st.switch_page("pages/view_favorites.py")



