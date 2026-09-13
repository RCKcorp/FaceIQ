from __future__ import annotations

import sys
from pathlib import Path


def resource_path(relative_path: str) -> Path:
    """Return a resource path in source and in a PyInstaller one-file build."""
    bundle_root = getattr(sys, "_MEIPASS", None)
    root = Path(bundle_root) if bundle_root else Path(__file__).resolve().parents[2]
    return root / relative_path
