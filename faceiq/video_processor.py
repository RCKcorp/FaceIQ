from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2

from faceiq.frame_processor import process_frame


def process_video(
    video_path: str | Path,
    output_faces_dir: str | Path,
    frame_interval_seconds: float = 1.0,
    detector: cv2.CascadeClassifier | None = None,
    min_score: float = 0.0,
    max_faces_per_video: int | None = None,
) -> list[dict[str, Any]]:
    """Analyse une vidéo en échantillonnant une frame toutes les X secondes."""
    video_path = Path(video_path)
    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        raise ValueError(f"Vidéo illisible : {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 25.0

    frame_step = max(1, int(round(fps * frame_interval_seconds)))
    frame_number = 0
    results: list[dict[str, Any]] = []

    while True:
        success, frame = cap.read()
        if not success:
            break

        if frame_number % frame_step == 0:
            timestamp_seconds = frame_number / fps
            frame_results = process_frame(
                frame=frame,
                source_file=video_path,
                source_type="video",
                output_faces_dir=output_faces_dir,
                timestamp_seconds=timestamp_seconds,
                frame_number=frame_number,
                detector=detector,
                min_score=min_score,
            )
            results.extend(frame_results)

        frame_number += 1

    cap.release()

    results.sort(key=lambda row: float(row["score"]), reverse=True)

    if max_faces_per_video is not None and max_faces_per_video > 0:
        results = results[:max_faces_per_video]

    return results
