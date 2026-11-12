# Team 1 API Choice

**API:** USGS Earthquake Catalog API

**Endpoint 1:** Recent earthquake query using the USGS FDSN Event query service with GeoJSON format, a minimum magnitude of 2.5, results ordered by time, and a limit of 10 earthquakes.

**Endpoint 2:** Specific earthquake detail query using the USGS FDSN Event query service with an earthquake event ID.

**Connection:** Both calls use the earthquake event ID, so we can use the ID from the recent earthquake results to retrieve and connect the detailed information for the same earthquake.

## Sprint 1 Roles

### Program Manager 
- Week 1: Danny Truong
- Week 2: Joshua Hanes
- Approval Rotation: Joshua → Danny → Hira → Vishvag → Joshua
- Tester: Vishvag

## Sprint 1 Statement

By September 24, we can answer one real question about whether shallow earthquakes feel stronger than deeper ones by running a SQL query across data our own code has been collecting since September 10.

## Sprint 2 Roles

### Program Manager
- Week 1, Sept. 24–Oct. 1: [Hira]
- Week 2, Oct. 2–Oct. 8: [Vishvag]
- Week 3, Oct. 9–Oct. 15: [Joshua]

### Reviewer Ring
Joshua → Danny → Hira → Vishvag → Joshua

### Tester
[Danny]

## Sprint 2 Dashboard
Public dashboard: https://f26-day2-team-1-itrbe4l8dsa5dbcui2bgpv.streamlit.app/

From the repository root, install dependencies with: `pip install -r requirements.txt`, then run: `streamlit run src/app.py`.

## Sprint 3 Roles

### Program Manager
- Week 1: [Danny]
- Week 2: [Joshua]
- Week 3: [Hira]
- Week 4: [Vishvag]

### Reviewer Ring
Joshua → Danny → Hira → Vishvag → Joshua

### Tester
[Hira]

## Sprint 3 Summary

The Daily earthquake refresh workflow runs every day at 11:00 AM. It fetches a new USGS earthquake snapshot, then `src/summarize.py` rebuilds the database and calculates the total event count and each depth group's average magnitude and significance. Groq turns those statistics into a short summary. The workflow saves it to `data/summary.md` and commits it to `main` alongside the snapshots.

The dashboard displays the saved summary and the dates it covers. The summary uses all collected data, so the dashboard filters do not change it. If summary generation fails, the previous summary stays in place and the workflow still commits the new snapshots.

### Required secrets

- GitHub Actions — `GROQ_API_KEY`: lets the workflow generate the daily summary
- GitHub Actions — `REFRESH_TOKEN1`: lets the workflow push the snapshots and summary to the repo
- Streamlit — `GROQ_API_KEY`: lets the live dashboard chatbot answer questions