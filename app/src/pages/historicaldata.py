import pandas as pd
import requests
from modules.nav import SideBarLinks
import streamlit as st
import logging
logger = logging.getLogger(__name__)


st.set_page_config(layout='wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()


st.title(f"Historical Data Viewer 🔎")
st.write("---")
st.write("\n \n")

col1, col2 = st.columns(2)

with col1:
    year_start = ["2000", "2001", "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009",
                  "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020"]
    start_choice = st.selectbox("Choose Start Year", year_start)
    # st.write("You selected:", choice)

    topic = ["Taxation", "Government Spending", "Public Deficit", "Interest Rates", "Inflation", "Money Supply",
             "Government Bonds", "Unemployment", "Tariffs", "Trade Agreements", "Minimum Wage", "Retirement", "Debt Management"]
    topic_choice = st.selectbox("Choose a Topic", topic)
    
    # Add new numeric input fields
    budget = st.number_input("Budget (in millions)", min_value=0, step=1)
    duration_length = st.number_input("Duration Length (in months)", min_value=0, step=1)
    population_size = st.number_input("Population Size", min_value=0, step=1000)

with col2:
    year_end = ["2000", "2001", "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009",
                "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020"]
    end_choice = st.selectbox("Choose End Year", year_end)

    country = ["USA", "EU", "China"]
    country_choice = st.selectbox("Choose a Country", country)

    sort_by = st.selectbox("Sort by:", ['policy_id', 'year_enacted', 'budget', 'duration_length', 'population_size'])

with col1:
    order = st.radio("Order:", ["ASC", "DESC"])

if st.button("Apply"):
    params = {
        "sort_by": sort_by,
        "order": order,
    }
    if year_start:
        params['Start Year'] = start_choice
    if year_end:
        params['End Year'] = end_choice
    if topic:
        params['Topic Choice'] = topic_choice
    if country:
        params['country_choice'] = country_choice
    if budget:
        params['budget'] = budget
    if duration_length:
        params['duration_length'] = duration_length
    if population_size:
        params['population_size'] = population_size

    response = requests.get("http://web-api:4000/pol/getpol", params=params)
    data = response.json()
    df = pd.DataFrame(data)
    
    # Format the numeric columns
    if 'budget' in df.columns:
        df['budget'] = df['budget'].apply(lambda x: f"${x:,.0f}M" if pd.notnull(x) else "")
    if 'population_size' in df.columns:
        df['population_size'] = df['population_size'].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "")
    if 'duration_length' in df.columns:
        df['duration_length'] = df['duration_length'].apply(lambda x: f"{x} months" if pd.notnull(x) else "")
    
    st.dataframe(df)

st.write("---")


enter_id = st.text_input("Enter a Policy ID to save:")

col1, col2 = st.columns(2)
with col1:
    if st.button("Save"):
        returnJson = {"policy_id": enter_id, "user_id": 1}
        requests.post("http://web-api:4000/pol/add_favorite", json=returnJson)
        st.write("Policy Saved!")

with col2:
    if st.button("Next Page"):
        st.switch_page("pages/view_favorites.py")
