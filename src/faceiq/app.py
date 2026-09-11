from __future__ import annotations

import os
import sys
import threading
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Qt, Signal, Slot, QUrl
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtWidgets import QApplication, QCheckBox, QFileDialog, QFrame, QHBoxLayout, QLabel, QMainWindow, QMessageBox, QPushButton, QProgressBar, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from .analyzer import AnalysisCancelled, FaceAnalyzer
from .config import AppConfig
from .logger import configure_logging
from .models import AnalysisSummary, FaceResult


class AnalysisWorker(QObject):
    progress = Signal(int, int, str)
    result = Signal(object)
    finished = Signal(object)
    failed = Signal(str)
    cancelled = Signal()

    def __init__(self, source: Path, recursive: bool) -> None:
        super().__init__()
        self.source = source
        self.recursive = recursive
        self.cancel_event = threading.Event()

    @Slot()
    def run(self) -> None:
        try:
            analyzer = FaceAnalyzer(AppConfig(recursive=self.recursive), logger=configure_logging())
            summary = analyzer.analyze_folder(self.source, recursive=self.recursive, progress=lambda done, total, name: self.progress.emit(done, total, name), on_result=lambda result: self.result.emit(result), cancel_event=self.cancel_event)
            self.finished.emit(summary)
        except AnalysisCancelled:
            self.cancelled.emit()
        except Exception as exc:
            self.failed.emit(str(exc))

    def cancel(self) -> None:
        self.cancel_event.set()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("FaceIQ")
        self.resize(1040, 720)
        self.source_folder: Path | None = None
        self.summary: AnalysisSummary | None = None
        self.thread: QThread | None = None
        self.worker: AnalysisWorker | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(14)
        title = QLabel("FaceIQ")
        title.setObjectName("title")
        subtitle = QLabel("Analyse locale de la qualité des visages dans vos photos")
        subtitle.setObjectName("subtitle")
        root.addWidget(title)
        root.addWidget(subtitle)

        picker = QFrame()
        picker.setObjectName("panel")
        picker_layout = QHBoxLayout(picker)
        self.folder_label = QLabel("Aucun dossier sélectionné")
        self.folder_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        browse = QPushButton("Choisir un dossier")
        browse.clicked.connect(self.choose_folder)
        picker_layout.addWidget(self.folder_label, 1)
        picker_layout.addWidget(browse)
        root.addWidget(picker)

        controls = QHBoxLayout()
        self.recursive = QCheckBox("Inclure les sous-dossiers")
        self.recursive.setChecked(True)
        self.start_button = QPushButton("Analyser")
        self.start_button.setObjectName("primary")
        self.start_button.clicked.connect(self.start_analysis)
        self.cancel_button = QPushButton("Annuler")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_analysis)
        controls.addWidget(self.recursive)
        controls.addStretch(1)
        controls.addWidget(self.cancel_button)
        controls.addWidget(self.start_button)
        root.addLayout(controls)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.status_label = QLabel("Prêt")
        root.addWidget(self.progress)
        root.addWidget(self.status_label)

        stats = QHBoxLayout()
        self.stats_labels: dict[str, QLabel] = {}
        for key, label in (("faces", "Visages"), ("excellent", "Excellent"), ("good", "Bon"), ("medium", "Moyen"), ("bad", "Mauvais")):
            box = QFrame(); box.setObjectName("stat"); layout = QVBoxLayout(box)
            value = QLabel("0"); value.setObjectName("statValue")
            caption = QLabel(label); caption.setObjectName("subtitle")
            layout.addWidget(value); layout.addWidget(caption); self.stats_labels[key] = value; stats.addWidget(box)
        root.addLayout(stats)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Aperçu", "Score", "Classement", "Photo source", "Fichier"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setDefaultSectionSize(70)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnWidth(0, 72); self.table.setColumnWidth(1, 80); self.table.setColumnWidth(2, 100); self.table.setColumnWidth(3, 250)
        self.table.cellDoubleClicked.connect(self.open_result)
        root.addWidget(self.table, 1)

        bottom = QHBoxLayout()
        self.open_results_button = QPushButton("Ouvrir les résultats"); self.open_results_button.setEnabled(False); self.open_results_button.clicked.connect(self.open_results)
        self.open_report_button = QPushButton("Ouvrir le rapport"); self.open_report_button.setEnabled(False); self.open_report_button.clicked.connect(self.open_report)
        bottom.addWidget(self.open_results_button); bottom.addWidget(self.open_report_button); bottom.addStretch(1); root.addLayout(bottom)
        self.setCentralWidget(central)
        self.setStyleSheet(STYLESHEET)

    @Slot()
    def choose_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Choisir le dossier contenant les photos")
        if folder:
            self.source_folder = Path(folder); self.folder_label.setText(folder)

    @Slot()
    def start_analysis(self) -> None:
        if not self.source_folder:
            QMessageBox.information(self, "FaceIQ", "Choisissez d'abord un dossier de photos."); return
        self._reset_results(); self.start_button.setEnabled(False); self.cancel_button.setEnabled(True); self.recursive.setEnabled(False)
        self.status_label.setText("Préparation de l'analyse…")
        self.thread = QThread(self); self.worker = AnalysisWorker(self.source_folder, self.recursive.isChecked()); self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run); self.worker.progress.connect(self.on_progress); self.worker.result.connect(self.on_result); self.worker.finished.connect(self.on_finished); self.worker.failed.connect(self.on_failed); self.worker.cancelled.connect(self.on_cancelled)
        self.worker.finished.connect(self.thread.quit); self.worker.failed.connect(self.thread.quit); self.worker.cancelled.connect(self.thread.quit); self.thread.finished.connect(self.thread.deleteLater); self.thread.start()

    @Slot()
    def cancel_analysis(self) -> None:
        if self.worker:
            self.status_label.setText("Annulation demandée…"); self.cancel_button.setEnabled(False); self.worker.cancel()

    @Slot(int, int, str)
    def on_progress(self, done: int, total: int, name: str) -> None:
        self.progress.setValue(100 if total == 0 else int(done / total * 100)); self.status_label.setText(f"{done}/{total} — {name}")

    @Slot(object)
    def on_result(self, result: FaceResult) -> None:
        row = self.table.rowCount(); self.table.insertRow(row)
        preview = QLabel(); preview.setAlignment(Qt.AlignCenter); pixmap = QPixmap(str(result.crop_path)); preview.setPixmap(pixmap.scaled(58, 58, Qt.KeepAspectRatio, Qt.SmoothTransformation)); self.table.setCellWidget(row, 0, preview)
        self.table.setItem(row, 1, QTableWidgetItem(f"{result.metrics.total:.1f}")); self.table.setItem(row, 2, QTableWidgetItem(result.metrics.category)); self.table.setItem(row, 3, QTableWidgetItem(result.source_path.name))
        file_item = QTableWidgetItem(str(result.crop_path)); file_item.setData(Qt.UserRole, str(result.crop_path)); self.table.setItem(row, 4, file_item); self._update_live_stats(result)

    @Slot(object)
    def on_finished(self, summary: AnalysisSummary) -> None:
        self.summary = summary; self.progress.setValue(100); self.status_label.setText(f"Terminé — {summary.images_processed} images, {summary.faces_detected} visages" + (f", {summary.images_failed} erreur(s)" if summary.images_failed else "")); self.open_results_button.setEnabled(True); self.open_report_button.setEnabled(True); self._set_idle()

    @Slot(str)
    def on_failed(self, message: str) -> None:
        self.status_label.setText("Échec de l'analyse"); QMessageBox.critical(self, "FaceIQ", message); self._set_idle()

    @Slot()
    def on_cancelled(self) -> None:
        self.status_label.setText("Analyse annulée"); self._set_idle()

    def _set_idle(self) -> None:
        self.start_button.setEnabled(True); self.cancel_button.setEnabled(False); self.recursive.setEnabled(True); self.worker = None; self.thread = None

    def _reset_results(self) -> None:
        self.summary = None; self.table.setRowCount(0); self.progress.setValue(0)
        for label in self.stats_labels.values(): label.setText("0")
        self.open_results_button.setEnabled(False); self.open_report_button.setEnabled(False)

    def _update_live_stats(self, result: FaceResult) -> None:
        self._inc("faces"); mapping = {"Excellent": "excellent", "Bon": "good", "Moyen": "medium", "Mauvais": "bad"}; self._inc(mapping[result.metrics.category])

    def _inc(self, key: str) -> None:
        label = self.stats_labels[key]; label.setText(str(int(label.text()) + 1))

    @Slot(int, int)
    def open_result(self, row: int, _column: int) -> None:
        item = self.table.item(row, 4)
        if item: self._open_path(Path(item.data(Qt.UserRole)))

    @Slot()
    def open_results(self) -> None:
        if self.summary: self._open_path(self.summary.output_folder)

    @Slot()
    def open_report(self) -> None:
        if self.summary: self._open_path(self.summary.output_folder / "rapport_analyse.html")

    @staticmethod
    def _open_path(path: Path) -> None:
        if sys.platform == "win32": os.startfile(path)
        else: QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))


