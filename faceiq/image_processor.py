from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2

from faceiq.frame_processor import process_frame


def process_image(
    image_path: str | Path,
    output_faces_dir: str | Path,
    detector: cv2.CascadeClassifier | None = None,
    min_score: float = 0.0,
) -> list[dict[str, Any]]:
    """Analyse une image et retourne les visages détectés."""
    image_path = Path(image_path)
    frame = cv2.imread(str(image_path))

    if frame is None:
        raise ValueError(f"Image illisible : {image_path}")

    return process_frame(
        frame=frame,
        source_file=image_path,
        source_type="image",
        output_faces_dir=output_faces_dir,
        detector=detector,
        min_score=min_score,
    )
