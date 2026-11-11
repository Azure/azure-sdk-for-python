# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Tests for agentserver on-disk state path resolution.

Covers ``resolve_state_root`` / ``resolve_state_subdir`` in
``azure.ai.agentserver.core._config`` (the central settings/env-var
module): default resolution to ``~/.agentserver/<name>/``, the
``AGENTSERVER_STATE_ROOT`` env-var override, the generic
(no-reserved-names) subdir resolver, and the operator override
``AGENTSERVER_TASKS_BACKEND=local|hosted`` consumed by
``TaskManager._create_provider``.
"""

from __future__ import annotations

from pathlib import Path


def test_state_path_resolver_lives_in_config() -> None:
    """The state-path resolver is exposed from the central ``_config``
    settings module (alongside the other ``resolve_*`` helpers), not a
    separate storage module. Only the subdir resolver is public — every
    caller wants a named subdir, not the bare root."""
    from azure.ai.agentserver.core import _config

    assert hasattr(_config, "resolve_state_subdir")


def test_resolve_state_subdir_defaults_to_home(monkeypatch) -> None:
    """With no env var set, ``resolve_state_subdir(<name>)`` returns
    ``~/.agentserver/<name>/`` for any caller-owned subdir name."""
    monkeypatch.delenv("AGENTSERVER_STATE_ROOT", raising=False)
    from azure.ai.agentserver.core import _config

    home_root = Path.home() / ".agentserver"
    assert _config.resolve_state_subdir("tasks") == home_root / "tasks"
    # The resolver is generic — each subsystem owns its own subdir name;
    # the core layer does not enumerate or reserve names.
    assert _config.resolve_state_subdir("streams") == home_root / "streams"
    assert _config.resolve_state_subdir("anything-a-caller-owns") == home_root / "anything-a-caller-owns"


def test_resolve_state_subdir_env_override(monkeypatch, tmp_path) -> None:
    """``AGENTSERVER_STATE_ROOT=/foo`` roots every subdir at /foo."""
    monkeypatch.setenv("AGENTSERVER_STATE_ROOT", str(tmp_path))
    from azure.ai.agentserver.core import _config

    assert _config.resolve_state_subdir("tasks") == tmp_path / "tasks"
    assert _config.resolve_state_subdir("streams") == tmp_path / "streams"


def test_legacy_env_vars_no_longer_consulted(monkeypatch, tmp_path) -> None:
    """The legacy per-subsystem env vars must NOT affect resolution —
    ``AGENTSERVER_STATE_ROOT`` is the single operator knob."""
    monkeypatch.delenv("AGENTSERVER_STATE_ROOT", raising=False)
    monkeypatch.setenv("AGENTSERVER_STATE_TASKS_PATH", str(tmp_path / "legacy_tasks"))
    monkeypatch.setenv("AGENTSERVER_STREAM_STORE_PATH", str(tmp_path / "legacy_streams"))
    from azure.ai.agentserver.core import _config

    home_root = Path.home() / ".agentserver"
    assert _config.resolve_state_subdir("tasks") == home_root / "tasks"
    assert _config.resolve_state_subdir("streams") == home_root / "streams"


def test_tasks_default_path_used_by_local_provider() -> None:
    """``TaskManager`` must resolve its tasks dir via the state resolver,
    not the legacy ``AGENTSERVER_STATE_TASKS_PATH`` / ``.agentserver-tasks``.
    """
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
        assert pat not in src, f"_manager.py must not read the legacy env var. Found '{pat}' in source."
    assert '".agentserver-tasks"' not in src and "'.agentserver-tasks'" not in src, (
        "_manager.py must not USE the legacy '.agentserver-tasks' path string."
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
