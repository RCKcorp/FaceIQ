from __future__ import annotations

import math
from collections.abc import Iterable

import cv2
import numpy as np

from .config import AppConfig
from .models import FaceDetection


class FaceDetector:
    """Offline face detector combining frontal and left/right profile cascades."""

    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or AppConfig()
        self.config.validate()

        cascade_root = cv2.data.haarcascades
        self._frontal = cv2.CascadeClassifier(
            cascade_root + "haarcascade_frontalface_default.xml"
        )
        self._profile = cv2.CascadeClassifier(
            cascade_root + "haarcascade_profileface.xml"
        )
        self._eye = cv2.CascadeClassifier(cascade_root + "haarcascade_eye.xml")
        if self._frontal.empty() or self._profile.empty() or self._eye.empty():
            raise RuntimeError("Impossible de charger les modèles OpenCV embarqués.")

    def detect(self, image_bgr: np.ndarray) -> list[FaceDetection]:
        if image_bgr is None or image_bgr.size == 0:
            return []

        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        min_size = (self.config.min_face_size, self.config.min_face_size)

        candidates: list[FaceDetection] = []
        candidates.extend(
            self._detect_cascade(
                self._frontal,
                gray,
                min_neighbors=self.config.detection_min_neighbors,
                min_size=min_size,
                pose="Frontal",
            )
        )
        candidates.extend(
            self._detect_cascade(
                self._profile,
                gray,
                min_neighbors=self.config.profile_min_neighbors,
                min_size=min_size,
                pose="Profil droit",
            )
        )

        flipped = cv2.flip(gray, 1)
        mirrored_profiles = self._detect_cascade(
            self._profile,
            flipped,
            min_neighbors=self.config.profile_min_neighbors,
            min_size=min_size,
            pose="Profil gauche",
            include_eyes=False,
        )
        image_width = gray.shape[1]
        for detection in mirrored_profiles:
            x, y, width, height = self._mirror_rect(
                (detection.x, detection.y, detection.width, detection.height),
                image_width,
            )
            eyes = self._detect_eyes(gray, x, y, width, height)
            candidates.append(
                FaceDetection(
                    x,
                    y,
                    width,
                    height,
                    detection.confidence,
                    eyes,
                    detection.pose,
                )
            )

        return self._deduplicate(candidates, self.config.deduplication_iou)

    def _detect_cascade(
        self,
        cascade: cv2.CascadeClassifier,
        gray: np.ndarray,
        *,
        min_neighbors: int,
        min_size: tuple[int, int],
        pose: str,
        include_eyes: bool = True,
    ) -> list[FaceDetection]:
        try:
            rects, _, weights = cascade.detectMultiScale3(
                gray,
                scaleFactor=self.config.detection_scale_factor,
                minNeighbors=min_neighbors,
                minSize=min_size,
                outputRejectLevels=True,
            )
            weighted_rects: Iterable[tuple[np.ndarray, object]] = zip(rects, weights)
        except (AttributeError, cv2.error):
            rects = cascade.detectMultiScale(
                gray,
                scaleFactor=self.config.detection_scale_factor,
                minNeighbors=min_neighbors,
                minSize=min_size,
            )
            weighted_rects = ((rect, 2.5 if pose == "Frontal" else 2.0) for rect in rects)

        detections: list[FaceDetection] = []
        for rect, raw_weight in weighted_rects:
            x, y, width, height = (int(value) for value in rect)
            weight = float(np.asarray(raw_weight).reshape(-1)[0])
            confidence = self._normalise_confidence(weight)
            eyes = (
                self._detect_eyes(gray, x, y, width, height)
                if include_eyes
                else ()
            )
            detections.append(
                FaceDetection(x, y, width, height, confidence, eyes, pose)
            )
        return detections

    def _detect_eyes(
        self, gray: np.ndarray, x: int, y: int, width: int, height: int
    ) -> tuple[tuple[int, int, int, int], ...]:
        roi = gray[y : y + height, x : x + width]
        eye_rects = self._eye.detectMultiScale(
            roi,
            scaleFactor=1.10,
            minNeighbors=5,
            minSize=(max(8, width // 10), max(8, height // 10)),
        )
        return tuple(
            (x + int(ex), y + int(ey), int(ew), int(eh))
            for ex, ey, ew, eh in eye_rects[:4]
        )

    @staticmethod
    def _mirror_rect(
        rect: tuple[int, int, int, int], image_width: int
    ) -> tuple[int, int, int, int]:
        x, y, width, height = rect
        return image_width - (x + width), y, width, height

    @classmethod
    def _deduplicate(
        cls, detections: Iterable[FaceDetection], iou_threshold: float
    ) -> list[FaceDetection]:
        ordered = sorted(
            detections,
            key=lambda item: (
                item.confidence,
                item.pose == "Frontal",
                item.area,
            ),
            reverse=True,
        )
        kept: list[FaceDetection] = []
        for candidate in ordered:
            if all(cls._iou(candidate, existing) < iou_threshold for existing in kept):
                kept.append(candidate)
        kept.sort(key=lambda item: item.area, reverse=True)
        return kept

    @staticmethod
    def _iou(first: FaceDetection, second: FaceDetection) -> float:
        left = max(first.x, second.x)
        top = max(first.y, second.y)
        right = min(first.x + first.width, second.x + second.width)
        bottom = min(first.y + first.height, second.y + second.height)
        intersection = max(0, right - left) * max(0, bottom - top)
        if intersection == 0:
            return 0.0
        union = first.area + second.area - intersection
        return intersection / max(1, union)

    @staticmethod
    def _normalise_confidence(weight: float) -> float:
        try:
            value = 1.0 / (1.0 + math.exp(-(weight - 2.0)))
        except OverflowError:
            value = 1.0 if weight > 0 else 0.0
        return float(max(0.35, min(0.99, value)))
