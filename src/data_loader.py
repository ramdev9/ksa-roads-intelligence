"""
Data loading and processing for KSA Roads Intelligence Dashboard.
"""

import pandas as pd
from pathlib import Path
from typing import Dict

DATA_DIR = Path(__file__).parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"


def load_traffic_accidents(use_sample: bool = True) -> pd.DataFrame:
    """Load traffic accidents data by region and year."""
    if use_sample:
        filepath = RAW_DIR / "sample_traffic_accidents.csv"
    else:
        filepath = RAW_DIR / "traffic_accidents.csv"

    if not filepath.exists():
        raise FileNotFoundError(f"Data file not found: {filepath}")

    df = pd.read_csv(filepath)

    # Calculate derived metrics
    df["accidents_per_100k"] = (df["accidents"] / df["population"]) * 100000
    df["fatality_rate"] = (df["deaths"] / df["accidents"]) * 100
    df["injury_rate"] = (df["injuries"] / df["accidents"]) * 100

    return df


def load_road_development(use_sample: bool = True) -> pd.DataFrame:
    """Load road infrastructure development data."""
    if use_sample:
        filepath = RAW_DIR / "sample_road_development.csv"
    else:
        filepath = RAW_DIR / "road_development.csv"

    if not filepath.exists():
        raise FileNotFoundError(f"Data file not found: {filepath}")

    df = pd.read_csv(filepath)

    # Calculate year-over-year growth
    df["total_growth_pct"] = df["total_km"].pct_change() * 100
    df["investment_growth_pct"] = df["investment_sar_billion"].pct_change() * 100

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
