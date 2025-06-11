import json
import requests
import streamlit as st

user_id = st.session_state['user_id']
url = f"http://host.docker.internal:4000/politician/allpolicy/{user_id}"


saved_policies = requests.get(url)


saved_policies_data = json.loads(saved_policies.text)


for item in saved_policies_data:
    id = int(item["saved_id"])
    policy_url = f"http://host.docker.internal:4000/politician/policy/{id}"
    response = requests.get(policy_url).text
    st.write(response)
