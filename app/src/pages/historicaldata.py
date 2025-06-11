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
choices = []

col1, col2 = st.columns(2)

with col1:
    year_start = ["2000", "2001", "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009",
                  "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020"]
    start_choice = st.selectbox("Choose Start Year", year_start)

    topic = ["Taxation", "Government Spending", "Public Deficit", "Interest Rates", "Inflation", "Money Supply",
             "Government Bonds", "Unemployment", "Tariffs", "Trade Agreements", "Minimum Wage", "Retirement", "Debt Management"]
    topic_choice = st.selectbox("Choose a Topic", topic)
    
    # Replace single number inputs with range sliders
    budget_range = st.slider(
        "Budget Range (in millions)",
        min_value=0,
        max_value=1000,
        value=(0, 1000),
        step=50
    )
    
    duration_range = st.slider(
        "Duration Length Range (in months)",
        min_value=0,
        max_value=120,
        value=(0, 120),
        step=1
    )
    
    population_range = st.slider(
        "Population Size Range (in millions)",
        min_value=0,
        max_value=1000,
        value=(0, 1000),
        step=50
    )

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
    
    # Add min/max parameters for each range
    params['budget_min'] = budget_range[0]
    params['budget_max'] = budget_range[1]
    params['duration_min'] = duration_range[0]
    params['duration_max'] = duration_range[1]
    params['population_min'] = population_range[0]
    params['population_max'] = population_range[1]

    response = requests.get("http://web-api:4000/pol/policy_handler", params=params)
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
    for i in range(len(df)):
        st.write(f"Policy ID: {df.loc[i, 'policy_id']} - Topic: {df.loc[i, 'topic']} - Policitian: {df.loc[i, 'politician']}")

    choices = [f"{c}. {a}- {b}" for a, b, c in zip(df['politician'], df['topic'], df['policy_id'])]
    st.write(choices)


    choice = st.selectbox("Choose a Policy to save", choices)
    st.write(choice)
    num = 0
    #num = int(choice.split('.')[0])
    st.write(num)
    if st.button("Save Policy"):
        returnJson = {"policy_id": num, "user_id": 1}
        requests.post("http://web-api:4000/pol/favorites", json=returnJson)
        st.write("Policy Saved!")    

st.write("---")


enter_id = st.text_input("Enter a Policy ID to save:")

col1, col2 = st.columns(2)
with col1:
    if st.button("Save"):
        returnJson = {"policy_id": enter_id, "user_id": 1}
        requests.post("http://web-api:4000/pol/favorites", json=returnJson)
        st.write("Policy Saved!")

with col2:
    if st.button("Next Page"):
        st.switch_page("pages/view_favorites.py")
