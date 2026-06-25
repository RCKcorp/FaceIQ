"""Heuristic, explainable face-quality scoring for FaceIQ V1."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from .config import category_for_score
from .detector import FaceDetection


@dataclass(frozen=True, slots=True)
class QualityResult:
    """The individual quality criteria and their weighted total, all out of 100."""

    sharpness: float
    brightness: float
    size: float
    framing: float
    orientation: float
    confidence: float

    @property
    def total(self) -> float:
        return round(
            self.sharpness * 0.35
            + self.brightness * 0.20
            + self.size * 0.20
            + self.framing * 0.10
            + self.orientation * 0.10
            + self.confidence * 0.05,
            1,
        )

    @property
    def category(self) -> str:
        return category_for_score(self.total)


class FaceQualityScorer:
    """Calculate the V1 quality score using image-only technical signals."""

    def evaluate(
        self,
        face_image: np.ndarray,
        detection: FaceDetection,
        source_shape: tuple[int, ...],
    ) -> QualityResult:
        """Evaluate a cropped BGR face image and its original source position."""
        if face_image is None or face_image.size == 0:
            raise ValueError("Le recadrage de visage est vide.")

        grayscale = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
        sharpness_variance = float(cv2.Laplacian(grayscale, cv2.CV_64F).var())
        brightness_mean = float(grayscale.mean())
        smallest_side = min(detection.width, detection.height)

        return QualityResult(
            sharpness=self._scale(sharpness_variance, lower=15, upper=300),
            brightness=self._brightness_score(brightness_mean),
            size=self._scale(smallest_side, lower=32, upper=200),
            framing=self._framing_score(detection, source_shape),
            orientation=round(self._clamp(detection.confidence) * 100, 1),
            confidence=round(self._clamp(detection.confidence) * 100, 1),
        )

    @staticmethod
    def _scale(value: float, lower: float, upper: float) -> float:
        if value <= lower:
            return 0.0
        if value >= upper:
            return 100.0
        return round((value - lower) / (upper - lower) * 100, 1)

    @staticmethod
    def _brightness_score(mean: float) -> float:
        distance_from_middle_gray = abs(mean - 127.5)
        return round(max(0.0, 100.0 * (1 - distance_from_middle_gray / 127.5)), 1)

    def _framing_score(self, detection: FaceDetection, source_shape: tuple[int, ...]) -> float:
        source_height, source_width = source_shape[:2]
        distances_to_edges = (
            detection.x,
            detection.y,
            source_width - (detection.x + detection.width),
            source_height - (detection.y + detection.height),
        )
        smallest_margin = max(0, min(distances_to_edges))
        relative_margin = smallest_margin / max(1, min(detection.width, detection.height))
        return self._scale(relative_margin, lower=0, upper=0.15)

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, value))
