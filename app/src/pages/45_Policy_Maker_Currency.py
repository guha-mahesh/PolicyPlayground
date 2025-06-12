from modules.nav import SideBarLinks
import streamlit as st
import logging
import requests
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import json
from modules.theme import custom_style


logger = logging.getLogger(__name__)

st.set_page_config(layout='wide')
custom_style()
SideBarLinks()


def fetch_current_rates():
    try:
        api_url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(api_url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            return {
                'EUR': data['rates']['EUR'],
                'GBP': data['rates']['GBP'],
                'JPY': data['rates']['JPY'],
                'CNY': data['rates']['CNY'],
                'AUD': data['rates']['AUD']
            }
        else:
            st.warning("Could not fetch current rates, using fallback values")
            return None
    except Exception as e:
        st.warning(f"Error fetching rates: {str(e)}")
        return None


current_rates = fetch_current_rates()

if current_rates is None:
    current_rates = {
        'EUR': 0.92,
        'GBP': 0.79,
        'JPY': 149.50,
        'CNY': 7.24,
        'AUD': 1.52
    }

user_country = st.session_state['policy_params'].get(
    'Monetary Policy Country', 'United States')

currency_preds = st.session_state["Predictions"]['Currencies'].copy()

if user_country != "Germany" and "Euro" in currency_preds:
    currency_preds["Euro"] = 1 / currency_preds["Euro"]

if user_country != "United Kingdom" and "British Pound" in currency_preds:
    currency_preds["British Pound"] = 1 / currency_preds["British Pound"]

if "Australian Dollar" in currency_preds:
    currency_preds["Australian Dollar"] = 1 / \
        currency_preds["Australian Dollar"]

if user_country == "United States":
    title_suffix = "USD Exchange Rates"

elif user_country == "United Kingdom":
    if 'British Pound' in currency_preds:
        currency_preds['US Dollar'] = 1 / currency_preds['British Pound']
        currency_preds.pop('British Pound', None)

    if 'Euro' in currency_preds:
        eur_to_usd = currency_preds['Euro']
        usd_to_gbp = current_rates['GBP']
        currency_preds['Euro'] = eur_to_usd * usd_to_gbp
    title_suffix = "GBP Exchange Rates"

elif user_country == "Germany":
    if 'Euro' in currency_preds:
        currency_preds['US Dollar'] = 1 / currency_preds['Euro']
        currency_preds.pop('Euro', None)

    if 'British Pound' in currency_preds:
        gbp_to_usd = currency_preds['British Pound']
        usd_to_eur = current_rates['EUR']
        currency_preds['British Pound'] = gbp_to_usd * usd_to_eur
    title_suffix = "EUR Exchange Rates"

st.markdown(f"""
<div style='text-align: center; padding: 20px;'>
    <h1 style='color: #1f77b4; font-size: 3rem; margin-bottom: 10px;'>Currency Predictions</h1>
    <p style='font-size: 1.2rem; color: #666; margin-bottom: 30px;'>AI-Powered {title_suffix} Forecasts vs Current Market Rates</p>
</div>
""", unsafe_allow_html=True)

df_data = []
for currency, predicted_rate in currency_preds.items():
    currency_code_map = {
        'Euro': 'EUR',
        'British Pound': 'GBP',
        'Japanese Yen': 'JPY',
        'Chinese Yuan': 'CNY',
        'Australian Dollar': 'AUD',
        'US Dollar': 'USD'
    }

    currency_code = currency_code_map.get(currency)

    if user_country == "United States":
        current_rate = current_rates.get(currency_code, predicted_rate)
        if currency == "Euro":
            label = "USD/EUR"
        elif currency == "British Pound":
            label = "USD/GBP"
        elif currency == "Japanese Yen":
            label = "USD/JPY"
        elif currency == "Chinese Yuan":
            label = "USD/CNY"
        elif currency == "Australian Dollar":
            label = "USD/AUD"
        else:
            label = currency

    elif user_country == "United Kingdom":
        if currency == "US Dollar":
            label = "GBP/USD"
            current_rate = 1 / current_rates.get('GBP', 0.79)
        elif currency_code and currency_code != 'GBP':
            usd_rate = current_rates.get(currency_code, 1)
            gbp_rate = current_rates.get('GBP', 0.79)
            current_rate = usd_rate / gbp_rate

            if currency == "Euro":
                label = "GBP/EUR"
            elif currency == "Japanese Yen":
                label = "GBP/JPY"
            elif currency == "Chinese Yuan":
                label = "GBP/CNY"
            elif currency == "Australian Dollar":
                label = "GBP/AUD"
            else:
                label = currency
        else:
            current_rate = predicted_rate
            label = currency

    elif user_country == "Germany":
        if currency == "US Dollar":
            label = "EUR/USD"
            current_rate = 1 / current_rates.get('EUR', 0.92)
        elif currency_code and currency_code != 'EUR':
            usd_rate = current_rates.get(currency_code, 1)
            eur_rate = current_rates.get('EUR', 0.92)
            current_rate = usd_rate / eur_rate

            if currency == "British Pound":
                label = "EUR/GBP"
            elif currency == "Japanese Yen":
                label = "EUR/JPY"
            elif currency == "Chinese Yuan":
                label = "EUR/CNY"
            elif currency == "Australian Dollar":
                label = "EUR/AUD"
            else:
                label = currency
        else:
            current_rate = predicted_rate
            label = currency
    else:
        current_rate = current_rates.get(currency_code, predicted_rate)
        label = currency

    df_data.append([label, predicted_rate, current_rate])

df = pd.DataFrame(df_data, columns=[
                  'Currency Pair', 'Predicted Rate', 'Current Rate'])
df['Predicted Rate'] = pd.to_numeric(df['Predicted Rate'], errors='coerce')
df['Current Rate'] = pd.to_numeric(df['Current Rate'], errors='coerce')

df['Change (%)'] = ((df['Predicted Rate'] - df['Current Rate']) /
                    df['Current Rate'] * 100)

st.markdown("### Key Currency Predictions")

if current_rates:
    st.caption(
        f"Current rates fetched at: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")

base_currency_symbol = {
    "United States": "🇺🇸",
    "United Kingdom": "🇬🇧",
    "Germany": "🇪🇺"
}.get(user_country, "💱")

num_currencies = len(df)
cols_per_row = min(4, num_currencies)
rows_needed = (num_currencies + cols_per_row - 1) // cols_per_row

for row in range(rows_needed):
    cols = st.columns(cols_per_row)
    for col_idx in range(cols_per_row):
        currency_idx = row * cols_per_row + col_idx
        if currency_idx < num_currencies:
            currency_pair = df.iloc[currency_idx]['Currency Pair']
            predicted_rate = df.iloc[currency_idx]['Predicted Rate']
            current_rate = df.iloc[currency_idx]['Current Rate']
            change_pct = df.iloc[currency_idx]['Change (%)']

            currency_emojis = {
                'USD': '🇺🇸', 'EUR': '🇪🇺', 'GBP': '🇬🇧', 'JPY': '🇯🇵',
                'CNY': '🇨🇳', 'YUAN': '🇨🇳', 'CAD': '🇨🇦', 'AUD': '🇦🇺',
                'CHF': '🇨🇭', 'INR': '🇮🇳', 'KRW': '🇰🇷', 'BRL': '🇧🇷'
            }

            emoji = base_currency_symbol
            for curr, flag in currency_emojis.items():
                if curr in currency_pair.upper() and currency_pair.split('/')[0] != curr:
                    emoji = flag
                    break

            with cols[col_idx]:
                st.metric(
                    label=f"{emoji} {currency_pair}",
                    value=f"{predicted_rate:.4f}",
                    delta=f"{change_pct:+.2f}% vs current",
                    help=f"Current rate: {current_rate:.4f}"
                )

st.divider()

st.markdown("### Detailed Predictions vs Market Rates")

df['Direction'] = np.where(df['Predicted Rate'] >
                           df['Current Rate'], '📈 Higher', '📉 Lower')

df['Base Currency'] = {
    "United States": "USD",
    "United Kingdom": "GBP",
    "Germany": "EUR"
}.get(user_country, "USD")

display_df = df.copy()
display_df['Predicted Rate'] = display_df['Predicted Rate'].round(4)
display_df['Current Rate'] = display_df['Current Rate'].round(4)
display_df['Change (%)'] = display_df['Change (%)'].round(2)

display_df = display_df[['Currency Pair', 'Base Currency', 'Predicted Rate',
                         'Current Rate', 'Change (%)', 'Direction']]

st.dataframe(
    display_df,
    use_container_width=True,
    column_config={
        "Currency Pair": st.column_config.TextColumn("Currency Pair", width="medium"),
        "Base Currency": st.column_config.TextColumn("Base", width="small"),
        "Predicted Rate": st.column_config.NumberColumn("Predicted Rate", format="%.4f"),
        "Current Rate": st.column_config.NumberColumn("Current Rate", format="%.4f"),
        "Change (%)": st.column_config.NumberColumn("Diff %", format="%.2f%%"),
        "Direction": st.column_config.TextColumn("Direction", width="small"),
    }
)

with st.expander("📊 Understanding Exchange Rates"):
    col1, col2 = st.columns(2)

    with col1:
        st.write("**About the Predictions:**")
        if user_country == "United Kingdom":
            st.write("""
            - **GBP/USD**: How many US Dollars per British Pound
            - **GBP/EUR**: How many Euros per British Pound
            - Higher values mean a stronger Pound Sterling
            """)
        elif user_country == "Germany":
            st.write("""
            - **EUR/USD**: How many US Dollars per Euro
            - **EUR/GBP**: How many British Pounds per Euro
            - Higher values mean a stronger Euro
            """)
        else:
            st.write("""
            - **USD/EUR**: How many Euros per US Dollar
            - **USD/GBP**: How many British Pounds per US Dollar
            - Higher values mean a stronger US Dollar
            """)

    with col2:
        st.write("**Data Sources:**")
        st.write("""
        - Current rates: Live market data
        - Predictions: AI model based on monetary policy inputs
        """)


if st.button("Back to Policy Results"):
    st.switch_page("pages/44_Policy_Maker_viewPred.py")
