from modules.nav import SideBarLinks
from modules.theme import custom_style
import streamlit as st
import logging

logging.basicConfig(
    format='%(filename)s:%(lineno)s:%(levelname)s -- %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

custom_style()

st.session_state['authenticated'] = False

SideBarLinks(show_home=True)

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
    
    .persona-title {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
        text-align: center !important;
    }
    
    .admin-section {
        background: linear-gradient(135deg, rgba(100, 100, 100, 0.1) 0%, rgba(80, 80, 80, 0.15) 100%);
        border: 2px dashed rgba(100, 100, 100, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .persona-container {
        padding: 1rem 0;
    }
    
    .persona-image-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 1rem 0;
    }
    
    .persona-dropdown {
        margin: 1rem 0;
    }
    </style>
    
    <div class='welcome-banner'>
        <h1 class='welcome-title'>Policy Playground</h1>
        <h3 class='welcome-subtitle'>By: Pushin' Policy</h3>
    </div>
""", unsafe_allow_html=True)

st.write('#### Choose a User to Login as:')

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown(
            '<p class="persona-title">Login as Policy Maker</p>', unsafe_allow_html=True)

        col_left, col_center, col_right = st.columns([1, 2, 1])
        with col_center:
            st.image("https://i.ibb.co/QjkRqcMd/guy1.png", width=175)

        makers_dict = {"Sun Yue 🇺🇸": [2, "United States"], "Dillon Brooks 🇬🇧": [
            3, "United Kingdom"], "Gerrard James 🇩🇪": [4, "Germany"]}
        makers = ["Sun Yue 🇺🇸", "Dillon Brooks 🇬🇧", "Gerrard James 🇩🇪"]

        maker = st.selectbox("Select Policy Maker", makers,
                             label_visibility="collapsed", key="policy_maker_select")

        if st.button('Login', type='primary', use_container_width=True, key="login1"):
            st.session_state['authenticated'] = True
            st.session_state['role'] = 'Policy Maker'
            st.session_state['nationality'] = makers_dict[maker][1]
            st.session_state['first_name'] = maker
            st.session_state['user_id'] = makers_dict[maker][0]
            logger.info("Logging in as Policy Maker Persona")
            st.switch_page('pages/00_Policy_Maker_Home.py')

with col2:
    with st.container(border=True):
        st.markdown('<p class="persona-title">Login as Economist</p>',
                    unsafe_allow_html=True)

        col_left, col_center, col_right = st.columns([1, 2, 1])
        with col_center:
            st.image("https://i.ibb.co/QFSJzLRS/guy2.png", width=175)

        econ_dict = {"Andrew Thornton": 5, "Ryan Gurtings": 6, "Bob Bobias": 7}
        econs = ["Andrew Thornton", "Ryan Gurtings", "Bob Bobias"]

        econ = st.selectbox("Select Economist", econs,
                            label_visibility="collapsed", key="economist_select")

        if st.button('Login', type='primary', use_container_width=True, key="login2"):
            st.session_state['authenticated'] = True
            st.session_state['role'] = 'economist'
            st.session_state["user_id"] = econ_dict[econ]
            st.session_state['first_name'] = econ
            logger.info("Logging in as Economist")
            st.switch_page('pages/31_Economist_Home.py')

with col3:
    with st.container(border=True):
        st.markdown('<p class="persona-title">Login as Lobbyist</p>',
                    unsafe_allow_html=True)

        col_left, col_center, col_right = st.columns([1, 2, 1])
        with col_center:
            st.image("https://i.ibb.co/QFvdtNM9/guy3.png", width=175)

        lobby_dict = {"Eleanore Goosens": 8,
                      "Hardy Nextur": 9, "Elmer Elms": 10}
        lobbys = ["Eleanore Goosens", "Hardy Nextur", "Elmer Elms"]

        lobby = st.selectbox("Select Lobbyist", lobbys,
                             label_visibility="collapsed", key="lobbyist_select")

        if st.button('Login', type='primary', use_container_width=True, key="login3"):
            st.session_state['authenticated'] = True
            st.session_state['role'] = 'Lobbyist'
            st.session_state['first_name'] = lobby
            st.session_state['user_id'] = lobby_dict[lobby]
            st.session_state['nationality'] = 'United States'
            st.switch_page('pages/40_Lobbyist.py')

st.divider()

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button('System Admin Login', type='secondary', use_container_width=True):
        st.session_state['authenticated'] = True
        st.session_state['role'] = 'administrator'
        st.session_state['first_name'] = 'Admin'
        st.session_state['user_id'] = 4
        st.switch_page('pages/20_Admin_Home.py')
