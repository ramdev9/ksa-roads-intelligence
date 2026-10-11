"""
Download Saudi Arabia transportation datasets from KAPSARC.
Run this script locally (not in cloud) to fetch the data.

Usage: python scripts/download_data.py
"""

import os
import requests
from pathlib import Path

# KAPSARC Open Data API endpoints
DATASETS = {
    "king_fahd_bridge_traffic": {
        "url": "https://datasource.kapsarc.org/api/v2/catalog/datasets/traffic-on-king-fahd-bridge-between-the-kingdom-and-bahrain-by-month-during-2009/exports/csv",
        "description": "Monthly traffic on King Fahd Bridge (Saudi-Bahrain) 2009-2019"
    },
    "passenger_freight_vehicles": {
        "url": "https://datasource.kapsarc.org/api/v2/catalog/datasets/number-of-passenger-and-freight-vehicles/exports/csv",
        "description": "Number of passenger and freight vehicles by type"
    },
    "trade_transport": {
        "url": "https://datasource.kapsarc.org/api/v2/catalog/datasets/trade-and-transport-data/exports/csv",
        "description": "Trade and transport costs, freight rates, shipment weights"
    },
    "traffic_accidents": {
        "url": "https://datasource.kapsarc.org/api/v2/catalog/datasets/saudi-arabia-traffic-accidents-and-casualties-injured-dead-2008/exports/csv",
        "description": "Traffic accidents and casualties by region (2008+)"
    },
    "vehicle_crossings_cities": {
        "url": "https://datasource.kapsarc.org/api/v2/catalog/datasets/number-of-vehicles-crossings-of-major-cities/exports/csv",
        "description": "Vehicle crossings at major Saudi cities"
    },
    "road_development": {
        "url": "https://datasource.kapsarc.org/api/v2/catalog/datasets/development-of-paved-and-rural-roads-construction/exports/csv",
        "description": "Development of paved and rural roads construction"
    }
}

def download_datasets(output_dir: str = "data/raw"):
    """Download all KAPSARC datasets to the specified directory."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"Downloading {len(DATASETS)} datasets to {output_path}/\n")

    for name, info in DATASETS.items():
        filename = f"{name}.csv"
        filepath = output_path / filename

        print(f"Downloading: {info['description']}")
        print(f"  URL: {info['url']}")

        try:
            response = requests.get(info["url"], timeout=30)
            response.raise_for_status()

            with open(filepath, "wb") as f:
                f.write(response.content)

            size_kb = len(response.content) / 1024
            print(f"  Saved to {filepath} ({size_kb:.1f} KB)\n")

        except requests.exceptions.RequestException as e:
            print(f"  Failed: {e}\n")

    print("Done! Run 'python src/data_loader.py' to process the data.")

if __name__ == "__main__":
    download_datasets()
