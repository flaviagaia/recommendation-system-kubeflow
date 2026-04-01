from __future__ import annotations

from pathlib import Path


KUBEFLOW_PIPELINE_SPEC = {
    "pipeline_name": "recommendation-system-kubeflow",
    "description": "Kubeflow-style recommendation DAG with ingestion, validation, preparation, training, recommendation, and registration steps.",
    "components": [
        {"name": "ingest_component", "outputs": ["users_path", "items_path", "interactions_path"]},
        {"name": "validate_component", "inputs": ["users_path", "items_path", "interactions_path"], "outputs": ["validation_metrics"]},
        {"name": "prepare_component", "inputs": ["users_path", "items_path", "interactions_path"], "outputs": ["matrix_path"]},
        {"name": "train_component", "inputs": ["matrix_path"], "outputs": ["similarity_artifacts"]},
        {"name": "recommend_component", "inputs": ["similarity_artifacts", "matrix_path"], "outputs": ["recommendations_path"]},
        {"name": "register_component", "inputs": ["validation_metrics", "recommendations_path"], "outputs": ["report_artifact"]},
    ],
}


def write_pipeline_spec(base_dir: str | Path) -> Path:
    import json

    artifacts_dir = Path(base_dir) / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    spec_path = artifacts_dir / "kubeflow_pipeline_spec.json"
    spec_path.write_text(json.dumps(KUBEFLOW_PIPELINE_SPEC, ensure_ascii=False, indent=2), encoding="utf-8")
    return spec_path
