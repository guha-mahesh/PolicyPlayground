from modules.theme import *
from modules.theme import custom_style
import pandas as pd
import requests
from modules.nav import SideBarLinks
import streamlit as st
import logging
logger = logging.getLogger(__name__)

custom_style()

SideBarLinks()
banner("Historical Data Viewer", "Analyze past policies and their impacts")

st.markdown(f"#### Logged in as: **{st.session_state['first_name']}**")
st.write("\n \n")


if 'filter_params' not in st.session_state:
    st.session_state.filter_params = {}

st.markdown("### Enter the criteria to find your policies:\n")

col1, col2 = st.columns(2)
with col1:
    with st.container(height=430):
        st.write("*General Information*")
        year_start = ["2000", "2001", "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009",
                      "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020"]
        start_choice = st.selectbox("Choose Start Year", year_start)

        year_end = ["2000", "2001", "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009",
                    "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020"]
        end_choice = st.selectbox("Choose End Year", year_end)

        topic = ["Taxation", "Government Spending", "Public Deficit", "Interest Rates", "Inflation", "Money Supply",
                 "Government Bonds", "Unemployment", "Tariffs", "Trade Agreements", "Minimum Wage", "Retirement", "Debt Management"]
        topic_choice = st.selectbox("Choose a Topic", topic)

        country = ["USA", "EU", "China"]
        country_choice = st.radio("Choose a Country", country)

with col2:
    with st.container(height=430):
        st.write("*Economic Information*\n\n")

        budget_range = st.slider(
            "Budget Range (in millions)",
            min_value=0,
            max_value=1000,
            value=(0, 1000),
            step=50
        )
        st.write("\n")
        duration_range = st.slider(
            "Duration Length Range (in months)",
            min_value=0,
            max_value=120,
            value=(0, 120),
            step=1
        )
        st.write("\n")
        population_range = st.slider(
            "Population Size Range (in thousands)",
            min_value=0,
            max_value=1000,
            value=(0, 1000),
            step=50
        )

with st.container(height=200):
    st.write("*Filter Criteria*")
    col1, col2 = st.columns(2)
    with col1:
        order = st.radio("Order:", ["ASC", "DESC"])
    with col2:
        sort_by = st.radio("Sort by:", ['policy_id', 'year_enacted'])

if st.button("Apply", use_container_width=True):

    st.session_state.filter_params = {
        "sort_by": sort_by,
        "order": order,
        'Start Year': start_choice,
        'End Year': end_choice,
        'Topic Choice': topic_choice,
        'country_choice': country_choice,
        'budget_min': budget_range[0],
        'budget_max': budget_range[1],
        'duration_min': duration_range[0],
        'duration_max': duration_range[1],
        'population_min': population_range[0],
        'population_max': population_range[1]
    }


params = st.session_state.get('filter_params', {})


response = requests.get(
    "http://web-api:4000/pol/policy_handler", params=params)
data = response.json()
df = pd.DataFrame(data, columns=("policy_id", "country", "year_enacted",
                  "politician", "topic", "budget", "duration_length", "population_size"))


raw_df = df.copy()

df = df.rename(columns={"policy_id": "Policy ID", "country": "Country", "year_enacted": "Year", "politician": "Politician",
               "topic": "Topic", "budget": "Budget", "duration_length": "Duration (Years)", "population_size": "Population"})

st.write("### Here is a list of all available policies:")


display_df = df.copy()
if 'Budget' in display_df.columns:
    display_df['Budget'] = display_df['Budget'].apply(
        lambda x: f"${x:,.0f}M" if pd.notnull(x) else "")
if 'Population' in display_df.columns:
    display_df['Population'] = display_df['Population'].apply(
        lambda x: f"{x:,.0f}" if pd.notnull(x) else "")
if 'Duration (Years)' in display_df.columns:
    display_df['Duration (Years)'] = display_df['Duration (Years)'].apply(
        lambda x: f"{x} months" if pd.notnull(x) else "")

st.write(display_df)

try:
    choices = [f"{c}. {a}- {b}" for a, b,
               c in zip(df['Politician'], df['Topic'], df['Policy ID'])]
    choice = st.selectbox("Choose a Policy to save", choices)
    num = int(choice.split('.')[0])

    if st.button("Save Policy"):
        returnJson = {"policy_id": num, "user_id": st.session_state['user_id']}
        requests.post(f"http://web-api:4000/pol/favorites", json=returnJson)
        st.success("Policy Saved!")

    st.write("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear Filters", use_container_width=True):
            st.session_state.filter_params = {}
            st.rerun()
    with col2:
        if st.button("Next Page", use_container_width=True):
            st.switch_page("pages/33_View_Favorites.py")
except Exception as e:
    st.write("No Results Found")
