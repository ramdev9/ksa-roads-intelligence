# KSA Roads Intelligence

*Case study · AI PM Portfolio · 2026*

A Vision 2030 traffic-safety dashboard built on real, messy, half-documented Saudi government open data — and the judgment calls that came with it.

**[Live Dashboard →](https://ksa-roads-intelligence-production.up.railway.app)** · **[Source on GitHub](https://github.com/ramdev9/ksa-roads-intelligence)** · **[Designed case-study page](https://claude.ai/artifact/9EYXyz5uKJjT55Xrfffi1M)**

| | | | |
|---|---|---|---|
| **287,781** accidents, 2019 | **13** regions covered | **6→2** dead URLs found & fixed | **4 yrs** of real annual data |

---

## The Problem

Saudi Arabia spends SAR 30B+ a year on road infrastructure under Vision 2030 — NEOM, the Red Sea Project, Qiddiya. Whether that spend is actually reducing accidents is a question the data could answer, except it's siloed across KAPSARC, MOT, and GASTAT in different formats on different update cycles.

I set out to build one dashboard that pulls KAPSARC's open traffic and road datasets live, normalizes them, and surfaces the metrics a city planner or Vision 2030 analyst would actually want: where accidents are concentrated, how infrastructure spend is trending, and which regions need attention next.

## What I Built

A Streamlit dashboard with nine views across accident patterns, road-development trends, and regional risk — pulling directly from KAPSARC's API on every deploy, with a clearly-labeled sample-data fallback if the source is unreachable.

![KSA Roads Intelligence dashboard showing KPI metrics and regional accident charts](dashboard-preview.png)

## Field Notes — what the real data actually looked like

The gap between "KAPSARC has an open API" and "the dashboard shows real numbers" was most of the work. Four things I ran into, and what I did about each:

**01 · Fixed — Two of six dataset URLs were dead**
The road-development and vehicle-crossings endpoints both 404'd. KAPSARC's catalog search API turned up the datasets under renamed slugs (`...-in-the-kingdom-1999-2009` instead of the documented URL). Fixed in the download script rather than quietly falling back to sample data.

**02 · Reshaped — The accident data wasn't the schema I assumed**
Real KAPSARC exports arrive long-format and semicolon-delimited — one row per region/year/indicator, not the tidy wide table the dashboard was designed against. Had to pivot it, and map KAPSARC's region labels ("Eastern Region") onto the app's canonical list ("Eastern").

**03 · Cut — No investment dataset exists, anywhere in KAPSARC**
The original plan had an "Investment vs. Outcome" chart. It doesn't exist in the data — KAPSARC publishes no SAR-spend figures for roads. Rather than fabricate a number, I dropped the chart and replaced it with what the data actually supports: paved roads completed per year.

**04 · Scoped down — Forecasting was the plan; the data said no**
The accident series turned out to be 2016–2019 only: 4 annual points per region, not the 11+ years assumed going in. That's far short of what ARIMA or Prophet need to fit reliably. Rather than ship a forecast that looks precise but isn't, I built a composite risk-scoring model instead — ranking regions by fatality rate, accident rate, and year-over-year trend. Less flashy, more honest, still answers "which region needs attention next."

```
$ why not ARIMA/Prophet?
13 regions × 4 annual points each — too thin to forecast reliably.
→ composite risk score instead: 40% fatality rate, 30% accidents/100K, 30% avg YoY trend.
→ ranked into High/Medium/Low terciles, not false-precision percentages.
```

## Stack

Streamlit · Pandas · Plotly · KAPSARC Open Data API · Railway

## What's Next

All six downloaded KAPSARC datasets are now wired into charts — including one (trade & transport costs) that turned out to have zero Saudi Arabia-specific records, which the dashboard says outright rather than hiding. Regional population — needed for per-100K rates — is still an approximate reference table, not a KAPSARC field, and is labeled as such in the app. If KAPSARC ever publishes more than four years of accident data, the risk model is the right place to revisit real forecasting.

---

*Ram Nimbalker · AI Product Manager · [madebyram.com](https://madebyram.com)*
