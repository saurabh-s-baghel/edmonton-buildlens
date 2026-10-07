# Edmonton BuildLens

[Open the live dashboard](https://edmonton-buildlens.streamlit.app/)

Edmonton BuildLens is a dashboard for exploring building-permit activity across Edmonton. It brings permit counts, declared construction values, housing units added, and neighbourhood comparisons into one place.

I built this project to work through a complete data workflow: fetching public records, cleaning them, storing analysis tables, and turning the results into an interactive application. The first version is deployed on Streamlit Community Cloud. I am continuing to improve the interface and the analysis.

## What it does today

- Fetches building-permit records from the City of Edmonton's open-data API.
- Parses dates and numeric fields, standardizes missing category labels, removes duplicate record IDs, and checks coordinates against a bounding box around Edmonton.
- Stores cleaned records and monthly, category, and neighbourhood summaries in SQLite.
- Lets users filter permits by year, job category, and declared construction value.
- Shows permit volume over time, value by category, neighbourhood rankings, and housing units added.
- Maps neighbourhood activity using average permit coordinates where coordinates are available.
- Groups neighbourhoods with similar activity using K-Means and displays cluster profiles alongside a silhouette score.
- Includes a table of the filtered permit records.

The dashboard reads a saved database. It does not fetch new records on each visit, and there is no automatic refresh yet.

## Data and current snapshot

Source: [City of Edmonton General Building Permits API](https://data.edmonton.ca/resource/24uj-dj8v.json), accessed through Socrata (dataset ID `24uj-dj8v`). No API key is required by the current pipeline.

The database included in this repository contains:

| Measure | Included snapshot |
| --- | --- |
| Cleaned permit records | 50,000 |
| Permit-date range | September 21, 2023 - October 4, 2026 |
| Records with usable coordinates | 39,700 |
| Neighbourhoods used in clustering | 362 |

The pipeline requests the latest records ordered by permit date, with a default limit of 50,000. This is a snapshot of recent activity, not the complete permit history. The first and last months in the snapshot may be incomplete, so their totals should not be compared directly with full months. Running the pipeline again can change the date range and results above.

## How the pipeline works

```text
City of Edmonton API
        |
        v
Pandas cleaning and validation
        |
        v
Monthly, category, and neighbourhood summaries
        |
        v
Feature scaling and neighbourhood clustering
        |
        v
SQLite database -> Streamlit dashboard with Plotly charts
```

SQLite holds five tables: `permits_clean`, `monthly_summary`, `neighbourhood_summary`, `category_summary`, and `pipeline_metadata`. The metadata table records cleaning counts and clustering results.

## Neighbourhood clustering

K-Means uses five neighbourhood-level features: permit count, total construction value, median construction value, average construction value, and units added. Neighbourhoods need at least five permits to be included. Features are scaled with `StandardScaler` before fitting four clusters, with a fixed random seed for repeatability.

For the included snapshot, the silhouette score is **0.593** across **362 neighbourhoods**. This measures separation between the clusters in the selected feature space; it is not a prediction-accuracy score. Four clusters is an initial choice, not a result of testing several cluster counts.

The clusters are exploratory groups, not rankings or investment recommendations. Large projects and neighbourhood activity levels can strongly influence the grouping. The cluster view uses the full saved snapshot and does not change with the dashboard's sidebar filters.

## Things to keep in mind

- Construction value is the value reported in permit data, not verified spending, revenue, or final project cost.
- Missing or unparseable construction values and units are currently filled with zero; negative values are also clipped to zero. This simplifies aggregation but loses the distinction between missing information and a reported zero.
- Coordinate checks use a bounding box, not Edmonton's exact boundary. Map points represent average permit locations, not official neighbourhood centroids.
- The current validation is basic. It does not fully reconcile dates, year/month fields, or missing record identifiers.
- This uses public City of Edmonton records. It is not connected to a construction company's internal systems.

## Run locally

Use **Python 3.12**, the version used for local verification. From the project folder:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The included SQLite snapshot lets the dashboard run without an API request. To rebuild it with current records:

```bash
python scripts/run_pipeline.py --limit 50000
```

This replaces the database and its summaries. For a smaller development run, use `--limit 5000 --database work/smoke.sqlite` to write a separate database without changing the dashboard snapshot.

Run the transformation tests with:

```bash
PYTHONPATH=src pytest -q
```

The two current tests cover cleaning and aggregation. They do not cover every dashboard interaction or API failure.

## Project layout

```text
app.py                                  Dashboard
data/edmonton_construction.sqlite        Saved data and analysis tables
scripts/run_pipeline.py                 Pipeline entry point
src/edmonton_construction_intelligence/  Ingestion, cleaning, clustering, storage
tests/test_transform.py                 Transformation tests
requirements.txt                        Python dependencies
```

The internal Python package still uses the project's original name, `edmonton_construction_intelligence`.

## Deployment

The application is hosted on Streamlit Community Cloud from this GitHub repository, using `app.py` as the entry point. Dependencies come from `requirements.txt`, and the deployment uses the committed SQLite snapshot. Pushing application changes updates the deployed app; updating the underlying data requires rebuilding and committing the database.

## Next improvements

These are planned improvements, not features in the current version:

- Improve the dashboard layout, chart labels, and empty-result states.
- Make the data period, freshness, and missing-value coverage easier to see in the dashboard.
- Add clearer explanations of the neighbourhood groups and compare different cluster counts and feature choices.
- Strengthen validation and preserve missing values instead of treating them as zero.
- Add pagination for larger API extracts and a repeatable refresh process.
- Expand tests for ingestion failures, clustering edge cases, and dashboard filters.
- Add dashboard screenshots and a short walkthrough to this README.

## Tools

Python, Pandas, NumPy, SQLite, scikit-learn, Plotly, Streamlit, pytest, and Git/GitHub.
