import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests

st.set_page_config(layout = 'wide')

SideBarLinks()

st.title('Pushing Policy Notes')

"""if st.button('Update ML Models', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/21_ML_Model_Mgmt.py')"""


options = ["Economic", "Social", "Defense"]
choice = st.selectbox("Choose Topic", options)
#st.write("You selected:", choice)

speaker = st.text_input("Speaker's Name:")
#st.write("You entered:", speaker)

user_text = st.text_area("Enter Notes Here:")
st.write("Notes:", user_text)



