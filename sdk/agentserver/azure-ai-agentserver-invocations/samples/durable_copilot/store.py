"""File-based key→JSON store for powering the invocation API.

This module provides a minimal persistence layer that the HTTP host uses to
store per-invocation results.  It is **not** part of the durable task
framework — it is the developer's own persistence for powering the API
contract (``GET /invocations/{invocation_id}``).

.. warning::

    For demonstration only.  In production, use a database (Redis, Cosmos DB,
    PostgreSQL, etc.).
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any


class FileStore:
    """Minimal file-backed key→JSON store.

    Each entry is a single JSON file.  Writes are atomic (temp + rename).
    """

    def __init__(self, base_dir: Path) -> None:
        self._base = base_dir
        self._base.mkdir(parents=True, exist_ok=True)

    def save(self, key: str, data: dict[str, Any]) -> None:
        """Atomically write *data* as JSON — temp file + rename."""
        target = self._base / f"{key}.json"
        fd, tmp_path = tempfile.mkstemp(
            dir=str(self._base), suffix=".tmp", prefix=f"{key}_"
        )
        try:
            with open(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            Path(tmp_path).replace(target)
        except BaseException:
            Path(tmp_path).unlink(missing_ok=True)
            raise

    def load(self, key: str) -> dict[str, Any] | None:
        """Return the stored dict, or ``None`` if the key does not exist."""
        path = self._base / f"{key}.json"
        if path.exists():
            return json.loads(path.read_text())
        return None

    def delete(self, key: str) -> bool:
        """Remove the entry for *key*.  Returns ``True`` if it existed."""
        path = self._base / f"{key}.json"
        if path.exists():
            path.unlink()
            return True
        return False
