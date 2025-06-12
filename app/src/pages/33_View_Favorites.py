import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests
import pandas as pd
from modules.theme import custom_style


st.set_page_config(layout = 'wide')
custom_style()
# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.markdown("""
    <div style='background: linear-gradient(90deg, #1e3a8a 0%, #1e40af 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem;'>
        <h1 style='color: white; margin: 0;'>Historical Data Viewer 🔎</h1>
        <p style='color: #94a3b8; margin: 0.5rem 0 0 0;'>Analyze past policies and their impacts</p>
    </div>
""", unsafe_allow_html=True)

st.write("\n \n")
st.write("## Choose a Favorited Policy to View:")

response = requests.get(f"http://web-api:4000/pol/favorites/{st.session_state['user_id']}")
data = response.json()
df = pd.DataFrame(data)

col1, col2 = st.columns(2, vertical_alignment="bottom")
try:
    with col1:
        policies_list = [f"{c}. {a}- {b}" for a, b, c in zip(df['politician'], df['topic'], df['policy_id'])]
        fav_choice = st.selectbox("Choose A Policy to Look at:", policies_list)  
        with st.container(height=300):
            st.markdown("**Policy Information**")
            num = int(fav_choice.split('.')[0])
            st.write(f"Year Enacted:\t{df.loc[df['policy_id'] == num, 'year_enacted'].iloc[0]}")
            st.write(f"Politician:\t{df.loc[df['policy_id'] == num, 'politician'].iloc[0]}")
            st.write(f"Country:\t{df.loc[df['policy_id'] == num, 'country'].iloc[0]}")
            st.write(f"Budget:\t{df.loc[df['policy_id'] == num, 'budget'].iloc[0]} M")
            st.write(f"Population:\t{df.loc[df['policy_id'] == num, 'population_size'].iloc[0]} K")
            st.write(f"Duration:\t{df.loc[df['policy_id'] == num, 'duration_length'].iloc[0]} M")

    with col2:
        num = int(fav_choice.split('.')[0])
        st.session_state['Politician Index'] = num
        if st.button("Delete Policy"):
            response = requests.delete(f"http://web-api:4000/pol/favorites/{num}")
        with st.container(height=300):
            st.markdown("**Policy Description:**")
            desc = df.loc[df['policy_id'] == num, 'pol_description'].iloc[0]
            st.write(desc)
            st.write("\n")
            if st.button("Polician Contact Info"):
                st.switch_page("pages/34_Politician_Information_Page.py")
except Exception as e:
    st.write("No Favorites Selected, please go back.")


st.markdown("""
    <div style='background: #1e293b; padding: 1.5rem; border-radius: 8px; margin: 2rem 0;'>
        <h3 style='color: #e2e8f0; margin: 0 0 1rem 0;'> Similar Policies</h3>
        <p style='color: #94a3b8; margin: 0;'>Policies with similar characteristics and objectives</p>
    </div>
""", unsafe_allow_html=True)

try:
    num = int(fav_choice.split('.')[0])
    similar_response = requests.get(f"http://web-api:4000/model/similar_policies/{num}")
    similar_data = similar_response.json()
    
    if similar_data and len(similar_data) > 0:
        similar_df = pd.DataFrame(similar_data)
        

        if 'budget' in similar_df.columns:
            similar_df['budget'] = similar_df['budget'].apply(lambda x: f"${x:,.0f}M" if pd.notnull(x) else "")
        if 'population_size' in similar_df.columns:
            similar_df['population_size'] = similar_df['population_size'].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "")
        if 'duration_length' in similar_df.columns:
            similar_df['duration_length'] = similar_df['duration_length'].apply(lambda x: f"{x} months" if pd.notnull(x) else "")

        # Display each similar policy in an expandable container
        for _, policy in similar_df.iterrows():
            with st.expander(f"📋 {policy['politician']} - {policy['topic']} ({policy['year_enacted']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Policy Details")
                    st.write(f"Country: {policy['country']}")
                    st.write(f"Budget: {policy['budget']}")
                    st.write(f"Duration: {policy['duration_length']}")
                    st.write(f"Population: {policy['population_size']}")
                    st.write(f"Advocacy Method: {policy['advocacy_method']}")
                
                with col2:
                    st.subheader("Description")
                    st.write(policy['pol_description'])
                
                # Add save button for each policy
                if st.button(f"Save Policy", key=f"save_{policy['policy_id']}", use_container_width=True):
                    returnJson = {"policy_id": policy['policy_id'], "user_id": st.session_state['user_id']}
                    response = requests.post(f"http://web-api:4000/pol/favorites", json=returnJson)
                    
                
                st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("No similar policies found.")
except Exception as e:
    st.error(f"Error fetching similar policies: {str(e)}")
    st.info("Please try again later or contact support if the issue persists.")

st.markdown("<br>", unsafe_allow_html=True)

st.write("---")
if st.button("Previous"):
    st.switch_page("pages/32_Historical_Data.py")
