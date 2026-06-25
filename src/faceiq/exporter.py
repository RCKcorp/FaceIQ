"""Export face crops into quality folders and generate the CSV report."""

from __future__ import annotations

import csv
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from .config import QUALITY_CATEGORIES
from .detector import FaceDetection
from .quality import QualityResult


@dataclass(frozen=True, slots=True)
class ExportedFace:
    """A face saved by the exporter, including the paths used in the report."""

    source_image: Path
    face_number: int
    detection: FaceDetection
    quality: QualityResult
    classified_path: Path
    all_faces_path: Path


class ResultsExporter:
    """Manage a deterministic FaceIQ result directory."""

    def __init__(
        self,
        output_dir: Path,
        jpeg_quality: int = 95,
        report_dir: Path | None = None,
        source_dir: Path | None = None,
        event_name: str = "",
    ) -> None:
        self.output_dir = output_dir
        self.jpeg_quality = jpeg_quality
        self.report_dir = report_dir or output_dir
        self.source_dir = source_dir
        self.event_name = event_name
        self.all_faces_dir = output_dir / "Tous_les_visages"
        self._prepare_directories()

    def export_face(
        self,
        source_image: Path,
        face_number: int,
        image: np.ndarray,
        detection: FaceDetection,
        quality: QualityResult,
    ) -> ExportedFace:
        """Save one crop in the master and quality-specific result folders."""
        filename = self._filename(source_image, face_number)
        all_faces_path = self.all_faces_dir / filename
        classified_path = self.output_dir / quality.category / filename
        self._save_jpeg(image, all_faces_path)
        self._save_jpeg(image, classified_path)
        return ExportedFace(
            source_image=source_image,
            face_number=face_number,
            detection=detection,
            quality=quality,
            classified_path=classified_path,
            all_faces_path=all_faces_path,
        )

    def write_report(self, exported_faces: list[ExportedFace]) -> Path:
        """Create an Excel-friendly UTF-8 CSV report for the completed run."""
        self.report_dir.mkdir(parents=True, exist_ok=True)
        report_path = self.report_dir / "rapport_analyse.csv"
        fields = (
            "evenement",
            "photographe",
            "photo_source",
            "photo_source_relative",
            "visage_numero",
            "score_total",
            "classement",
            "score_nettete",
            "score_luminosite",
            "score_taille",
            "taille_visage_px",
            "score_cadrage",
            "score_orientation",
            "score_confiance",
            "fichier_exporte",
            "fichier_tous_les_visages",
        )
        with report_path.open("w", newline="", encoding="utf-8-sig") as report_file:
            writer = csv.DictWriter(report_file, fieldnames=fields)
            writer.writeheader()
            for exported_face in exported_faces:
                writer.writerow(self._report_row(exported_face))
        return report_path

    def _prepare_directories(self) -> None:
        self.all_faces_dir.mkdir(parents=True, exist_ok=True)
        for category in QUALITY_CATEGORIES:
            (self.output_dir / category).mkdir(parents=True, exist_ok=True)

    def _filename(self, source_image: Path, face_number: int) -> str:
        safe_stem = self._safe_name(source_image.stem) or "photo"
        photographer = self._photographer_for(source_image)
        if photographer:
            safe_stem = f"{self._safe_name(photographer)}_{safe_stem}"
        source_hash = hashlib.sha1(str(source_image.resolve()).encode("utf-8")).hexdigest()[:8]
        return f"{safe_stem}_{source_hash}_visage_{face_number:02d}.jpg"

    def _save_jpeg(self, image: np.ndarray, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        Image.fromarray(rgb_image).save(destination, format="JPEG", quality=self.jpeg_quality)

    def _report_row(self, exported_face: ExportedFace) -> dict[str, str | float | int]:
        detection = exported_face.detection
        quality = exported_face.quality
        photographer = self._photographer_for(exported_face.source_image)
        relative_source = self._relative_source(exported_face.source_image)
        return {
            "evenement": self.event_name,
            "photographe": photographer,
            "photo_source": str(exported_face.source_image),
            "photo_source_relative": relative_source,
            "visage_numero": exported_face.face_number,
            "score_total": quality.total,
            "classement": quality.category,
            "score_nettete": quality.sharpness,
            "score_luminosite": quality.brightness,
            "score_taille": quality.size,
            "taille_visage_px": min(detection.width, detection.height),
            "score_cadrage": quality.framing,
            "score_orientation": quality.orientation,
            "score_confiance": quality.confidence,
            "fichier_exporte": str(exported_face.classified_path),
            "fichier_tous_les_visages": str(exported_face.all_faces_path),
        }

    def _relative_source(self, source_image: Path) -> str:
        if self.source_dir is None:
            return source_image.name
        try:
            return str(source_image.resolve().relative_to(self.source_dir.resolve()))
        except ValueError:
            return source_image.name

    def _photographer_for(self, source_image: Path) -> str:
        if self.source_dir is None:
            return ""
        try:
            relative_source = source_image.resolve().relative_to(self.source_dir.resolve())
        except ValueError:
            return ""
        return relative_source.parts[0] if len(relative_source.parts) > 1 else ""

    @staticmethod
    def _safe_name(value: str) -> str:
        return re.sub(r"[^A-Za-z0-9_-]+", "_", value).strip("_")
