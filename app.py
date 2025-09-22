import streamlit as st
from src.utils import ensure_dirs, load_fontawesome

st.set_page_config(
    page_title="100 Days Dashboard",
    page_icon="🗓️",
    layout="wide",
    initial_sidebar_state="expanded",
)

ensure_dirs()
load_fontawesome()

st.markdown(
    "<h1 style='margin-top:0'>100 Days Habit + Productivity</h1>", unsafe_allow_html=True
)

st.info("Use the sidebar to navigate pages: Dashboard, Calendar, Analytics, Data & Export.")

# Force Streamlit built-in theme variables so viewer settings cannot override our palette
st.markdown(
        """
        <style>
        :root {
            --primary-color: #FFBE98;
            --background-color: #0B0F14;
            --secondary-background-color: #12161D;
            --text-color: #E6E7EB;
            --font: sans-serif;
        }
        html, body, .stApp { background-color: var(--background-color) !important; color: var(--text-color) !important; }
        .stButton>button, .stDownloadButton>button { background: var(--primary-color) !important; color: #0A0C0F !important; border: 0; }
        .stTabs [data-baseweb=\"tab\"] { color: var(--text-color) !important; }
        .stSidebar, section[data-testid=\"stSidebar\"] { background-color: var(--secondary-background-color) !important; }
        </style>
        """,
        unsafe_allow_html=True,
)
