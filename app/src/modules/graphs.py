import streamlit as st
import logging
import requests
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from requestfunctions import getmethods

def sp500graph():

    policy = st.session_state['cur_policy']

    selected_country = policy['Selected Country']

    market_indices = {
        "USA": "SP500",
        "United Kingdom": "FTSE",
        "Great Britain": "FTSE",
        "Germany": "DAX",
        "Japan": "NIKKEI",
        "China": "SSE"
    }


    market_index = market_indices.get(selected_country, "SP500")


    market_pred = round(float(policy['SP500']), 2)


    gdp_pred = round(float(policy["GDP"]), 2)


    col1, col2 = st.columns(2)

    api_endpoints = {
        "SP500": "sp500",
        "FTSE": "ftse",
        "DAX": "dax",
        "NIKKEI": "nikkei",
        "SSE": "sse"
    }

    endpoint = api_endpoints.get(market_index, "sp500")
    API_URL = f"http://web-api:4000/model/data/{endpoint}"

    try:
        response = requests.get(API_URL)
        response.raise_for_status()

        data = response.json()

        if isinstance(data, dict):
            possible_keys = ['data', 'results', 'records', 'items', 'rows']
            actual_data = None

            for key in possible_keys:
                if key in data:
                    actual_data = data[key]
                    break

            if actual_data is None:
                actual_data = data
        else:
            actual_data = data

        df = pd.DataFrame(actual_data)

        df['mos'] = pd.to_datetime(df['mos'])
        df['vals'] = pd.to_numeric(df['vals'])

        df = df.sort_values('mos')

        start_date = pd.Timestamp('2025-01-01')
        end_date = pd.Timestamp('2025-06-30')

        df_filtered = df[(df['mos'] >= start_date) & (df['mos'] <= end_date)]

        if df_filtered.empty:
            current_date = df['mos'].max()
            six_months_ago = current_date - timedelta(days=180)
            df_filtered = df[df['mos'] >= six_months_ago]

        market_last_value = df_filtered['vals'].iloc[-1] if not df_filtered.empty else None

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df_filtered['mos'],
            y=df_filtered['vals'],
            mode='lines',
            line=dict(color='#64B5F6', width=3),
            name='Historical',
            showlegend=False
        ))

        last_date = df_filtered['mos'].max()
        last_value = df_filtered[df_filtered['mos']
                                 == last_date]['vals'].iloc[0]

        prediction_date = last_date + pd.DateOffset(months=1)

        fig.add_trace(go.Scatter(
            x=[prediction_date],
            y=[market_pred],
            mode='markers+text',
            marker=dict(
                size=12,
                color='#ff4444',
                symbol='circle',
                line=dict(color='white', width=2)
            ),
            name=f'Prediction {market_index}',
            showlegend=False
        ))

        y_min = min(df_filtered['vals'].min(), market_pred) * 0.98
        y_max = max(df_filtered['vals'].max(), market_pred) * 1.02

        fig.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=10, b=20),
            plot_bgcolor='#1e293b',
            paper_bgcolor='#1e293b',
            font=dict(color='#94a3b8'),
            xaxis=dict(
                showgrid=False,
                showticklabels=True,
                tickformat='%b %Y',
                tickfont=dict(size=10),
                zeroline=False,
                showline=False,
                range=[df_filtered['mos'].min() - pd.DateOffset(days=15),
                       prediction_date + pd.DateOffset(days=15)]
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='#334155',
                showticklabels=True,
                tickformat=',.0f',
                tickfont=dict(size=10),
                zeroline=False,
                showline=False,
                range=[y_min, y_max]
            )
        )

        st.plotly_chart(fig, use_container_width=True,
                        config={'displayModeBar': False})

    except Exception as e:
        st.error(f"Error fetching {market_index} data: {str(e)}")

def GDPgraph():

    policy = getmethods.getPolicy(st.session_state["current_convo"]["saved_id"]).json()[0]

    selected_country = policy['Country']

    market_indices = {
        "USA": "SP500",
        "United Kingdom": "FTSE",
        "Great Britain": "FTSE",
        "Germany": "DAX",
        "Japan": "NIKKEI",
        "China": "SSE"
    }


    market_index = market_indices.get(selected_country, "SP500")


    market_pred = round(float(policy['SP500']), 2)


    gdp_pred = round(float(policy["GDP"]), 2)


    col1, col2 = st.columns(2)
    country_for_api = selected_country.replace(' ', '')
    if selected_country == "Great Britain":
        country_for_api = "UnitedKingdom"

    GDP_API_URL = f"http://web-api:4000/model/countryGDP/{country_for_api}"

    try:
        response = requests.get(GDP_API_URL)
        response.raise_for_status()

        data = response.json()

        if data.get('success'):
            actual_data = data.get('data', [])
        else:
            actual_data = []

        df_gdp = pd.DataFrame(actual_data)

        df_gdp['mos'] = pd.to_datetime(df_gdp['mos'], format='%Y')
        df_gdp['vals'] = pd.to_numeric(df_gdp['vals'])

        df_gdp = df_gdp.sort_values('mos')

        current_year = datetime.now().year
        five_years_ago = current_year - 5
        df_gdp_filtered = df_gdp[df_gdp['mos'].dt.year >= five_years_ago]
        gdp_last_value = df_gdp_filtered['vals'].iloc[-1] if not df_gdp_filtered.empty else None

        fig2 = go.Figure()

        fig2.add_trace(go.Scatter(
            x=df_gdp_filtered['mos'],
            y=df_gdp_filtered['vals'],
            mode='lines+markers',
            line=dict(color='#81C784', width=3),
            marker=dict(size=6, color='#81C784'),
            showlegend=False
        ))

        last_date_gdp = df_gdp_filtered['mos'].max()
        next_year = last_date_gdp + pd.DateOffset(years=1)

        fig2.add_trace(go.Scatter(
            x=[next_year],
            y=[gdp_pred],
            mode='markers',
            marker=dict(
                size=12,
                color='#ff4444',
                symbol='circle',
                line=dict(color='white', width=2)
            ),
            name='Prediction GDP per Capita',
            showlegend=False
        ))

        y_min = df_gdp_filtered['vals'].min() * 0.9
        y_max = max(df_gdp_filtered['vals'].max(), gdp_pred) * 1.1

        fig2.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=10, b=20),
            plot_bgcolor='#1e293b',
            paper_bgcolor='#1e293b',
            font=dict(color='#94a3b8'),
            xaxis=dict(
                showgrid=False,
                showticklabels=True,
                tickformat='%Y',
                tickfont=dict(size=10),
                zeroline=False,
                showline=False
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='#334155',
                showticklabels=True,
                tickformat='$,.0f',
                tickfont=dict(size=10),
                zeroline=False,
                showline=False,
                range=[y_min, y_max]
            )
        )

        st.plotly_chart(fig2, use_container_width=True,
                        config={'displayModeBar': False})

    except Exception as e:
        st.error(f"Error fetching GDP data for {selected_country}: {str(e)}")