"""Professional event workflow for photographer photo deliveries."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import unicodedata
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from .config import is_supported_image


WORKSPACE_INBOX = "00_A_RECEVOIR"
WORKSPACE_EVENTS = "01_EVENEMENTS"
WORKSPACE_ARCHIVES = "02_ARCHIVES"
WORKSPACE_SOURCE_GUIDE = "A_LIRE_SOURCES.txt"
EVENT_SOURCES = "01_Photos_originales"
EVENT_FACES = "02_Visages_extraits"
EVENT_REPORTS = "03_Rapports"
EVENT_LOGS = "04_Logs"


@dataclass(frozen=True, slots=True)
class EventLayout:
    """Concrete folders used by one event."""

    workspace: Path
    event_dir: Path
    event_name: str
    event_date: str
    sources_dir: Path
    faces_dir: Path
    reports_dir: Path
    logs_dir: Path


@dataclass(frozen=True, slots=True)
class DeliveryBatch:
    """One photographer delivery folder."""

    photographer: str
    source_dir: Path
    recursive: bool = True


@dataclass(frozen=True, slots=True)
class IngestRecord:
    """One copied or skipped source image."""

    event_name: str
    photographer: str
    original_path: Path
    stored_path: Path
    sha256: str
    size_bytes: int
    status: str


@dataclass(frozen=True, slots=True)
class IngestSummary:
    """Counts produced by a delivery import."""

    event_dir: Path
    batches: int
    copied: int
    skipped_duplicates: int
    unsupported: int
    inventory_path: Path


def initialize_workspace(workspace: Path) -> Path:
    """Create the top-level folders used by the FaceIQ event workflow."""
    workspace = workspace.expanduser().resolve()
    for folder in (WORKSPACE_INBOX, WORKSPACE_EVENTS, WORKSPACE_ARCHIVES):
        (workspace / folder).mkdir(parents=True, exist_ok=True)
    _write_source_guide(workspace / WORKSPACE_INBOX)
    return workspace


def create_event_layout(
    workspace: Path, event_name: str, event_date: str | None = None
) -> EventLayout:
    """Return the deterministic event folder layout, creating directories."""
    workspace = initialize_workspace(workspace)
    event_date = _normalise_date(event_date)
    event_dir = workspace / WORKSPACE_EVENTS / f"{event_date}_{slugify(event_name)}"
    layout = EventLayout(
        workspace=workspace,
        event_dir=event_dir,
        event_name=event_name,
        event_date=event_date,
        sources_dir=event_dir / EVENT_SOURCES,
        faces_dir=event_dir / EVENT_FACES,
        reports_dir=event_dir / EVENT_REPORTS,
        logs_dir=event_dir / EVENT_LOGS,
    )
    ensure_event_layout(layout)
    write_event_manifest(layout, "created", {})
    return layout


def layout_from_event_dir(event_dir: Path) -> EventLayout:
    """Build an event layout from an existing event directory."""
    event_dir = event_dir.expanduser().resolve()
    manifest = _read_manifest(event_dir / EVENT_REPORTS / "manifest_event.json")
    event_name = str(manifest.get("event_name") or _event_name_from_folder(event_dir.name))
    event_date = str(manifest.get("event_date") or _event_date_from_folder(event_dir.name))
    workspace = event_dir.parent.parent if event_dir.parent.name == WORKSPACE_EVENTS else event_dir.parent
    layout = EventLayout(
        workspace=workspace,
        event_dir=event_dir,
        event_name=event_name,
        event_date=event_date,
        sources_dir=event_dir / EVENT_SOURCES,
        faces_dir=event_dir / EVENT_FACES,
        reports_dir=event_dir / EVENT_REPORTS,
        logs_dir=event_dir / EVENT_LOGS,
    )
    ensure_event_layout(layout)
    return layout


def find_event_layout(workspace: Path, event: str) -> EventLayout:
    """Resolve an event name or event directory to an EventLayout."""
    candidate = Path(event).expanduser()
    if candidate.is_dir():
        return layout_from_event_dir(candidate)

    workspace = initialize_workspace(workspace)
    events_dir = workspace / WORKSPACE_EVENTS
    exact = events_dir / event
    if exact.is_dir():
        return layout_from_event_dir(exact)

    event_slug = slugify(event)
    matches = sorted(
        path for path in events_dir.iterdir() if path.is_dir() and path.name.endswith(f"_{event_slug}")
    )
    if not matches:
        raise FileNotFoundError(
            f"Evénement introuvable : {event}. Utilise le chemin du dossier événement ou lance d'abord ingest/run."
        )
    if len(matches) > 1:
        choices = ", ".join(str(path) for path in matches)
        raise ValueError(f"Plusieurs événements correspondent à {event} : {choices}")
    return layout_from_event_dir(matches[0])


def ensure_event_layout(layout: EventLayout) -> None:
    """Create all folders for an event."""
    for folder in (
        layout.event_dir,
        layout.sources_dir,
        layout.faces_dir,
        layout.reports_dir,
        layout.logs_dir,
    ):
        folder.mkdir(parents=True, exist_ok=True)


def ingest_delivery(
    layout: EventLayout,
    delivery_dir: Path,
    photographer: str | None = None,
) -> IngestSummary:
    """Copy a photographer delivery into the event sources with duplicate detection."""
    delivery_dir = delivery_dir.expanduser().resolve()
    if not delivery_dir.is_dir():
        raise FileNotFoundError(f"Dossier de livraison introuvable : {delivery_dir}")

    ensure_event_layout(layout)
    batches = discover_batches(delivery_dir, photographer)
    known_hashes = _load_known_hashes(_inventory_path(layout))
    records: list[IngestRecord] = []
    unsupported = 0

    for batch in batches:
        photographer_name = safe_folder_name(batch.photographer)
        target_root = layout.sources_dir / photographer_name
        images = list(_iter_images(batch.source_dir, batch.recursive))
        unsupported += _count_unsupported_files(batch.source_dir, batch.recursive)

        for image_path in images:
            image_hash = _sha256(image_path)
            if image_hash in known_hashes:
                records.append(
                    IngestRecord(
                        event_name=layout.event_name,
                        photographer=photographer_name,
                        original_path=image_path,
                        stored_path=known_hashes[image_hash],
                        sha256=image_hash,
                        size_bytes=image_path.stat().st_size,
                        status="skipped_duplicate",
                    )
                )
                continue

            relative_path = image_path.relative_to(batch.source_dir) if batch.recursive else Path(image_path.name)
            destination = _unique_destination(target_root / relative_path, image_hash)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(image_path, destination)
            known_hashes[image_hash] = destination
            records.append(
                IngestRecord(
                    event_name=layout.event_name,
                    photographer=photographer_name,
                    original_path=image_path,
                    stored_path=destination,
                    sha256=image_hash,
                    size_bytes=image_path.stat().st_size,
                    status="copied",
                )
            )

    inventory_path = _append_inventory(layout, records)
    copied = sum(1 for record in records if record.status == "copied")
    skipped = sum(1 for record in records if record.status == "skipped_duplicate")
    write_event_manifest(
        layout,
        "ingested",
        {
            "last_delivery": str(delivery_dir),
            "batches": len(batches),
            "copied": copied,
            "skipped_duplicates": skipped,
            "unsupported": unsupported,
            "inventory_path": str(inventory_path),
        },
    )
    return IngestSummary(
        event_dir=layout.event_dir,
        batches=len(batches),
        copied=copied,
        skipped_duplicates=skipped,
        unsupported=unsupported,
        inventory_path=inventory_path,
    )


def discover_batches(delivery_dir: Path, photographer: str | None = None) -> list[DeliveryBatch]:
    """Discover photographer folders from one delivery directory."""
    delivery_dir = delivery_dir.expanduser().resolve()
    if photographer:
        return [DeliveryBatch(photographer=photographer, source_dir=delivery_dir)]

    direct_dirs = [
        path for path in sorted(delivery_dir.iterdir()) if path.is_dir() and any(_iter_images(path, True))
    ]
    if direct_dirs:
        batches = [DeliveryBatch(photographer=path.name, source_dir=path) for path in direct_dirs]
        direct_images = [path for path in sorted(delivery_dir.iterdir()) if path.is_file() and is_supported_image(path)]
        if direct_images:
            batches.append(
                DeliveryBatch(photographer=delivery_dir.name, source_dir=delivery_dir, recursive=False)
            )
        return batches

    if any(_iter_images(delivery_dir, True)):
        return [DeliveryBatch(photographer=delivery_dir.name, source_dir=delivery_dir)]

    raise FileNotFoundError(f"Aucune image compatible trouvée dans : {delivery_dir}")


def write_event_manifest(layout: EventLayout, status: str, updates: dict[str, object]) -> Path:
    """Write or update the event manifest JSON."""
    ensure_event_layout(layout)
    manifest_path = layout.reports_dir / "manifest_event.json"
    manifest = _read_manifest(manifest_path)
    now = datetime.now().isoformat(timespec="seconds")
    manifest.setdefault("created_at", now)
    manifest.update(
        {
            "event_name": layout.event_name,
            "event_date": layout.event_date,
            "event_dir": str(layout.event_dir),
            "sources_dir": str(layout.sources_dir),
            "faces_dir": str(layout.faces_dir),
            "reports_dir": str(layout.reports_dir),
            "logs_dir": str(layout.logs_dir),
            "status": status,
            "updated_at": now,
        }
    )
    manifest.update(updates)
    with manifest_path.open("w", encoding="utf-8") as manifest_file:
        json.dump(manifest, manifest_file, ensure_ascii=False, indent=2)
    return manifest_path


def slugify(value: str) -> str:
    """Return a stable ASCII folder slug."""
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^A-Za-z0-9]+", "_", normalized).strip("_").lower()
    return slug or "evenement"


def safe_folder_name(value: str) -> str:
    """Return a safe folder name while keeping photographer labels readable."""
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    safe_name = re.sub(r"[^A-Za-z0-9]+", "_", normalized).strip("_")
    return safe_name or "photographe"


def _iter_images(folder: Path, recursive: bool) -> list[Path]:
    candidates = folder.rglob("*") if recursive else folder.glob("*")
    return sorted(path for path in candidates if path.is_file() and is_supported_image(path))


def _count_unsupported_files(folder: Path, recursive: bool) -> int:
    candidates = folder.rglob("*") if recursive else folder.glob("*")
    return sum(1 for path in candidates if path.is_file() and not is_supported_image(path))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as image_file:
        for chunk in iter(lambda: image_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _unique_destination(destination: Path, image_hash: str) -> Path:
    if not destination.exists():
        return destination
    return destination.with_name(f"{destination.stem}_{image_hash[:8]}{destination.suffix.lower()}")


def _inventory_path(layout: EventLayout) -> Path:
    return layout.reports_dir / "inventaire_photos.csv"


def _append_inventory(layout: EventLayout, records: list[IngestRecord]) -> Path:
    inventory_path = _inventory_path(layout)
    inventory_path.parent.mkdir(parents=True, exist_ok=True)
    fields = (
        "date_import",
        "evenement",
        "photographe",
        "statut",
        "sha256",
        "taille_octets",
        "photo_originale",
        "photo_stockee",
    )
    file_exists = inventory_path.exists()
    with inventory_path.open("a", newline="", encoding="utf-8-sig") as inventory_file:
        writer = csv.DictWriter(inventory_file, fieldnames=fields)
        if not file_exists:
            writer.writeheader()
        imported_at = datetime.now().isoformat(timespec="seconds")
        for record in records:
            writer.writerow(
                {
                    "date_import": imported_at,
                    "evenement": record.event_name,
                    "photographe": record.photographer,
                    "statut": record.status,
                    "sha256": record.sha256,
                    "taille_octets": record.size_bytes,
                    "photo_originale": str(record.original_path),
                    "photo_stockee": str(record.stored_path),
                }
            )
    return inventory_path


def _load_known_hashes(inventory_path: Path) -> dict[str, Path]:
    if not inventory_path.exists():
        return {}

    known_hashes: dict[str, Path] = {}
    with inventory_path.open(encoding="utf-8-sig", newline="") as inventory_file:
        for row in csv.DictReader(inventory_file):
            if row.get("statut") == "copied" and row.get("sha256") and row.get("photo_stockee"):
                known_hashes[row["sha256"]] = Path(row["photo_stockee"])
    return known_hashes


def _normalise_date(value: str | None) -> str:
    if value is None:
        return date.today().isoformat()
    date.fromisoformat(value)
    return value


def _event_date_from_folder(folder_name: str) -> str:
    candidate = folder_name[:10]
    try:
        date.fromisoformat(candidate)
    except ValueError:
        return date.today().isoformat()
    return candidate


def _event_name_from_folder(folder_name: str) -> str:
    return folder_name[11:].replace("_", " ") if len(folder_name) > 11 else folder_name


def _read_manifest(manifest_path: Path) -> dict[str, object]:
    if not manifest_path.exists():
        return {}
    with manifest_path.open(encoding="utf-8") as manifest_file:
        return json.load(manifest_file)


def _write_source_guide(inbox_dir: Path) -> None:
    guide_path = inbox_dir / WORKSPACE_SOURCE_GUIDE
    if guide_path.exists():
        return
    guide_path.write_text(
        "\n".join(
            (
                "FaceIQ - zone sources",
                "",
                "Mets les photos recues ici, jamais dans samples.",
                "",
                "Structure attendue :",
                "00_A_RECEVOIR/",
                "  Nom_Evenement/",
                "    Nom_Photographe_1/",
                "      IMG_001.jpg",
                "      IMG_002.jpg",
                "    Nom_Photographe_2/",
                "      DSC_1001.jpg",
                "",
                "Puis lance depuis le dossier FaceIQ :",
                '  .\\.venv\\Scripts\\faceiq.exe run "Nom Evenement" ".\\FaceIQ_Workspace\\00_A_RECEVOIR\\Nom_Evenement" --workspace ".\\FaceIQ_Workspace" --date AAAA-MM-JJ',
                "",
                "FaceIQ copiera ensuite les originaux dans 01_EVENEMENTS et extraira les visages.",
            )
        )
        + "\n",
        encoding="utf-8",
    )
