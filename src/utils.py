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
