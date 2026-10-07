import pandas as pd

from edmonton_construction_intelligence.transform import (
    build_category_summary,
    build_monthly_summary,
    build_neighbourhood_summary,
    clean_permits,
)


def sample_raw_permits() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "row_id": "1",
                "issue_date": "2025-01-03T00:00:00.000",
                "permit_date": "2025-01-03T00:00:00.000",
                "year": "2025",
                "month_number": "1",
                "job_category": "Commercial Final",
                "construction_value": "100000",
                "units_added": "2",
                "neighbourhood": "DOWNTOWN",
                "latitude": "53.54",
                "longitude": "-113.49",
            },
            {
                "row_id": "2",
                "issue_date": "2025-01-15T00:00:00.000",
                "permit_date": "2025-01-15T00:00:00.000",
                "year": "2025",
                "month_number": "1",
                "job_category": "Home Improvement",
                "construction_value": "-50",
                "units_added": None,
                "neighbourhood": "",
                "latitude": "999",
                "longitude": "-999",
            },
            {
                "row_id": "2",
                "issue_date": "2025-01-15T00:00:00.000",
                "permit_date": "2025-01-15T00:00:00.000",
                "year": "2025",
                "month_number": "1",
                "job_category": "Home Improvement",
                "construction_value": "25000",
                "units_added": "1",
                "neighbourhood": "OLIVER",
                "latitude": "53.54",
                "longitude": "-113.51",
            },
        ]
    )


def test_clean_permits_coerces_types_and_removes_duplicates():
    clean, validation = clean_permits(sample_raw_permits())

    assert len(clean) == 2
    assert validation["raw_rows"] == 3
    assert validation["duplicate_or_invalid_rows_removed"] == 1
    assert clean["construction_value"].min() == 0
    assert clean.loc[clean["row_id"] == "2", "neighbourhood"].iloc[0] == "UNSPECIFIED"
    assert clean.loc[clean["row_id"] == "2", "latitude"].isna().iloc[0]


def test_summary_builders_return_expected_kpis():
    clean, _ = clean_permits(sample_raw_permits())

    monthly = build_monthly_summary(clean)
    neighbourhoods = build_neighbourhood_summary(clean)
    categories = build_category_summary(clean)

    assert monthly.loc[0, "permit_count"] == 2
    assert monthly.loc[0, "total_construction_value"] == 100000
    assert set(neighbourhoods["neighbourhood"]) == {"DOWNTOWN", "UNSPECIFIED"}
    assert categories["permit_count"].sum() == 2
