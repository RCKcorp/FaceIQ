from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


@dataclass(frozen=True)
class FaceDetection:
    """Bounding box d'un visage détecté."""

    x: int
    y: int
    w: int
    h: int
    confidence: float = 70.0

    @property
    def area(self) -> int:
        return self.w * self.h


def load_default_face_detector() -> cv2.CascadeClassifier:
    """Charge le détecteur frontal OpenCV livré avec opencv-python."""
    cascade_path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(str(cascade_path))

    if detector.empty():
        raise RuntimeError(f"Détecteur visage introuvable : {cascade_path}")

    return detector


def detect_faces(
    frame: np.ndarray,
    detector: cv2.CascadeClassifier | None = None,
    scale_factor: float = 1.1,
    min_neighbors: int = 5,
    min_size: tuple[int, int] = (40, 40),
) -> list[FaceDetection]:
    """Détecte les visages dans une image OpenCV BGR."""
    if detector is None:
        detector = load_default_face_detector()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    boxes = detector.detectMultiScale(
        gray,
        scaleFactor=scale_factor,
        minNeighbors=min_neighbors,
        minSize=min_size,
    )

    faces = [FaceDetection(int(x), int(y), int(w), int(h)) for x, y, w, h in boxes]
    faces.sort(key=lambda face: face.area, reverse=True)
    return faces


def crop_face(frame: np.ndarray, face: FaceDetection, padding_ratio: float = 0.25) -> np.ndarray:
    """Extrait un visage avec une marge autour du cadre détecté."""
    height, width = frame.shape[:2]

    pad_x = int(face.w * padding_ratio)
    pad_y = int(face.h * padding_ratio)

    x1 = max(face.x - pad_x, 0)
    y1 = max(face.y - pad_y, 0)
    x2 = min(face.x + face.w + pad_x, width)
    y2 = min(face.y + face.h + pad_y, height)

    return frame[y1:y2, x1:x2]
