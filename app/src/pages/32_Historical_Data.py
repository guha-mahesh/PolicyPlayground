import pandas as pd
import requests
from modules.nav import SideBarLinks
import streamlit as st
import logging
logger = logging.getLogger(__name__)


st.set_page_config(layout='wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()


st.markdown("""
    <div style='background: linear-gradient(90deg, #1e3a8a 0%, #1e40af 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem;'>
        <h1 style='color: white; margin: 0;'>Historical Data Viewer 🔎</h1>
        <p style='color: #94a3b8; margin: 0.5rem 0 0 0;'>Analyze past policies and their impacts</p>
    </div>
""", unsafe_allow_html=True)

st.markdown(f"#### Logged in as: **{st.session_state['first_name']}**")
st.write("\n \n")
choices = []
params = []
df = []

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
    with st.container(height = 430):
        st.write("*Economic Information*\n\n")
        # Replace single number inputs with range sliders
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
            "Population Size Range (in millions)",
            min_value=0,
            max_value=1000,
            value=(0, 1000),
            step=50
        )

with st.container(height = 200):
    st.write("*Filter Criteria*")
    col1, col2 = st.columns(2)
    with col1:
        order = st.radio("Order:", ["ASC", "DESC"])
    with col2:
        sort_by = st.radio("Sort by:", ['policy_id', 'year_enacted'])
if st.button("Apply", use_container_width=True):
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
df = pd.DataFrame(data, columns=("policy_id", "country", "year_enacted", "politician", "topic", "budget", "duration_length", "population_size"))
df = df.rename(columns={"policy_id": "Policy ID", "country" : "Country", "year_enacted": "Year", "politician" : "Politician", "topic": "Topic", "budget": "Budget", "duration_length": "Duration (Years)", "population_size": "Population"})
st.write("### Here is a list of all availiable policy:")
st.write(df)

# Format the numeric columns
if 'budget' in df.columns:
    df['budget'] = df['budget'].apply(lambda x: f"${x:,.0f}M" if pd.notnull(x) else "")
if 'population_size' in df.columns:
    df['population_size'] = df['population_size'].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "")
if 'duration_length' in df.columns:
    df['duration_length'] = df['duration_length'].apply(lambda x: f"{x} months" if pd.notnull(x) else "")

choices = [f"{c}. {a}- {b}" for a, b, c in zip(df['Politician'], df['Topic'], df['Policy ID'])]
choice = st.selectbox("Choose a Policy to save", choices)
num = int(choice.split('.')[0])

if st.button("Save Policy"):
    returnJson = {"policy_id": num, "user_id": st.session_state['user_id']}
    requests.post(f"http://web-api:4000/pol/favorites", json=returnJson)
    st.write("Policy Saved!")    

st.write("---")

if st.button("Next Page"):
    st.switch_page("pages/33_View_Favorites.py")
