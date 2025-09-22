from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Joel Maisel Color Palette alignment for charts
JOEL_BG = "#373B4B"          # Navy Blazer (app background)
JOEL_PANEL = "#444C38"       # Rifle Green (panels/plots)
JOEL_TEXT = "#EAECEF"        # Soft light text
JOEL_PRIMARY = "#3BB7B7"     # Crystal Teal (primary accent)
JOEL_ALERT = "#B32727"       # Pomegranate (strong accent)

# Minimal, harmonious colorway derived from the primary/accent with soft tints
COLORWAY = [
    JOEL_PRIMARY,
    JOEL_ALERT,
    "#79D3D3",  # lighter teal tint
    "#E38E8E",  # lighter pomegranate tint
    "#A0E5D2",  # mint-teal
]

BASE_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor=JOEL_BG,
    plot_bgcolor=JOEL_PANEL,
    font=dict(color=JOEL_TEXT),
    colorway=COLORWAY,
)


def kpi_sparkline(df: pd.DataFrame, y: str) -> go.Figure:
    fig = px.line(df, x="date", y=y, height=100)
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), showlegend=False, **BASE_LAYOUT)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def time_series(df: pd.DataFrame, y_cols: list[str]) -> go.Figure:
    fig = go.Figure()
    for col in y_cols:
        fig.add_trace(go.Scatter(x=df["date"], y=df[col], name=col, mode="lines+markers"))
    fig.update_layout(hovermode="x unified", **BASE_LAYOUT)
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
    # A dark-to-accent scale aligned with the Joel palette for good contrast
    heat_scale = [
        (0.0, "#2F3542"),   # deep muted base
        (0.5, JOEL_PRIMARY), # mid values in teal
        (1.0, JOEL_ALERT),   # high intensity in pomegranate
    ]
    fig = px.imshow(pivot, aspect="auto", color_continuous_scale=heat_scale)
    fig.update_layout(coloraxis_showscale=True, **BASE_LAYOUT)
    fig.update_yaxes(title="Day of Week")
    fig.update_xaxes(title="Week #")
    return fig
