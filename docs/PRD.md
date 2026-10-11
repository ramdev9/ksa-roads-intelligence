# PRD · 2026-ERA TEMPLATE

## KSA Roads Intelligence

A data dashboard that turns Saudi Arabia's scattered transportation datasets into one view — with trend analysis, regional comparison, and a forecasting model that flags which regions are likely to see accident spikes next quarter.

| Field | Value |
|-------|-------|
| Owner | Ram |
| Status | Structure complete, data pending |
| Repo | ksa-roads-intelligence |
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
KAPSARC API → download_data.py → data/raw/*.csv → data_loader.py → normalized DataFrames
```

Six datasets from KAPSARC:
- Traffic accidents and casualties by region
- King Fahd Bridge vehicle crossings (monthly)
- Passenger and freight vehicles by type
- Trade and transport costs
- Road development (paved, rural, highways)
- Vehicle crossings at major cities

### DERIVED METRICS

Calculated at load time, not stored:
- `accidents_per_100k` = (accidents / population) × 100,000
- `fatality_rate` = (deaths / accidents) × 100
- `yoy_growth` = year-over-year percentage change

### DASHBOARD VIEWS

| View | What it shows |
|------|---------------|
| KPI Row | Total accidents, injuries, deaths, avg fatality rate (latest year) |
| Regional Bar | Accidents by region, sorted |
| Trend Line | Accidents/injuries/deaths over time |
| Infrastructure Area | Paved roads + highways growth |
| Investment Bar | Annual SAR spend on roads |
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
| TBD | Download script tested with real KAPSARC data | PENDING |
| TBD | Forecasting model added | PENDING |
| TBD | Portfolio page written | PENDING |

---

## THE GOLDEN STANDARD · 2026

Could a developer or an AI agent build this feature from only this document, without asking a single question?

**Gap:** Forecasting model spec is vague — needs input/output schema, model choice rationale, and accuracy threshold before someone could implement it blind.

---

*KSA Roads Intelligence · ksa-roads-intelligence · PRD drafted 2026-10-11*
