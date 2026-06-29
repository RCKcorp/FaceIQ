from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


REPORT_COLUMNS = [
    "source_file",
    "source_type",
    "timestamp",
    "frame_number",
    "face_index",
    "face_path",
    "score",
    "quality",
    "sharpness",
    "brightness",
    "size",
    "centering",
    "confidence",
    "face_x",
    "face_y",
    "face_w",
    "face_h",
]


def write_csv_report(rows: list[dict[str, Any]], output_path: str | Path) -> Path:
    """Écrit le rapport d'analyse FaceIQ au format CSV."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=REPORT_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    return output_path
