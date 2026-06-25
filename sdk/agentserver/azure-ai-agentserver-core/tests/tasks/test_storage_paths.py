# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Tests for the unified storage paths module.

Covers the public ``azure.ai.agentserver.core.storage_paths`` module:
default resolution to ``~/.agentserver/{tasks,streams,responses}/``, the
``AGENTSERVER_STATE_ROOT`` env-var override, rejection of unknown
subdir kinds, and the operator override
``AGENTSERVER_TASKS_BACKEND=local|hosted`` consumed by
``TaskManager._create_provider``.
"""

from __future__ import annotations

import os
from pathlib import Path


def test_storage_paths_module_is_public(monkeypatch) -> None:
    """``azure.ai.agentserver.core.storage_paths`` must be a PUBLIC module.

    Per Principle I (Modular Package Architecture) + constitution.md:7-15,
    responses must not import from a private ``_storage_paths`` module.
    """
    monkeypatch.delenv("AGENTSERVER_STATE_ROOT", raising=False)
    from azure.ai.agentserver.core import storage_paths  # noqa: F401

    # Module must be importable without leading underscore.
    assert hasattr(storage_paths, "resolve_state_subdir"), "storage_paths.resolve_state_subdir must be exported"


def test_resolve_state_subdir_defaults_to_home_resilient(monkeypatch, tmp_path) -> None:
    """With no env var set, ``resolve_state_subdir('tasks')`` returns
    ``~/.agentserver/tasks/`` (NOT the legacy ``~/.agentserver-tasks/``)."""
    monkeypatch.delenv("AGENTSERVER_STATE_ROOT", raising=False)
    monkeypatch.delenv("AGENTSERVER_STATE_TASKS_PATH", raising=False)
    monkeypatch.delenv("AGENTSERVER_STREAM_STORE_PATH", raising=False)
    from azure.ai.agentserver.core import storage_paths

    tasks_path = storage_paths.resolve_state_subdir("tasks")
    streams_path = storage_paths.resolve_state_subdir("streams")
    responses_path = storage_paths.resolve_state_subdir("responses")

    home_resilient = Path.home() / ".agentserver"
    assert tasks_path == home_resilient / "tasks"
    assert streams_path == home_resilient / "streams"
    assert responses_path == home_resilient / "responses"


def test_resolve_state_subdir_env_override(monkeypatch, tmp_path) -> None:
    """``AGENTSERVER_STATE_ROOT=/foo`` makes all three subdirs root at /foo."""
    monkeypatch.setenv("AGENTSERVER_STATE_ROOT", str(tmp_path))
    monkeypatch.delenv("AGENTSERVER_STATE_TASKS_PATH", raising=False)
    monkeypatch.delenv("AGENTSERVER_STREAM_STORE_PATH", raising=False)
    from azure.ai.agentserver.core import storage_paths

    tasks_path = storage_paths.resolve_state_subdir("tasks")
    streams_path = storage_paths.resolve_state_subdir("streams")
    responses_path = storage_paths.resolve_state_subdir("responses")

    assert tasks_path == tmp_path / "tasks"
    assert streams_path == tmp_path / "streams"
    assert responses_path == tmp_path / "responses"


def test_resolve_state_subdir_rejects_unknown_kind() -> None:
    """``resolve_state_subdir('garbage')`` must reject — only the known kinds are valid."""
    from azure.ai.agentserver.core import storage_paths

    try:
        storage_paths.resolve_state_subdir("garbage")  # type: ignore[arg-type]
    except (ValueError, TypeError):
        return
    raise AssertionError("resolve_state_subdir must reject unknown subdir kinds")


def test_legacy_env_vars_no_longer_consulted(monkeypatch, tmp_path) -> None:
    """Setting the legacy ``AGENTSERVER_STATE_TASKS_PATH`` / ``AGENTSERVER_STREAM_STORE_PATH``
    must NOT affect path resolution — the legacy vars are deleted.
    """
    monkeypatch.delenv("AGENTSERVER_STATE_ROOT", raising=False)
    monkeypatch.setenv("AGENTSERVER_STATE_TASKS_PATH", str(tmp_path / "legacy_tasks"))
    monkeypatch.setenv("AGENTSERVER_STREAM_STORE_PATH", str(tmp_path / "legacy_streams"))
    from azure.ai.agentserver.core import storage_paths

    # The new resolver must IGNORE the legacy vars.
    tasks_path = storage_paths.resolve_state_subdir("tasks")
    streams_path = storage_paths.resolve_state_subdir("streams")
    home_resilient = Path.home() / ".agentserver"
    assert (
        tasks_path == home_resilient / "tasks"
    ), f"legacy AGENTSERVER_STATE_TASKS_PATH leaked into new resolver — got {tasks_path}"
    assert (
        streams_path == home_resilient / "streams"
    ), f"legacy AGENTSERVER_STREAM_STORE_PATH leaked into new resolver — got {streams_path}"


def test_tasks_default_path_used_by_local_provider(monkeypatch, tmp_path) -> None:
    """The TaskManager's local-provider default path must use the new resolver.

    Pre-Phase-3a: ``Path.home() / ".agentserver-tasks"``.
    Post-Phase-3a: ``storage_paths.resolve_state_subdir("tasks")`` →
    ``Path.home() / ".agentserver" / "tasks"``.

    Comment references to the legacy path (historical migration notes)
    are permitted; only actual ``Path('.agentserver-tasks')`` use or
    ``os.environ.get('AGENTSERVER_STATE_TASKS_PATH')`` reads are
    forbidden.
    """
    monkeypatch.delenv("AGENTSERVER_STATE_ROOT", raising=False)
    monkeypatch.delenv("AGENTSERVER_STATE_TASKS_PATH", raising=False)
    # Read the _manager.py source to confirm it no longer USES the
    # legacy path. This is a structural assertion (Principle XII §3 RED
    # signal that survives even if behavior coincidentally aligns).
    import inspect

    from azure.ai.agentserver.core.tasks import _manager

    src = inspect.getsource(_manager)
    forbidden_env_reads = [
        'environ.get("AGENTSERVER_STATE_TASKS_PATH")',
        "environ.get('AGENTSERVER_STATE_TASKS_PATH')",
        'getenv("AGENTSERVER_STATE_TASKS_PATH")',
        "getenv('AGENTSERVER_STATE_TASKS_PATH')",
    ]
    for pat in forbidden_env_reads:
        assert pat not in src, (
            f"_manager.py must not read the legacy "
            f"AGENTSERVER_STATE_TASKS_PATH env var. Found '{pat}' in source. "
            f"Use storage_paths.resolve_state_subdir('tasks') instead."
        )
    assert '"/.agentserver-tasks"' not in src and "'/.agentserver-tasks'" not in src, (
        "_manager.py must not USE the legacy "
        "'.agentserver-tasks' path string. Use storage_paths.resolve_state_subdir('tasks')."
    )
    assert '".agentserver-tasks"' not in src and "'.agentserver-tasks'" not in src, (
        "_manager.py must not USE the legacy " "'.agentserver-tasks' path string."
    )


# ────────────────────────────────────────────────────────────────────
# AGENTSERVER_TASKS_BACKEND operator override
# ────────────────────────────────────────────────────────────────────


def test_tasks_backend_local_forces_local_provider_in_hosted(monkeypatch, tmp_path) -> None:
    """AGENTSERVER_TASKS_BACKEND=local forces LocalFileTaskProvider even when
    config.is_hosted is True.

    Allows local repro / debugging of hosted-only scenarios on a workstation
    without standing up the hosted task API, and lets hosted operators opt
    out of the task-storage API in favour of on-disk persistence.
    """
    from unittest.mock import MagicMock

    from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
    from azure.ai.agentserver.core.tasks._manager import TaskManager

    monkeypatch.setenv("AGENTSERVER_TASKS_BACKEND", "local")
    monkeypatch.setenv("AGENTSERVER_STATE_ROOT", str(tmp_path))

    config = MagicMock()
    config.is_hosted = True
    config.project_endpoint = "https://fake.example/projects/fake"

    provider = TaskManager._create_provider(config)
    assert isinstance(
        provider, LocalFileTaskProvider
    ), f"Expected LocalFileTaskProvider with backend override, got {type(provider).__name__}"


def test_tasks_backend_hosted_forces_hosted_provider_in_local(monkeypatch, tmp_path) -> None:
    """AGENTSERVER_TASKS_BACKEND=hosted forces HostedTaskProvider even when
    config.is_hosted is False.

    Enables the inverse override — testing the hosted code path against a
    fake task API from a local environment.
    """
    from unittest.mock import MagicMock

    from azure.ai.agentserver.core.tasks._client import HostedTaskProvider
    from azure.ai.agentserver.core.tasks._manager import TaskManager

    monkeypatch.setenv("AGENTSERVER_TASKS_BACKEND", "hosted")
    monkeypatch.setenv("AGENTSERVER_STATE_ROOT", str(tmp_path))

    config = MagicMock()
    config.is_hosted = False
    config.project_endpoint = "https://fake.example/projects/fake"

    provider = TaskManager._create_provider(config)
    assert isinstance(
        provider, HostedTaskProvider
    ), f"Expected HostedTaskProvider with backend override, got {type(provider).__name__}"


def test_tasks_backend_invalid_value_raises(monkeypatch, tmp_path) -> None:
    """Unknown AGENTSERVER_TASKS_BACKEND values must raise at provider-create."""
    import pytest as _pytest
    from unittest.mock import MagicMock

    from azure.ai.agentserver.core.tasks._manager import TaskManager

    monkeypatch.setenv("AGENTSERVER_TASKS_BACKEND", "wat")
    monkeypatch.setenv("AGENTSERVER_STATE_ROOT", str(tmp_path))

    config = MagicMock()
    config.is_hosted = False
    config.project_endpoint = "https://fake.example/projects/fake"

    with _pytest.raises(ValueError, match="AGENTSERVER_TASKS_BACKEND"):
        TaskManager._create_provider(config)


def test_tasks_backend_unset_uses_is_hosted_detection(monkeypatch, tmp_path) -> None:
    """No AGENTSERVER_TASKS_BACKEND override → fall back to config.is_hosted."""
    from unittest.mock import MagicMock

    from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
    from azure.ai.agentserver.core.tasks._manager import TaskManager

    monkeypatch.delenv("AGENTSERVER_TASKS_BACKEND", raising=False)
    monkeypatch.setenv("AGENTSERVER_STATE_ROOT", str(tmp_path))

    config = MagicMock()
    config.is_hosted = False
    config.project_endpoint = "https://fake.example/projects/fake"

    provider = TaskManager._create_provider(config)
    assert isinstance(provider, LocalFileTaskProvider)
