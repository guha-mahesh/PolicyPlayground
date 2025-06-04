import logging

logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests
import requestfunctions.getmethods as getmethods

st.set_page_config(layout="wide")

# Display the appropriate sidebar links for the role of the logged in user
SideBarLinks()

# Simulated conversation data
conversations = {
    "Alice": ["Hi there!", "How's the project going?"],
    "Bob": ["Did you see the latest update?", "We need to review it."],
    "Charlie": ["Lunch at 1 PM?", "Let me know."],
}

# Initialize session state for selected conversation
if "selected" not in st.session_state:
    st.session_state.selected = list(conversations.keys())[0]  # Default selection

# Layout: Two columns
col1, col2 = st.columns([1, 2])

# Left panel: Scrollable conversation list
with col1:
    with st.container(height=500):
        for name in conversations:
            if st.button(label="Conversation #1", key=name, use_container_width=True):
                st.session_state.selected = name

# Right panel: Show selected conversation
with col2:
    st.subheader(f"Conversation with {st.session_state.selected}")
    for msg in conversations[st.session_state.selected]:
        st.markdown(f"🗨️ {msg}")
