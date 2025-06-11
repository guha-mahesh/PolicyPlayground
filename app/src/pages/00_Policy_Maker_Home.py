from modules.nav import SideBarLinks
import streamlit as st
import logging
import requests
logger = logging.getLogger(__name__)

st.set_page_config(layout='wide')
SideBarLinks()


st.title(
    f"Welcome {st.session_state['first_name']}")

st.write('')
st.write('')
st.write('# Test your Policy')


tab1, tab2 = st.tabs(["Monetary Policy", "Fiscal Policy"])


selected_country = "Use My Nationality"


def get_monetary_policy_config(country):
    """Returns the appropriate monetary policy configuration based on country"""

    if country == "United States":
        return {
            "central_bank": "Federal Reserve",
            "rate_name": "Federal Reserve Discount Rate",
            "rate_min": 0.0,
            "rate_max": 15.0,
            "rate_default": 2.5,
            "balance_name": "Fed Balance Sheet Size",
            "balance_min": 1000,
            "balance_max": 10000,
            "balance_default": 7500,
            "securities_name": "Treasury Securities Holdings",
            "securities_min": 500,
            "securities_max": 6000,
            "securities_default": 4500,
            "currency": "$"
        }
    elif country == "United Kingdom":
        return {
            "central_bank": "Bank of England",
            "rate_name": "Bank Rate",
            "rate_min": 0.0,
            "rate_max": 15.0,
            "rate_default": 5.25,
            "balance_name": "BoE Balance Sheet Size",
            "balance_min": 500,
            "balance_max": 1500,
            "balance_default": 950,
            "securities_name": "Gilt Holdings",
            "securities_min": 300,
            "securities_max": 1000,
            "securities_default": 750,
            "currency": "£"
        }
    elif country == "Germany":
        return {
            "central_bank": "European Central Bank",
            "rate_name": "ECB Main Refinancing Rate",
            "rate_min": -1.0,
            "rate_max": 10.0,
            "rate_default": 4.5,
            "balance_name": "ECB Balance Sheet Size",
            "balance_min": 3000,
            "balance_max": 9000,
            "balance_default": 7000,
            "securities_name": "Government Bond Holdings",
            "securities_min": 2000,
            "securities_max": 6000,
            "securities_default": 4500,
            "currency": "€"
        }
    else:

        return get_monetary_policy_config("United States")


def adjust_currencies_for_country(base_currencies, user_country, discount_rate):
    """Adjust currency predictions based on the country's monetary policy"""

    adjusted_currencies = base_currencies.copy()

    if user_country == "United Kingdom":

        rate_effect = (discount_rate - 5.25) * 0.02

        gbp_to_usd = base_currencies["British Pound"]
        usd_to_gbp = 1 / gbp_to_usd

        adjusted_currencies["US Dollar"] = usd_to_gbp * (1 + rate_effect)

        del adjusted_currencies["British Pound"]

        adjusted_currencies["Euro"] = base_currencies["Euro"] * \
            (1 + rate_effect * 0.3)

        adjusted_currencies["Japanese Yen"] = base_currencies["Japanese Yen"] * \
            (1 + rate_effect * 0.1)
        adjusted_currencies["Australian Dollar"] = base_currencies["Australian Dollar"] * (
            1 - rate_effect * 0.1)

    elif user_country == "Germany":

        rate_effect = (discount_rate - 4.5) * 0.025

        eur_to_usd = base_currencies["Euro"]
        usd_to_eur = 1 / eur_to_usd

        adjusted_currencies["US Dollar"] = usd_to_eur * (1 + rate_effect)

        del adjusted_currencies["Euro"]

        adjusted_currencies["British Pound"] = base_currencies["British Pound"] * \
            (1 - rate_effect * 0.4)

        adjusted_currencies["Chinese Yuan"] = base_currencies["Chinese Yuan"] * \
            (1 + rate_effect * 0.2)
        adjusted_currencies["Japanese Yen"] = base_currencies["Japanese Yen"] * \
            (1 + rate_effect * 0.15)

    return adjusted_currencies


user_country = st.session_state.get('nationality', 'United States')
if user_country not in ["United States", "United Kingdom", "Germany"]:

    user_country = "United States"


policy_config = get_monetary_policy_config(user_country)

