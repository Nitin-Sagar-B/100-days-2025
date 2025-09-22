import streamlit as st
import pandas as pd
from src.repo import init_db, to_dataframe
from src.analytics import add_rolling, weekly_breakdown, correlation_matrix, compute_streak
from src.charts import time_series

st.set_page_config(page_title="Analytics", page_icon="📈", layout="wide")
init_db()

st.title("Analytics")

df = to_dataframe()
if df.empty:
    st.info("No data yet.")
    st.stop()

df["date"] = pd.to_datetime(df["date"])  # type: ignore[assignment]
df = add_rolling(df)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Rolling averages (prod hours)")
    st.plotly_chart(time_series(df, ["productive_hours", "prod_7", "prod_30"]))
with col2:
    st.subheader("Weekly breakdown")
    weekly = weekly_breakdown(df)
    st.dataframe(weekly, use_container_width=True)

st.subheader("Correlations")
corr = correlation_matrix(df)
st.dataframe(corr.style.background_gradient(cmap="viridis"), use_container_width=True)

st.subheader("Streaks")
st.metric("Current streak (days)", compute_streak(df))

st.subheader("Weight trend")
if "weight_kg" in df.columns:
    w = df[["date", "weight_kg"]].dropna().copy()
    if not w.empty:
        w["weight_ma7"] = w["weight_kg"].rolling(7, min_periods=1).mean()
        st.plotly_chart(time_series(w, ["weight_kg", "weight_ma7"]))
