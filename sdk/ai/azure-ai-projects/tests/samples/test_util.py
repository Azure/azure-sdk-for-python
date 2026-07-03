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
from util import zip as zip_directory


def test_zip_writes_zip_to_temp_folder(tmp_path, monkeypatch):
    source_dir = tmp_path / "source"
    nested_dir = source_dir / "nested"
    nested_dir.mkdir(parents=True)
    (source_dir / "b.txt").write_bytes(b"bravo")
    (nested_dir / "a.txt").write_bytes(b"alpha")
    (source_dir / "README.md").write_bytes(b"skip")
    pycache_dir = source_dir / "__pycache__"
    pycache_dir.mkdir()
    (pycache_dir / "module.pyc").write_bytes(b"skip")

    temp_dir = tmp_path / "temp"
    temp_dir.mkdir()
    monkeypatch.setattr(util.tempfile, "gettempdir", lambda: str(temp_dir))

    zip_bytes, zip_sha256, zip_path = zip_directory(source_dir, "source.zip")

    assert zip_path == temp_dir.resolve() / "source.zip"
    assert zip_path.read_bytes() == zip_bytes
    assert zip_sha256 == hashlib.sha256(zip_bytes).hexdigest()

    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        assert zf.namelist() == ["b.txt", "nested/a.txt"]
        assert zf.read("b.txt") == b"bravo"
        assert zf.read("nested/a.txt") == b"alpha"


def test_zip_loads_zip_file_from_env_var(tmp_path, monkeypatch):
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "ignored.txt").write_text("ignored", encoding="utf-8")

    prebuilt_zip = tmp_path / "prebuilt.zip"
    with zipfile.ZipFile(prebuilt_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("asset.txt", b"from prebuilt")

    monkeypatch.setenv("ZIP_FILE_PATH", str(prebuilt_zip))

    zip_bytes, zip_sha256, zip_path = zip_directory(source_dir, "runtime.zip")

    assert zip_path == prebuilt_zip
    assert zip_bytes == prebuilt_zip.read_bytes()
    assert zip_sha256 == hashlib.sha256(zip_bytes).hexdigest()


def test_zip_uses_source_dir_name_for_default_zip_filename(tmp_path, monkeypatch):
    source_dir = tmp_path / "canvas-design"
    source_dir.mkdir()
    (source_dir / "SKILL.md").write_text("# Canvas Design\n", encoding="utf-8")

    temp_dir = tmp_path / "temp"
    temp_dir.mkdir()
    monkeypatch.setattr(util.tempfile, "gettempdir", lambda: str(temp_dir))

    _zip_bytes, _zip_sha256, zip_path = zip_directory(source_dir)

    assert zip_path == temp_dir.resolve() / "canvas-design.zip"
    assert zip_path.exists()
