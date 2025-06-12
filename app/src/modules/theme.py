import streamlit as st

def custom_style():
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            background-color: #18435a;
        }
        [data-testid="stSidebar"] * {
            color: #FFFFFF !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )