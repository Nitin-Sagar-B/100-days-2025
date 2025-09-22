import streamlit as st
from src.utils import ensure_dirs, load_fontawesome

st.set_page_config(
    page_title="Sparky's 100 Days Dashboard",
    page_icon="🗓️",
    layout="wide",
    initial_sidebar_state="expanded",
)

ensure_dirs()
load_fontawesome()

st.markdown(
    "<h1 style='margin-top:0'>Sparky's last 100 Days Habit + Productivity for 2025</h1>", unsafe_allow_html=True
)
st.info("👈 I’ll use the sidebar to switch between: Dashboard, Calendar, Analytics, Data & Export.")

st.success("This is my space to track the last 100 days of 2025. I’m logging sugar intake, weight, water, fap count, and productivity hours. If I stay consistent, I’ll see exactly how my choices stack up over time.")

st.warning("⚠️ Missing a day isn’t the end of the world, but ghosting the tracker for too long kills the whole point. Consistency beats perfection.")

st.error("❌ My Red Zone:\n- Too much sugar\n- Low productivity\n- Barely any water\n\nThese are the danger signs I need to keep in check every day.")


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
