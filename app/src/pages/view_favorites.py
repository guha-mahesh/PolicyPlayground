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

col1, col2 = st.columns(2, vertical_alignment="bottom")

with col1:
    #select box of policies
    policies_list = [f"{c}. {a}- {b}" for a, b, c in zip(df['politician'], df['topic'], df['policy_id'])]
    fav_choice = st.selectbox("Choose A Policy to Look at", policies_list)  

    with st.container(height=300):
        st.markdown("**Policy Information**")
        num = int(fav_choice.split('.')[0])
        st.write(f"Year Enacted:\t{df.loc[df['policy_id'] == num, 'year_enacted'].iloc[0]}")
        st.write(f"Scope:\t{df.loc[df['policy_id'] == num, 'pol_scope'].iloc[0]}")
        st.write(f"Duration:\t{df.loc[df['policy_id'] == num, 'duration'].iloc[0]}")
        st.write(f"Intensity:\t{df.loc[df['policy_id'] == num, 'intensity'].iloc[0]}")
        st.write(f"Course of Action:\t{df.loc[df['policy_id'] == num, 'advocacy_method'].iloc[0]}")

with col2:
    num = int(fav_choice.split('.')[0])
    if st.button("Delete Policy"):
        response = requests.delete(f"http://web-api:4000/pol/deletefav/{num}")


    with st.container(height=300):
        st.markdown("**Policy Description:**")
        desc = df.loc[df['policy_id'] == num, 'pol_description'].iloc[0]
        st.write(desc)

# Add Similar Policies section
st.header("Similar Policies")

try:
    similar_response = requests.get("http://web-api:4000/model/similar_policies")
    similar_data = similar_response.json()
    
    if similar_data and len(similar_data) > 0:
        similar_df = pd.DataFrame(similar_data)
        
        # Format the numeric columns
        if 'budget' in similar_df.columns:
            similar_df['budget'] = similar_df['budget'].apply(lambda x: f"${x:,.0f}M" if pd.notnull(x) else "")
        if 'population_size' in similar_df.columns:
            similar_df['population_size'] = similar_df['population_size'].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "")
        if 'duration_length' in similar_df.columns:
            similar_df['duration_length'] = similar_df['duration_length'].apply(lambda x: f"{x} months" if pd.notnull(x) else "")
        
        st.dataframe(similar_df)
    else:
        st.info("No similar policies found.")
except Exception as e:
    st.error(f"Error fetching similar policies: {str(e)}")
    st.info("Please try again later or contact support if the issue persists.")

st.write("---")




