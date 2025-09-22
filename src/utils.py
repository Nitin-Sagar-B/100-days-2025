from __future__ import annotations

from pathlib import Path
import streamlit as st


def ensure_dirs() -> None:
    Path("data").mkdir(parents=True, exist_ok=True)
    Path("backups").mkdir(parents=True, exist_ok=True)


def load_fontawesome() -> None:
    st.markdown(
        """
        <link
          rel="stylesheet"
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"
          integrity="sha512-0DCNgB4m4Yw1yK+MJtYbU5t64B7pIxZotF1r7c6rKqFQm6S0ZgT9g4o9Qv6a4mOyf3x9jE0l2lXwYkzjYcJ/1g=="
          crossorigin="anonymous"
          referrerpolicy="no-referrer" />
        """,
        unsafe_allow_html=True,
    )


def apply_theme_css() -> None:
    """Inject CSS variables to enforce the custom dark theme on every page.

    Streamlit pages are separate scripts; this ensures consistent theming
    in local, Cloud, and mobile environments.
    """
    st.markdown(
        """
    <meta name="theme-color" content="#373B4B" />
        <meta name="color-scheme" content="dark light" />
        <style>
        :root {
            --primary-color: #3BB7B7;          /* Crystal Teal */
            --accent-bright: #B32727;          /* Pomegranate */
            --background-color: #373B4B;       /* Navy Blazer */
            --secondary-background-color: #444C38; /* Rifle Green */
            --text-color: #EAECEF;             /* Soft light */
            --font: -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
        }
        html, body, .stApp { background-color: var(--background-color) !important; color: var(--text-color) !important; }
        body, .stApp, div, p, span, label { color: var(--text-color) !important; font-family: var(--font) !important; }
        div[data-testid="stAppViewContainer"] { background-color: var(--background-color) !important; }
        section[data-testid="stSidebar"] { background-color: var(--secondary-background-color) !important; }
        section[data-testid="stSidebar"] * { color: var(--text-color) !important; }
        div[data-testid="stHeader"] { background: transparent !important; }
    .stButton>button, .stDownloadButton>button { background: var(--primary-color) !important; color: #0C1618 !important; border: 0 !important; }
    .stButton>button:hover, .stDownloadButton>button:hover { filter: brightness(1.05); box-shadow: 0 0 0 2px var(--accent-bright)33 inset; }
        .stTabs [data-baseweb="tab"] { color: var(--text-color) !important; }
        [data-testid="stMarkdownContainer"] * { color: var(--text-color) !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )
