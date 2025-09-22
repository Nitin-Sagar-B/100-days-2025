import calendar
from datetime import date, datetime

import pandas as pd
import streamlit as st

from src.repo import init_db, to_dataframe, upsert_day

st.set_page_config(page_title="Calendar", page_icon="📅", layout="wide")
init_db()

st.title("Calendar")

# Simple month grid with day-click selection
today = date(2025, 9, 22)
year = st.selectbox("Year", [2025], index=0)
month = st.selectbox(
    "Month",
    list(range(1, 13)),
    index=8 if year == 2025 else 0,
    format_func=lambda m: calendar.month_name[m],
)

cal = calendar.Calendar(firstweekday=0)
days = [d for d in cal.itermonthdates(year, month)]

st.write(f"{calendar.month_name[month]} {year}")
cols = st.columns(7)
for i, wd in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
    cols[i].markdown(f"**{wd}**")

row_cols = None
for idx, d in enumerate(days):
    if idx % 7 == 0:
        row_cols = st.columns(7)
    style = ""
    if d.month != month:
        label = f"{d.day}"  # dim other-month days
    else:
        label = f"{d.day}"
    if row_cols:
        if d.month == month:
            if row_cols[idx % 7].button(label, key=f"daybtn-{d.isoformat()}"):
                st.session_state["selected_date"] = d
        else:
            row_cols[idx % 7].markdown(f"<span style='opacity:0.3'>{label}</span>", unsafe_allow_html=True)

sel = st.session_state.get("selected_date", today)
st.markdown(f"### Edit {sel}")

with st.form("day_form", clear_on_submit=False):
    d = st.date_input("Date", value=sel)
    sugar = st.number_input("Sugar (g)", min_value=0, max_value=1000, step=5)
    water = st.number_input("Water (ml)", min_value=0, max_value=5000, step=50)
    fap = st.number_input("Fap count", min_value=0, max_value=10, step=1)
    prod = st.number_input("Productive hours", min_value=0.0, max_value=24.0, step=0.5)
    weight = st.number_input("Weight (kg)", min_value=0.0, max_value=200.0, step=0.1, value=70.0)
    notes = st.text_area("Notes", placeholder="Quick note…")
    submitted = st.form_submit_button("Save day")
    if submitted:
        try:
            upsert_day(
                {
                    "date": d,
                    "sugar_intake_g": int(sugar),
                    "water_ml": int(water),
                    "fap_count": int(fap),
                    "productive_hours": float(prod),
                    "weight_kg": float(weight),
                    "notes": notes,
                }
            )
            st.success("Logged. Nice.")
        except Exception as e:
            st.error(str(e))

st.caption("Day-click calendar grid provided. If an advanced component is needed, FullCalendar embed can be added later with a fallback to this form.")

df = to_dataframe()
if not df.empty:
    st.dataframe(df.tail(10), use_container_width=True)
