import numpy as np

from faceiq.extractor import crop_face
from faceiq.models import FaceDetection


def test_crop_face_is_clamped_to_image_edges() -> None:
    image = np.zeros((100, 80, 3), dtype=np.uint8)
    detection = FaceDetection(x=5, y=4, width=20, height=30)


    crop = crop_face(image, detection, margin=0.5)

    assert crop.shape == (49, 35, 3)


def test_crop_face_returns_a_copy() -> None:
    image = np.zeros((100, 80, 3), dtype=np.uint8)
    crop = crop_face(image, FaceDetection(10, 10, 10, 10), margin=0)

    crop[:] = 255

    assert crop.shape == (10, 10, 3)
    assert not image[10:20, 10:20].any()
