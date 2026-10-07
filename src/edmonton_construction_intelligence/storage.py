from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd


def write_tables(
    database_path: Path,
    permits: pd.DataFrame,
    monthly_summary: pd.DataFrame,
    neighbourhood_summary: pd.DataFrame,
    category_summary: pd.DataFrame,
    cluster_metrics: dict,
    validation_metrics: dict,
) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_path) as connection:
        permits.to_sql("permits_clean", connection, if_exists="replace", index=False)
        monthly_summary.to_sql("monthly_summary", connection, if_exists="replace", index=False)
        neighbourhood_summary.to_sql(
            "neighbourhood_summary", connection, if_exists="replace", index=False
        )
        category_summary.to_sql("category_summary", connection, if_exists="replace", index=False)

        metadata = pd.DataFrame(
            [
                {"metric_group": "clustering", "metrics_json": json.dumps(cluster_metrics)},
                {"metric_group": "validation", "metrics_json": json.dumps(validation_metrics)},
            ]
        )
        metadata.to_sql("pipeline_metadata", connection, if_exists="replace", index=False)


def read_table(database_path: Path, table_name: str) -> pd.DataFrame:
    with sqlite3.connect(database_path) as connection:
        return pd.read_sql_query(f"SELECT * FROM {table_name}", connection)
