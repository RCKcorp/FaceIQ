from __future__ import annotations

import math

import cv2
import numpy as np

from .config import AppConfig
from .models import FaceDetection, QualityMetrics


class QualityScorer:
    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or AppConfig()
        self.config.validate()

    def score(self, image_bgr: np.ndarray, crop_bgr: np.ndarray, detection: FaceDetection) -> QualityMetrics:
        sharpness, lap_var = self._sharpness(crop_bgr)
        brightness, raw_brightness = self._brightness(crop_bgr)
        size = self._size(detection)
        framing = self._framing(image_bgr, detection)
        orientation = self._orientation(detection)
        confidence = max(0.0, min(1.0, detection.confidence))

        w = self.config.weights
        total = (
            sharpness * w.sharpness
            + brightness * w.brightness
            + size * w.size
            + framing * w.framing
            + orientation * w.orientation
            + confidence * w.confidence
        )
        total = round(max(0.0, min(100.0, total)), 1)

        return QualityMetrics(
            sharpness=round(sharpness * w.sharpness, 1),
            brightness=round(brightness * w.brightness, 1),
            size=round(size * w.size, 1),
            framing=round(framing * w.framing, 1),
            orientation=round(orientation * w.orientation, 1),
            confidence=round(confidence * w.confidence, 1),
            total=total,
            category=self.config.classify(total),
            raw_laplacian_variance=round(lap_var, 2),
            raw_brightness=round(raw_brightness, 2),
        )

    @staticmethod
    def _sharpness(crop_bgr: np.ndarray) -> tuple[float, float]:
        gray = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2GRAY)
        lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        score = 1.0 - math.exp(-lap_var / 170.0)
        return max(0.0, min(1.0, score)), lap_var

    @staticmethod
    def _brightness(crop_bgr: np.ndarray) -> tuple[float, float]:
        gray = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2GRAY)
        mean = float(np.mean(gray))
        if 85.0 <= mean <= 185.0:
            return 1.0, mean
        if mean < 85.0:
            score = (mean - 25.0) / 60.0
        else:
            score = (245.0 - mean) / 60.0
        return max(0.0, min(1.0, score)), mean

    @staticmethod
    def _size(detection: FaceDetection) -> float:
        side = min(detection.width, detection.height)
        if side <= 40:
            return 0.0
        if side >= 180:
            return 1.0
        return (side - 40.0) / 140.0

    @staticmethod
    def _framing(image_bgr: np.ndarray, detection: FaceDetection) -> float:
        h, w = image_bgr.shape[:2]
        left = detection.x
        top = detection.y
        right = w - (detection.x + detection.width)
        bottom = h - (detection.y + detection.height)
        min_margin = min(left, top, right, bottom)
        reference = max(1.0, min(detection.width, detection.height) * 0.20)
        return max(0.25, min(1.0, min_margin / reference))

    @staticmethod
    def _orientation(detection: FaceDetection) -> float:
        eyes = list(detection.eyes)
        if detection.pose != "Frontal" and len(eyes) < 2:
            return 0.60
        if len(eyes) < 2:
            return 0.55 if len(eyes) == 1 else 0.35
        upper = [e for e in eyes if (e[1] + e[3] / 2) < detection.y + detection.height * 0.65]
        if len(upper) < 2:
            upper = eyes
        upper = sorted(upper, key=lambda e: e[0])[:2]
        e1, e2 = upper
        c1 = (e1[0] + e1[2] / 2, e1[1] + e1[3] / 2)
        c2 = (e2[0] + e2[2] / 2, e2[1] + e2[3] / 2)
        dx = max(1.0, abs(c2[0] - c1[0]))
        dy = abs(c2[1] - c1[1])
        angle_penalty = min(1.0, dy / (dx * 0.45))
        eye_distance = dx / max(1.0, detection.width)
        distance_score = min(1.0, max(0.0, (eye_distance - 0.18) / 0.22))
        return max(0.35, min(1.0, 1.0 - 0.55 * angle_penalty + 0.15 * distance_score))
