from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


ROOT = Path(__file__).resolve().parent
DATABASE_PATH = ROOT / "data" / "edmonton_construction.sqlite"


@st.cache_data
def load_data(database_path: Path) -> dict[str, pd.DataFrame]:
    with sqlite3.connect(database_path) as connection:
        return {
            "permits": pd.read_sql_query("SELECT * FROM permits_clean", connection),
            "monthly": pd.read_sql_query("SELECT * FROM monthly_summary", connection),
            "neighbourhoods": pd.read_sql_query(
                "SELECT * FROM neighbourhood_summary", connection
            ),
            "categories": pd.read_sql_query("SELECT * FROM category_summary", connection),
            "metadata": pd.read_sql_query("SELECT * FROM pipeline_metadata", connection),
        }


def format_currency(value: float) -> str:
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.1f}B"
    if value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:,.0f}"


st.set_page_config(
    page_title="Edmonton Construction Intelligence",
    page_icon="ECI",
    layout="wide",
)

st.title("Edmonton Construction Intelligence")
st.caption(
    "City of Edmonton building permits: EDA, neighbourhood trends, and simple clustering."
)

if not DATABASE_PATH.exists():
    st.error(
        "Database not found. Run `python scripts/run_pipeline.py --limit 50000` first."
    )
    st.stop()

data = load_data(DATABASE_PATH)
permits = data["permits"]
monthly = data["monthly"]
neighbourhoods = data["neighbourhoods"]
categories = data["categories"]
metadata = data["metadata"]

permits["permit_date"] = pd.to_datetime(permits["permit_date"])

with st.sidebar:
    st.header("Filters")
    years = sorted(permits["year"].dropna().astype(int).unique())
    selected_years = st.multiselect("Year", years, default=years[-3:] if len(years) > 3 else years)
    category_options = sorted(permits["job_category"].dropna().unique())
    selected_categories = st.multiselect("Job category", category_options, default=category_options)
    min_value, max_value = st.slider(
        "Construction value",
        min_value=0,
        max_value=int(max(permits["construction_value"].max(), 1)),
        value=(0, int(max(permits["construction_value"].max(), 1))),
        step=10_000,
    )

filtered = permits[
    permits["year"].isin(selected_years)
    & permits["job_category"].isin(selected_categories)
    & permits["construction_value"].between(min_value, max_value)
].copy()

total_value = float(filtered["construction_value"].sum())
permit_count = int(filtered["row_id"].nunique())
units_added = int(filtered["units_added"].sum())
active_neighbourhoods = int(filtered["neighbourhood"].nunique())

kpi_cols = st.columns(4)
kpi_cols[0].metric("Permits", f"{permit_count:,}")
kpi_cols[1].metric("Construction value", format_currency(total_value))
kpi_cols[2].metric("Units added", f"{units_added:,}")
kpi_cols[3].metric("Neighbourhoods", f"{active_neighbourhoods:,}")

tab_overview, tab_neighbourhoods, tab_clusters, tab_data = st.tabs(
    ["Overview", "Neighbourhoods", "Clusters", "Data"]
)

with tab_overview:
    left, right = st.columns(2)
    filtered_monthly = (
        filtered.groupby("permit_month", as_index=False)
        .agg(permit_count=("row_id", "count"), total_construction_value=("construction_value", "sum"))
        .sort_values("permit_month")
    )
    left.plotly_chart(
        px.line(
            filtered_monthly,
            x="permit_month",
            y="permit_count",
            title="Permit Volume Over Time",
            markers=True,
        ),
        use_container_width=True,
    )

    filtered_categories = (
        filtered.groupby("job_category", as_index=False)
        .agg(permit_count=("row_id", "count"), total_construction_value=("construction_value", "sum"))
        .sort_values("permit_count", ascending=False)
        .head(12)
    )
    right.plotly_chart(
        px.bar(
            filtered_categories,
            x="permit_count",
            y="job_category",
            orientation="h",
            title="Top Job Categories by Permit Count",
            color="total_construction_value",
            color_continuous_scale="Blues",
        ).update_layout(yaxis={"categoryorder": "total ascending"}),
        use_container_width=True,
    )

    value_by_category = (
        filtered.groupby("job_category", as_index=False)
        .agg(total_construction_value=("construction_value", "sum"))
        .sort_values("total_construction_value", ascending=False)
        .head(15)
    )
    st.plotly_chart(
        px.treemap(
            value_by_category,
            path=["job_category"],
            values="total_construction_value",
            title="Construction Value by Category",
        ),
        use_container_width=True,
    )

