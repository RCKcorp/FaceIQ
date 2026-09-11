from __future__ import annotations

import csv
import html
import shutil
from pathlib import Path

from .models import AnalysisSummary, FaceResult


CSV_FIELDS = ["photo_source", "visage", "score_total", "classement", "netteté", "luminosité", "taille", "cadrage", "orientation", "confiance", "largeur_visage", "hauteur_visage", "variance_laplacien", "luminosité_moyenne", "fichier_visage"]


def ensure_output_structure(output_folder: Path) -> None:
    output_folder.mkdir(parents=True, exist_ok=True)
    (output_folder / "Tous_les_visages").mkdir(exist_ok=True)
    for category in ("Excellent", "Bon", "Moyen", "Mauvais"):
        (output_folder / category).mkdir(exist_ok=True)


def copy_to_category(crop_path: Path, category_folder: Path) -> Path:
    category_folder.mkdir(parents=True, exist_ok=True)
    target = category_folder / crop_path.name
    shutil.copy2(crop_path, target)
    return target


def export_csv(summary: AnalysisSummary) -> Path:
    report = summary.output_folder / "rapport_analyse.csv"
    with report.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, delimiter=";")
        writer.writeheader()
        for result in summary.results:
            writer.writerow(_row(result))
    return report


def export_html(summary: AnalysisSummary) -> Path:
    report = summary.output_folder / "rapport_analyse.html"
    counts = summary.category_counts
    cards = []
    for result in sorted(summary.results, key=lambda r: r.metrics.total, reverse=True):
        rel = result.crop_path.relative_to(summary.output_folder).as_posix()
        cards.append("<article class='card'>" f"<img src='{html.escape(rel)}' alt='Visage'>" f"<strong>{result.metrics.total:.1f}/100 — {html.escape(result.metrics.category)}</strong>" f"<span>{html.escape(result.source_path.name)} · visage {result.face_index}</span>" "</article>")

    document = f"""<!doctype html>
<html lang='fr'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>FaceIQ — Rapport</title><style>
body{{font-family:Segoe UI,Arial,sans-serif;background:#0f172a;color:#e2e8f0;margin:0;padding:32px}}main{{max-width:1200px;margin:auto}}h1{{margin:0 0 8px}}.muted{{color:#94a3b8}}.stats{{display:flex;gap:12px;flex-wrap:wrap;margin:24px 0}}.stat{{background:#1e293b;padding:14px 18px;border-radius:12px}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:16px}}.card{{background:#1e293b;padding:10px;border-radius:14px;display:flex;flex-direction:column;gap:7px}}.card img{{width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:10px;background:#020617}}.card span{{font-size:12px;color:#94a3b8;overflow-wrap:anywhere}}
</style></head><body><main><h1>FaceIQ</h1><p class='muted'>Rapport d'analyse local</p><section class='stats'>
<div class='stat'>Images : <strong>{summary.images_processed}/{summary.images_total}</strong></div><div class='stat'>Visages : <strong>{summary.faces_detected}</strong></div><div class='stat'>Excellent : <strong>{counts.get('Excellent', 0)}</strong></div><div class='stat'>Bon : <strong>{counts.get('Bon', 0)}</strong></div><div class='stat'>Moyen : <strong>{counts.get('Moyen', 0)}</strong></div><div class='stat'>Mauvais : <strong>{counts.get('Mauvais', 0)}</strong></div></section><section class='grid'>{''.join(cards)}</section></main></body></html>"""
    report.write_text(document, encoding="utf-8")
    return report


def _row(result: FaceResult) -> dict[str, object]:
    m = result.metrics
    d = result.detection
    return {"photo_source": str(result.source_path), "visage": result.face_index, "score_total": m.total, "classement": m.category, "netteté": m.sharpness, "luminosité": m.brightness, "taille": m.size, "cadrage": m.framing, "orientation": m.orientation, "confiance": m.confidence, "largeur_visage": d.width, "hauteur_visage": d.height, "variance_laplacien": m.raw_laplacian_variance, "luminosité_moyenne": m.raw_brightness, "fichier_visage": str(result.crop_path)}
