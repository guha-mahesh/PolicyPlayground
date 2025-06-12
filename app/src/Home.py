##################################################
# This is the main/entry-point file for the
# sample application for your project
##################################################

# Set up basic logging infrastructure
from modules.nav import SideBarLinks
import streamlit as st
import logging
from modules.theme import custom_style

logging.basicConfig(
    format='%(filename)s:%(lineno)s:%(levelname)s -- %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# import the main streamlit library as well
# as SideBarLinks function from src/modules folder

# streamlit supports reguarl and wide layout (how the controls
# are organized/displayed on the screen).
st.set_page_config(layout='wide')

custom_style()

# If a user is at this page, we assume they are not
# authenticated.  So we change the 'authenticated' value
# in the streamlit session_state to false.
st.session_state['authenticated'] = False

# Use the SideBarLinks function from src/modules/nav.py to control
# the links displayed on the left-side panel.
# IMPORTANT: ensure src/.streamlit/config.toml sets
# showSidebarNavigation = false in the [client] section
SideBarLinks(show_home=True)

# ***************************************************
#    The major content of this page
# ***************************************************

# set the title of the page and provide a simple prompt.
logger.info("Loading the Home page of the app")
st.title('Policy Playground')
st.write('\n')
st.write("### By: Pushin' Policy")
st.write('\n')
st.write('#### Choose a User to Login as:')

# For each of the user personas for which we are implementing
# functionality, we put a button on the screen that the user
# can click to MIMIC logging in as that mock user.
st.write('\n\n')
makers_dict = {"Sun Yue 🇺🇸": [2, "United States"], "Dillon Brooks 🇬🇧": [
    3, "United Kingdom"], "Gerrard James 🇩🇪": [4, "Germany"]}
makers = ["Sun Yue 🇺🇸", "Dillon Brooks 🇬🇧", "Gerrard James 🇩🇪"]
maker = st.selectbox("Choose a User:", makers)
if st.button('Policy Maker Login',
             type='primary',
             use_container_width=True):
    # when user clicks the button, they are now considered authenticated
    st.session_state['authenticated'] = True

    st.session_state['role'] = 'Policy Maker'
    st.session_state['nationality'] = makers_dict[maker][1]
    st.session_state['first_name'] = maker
    st.session_state['user_id'] = makers_dict[maker][0]

    logger.info("Logging in as Policy Maker Persona")
    st.switch_page('pages/00_Policy_Maker_Home.py')

st.write('\n\n')

econ_dict = {"Andrew Thornton": 5, "Ryan Gurtings": 6, "Bob": 7}
econs = ["Andrew Thornton", "Ryan Gurtings", "Bob"]
econ = st.selectbox("Choose a User:", econs)
if st.button('Economist Login',
             type='primary',
             use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'economist'
    st.session_state["user_id"] = econ_dict[econ]
    st.session_state['first_name'] = econ
    logger.info("Logging in as Economist")
    st.switch_page('pages/31_Economist_Home.py')

st.write('\n\n')

lobby_dict = {"Eleanore Goosens": 8, "User 2": 9, "User 3": 10}
lobbys = ["Eleanore Goosens", "User 2", "User 3"]
lobby = st.selectbox("Choose a User:", lobbys)
if st.button('Lobbyist Login', type='primary',  use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'Lobbyist'
    st.session_state['first_name'] = lobby
    st.session_state['user_id'] = lobby_dict[lobby]
    st.session_state['nationality'] = 'United States'
    st.switch_page('pages/40_Lobbyist.py')

st.write("\n\n\n\n\n")
st.write('\n')
st.write('\n')
