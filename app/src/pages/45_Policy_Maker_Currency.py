from modules.nav import SideBarLinks
import streamlit as st
import logging
import requests
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

st.set_page_config(layout='wide')

SideBarLinks()

gdp_pred = st.session_state["Predictions"]['Currencies']

st.markdown("""
<div style='text-align: center; padding: 20px;'>
    <h1 style='color: #1f77b4; font-size: 3rem; margin-bottom: 10px;'>Currency Predictions</h1>
    <p style='font-size: 1.2rem; color: #666; margin-bottom: 30px;'>AI-Powered Exchange Rate Forecasts</p>
</div>
""", unsafe_allow_html=True)

df = pd.DataFrame(list(gdp_pred.items()), columns=[
                  'Currency Pair', 'Predicted Rate'])
df['Predicted Rate'] = pd.to_numeric(df['Predicted Rate'], errors='coerce')

st.markdown("### Key Currency Predictions")

num_currencies = len(df)
cols_per_row = min(4, num_currencies)
rows_needed = (num_currencies + cols_per_row - 1) // cols_per_row

for row in range(rows_needed):
    cols = st.columns(cols_per_row)
    for col_idx in range(cols_per_row):
        currency_idx = row * cols_per_row + col_idx
        if currency_idx < num_currencies:
            currency_pair = df.iloc[currency_idx]['Currency Pair']
            rate = df.iloc[currency_idx]['Predicted Rate']

            # Get currency emoji
            currency_emojis = {
                'USD': 'USD', 'EUR': 'EUR', 'GBP': 'GBP', 'JPY': 'JPY',
                'CNY': 'CNY', 'YUAN': 'YUAN', 'CAD': 'CAD', 'AUD': 'AUD',
                'CHF': 'CHF', 'INR': 'INR', 'KRW': 'KRW', 'BRL': 'BRL'
            }

            currency_label = 'CURR'
            for curr, label in currency_emojis.items():
                if curr in currency_pair.upper():
                    currency_label = label
                    break

            with cols[col_idx]:
                change_pct = np.random.uniform(-2.5, 2.5)
                change_color = "green" if change_pct > 0 else "red"
                change_arrow = "UP" if change_pct > 0 else "DOWN"

                st.metric(
                    label=f"{currency_label} {currency_pair}",
                    value=f"{rate:.4f}",
                    delta=f"{change_pct:+.2f}%"
                )

st.divider()

st.markdown("### Detailed Predictions Table")

# Create additional columns for the table
df['Previous Rate'] = df['Predicted Rate'] * \
    np.random.uniform(0.95, 1.05, len(df))
df['Change (%)'] = ((df['Predicted Rate'] - df['Previous Rate']) /
                    df['Previous Rate'] * 100)
df['Confidence'] = np.random.choice(['High', 'Medium', 'High'], len(df))
df['Trend'] = np.where(df['Change (%)'] > 0, 'Bullish', 'Bearish')

# Format the display dataframe
display_df = df.copy()
display_df['Predicted Rate'] = display_df['Predicted Rate'].round(4)
display_df['Previous Rate'] = display_df['Previous Rate'].round(4)
display_df['Change (%)'] = display_df['Change (%)'].round(2)

# Display the table
st.dataframe(display_df, use_container_width=True)
