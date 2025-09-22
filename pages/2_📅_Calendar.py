import calendar
from datetime import date, datetime

import pandas as pd
import streamlit as st
from src.utils import apply_theme_css

from src.repo import init_db, to_dataframe, upsert_day, get_day, delete_day

st.set_page_config(page_title="Calendar", page_icon="📅", layout="wide")
init_db()
apply_theme_css()

st.title("Calendar")

# Simple month grid with day-click selection
today = date.today()
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

# Prefill existing values if the day exists
existing = get_day(sel)
prefill = {
    "sugar_intake_g": existing.sugar_intake_g if existing else 0,
    "water_ml": existing.water_ml if existing else 0,
    "fap_count": existing.fap_count if existing else 0,
    "productive_hours": existing.productive_hours if existing else 0.0,
    "weight_kg": existing.weight_kg if (existing and existing.weight_kg is not None) else 70.0,
    "notes": existing.notes if (existing and existing.notes) else "",
}

with st.form("day_form", clear_on_submit=False):
    d = st.date_input("Date", value=sel)
    sugar = st.number_input("Sugar (g)", min_value=0, max_value=1000, step=5, value=int(prefill["sugar_intake_g"]))
    water = st.number_input("Water (ml)", min_value=0, max_value=5000, step=50, value=int(prefill["water_ml"]))
    fap = st.number_input("Fap count", min_value=0, max_value=10, step=1, value=int(prefill["fap_count"]))
    prod = st.number_input("Productive hours", min_value=0.0, max_value=24.0, step=0.5, value=float(prefill["productive_hours"]))
    weight = st.number_input("Weight (kg)", min_value=0.0, max_value=200.0, step=0.1, value=float(prefill["weight_kg"]))
    notes = st.text_area("Notes", value=prefill["notes"], placeholder="Quick note…")
    c1, c2 = st.columns([3,1])
    with c1:
        submitted = st.form_submit_button("Save / Update day")
    with c2:
        del_clicked = st.form_submit_button("Delete", type="secondary")
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
            st.success("Saved / Updated ✨")
        except Exception as e:
            st.error(str(e))
    if del_clicked:
        ok = delete_day(d)
        if ok:
            st.success("Deleted that day.")
            st.session_state["selected_date"] = d  # keep selection
        else:
            st.info("Nothing to delete for that date.")

st.caption("Day-click calendar grid provided. If an advanced component is needed, FullCalendar embed can be added later with a fallback to this form.")

df = to_dataframe()
if not df.empty:
    st.dataframe(df.tail(10), width="stretch")
