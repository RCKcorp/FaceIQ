from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class FaceDetection:
    x: int
    y: int
    width: int
    height: int
    confidence: float = 0.75
    eyes: tuple[tuple[int, int, int, int], ...] = ()

    @property
    def area(self) -> int:
        return self.width * self.height


@dataclass(frozen=True)
class QualityMetrics:
    sharpness: float
    brightness: float
    size: float
    framing: float
    orientation: float
    confidence: float
    total: float
    category: str
    raw_laplacian_variance: float = 0.0
    raw_brightness: float = 0.0


@dataclass(frozen=True)
class FaceResult:
    source_path: Path
    face_index: int
    detection: FaceDetection
    metrics: QualityMetrics
    crop_path: Path
    category_path: Path


@dataclass
class AnalysisSummary:
    source_folder: Path
    output_folder: Path
    images_total: int = 0
    images_processed: int = 0
    images_failed: int = 0
    faces_detected: int = 0
    results: list[FaceResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def category_counts(self) -> dict[str, int]:
        counts = {"Excellent": 0, "Bon": 0, "Moyen": 0, "Mauvais": 0}
        for result in self.results:
            counts[result.metrics.category] = counts.get(result.metrics.category, 0) + 1
        return counts
