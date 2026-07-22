# Copyright (c) Microsoft. All rights reserved.

"""File-backed checkpoint store for in-flight LLM content.

``ctx.metadata`` on the resilient-task primitive is a *small-watermark*
store, not a bulk-data store (see ``core/docs/tasks-guide.md``
§"Persistence Model"). For anything heavier than a few bytes — e.g.
the partially-streamed text of the current phase's in-flight subcall
chain — the application is expected to maintain its own per-app
checkpoint store and just keep a *reference* in metadata.

This file is the minimal local checkpoint store for the resilient
research agent. Each phase's in-progress text is a JSON blob keyed by
``<task_id>:<phase_idx>``. Writes are atomic (tempfile + rename) so a
crash mid-write leaves either the old value or the new value, never a
truncated file. The store is deliberately tiny — no metrics, no
contention handling — because this is a sample, not a production
component. In production, swap this for a real resilient blob store
(Cosmos, blob storage, etc.).

The store survives container restarts via the platform's per-session
mounted directory (the same directory the streams registry uses); it
does not survive task deletion.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path


class CheckpointStore:
    """File-backed key->str blob store with atomic writes.

    Used for in-flight phase text — the heaviest non-stream artifact
    the resilient handler keeps around. The agent's per-phase recovery
    flow loads the previous-subcall text via :meth:`get` at phase
    entry, advances it after each subcall via :meth:`put`, and clears
    the phase entry via :meth:`delete` at phase end (so completed
    phases don't accumulate disk usage).
    """

    def __init__(self, base_dir: Path) -> None:
        self._base = base_dir
        self._base.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        # Hyphens + colons are safe on every fs we target; keep the
        # original key as-is so a directory listing is self-describing.
        return self._base / f"{key}.json"

    def get(self, key: str) -> str:
        """Return the stored text, or empty string if absent."""
        path = self._path(key)
        if not path.exists():
            return ""
        return json.loads(path.read_text(encoding="utf-8"))

    def put(self, key: str, value: str) -> None:
        """Atomically write *value* — temp file + rename."""
        target = self._path(key)
        fd, tmp = tempfile.mkstemp(dir=str(self._base), prefix=f"{key}_", suffix=".tmp")
        try:
            with open(fd, "w", encoding="utf-8") as fh:
                json.dump(value, fh)
            Path(tmp).replace(target)
        except BaseException:
            Path(tmp).unlink(missing_ok=True)
            raise

    def delete(self, key: str) -> None:
        """Remove *key* if present; no-op otherwise."""
        path = self._path(key)
        if path.exists():
            path.unlink()

    def delete_prefix(self, prefix: str) -> None:
        """Remove all keys with the given prefix.

        Used on a steered-turn reset to clear all phase entries for a
        task in one shot, without enumerating each phase index.
        """
        for path in self._base.glob(f"{prefix}*.json"):
            path.unlink(missing_ok=True)
