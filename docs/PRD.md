# PRD · 2026-ERA TEMPLATE

## KSA Roads Intelligence

A data dashboard that turns Saudi Arabia's scattered transportation datasets into one view — with trend analysis, regional comparison, and a forecasting model that flags which regions are likely to see accident spikes next quarter.

| Field | Value |
|-------|-------|
| Owner | Ram |
| Status | Live on Railway with real KAPSARC data; forecasting model pending |
| Repo | ksa-roads-intelligence |
| Live | ksa-roads-intelligence-production.up.railway.app |
| Updated | 2026-10-11 |

---

## 01 · The Decision This Records

**NEW**

We're building a unified dashboard over KAPSARC open data as the foundation — regional accident stats, road development metrics, vehicle counts — with a simple time-series forecasting model on top, because showing predictions (not just history) is what separates a portfolio piece from a Kaggle notebook.

---

## 02 · Purpose

**TIMELESS**

### What

A dashboard that pulls Saudi transportation data from KAPSARC's open API, normalizes it into a single schema, and displays:
- Accidents by region and year
- Road infrastructure growth over time
- Investment vs outcome correlation
- A forecast of next-quarter accident risk by region

### Who it's for

City planners, transport ministry analysts, and journalists covering Vision 2030 infrastructure — anyone who currently has to download separate Excel files from three different government portals and manually paste them together.

### Why it matters

Saudi Arabia is spending SAR 30B+ annually on road infrastructure under Vision 2030. The data to evaluate whether that spend is reducing accidents exists, but it's scattered across KAPSARC, MOT, and GASTAT in different formats and update cycles.

### Hypothesis

We believe that consolidating 5+ KAPSARC datasets into one normalized schema, adding derived safety metrics (accidents per 100K, fatality rate), and running a basic forecast model will produce a tool that answers "which regions need intervention next" faster than the current manual process.

---

## 03 · The Prototype

**NEW**

Running locally:

```
streamlit run src/dashboard.py
```

Opens at http://localhost:8501 — no auth, sample data included, real data requires running `python scripts/download_data.py` first.

---

## 04 · Features & How They Work

**TIMELESS**

### DATA PIPELINE

```
KAPSARC API → download_data.py → data/raw/*.csv → data_loader.py (reshape + derive) → normalized DataFrames
```

`dashboard.py` tries real data first (`use_sample=False`) and falls back to bundled sample CSVs if the raw files aren't present, with an in-app caption showing which source is active.

Six datasets downloaded from KAPSARC; two are actively used by the dashboard:
- **Traffic accidents and casualties by region** — used. Raw format is long/semicolon-delimited (`time_period;region;indicator;value`), covers **2016-2019 only**, 13 regions + a "Total" row. `data_loader.py` pivots this to wide form and maps KAPSARC's region labels (e.g. "Eastern Region" → "Eastern") onto the app's canonical region list.
- **Road development (paved + agricultural dirt roads)** — used. Raw format gives km **completed per year**, not a running network total, and covers **1990-2013 with gaps** (not continuous, stops well before the accident data starts). No highway-specific or investment figures exist in this dataset.
- King Fahd Bridge vehicle crossings (monthly) — downloaded, not yet wired into a chart
- Passenger and freight vehicles by type — downloaded, not yet wired into a chart
- Trade and transport costs — downloaded, not yet wired into a chart
- Vehicle crossings at major cities — downloaded (9 cities, point-in-time, not a time series), not yet wired into a chart

**Known gaps vs. the original plan:** KAPSARC has no investment/spend dataset for Saudi roads, so the "Investment vs outcome correlation" hypothesis in section 02 can't be tested with this data source — the investment chart was dropped and replaced with "Paved Roads Completed per Year." The accident and road-development series also don't overlap in time (2016-19 vs 1990-2013), so no single chart can correlate them. Population-by-region (needed for `accidents_per_100k`) isn't in any KAPSARC dataset either — `data_loader.py` uses a small hardcoded table of approximate GASTAT-era regional population estimates (~2019), clearly caveated in the UI as a reference figure, not sourced from KAPSARC.

### DERIVED METRICS

