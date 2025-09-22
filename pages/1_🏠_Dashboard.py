import streamlit as st
import pandas as pd
from datetime import date

from src.repo import init_db, to_dataframe
from src.analytics import add_rolling, composite_score
from src.charts import kpi_sparkline, time_series, calendar_heatmap
from src.utils import apply_theme_css

st.set_page_config(page_title="Dashboard", page_icon="🏠", layout="wide")
init_db()
apply_theme_css()

st.title("Dashboard")

df = to_dataframe()
if not df.empty:
    df["date"] = pd.to_datetime(df["date"])  # ensure datetime
    df = add_rolling(df)
    score = composite_score(df)
else:
    st.info("No data yet. Use the Calendar or Data page to add your first day.")

if not df.empty:
    latest = df.iloc[-1]

    # Row 1: Productive hours
    st.markdown("**Productive hours (h) — last 30 days**")
    st.metric("Productive (hours)", f"{latest['productive_hours']:.1f} h")
    st.plotly_chart(kpi_sparkline(df.tail(30), "productive_hours"), width="stretch")
    st.divider()

    # Row 2: Water intake in liters
    latest_water_l = float(latest["water_ml"]) / 1000.0
    st.markdown("**Water intake (L) — last 30 days**")
    st.metric("Water (L)", f"{latest_water_l:.2f} L")
    df_water = df.copy()
    df_water["water_l"] = df_water["water_ml"] / 1000.0
    st.plotly_chart(kpi_sparkline(df_water.tail(30), "water_l"), width="stretch")
    st.divider()

    # Row 3: Sugar intake grams
    st.markdown("**Sugar intake (g) — last 30 days**")
    st.metric("Sugar (g)", f"{int(latest['sugar_intake_g'])}")
    st.plotly_chart(kpi_sparkline(df.tail(30), "sugar_intake_g"), width="stretch")
    st.divider()

    # Row 4: Fap count
    st.markdown("**Fap count — last 30 days**")
    st.metric("Fap count", f"{int(latest['fap_count'])}")
    st.plotly_chart(kpi_sparkline(df.tail(30), "fap_count"), width="stretch")
    st.divider()

    # Row 5: Weight kg
    st.markdown("**Weight (kg) — last 30 days**")
    weight_val = f"{latest['weight_kg']} kg" if pd.notnull(latest['weight_kg']) else "— kg"
    st.metric("Weight (kg)", weight_val)
    st.plotly_chart(kpi_sparkline(df.tail(30), "weight_kg"), width="stretch")

st.subheader("Calendar heatmap (composite score)")
if not df.empty:
    sc = composite_score(df)
    sc.name = "score"
    st.plotly_chart(calendar_heatmap(df, sc), width="stretch")

st.subheader("Time series")
if not df.empty:
    # 1) Productive hours
    st.markdown("**Productive hours (h)**")
    st.plotly_chart(time_series(df, ["productive_hours"]), width="stretch")

    # 2) Water in liters
    st.markdown("**Water intake (L)**")
    df2 = df.copy()
    df2["water_l"] = df2["water_ml"] / 1000.0
    st.plotly_chart(time_series(df2, ["water_l"]), width="stretch")

    # 3) Sugar intake grams
    st.markdown("**Sugar intake (g)**")
    st.plotly_chart(time_series(df, ["sugar_intake_g"]), width="stretch")

    # 4) Fap count
    st.markdown("**Fap count**")
    st.plotly_chart(time_series(df, ["fap_count"]), width="stretch")

    # 5) Weight kg
    st.markdown("**Weight (kg)**")
    st.plotly_chart(time_series(df, ["weight_kg"]), width="stretch")
