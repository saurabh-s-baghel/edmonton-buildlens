from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from edmonton_construction_intelligence.config import DATABASE_PATH
from edmonton_construction_intelligence.ingest import fetch_building_permits
from edmonton_construction_intelligence.model import cluster_neighbourhoods
from edmonton_construction_intelligence.storage import write_tables
from edmonton_construction_intelligence.transform import (
    build_category_summary,
    build_monthly_summary,
    build_neighbourhood_summary,
    clean_permits,
)


def run(limit: int, database_path: Path) -> dict:
    raw = fetch_building_permits(limit=limit)
    clean, validation_metrics = clean_permits(raw)
    monthly_summary = build_monthly_summary(clean)
    neighbourhood_summary = build_neighbourhood_summary(clean)
    category_summary = build_category_summary(clean)
    clustered_neighbourhoods, cluster_metrics = cluster_neighbourhoods(neighbourhood_summary)

    write_tables(
        database_path=database_path,
        permits=clean,
        monthly_summary=monthly_summary,
        neighbourhood_summary=clustered_neighbourhoods,
        category_summary=category_summary,
        cluster_metrics=cluster_metrics,
        validation_metrics=validation_metrics,
    )
    return {
        "database_path": str(database_path),
        "validation": validation_metrics,
        "clustering": cluster_metrics,
        "tables": [
            "permits_clean",
            "monthly_summary",
            "neighbourhood_summary",
            "category_summary",
            "pipeline_metadata",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Edmonton permit analytics database.")
    parser.add_argument("--limit", type=int, default=50_000, help="Number of records to fetch.")
    parser.add_argument(
        "--database",
        type=Path,
        default=DATABASE_PATH,
        help="SQLite database output path.",
    )
    args = parser.parse_args()
    result = run(limit=args.limit, database_path=args.database)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
