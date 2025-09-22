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

# Subtle CSS nudge to align Streamlit base with our theme tokens (no heavy overrides)
st.markdown(
        """
        <style>
        :root {
            --accent: #FFBE98;
            --bg: #0B0F14;
            --bg2: #12161D;
            --text: #E6E7EB;
        }
        .stApp { background-color: var(--bg) !important; }
        .stMarkdown, .stText, .stNumberInput, .stSelectbox, .stDateInput, label, .css-10trblm, .css-1d391kg {
            color: var(--text) !important;
        }
        .stButton>button, .stDownloadButton>button { background: var(--accent) !important; color: #0A0C0F !important; border: 0; }
        .stTabs [data-baseweb="tab"] { color: var(--text); }
        </style>
        """,
        unsafe_allow_html=True,
)
