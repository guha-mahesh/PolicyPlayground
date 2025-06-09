from modules.nav import SideBarLinks
import streamlit as st
import logging
import requests
import matplotlib.pyplot as plt
import numpy as np

logger = logging.getLogger(__name__)

st.set_page_config(layout='wide')

SideBarLinks()

st.title(f"Your Predictions")

sp500_pred = round(float(st.session_state['Predictions']["SP500"]), 2)
gdp_pred = round(float(st.session_state['Predictions']["GDP/C"]), 2)

col1, col2 = st.columns(2)

with col1:
    st.metric(label="📈 S&P 500 Prediction", value=f"{sp500_pred:,}")

with col2:
    st.metric(label="💰 GDP per Capita Prediction", value=f"${gdp_pred:,.2f}")


st.divider()
st.subheader("Prediction Analysis & Comparisons")


graph_col1, graph_col2 = st.columns(2)

with graph_col1:

    st.subheader("💰 GDP per Capita: Prediction vs Historical")
    fig1, ax1 = plt.subplots(figsize=(8, 5))

    years_hist = np.arange(2015, 2025)
    gdp_historical = 55000 + \
        np.cumsum(np.random.normal(2000, 1500, len(years_hist)))

    pred_year = 2025
    pred_gdp = gdp_pred

    ax1.plot(years_hist, gdp_historical, 'b-', linewidth=2,
             label='Historical GDP per Capita')
    ax1.plot([years_hist[-1], pred_year], [gdp_historical[-1],
             pred_gdp], 'r--', linewidth=2, label='Prediction')
    ax1.scatter([pred_year], [pred_gdp], color='red', s=100,
                zorder=5, label=f'Your Prediction: ${pred_gdp:,.0f}')

    ax1.set_xlabel('Year')
    ax1.set_ylabel('GDP per Capita ($)')
    ax1.set_title('GDP per Capita Prediction vs Historical Data')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    st.pyplot(fig1)

    st.subheader("🌍 GDP per Capita: Your Prediction vs World Average")
    fig3, ax3 = plt.subplots(figsize=(8, 5))

    world_gdp_historical = 45000 + \
        np.cumsum(np.random.normal(1500, 1000, len(years_hist)))
    world_gdp_pred = world_gdp_historical[-1] + 2000

    ax3.plot(years_hist, world_gdp_historical, 'g-',
             linewidth=2, label='World Average (Historical)')
    ax3.plot([years_hist[-1], pred_year], [world_gdp_historical[-1],
             world_gdp_pred], 'g--', linewidth=2, label='World Average (Projected)')
    ax3.axhline(y=pred_gdp, color='red', linestyle='-', linewidth=3,
                label=f'Your Prediction: ${pred_gdp:,.0f}')

    ax3.set_xlabel('Year')
    ax3.set_ylabel('GDP per Capita ($)')
    ax3.set_title('Your GDP Prediction vs World Average')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    st.pyplot(fig3)

with graph_col2:

    st.subheader("📈 S&P 500: Prediction vs Historical")
    fig2, ax2 = plt.subplots(figsize=(8, 5))

    sp500_historical = 3000 + \
        np.cumsum(np.random.normal(50, 200, len(years_hist)))

    ax2.plot(years_hist, sp500_historical, 'b-',
             linewidth=2, label='Historical S&P 500')
    ax2.plot([years_hist[-1], pred_year], [sp500_historical[-1],
             sp500_pred], 'r--', linewidth=2, label='Prediction')
    ax2.scatter([pred_year], [sp500_pred], color='red', s=100,
                zorder=5, label=f'Your Prediction: {sp500_pred:,.0f}')

    ax2.set_xlabel('Year')
    ax2.set_ylabel('S&P 500 Index')
    ax2.set_title('S&P 500 Prediction vs Historical Data')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    st.pyplot(fig2)

    st.subheader("🌐 S&P 500 vs URTH Historical")
    fig4, ax4 = plt.subplots(figsize=(8, 5))

    urth_historical = sp500_historical * 0.85 + \
        np.random.normal(0, 50, len(years_hist))

    ax4.plot(years_hist, sp500_historical, 'b-',
             linewidth=2, label='S&P 500 (Historical)')
    ax4.plot(years_hist, urth_historical, 'orange',
             linewidth=2, label='URTH (Historical)')
    ax4.axhline(y=sp500_pred, color='red', linestyle='-', linewidth=3,
                label=f'Your S&P 500 Prediction: {sp500_pred:,.0f}')

    ax4.set_xlabel('Year')
    ax4.set_ylabel('Index Value')
    ax4.set_title('S&P 500 vs URTH Comparison')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    st.pyplot(fig4)
if st.button("Save Policy Settings", type="secondary"):

    policy_data = {
        "discountRate": st.session_state['policy_params']["Discount Rate"],
        "federalReserveBalanceSheet": st.session_state['policy_params']["Federal Balance"],
        "treasurySecurities": st.session_state['policy_params']["Treasury Holdings"],
        "millitarySpending": st.session_state['policy_params']["Military Spending"],
        "educationSpending": st.session_state['policy_params']["Education Spending"],
        "healthSpending": st.session_state['policy_params']["Health Spending"],
        "country": st.session_state['policy_params']["Selected Country"],
        "SP500": st.session_state['Predictions']["SP500"],
        "GDP": st.session_state['Predictions']["GDP/C"]
    }

    try:

        save_url = "http://host.docker.internal:4000/politician/savePolicy"
        response = requests.post(
            save_url,
            json=policy_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

        if response.status_code == 200:
            st.success("✅ Policy settings saved successfully!")
        else:
            st.error(f"Failed to save policy: {response.status_code}")
            st.write(response.text)

    except Exception as e:
        st.error(f"Error saving policy: {str(e)}")
st.divider()

if st.button("Try a New Set"):
    st.switch_page('pages/00_Policy_Maker_Home.py')

if st.button("View Currency Forecasts"):
    st.switch_page('pages/45_Policy_Maker_Currency.py')
