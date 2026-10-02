# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Tests for automatic observability startup mode selection."""

from __future__ import annotations

import asyncio
import os
import sys
import sysconfig
from threading import Event
from unittest import mock

import pytest

from azure.ai.agentserver.core import AgentServerHost
from azure.ai.agentserver.core import _tracing
from azure.ai.agentserver.core._observability_startup import (
    effective_cpu_count,
    is_free_threaded_runtime,
    parse_cpuset_count,
    resolve_observability_startup_mode,
)


@pytest.mark.parametrize(
    "cpuset, expected",
    [
        ("0", 1),
        ("0-1", 2),
        ("0-1,4,6-7", 5),
        ("", None),
        ("bad", None),
    ],
)
def test_parse_cpuset_count(cpuset: str, expected: int | None) -> None:
    assert parse_cpuset_count(cpuset) == expected


def test_explicit_cpu_limit_wins(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGENTSERVER_CPU_LIMIT", "2.5")
    assert effective_cpu_count() == 2.5


def test_standard_python_is_not_free_threaded(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "_is_gil_enabled", lambda: True, raising=False)
    assert not is_free_threaded_runtime()


def test_free_threaded_python_requires_disabled_gil_build(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "_is_gil_enabled", lambda: False, raising=False)
    monkeypatch.setattr(sysconfig, "get_config_var", lambda _name: 1)
    assert is_free_threaded_runtime()


def test_cgroup_v2_quota_limits_cpu_count(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AGENTSERVER_CPU_LIMIT", raising=False)
    monkeypatch.setattr(os, "process_cpu_count", lambda: 16, raising=False)
    monkeypatch.setattr(
        "azure.ai.agentserver.core._observability_startup._read_text_file",
        lambda path: "50000 100000" if path == "/sys/fs/cgroup/cpu.max" else None,
    )
    assert effective_cpu_count() == 0.5


def test_cgroup_v1_quota_limits_cpu_count(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AGENTSERVER_CPU_LIMIT", raising=False)
    monkeypatch.setattr(os, "process_cpu_count", lambda: 16, raising=False)

    def read_text(path: str) -> str | None:
        values = {
            "/sys/fs/cgroup/cpu.max": None,
            "/sys/fs/cgroup/cpu/cpu.cfs_quota_us": "200000",
            "/sys/fs/cgroup/cpu/cpu.cfs_period_us": "100000",
        }
        return values.get(path)

    monkeypatch.setattr("azure.ai.agentserver.core._observability_startup._read_text_file", read_text)
    assert effective_cpu_count() == 2.0


def test_cpuset_limits_cpu_count(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AGENTSERVER_CPU_LIMIT", raising=False)
    monkeypatch.setattr(os, "process_cpu_count", lambda: 16, raising=False)

    def read_text(path: str) -> str | None:
        if path == "/sys/fs/cgroup/cpu.max":
            return "max 100000"
        if path == "/sys/fs/cgroup/cpuset.cpus.effective":
            return "0-1"
        return None

    monkeypatch.setattr("azure.ai.agentserver.core._observability_startup._read_text_file", read_text)
    assert effective_cpu_count() == 2.0


def test_invalid_explicit_limit_falls_back_to_detected_cpu(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AGENTSERVER_CPU_LIMIT", "invalid")
    monkeypatch.setattr(os, "process_cpu_count", lambda: 3, raising=False)
    monkeypatch.setattr(
        "azure.ai.agentserver.core._observability_startup._read_text_file",
        lambda _path: None,
    )
    assert effective_cpu_count() == 3.0


def test_auto_uses_sync_on_standard_python(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AGENTSERVER_OBSERVABILITY_STARTUP", raising=False)
    monkeypatch.setattr(
        "azure.ai.agentserver.core._observability_startup.is_free_threaded_runtime",
        lambda: False,
    )
    mode, reason = resolve_observability_startup_mode(True)
    assert mode == "sync"
    assert "not free-threaded" in reason


def test_auto_uses_sync_below_two_cpus(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AGENTSERVER_OBSERVABILITY_STARTUP", raising=False)
    monkeypatch.setattr(
        "azure.ai.agentserver.core._observability_startup.is_free_threaded_runtime",
        lambda: True,
    )
    monkeypatch.setattr(
        "azure.ai.agentserver.core._observability_startup.effective_cpu_count",
        lambda: 1.0,
    )
    mode, reason = resolve_observability_startup_mode(True)
    assert mode == "sync"
    assert reason == "effective CPU capacity is 1"


def test_auto_uses_concurrent_on_free_threaded_two_cpu(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AGENTSERVER_OBSERVABILITY_STARTUP", raising=False)
    monkeypatch.setattr(
        "azure.ai.agentserver.core._observability_startup.is_free_threaded_runtime",
        lambda: True,
    )
    monkeypatch.setattr(
        "azure.ai.agentserver.core._observability_startup.effective_cpu_count",
        lambda: 2.0,
    )
    mode, reason = resolve_observability_startup_mode(True)
    assert mode == "concurrent"
    assert reason == "free-threaded runtime with 2 effective CPUs"


def test_sync_override_preserves_legacy_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGENTSERVER_OBSERVABILITY_STARTUP", "sync")
    mode, reason = resolve_observability_startup_mode(True)
    assert mode == "sync"
    assert reason == "forced by configuration"


def test_concurrent_request_safely_falls_back_on_standard_python(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AGENTSERVER_OBSERVABILITY_STARTUP", "concurrent")
    monkeypatch.setattr(
        "azure.ai.agentserver.core._observability_startup.is_free_threaded_runtime",
        lambda: False,
    )
    mode, reason = resolve_observability_startup_mode(True)
    assert mode == "sync"
    assert "not free-threaded" in reason


def test_custom_callback_remains_synchronous(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGENTSERVER_OBSERVABILITY_STARTUP", "concurrent")
    mode, reason = resolve_observability_startup_mode(False)
    assert mode == "sync"
    assert reason == "custom callback"


def test_concurrent_observability_joins_before_lifespan(monkeypatch: pytest.MonkeyPatch) -> None:
    tracing_started = Event()
    allow_tracing_to_finish = Event()
    tracing_finished = Event()

    def configure_tracing(**_kwargs: object) -> None:
        tracing_started.set()
        allow_tracing_to_finish.wait(timeout=5)
        tracing_finished.set()

    async def run_lifespan(app: AgentServerHost) -> None:
        async with app.router.lifespan_context(app):
            assert tracing_finished.is_set()

    monkeypatch.setattr(
        "azure.ai.agentserver.core._base.resolve_observability_startup_mode",
        lambda _is_default: ("concurrent", "test"),
    )
    monkeypatch.setattr(_tracing, "_configure_console_logging", mock.MagicMock())
    monkeypatch.setattr(_tracing, "_configure_tracing", configure_tracing)
    with mock.patch.dict(os.environ, {}, clear=False):
        app = AgentServerHost()
    assert tracing_started.wait(timeout=5)
    assert app._observability_startup_mode == "concurrent"  # pylint: disable=protected-access
    assert not tracing_finished.is_set()

    allow_tracing_to_finish.set()
    asyncio.run(run_lifespan(app))
