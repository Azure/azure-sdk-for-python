# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import hashlib
import os
import tempfile
import zipfile
from pathlib import Path
from typing import Optional, Tuple


def _resolve_zip_file(zip_file: str) -> Path:
    zip_path = Path(zip_file)
    if zip_path.is_absolute():
        return zip_path

    for base_path in (Path.cwd(), Path(__file__).resolve().parent, Path(__file__).resolve().parents[1]):
        candidate = base_path / zip_path
        if candidate.exists():
            return candidate.resolve()

    return (Path.cwd() / zip_path).resolve()


def zip(
    source_dir: Path, zip_filename: Optional[str] = None, *, env_var: str = "ZIP_FILE_PATH"
) -> Tuple[bytes, str, Path]:
    """Return zip bytes, SHA-256, and path for a source directory.

    Direct sample runs create a normal zip from ``source_dir`` in the temp folder.
    Callers can set ``env_var`` to load an existing zip file instead of creating
    a new archive.
    """
    configured_zip_file = os.environ.get(env_var)
    if configured_zip_file:
        zip_path = _resolve_zip_file(configured_zip_file)
        zip_bytes = zip_path.read_bytes()
        zip_sha256 = hashlib.sha256(zip_bytes).hexdigest()
        print(f"Loaded zip from {zip_path}: {len(zip_bytes)} bytes, sha256={zip_sha256}")
        return zip_bytes, zip_sha256, zip_path

    zip_path = Path(tempfile.gettempdir()).resolve() / (zip_filename or f"{source_dir.name}.zip")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(source_dir.rglob("*")):
            if not file_path.is_file():
                continue
            if "__pycache__" in file_path.parts or file_path.suffix == ".pyc" or file_path.name == "README.md":
                continue
            zf.write(file_path, file_path.relative_to(source_dir).as_posix())

    zip_bytes = zip_path.read_bytes()
    zip_sha256 = hashlib.sha256(zip_bytes).hexdigest()
    print(f"Built zip from {source_dir}: {len(zip_bytes)} bytes, sha256={zip_sha256}, path={zip_path}")
    return zip_bytes, zip_sha256, zip_path
