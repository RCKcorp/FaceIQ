"""Face crop creation with a configurable safety margin."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .detector import FaceDetection


@dataclass(frozen=True, slots=True)
class FaceCrop:
    """An exported crop and the clamped source rectangle used to create it."""

    image: np.ndarray
    source_box: tuple[int, int, int, int]


def expanded_box(
    detection: FaceDetection, image_shape: tuple[int, ...], margin: float
) -> tuple[int, int, int, int]:
    """Expand a detection rectangle while keeping it inside the source image."""
    image_height, image_width = image_shape[:2]
    horizontal_margin = round(detection.width * margin)
    vertical_margin = round(detection.height * margin)

    left = max(0, detection.x - horizontal_margin)
    top = max(0, detection.y - vertical_margin)
    right = min(image_width, detection.x + detection.width + horizontal_margin)
    bottom = min(image_height, detection.y + detection.height + vertical_margin)

    if left >= right or top >= bottom:
        raise ValueError("La zone de visage détectée est invalide.")
    return left, top, right, bottom


def extract_face(image: np.ndarray, detection: FaceDetection, margin: float) -> FaceCrop:
    """Return a copy of a face crop with surrounding context."""
    left, top, right, bottom = expanded_box(detection, image.shape, margin)
    return FaceCrop(image=image[top:bottom, left:right].copy(), source_box=(left, top, right, bottom))
