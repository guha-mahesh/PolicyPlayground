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
    
    Functionalities Include:
    - AI Models to predict Currency Exchange Rates, Market Indicators such as the SPY or the FTSE, and the GDP/Capita of a country based on fiscal and monetary policy.
    - Policy saving and publishing features for politicians to test out policies and save their favorite "presets" or publish policies to receive feedback from Economists
    - Note taking features for Lobbyists to keep track of their conversations with politicians and view the politicians proposed policies and their implications
    - Pages for Economists to view historic policies and information regarding how the policy was carried out, when the policies were made, and what the policies accomplished
    - Additionally, Economists can also utilize a model which shows them similar policies to the historic policies they have saved

    Created By: Guha Mahesh, Bhuvan Hospet, Sota Shimizu, and Carter Vargas
    """
)


# Add a button to return to home page
if st.button("Return to Home", type="primary"):
    st.switch_page("Home.py")
