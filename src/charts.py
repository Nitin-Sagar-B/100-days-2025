from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Define a minimalist dark template and consistent colorway aligned with the app theme
# Complementary minimalist dark palette for visualizations
PANTONE_DARK_BG = "#0D1117"   # deep graphite/navy (GitHub dark-esque)
PANTONE_DARK_FG = "#E6E7EB"   # soft light ink for legibility
PANTONE_PANEL = "#0F141B"     # slightly lifted panel
PANTONE_ACCENT = "#FF8A5B"    # keep warm coral as primary accent
COLORWAY = [
    PANTONE_ACCENT,    # warm coral
    "#7DD3FC",        # ice blue
    "#C084FC",        # lilac
    "#34D399",        # teal/green
    "#FBBF24",        # amber
]

BASE_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor=PANTONE_DARK_BG,
    plot_bgcolor=PANTONE_PANEL,
    font=dict(color=PANTONE_DARK_FG),
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
    # A warm-to-cool minimalist scale aligned with the palette
    heat_scale = [(0.0, "#1F2937"), (0.5, "#374151"), (1.0, PANTONE_ACCENT)]
    fig = px.imshow(pivot, aspect="auto", color_continuous_scale=heat_scale)
    fig.update_layout(coloraxis_showscale=True, **BASE_LAYOUT)
    fig.update_yaxes(title="Day of Week")
    fig.update_xaxes(title="Week #")
    return fig
