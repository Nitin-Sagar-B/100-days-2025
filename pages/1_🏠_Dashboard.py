import streamlit as st
import pandas as pd
from datetime import date

from src.repo import init_db, to_dataframe
from src.analytics import add_rolling, composite_score
from src.charts import kpi_sparkline, time_series, calendar_heatmap

st.set_page_config(page_title="Dashboard", page_icon="🏠", layout="wide")
init_db()

st.title("Dashboard")

df = to_dataframe()
if not df.empty:
    df["date"] = pd.to_datetime(df["date"])  # ensure datetime
    df = add_rolling(df)
    score = composite_score(df)
else:
    st.info("No data yet. Go to Data or run the seed script.")

col1, col2, col3, col4, col5 = st.columns(5)
if not df.empty:
    latest = df.iloc[-1]
    with col1:
        st.metric("Productive hours", f"{latest['productive_hours']:.1f}")
        st.plotly_chart(kpi_sparkline(df.tail(30), "productive_hours"), use_container_width=True)
    with col2:
        st.metric("Water (ml)", f"{int(latest['water_ml'])}")
        st.plotly_chart(kpi_sparkline(df.tail(30), "water_ml"), use_container_width=True)
    with col3:
        st.metric("Sugar (g)", f"{int(latest['sugar_intake_g'])}")
        st.plotly_chart(kpi_sparkline(df.tail(30), "sugar_intake_g"), use_container_width=True)
    with col4:
        st.metric("Fap count", f"{int(latest['fap_count'])}")
        st.plotly_chart(kpi_sparkline(df.tail(30), "fap_count"), use_container_width=True)
    with col5:
        st.metric("Weight (kg)", f"{latest['weight_kg'] if pd.notnull(latest['weight_kg']) else '—'}")
        st.plotly_chart(kpi_sparkline(df.tail(30), "weight_kg"), use_container_width=True)

st.subheader("Calendar heatmap (composite score)")
if not df.empty:
    sc = composite_score(df)
    sc.name = "score"
    st.plotly_chart(calendar_heatmap(df, sc), use_container_width=True)

st.subheader("Time series")
if not df.empty:
    st.plotly_chart(
        time_series(df, ["productive_hours", "water_ml", "sugar_intake_g", "fap_count"]),
        use_container_width=True,
    )
