import csv

from faceiq.workflow import create_event_layout, find_event_layout, ingest_delivery, initialize_workspace


def test_initialize_workspace_creates_source_guide(tmp_path) -> None:
    workspace = initialize_workspace(tmp_path / "workspace")

    guide = workspace / "00_A_RECEVOIR" / "A_LIRE_SOURCES.txt"

    assert guide.is_file()
    assert "jamais dans samples" in guide.read_text(encoding="utf-8")


def test_ingest_delivery_copies_photographer_batches_and_skips_duplicates(tmp_path) -> None:
    delivery = tmp_path / "livraison"
    (delivery / "Alice").mkdir(parents=True)
    (delivery / "Bob").mkdir(parents=True)
    (delivery / "Alice" / "photo_1.jpg").write_bytes(b"alice-image")
    (delivery / "Bob" / "photo_2.jpg").write_bytes(b"bob-image")
    (delivery / "Bob" / "notes.txt").write_text("ignore", encoding="utf-8")

    layout = create_event_layout(tmp_path / "workspace", "Gala Été", "2026-06-25")
    first_summary = ingest_delivery(layout, delivery)
    second_summary = ingest_delivery(layout, delivery)

    assert first_summary.copied == 2
    assert first_summary.skipped_duplicates == 0
    assert first_summary.unsupported == 1
    assert second_summary.copied == 0
    assert second_summary.skipped_duplicates == 2
    assert (layout.sources_dir / "Alice" / "photo_1.jpg").is_file()
    assert (layout.sources_dir / "Bob" / "photo_2.jpg").is_file()

    with first_summary.inventory_path.open(encoding="utf-8-sig", newline="") as inventory_file:
        rows = list(csv.DictReader(inventory_file))
    assert [row["statut"] for row in rows] == [
        "copied",
        "copied",
        "skipped_duplicate",
        "skipped_duplicate",
    ]


def test_find_event_layout_resolves_existing_event_by_name(tmp_path) -> None:
    layout = create_event_layout(tmp_path / "workspace", "Salon Photo", "2026-06-25")

    resolved = find_event_layout(tmp_path / "workspace", "Salon Photo")

    assert resolved.event_dir == layout.event_dir
    assert resolved.reports_dir == layout.reports_dir
