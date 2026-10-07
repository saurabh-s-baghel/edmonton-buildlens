from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_DIR / "edmonton_construction.sqlite"

SOCRATA_DOMAIN = "data.edmonton.ca"
BUILDING_PERMITS_DATASET_ID = "24uj-dj8v"
BUILDING_PERMITS_API_URL = (
    f"https://{SOCRATA_DOMAIN}/resource/{BUILDING_PERMITS_DATASET_ID}.json"
)

PERMIT_COLUMNS = [
    "row_id",
    "issue_date",
    "permit_number",
    "permit_date",
    "year",
    "month_number",
    "job_category",
    "job_description",
    "building_type",
    "work_type",
    "construction_value",
    "floor_area",
    "units_added",
    "address",
    "zoning",
    "neighbourhood_numberr",
    "neighbourhood",
    "bia",
    "count",
    "latitude",
    "longitude",
]
