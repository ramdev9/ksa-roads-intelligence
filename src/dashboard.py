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
from data_loader import (
    load_traffic_accidents, load_road_development, get_summary_stats, get_regions,
    load_king_fahd_bridge_traffic, load_passenger_freight_vehicles,
    load_trade_transport, load_vehicle_crossings_cities,
)
from risk_model import compute_risk_scores, compute_yoy_trend

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

# Load data — prefer real KAPSARC data, fall back to bundled sample data
@st.cache_data
def load_all_data():
    try:
        accidents = load_traffic_accidents(use_sample=False)
        roads = load_road_development(use_sample=False)
        return accidents, roads, "real"
    except FileNotFoundError:
        accidents = load_traffic_accidents(use_sample=True)
        roads = load_road_development(use_sample=True)
        return accidents, roads, "sample"

try:
    accidents_df, roads_df, data_source = load_all_data()
    data_loaded = True
except FileNotFoundError as e:
    st.error(f"Data not found: {e}")
    st.info("Run `python scripts/download_data.py` to download the datasets first.")
    data_loaded = False

if data_loaded:
    if data_source == "real":
        st.caption(
            "📡 Live KAPSARC data — accidents cover 2016–2019, road completions cover 1990–2013 "
            "(KAPSARC's most recent published years; the two series don't overlap in time). "
            "Regional population used for per-100k rates is an approximate reference figure, not from KAPSARC."
        )
    else:
        st.caption("🧪 Using bundled sample data — run `python scripts/download_data.py` for real KAPSARC data.")

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
        # Cumulative roads completed since the dataset's earliest year
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=roads_df["year"],
            y=roads_df["cumulative_paved_km"],
            name="Paved Roads (cumulative)",
            fill="tozeroy",
            line=dict(color="#3498db")
        ))
        fig.add_trace(go.Scatter(
            x=roads_df["year"],
            y=roads_df["cumulative_dirt_km"],
            name="Agricultural Dirt Roads (cumulative)",
            fill="tozeroy",
            line=dict(color="#27ae60")
        ))
        fig.update_layout(
            title="Cumulative Roads Completed (km)",
            height=350,
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Roads completed per year
        fig = px.bar(
            roads_df,
            x="year",
            y="paved_roads_completed_km",
            color="paved_roads_completed_km",
            color_continuous_scale="Greens"
        )
        fig.update_layout(
            title="Paved Roads Completed per Year (km)",
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

    # Risk Scoring & Trend Analysis
    st.subheader("🎯 Regional Risk Scoring")
    st.caption(
        "Not a forecast — the accident data is annual with only "
        f"{accidents_df['year'].nunique()} years per region, too few points for "
        "ARIMA/Prophet-style forecasting. This is a composite score (40% fatality "
        "rate, 30% accidents per 100K, 30% average year-over-year trend) ranking "
        "regions into High/Medium/Low risk terciles, plus the year-over-year trend "
        "each score is partly built from."
    )

    risk_df = compute_risk_scores(accidents_df)
    yoy_df = compute_yoy_trend(accidents_df)

    col1, col2 = st.columns(2)

    with col1:
        risk_colors = {"High": "#e74c3c", "Medium": "#f39c12", "Low": "#27ae60"}
        fig = px.bar(
            risk_df,
            x="risk_score",
            y="region",
            orientation="h",
            color="risk_level",
            color_discrete_map=risk_colors,
            category_orders={"risk_level": ["High", "Medium", "Low"]},
            title=f"Composite Risk Score by Region ({int(accidents_df['year'].max())})"
        )
        fig.update_layout(
            height=450,
            yaxis={"categoryorder": "total ascending"},
            xaxis_title="Risk Score (0-100)",
            yaxis_title=""
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        avg_trend = yoy_df.groupby("region")["yoy_pct"].mean().reset_index()
        avg_trend = avg_trend.sort_values("yoy_pct")

        fig = px.bar(
            avg_trend,
            x="yoy_pct",
            y="region",
            orientation="h",
            color="yoy_pct",
            color_continuous_scale="RdYlGn_r",
            color_continuous_midpoint=0,
            title="Average Year-over-Year Accident Change (%)"
        )
        fig.update_layout(
            height=450,
            xaxis_title="Avg YoY Change (%)",
            yaxis_title=""
        )
        st.plotly_chart(fig, use_container_width=True)

    top_risk = risk_df.iloc[0]
    st.info(
        f"📌 Highest composite risk: **{top_risk['region']}** "
        f"(fatality rate {top_risk['fatality_rate']:.1f}%, "
        f"{top_risk['accidents_per_100k']:.0f} accidents per 100K, "
        f"{top_risk['avg_yoy_pct']:+.1f}% avg YoY trend)."
    )

    with st.expander("📋 View Risk Scoring Data"):
        st.dataframe(risk_df, use_container_width=True)

    st.divider()

    # Other KAPSARC Signals (real data only — these 4 datasets have no sample fallback)
    st.subheader("🌉 Other KAPSARC Signals")

    if data_source != "real":
        st.info(
            "These views need real KAPSARC data — run `python scripts/download_data.py` "
            "and reload to see them. No sample data was built for these 4 datasets."
        )
    else:
        try:
            kf_df = load_king_fahd_bridge_traffic()
            pf_df = load_passenger_freight_vehicles()
            tt_df = load_trade_transport()
            vc_df = load_vehicle_crossings_cities()
            other_data_loaded = True
        except FileNotFoundError as e:
            st.warning(f"Some datasets aren't downloaded yet: {e}")
            other_data_loaded = False

        if other_data_loaded:
            col1, col2 = st.columns(2)

            with col1:
                yearly_kf = kf_df.groupby("year")["value"].sum().reset_index()
                fig = px.line(
                    yearly_kf, x="year", y="value", markers=True,
                    title="King Fahd Causeway Traffic (Saudi-Bahrain), Total Vehicles/Year"
                )
                fig.update_layout(height=380, xaxis_title="Year", yaxis_title="Total Crossings")
                st.plotly_chart(fig, use_container_width=True)
                st.caption("Monthly crossing counts by category (trucks/vehicles, incoming/outgoing), summed per year. 2008–2019.")

            with col2:
                fig = px.bar(
                    vc_df.sort_values("entrance_million_vehicles"),
                    x="entrance_million_vehicles", y="city", orientation="h",
                    color="avg_speed_kph", color_continuous_scale="Teal",
                    title="Vehicle Entrances by City (Millions, Registered)"
                )
                fig.update_layout(height=380, xaxis_title="Entrances (Millions)", yaxis_title="")
                st.plotly_chart(fig, use_container_width=True)
                st.caption("Single snapshot, not a time series. Color = average recorded speed (km/h).")

            col1, col2 = st.columns(2)

            with col1:
                fig = px.bar(
                    pf_df, x="vehicle_type", y="value", color="operation", barmode="group",
                    title="Passenger & Freight Vehicles by Type"
                )
                fig.update_layout(height=380, xaxis_title="", yaxis_title="Vehicle Count")
                st.plotly_chart(fig, use_container_width=True)
                st.caption("Single snapshot, not a time series.")

            with col2:
                top_tt = tt_df.sort_values("value", ascending=False).head(15)
                fig = px.bar(
                    top_tt.sort_values("value"),
                    x="value", y="origin_label", orientation="h",
                    title="Road Transport Cost Intensity — Top 15 (US$/ton-km)"
                )
                fig.update_layout(height=380, xaxis_title="US$ per ton-km", yaxis_title="")
                st.plotly_chart(fig, use_container_width=True)
                st.caption(
                    "⚠️ KAPSARC's trade & transport dataset has no Saudi Arabia-specific records "
                    "(all Saudi Arabia rows are null) — shown here as global context only, across "
                    "298 countries/regions."
                )

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
