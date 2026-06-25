import csv

import numpy as np

from faceiq.detector import FaceDetection
from faceiq.exporter import ResultsExporter
from faceiq.quality import QualityResult


def test_exporter_creates_classified_images_and_csv_report(tmp_path) -> None:
    exporter = ResultsExporter(tmp_path / "FaceIQ_Resultats")
    quality = QualityResult(90, 90, 90, 90, 90, 90)
    exported_face = exporter.export_face(
        source_image=tmp_path / "Photo été.png",
        face_number=1,
        image=np.full((30, 30, 3), 127, dtype=np.uint8),
        detection=FaceDetection(20, 20, 30, 30),
        quality=quality,
    )

    report_path = exporter.write_report([exported_face])

    assert exported_face.classified_path.is_file()
    assert exported_face.all_faces_path.is_file()
    with report_path.open(encoding="utf-8-sig", newline="") as report_file:
        rows = list(csv.DictReader(report_file))
    assert rows[0]["classement"] == "Excellent"
    assert rows[0]["visage_numero"] == "1"
