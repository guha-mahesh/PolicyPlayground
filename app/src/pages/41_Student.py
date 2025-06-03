import logging

logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests

st.set_page_config(layout="wide")

# Display the appropriate sidebar links for the role of the logged in user
SideBarLinks()

st.title('Enter Policy Features')

# create a 2 column layout
col1, col2 = st.columns(2)
politicians = ['John Pork', 'Guha']
# add one number input for variable 1 into column 1
with col1:
   st.selectbox(label="Enter Scope:", options=politicians)
   st.selectbox(label="Enter Policy Type:", options=politicians)
   st.selectbox(label="Select Politician:", options=politicians)
# add another number input for variable 2 into column 2
with col2:
    with st.container(height=400):
        st.text("Lorem ipsum Lorem ipsum Lorem ipsum" \
        " Lorem ipsum Lorem ipsum Lorem ipsum" \
        " Lorem ipsum Lorem ipsum Lorem ipsum")

st.text_area(label="Enter Description", value="", height=None, max_chars=None,
             key=None, help=None, on_change=None, args=None, kwargs=None,
             placeholder=None, disabled=False, label_visibility="visible")

col1, col2 = st.columns(2, vertical_alignment="bottom")
polName = 'John Pork'
politicians = ['John Pork', 'Guha']
#requests.get("http://web-api:4000/politicians/{polName}")

with col1:
    st.selectbox(label="Select Politician:", options=politicians, index=0, key=None, help=None, on_change=None, args=None, kwargs=None, placeholder=None, disabled=False, label_visibility="visible", accept_new_options=False)

with col2:
    st.button("New Politician")

st.subheader('Policy Changes')
st.text('Monetary Policy:')
col1, col2, col3 = st.columns(3)
with col1:
    st.slider(label='Discount Rate')
    
with col2:
    st.slider(label='Treasury Securities')

with col3:
    st.slider(label='Penis Length')

# add a button to use the values entered into the number field to send to the
# prediction function via the REST API
if st.button("Save Note", type="primary", use_container_width=True):
    results = requests.get(f"http://web-api:4000/prediction/{var_01}/{var_02}")
    json_results = results.json()
    st.dataframe(json_results)