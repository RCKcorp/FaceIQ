import numpy as np

from faceiq.detector import FaceDetection
from faceiq.extractor import expanded_box, extract_face


def test_expanded_box_is_clamped_to_image_edges() -> None:
    detection = FaceDetection(x=5, y=4, width=20, height=30)

    assert expanded_box(detection, (100, 80, 3), margin=0.5) == (0, 0, 35, 49)


def test_extract_face_returns_a_copy_of_the_expanded_region() -> None:
    image = np.zeros((100, 80, 3), dtype=np.uint8)
    image[10:20, 10:20] = 255

    face_crop = extract_face(image, FaceDetection(10, 10, 10, 10), margin=0)

    assert face_crop.image.shape == (10, 10, 3)
    assert face_crop.source_box == (10, 10, 20, 20)
    assert face_crop.image is not image
