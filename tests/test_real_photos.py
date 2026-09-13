import cv2
import numpy as np
import pytest
from skimage import data

from faceiq.detector import FaceDetector


def _gray_to_bgr(image: np.ndarray) -> np.ndarray:
    if image.dtype != np.uint8:
        image = (np.clip(image, 0, 1) * 255).astype(np.uint8)
    return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)


@pytest.mark.integration
def test_real_face_corpus_detection_rate() -> None:
    """LFW subset: first 100 images contain faces, last 100 do not."""
    detector = FaceDetector()
    samples = data.lfw_subset()
    detected: list[bool] = []
    for sample in samples:
        image = cv2.resize(
            _gray_to_bgr(sample),
            (250, 250),
            interpolation=cv2.INTER_CUBIC,
        )
        detected.append(bool(detector.detect(image)))

    assert sum(detected[:100]) >= 80
    assert sum(detected[100:]) <= 10


@pytest.mark.integration
def test_real_profile_photo_is_detected() -> None:
    detector = FaceDetector()
    image = _gray_to_bgr(data.camera())

    detections = detector.detect(image)

    assert any(result.pose.startswith("Profil") for result in detections)
