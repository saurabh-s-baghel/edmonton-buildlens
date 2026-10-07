from __future__ import annotations

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


CLUSTER_FEATURES = [
    "permit_count",
    "total_construction_value",
    "median_construction_value",
    "avg_construction_value",
    "units_added",
]


def cluster_neighbourhoods(
    neighbourhood_summary: pd.DataFrame, n_clusters: int = 4
) -> tuple[pd.DataFrame, dict[str, float | int | str]]:
    """Cluster neighbourhoods with enough activity to support interpretation."""
    required = {"neighbourhood", *CLUSTER_FEATURES}
    missing = required.difference(neighbourhood_summary.columns)
    if missing:
        raise ValueError(f"Missing clustering columns: {sorted(missing)}")

    model_df = neighbourhood_summary.copy()
    model_df = model_df[model_df["permit_count"] >= 5].dropna(subset=CLUSTER_FEATURES)

    if len(model_df) < max(n_clusters * 2, 8):
        empty = neighbourhood_summary.assign(cluster=pd.NA)
        metrics = {
            "status": "skipped",
            "reason": "Not enough neighbourhoods with at least 5 permits.",
            "n_clusters": 0,
            "silhouette_score": 0.0,
            "clustered_neighbourhoods": int(len(model_df)),
        }
        return empty, metrics

    scaler = StandardScaler()
    features = scaler.fit_transform(model_df[CLUSTER_FEATURES])

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=20)
    model_df["cluster"] = kmeans.fit_predict(features)
    score = float(silhouette_score(features, model_df["cluster"]))

    clustered = neighbourhood_summary.merge(
        model_df[["neighbourhood", "cluster"]], on="neighbourhood", how="left"
    )
    metrics = {
        "status": "completed",
        "reason": "Clustered neighbourhoods with at least 5 permits.",
        "n_clusters": n_clusters,
        "silhouette_score": round(score, 3),
        "clustered_neighbourhoods": int(model_df["neighbourhood"].nunique()),
    }
    return clustered, metrics
