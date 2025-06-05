from modules.nav import SideBarLinks
import streamlit as st
import logging
import requests
logger = logging.getLogger(__name__)


st.set_page_config(layout='wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.title(f"Welcome Respected Politician")
st.write('')
st.write('')
st.write('Test your Policy')

col1, col2 = st.columns([3, 1])  # 3:1 ratio for slider:number input

# Discount Rate
with col1:
    discount_rate_slider = st.slider(
        "Federal Reserve Discount Rate (%)",
        min_value=0.0,
        max_value=15.0,
        value=2.5,
        step=0.25,
        key="discount_slider"
    )

with col2:
    discount_rate_input = st.number_input(
        "Rate",
        min_value=0.0,
        max_value=15.0,
        value=discount_rate_slider,  # This syncs with slider
        step=0.25,
        format="%.2f",
        key="discount_input"
    )

# Fed Balance Sheet
col3, col4 = st.columns([3, 1])

with col3:
    fed_balance_slider = st.slider(
        "Fed Balance Sheet Size (Billions $)",
        min_value=1000,
        max_value=10000,
        value=7500,
        step=100,
        key="balance_slider"
    )

with col4:
    fed_balance_input = st.number_input(
        "Balance",
        min_value=1000,
        max_value=10000,
        value=fed_balance_slider,  # This syncs with slider
        step=100,
        key="balance_input"
    )

# Treasury Securities
col5, col6 = st.columns([3, 1])

with col5:
    treasury_slider = st.slider(
        "Treasury Securities Holdings (Billions $)",
        min_value=500,
        max_value=6000,
        value=4500,
        step=100,
        key="treasury_slider"
    )

with col6:
    treasury_input = st.number_input(
        "Treasury",
        min_value=500,
        max_value=6000,
        value=treasury_slider,
        step=100,
        key="treasury_input"
    )


discount_rate = discount_rate_input or discount_rate_slider
fed_balance = fed_balance_input or fed_balance_slider
treasury_holdings = treasury_input or treasury_slider

st.write(
    f"Current values: {discount_rate}%, \\${fed_balance}B, \\${treasury_holdings}B")

if st.button("Get S&P 500 Prediction"):
    api_url = f"http://host.docker.internal:4000/predictSp/{discount_rate},{fed_balance},{treasury_holdings}"
    api_url2 = f"http://host.docker.internal:4000/predictCurr/{discount_rate},{fed_balance},{treasury_holdings}"

    try:

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Connection': 'keep-alive'
        }

        response = requests.get(api_url, headers=headers, timeout=10)
        response2 = requests.get(api_url2, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            data2 = response2.json()
            st.success("Prediction successful!")
            st.json(data)
            st.json(data2)
        else:
            st.error(f"API Error: {response.status_code}")
            st.write(response.text)

    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.write(f"URL that worked in browser: {api_url}, {api_url2}")