STYLESHEET = """
QWidget { background: #0f172a; color: #e2e8f0; font-family: 'Segoe UI'; font-size: 10pt; }
QLabel#title { font-size: 26pt; font-weight: 700; color: white; } QLabel#subtitle { color: #94a3b8; }
QFrame#panel, QFrame#stat { background: #1e293b; border: 1px solid #334155; border-radius: 10px; } QLabel#statValue { font-size: 20pt; font-weight: 700; color: white; }
QPushButton { background: #334155; border: 1px solid #475569; padding: 9px 15px; border-radius: 7px; } QPushButton:hover { background: #475569; } QPushButton:disabled { color: #64748b; background: #1e293b; } QPushButton#primary { background: #2563eb; border-color: #3b82f6; font-weight: 600; } QPushButton#primary:hover { background: #1d4ed8; }
QProgressBar { background: #1e293b; border: 1px solid #334155; border-radius: 6px; text-align: center; height: 18px; } QProgressBar::chunk { background: #2563eb; border-radius: 5px; }
QTableWidget { background: #111827; alternate-background-color: #172033; border: 1px solid #334155; gridline-color: #243244; } QHeaderView::section { background: #1e293b; color: #cbd5e1; padding: 8px; border: 0; border-right: 1px solid #334155; }
"""


def main() -> int:
    app = QApplication(sys.argv); app.setApplicationName("FaceIQ"); window = MainWindow(); window.show(); return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
