import cv2
import numpy as np

from faceiq.config import AppConfig
from faceiq.models import FaceDetection
from faceiq.quality import QualityScorer


def test_quality_score_is_bounded():
    image = np.full((300, 300, 3), 128, dtype=np.uint8); cv2.line(image, (50, 50), (250, 250), (255, 255, 255), 3); crop = image[60:240, 60:240]
    detection = FaceDetection(60, 60, 180, 180, 0.9, ((90, 105, 25, 15), (170, 104, 25, 15)))
    metrics = QualityScorer(AppConfig()).score(image, crop, detection); assert 0 <= metrics.total <= 100; assert metrics.category in {"Excellent", "Bon", "Moyen", "Mauvais"}


def test_dark_face_loses_brightness_points():
    scorer = QualityScorer(AppConfig()); detection = FaceDetection(60, 60, 180, 180, 0.9); normal = np.full((300, 300, 3), 130, dtype=np.uint8); dark = np.full((300, 300, 3), 10, dtype=np.uint8)
    normal_metrics = scorer.score(normal, normal[60:240, 60:240], detection); dark_metrics = scorer.score(dark, dark[60:240, 60:240], detection); assert normal_metrics.brightness > dark_metrics.brightness
