"""
KSA Roads Intelligence Dashboard
Interactive visualization of Saudi Arabia transportation data.

Run: streamlit run src/dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from data_loader import load_traffic_accidents, load_road_development, get_summary_stats, get_regions

# Page config
st.set_page_config(
    page_title="KSA Roads Intelligence",
    page_icon="🛣️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #0f3460;
    }
    .stMetric > div {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 1rem;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🛣️ KSA Roads Intelligence Dashboard")
st.markdown("*Analyzing Saudi Arabia's Road Infrastructure & Traffic Safety | Vision 2030*")
st.divider()

# Load data
@st.cache_data
def load_all_data():
    accidents = load_traffic_accidents(use_sample=True)
    roads = load_road_development(use_sample=True)
    return accidents, roads

try:
    accidents_df, roads_df = load_all_data()
    data_loaded = True
except FileNotFoundError as e:
    st.error(f"Data not found: {e}")
    st.info("Run `python scripts/download_data.py` to download the datasets first.")
    data_loaded = False

if data_loaded:
    # Sidebar filters
    st.sidebar.header("🔍 Filters")

    years = sorted(accidents_df["year"].unique())
    selected_years = st.sidebar.slider(
        "Year Range",
        min_value=int(min(years)),
        max_value=int(max(years)),
        value=(int(min(years)), int(max(years)))
    )

    regions = get_regions()
    selected_regions = st.sidebar.multiselect(
        "Regions",
        options=regions,
        default=regions[:5]  # Default to top 5
    )

    # Filter data
    filtered_accidents = accidents_df[
        (accidents_df["year"] >= selected_years[0]) &
        (accidents_df["year"] <= selected_years[1]) &
        (accidents_df["region"].isin(selected_regions))
    ]

    # KPI Metrics Row
    st.subheader("📊 Key Metrics (Latest Year)")
    stats = get_summary_stats(accidents_df)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Accidents", f"{stats['total_accidents']:,}", help=f"Year {stats['year']}")
    with col2:
        st.metric("Total Injuries", f"{stats['total_injuries']:,}")
    with col3:
        st.metric("Total Fatalities", f"{stats['total_deaths']:,}")
    with col4:
        st.metric("Avg Fatality Rate", f"{stats['avg_fatality_rate']}%")

    st.divider()

    # Charts Row 1
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🗺️ Accidents by Region")
        region_totals = filtered_accidents.groupby("region")["accidents"].sum().reset_index()
        region_totals = region_totals.sort_values("accidents", ascending=True)

        fig = px.bar(
            region_totals,
            x="accidents",
            y="region",
            orientation="h",
            color="accidents",
            color_continuous_scale="Reds"
        )
        fig.update_layout(
            height=400,
            showlegend=False,
            xaxis_title="Total Accidents",
            yaxis_title=""
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("📈 Accidents Trend Over Time")
        yearly_totals = filtered_accidents.groupby("year").agg({
            "accidents": "sum",
            "deaths": "sum",
            "injuries": "sum"
        }).reset_index()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=yearly_totals["year"],
            y=yearly_totals["accidents"],
            name="Accidents",
            mode="lines+markers",
            line=dict(color="#e74c3c", width=3)
        ))
        fig.add_trace(go.Scatter(
            x=yearly_totals["year"],
            y=yearly_totals["injuries"],
            name="Injuries",
            mode="lines+markers",
            line=dict(color="#f39c12", width=2)
        ))
        fig.add_trace(go.Scatter(
            x=yearly_totals["year"],
            y=yearly_totals["deaths"],
            name="Deaths",
            mode="lines+markers",
            line=dict(color="#2c3e50", width=2)
        ))
        fig.update_layout(
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            xaxis_title="Year",
            yaxis_title="Count"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Charts Row 2 - Road Development
    st.subheader("🏗️ Road Infrastructure Development")

    col1, col2 = st.columns(2)

    with col1:
        # Road network growth
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=roads_df["year"],
            y=roads_df["paved_roads_km"],
            name="Paved Roads",
            fill="tozeroy",
            line=dict(color="#3498db")
        ))
        fig.add_trace(go.Scatter(
            x=roads_df["year"],
            y=roads_df["highways_km"],
            name="Highways",
            fill="tozeroy",
            line=dict(color="#27ae60")
        ))
        fig.update_layout(
            title="Road Network Growth (km)",
            height=350,
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Investment trend
        fig = px.bar(
            roads_df,
            x="year",
            y="investment_sar_billion",
            color="investment_sar_billion",
            color_continuous_scale="Greens"
        )
        fig.update_layout(
            title="Annual Road Investment (SAR Billion)",
            height=350,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Safety Analysis
    st.subheader("⚠️ Safety Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Fatality rate by region
        latest_year = accidents_df["year"].max()
        latest_data = accidents_df[accidents_df["year"] == latest_year]

        fig = px.scatter(
            latest_data,
            x="accidents_per_100k",
            y="fatality_rate",
            size="population",
            color="region",
            hover_name="region",
            title=f"Accident Rate vs Fatality Rate ({latest_year})"
        )
        fig.update_layout(
            height=400,
            xaxis_title="Accidents per 100K Population",
            yaxis_title="Fatality Rate (%)"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Heatmap of accidents by region and year
        pivot_data = filtered_accidents.pivot_table(
            values="accidents",
            index="region",
            columns="year",
            aggfunc="sum"
        )

        fig = px.imshow(
            pivot_data,
            color_continuous_scale="RdYlGn_r",
            title="Accidents Heatmap by Region & Year"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Data Table
    with st.expander("📋 View Raw Data"):
        tab1, tab2 = st.tabs(["Traffic Accidents", "Road Development"])

        with tab1:
            st.dataframe(filtered_accidents, use_container_width=True)

        with tab2:
            st.dataframe(roads_df, use_container_width=True)

    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #888;'>
        <p>📊 Data Source: KAPSARC Saudi Arabia Open Data | Built with Streamlit</p>
        <p>Part of Ram Nimbalker's AI PM Portfolio | <a href="https://madebyram.com">madebyram.com</a></p>
    </div>
    """, unsafe_allow_html=True)