Calculated at load time, not stored:
- `accidents_per_100k` = (accidents / population) × 100,000 — population from the approximate reference table above
- `fatality_rate` = (deaths / accidents) × 100
- `cumulative_paved_km` / `cumulative_dirt_km` = running sum of km completed per year, starting from the dataset's earliest year (not a true historical network total, since the pre-1990 baseline is unknown)
- `paved_growth_pct` = year-over-year % change in km completed

### DASHBOARD VIEWS

| View | What it shows |
|------|---------------|
| KPI Row | Total accidents, injuries, deaths, avg fatality rate (latest year) |
| Regional Bar | Accidents by region, sorted |
| Trend Line | Accidents/injuries/deaths over time |
| Infrastructure Area | Cumulative paved + dirt roads completed since 1990 |
| Completions Bar | Paved roads completed per year (km) |
| Safety Scatter | Accident rate vs fatality rate by region |
| Heatmap | Accidents by region × year |

### FORECASTING MODEL (v2)

Not yet built. Planned:
- Simple ARIMA or Prophet model on regional accident time-series
- Output: predicted accident count for next 4 quarters by region
- Confidence intervals shown on chart
- "High risk" flag when prediction exceeds 1.5× historical average

### BEHAVIOUR CONTRACT

- All data from KAPSARC open API, no scraping
- No PII, all aggregated regional statistics
- Forecasts labeled as predictions, not facts
- Last-updated timestamp shown on every view

---

## 05 · Success Measurement & Evals

**NEW**

### Metric to graduate

Dashboard loads all 6 datasets without error, displays all 7 chart types correctly, and forecasting model (when built) achieves MAPE < 15% on held-out 2022 data.

### Eval approach

| Check | Method |
|-------|--------|
| Data integrity | Row counts match KAPSARC source |
| Schema validation | All expected columns present |
| Derived metrics | Spot-check 5 rows manually |
| Forecast accuracy | Train on 2018-2021, test on 2022 |

No automated eval harness yet — this is a data/BI project, not an LLM output validation problem.

---

## 06 · Scope & Non-Goals

**MERGED**

### IN

- KAPSARC data ingestion (6 datasets)
- Normalized data model
- Streamlit dashboard with 7 chart types
- Derived safety metrics
- Time-series forecasting model
- Dark theme, mobile-responsive

### OUT

- Real-time data (KAPSARC updates monthly/quarterly)
- Arabic language UI (English only for v1)
- User accounts or saved views
- Direct integration with MOT or GASTAT APIs
- Map visualization (would need geocoding)

### Trade-offs accepted

Sample data ships with the repo so the dashboard works without API access. Real data requires running the download script locally — KAPSARC's API is open but not cached here.

---

## 07 · Rollout & Rollback

**NEW**

This is a portfolio project, not a production system. No staged rollout needed.

Kill switch: if KAPSARC changes their API schema, the download script fails loudly rather than ingesting malformed data.

---

## 08 · Release Criteria & Change Log

**TIMELESS**

### Definition of done

Dashboard displays all 7 chart types with sample data, download script fetches all 6 KAPSARC datasets successfully, and README documents the full setup process. Testable — run `streamlit run src/dashboard.py` and visually confirm.

### Change Log

| Date | Change | Status |
|------|--------|--------|
| 2026-10-11 | Project scaffolded | DONE |
| 2026-10-11 | Sample data created | DONE |
| 2026-10-11 | Dashboard v1 (7 charts) | DONE |
| 2026-10-11 | Pushed to GitHub (ramdev9/ksa-roads-intelligence) | DONE |
| 2026-10-11 | Download script tested with real KAPSARC data; 2 of 6 URLs were dead and fixed | DONE |
| 2026-10-11 | Real-data transform built for accidents + road development; dashboard reads real data with sample fallback; investment chart dropped (no real data for it) | DONE |
| 2026-10-11 | Deployed to Railway: ksa-roads-intelligence-production.up.railway.app | DONE |
| TBD | Forecasting model added | PENDING |
| TBD | Portfolio page written | PENDING |

---

## THE GOLDEN STANDARD · 2026

Could a developer or an AI agent build this feature from only this document, without asking a single question?

**Gap:** Forecasting model spec is vague — needs input/output schema, model choice rationale, and accuracy threshold before someone could implement it blind.

---

*KSA Roads Intelligence · ksa-roads-intelligence · PRD drafted 2026-10-11*
