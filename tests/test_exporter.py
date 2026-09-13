import csv
from pathlib import Path

import numpy as np

from faceiq.exporter import copy_to_category, ensure_output_structure, export_csv, export_html
from faceiq.extractor import save_jpeg
from faceiq.models import AnalysisSummary, FaceDetection, FaceResult, QualityMetrics


def test_exporter_creates_reports_with_pose(tmp_path: Path) -> None:
    output = tmp_path / "FaceIQ_Resultats"
    ensure_output_structure(output)
    crop_path = output / "Tous_les_visages" / "visage.jpg"
    save_jpeg(crop_path, np.full((40, 40, 3), 127, dtype=np.uint8))
    category_path = copy_to_category(crop_path, output / "Bon")
    metrics = QualityMetrics(25, 15, 15, 8, 6, 4, 73, "Bon")
    result = FaceResult(
        tmp_path / "photo.jpg",
        1,
        FaceDetection(10, 10, 40, 40, 0.8, pose="Profil gauche"),
        metrics,
        crop_path,
        category_path,
    )
    summary = AnalysisSummary(tmp_path, output, images_total=1, images_processed=1)
    summary.faces_detected = 1
    summary.results.append(result)

    csv_path = export_csv(summary)
    html_path = export_html(summary)

    with csv_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter=";"))
    assert rows[0]["pose"] == "Profil gauche"
    assert rows[0]["classement"] == "Bon"
    assert "Profil gauche" in html_path.read_text(encoding="utf-8")
    assert category_path.is_file()
