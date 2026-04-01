from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from src.data_factory import ensure_datasets


def ingest_component(base_dir: str | Path) -> dict:
    users_path, items_path, interactions_path = ensure_datasets(base_dir)
    return {
        "users_path": str(users_path),
        "items_path": str(items_path),
        "interactions_path": str(interactions_path),
    }


def validate_component(paths: dict) -> dict:
    users = pd.read_csv(paths["users_path"])
    items = pd.read_csv(paths["items_path"])
    interactions = pd.read_csv(paths["interactions_path"])
    return {
        "user_count": int(len(users)),
        "item_count": int(len(items)),
        "interaction_count": int(len(interactions)),
        "mean_rating": round(float(interactions["rating"].mean()), 4),
    }


def prepare_component(paths: dict, base_dir: str | Path) -> dict:
    users = pd.read_csv(paths["users_path"])
    items = pd.read_csv(paths["items_path"])
    interactions = pd.read_csv(paths["interactions_path"])

    user_item = interactions.pivot_table(index="user_id", columns="item_id", values="rating", fill_value=0)
    processed_dir = Path(base_dir) / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    matrix_path = processed_dir / "user_item_matrix.csv"
    user_item.to_csv(matrix_path)

    return {
        "matrix_path": str(matrix_path),
        "users": users.to_dict(orient="records"),
        "items": items.to_dict(orient="records"),
    }


def train_component(matrix_path: str | Path) -> dict:
    matrix = pd.read_csv(matrix_path, index_col=0)
    similarity = cosine_similarity(matrix)
    similarity_df = pd.DataFrame(similarity, index=matrix.index, columns=matrix.index)
    return {
        "user_item_matrix": matrix,
        "similarity_df": similarity_df,
    }


def recommend_component(training_artifacts: dict, prepared_artifacts: dict, base_dir: str | Path) -> dict:
    matrix = training_artifacts["user_item_matrix"]
    similarity_df = training_artifacts["similarity_df"]
    items_df = pd.DataFrame(prepared_artifacts["items"])

    recommendations: list[dict[str, str | float]] = []
    for user_id in matrix.index:
        similar_users = similarity_df.loc[user_id].drop(user_id).sort_values(ascending=False)
        weighted_scores = pd.Series(0.0, index=matrix.columns)
        for neighbor_id, sim_score in similar_users.items():
            weighted_scores += matrix.loc[neighbor_id] * sim_score
        consumed_items = matrix.loc[user_id]
        candidate_scores = weighted_scores[consumed_items == 0]
        candidate_scores = candidate_scores[candidate_scores > 0].sort_values(ascending=False)
        top_items = candidate_scores.head(3)
        for item_id, score in top_items.items():
            item_row = items_df[items_df["item_id"] == item_id].iloc[0]
            recommendations.append(
                {
                    "user_id": user_id,
                    "item_id": item_id,
                    "item_name": item_row["item_name"],
                    "category": item_row["category"],
                    "score": round(float(score), 4),
                }
            )

    processed_dir = Path(base_dir) / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    recs_path = processed_dir / "recommendations.csv"
    pd.DataFrame(recommendations).to_csv(recs_path, index=False)
    return {
        "recommendations_path": str(recs_path),
        "top_recommendations": recommendations[:6],
    }


def register_component(validation_metrics: dict, recommendations: dict, base_dir: str | Path) -> dict:
    processed_dir = Path(base_dir) / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    report_path = processed_dir / "kubeflow_recommendation_report.json"
    summary = {
        "runtime_mode": "local_kubeflow_style_pipeline",
        "validation": validation_metrics,
        **recommendations,
        "report_artifact": str(report_path),
    }
    report_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary
