# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import hashlib
import io
import sys
import zipfile
from pathlib import Path

SAMPLES_DIR = Path(__file__).resolve().parents[2] / "samples"
sys.path.insert(0, str(SAMPLES_DIR.resolve()))

import util
from util import build_skill_zip


def test_build_skill_zip_writes_deterministic_zip_to_temp_folder(tmp_path, monkeypatch):
    source_dir = tmp_path / "source"
    nested_dir = source_dir / "nested"
    nested_dir.mkdir(parents=True)
    (source_dir / "b.txt").write_bytes(b"bravo")
    (nested_dir / "a.txt").write_bytes(b"alpha")

    temp_dir = tmp_path / "temp"
    temp_dir.mkdir()
    monkeypatch.setattr(util.tempfile, "gettempdir", lambda: str(temp_dir))

    zip_bytes, zip_sha256, zip_path = build_skill_zip(source_dir, "skill.zip")

    assert zip_path == temp_dir.resolve() / "skill.zip"
    assert zip_path.read_bytes() == zip_bytes
    assert zip_sha256 == hashlib.sha256(zip_bytes).hexdigest()

    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        assert zf.namelist() == ["b.txt", "nested/a.txt"]
        assert zf.read("b.txt") == b"bravo"
        assert zf.read("nested/a.txt") == b"alpha"

        for zip_info in zf.infolist():
            assert zip_info.date_time == (1980, 1, 1, 0, 0, 0)
            assert zip_info.create_system == 3
            assert zip_info.compress_type == zipfile.ZIP_STORED
            assert zip_info.external_attr == 0o644 << 16


def test_build_skill_zip_normalizes_text_line_endings_and_preserves_binary(tmp_path, monkeypatch):
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "SKILL.md").write_bytes(b"# Title\r\n\r\nBody\r\n")
    (source_dir / "data.bin").write_bytes(b"\x00\r\n\xff")

    temp_dir = tmp_path / "temp"
    temp_dir.mkdir()
    monkeypatch.setattr(util.tempfile, "gettempdir", lambda: str(temp_dir))

    zip_bytes, _zip_sha256, _zip_path = build_skill_zip(source_dir, "skill.zip")

    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        assert zf.read("SKILL.md") == b"# Title\n\nBody\n"
        assert zf.read("data.bin") == b"\x00\r\n\xff"


def test_build_skill_zip_uses_source_dir_name_for_default_zip_filename(tmp_path, monkeypatch):
    source_dir = tmp_path / "canvas-design"
    source_dir.mkdir()
    (source_dir / "SKILL.md").write_text("# Canvas Design\n", encoding="utf-8")

    temp_dir = tmp_path / "temp"
    temp_dir.mkdir()
    monkeypatch.setattr(util.tempfile, "gettempdir", lambda: str(temp_dir))

    _zip_bytes, _zip_sha256, zip_path = build_skill_zip(source_dir)

    assert zip_path == temp_dir.resolve() / "canvas-design.zip"
    assert zip_path.exists()
