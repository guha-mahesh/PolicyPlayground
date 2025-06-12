import streamlit as st
from modules.nav import SideBarLinks
from modules.theme import *

custom_style()
SideBarLinks()

# Get policy data first
policy_data = st.session_state.get('published_policy', {})

st.markdown("""
<style>
    /* Currency display styling */
    .currency-header {
        background: #1e293b;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        color: #e2e8f0;
        text-align: center;
    }
    
    .currency-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .currency-card {
        background: #18435a;
        border: none;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .currency-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    .currency-flag {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .currency-name {
        color: #e2e8f0;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .currency-rate {
        color: #e2e8f0;
        font-size: 1.5rem;
        font-weight: bold;
    }
    
    .base-currency-info {
        background: #1e293b;
        border: none;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        text-align: center;
        color: #e2e8f0;
    }
    
    .policy-params-section {
        background: #18435a;
        border: none;
        padding: 2rem;
        border-radius: 12px;
        margin-top: 2rem;
    }
    
    .policy-params-header {
        color: #e2e8f0;
        margin: 0 0 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

if 'predictionsCurrency' not in st.session_state or not st.session_state['predictionsCurrency']:
    st.error(
        "No currency predictions available. Please go back and select a policy to analyze.")
    st.stop()

currency_predictions = st.session_state['predictionsCurrency']
analysis_country = policy_data.get('Selected Country', 'United States')
user_nationality = st.session_state.get('nationality', 'United States')

# Determine base currency based on analysis country
if analysis_country == "United Kingdom":
    base_currency = "GBP"
    base_currency_name = "British Pound"
    base_symbol = "£"
elif analysis_country == "Germany":
    base_currency = "EUR"
    base_currency_name = "Euro"
    base_symbol = "€"
else:
    base_currency = "USD"
    base_currency_name = "US Dollar"
    base_symbol = "$"

currency_info = {
    "US Dollar": {"symbol": "$", "flag": "🇺🇸", "code": "USD"},
    "Euro": {"symbol": "€", "flag": "🇪🇺", "code": "EUR"},
    "Japanese Yen": {"symbol": "¥", "flag": "🇯🇵", "code": "JPY"},
    "British Pound": {"symbol": "£", "flag": "🇬🇧", "code": "GBP"},
    "Australian Dollar": {"symbol": "A$", "flag": "🇦🇺", "code": "AUD"},
    "Canadian Dollar": {"symbol": "C$", "flag": "🇨🇦", "code": "CAD"},
    "Swiss Franc": {"symbol": "CHF", "flag": "🇨🇭", "code": "CHF"},
    "Chinese Yuan": {"symbol": "¥", "flag": "🇨🇳", "code": "CNY"},
    "Swedish Krona": {"symbol": "kr", "flag": "🇸🇪", "code": "SEK"},
    "New Zealand Dollar": {"symbol": "NZ$", "flag": "🇳🇿", "code": "NZD"}
}

st.markdown(f"""
    <div class='currency-header'>
        <h1 style='margin: 0; color: #e2e8f0;'>💱 Currency Exchange Rate Predictions</h1>
        <p style='margin: 0.5rem 0 0 0; color: #e2e8f0;'>Based on Policy Analysis for {analysis_country}</p>
    </div>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class='base-currency-info'>
        <h3 style='color: #e2e8f0; margin: 0;'>Exchange Rates per 1 {base_currency_name} ({base_symbol}1.00)</h3>
        <p style='margin: 0.5rem 0 0 0; color: #e2e8f0;'>Predictions based on monetary policy with {policy_data.get('Discount Rate', 'N/A')}% discount rate</p>
    </div>
""", unsafe_allow_html=True)

cols = st.columns(3)
currency_items = list(currency_predictions.items())

i = 0
for idx, (currency_name, rate) in enumerate(currency_items):
    col_idx = idx % 3
    with cols[col_idx]:
        info = currency_info.get(
            currency_name, {"symbol": "", "flag": "🌐", "code": "???"})

        if currency_name == "Japanese Yen":
            formatted_rate = f"{rate:.2f}"
        elif rate < 1:
            formatted_rate = f"{rate:.4f}"
        else:
            formatted_rate = f"{rate:.3f}"

        st.markdown(f"""
            <div class='currency-card'>
                <div class='currency-flag'>{info['flag']}</div>
                <div class='currency-name'>{currency_name}</div>
                <div class='currency-rate'>{info['symbol']}{formatted_rate}</div>
                <div style='color: #e2e8f0; font-size: 0.9rem; margin-top: 0.5rem;'>{info['code']}</div>
            </div>
        """, unsafe_allow_html=True)
        if i > 2:
            st.write("\n\n\n")
        i += 1

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    st.write("\n\n\n")
    st.write("\n\n\n")
    if st.button("← Back to Policies", type="secondary", use_container_width=True):
        st.switch_page("pages/33_Economist_viewPolicy.py")

if st.button("View GDP and Market Predictions", type="primary", use_container_width=True):
    st.switch_page("pages/35_Economist_ViewPred.py")
