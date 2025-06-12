import streamlit as st

def custom_style():
    st.markdown(
        """
        <style>
        /* Import Poppins font from Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

        [data-testid="stSidebar"] {
            background-color: #18435a;
        }

        [data-testid="stSidebar"] * {
            color: #FFFFFF !important;
        }

        .stApp {
            font-family: 'Poppins', sans-serif !important;
        }

        .stApp * {
            font-family: 'Poppins', sans-serif !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
