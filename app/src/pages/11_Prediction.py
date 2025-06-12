import logging
import streamlit as st
from modules.nav import SideBarLinks
import requests
from modules.theme import custom_style

custom_style()

# Display the appropriate sidebar links for the role of the logged in user
SideBarLinks()

logger = logging.getLogger(__name__)
st.title("Policy Maker")
st.markdown("---")

st.markdown("**Monetary Policy**")

col1, col2, col3 = st.columns(3)
with col1:  
    discountrate = st.slider("Discount Rate", 0, 100)

with col2:
    treasurysecurities = st.slider("Treasury Securities", 0, 100)

with col3:
    fedreserve = st.slider("Federal Reserve Balance Sheets", 0, 100)

st.markdown("**Fiscal Policy**")
col1, col2, col3 = st.columns(3)
with col1:  
    education = st.slider("Education Spending", 0, 100)

with col2:
    healthcare = st.slider("Healthcare Spending", 0, 100)

with col3:
    infrastrucutre = st.slider("Infrastructure Spending", 0, 100)
    st.markdown("\n\n\n")
    st.button("Test")



