from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from faceiq.detector import load_default_face_detector
from faceiq.exporter import write_csv_report
from faceiq.image_processor import process_image
from faceiq.media import is_image, is_video, iter_supported_files
from faceiq.video_processor import process_video


def analyze_media(
    input_path: str | Path,
    output_dir: str | Path = "output",
    frame_interval_seconds: float = 1.0,
    min_score: float = 0.0,
    max_faces_per_video: int | None = None,
) -> tuple[list[dict[str, Any]], Path]:
    """Analyse un fichier ou dossier contenant images et vidéos."""
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    faces_dir = output_dir / "faces"
    reports_dir = output_dir / "reports"

    files = iter_supported_files(input_path)
    if not files:
        raise ValueError(f"Aucun fichier image/vidéo supporté trouvé dans : {input_path}")

    detector = load_default_face_detector()
    all_results: list[dict[str, Any]] = []

    for file_path in files:
        print(f"Analyse : {file_path}")

        if is_image(file_path):
            results = process_image(
                image_path=file_path,
                output_faces_dir=faces_dir,
                detector=detector,
                min_score=min_score,
            )
        elif is_video(file_path):
            results = process_video(
                video_path=file_path,
                output_faces_dir=faces_dir,
                frame_interval_seconds=frame_interval_seconds,
                detector=detector,
                min_score=min_score,
                max_faces_per_video=max_faces_per_video,
            )
        else:
            continue

        print(f"  -> {len(results)} visage(s) conservé(s)")
        all_results.extend(results)

    all_results.sort(key=lambda row: float(row["score"]), reverse=True)
    report_path = write_csv_report(all_results, reports_dir / "rapport_faceiq.csv")

    return all_results, report_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="FaceIQ - Détection, extraction et notation de visages depuis photos et vidéos."
    )
    parser.add_argument(
        "input",
        help="Fichier ou dossier à analyser. Exemples : samples, samples/photos, samples/video.mp4",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="output",
        help="Dossier de sortie. Par défaut : output",
    )
    parser.add_argument(
        "--frame-interval",
        type=float,
        default=1.0,
        help="Intervalle vidéo en secondes entre deux frames analysées. Par défaut : 1.0",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=0.0,
        help="Score minimum pour conserver un visage. Par défaut : 0",
    )
    parser.add_argument(
        "--max-faces-per-video",
        type=int,
        default=None,
        help="Nombre maximum de meilleurs visages conservés par vidéo. Par défaut : illimité",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results, report_path = analyze_media(
        input_path=args.input,
        output_dir=args.output,
        frame_interval_seconds=args.frame_interval,
        min_score=args.min_score,
        max_faces_per_video=args.max_faces_per_video,
    )

    print("\nAnalyse terminée.")
    print(f"Visages extraits : {len(results)}")
    print(f"Rapport CSV : {report_path}")


if __name__ == "__main__":
    main()
