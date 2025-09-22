from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def kpi_sparkline(df: pd.DataFrame, y: str) -> go.Figure:
    fig = px.line(df, x="date", y=y, height=100)
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), template="plotly_dark", showlegend=False)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def time_series(df: pd.DataFrame, y_cols: list[str]) -> go.Figure:
    fig = go.Figure()
    for col in y_cols:
        fig.add_trace(go.Scatter(x=df["date"], y=df[col], name=col, mode="lines+markers"))
    fig.update_layout(template="plotly_dark", hovermode="x unified")
    fig.update_xaxes(rangeselector=dict(
        buttons=list([
            dict(count=7, label="7d", step="day", stepmode="backward"),
            dict(count=30, label="30d", step="day", stepmode="backward"),
            dict(step="all")
        ])
    ))
    return fig


def calendar_heatmap(df: pd.DataFrame, values: pd.Series) -> go.Figure:
    # Simple heatmap by day index (fallback to visual calendar look)
    if df.empty or values is None or len(values) == 0:
        return go.Figure()
    x = df.copy()
    # align values with df index and give it a stable column name
    col = values.name or "value"
    x[col] = values.values
    x["dow"] = x["date"].dt.weekday
    x["week"] = x["date"].dt.isocalendar().week
    pivot = x.pivot_table(index="dow", columns="week", values=col, aggfunc="mean")
    fig = px.imshow(pivot, aspect="auto", color_continuous_scale="Viridis")
    fig.update_layout(template="plotly_dark", coloraxis_showscale=True)
    fig.update_yaxes(title="Day of Week")
    fig.update_xaxes(title="Week #")
    return fig
