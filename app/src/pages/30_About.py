import streamlit as st
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks
from modules.theme import custom_style

custom_style()
SideBarLinks()
st.write("# About this App")

st.markdown(
    """
    Welcome to **Policy Playground** by Pushin Policy! Our app is designed to empower individuals working with economic public policy by providing data-driven insights to support the legislative process. 

    Through interactive fiscal and monetary tools, users can explore and predict key economic indicators such as the **S&P 500** and **GDP**. Policy Playground also offers access to historical policy data, politicians’ records, and their associated economic impacts—helping economists, lobbyists, and policymakers make informed decisions with confidence.
    """
)


# Add a button to return to home page
if st.button("Return to Home", type="primary"):
    st.switch_page("Home.py")
