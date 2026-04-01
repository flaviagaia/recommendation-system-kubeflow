from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile

import pandas as pd


USERS = [
    ("U-1001", "budget"),
    ("U-1002", "family"),
    ("U-1003", "premium"),
    ("U-1004", "tech"),
    ("U-1005", "fitness"),
]

ITEMS = [
    ("I-1001", "smartphone", "tech"),
    ("I-1002", "headphone", "tech"),
    ("I-1003", "blender", "family"),
    ("I-1004", "stroller", "family"),
    ("I-1005", "treadmill", "fitness"),
    ("I-1006", "protein_kit", "fitness"),
    ("I-1007", "luxury_watch", "premium"),
    ("I-1008", "designer_bag", "premium"),
    ("I-1009", "discount_bundle", "budget"),
    ("I-1010", "entry_phone", "budget"),
]

INTERACTIONS = [
    ("U-1001", "I-1009", 5),
    ("U-1001", "I-1010", 4),
    ("U-1001", "I-1003", 2),
    ("U-1002", "I-1003", 5),
    ("U-1002", "I-1004", 5),
    ("U-1002", "I-1009", 3),
    ("U-1003", "I-1007", 5),
    ("U-1003", "I-1008", 4),
    ("U-1003", "I-1001", 3),
    ("U-1004", "I-1001", 5),
    ("U-1004", "I-1002", 5),
    ("U-1004", "I-1010", 3),
    ("U-1005", "I-1005", 5),
    ("U-1005", "I-1006", 5),
    ("U-1005", "I-1002", 2),
]


def ensure_datasets(base_dir: str | Path) -> tuple[Path, Path, Path]:
    base_path = Path(base_dir)
    raw_dir = base_path / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    users_path = raw_dir / "users.csv"
    items_path = raw_dir / "items.csv"
    interactions_path = raw_dir / "interactions.csv"

    frames = [
        (pd.DataFrame(USERS, columns=["user_id", "segment"]), users_path),
        (pd.DataFrame(ITEMS, columns=["item_id", "item_name", "category"]), items_path),
        (pd.DataFrame(INTERACTIONS, columns=["user_id", "item_id", "rating"]), interactions_path),
    ]

    for dataframe, path in frames:
        with NamedTemporaryFile("w", suffix=".csv", delete=False, dir=raw_dir, encoding="utf-8") as tmp_file:
            temp_path = Path(tmp_file.name)
        try:
            dataframe.to_csv(temp_path, index=False)
            temp_path.replace(path)
        finally:
            if temp_path.exists():
                temp_path.unlink()
    return users_path, items_path, interactions_path
