from __future__ import annotations

import cv2
import numpy as np

from .models import FaceDetection


def crop_face(image_bgr: np.ndarray, detection: FaceDetection, margin: float = 0.28) -> np.ndarray:
    h_img, w_img = image_bgr.shape[:2]
    margin_x = int(detection.width * margin)
    margin_y = int(detection.height * margin)

    x1 = max(0, detection.x - margin_x)
    y1 = max(0, detection.y - margin_y)
    x2 = min(w_img, detection.x + detection.width + margin_x)
    y2 = min(h_img, detection.y + detection.height + margin_y)

    if x2 <= x1 or y2 <= y1:
        raise ValueError("Zone de visage invalide après application de la marge.")
    return image_bgr[y1:y2, x1:x2].copy()


def save_jpeg(path, image_bgr: np.ndarray, quality: int = 94) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ok, encoded = cv2.imencode(".jpg", image_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    if not ok:
        raise OSError(f"Impossible d'encoder l'image : {path}")
    path.write_bytes(encoded.tobytes())
