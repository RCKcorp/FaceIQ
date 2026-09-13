from faceiq.detector import FaceDetector
from faceiq.models import FaceDetection


def test_mirror_rect_restores_coordinates() -> None:
    assert FaceDetector._mirror_rect((30, 12, 40, 50), 200) == (130, 12, 40, 50)


def test_deduplicate_keeps_best_overlapping_detection() -> None:
    profile = FaceDetection(20, 20, 100, 100, 0.70, pose="Profil droit")
    frontal = FaceDetection(24, 22, 98, 98, 0.94, pose="Frontal")
    separate = FaceDetection(220, 20, 80, 80, 0.80, pose="Profil gauche")

    kept = FaceDetector._deduplicate([profile, frontal, separate], 0.32)

    assert len(kept) == 2
    assert frontal in kept
    assert profile not in kept
    assert separate in kept


def test_iou_is_zero_for_separate_faces() -> None:
    first = FaceDetection(0, 0, 50, 50)
    second = FaceDetection(100, 100, 50, 50)

    assert FaceDetector._iou(first, second) == 0.0
