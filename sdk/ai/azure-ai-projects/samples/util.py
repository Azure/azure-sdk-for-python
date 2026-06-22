# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import hashlib
import io
import tempfile
import zipfile
from pathlib import Path
from typing import Optional, Tuple


def _read_zip_member_bytes(file_path: Path) -> bytes:
    file_bytes = file_path.read_bytes()
    if b"\0" in file_bytes:
        return file_bytes

    try:
        text = file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return file_bytes

    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def build_skill_zip(source_dir: Path, zip_filename: Optional[str] = None) -> Tuple[bytes, str, Path]:
    """Zip all files in *source_dir* deterministically and return ``(zip_bytes, sha256_hex, zip_path)``."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_STORED) as zf:
        for file_path in sorted(source_dir.rglob("*")):
            if file_path.is_file():
                arcname = file_path.relative_to(source_dir).as_posix()
                zip_info = zipfile.ZipInfo(arcname, date_time=(1980, 1, 1, 0, 0, 0))
                zip_info.compress_type = zipfile.ZIP_STORED
                zip_info.external_attr = 0o644 << 16
                zf.writestr(zip_info, _read_zip_member_bytes(file_path))
    zip_bytes = buf.getvalue()
    zip_sha256 = hashlib.sha256(zip_bytes).hexdigest()
    zip_path = Path(tempfile.gettempdir()).resolve() / (zip_filename or f"{source_dir.name}.zip")
    zip_path.write_bytes(zip_bytes)
    print(f"Built skill zip from {source_dir}: " f"{len(zip_bytes)} bytes, sha256={zip_sha256}, path={zip_path}")
    return zip_bytes, zip_sha256, zip_path
