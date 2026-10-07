from __future__ import annotations

from typing import Any

import pandas as pd
import requests

from .config import BUILDING_PERMITS_API_URL, PERMIT_COLUMNS


def fetch_building_permits(limit: int = 50_000, offset: int = 0) -> pd.DataFrame:
    """Fetch recent Edmonton building permit records from the Socrata API."""
    params: dict[str, Any] = {
        "$select": ", ".join(PERMIT_COLUMNS),
        "$order": "permit_date DESC",
        "$limit": limit,
        "$offset": offset,
    }
    response = requests.get(BUILDING_PERMITS_API_URL, params=params, timeout=60)
    response.raise_for_status()
    return pd.DataFrame(response.json())
