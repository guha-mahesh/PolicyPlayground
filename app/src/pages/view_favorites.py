import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests
import pandas as pd

st.set_page_config(layout = 'wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()


st.title(f"View Favorite Policies 🔎")
st.write("---")
st.write("\n \n")

response = requests.get("http://web-api:4000/pol/getfav/"+ str(st.session_state["user_id"]))
data = response.json()
df = pd.DataFrame(data)

# select box of policies
policies_list = [f"{c}. {a}- {b}" for a, b, c in zip(df['politician'], df['topic'], df['policy_id'])]
fav_choice = st.selectbox("Choose A Policy to Look at", policies_list)

col1, col2 = st.columns(2)

with col2: 
    with st.container(height=300):
        num = int(fav_choice.split('.')[0])
        st.markdown("**Policy Description:**")
        desc = df.loc[df['policy_id'] == num, 'pol_description'].iloc[0]
        st.write(desc)

with col1:
    with st.container(height=300):
        st.markdown("**Policy Information**")
        num = int(fav_choice.split('.')[0])
        st.write(f"Year Enacted:\t{df.loc[df['policy_id'] == num, 'year_enacted'].iloc[0]}")
        st.write(f"Scope:\t{df.loc[df['policy_id'] == num, 'pol_scope'].iloc[0]}")
        st.write(f"Duration:\t{df.loc[df['policy_id'] == num, 'duration'].iloc[0]}")
        st.write(f"Intensity:\t{df.loc[df['policy_id'] == num, 'intensity'].iloc[0]}")
        st.write(f"Course of Action:\t{df.loc[df['policy_id'] == num, 'advocacy_method'].iloc[0]}")




