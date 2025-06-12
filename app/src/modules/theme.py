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
        /* Target Streamlit's main container */
        .stApp {
            font-family: 'Poppins', serif !important;
        }
        .stApp * {
            font-family: inherit !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )