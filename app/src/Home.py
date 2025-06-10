##################################################
# This is the main/entry-point file for the
# sample application for your project
##################################################

# Set up basic logging infrastructure
from modules.nav import SideBarLinks
import streamlit as st
import logging
logging.basicConfig(
    format='%(filename)s:%(lineno)s:%(levelname)s -- %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# import the main streamlit library as well
# as SideBarLinks function from src/modules folder

# streamlit supports reguarl and wide layout (how the controls
# are organized/displayed on the screen).
st.set_page_config(layout='wide')

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
st.write('\n\n')
st.write("### By: Pushin' Policy")
st.write('\n')
st.write('#### HI! As which user would you like to log in?')

# For each of the user personas for which we are implementing
# functionality, we put a button on the screen that the user
# can click to MIMIC logging in as that mock user.

if st.button("Act as Sun Yue, a  Policy Maker",
             type='primary',
             use_container_width=True):
    # when user clicks the button, they are now considered authenticated
    st.session_state['authenticated'] = True
    # we set the role of the current user
    st.session_state['role'] = 'Policy Maker'
    st.session_state['nationality'] = 'United States'
    st.session_state['first_name'] = 'Sun'
    st.session_state['user_id'] = '3'
    # we add the first name of the user (so it can be displayed on
    # subsequent pages).
    # st.session_state['first_name'] = 'John'
    # finally, we ask streamlit to switch to another page, in this case, the
    # landing page for this particular user type
    logger.info("Logging in as Policy Maker Persona")
    st.switch_page('pages/00_Policy_Maker_Home.py')

if st.button('Act as Andrew Thornton, an Economist',
             type='primary',
             use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'economist'
    st.session_state["user_id"] = 1
    logger.info("Logging in as Political Strategy Advisor Persona")
    st.switch_page('pages/historicaldata.py')


if st.button('Act as Eleanore Goosens, a poltical lobbyist.', type='primary',  use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'Lobbyist'
    st.session_state['first_name'] = 'Eleanor'
    st.session_state['user_id'] = 2
    st.session_state['nationality'] = 'United States'
    st.switch_page('pages/40_Lobbyist.py')

if st.button('Act as System Admin', type='primary',  use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'administrator'
    st.session_state['first_name'] = 'Admin'
    st.session_state['user_id'] = 4
    st.switch_page('pages/20_Admin_Home.py')
