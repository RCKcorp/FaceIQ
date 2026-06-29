from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2
import numpy as np

from faceiq.detector import FaceDetection, crop_face, detect_faces, load_default_face_detector
from faceiq.quality import calculate_face_quality


def _format_timestamp(timestamp_seconds: float | None) -> str:
    if timestamp_seconds is None:
        return ""

    total_seconds = int(timestamp_seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def _safe_stem(path: str | Path) -> str:
    return Path(path).stem.replace(" ", "_")


def process_frame(
    frame: np.ndarray,
    source_file: str | Path,
    source_type: str,
    output_faces_dir: str | Path,
    timestamp_seconds: float | None = None,
    frame_number: int | None = None,
    detector: cv2.CascadeClassifier | None = None,
    min_score: float = 0.0,
) -> list[dict[str, Any]]:
    """Détecte, extrait, note et sauvegarde les visages d'une frame."""
    if detector is None:
        detector = load_default_face_detector()

    output_faces_dir = Path(output_faces_dir)
    output_faces_dir.mkdir(parents=True, exist_ok=True)

    faces = detect_faces(frame, detector=detector)
    results: list[dict[str, Any]] = []

    for face_index, face in enumerate(faces, start=1):
        face_crop = crop_face(frame, face)

        if face_crop.size == 0:
            continue

        quality = calculate_face_quality(face_crop, face, frame.shape)

        if float(quality["score"]) < min_score:
            continue

        source_stem = _safe_stem(source_file)
        timestamp_part = ""
        if frame_number is not None:
            timestamp_part = f"_frame_{frame_number}"

        face_filename = f"{source_stem}{timestamp_part}_face_{face_index:03d}_{quality['score']}.jpg"
        face_path = output_faces_dir / face_filename
        cv2.imwrite(str(face_path), face_crop)

        results.append(
            {
                "source_file": str(source_file),
                "source_type": source_type,
                "timestamp": _format_timestamp(timestamp_seconds),
                "frame_number": "" if frame_number is None else frame_number,
                "face_index": face_index,
                "face_path": str(face_path),
                "score": quality["score"],
                "quality": quality["quality"],
                "sharpness": quality["sharpness"],
                "brightness": quality["brightness"],
                "size": quality["size"],
                "centering": quality["centering"],
                "confidence": quality["confidence"],
                "face_x": face.x,
                "face_y": face.y,
                "face_w": face.w,
                "face_h": face.h,
            }
        )

    return results
