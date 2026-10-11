"""
Data loading and processing for KSA Roads Intelligence Dashboard.
"""

import pandas as pd
from pathlib import Path
from typing import Dict

DATA_DIR = Path(__file__).parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# Approximate regional population reference values (GASTAT-era estimates,
# ~2019). KAPSARC's accident dataset has no population field, so this is
# used only to derive accidents-per-100k; treat it as a rough reference,
# not an authoritative census figure.
POPULATION_BY_REGION = {
    "Riyadh": 8_220_000,
    "Makkah": 8_350_000,
    "Eastern": 5_000_000,
    "Madinah": 2_130_000,
    "Qassim": 1_370_000,
    "Asir": 2_220_000,
    "Tabuk": 910_000,
    "Hail": 730_000,
    "Northern Borders": 375_000,
    "Jazan": 1_570_000,
    "Najran": 595_000,
    "Al-Baha": 476_000,
    "Al-Jouf": 508_000,
}

# KAPSARC's raw region labels differ slightly from the names used elsewhere
# in this app.
REGION_NAME_MAP = {
    "Eastern Region": "Eastern",
    "Tabouk": "Tabuk",
}


def _add_accident_metrics(df: pd.DataFrame) -> pd.DataFrame:
    df["accidents_per_100k"] = (df["accidents"] / df["population"]) * 100000
    df["fatality_rate"] = (df["deaths"] / df["accidents"]) * 100
    df["injury_rate"] = (df["injuries"] / df["accidents"]) * 100
    return df


def _load_real_traffic_accidents() -> pd.DataFrame:
    filepath = RAW_DIR / "traffic_accidents.csv"
    if not filepath.exists():
        raise FileNotFoundError(f"Data file not found: {filepath}")

    raw = pd.read_csv(filepath, sep=";", usecols=["time_period", "region", "indicator", "value"])
    raw = raw[raw["region"] != "Total"].copy()
    raw["region"] = raw["region"].replace(REGION_NAME_MAP)

    wide = raw.pivot_table(
        index=["time_period", "region"], columns="indicator", values="value", aggfunc="sum"
    ).reset_index()
    wide = wide.rename(columns={
        "time_period": "year",
        "No. of Accidents": "accidents",
        "No. of Casualties - Injured": "injuries",
        "No. of Casualties - Dead": "deaths",
    })
    wide["population"] = wide["region"].map(POPULATION_BY_REGION)
    return wide[["year", "region", "accidents", "injuries", "deaths", "population"]]


def load_traffic_accidents(use_sample: bool = True) -> pd.DataFrame:
    """Load traffic accidents data by region and year."""
    if use_sample:
        filepath = RAW_DIR / "sample_traffic_accidents.csv"
        if not filepath.exists():
            raise FileNotFoundError(f"Data file not found: {filepath}")
        df = pd.read_csv(filepath)
    else:
        df = _load_real_traffic_accidents()

    return _add_accident_metrics(df)


def _load_real_road_development() -> pd.DataFrame:
    filepath = RAW_DIR / "road_development.csv"
    if not filepath.exists():
        raise FileNotFoundError(f"Data file not found: {filepath}")

    df = pd.read_csv(filepath, sep=";")
    df = df.rename(columns={
        "gregorian_year": "year",
        "paved_roads_completed_during_the_year": "paved_roads_completed_km",
        "agricultural_dirt_roads_completed_during_the_year": "dirt_roads_completed_km",
    })
    df = df[["year", "paved_roads_completed_km", "dirt_roads_completed_km"]].sort_values("year")
    return df


def load_road_development(use_sample: bool = True) -> pd.DataFrame:
    """Load road infrastructure development data.

    KAPSARC publishes roads *completed per year*, not a running network
    total and not investment spend — so this returns per-year completions
    plus a cumulative sum of what's been completed since the earliest
    year in the dataset (not the true historical network size).
    """
    if use_sample:
        filepath = RAW_DIR / "sample_road_development.csv"
        if not filepath.exists():
            raise FileNotFoundError(f"Data file not found: {filepath}")
        df = pd.read_csv(filepath).sort_values("year")
    else:
        df = _load_real_road_development()

    df["cumulative_paved_km"] = df["paved_roads_completed_km"].cumsum()
    df["cumulative_dirt_km"] = df["dirt_roads_completed_km"].cumsum()
    df["paved_growth_pct"] = df["paved_roads_completed_km"].pct_change() * 100

    return df


def get_regions() -> list:
    """Get list of Saudi regions."""
    return [
        "Riyadh",
        "Makkah",
        "Eastern",
        "Madinah",
        "Asir",
        "Jazan",
        "Qassim",
        "Tabuk",
        "Hail",
        "Najran",
        "Northern Borders",
        "Al-Baha",
        "Al-Jouf"
    ]


def get_summary_stats(df: pd.DataFrame) -> Dict:
    """Calculate summary statistics for dashboard KPIs."""
    latest_year = df["year"].max()
    latest_data = df[df["year"] == latest_year]

    return {
        "total_accidents": int(latest_data["accidents"].sum()),
        "total_injuries": int(latest_data["injuries"].sum()),
        "total_deaths": int(latest_data["deaths"].sum()),
        "avg_fatality_rate": round(latest_data["fatality_rate"].mean(), 2),
        "year": latest_year
    }


if __name__ == "__main__":
    # Test data loading
    print("Testing data loaders...\n")

    try:
        accidents_df = load_traffic_accidents()
        print(f"Traffic Accidents: {len(accidents_df)} rows")
        print(accidents_df.head())
        print(f"\nSummary: {get_summary_stats(accidents_df)}")
    except FileNotFoundError as e:
        print(f"Error: {e}")

    print("\n" + "="*50 + "\n")

    try:
        roads_df = load_road_development()
        print(f"Road Development: {len(roads_df)} rows")
        print(roads_df.head())
    except FileNotFoundError as e:
        print(f"Error: {e}")
