import logging

logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests
import requestfunctions.getmethods as getmethods

st.set_page_config(layout="wide")

# Display the appropriate sidebar links for the role of the logged in user
SideBarLinks()

politicians = getmethods.getPoliticians(st.session_state["user_id"]).json()

selected_politician = st.selectbox(label="Select Politician:", options=politicians, index=0, format_func=lambda pol: pol["Name"])


currentConvo = {"title" : "", "content" : ""}
conversations = getmethods.getNotes(st.session_state["user_id"], selected_politician["politician_id"]).json()
st.session_state["notes_empty"] = True

try:
    currentConvo = conversations[0]
    st.session_state["notes_empty"] = False
except IndexError:
    st.session_state["notes_empty"] = True

col1, col2 = st.columns([1, 2])

# Left panel
with col1:
    with st.container(height=500): 
        if st.session_state["notes_empty"]:
            st.write("No conversations found")
        else:
            for convo in conversations:
                if st.button(label=convo["title"], key=convo["conversation_id"], use_container_width=True):
                    currentConvo = convo
                    st.session_state["current_convo"] = currentConvo

# Right panel
with col2:
    if not(st.session_state["notes_empty"]):  
        st.subheader(currentConvo["title"])

        st.write("Future Prediction")
        with st.container(height=200):
            st.write("graph")

        col2_1, col2_2 = st.columns([2, 1])

        with col2_1:
            with st.container(height=150):
                st.write("description")
                st.write(currentConvo["content"])

        with col2_2:
            with st.container(height=150):
                st.write("Policy Summary")

        col2_3, col2_4 = st.columns([3, 1])

        with col2_3:
            with st.container(height=150):
                st.write("Similar Politicians")
                
        with col2_4:
            if st.button(label="Modify", use_container_width=True):
                st.session_state["current_politician"] = selected_politician
                st.switch_page("pages/44_Lobbyist3.py")
