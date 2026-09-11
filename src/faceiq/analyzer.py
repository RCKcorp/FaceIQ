from __future__ import annotations

import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Callable

import cv2
import numpy as np
from PIL import Image, ImageOps

from .config import AppConfig
from .detector import FaceDetector
from .exporter import copy_to_category, ensure_output_structure, export_csv, export_html
from .extractor import crop_face, save_jpeg
from .models import AnalysisSummary, FaceResult
from .quality import QualityScorer

ProgressCallback = Callable[[int, int, str], None]
ResultCallback = Callable[[FaceResult], None]


class AnalysisCancelled(RuntimeError):
    pass


class FaceAnalyzer:
    def __init__(self, config: AppConfig | None = None, detector: FaceDetector | None = None, scorer: QualityScorer | None = None, logger: logging.Logger | None = None) -> None:
        self.config = config or AppConfig()
        self.config.validate()
        self.detector = detector or FaceDetector(self.config)
        self.scorer = scorer or QualityScorer(self.config)
        self.logger = logger or logging.getLogger("faceiq")

    def discover_images(self, folder: Path, recursive: bool | None = None) -> list[Path]:
        recursive = self.config.recursive if recursive is None else recursive
        iterator = folder.rglob("*") if recursive else folder.glob("*")
        return sorted(p for p in iterator if p.is_file() and self.config.is_supported(p))

    def analyze_folder(self, source_folder: Path, output_parent: Path | None = None, recursive: bool | None = None, progress: ProgressCallback | None = None, on_result: ResultCallback | None = None, cancel_event: threading.Event | None = None) -> AnalysisSummary:
        source_folder = Path(source_folder)
        if not source_folder.is_dir():
            raise NotADirectoryError(f"Dossier source introuvable : {source_folder}")
        images = self.discover_images(source_folder, recursive)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        parent = Path(output_parent) if output_parent else source_folder.parent
        output_folder = parent / f"FaceIQ_Resultats_{stamp}"
        ensure_output_structure(output_folder)
        summary = AnalysisSummary(source_folder=source_folder, output_folder=output_folder, images_total=len(images))

        for index, path in enumerate(images, start=1):
            if cancel_event and cancel_event.is_set():
                raise AnalysisCancelled("Analyse annulée par l'utilisateur.")
            if progress:
                progress(index - 1, len(images), path.name)
            try:
                image = self._load_image(path)
                detections = self.detector.detect(image)
                for face_index, detection in enumerate(detections, start=1):
                    crop = crop_face(image, detection, self.config.crop_margin)
                    metrics = self.scorer.score(image, crop, detection)
                    safe_stem = self._safe_stem(path.stem)
                    filename = f"{safe_stem}__face_{face_index:02d}__{metrics.total:05.1f}.jpg"
                    crop_path = output_folder / "Tous_les_visages" / filename
                    save_jpeg(crop_path, crop)
                    category_path = copy_to_category(crop_path, output_folder / metrics.category)
                    result = FaceResult(path, face_index, detection, metrics, crop_path, category_path)
                    summary.results.append(result)
                    summary.faces_detected += 1
                    if on_result:
                        on_result(result)
                summary.images_processed += 1
            except Exception as exc:
                summary.images_failed += 1
                message = f"{path.name}: {exc}"
                summary.errors.append(message)
                self.logger.exception("Erreur pendant l'analyse de %s", path)

        export_csv(summary)
        export_html(summary)
        if progress:
            progress(len(images), len(images), "Terminé")
        return summary

    @staticmethod
    def _safe_stem(stem: str) -> str:
        allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
        cleaned = "".join(c if c in allowed else "_" for c in stem).strip("_")
        return cleaned[:80] or "image"

    @staticmethod
    def _load_image(path: Path) -> np.ndarray:
        with Image.open(path) as image:
            image = ImageOps.exif_transpose(image).convert("RGB")
            array = np.asarray(image)
        return cv2.cvtColor(array, cv2.COLOR_RGB2BGR)
