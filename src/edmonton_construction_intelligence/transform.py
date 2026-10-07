from __future__ import annotations

import numpy as np
import pandas as pd


REQUIRED_COLUMNS = {
    "row_id",
    "permit_date",
    "year",
    "month_number",
    "job_category",
    "construction_value",
    "units_added",
    "neighbourhood",
}


def clean_permits(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Clean permit records and return simple validation counts."""
    missing = REQUIRED_COLUMNS.difference(raw.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df = raw.copy()
    initial_rows = len(df)

    text_columns = [
        "row_id",
        "permit_number",
        "job_category",
        "job_description",
        "building_type",
        "work_type",
        "address",
        "zoning",
        "neighbourhood_numberr",
        "neighbourhood",
        "bia",
    ]
    for column in text_columns:
        if column in df.columns:
            df[column] = (
                df[column]
                .fillna("Unknown")
                .astype(str)
                .str.strip()
                .replace({"": "Unknown", "nan": "Unknown", "None": "Unknown"})
            )

    for column in ["issue_date", "permit_date"]:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors="coerce").dt.date

    numeric_columns = [
        "year",
        "month_number",
        "construction_value",
        "floor_area",
        "units_added",
        "count",
        "latitude",
        "longitude",
    ]
    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.dropna(subset=["row_id", "permit_date", "year", "month_number"])
    df = df.drop_duplicates(subset=["row_id"])

    for column in ["construction_value", "floor_area", "units_added", "count"]:
        if column in df.columns:
            df[column] = df[column].fillna(0).clip(lower=0)

    df["year"] = df["year"].astype(int)
    df["month_number"] = df["month_number"].astype(int)
    df["permit_month"] = pd.to_datetime(df["permit_date"]).dt.to_period("M").astype(str)
    df["neighbourhood"] = df["neighbourhood"].replace({"Unknown": "UNSPECIFIED"})
    df["job_category"] = df["job_category"].replace({"Unknown": "Unspecified"})

    if {"latitude", "longitude"}.issubset(df.columns):
        valid_lat = df["latitude"].between(53.2, 53.8)
        valid_lon = df["longitude"].between(-114.2, -113.1)
        df.loc[~(valid_lat & valid_lon), ["latitude", "longitude"]] = np.nan

    validation = {
        "raw_rows": initial_rows,
        "clean_rows": len(df),
        "duplicate_or_invalid_rows_removed": initial_rows - len(df),
        "rows_with_coordinates": int(df[["latitude", "longitude"]].dropna().shape[0])
        if {"latitude", "longitude"}.issubset(df.columns)
        else 0,
    }
    return df.reset_index(drop=True), validation


def build_monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["permit_month", "year", "month_number"], as_index=False)
        .agg(
            permit_count=("row_id", "count"),
            total_construction_value=("construction_value", "sum"),
            median_construction_value=("construction_value", "median"),
            units_added=("units_added", "sum"),
        )
        .sort_values("permit_month")
    )


def build_neighbourhood_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("neighbourhood", as_index=False)
        .agg(
            permit_count=("row_id", "count"),
            total_construction_value=("construction_value", "sum"),
            median_construction_value=("construction_value", "median"),
            avg_construction_value=("construction_value", "mean"),
            units_added=("units_added", "sum"),
            avg_latitude=("latitude", "mean"),
            avg_longitude=("longitude", "mean"),
        )
        .sort_values("total_construction_value", ascending=False)
    )
    return summary


def build_category_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("job_category", as_index=False)
        .agg(
            permit_count=("row_id", "count"),
            total_construction_value=("construction_value", "sum"),
            median_construction_value=("construction_value", "median"),
            units_added=("units_added", "sum"),
        )
        .sort_values("permit_count", ascending=False)
    )
