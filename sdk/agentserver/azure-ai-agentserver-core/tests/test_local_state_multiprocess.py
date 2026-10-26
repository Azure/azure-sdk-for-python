# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Cross-process isolation tests for the local state store backend."""

from __future__ import annotations

import multiprocessing
import sys
from pathlib import Path

import pytest
from azure.ai.agentserver.core.storage._errors import FoundryStorageConflictError
from azure.ai.agentserver.core.storage._local_state import LocalStateStoreBackend

_WRITERS = 8


def _backend(path: Path) -> LocalStateStoreBackend:
    return LocalStateStoreBackend(
        path,
        name="shared",
        user_isolation=False,
        item_ttl_seconds=-1,
        description=None,
        tags={},
    )


def _write(path: str, index: int, gate, outcomes) -> None:
    backend = _backend(Path(path))
    gate.wait()
    try:
        backend.set_item(f"key-{index}", {"value": index}, None, None)
        outcomes.put("success")
    except Exception as exc:  # pylint: disable=broad-except
        outcomes.put(type(exc).__name__)


def _create(path: str, gate, outcomes) -> None:
    backend = _backend(Path(path))
    gate.wait()
    try:
        backend.create_item("same", {"value": 1}, None)
        outcomes.put("success")
    except FoundryStorageConflictError:
        outcomes.put("conflict")


def _run(target, path: Path, args_for) -> list[str]:
    context = multiprocessing.get_context("spawn")
    gate = context.Barrier(_WRITERS)
    outcomes = context.Queue()
    processes = [
        context.Process(target=target, args=args_for(index, gate, outcomes))
        for index in range(_WRITERS)
    ]
    for process in processes:
        process.start()
    results = [outcomes.get(timeout=60) for _ in processes]
    for process in processes:
        process.join(60)
    assert [process.exitcode for process in processes] == [0] * _WRITERS
    return results


@pytest.mark.skipif(sys.platform == "win32", reason="spawn-heavy; covered on POSIX")
def test_concurrent_processes_preserve_distinct_writes(tmp_path: Path) -> None:
    path = tmp_path / "shared.json"
    _backend(path).ensure_store()
    results = _run(_write, path, lambda i, g, o: (str(path), i, g, o))
    assert results == ["success"] * _WRITERS
    page = _backend(path).list_keys(
        tags=None, limit=100, after=None, before=None, order="asc"
    )
    assert len(page.keys) == _WRITERS


@pytest.mark.skipif(sys.platform == "win32", reason="spawn-heavy; covered on POSIX")
def test_concurrent_processes_create_item_single_winner(tmp_path: Path) -> None:
    path = tmp_path / "shared.json"
    _backend(path).ensure_store()
    results = _run(_create, path, lambda i, g, o: (str(path), g, o))
    assert results.count("success") == 1
    assert results.count("conflict") == _WRITERS - 1
