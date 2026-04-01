from __future__ import annotations

from pathlib import Path

from src.components import (
    ingest_component,
    prepare_component,
    recommend_component,
    register_component,
    train_component,
    validate_component,
)


def run_local_pipeline(base_dir: str | Path) -> dict:
    paths = ingest_component(base_dir)
    validation = validate_component(paths)
    prepared = prepare_component(paths, base_dir)
    trained = train_component(prepared["matrix_path"])
    recommendations = recommend_component(trained, prepared, base_dir)
    return register_component(validation, recommendations, base_dir)
