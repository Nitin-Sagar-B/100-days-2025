# 100-days-2025

Track habits and productivity for the last 100 days of 2025 (Sep 22 → Dec 31, 2025). Streamlit app with SQLite, charts, exports, tests, and CI.

## Features
- KPI cards and sparklines
- Calendar day editor (fallback form)
- Analytics: rolling averages, weekly breakdowns, correlations, streaks, weight trend
- SQLite at `data/habits.db`, weekly CSV backups in `backups/`
- Import/Export CSV and JSON
- Tests (pytest) and CI workflow

## Quickstart (Windows cmd)
```cmd
call env\Scripts\activate.bat
pip install -r requirements.txt
streamlit run app.py
```

If you need to create `env` first:
```cmd
py -3.11 -m venv env
call env\Scripts\activate.bat
pip install -r requirements.txt
```

## Structure
- `app.py` – entry
- `src/` – data layer, analytics, charts, utils
- `pages/` – Streamlit pages
- `.streamlit/config.toml` – dark theme
- `.github/workflows/ci.yml` – CI

## Notes
- FullCalendar embed can be added later; app ships with robust Streamlit form fallback.
- Offline-first; no secrets required.

MIT License
