from __future__ import annotations

import logging
from pathlib import Path


def configure_logging(base_dir: Path | None = None) -> logging.Logger:
    folder = base_dir or (Path.home() / "FaceIQ" / "logs")
    folder.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("faceiq")
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    file_handler = logging.FileHandler(folder / "faceiq.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger
