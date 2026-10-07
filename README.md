# Edmonton Construction Intelligence

A tonight-ready portfolio MVP for Winter 2027 Data Science / Data Engineering internship applications, especially construction-focused teams such as PCL.

The project ingests real City of Edmonton building permit records, cleans and validates key fields, stores analysis tables in SQLite, and serves an interactive Streamlit dashboard with KPIs, trends, neighbourhood analysis, a map, and a small K-Means clustering component.

## Why this project

The goal is to show practical, interview-explainable data work:

- API ingestion from a real public dataset
- pandas cleaning and validation
- SQLite storage for cleaned and aggregated tables
- exploratory analysis with business-friendly KPIs
- scikit-learn clustering with feature scaling and silhouette score
- Plotly + Streamlit dashboard for stakeholders
- basic tests for transformations

## Data Source

- Dataset: City of Edmonton **General Building Permits**
- Portal: `https://data.edmonton.ca`
- Socrata dataset id: `24uj-dj8v`
- API endpoint: `https://data.edmonton.ca/resource/24uj-dj8v.json`

Key fields used include permit dates, job category, building type, work type, construction value, units added, neighbourhood, zoning, latitude, and longitude.

## Project Structure

```text
.
├── app.py
├── data/
│   └── edmonton_construction.sqlite
├── scripts/
│   └── run_pipeline.py
├── src/
│   └── edmonton_construction_intelligence/
│       ├── config.py
│       ├── ingest.py
│       ├── model.py
│       ├── storage.py
│       └── transform.py
├── tests/
│   └── test_transform.py
└── requirements.txt
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the Data Pipeline

Fetch recent records, clean them, create summary tables, run clustering, and write SQLite output:

```bash
python scripts/run_pipeline.py --limit 50000
```

For a faster smoke test:

```bash
python scripts/run_pipeline.py --limit 5000
```

## Run the Dashboard

```bash
streamlit run app.py
```

## Run Tests

```bash
PYTHONPATH=src pytest
```

## Current MVP Scope

Complete:

- Real open-data ingestion from City of Edmonton Socrata API
- Cleaning and validation of dates, categories, neighbourhoods, values, units, and coordinates
- SQLite tables for cleaned permits, monthly summary, neighbourhood summary, category summary, and metadata
- EDA KPIs for permit volume, construction value, units added, neighbourhoods, category breakdowns, and trends
- K-Means neighbourhood clustering using scaled permit activity/value/unit features
- Silhouette score saved in metadata
- Streamlit dashboard with filters, KPI cards, charts, map, cluster view, and data table
- Basic tests for cleaning and aggregation logic

Deferred:

- Deployment
- Docker
- Scheduled refresh
- Deeper feature engineering
- More robust data quality reporting
