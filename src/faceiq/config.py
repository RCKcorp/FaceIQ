from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ScoreWeights:
    sharpness: int = 35
    brightness: int = 20
    size: int = 20
    framing: int = 10
    orientation: int = 10
    confidence: int = 5

    def total(self) -> int:
        return (
            self.sharpness
            + self.brightness
            + self.size
            + self.framing
            + self.orientation
            + self.confidence
        )


@dataclass(frozen=True)
class AppConfig:
    supported_extensions: tuple[str, ...] = (".jpg", ".jpeg", ".png", ".webp")
    crop_margin: float = 0.28
    min_face_size: int = 42
    detection_scale_factor: float = 1.08
    detection_min_neighbors: int = 5
    profile_min_neighbors: int = 4
    deduplication_iou: float = 0.32
    recursive: bool = True
    weights: ScoreWeights = field(default_factory=ScoreWeights)

    excellent_min: float = 85.0
    good_min: float = 65.0
    medium_min: float = 45.0

    def validate(self) -> None:
        if self.weights.total() != 100:
            raise ValueError("Les poids de notation doivent totaliser 100.")
        if not 0.0 <= self.crop_margin <= 1.5:
            raise ValueError("crop_margin doit être compris entre 0 et 1.5.")
        if self.min_face_size < 20:
            raise ValueError("min_face_size est trop faible.")
        if self.profile_min_neighbors < 3:
            raise ValueError("profile_min_neighbors est trop faible.")
        if not 0.0 < self.deduplication_iou < 1.0:
            raise ValueError("deduplication_iou doit être compris entre 0 et 1.")
        if not (0 <= self.medium_min < self.good_min < self.excellent_min <= 100):
            raise ValueError("Les seuils de classement sont invalides.")

    def classify(self, score: float) -> str:
        if score >= self.excellent_min:
            return "Excellent"
        if score >= self.good_min:
            return "Bon"
        if score >= self.medium_min:
            return "Moyen"
        return "Mauvais"

    def is_supported(self, path: Path) -> bool:
        return path.suffix.lower() in self.supported_extensions
