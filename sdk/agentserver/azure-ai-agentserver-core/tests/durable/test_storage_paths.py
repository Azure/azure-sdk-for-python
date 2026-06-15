# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Spec 024 Phase 3a RED tests for the unified storage paths.

These tests verify the new public ``azure.ai.agentserver.core.storage_paths``
module and the cross-package storage-root rename: ``~/.durable-tasks/`` →
``~/.durable/tasks/`` (with ``AGENTSERVER_DURABLE_ROOT`` as the single env
var override).

Test-file rationale (Principle XII §4 non-duplication): no existing test
file covers default-path-resolution for the durable task store. The
storage-paths helper is also a NEW public module that warrants its own
test file. Existing tests that monkeypatch ``AGENTSERVER_DURABLE_TASKS_PATH``
will be updated in the impl commit to use ``AGENTSERVER_DURABLE_ROOT``.

EXPECTED: RED at this commit; GREEN after the Phase 3a implementation
commit lands. See ``sdk/agentserver/specs/024-responses-redesign.md``
Phase 3a steps 16a-16e.
"""

from __future__ import annotations

import os
from pathlib import Path


def test_storage_paths_module_is_public(monkeypatch) -> None:
    """``azure.ai.agentserver.core.storage_paths`` must be a PUBLIC module.

    Per Principle I (Modular Package Architecture) + constitution.md:7-15,
    responses must not import from a private ``_storage_paths`` module.
    """
    monkeypatch.delenv("AGENTSERVER_DURABLE_ROOT", raising=False)
    from azure.ai.agentserver.core import storage_paths  # noqa: F401

    # Module must be importable without leading underscore.
    assert hasattr(storage_paths, "resolve_durable_subdir"), (
        "spec 024 Phase 3a: storage_paths.resolve_durable_subdir must be exported"
    )


def test_resolve_durable_subdir_defaults_to_home_durable(monkeypatch, tmp_path) -> None:
    """With no env var set, ``resolve_durable_subdir('tasks')`` returns
    ``~/.durable/tasks/`` (NOT the legacy ``~/.durable-tasks/``)."""
    monkeypatch.delenv("AGENTSERVER_DURABLE_ROOT", raising=False)
    monkeypatch.delenv("AGENTSERVER_DURABLE_TASKS_PATH", raising=False)
    monkeypatch.delenv("AGENTSERVER_STREAM_STORE_PATH", raising=False)
    from azure.ai.agentserver.core import storage_paths

    tasks_path = storage_paths.resolve_durable_subdir("tasks")
    streams_path = storage_paths.resolve_durable_subdir("streams")
    responses_path = storage_paths.resolve_durable_subdir("responses")

    home_durable = Path.home() / ".durable"
    assert tasks_path == home_durable / "tasks"
    assert streams_path == home_durable / "streams"
    assert responses_path == home_durable / "responses"


def test_resolve_durable_subdir_env_override(monkeypatch, tmp_path) -> None:
    """``AGENTSERVER_DURABLE_ROOT=/foo`` makes all three subdirs root at /foo."""
    monkeypatch.setenv("AGENTSERVER_DURABLE_ROOT", str(tmp_path))
    monkeypatch.delenv("AGENTSERVER_DURABLE_TASKS_PATH", raising=False)
    monkeypatch.delenv("AGENTSERVER_STREAM_STORE_PATH", raising=False)
    from azure.ai.agentserver.core import storage_paths

    tasks_path = storage_paths.resolve_durable_subdir("tasks")
    streams_path = storage_paths.resolve_durable_subdir("streams")
    responses_path = storage_paths.resolve_durable_subdir("responses")

    assert tasks_path == tmp_path / "tasks"
    assert streams_path == tmp_path / "streams"
    assert responses_path == tmp_path / "responses"


def test_resolve_durable_subdir_rejects_unknown_kind() -> None:
    """``resolve_durable_subdir('garbage')`` must reject — only the known kinds are valid."""
    from azure.ai.agentserver.core import storage_paths

    try:
        storage_paths.resolve_durable_subdir("garbage")  # type: ignore[arg-type]
    except (ValueError, TypeError):
        return
    raise AssertionError(
        "spec 024 Phase 3a: resolve_durable_subdir must reject unknown subdir kinds"
    )


def test_legacy_env_vars_no_longer_consulted(monkeypatch, tmp_path) -> None:
    """Setting the legacy ``AGENTSERVER_DURABLE_TASKS_PATH`` / ``AGENTSERVER_STREAM_STORE_PATH``
    must NOT affect path resolution after Phase 3a — the legacy vars are deleted.
    """
    monkeypatch.delenv("AGENTSERVER_DURABLE_ROOT", raising=False)
    monkeypatch.setenv("AGENTSERVER_DURABLE_TASKS_PATH", str(tmp_path / "legacy_tasks"))
    monkeypatch.setenv("AGENTSERVER_STREAM_STORE_PATH", str(tmp_path / "legacy_streams"))
    from azure.ai.agentserver.core import storage_paths

    # The new resolver must IGNORE the legacy vars.
    tasks_path = storage_paths.resolve_durable_subdir("tasks")
    streams_path = storage_paths.resolve_durable_subdir("streams")
    home_durable = Path.home() / ".durable"
    assert tasks_path == home_durable / "tasks", (
        f"legacy AGENTSERVER_DURABLE_TASKS_PATH leaked into new resolver — got {tasks_path}"
    )
    assert streams_path == home_durable / "streams", (
        f"legacy AGENTSERVER_STREAM_STORE_PATH leaked into new resolver — got {streams_path}"
    )


def test_tasks_default_path_used_by_local_provider(monkeypatch, tmp_path) -> None:
    """The TaskManager's local-provider default path must use the new resolver.

    Pre-Phase-3a: ``Path.home() / ".durable-tasks"``.
    Post-Phase-3a: ``storage_paths.resolve_durable_subdir("tasks")`` →
    ``Path.home() / ".durable" / "tasks"``.

    Comment references to the legacy path (historical migration notes)
    are permitted; only actual ``Path('.durable-tasks')`` use or
    ``os.environ.get('AGENTSERVER_DURABLE_TASKS_PATH')`` reads are
    forbidden.
    """
    monkeypatch.delenv("AGENTSERVER_DURABLE_ROOT", raising=False)
    monkeypatch.delenv("AGENTSERVER_DURABLE_TASKS_PATH", raising=False)
    # Read the _manager.py source to confirm it no longer USES the
    # legacy path. This is a structural assertion (Principle XII §3 RED
    # signal that survives even if behavior coincidentally aligns).
    import inspect

    from azure.ai.agentserver.core.durable import _manager

    src = inspect.getsource(_manager)
    forbidden_env_reads = [
        'environ.get("AGENTSERVER_DURABLE_TASKS_PATH")',
        "environ.get('AGENTSERVER_DURABLE_TASKS_PATH')",
        'getenv("AGENTSERVER_DURABLE_TASKS_PATH")',
        "getenv('AGENTSERVER_DURABLE_TASKS_PATH')",
    ]
    for pat in forbidden_env_reads:
        assert pat not in src, (
            f"spec 024 Phase 3a: _manager.py must not read the legacy "
            f"AGENTSERVER_DURABLE_TASKS_PATH env var. Found '{pat}' in source. "
            f"Use storage_paths.resolve_durable_subdir('tasks') instead."
        )
    assert '"/.durable-tasks"' not in src and "'/.durable-tasks'" not in src, (
        "spec 024 Phase 3a: _manager.py must not USE the legacy "
        "'.durable-tasks' path string. Use storage_paths.resolve_durable_subdir('tasks')."
    )
    assert '".durable-tasks"' not in src and "'.durable-tasks'" not in src, (
        "spec 024 Phase 3a: _manager.py must not USE the legacy "
        "'.durable-tasks' path string."
    )
