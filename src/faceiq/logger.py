"""Logging setup for a FaceIQ analysis run."""

from __future__ import annotations

import logging
from pathlib import Path


def configure_logger(output_dir: Path, verbose: bool = False) -> logging.Logger:
    """Configure a console and file logger for the current analysis output."""
    output_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("faceiq")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    logger.propagate = False

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(output_dir / "faceiq.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger
