from modules.theme import custom_style
from modules.nav import SideBarLinks
from modules.theme import welcome_banner, logOut
import streamlit as st
import logging
import requests
logger = logging.getLogger(__name__)

st.set_page_config(layout='wide')
custom_style()
SideBarLinks()

logOut()


# Custom CSS for enhanced styling
st.markdown("""
<style>
    /* Enhanced header styling */
    .policy-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        position: relative;
        overflow: hidden;
    }
    
    .policy-header::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 200px;
        height: 200px;
        background: rgba(255,255,255,0.05);
        border-radius: 50%;
        transform: translate(50px, -50px);
    }
    
    /* Nationality selector styling */
    .nationality-container {
        background: #f8fafc;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    .nationality-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    .nationality-header h4 {
        color: #1e293b;
        margin: 0;
        font-weight: 600;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #f1f5f9;
        border-radius: 10px;
        padding: 0.25rem;
        gap: 0.5rem;
        
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        color: #64748b;
        font-weight: 500;
        transition: all 0.3s ease;
        padding: 2rem;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e2e8f0;
        color: #1e293b;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white !important;
        color: #1e3a8a !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Enhanced section headers */
    .section-header {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Policy display cards */
    .policy-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        border: 1px solid #334155;
        transition: transform 0.3s ease;
    }
    
    .policy-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    
            
</style>
""", unsafe_allow_html=True)

welcome_banner()

# Get user's nationality
user_country = st.session_state.get('nationality', 'United States')
if user_country not in ["United States", "United Kingdom", "Germany"]:
    user_country = "United States"

# Country selector above tabs
st.markdown("""
    <div class='nationality-container'>
        <div class='nationality-header'>
            <span style='font-size: 1.5rem;'></span>
            <h4>Policy Analysis Country</h4>
        </div>
        <p style='color: #64748b; margin: 0 0 1rem 0;'>Select a country for comparative analysis, or use your default nationality</p>
    </div>
""", unsafe_allow_html=True)

# Country selection dropdown
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    country_options = ["Use My Nationality",
                       "United States", "Germany", "United Kingdom"]
    selected_country = st.selectbox(
        "Country for Analysis",
        options=country_options,
        index=0,
        help=f"Your nationality: {user_country}. Choose a different country for comparative analysis.",
        key="country_selector"
    )

# Determine the actual country to use
if selected_country == "Use My Nationality":
    analysis_country = user_country
else:
    analysis_country = selected_country


with col3:
    st.metric("Analysis Country", analysis_country, delta=None)

# Create tabs
tab1, tab2 = st.tabs(["Monetary Policy", "Fiscal Policy"])

# Helper functions


def get_monetary_policy_config(country):
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


# Get policy configuration based on user's nationality
policy_config = get_monetary_policy_config(user_country)

