import streamlit as st
from src.utils import ensure_dirs, load_fontawesome, apply_theme_css

st.set_page_config(
    page_title="Sparky's 100 Days Dashboard",
    page_icon="🗓️",
    layout="wide",
    initial_sidebar_state="expanded",
)

ensure_dirs()
load_fontawesome()
apply_theme_css()

st.markdown(
    "<h1 style='margin-top:0'>Sparky's last 100 Days Habit + Productivity for 2025</h1>", unsafe_allow_html=True
)
st.info("👈 I’ll use the sidebar to switch between: Dashboard, Calendar, Analytics, Data & Export.")

st.success("This is my space to track the last 100 days of 2025. I’m logging sugar intake, weight, water, fap count, and productivity hours. If I stay consistent, I’ll see exactly how my choices stack up over time.")

st.warning("⚠️ Missing a day isn’t the end of the world, but ghosting the tracker for too long kills the whole point. Consistency beats perfection.")

st.error("❌ My Red Zone:\n- Too much sugar\n- Low productivity\n- Barely any water\n\nThese are the danger signs I need to keep in check every day.")


# Theme CSS injected above for consistent look everywhere
