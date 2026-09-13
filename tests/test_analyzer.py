from pathlib import Path

from faceiq.analyzer import FaceAnalyzer
from faceiq.config import AppConfig


def test_discover_images_filters_supported_files(tmp_path: Path):
    (tmp_path / "a.jpg").write_bytes(b"x"); (tmp_path / "b.PNG").write_bytes(b"x"); (tmp_path / "c.txt").write_text("x"); nested = tmp_path / "nested"; nested.mkdir(); (nested / "d.webp").write_bytes(b"x")
    analyzer = object.__new__(FaceAnalyzer); analyzer.config = AppConfig(); recursive = analyzer.discover_images(tmp_path, recursive=True); flat = analyzer.discover_images(tmp_path, recursive=False)
    assert [p.name for p in recursive] == ["a.jpg", "b.PNG", "d.webp"]; assert [p.name for p in flat] == ["a.jpg", "b.PNG"]
