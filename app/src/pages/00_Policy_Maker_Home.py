from modules.nav import SideBarLinks
import streamlit as st
import logging
import requests
logger = logging.getLogger(__name__)

st.set_page_config(layout='wide')
SideBarLinks()

st.title(f"Welcome {st.session_state['first_name']}")
st.write('')
st.write('')
st.write('# Test your Policy')


tab1, tab2 = st.tabs(["Monetary Policy", "Fiscal Policy"])


selected_country = "Use My Nationality"

with tab1:
    st.write("#### Federal Reserve Controls")
    st.write("")

    col1, col2 = st.columns([3, 1])
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
            value=discount_rate_slider,
            step=0.25,
            format="%.2f",
            key="discount_input"
        )

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
            value=fed_balance_slider,
            step=100,
            key="balance_input"
        )

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

with tab2:
    st.write("#### Government Spending Allocation")
    st.write("")

    country_options = ["Use My Nationality", "United States", "Japan", "Germany",
                       "United Kingdom", "France", "Russia", "Canada"]
    selected_country = st.selectbox(
        "Select Country for GDP Analysis (Optional)",
        options=country_options,
        index=0,
        help="Choose a country for GDP prediction, or use your nationality"
    )
    st.write("")

    col7, col8 = st.columns([3, 1])
    with col7:
        military_slider = st.slider(
            "Military Spending (% of Government Expenditure)",
            min_value=0.0,
            max_value=20.0,
            value=3.0,
            step=0.1,
            key="military_slider"
        )
    with col8:
        military_input = st.number_input(
            "Military",
            min_value=0.0,
            max_value=20.0,
            value=military_slider,
            step=0.1,
            key="military_input"
        )

    col9, col10 = st.columns([3, 1])
    with col9:
        education_slider = st.slider(
            "Education Spending (% of GDP)",
            min_value=0.0,
            max_value=20.0,
            value=5.0,
            step=0.1,
            key="education_slider"
        )
    with col10:
        education_input = st.number_input(
            "Education",
            min_value=0.0,
            max_value=20.0,
            value=education_slider,
            step=0.1,
            key="education_input"
        )

    col11, col12 = st.columns([3, 1])
    with col11:
        health_slider = st.slider(
            "Health Spending (% of GDP)",
            min_value=0.0,
            max_value=15.0,
            value=8.0,
            step=0.1,
            key="health_slider"
        )
    with col12:
        health_input = st.number_input(
            "Health",
            min_value=0.0,
            max_value=15.0,
            value=health_slider,
            step=0.1,
            key="health_input"
        )


discount_rate = discount_rate_input or discount_rate_slider
fed_balance = fed_balance_input or fed_balance_slider
treasury_holdings = treasury_input or treasury_slider
military_spending = military_input or military_slider
education_spending = education_input or education_slider
health_spending = health_input or health_slider

ls = ["United States", "Japan", "Germany",
      "United Kingdom", "France", "Russia", "Canada"]


if selected_country == "Use My Nationality":
    if st.session_state['nationality'] in ls:
        country = st.session_state['nationality']
    else:
        country = "United States"
else:
    country = selected_country

st.write("---")
st.write("### Current Policy Settings")
col_left, col_right = st.columns(2)

with col_left:
    st.write("**Monetary Policy:**")
    st.write(f"• Discount Rate: {discount_rate}%")
    st.write(f"• Fed Balance: ${fed_balance:,}B")
    st.write(f"• Treasury Holdings: ${treasury_holdings:,}B")

with col_right:
    st.write("**Fiscal Policy:**")
    st.write(f"• Country: {country}")
    st.write(f"• Military Spending: {military_spending}%")
    st.write(f"• Education Spending: {education_spending}%")
    st.write(f"• Health Spending: {health_spending}%")


if st.button("test database", type="primary"):
    data = requests.get(
        "http://web-api:4000/model/fetchData/AUDTOUSD")
    st.write(data.text)


if st.button("Test Policy Set", type="primary"):
    st.session_state['policy_params'] = {
        "Discount Rate": discount_rate,
        "Federal Balance": fed_balance,
        "Treasury Holdings": treasury_holdings,
        "Military Spending": military_spending,
        "Education Spending": education_spending,
        "Health Spending": health_spending,
        "Selected Country": country
    }

    # API calls
    api_url = f"http://host.docker.internal:4000/predictSp/{discount_rate},{fed_balance},{treasury_holdings}"
    api_url2 = f"http://host.docker.internal:4000/predictCurr/{discount_rate},{fed_balance},{treasury_holdings}"
    api_url3 = f"http://host.docker.internal:4000/predictGDP/{military_spending},{education_spending},{health_spending}/{country}"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Connection': 'keep-alive'
        }

        with st.spinner('Running policy analysis...'):
            response = requests.get(api_url, headers=headers, timeout=10)
            response2 = requests.get(api_url2, headers=headers, timeout=10)
            response3 = requests.get(api_url3, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            data2 = response2.json()
            data3 = response3.json()
            st.success("Prediction successful!")
            st.session_state['Predictions'] = {
                "SP500": data['prediction'],
                "Currencies": data2['prediction'],
                "GDP/C": data3["prediction"]
            }
            st.switch_page("pages/44_Policy_Maker_viewPred.py")
        else:
            st.error(f"API Error: {response.status_code}")
            st.write(response.text)

    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.write(
            f"URL that worked in browser: {api_url}, {api_url2}, {api_url3}")
