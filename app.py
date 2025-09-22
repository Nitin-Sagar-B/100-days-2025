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

st.info("Use the sidebar to navigate pages: Dashboard, Calendar, Analytics, Data & Export, Settings.")

st.markdown(
    "<div class='fa fa-clock' style='margin-right:6px'></div> Minimal dark theme active.",
    unsafe_allow_html=True,
)