with tab_neighbourhoods:
    top_neighbourhoods = (
        filtered.groupby("neighbourhood", as_index=False)
        .agg(
            permit_count=("row_id", "count"),
            total_construction_value=("construction_value", "sum"),
            median_construction_value=("construction_value", "median"),
            units_added=("units_added", "sum"),
            latitude=("latitude", "mean"),
            longitude=("longitude", "mean"),
        )
        .sort_values("total_construction_value", ascending=False)
    )
    st.plotly_chart(
        px.bar(
            top_neighbourhoods.head(15),
            x="total_construction_value",
            y="neighbourhood",
            orientation="h",
            title="Top Neighbourhoods by Construction Value",
        ).update_layout(yaxis={"categoryorder": "total ascending"}),
        use_container_width=True,
    )

    map_df = top_neighbourhoods.dropna(subset=["latitude", "longitude"])
    if not map_df.empty:
        st.plotly_chart(
            px.scatter_mapbox(
                map_df,
                lat="latitude",
                lon="longitude",
                size="permit_count",
                color="total_construction_value",
                hover_name="neighbourhood",
                hover_data=["permit_count", "units_added"],
                zoom=9,
                height=520,
                title="Neighbourhood Permit Activity Map",
            ).update_layout(mapbox_style="open-street-map", margin={"r": 0, "t": 40, "l": 0, "b": 0}),
            use_container_width=True,
        )

with tab_clusters:
    cluster_metadata = metadata.loc[metadata["metric_group"] == "clustering", "metrics_json"]
    cluster_metrics = json.loads(cluster_metadata.iloc[0]) if not cluster_metadata.empty else {}
    st.write(
        f"Status: **{cluster_metrics.get('status', 'unknown')}** | "
        f"Silhouette score: **{cluster_metrics.get('silhouette_score', 'n/a')}** | "
        f"Clustered neighbourhoods: **{cluster_metrics.get('clustered_neighbourhoods', 'n/a')}**"
    )
    clustered = neighbourhoods.dropna(subset=["cluster"]).copy()
    if clustered.empty:
        st.info("Clustering was skipped because there was not enough usable neighbourhood data.")
    else:
        clustered["cluster"] = clustered["cluster"].astype(int).astype(str)
        left, right = st.columns(2)
        left.plotly_chart(
            px.scatter(
                clustered,
                x="permit_count",
                y="total_construction_value",
                color="cluster",
                size="units_added",
                hover_name="neighbourhood",
                title="Neighbourhood Clusters",
            ),
            use_container_width=True,
        )
        profile = (
            clustered.groupby("cluster", as_index=False)
            .agg(
                neighbourhoods=("neighbourhood", "count"),
                avg_permits=("permit_count", "mean"),
                avg_total_value=("total_construction_value", "mean"),
                avg_units_added=("units_added", "mean"),
            )
            .round(1)
        )
        right.dataframe(profile, use_container_width=True, hide_index=True)
        st.dataframe(
            clustered.sort_values(["cluster", "total_construction_value"], ascending=[True, False]),
            use_container_width=True,
            hide_index=True,
        )

with tab_data:
    st.subheader("Filtered Permits")
    columns = [
        "permit_date",
        "permit_number",
        "job_category",
        "work_type",
        "construction_value",
        "units_added",
        "neighbourhood",
        "address",
    ]
    available_columns = [column for column in columns if column in filtered.columns]
    st.dataframe(
        filtered[available_columns].sort_values("permit_date", ascending=False).head(1000),
        use_container_width=True,
        hide_index=True,
    )
