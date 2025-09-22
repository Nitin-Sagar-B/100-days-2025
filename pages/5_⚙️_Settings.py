import streamlit as st

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

st.title("Settings")

units = st.radio("Weight units", ["kg", "lbs"], index=0)
water_units = st.radio("Water units", ["ml", "glasses"], index=0)
goal_hours = st.slider("Daily goal: productive hours", 0.0, 12.0, 4.0, 0.5)
goal_water = st.slider("Daily goal: water (ml)", 0, 4000, 2000, 100)

st.session_state["settings"] = {
    "weight_units": units,
    "water_units": water_units,
    "goal_hours": goal_hours,
    "goal_water": goal_water,
}

st.success("Preferences saved (session only).")
