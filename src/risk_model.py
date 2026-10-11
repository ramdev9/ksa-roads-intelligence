"""
Regional risk scoring for KSA Roads Intelligence Dashboard.

Not a forecasting model. The accident dataset is annual-only with ~4
years per region (2016-2019 from KAPSARC's current export), which is too
thin for ARIMA/Prophet-style time-series forecasting — that needs tens
of points per series to fit reliably. Instead this computes a composite
risk score per region from the data that does exist: how severe
accidents currently are, how frequent they are relative to population,
and whether the trend is getting better or worse.
"""

import pandas as pd


def _normalize(series: pd.Series) -> pd.Series:
    """Min-max normalize to [0, 1]. Returns all zeros if the series is constant."""
    span = series.max() - series.min()
    if span == 0:
        return series * 0
    return (series - series.min()) / span


def compute_yoy_trend(accidents_df: pd.DataFrame) -> pd.DataFrame:
    """Year-over-year % change in accidents per region, plus each region's average YoY change."""
    df = accidents_df.sort_values(["region", "year"]).copy()
    df["yoy_pct"] = df.groupby("region")["accidents"].pct_change() * 100
    return df[["region", "year", "accidents", "yoy_pct"]]


def compute_risk_scores(accidents_df: pd.DataFrame) -> pd.DataFrame:
    """
    Composite risk score (0-100) per region, using the latest year's
    fatality rate and accidents-per-100k, weighted with each region's
    average year-over-year accident trend.

    Weights: 40% fatality rate, 30% accidents per 100K, 30% YoY trend
    direction. Regions are ranked into terciles (High/Medium/Low) rather
    than fixed thresholds, since the underlying scale is relative, not
    absolute — there's no external baseline to compare against.
    """
    latest_year = accidents_df["year"].max()
    latest = accidents_df[accidents_df["year"] == latest_year][
        ["region", "accidents", "fatality_rate", "accidents_per_100k"]
    ].copy()

    yoy = compute_yoy_trend(accidents_df)
    avg_yoy = (
        yoy.groupby("region")["yoy_pct"]
        .mean()
        .reset_index()
        .rename(columns={"yoy_pct": "avg_yoy_pct"})
    )

    scored = latest.merge(avg_yoy, on="region")

    scored["fatality_norm"] = _normalize(scored["fatality_rate"])
    scored["rate_norm"] = _normalize(scored["accidents_per_100k"])
    scored["trend_norm"] = _normalize(scored["avg_yoy_pct"])

    scored["risk_score"] = (
        0.4 * scored["fatality_norm"] + 0.3 * scored["rate_norm"] + 0.3 * scored["trend_norm"]
    ) * 100

    scored = scored.sort_values("risk_score", ascending=False).reset_index(drop=True)

    try:
        scored["risk_level"] = pd.qcut(
            scored["risk_score"], q=3, labels=["Low", "Medium", "High"], duplicates="drop"
        )
    except ValueError:
        # Too few distinct values to cut into 3 bins — fall back to a simple split.
        median = scored["risk_score"].median()
        scored["risk_level"] = scored["risk_score"].apply(lambda s: "High" if s >= median else "Low")

    return scored[
        ["region", "accidents", "fatality_rate", "accidents_per_100k", "avg_yoy_pct", "risk_score", "risk_level"]
    ]
