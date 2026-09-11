from __future__ import annotations

import math

import cv2
import numpy as np

from .config import AppConfig
from .models import FaceDetection


class FaceDetector:
    """Détecteur de visages 100 % local basé sur les cascades livrées avec OpenCV.

    Le backend est volontairement isolé dans cette classe afin de pouvoir remplacer
    la détection par YuNet plus tard sans modifier le reste de l'application.
    """

    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or AppConfig()
        face_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        eye_path = cv2.data.haarcascades + "haarcascade_eye.xml"
        self._face = cv2.CascadeClassifier(face_path)
        self._eye = cv2.CascadeClassifier(eye_path)
        if self._face.empty() or self._eye.empty():
            raise RuntimeError("Impossible de charger les modèles OpenCV embarqués.")

    def detect(self, image_bgr: np.ndarray) -> list[FaceDetection]:
        if image_bgr is None or image_bgr.size == 0:
            return []

        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        min_size = (self.config.min_face_size, self.config.min_face_size)

        detections: list[FaceDetection] = []
        try:
            rects, _, weights = self._face.detectMultiScale3(
                gray,
                scaleFactor=self.config.detection_scale_factor,
                minNeighbors=self.config.detection_min_neighbors,
                minSize=min_size,
                outputRejectLevels=True,
            )
            weighted_rects = zip(rects, weights)
        except (AttributeError, cv2.error):
            rects = self._face.detectMultiScale(
                gray,
                scaleFactor=self.config.detection_scale_factor,
                minNeighbors=self.config.detection_min_neighbors,
                minSize=min_size,
            )
            weighted_rects = ((rect, 1.0) for rect in rects)

        for rect, raw_weight in weighted_rects:
            x, y, w, h = (int(v) for v in rect)
            weight = float(np.asarray(raw_weight).reshape(-1)[0])
            confidence = self._normalise_confidence(weight)
            roi = gray[y : y + h, x : x + w]
            eye_rects = self._eye.detectMultiScale(
                roi,
                scaleFactor=1.10,
                minNeighbors=5,
                minSize=(max(8, w // 10), max(8, h // 10)),
            )
            eyes = tuple(
                (x + int(ex), y + int(ey), int(ew), int(eh))
                for ex, ey, ew, eh in eye_rects[:4]
            )
            detections.append(FaceDetection(x, y, w, h, confidence, eyes))

        detections.sort(key=lambda d: d.area, reverse=True)
        return detections

    @staticmethod
    def _normalise_confidence(weight: float) -> float:
        try:
            value = 1.0 / (1.0 + math.exp(-(weight - 2.0)))
        except OverflowError:
            value = 1.0 if weight > 0 else 0.0
        return float(max(0.35, min(0.99, value)))
