import requestfunctions.getmethods as getmethods
import requests
from modules.nav import SideBarLinks
import streamlit as st
import logging
import json

logger = logging.getLogger(__name__)

st.set_page_config(layout="wide")

# Display the appropriate sidebar links for the role of the logged in user
SideBarLinks()

# create a 2 column layout
col1, col2 = st.columns(2)

# add one number input for variable 1 into column 1
with col1:
    st.title("New Note")

# add another number input for variable 2 into column 2
with col2:
    title = st.text_input("Enter Title")

content = st.text_area(label="Enter Description", value="", height=None, max_chars=None,
                       key=None, help=None, on_change=None, args=None, kwargs=None,
                       placeholder=None, disabled=False, label_visibility="visible")

col1, col2 = st.columns(2, vertical_alignment="bottom")
response = getmethods.getPoliticians(st.session_state["user_id"])

if response.ok:
    try:
        politicians = response.json()
    except json.decoder.JSONDecodeError:
        st.error("Error: Received empty or invalid JSON from server.")
        politicians = []
else:
    st.error(f"Error: {response.status_code} {response.reason}")
    politicians = []
list_pol = []
for pol in politicians:
    list_pol.append(pol["Name"])

# requests.get("http://web-api:4000/politicians/{polName}")

with col1:
    selected_politician = st.selectbox(label="Select Politician:", options=list_pol, index=0, key=None, help=None, on_change=None,
                                       args=None, kwargs=None, placeholder=None, disabled=False, label_visibility="visible", accept_new_options=False)

with col2:
    if st.button("New Politician"):
        st.switch_page('pages/42_NewPolitician.py')


st.subheader('Policy Changes')
st.text('Monetary Policy:')
col1, col2, col3 = st.columns(3)
with col1:
    st.slider(label='Discount Rate')

with col2:
    st.slider(label='Treasury Securities')

with col3:
    st.slider(label='Feature #3')

returnJson = {"politician_id": getmethods.getPoliticianID(selected_politician),
              "content": content, "title": title, "user_id": st.session_state["user_id"]}


if st.button("Save Note", type="primary", use_container_width=True):
    getmethods.postNote(returnJson)
