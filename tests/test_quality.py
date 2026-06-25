import numpy as np

from faceiq.config import category_for_score
from faceiq.detector import FaceDetection
from faceiq.quality import FaceQualityScorer


def test_quality_categories_follow_project_thresholds() -> None:
    assert category_for_score(85) == "Excellent"
    assert category_for_score(65) == "Bon"
    assert category_for_score(45) == "Moyen"
    assert category_for_score(44.9) == "Mauvais"


def test_quality_scorer_rewards_a_sharp_well_framed_face() -> None:
    checkerboard = (np.indices((180, 180)).sum(axis=0) % 2 * 255).astype(np.uint8)
    image = np.dstack([checkerboard, checkerboard, checkerboard])
    detection = FaceDetection(x=50, y=50, width=180, height=180, confidence=0.9)

    result = FaceQualityScorer().evaluate(image, detection, (300, 300, 3))

    assert result.sharpness == 100
    assert result.brightness == 100
    assert result.framing == 100
    assert result.total >= 85
    assert result.category == "Excellent"
