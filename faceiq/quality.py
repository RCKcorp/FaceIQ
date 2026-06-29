from __future__ import annotations

import cv2
import numpy as np

from faceiq.detector import FaceDetection


def _clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, value))


def _quality_label(score: float) -> str:
    if score >= 85:
        return "Excellent"
    if score >= 65:
        return "Bon"
    if score >= 45:
        return "Moyen"
    return "Mauvais"


def score_sharpness(face_crop: np.ndarray) -> float:
    """Note la netteté avec la variance du Laplacien."""
    gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
    laplacian_variance = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    return _clamp(laplacian_variance / 2.0)


def score_brightness(face_crop: np.ndarray) -> float:
    """Note l'exposition : meilleur score autour d'une luminosité moyenne."""
    gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
    mean_brightness = float(gray.mean())
    distance_from_ideal = abs(mean_brightness - 127.5)
    return _clamp(100.0 - (distance_from_ideal / 127.5) * 100.0)


def score_face_size(face: FaceDetection, frame_shape: tuple[int, ...]) -> float:
    """Note la taille du visage dans l'image source."""
    frame_height, frame_width = frame_shape[:2]
    frame_area = frame_width * frame_height

    if frame_area <= 0:
        return 0.0

    face_ratio = face.area / frame_area
    # 2 % de l'image ou plus = taille confortable pour exploitation.
    return _clamp((face_ratio / 0.02) * 100.0)


def score_centering(face: FaceDetection, frame_shape: tuple[int, ...]) -> float:
    """Note le centrage du visage dans l'image source."""
    frame_height, frame_width = frame_shape[:2]
    face_center_x = face.x + face.w / 2
    face_center_y = face.y + face.h / 2

    distance_x = abs(face_center_x - frame_width / 2) / max(frame_width / 2, 1)
    distance_y = abs(face_center_y - frame_height / 2) / max(frame_height / 2, 1)
    average_distance = (distance_x + distance_y) / 2

    return _clamp(100.0 - average_distance * 100.0)


def calculate_face_quality(
    face_crop: np.ndarray,
    face: FaceDetection,
    frame_shape: tuple[int, ...],
) -> dict[str, float | str]:
    """Calcule une note globale exploitable de 0 à 100."""
    sharpness = score_sharpness(face_crop)
    brightness = score_brightness(face_crop)
    size = score_face_size(face, frame_shape)
    centering = score_centering(face, frame_shape)
    confidence = _clamp(face.confidence)

    score = (
        sharpness * 0.35
        + brightness * 0.25
        + size * 0.20
        + centering * 0.10
        + confidence * 0.10
    )
    score = round(_clamp(score), 2)

    return {
        "score": score,
        "quality": _quality_label(score),
        "sharpness": round(sharpness, 2),
        "brightness": round(brightness, 2),
        "size": round(size, 2),
        "centering": round(centering, 2),
        "confidence": round(confidence, 2),
    }
