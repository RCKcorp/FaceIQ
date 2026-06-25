"""Face detection based on OpenCV's bundled frontal-face cascade."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from .config import FaceIQConfig


class DetectorError(RuntimeError):
    """Raised when the OpenCV face detector cannot be initialised."""


@dataclass(frozen=True, slots=True)
class FaceDetection:
    """One face bounding box in source-image pixel coordinates."""

    x: int
    y: int
    width: int
    height: int
    confidence: float = 0.80

    @property
    def box(self) -> tuple[int, int, int, int]:
        return self.x, self.y, self.width, self.height


class FaceDetector:
    """Detect frontal faces without downloading a model or using cloud services."""

    def __init__(self, config: FaceIQConfig, cascade_path: Path | None = None) -> None:
        self.config = config
        model_path = cascade_path or Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
        self._cascade = cv2.CascadeClassifier(str(model_path))
        if self._cascade.empty():
            raise DetectorError(f"Impossible de charger le modèle de détection : {model_path}")

    def detect(self, image: np.ndarray) -> list[FaceDetection]:
        """Detect faces in a BGR image and return their bounding boxes."""
        if image is None or image.size == 0:
            raise ValueError("L'image à analyser est vide.")

        grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        detections = self._detect_with_weights(grayscale)
        if detections is None:
            boxes = self._cascade.detectMultiScale(
                grayscale,
                scaleFactor=self.config.detection_scale_factor,
                minNeighbors=self.config.detection_min_neighbors,
                minSize=(self.config.min_face_width, self.config.min_face_height),
            )
            return [FaceDetection(*map(int, box)) for box in boxes]

        boxes, weights = detections
        return [
            FaceDetection(*map(int, box), confidence=self._normalise_confidence(weight))
            for box, weight in zip(boxes, weights, strict=True)
        ]

    def _detect_with_weights(
        self, grayscale: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray] | None:
        """Use level weights when the installed OpenCV build exposes them."""
        try:
            boxes, _, weights = self._cascade.detectMultiScale3(
                grayscale,
                scaleFactor=self.config.detection_scale_factor,
                minNeighbors=self.config.detection_min_neighbors,
                outputRejectLevels=True,
                minSize=(self.config.min_face_width, self.config.min_face_height),
            )
        except (AttributeError, cv2.error):
            return None

        return boxes, np.asarray(weights).reshape(-1)

    @staticmethod
    def _normalise_confidence(weight: float) -> float:
        """Map OpenCV cascade level weights to a stable 0-1 display value."""
        return max(0.50, min(0.99, 0.50 + max(float(weight), 0.0) / 20.0))
