import streamlit as st
from src.utils import apply_theme_css
from datetime import date
from pathlib import Path
import pandas as pd

from src.repo import init_db, to_dataframe, export_csv, export_json, import_csv, weekly_auto_backup, delete_day

st.set_page_config(page_title="Data & Export", page_icon="🗄️", layout="wide")
init_db()
apply_theme_css()

st.title("Data & Export")

df = to_dataframe()
st.dataframe(df, width="stretch")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Export CSV"):
        p = export_csv(Path("data/export.csv"))
        st.success(f"Saved {p}")
with col2:
    if st.button("Export JSON"):
        p = export_json(Path("data/export.json"))
        st.success(f"Saved {p}")
with col3:
    if st.button("Backup (CSV)"):
        p = weekly_auto_backup()
        st.success(f"Backup at {p}")

st.subheader("Import CSV")
up = st.file_uploader("Choose CSV", type=["csv"])
if up is not None:
    temp = Path("data/_import.csv")
    temp.write_bytes(up.getvalue())
    try:
        n = import_csv(temp, drop_conflicts=True)
        st.success(f"Imported {n} rows")
    except Exception as e:
        st.error(str(e))

st.subheader("Restore from backup")
backup_files = sorted(Path("backups").glob("*.csv"))
if backup_files:
    sel = st.selectbox("Select backup CSV", backup_files, format_func=lambda p: p.name)
    if st.button("Restore selected backup"):
        try:
            n = import_csv(sel, drop_conflicts=True)
            st.success(f"Restored {n} rows from {sel.name}")
        except Exception as e:
            st.error(str(e))
else:
    st.caption("No backups found yet. Create one above.")

st.subheader("Delete a day")
if not df.empty:
    dsel = st.selectbox("Pick date to delete", df["date"].dt.date.tolist())
    if st.button("Delete selected day", type="secondary"):
        if delete_day(dsel):
            st.success(f"Deleted {dsel}")
        else:
            st.info("That date wasn't in the database.")
else:
    st.caption("No rows to delete yet.")
