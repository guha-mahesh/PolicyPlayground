# Idea borrowed from https://github.com/fsmosca/sample-streamlit-authenticator

# This file has function to add certain functionality to the left side bar of the app

import streamlit as st


# ------------------------ General ------------------------


def HomeNav():
    st.sidebar.page_link("Home.py", label="Home", icon="🏠")


def AboutPageNav():
    st.sidebar.page_link("pages/30_About.py", label="About", icon="🧠")


# ------------------------ Economist ------------------------
def economy_home():
    st.sidebar.page_link(
        "pages/economist_home.py", label="Home", icon="🏦"
    )

def PolStratAdvHomeNav():
    st.sidebar.page_link(
        "pages/historicaldata.py", label="Historical Data Viewer", icon="💰"
    )

def viewFavoritesNav():
    st.sidebar.page_link(
        "pages/view_favorites.py", label="View Favorites", icon="🧾"
    )

# ------------------------ Examples for Role of usaid_worker ------------------------


def ApiTestNav():
    st.sidebar.page_link("pages/12_API_Test.py",
                         label="Test the API", icon="🛜")


def PredictionNav():
    st.sidebar.page_link(
        "pages/11_Prediction.py", label="Regression Prediction", icon="📈"
    )


def ClassificationNav():
    st.sidebar.page_link(
        "pages/13_Classification.py", label="Classification Demo", icon="🌺"
    )


def NgoDirectoryNav():
    st.sidebar.page_link("pages/14_NGO_Directory.py",
                         label="NGO Directory", icon="📁")


def AddNgoNav():
    st.sidebar.page_link("pages/15_Add_NGO.py", label="Add New NGO", icon="➕")

# ------------------------ Lobbyist ----------------------------


def MakeNoteNav():
    st.sidebar.page_link("pages/40_Lobbyist.py",
                         label="Make a New Note", icon="✍️")


def ViewNotesNav():
    st.sidebar.page_link("pages/43_Lobbyist2.py", label="View Notes", icon="📝")


# ------------------------ System Admin Role ------------------------
def AdminPageNav():
    st.sidebar.page_link("pages/20_Admin_Home.py",
                         label="Note Taker", icon="🗒️")
    st.sidebar.page_link(
        "pages/21_ML_Model_Mgmt.py", label="Access Previous Notes", icon="⌨️"
    )


# --------------------------------Links Function -----------------------------------------------
def SideBarLinks(show_home=False):
    """
    This function handles adding links to the sidebar of the app based upon the logged-in user's role, which was put in the streamlit session_state object when logging in.
    """

    # add a logo to the sidebar always
    st.sidebar.image("assets/logo.png", width=150)

    # If there is no logged in user, redirect to the Home (Landing) page
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.switch_page("Home.py")

    if show_home:
        # Show the Home page link (the landing page)
        HomeNav()

    # Show the other page navigators depending on the users' role.
    if st.session_state["authenticated"]:

        # Show World Bank Link and Map Demo Link if the user is a political strategy advisor role.

        # If the user role is usaid worker, show the Api Testing page
        if st.session_state["role"] == "economist":
            economy_home()
            PolStratAdvHomeNav()
            viewFavoritesNav()

        # If the user is an administrator, give them access to the administrator pages
        if st.session_state["role"] == "administrator":
            AdminPageNav()

        if st.session_state["role"] == "Lobbyist":
            MakeNoteNav()
            ViewNotesNav()

    # Always show the About page at the bottom of the list of links
    AboutPageNav()

    if st.session_state["authenticated"]:
        # Always show a logout button if there is a logged in user
        if st.sidebar.button("Logout"):
            del st.session_state["role"]
            del st.session_state["authenticated"]
            st.switch_page("Home.py")
