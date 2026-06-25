"""Command-line application entry point for FaceIQ."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import cv2
import numpy as np
from PIL import Image, ImageOps

from .config import FaceIQConfig, is_supported_image
from .detector import FaceDetector
from .exporter import ExportedFace, ResultsExporter
from .extractor import extract_face
from .logger import configure_logger
from .quality import FaceQualityScorer
from .workflow import (
    EventLayout,
    create_event_layout,
    find_event_layout,
    ingest_delivery,
    initialize_workspace,
    write_event_manifest,
)


COMMANDS = {"analyze", "init", "ingest", "process", "run"}


@dataclass(frozen=True, slots=True)
class AnalysisSummary:
    """Counts and locations produced by an analysis run."""

    images_scanned: int
    faces_found: int
    images_failed: int
    output_dir: Path
    report_path: Path


def build_parser() -> argparse.ArgumentParser:
    """Build the FaceIQ command parser."""
    parser = argparse.ArgumentParser(
        prog="faceiq",
        description="Détecte, extrait et organise les visages de livraisons photo.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyse simple d'un dossier de photos."
    )
    _add_analyze_arguments(analyze_parser)

    init_parser = subparsers.add_parser(
        "init", help="Crée la structure de travail FaceIQ."
    )
    init_parser.add_argument(
        "workspace",
        nargs="?",
        type=Path,
        default=Path.cwd() / "FaceIQ_Workspace",
        help="Dossier racine de travail.",
    )

    ingest_parser = subparsers.add_parser(
        "ingest", help="Copie une livraison photographe dans un événement."
    )
    _add_event_arguments(ingest_parser)
    ingest_parser.add_argument("delivery", type=Path, help="Dossier reçu du photographe.")
    ingest_parser.add_argument(
        "--photographer",
        help="Nom du photographe si le dossier ne contient pas déjà des sous-dossiers par photographe.",
    )

    process_parser = subparsers.add_parser(
        "process", help="Extrait les visages d'un événement déjà importé."
    )
    process_parser.add_argument(
        "event",
        help="Nom de l'événement ou chemin complet du dossier événement.",
    )
    process_parser.add_argument(
        "--workspace",
        type=Path,
        default=Path.cwd() / "FaceIQ_Workspace",
        help="Dossier racine de travail.",
    )
    process_parser.add_argument(
        "--margin",
        type=float,
        default=0.25,
        help="Marge autour de chaque visage, entre 0 et 1.",
    )
    process_parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="N'analyse pas les sous-dossiers des photos originales.",
    )
    process_parser.add_argument(
        "--verbose", action="store_true", help="Affiche les détails de traitement."
    )

    run_parser = subparsers.add_parser(
        "run", help="Importe une livraison puis extrait les visages en une commande."
    )
    _add_event_arguments(run_parser)
    run_parser.add_argument("delivery", type=Path, help="Dossier reçu du photographe.")
    run_parser.add_argument(
        "--photographer",
        help="Nom du photographe si le dossier ne contient pas déjà des sous-dossiers par photographe.",
    )
    run_parser.add_argument(
        "--margin",
        type=float,
        default=0.25,
        help="Marge autour de chaque visage, entre 0 et 1.",
    )
    run_parser.add_argument(
        "--verbose", action="store_true", help="Affiche les détails de traitement."
    )
    return parser


def main(arguments: Sequence[str] | None = None) -> int:
    """Parse command-line arguments and run the requested workflow."""
    raw_arguments = list(arguments if arguments is not None else sys.argv[1:])
    if raw_arguments and raw_arguments[0] not in COMMANDS and not raw_arguments[0].startswith("-"):
        raw_arguments = ["analyze", *raw_arguments]

    parser = build_parser()
    args = parser.parse_args(raw_arguments)

    try:
        if args.command == "analyze":
            return _run_analyze_command(args, parser)
        if args.command == "init":
            return _run_init_command(args)
        if args.command == "ingest":
            return _run_ingest_command(args)
        if args.command == "process":
            return _run_process_command(args, parser)
        if args.command == "run":
            return _run_event_command(args, parser)
    except (FileNotFoundError, ValueError, RuntimeError) as error:
        parser.error(str(error))
    return 0


def run_analysis(config: FaceIQConfig, verbose: bool = False) -> AnalysisSummary:
    """Run the full local analysis pipeline using *config*."""
    exporter = ResultsExporter(
        config.output_dir,
        config.jpeg_quality,
        report_dir=config.report_dir,
        source_dir=config.source_dir,
        event_name=config.event_name,
    )
    logger = configure_logger(config.log_dir or config.output_dir, verbose)
    image_paths = collect_images(config.source_dir, config.output_dir, config.recursive)
    detector = FaceDetector(config)
    scorer = FaceQualityScorer()
    exported_faces: list[ExportedFace] = []
    images_failed = 0

    logger.info("%s image(s) à analyser dans %s", len(image_paths), config.source_dir)
    for image_number, image_path in enumerate(image_paths, start=1):
        try:
            source_image = load_image(image_path)
            detections = detector.detect(source_image)
            logger.info(
                "[%s/%s] %s : %s visage(s)",
                image_number,
                len(image_paths),
                image_path.name,
                len(detections),
            )

            for face_number, detection in enumerate(detections, start=1):
                face_crop = extract_face(source_image, detection, config.crop_margin)
                quality = scorer.evaluate(face_crop.image, detection, source_image.shape)
                exported_faces.append(
                    exporter.export_face(
                        source_image=image_path,
                        face_number=face_number,
                        image=face_crop.image,
                        detection=detection,
                        quality=quality,
                    )
                )
        except (OSError, ValueError, cv2.error) as error:
            images_failed += 1
            logger.exception("Impossible de traiter %s : %s", image_path, error)

    report_path = exporter.write_report(exported_faces)
    return AnalysisSummary(
        images_scanned=len(image_paths),
        faces_found=len(exported_faces),
        images_failed=images_failed,
        output_dir=config.output_dir,
        report_path=report_path,
    )


def collect_images(source_dir: Path, output_dir: Path, recursive: bool) -> list[Path]:
    """Find supported images, excluding a result directory nested in the source."""
    candidates = source_dir.rglob("*") if recursive else source_dir.glob("*")
    return sorted(
        path
        for path in candidates
        if path.is_file() and is_supported_image(path) and not _is_within(path, output_dir)
    )


def load_image(path: Path) -> np.ndarray:
    """Load a photo with EXIF orientation applied, including Unicode Windows paths."""
    with Image.open(path) as image:
        rgb_image = ImageOps.exif_transpose(image).convert("RGB")
        return cv2.cvtColor(np.asarray(rgb_image), cv2.COLOR_RGB2BGR)


def _add_analyze_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("source", type=Path, help="Dossier contenant les photos à analyser.")
    parser.add_argument(
        "--output",
        type=Path,
        help="Dossier de résultats (par défaut : FaceIQ_Resultats à côté des photos).",
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="N'analyse pas les sous-dossiers du dossier source.",
    )
    parser.add_argument(
        "--margin",
        type=float,
        default=0.25,
        help="Marge autour de chaque visage, entre 0 et 1.",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Affiche les détails de traitement."
    )


def _add_event_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("event", help="Nom de l'événement.")
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path.cwd() / "FaceIQ_Workspace",
        help="Dossier racine de travail.",
    )
    parser.add_argument(
        "--date",
        help="Date de l'événement au format AAAA-MM-JJ (défaut : aujourd'hui).",
    )


def _run_analyze_command(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    source_dir = args.source.expanduser().resolve()
    output_dir = (args.output or source_dir.parent / "FaceIQ_Resultats").expanduser().resolve()

    if not source_dir.is_dir():
        parser.error(f"Le dossier source est introuvable : {source_dir}")
    if source_dir == output_dir:
        parser.error("Le dossier de résultats doit être différent du dossier source.")

    config = FaceIQConfig(
        source_dir=source_dir,
        output_dir=output_dir,
        recursive=not args.no_recursive,
        crop_margin=args.margin,
    )
    summary = run_analysis(config, verbose=args.verbose)
    _print_analysis_summary(summary)
    return 0


def _run_init_command(args: argparse.Namespace) -> int:
    workspace = initialize_workspace(args.workspace)
    inbox = workspace / "00_A_RECEVOIR"
    print(f"Espace de travail prêt : {workspace}")
    print(f"Déposer les photos ici : {inbox}")
    print(f"Guide source : {inbox / 'A_LIRE_SOURCES.txt'}")
    print(f"Evénements traités : {workspace / '01_EVENEMENTS'}")
    return 0


def _run_ingest_command(args: argparse.Namespace) -> int:
    layout = create_event_layout(args.workspace, args.event, args.date)
    summary = ingest_delivery(layout, args.delivery, args.photographer)
    _print_ingest_summary(summary)
    return 0


def _run_process_command(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    layout = find_event_layout(args.workspace, args.event)
    summary = _process_event(layout, args.margin, not args.no_recursive, args.verbose, parser)
    _print_analysis_summary(summary)
    return 0


def _run_event_command(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    layout = create_event_layout(args.workspace, args.event, args.date)
    ingest_summary = ingest_delivery(layout, args.delivery, args.photographer)
    _print_ingest_summary(ingest_summary)
    summary = _process_event(layout, args.margin, True, args.verbose, parser)
    _print_analysis_summary(summary)
    return 0


def _process_event(
    layout: EventLayout,
    margin: float,
    recursive: bool,
    verbose: bool,
    parser: argparse.ArgumentParser,
) -> AnalysisSummary:
    if not layout.sources_dir.is_dir():
        parser.error(f"Aucune photo originale importée dans : {layout.sources_dir}")

    config = FaceIQConfig(
        source_dir=layout.sources_dir,
        output_dir=layout.faces_dir,
        report_dir=layout.reports_dir,
        log_dir=layout.logs_dir,
        event_name=layout.event_name,
        recursive=recursive,
        crop_margin=margin,
    )
    summary = run_analysis(config, verbose=verbose)
    write_event_manifest(
        layout,
        "processed",
        {
            "images_scanned": summary.images_scanned,
            "faces_found": summary.faces_found,
            "images_failed": summary.images_failed,
            "report_path": str(summary.report_path),
        },
    )
    return summary


def _print_ingest_summary(summary) -> None:
    print(
        "Import terminé : "
        f"{summary.copied} photo(s) copiée(s), "
        f"{summary.skipped_duplicates} doublon(s) ignoré(s), "
        f"{summary.unsupported} fichier(s) non compatible(s)."
    )
    print(f"Evénement : {summary.event_dir}")
    print(f"Inventaire : {summary.inventory_path}")


def _print_analysis_summary(summary: AnalysisSummary) -> None:
    print(
        "Analyse terminée : "
        f"{summary.images_scanned} photo(s), {summary.faces_found} visage(s), "
        f"{summary.images_failed} erreur(s)."
    )
    print(f"Visages : {summary.output_dir}")
    print(f"Rapport CSV : {summary.report_path}")


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True
