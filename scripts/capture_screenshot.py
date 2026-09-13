from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

from PIL import Image
from PySide6.QtWidgets import QApplication
from skimage import data

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from faceiq.analyzer import FaceAnalyzer  # noqa: E402
from faceiq.app import MainWindow  # noqa: E402


def main() -> int:
    destination = PROJECT_ROOT / "docs" / "images" / "faceiq-main.png"
    ready_destination = PROJECT_ROOT / "docs" / "images" / "faceiq-ready.png"
    destination.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="faceiq-screenshot-") as temp:
        source = Path(temp) / "photos"
        source.mkdir()
        Image.fromarray(data.astronaut()).save(source / "astronaute.jpg")
        summary = FaceAnalyzer().analyze_folder(source)

        app = QApplication.instance() or QApplication([])
        window = MainWindow()
        window.resize(1200, 820)
        window.show()
        app.processEvents()
        if not window.grab().save(str(ready_destination)):
            raise RuntimeError("Impossible d'enregistrer l'écran d'accueil.")

        window.source_folder = source
        window.folder_label.setText(r"C:\Photos\Evenement")
        for result in summary.results:
            window.on_result(result)
        window.on_finished(summary)
        app.processEvents()
        if not window.grab().save(str(destination)):
            raise RuntimeError("Impossible d'enregistrer la capture d'écran.")
        window.close()

    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
