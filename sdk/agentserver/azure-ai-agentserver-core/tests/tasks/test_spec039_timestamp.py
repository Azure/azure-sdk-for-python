# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Spec 039 T1 — ``payload.turn_started_at`` timestamp format parity.

Every persisted task-record timestamp (``created_at`` / ``updated_at`` /
``started_at`` / ``lease.*``) uses ``datetime.isoformat()`` → a ``+00:00``
offset. ``turn_started_at`` was the lone exception, emitting a ``Z`` suffix
via ``strftime(...) + "Z"`` — internally inconsistent with the rest of the
Python record and divergent from the .NET port (which uses ``+00:00``). T1
normalizes it to ``+00:00`` while keeping the read path tolerant of legacy
``Z`` records (no migration).
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

import azure.ai.agentserver.core.tasks._manager as mgr_mod
from azure.ai.agentserver.core.tasks import TaskContext, task
from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
from azure.ai.agentserver.core.tasks._manager import TaskManager


def _config_stub() -> Any:
    return type(
        "C",
        (),
        {
            "agent_name": "research-agent",
            "session_id": "sess-1",
            "agent_version": "1.0.0",
            "is_hosted": False,
        },
    )()


def test_utc_now_iso_uses_offset_not_z() -> None:
    """The shared timestamp helper emits a ``+00:00`` offset, not ``Z``."""
    value = mgr_mod._utc_now_iso()
    assert value.endswith("+00:00"), value
    assert not value.endswith("Z"), value
    # Parses as an aware datetime.
    assert datetime.fromisoformat(value).tzinfo is not None


@pytest.mark.asyncio
async def test_turn_started_at_persisted_with_offset(tmp_path) -> None:
    """A created task's ``payload.turn_started_at`` ends in ``+00:00`` and
    matches the offset spelling of the other record timestamps."""
    captured: dict[str, Any] = {}

    class _CreateSpy(LocalFileTaskProvider):
        async def create(self, request):  # type: ignore[override]
            captured["payload"] = dict(request.payload or {})
            return await super().create(request)

    provider = _CreateSpy(Path(str(tmp_path)))
    manager = TaskManager(config=_config_stub(), provider=provider)
    mgr_mod._manager = manager
    await manager.startup()
    try:

        @task(name="s039-ts")
        async def handler(ctx: TaskContext[str]) -> str:
            return "ok"

        run = await handler.start(input="hi", task_id="s039-ts-1")
        await run.result()

        ts = captured["payload"].get(mgr_mod._TURN_STARTED_AT_KEY)
        assert isinstance(ts, str) and ts.endswith("+00:00"), ts
        assert not ts.endswith("Z"), ts
    finally:
        await manager.shutdown()
        mgr_mod._manager = None


def test_parse_turn_started_at_accepts_legacy_z_and_new_offset() -> None:
    """Read-compat: legacy ``…Z`` and new ``…+00:00`` values parse to the
    identical instant (no migration required for in-flight records)."""
    legacy_z = "2026-07-14T16:36:18.132977Z"
    new_offset = "2026-07-14T16:36:18.132977+00:00"
    parsed_legacy = mgr_mod._parse_turn_started_at(legacy_z)
    parsed_new = mgr_mod._parse_turn_started_at(new_offset)
    assert parsed_legacy is not None and parsed_new is not None
    assert parsed_legacy == parsed_new