# Monetary Policy Tab
with tab1:
    st.markdown(f"""
        <div class='section-header'>
            <h3 style='color: #e2e8f0; margin: 0;'>{policy_config['central_bank']} Controls</h3>
            <p style='color: #94a3b8; margin: 0.5rem 0 0 0;'>Adjust monetary policy parameters to influence economic outcomes</p>
        </div>
    """, unsafe_allow_html=True)

    # Discount Rate
    col1, col2 = st.columns([3, 1])
    with col1:
        discount_rate_slider = st.slider(
            f"{policy_config['rate_name']} (%)",
            min_value=policy_config['rate_min'],
            max_value=policy_config['rate_max'],
            value=policy_config['rate_default'],
            step=0.25,
            key="discount_slider",
            help="Adjust the central bank's key interest rate to influence borrowing costs and economic activity"
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

    # Balance Sheet
    col3, col4 = st.columns([3, 1])
    with col3:
        fed_balance_slider = st.slider(
            f"{policy_config['balance_name']} (Billions {policy_config['currency']})",
            min_value=policy_config['balance_min'],
            max_value=policy_config['balance_max'],
            value=policy_config['balance_default'],
            step=100,
            key="balance_slider",
            help="Control the size of the central bank's balance sheet to influence money supply"
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

    # Securities Holdings
    col5, col6 = st.columns([3, 1])
    with col5:
        treasury_slider = st.slider(
            f"{policy_config['securities_name']} (Billions {policy_config['currency']})",
            min_value=policy_config['securities_min'],
            max_value=policy_config['securities_max'],
            value=policy_config['securities_default'],
            step=100,
            key="treasury_slider",
            help="Manage government securities holdings to influence long-term interest rates"
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

    # Federal Funds Rate
    col13, col14 = st.columns([3, 1])
    with col13:
        fed_funds_slider = st.slider(
            "Federal Funds Rate (%)",
            min_value=0.00,
            max_value=10.00,
            value=2.50,
            step=0.25,
            key="fed_funds_slider"
        )
    with col14:
        fed_funds_input = st.number_input(
            "Fed Funds Rate",
            min_value=0.00,
            max_value=10.00,
            value=fed_funds_slider,
            step=0.25,
            format="%.2f",
            key="fed_funds_input"
        )

    # Money Supply
    col15, col16 = st.columns([3, 1])
    with col15:
        money_supply_slider = st.slider(
            "Money Supply (Billions)",
            min_value=0,
            max_value=50000,
            value=20000,
            step=500,
            key="money_supply_slider"
        )
    with col16:
        money_supply_input = st.number_input(
            "Money Supply",
            min_value=0,
            max_value=50000,
            value=money_supply_slider,
            step=500,
            key="money_supply_input"
        )

    # Reserve Requirement Ratio
    col17, col18 = st.columns([3, 1])
    with col17:
        reserve_ratio_slider = st.slider(
            "Reserve Requirement Ratio (%)",
            min_value=0.00,
            max_value=20.00,
            value=10.00,
            step=0.25,
            key="reserve_ratio_slider"
        )
    with col18:
        reserve_ratio_input = st.number_input(
            "Reserve Ratio",
            min_value=0.00,
            max_value=20.00,
            value=reserve_ratio_slider,
            step=0.25,
            format="%.2f",
            key="reserve_ratio_input"
        )

# Fiscal Policy Tab
with tab2:
    st.markdown("""
        <div class='section-header'>
            <h3 style='color: #e2e8f0; margin: 0;'>Government Spending Allocation</h3>
            <p style='color: #94a3b8; margin: 0.5rem 0 0 0;'>Configure fiscal policy parameters to shape economic growth and development</p>
        </div>
    """, unsafe_allow_html=True)

    # Military Spending
    col7, col8 = st.columns([3, 1])
    with col7:
        military_slider = st.slider(
            "Military Spending (% of Government Expenditure)",
            min_value=0.0,
            max_value=20.0,
            value=3.0,
            step=0.1,
            key="military_slider",
            help="Allocate government spending to defense and security"
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

    # Education Spending
    col9, col10 = st.columns([3, 1])
    with col9:
        education_slider = st.slider(
            "Education Spending (% of GDP)",
            min_value=0.0,
            max_value=20.0,
            value=5.0,
            step=0.1,
            key="education_slider",
            help="Invest in education to develop human capital and future productivity"
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

    # Health Spending
    col11, col12 = st.columns([3, 1])
    with col11:
        health_slider = st.slider(
            "Health Spending (% of GDP)",
            min_value=0.0,
            max_value=15.0,
            value=8.0,
            step=0.1,
            key="health_slider",
            help="Allocate resources to healthcare to improve population health and productivity"
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

    # Debt-to-GDP Ratio
    col19, col20 = st.columns([3, 1])
    with col19:
        debt_gdp_slider = st.slider(
            "Debt-to-GDP Ratio (%)",
            min_value=0.00,
            max_value=150.00,
            value=90.00,
            step=1.0,
            key="debt_gdp_slider"
        )
    with col20:
        debt_gdp_input = st.number_input(
            "Debt/GDP",
            min_value=0.00,
            max_value=150.00,
            value=debt_gdp_slider,
            step=1.0,
            format="%.2f",
            key="debt_gdp_input"
        )

    # Infrastructure Spending
    col21, col22 = st.columns([3, 1])
    with col21:
        infrastructure_slider = st.slider(
            "Infrastructure Spending (% of GDP)",
            min_value=0.00,
            max_value=20.00,
            value=5.00,
            step=0.1,
            key="infrastructure_slider"
        )
    with col22:
        infrastructure_input = st.number_input(
            "Infrastructure",
            min_value=0.00,
            max_value=20.00,
            value=infrastructure_slider,
            step=0.1,
            format="%.2f",
            key="infrastructure_input"
        )

    # Corporate Tax Rate
    col23, col24 = st.columns([3, 1])
    with col23:
        corp_tax_slider = st.slider(
            "Corporate Tax Rate (%)",
            min_value=0.00,
            max_value=50.00,
            value=25.00,
            step=0.5,
            key="corp_tax_slider"
        )
    with col24:
        corp_tax_input = st.number_input(
            "Corporate Tax",
            min_value=0.00,
            max_value=50.00,
            value=corp_tax_slider,
            step=0.5,
            format="%.2f",
            key="corp_tax_input"
        )

# Collect all values
discount_rate = discount_rate_input or discount_rate_slider
fed_balance = fed_balance_input or fed_balance_slider
treasury_holdings = treasury_input or treasury_slider
military_spending = military_input or military_slider
education_spending = education_input or education_slider
health_spending = health_input or health_slider
fed_funds_rate = fed_funds_input or fed_funds_slider
money_supply = money_supply_input or money_supply_slider
reserve_ratio = reserve_ratio_input or reserve_ratio_slider
infrastructure_spending = infrastructure_input or infrastructure_slider
debt_gdp_ratio = debt_gdp_input or debt_gdp_slider
corporate_tax_rate = corp_tax_input or corp_tax_slider

# Country codes for API
country_codes = {
    "United States": "USA",
    "Japan": "JPN",
    "Germany": "DEU",
    "United Kingdom": "GBR",
    "France": "FRA",
    "Russia": "RUS",
    "Canada": "CAN"
}

# Policy Summary Section
st.markdown("""
    <div style='background: #1e293b; padding: 1.5rem; border-radius: 8px; margin: 2rem 0;'>
        <h3 style='color: #e2e8f0; margin: 0;'>Current Policy Settings</h3>
        <p style='color: #94a3b8; margin: 0.5rem 0 0 0;'>Review your selected policy parameters</p>
    </div>
""", unsafe_allow_html=True)

col_left, col_right = st.columns(2)

with col_left:
    st.markdown(f"""
        <div class='policy-card'>
            <h4 style='color: #e2e8f0; margin: 0 0 0.5rem 0;'>💰 Monetary Policy</h4>
            <p style='color: #94a3b8; margin: 0;'>• {policy_config['rate_name']}: {discount_rate}%</p>
            <p style='color: #94a3b8; margin: 0;'>• Balance Sheet: {policy_config['currency']}{fed_balance:,}B</p>
            <p style='color: #94a3b8; margin: 0;'>• Securities Holdings: {policy_config['currency']}{treasury_holdings:,}B</p>
            <p style='color: #94a3b8; margin: 0;'>• Federal Funds Rate: {fed_funds_rate}%</p>
            <p style='color: #94a3b8; margin: 0;'>• Money Supply: {policy_config['currency']}{money_supply:,}B</p>
            <p style='color: #94a3b8; margin: 0;'>• Reserve Requirement: {reserve_ratio}%</p>
        </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown(f"""
        <div class='policy-card'>
            <h4 style='color: #e2e8f0; margin: 0 0 0.5rem 0;'>📊 Fiscal Policy</h4>
            <p style='color: #94a3b8; margin: 0;'>• Analysis Country: {analysis_country}</p>
            <p style='color: #94a3b8; margin: 0;'>• Military Spending: {military_spending}%</p>
            <p style='color: #94a3b8; margin: 0;'>• Education Spending: {education_spending}%</p>
            <p style='color: #94a3b8; margin: 0;'>• Health Spending: {health_spending}%</p>
            <p style='color: #94a3b8; margin: 0;'>• Infrastructure Spending: {infrastructure_spending}%</p>
            <p style='color: #94a3b8; margin: 0;'>• Debt-to-GDP Ratio: {debt_gdp_ratio}%</p>
            <p style='color: #94a3b8; margin: 0;'>• Corporate Tax Rate: {corporate_tax_rate}%</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Test Policy Button
if st.button("🚀 Test Policy Set", type="primary", use_container_width=True):
    st.session_state['policy_params'] = {
        "Discount Rate": discount_rate,
        "Federal Balance": fed_balance,
        "Treasury Holdings": treasury_holdings,
        "Military Spending": military_spending,
        "Education Spending": education_spending,
        "Health Spending": health_spending,
        "Selected Country": analysis_country,
        "Monetary Policy Country": user_country,
        "Central Bank": policy_config['central_bank'],
        "Rate Name": policy_config['rate_name'],
        "Currency": policy_config['currency'],
        "Federal Funds Rate": fed_funds_rate,
        "Money Supply": money_supply,
        "Reserve Requirement Ratio": reserve_ratio,
        "Infrastructure Spending": infrastructure_spending,
        "Debt to GDP Ratio": debt_gdp_ratio,
        "Corporate Tax Rate": corporate_tax_rate
    }

    # API calls
    api_url = f"http://host.docker.internal:4000/model/SP500/{discount_rate},{treasury_holdings},{fed_balance}"
    api_url2 = f"http://host.docker.internal:4000/model/currency/{discount_rate},{treasury_holdings},{fed_balance}"
    api_url3 = f"http://host.docker.internal:4000/model/GDP/{health_spending},{education_spending},{military_spending}/{country_codes[analysis_country]}"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Connection': 'keep-alive'
        }

        with st.spinner('🔄 Running policy analysis...'):
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

            # Adjust market prediction based on user's nationality
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

            st.success("✅ Prediction successful!")
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
