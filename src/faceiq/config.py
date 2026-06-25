"""Application settings and image-quality thresholds."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


SUPPORTED_IMAGE_SUFFIXES = frozenset({".jpg", ".jpeg", ".png", ".webp"})
QUALITY_CATEGORIES = ("Excellent", "Bon", "Moyen", "Mauvais")


def category_for_score(score: float) -> str:
    """Return the user-facing category for a score out of 100."""
    if score >= 85:
        return "Excellent"
    if score >= 65:
        return "Bon"
    if score >= 45:
        return "Moyen"
    return "Mauvais"


@dataclass(frozen=True, slots=True)
class FaceIQConfig:
    """Settings used by one analysis run."""

    source_dir: Path
    output_dir: Path
    report_dir: Path | None = None
    log_dir: Path | None = None
    event_name: str = ""
    recursive: bool = True
    crop_margin: float = 0.25
    min_face_width: int = 30
    min_face_height: int = 30
    detection_scale_factor: float = 1.1
    detection_min_neighbors: int = 5
    jpeg_quality: int = 95

    def __post_init__(self) -> None:
        if not 0 <= self.crop_margin <= 1:
            raise ValueError("La marge de recadrage doit être comprise entre 0 et 1.")
        if self.min_face_width <= 0 or self.min_face_height <= 0:
            raise ValueError("La taille minimale d'un visage doit être positive.")
        if self.detection_scale_factor <= 1:
            raise ValueError("Le facteur d'échelle de détection doit être supérieur à 1.")
        if self.detection_min_neighbors < 0:
            raise ValueError("Le nombre minimal de voisins ne peut pas être négatif.")
        if not 1 <= self.jpeg_quality <= 100:
            raise ValueError("La qualité JPEG doit être comprise entre 1 et 100.")


def is_supported_image(path: Path) -> bool:
    """Return whether *path* has a supported image extension."""
    return path.suffix.lower() in SUPPORTED_IMAGE_SUFFIXES
