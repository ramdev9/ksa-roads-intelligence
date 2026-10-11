# KSA Roads Intelligence Dashboard

Interactive data visualization of Saudi Arabia's road infrastructure and traffic safety metrics. Built to demonstrate Data/BI skills using real KSA government open data.

![Dashboard Preview](docs/dashboard-preview.png)

## 🎯 Problem Statement

Saudi Arabia's Vision 2030 involves massive infrastructure development including NEOM, Red Sea Project, and Qiddiya. City planners and transport authorities need consolidated visibility into:

- Current road network utilization
- Traffic accident hotspots by region
- Infrastructure investment trends
- Safety metrics to prioritize interventions

Currently, this data is siloed across multiple government agencies (MOT, GASTAT, KAPSARC).

## 💡 Solution

A unified dashboard that combines multiple Saudi transportation datasets:

- **Traffic Accidents by Region** (2018-2022): Accidents, injuries, deaths, population
- **Road Infrastructure Development** (2010-2024): Paved roads, highways, investments
- Cross-regional safety analysis with derived metrics

## 📊 Key Visualizations

1. **Regional Accident Distribution** - Horizontal bar chart showing accident counts by region
2. **Trend Analysis** - Time-series of accidents, injuries, and deaths
3. **Road Network Growth** - Area chart of infrastructure expansion
4. **Investment Tracker** - Annual road investment in SAR billions
5. **Safety Scatter Plot** - Accident rate vs fatality rate by region
6. **Heatmap** - Accidents by region and year

## 🛠 Tech Stack

| Component | Technology |
|-----------|------------|
| Dashboard | Streamlit |
| Data Processing | Pandas |
| Visualization | Plotly |
| Data Source | KAPSARC Open Data |
| Deployment | Railway / Render |

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
# Clone the repo
git clone https://github.com/ramdev9/ksa-roads-intelligence.git
cd ksa-roads-intelligence

# Install dependencies
pip install -r requirements.txt

# Download real data (optional - sample data included)
python scripts/download_data.py

# Run the dashboard
streamlit run src/dashboard.py
```

Open http://localhost:8501 in your browser.

## 📁 Project Structure

```
ksa-roads-intelligence/
├── data/
│   ├── raw/                    # Downloaded datasets
│   │   ├── sample_traffic_accidents.csv
│   │   └── sample_road_development.csv
│   └── processed/              # Cleaned data
├── src/
│   ├── data_loader.py          # Data loading utilities
│   └── dashboard.py            # Streamlit app
├── scripts/
│   └── download_data.py        # KAPSARC data downloader
├── notebooks/                  # Exploratory analysis
├── .streamlit/
│   └── config.toml             # Streamlit theme config
├── requirements.txt
└── README.md
```

## 📦 Data Sources

All data from [KAPSARC Open Data Portal](https://datasource.kapsarc.org):

| Dataset | Description | Years |
|---------|-------------|-------|
| Traffic Accidents | Accidents and casualties by region | 2008+ |
| King Fahd Bridge Traffic | Monthly vehicle crossings | 2009-2019 |
| Passenger & Freight Vehicles | Vehicle counts by type | Various |
| Road Development | Paved/rural roads construction | 2010+ |

## 🔮 Future Enhancements

- [ ] Add predictive model for accident forecasting
- [ ] Integrate real-time traffic data (if API available)
- [ ] Add interactive map visualization
- [ ] Include more GASTAT datasets
- [ ] Add Arabic language support

## 📄 License

MIT License

## 👤 Author

**Ram Nimbalker** - AI Product Manager  
[madebyram.com](https://madebyram.com) | [LinkedIn](https://linkedin.com/in/ramnimbalker)

---

*Part of my AI PM portfolio demonstrating Data/BI product skills for Vision 2030 context.*