with tab1:
    st.write(f"#### {policy_config['central_bank']} Controls")
    st.write("")

    col1, col2 = st.columns([3, 1])
    with col1:
        discount_rate_slider = st.slider(
            f"{policy_config['rate_name']} (%)",
            min_value=policy_config['rate_min'],
            max_value=policy_config['rate_max'],
            value=policy_config['rate_default'],
            step=0.25,
            key="discount_slider"
        )
    with col2:
        discount_rate_input = st.number_input(
            "Rate",
            min_value=policy_config['rate_min'],
            max_value=policy_config['rate_max'],
            value=discount_rate_slider,
            step=0.25,
            format="%.2f",
            key="discount_input"
        )

    col3, col4 = st.columns([3, 1])
    with col3:
        fed_balance_slider = st.slider(
            f"{policy_config['balance_name']} (Billions {policy_config['currency']})",
            min_value=policy_config['balance_min'],
            max_value=policy_config['balance_max'],
            value=policy_config['balance_default'],
            step=100,
            key="balance_slider"
        )
    with col4:
        fed_balance_input = st.number_input(
            "Balance",
            min_value=policy_config['balance_min'],
            max_value=policy_config['balance_max'],
            value=fed_balance_slider,
            step=100,
            key="balance_input"
        )

    col5, col6 = st.columns([3, 1])
    with col5:
        treasury_slider = st.slider(
            f"{policy_config['securities_name']} (Billions {policy_config['currency']})",
            min_value=policy_config['securities_min'],
            max_value=policy_config['securities_max'],
            value=policy_config['securities_default'],
            step=100,
            key="treasury_slider"
        )
    with col6:
        treasury_input = st.number_input(
            "Securities",
            min_value=policy_config['securities_min'],
            max_value=policy_config['securities_max'],
            value=treasury_slider,
            step=100,
            key="treasury_input"
        )

with tab2:
    st.write("#### Government Spending Allocation")
    st.write("")

    country_options = ["Use My Nationality", "United States", "Japan", "Germany",
                       "United Kingdom", "Russia", "Canada"]
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

country_codes = {
    "United States": "USA",
    "Japan": "JPN",
    "Germany": "DEU",
    "United Kingdom": "GBR",
    "France": "FRA",
    "Russia": "RUS",
    "Canada": "CAN"
}

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
    st.write(f"• {policy_config['central_bank']} Rate: {discount_rate}%")
    st.write(f"• Balance Sheet: {policy_config['currency']}{fed_balance:,}B")
    st.write(
        f"• Securities Holdings: {policy_config['currency']}{treasury_holdings:,}B")

with col_right:
    st.write("**Fiscal Policy:**")
    st.write(f"• Country: {country}")
    st.write(f"• Military Spending: {military_spending}%")
    st.write(f"• Education Spending: {education_spending}%")
    st.write(f"• Health Spending: {health_spending}%")
tables = [
    "YuantoUSD",
    "AUDtoUSD",
    "JPYtoUSD",
    "GBPtoUSD",
    "EUROTOUSD",
    "FRBS",
    "treasurysecurities",
    "discountrate", "sp500"]


if st.button("Test Policy Set", type="primary"):
    st.session_state['policy_params'] = {
        "Discount Rate": discount_rate,
        "Federal Balance": fed_balance,
        "Treasury Holdings": treasury_holdings,
        "Military Spending": military_spending,
        "Education Spending": education_spending,
        "Health Spending": health_spending,
        "Selected Country": country,
        "Monetary Policy Country": user_country,
        "Central Bank": policy_config['central_bank'],
        "Rate Name": policy_config['rate_name'],
        "Currency": policy_config['currency']
    }

    api_url = f"http://host.docker.internal:4000/model/predictSp/{discount_rate},{treasury_holdings},{fed_balance}"
    api_url2 = f"http://host.docker.internal:4000/model/predictCurr/{discount_rate},{treasury_holdings},{fed_balance}"
    api_url3 = f"http://host.docker.internal:4000/model/predictGDP/{military_spending},{education_spending},{health_spending}/{country_codes[country]}"

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

            market_prediction = float(data['prediction'])
            gdp_prediction = float(data3['prediction'])

            base_currencies = data2['prediction']

            if user_country == "United Kingdom":

                market_prediction = market_prediction * 0.8
                market_prediction = (market_prediction / 5500) * 7800
                market_index = "FTSE"

                adjusted_currencies = adjust_currencies_for_country(
                    base_currencies, user_country, discount_rate)

            elif user_country == "Germany":

                market_prediction = market_prediction * 1.1
                market_prediction = (market_prediction / 5500) * 17000
                market_index = "DAX"

                adjusted_currencies = adjust_currencies_for_country(
                    base_currencies, user_country, discount_rate)
            else:
                market_index = "SP500"
                adjusted_currencies = base_currencies

            st.success("Prediction successful!")
            st.session_state['Predictions'] = {
                "Market": str(market_prediction),
                "Market_Index": market_index,
                "Currencies": adjusted_currencies,
                "GDP/C": str(gdp_prediction)
            }
            st.write(f"Prediction for {market_index}: {market_prediction:.2f}")
            st.switch_page("pages/44_Policy_Maker_viewPred.py")
        else:
            st.error(f"API Error: {response.status_code}")
            st.write(response.text)

    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.write(
            f"URL that worked in browser: {api_url}, {api_url2}, {api_url3}")
