##################################################
# This is the main/entry-point file for the
# sample application for your project
##################################################

# Set up basic logging infrastructure
from modules.nav import SideBarLinks
from modules.theme import custom_style
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
st.markdown("""
    <style>
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .welcome-banner {
        background: linear-gradient(90deg, rgba(240, 167, 108, 0.8) 0%, rgba(240, 146, 64, 0.8) 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 15px 35px rgba(240, 167, 108, 0.3);
        animation: fadeInUp 0.8s ease-out forwards;
        position: relative;
        overflow: hidden;
    }
    
    .welcome-banner::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
    }
    
    .welcome-banner::after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
    }
    
    .welcome-title {
        color: #FFFFFF !important;
        margin: 0 !important;
        font-size: 3rem !important;
        font-weight: 700 !important;
        line-height: 1 !important;
        animation: fadeInUp 0.8s ease-out 0.2s both !important;
    }
    
    .welcome-subtitle {
        color: rgba(255, 255, 255, 0.9) !important;
        margin: 0.2rem 0 !important;
        font-size: 1.3rem !important;
        font-weight: 400 !important;
        line-height: 1.2 !important;
        animation: fadeInUp 0.8s ease-out 0.4s both !important;
    }
    
    .welcome-user {
        color: rgba(255, 255, 255, 0.85) !important;
        margin: 0.3rem 0 0 0 !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        line-height: 1.2 !important;
        animation: fadeInUp 0.8s ease-out 0.6s both !important;
    }
    </style>
    
    <div class='welcome-banner'>
        <h1 class='welcome-title'>Policy Playground</h1>
        <h3 class='welcome-subtitle'>By: Pushin' Policy</h3>
    </div>
""", unsafe_allow_html=True)

st.write('#### Choose a User to Login as:')

# For each of the user personas for which we are implementing
# functionality, we put a button on the screen that the user
# can click to MIMIC logging in as that mock user.
st.write('\n\n')

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.write('#### Login as Policy Maker')
        makers_dict = {"Sun Yue 🇺🇸": [2, "United States"], "Dillon Brooks 🇬🇧": [
            3, "United Kingdom"], "Gerrard James 🇩🇪": [4, "Germany"]}
        makers = ["Sun Yue 🇺🇸", "Dillon Brooks 🇬🇧", "Gerrard James 🇩🇪"]
        maker = st.selectbox("", makers)
        if st.button('Login',
                    type='primary',
                    use_container_width=True, key="login1"):
            # when user clicks the button, they are now considered authenticated
            st.session_state['authenticated'] = True

            st.session_state['role'] = 'Policy Maker'
            st.session_state['nationality'] = makers_dict[maker][1]
            st.session_state['first_name'] = maker
            st.session_state['user_id'] = makers_dict[maker][0]

            logger.info("Logging in as Policy Maker Persona")
            st.switch_page('pages/00_Policy_Maker_Home.py')

with col2:
    with st.container(border=True):
        st.write('#### Login as Economist')
        econ_dict = {"Andrew Thornton": 5, "Ryan Gurtings": 6, "Bob": 7}
        econs = ["Andrew Thornton", "Ryan Gurtings", "Bob"]
        econ = st.selectbox("", econs)
        if st.button('Login',
                    type='primary',
                    use_container_width=True, key="login2"):
            st.session_state['authenticated'] = True
            st.session_state['role'] = 'economist'
            st.session_state["user_id"] = econ_dict[econ]
            st.session_state['first_name'] = econ
            logger.info("Logging in as Economist")
            st.switch_page('pages/31_Economist_Home.py')

with col3:
    with st.container(border=True):
        st.write('#### Login as Lobbyist')
        lobby_dict = {"Eleanore Goosens": 8, "User 2": 9, "User 3": 10}
        lobbys = ["Eleanore Goosens", "User 2", "User 3"]
        lobby = st.selectbox("", lobbys)
        if st.button('Login', type='primary',  use_container_width=True, key="login3"):
            st.session_state['authenticated'] = True
            st.session_state['role'] = 'Lobbyist'
            st.session_state['first_name'] = lobby
            st.session_state['user_id'] = lobby_dict[lobby]
            st.session_state['nationality'] = 'United States'
            st.switch_page('pages/40_Lobbyist.py')
