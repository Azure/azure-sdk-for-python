# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Spec 038 — task-record schema cleanup.

Covers the four task-record changes:

1. De-``_``-prefixed wire keys (``task_name`` tag; ``schema_version`` /
   ``last_input_id`` / ``turn_started_at`` / ``retry_attempt`` / ``steering``
   payload keys; ``input`` / ``steering_input_`` / ``output`` attachment keys).
2. ``source.hosting_environment`` stamped from ``FOUNDRY_HOSTING_ENVIRONMENT``.
3. ``payload.schema_version`` stamped at create (in ``payload`` so it stays
   PATCH-mutable for a future migrator).
4. One-time legacy cleanup: a stale task lacking ``payload.schema_version`` is
   deleted (not recovered) by the recovery scan.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

import azure.ai.agentserver.core.tasks._manager as mgr_mod
from azure.ai.agentserver.core.tasks import TaskContext, task
from azure.ai.agentserver.core.tasks._attachments import (
    _ATTACHMENT_REF_KEY,
    _FUNCTION_INPUT_KEY,
    _OUTPUT_KEY,
    _STEERING_INPUT_KEY_PREFIX,
)
from azure.ai.agentserver.core.tasks._decorator import (
    _LAST_INPUT_ID_PAYLOAD_KEY,
    _RESERVED_TAG_KEYS,
    _strip_reserved_tags,
)
from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
from azure.ai.agentserver.core.tasks._manager import TaskManager
from azure.ai.agentserver.core.tasks._models import TaskCreateRequest


def _config_stub() -> Any:
    return type(
        "C",
        (),
        {
            "agent_name": "test-agent",
            "session_id": "test-session",
            "agent_version": "1.0.0",
            "is_hosted": False,
        },
    )()


async def _setup_manager(tmp_path: Path) -> tuple[TaskManager, Any]:
    provider = LocalFileTaskProvider(Path(str(tmp_path)))
    manager = TaskManager(config=_config_stub(), provider=provider)
    mgr_mod._manager = manager
    await manager.startup()
    return manager, provider


async def _teardown_manager(manager: TaskManager) -> None:
    await manager.shutdown()
    mgr_mod._manager = None


# --------------------------------------------------------------------------- #
# Change #1 — wire-key rename (no leading underscore except the discriminator)
# --------------------------------------------------------------------------- #


def test_reserved_wire_keys_have_no_underscore_prefix() -> None:
    assert mgr_mod._TAG_TASK_NAME == "task_name"
    assert mgr_mod._TURN_STARTED_AT_KEY == "turn_started_at"
    assert mgr_mod._SCHEMA_VERSION_KEY == "schema_version"
    assert _FUNCTION_INPUT_KEY == "input"
    assert _STEERING_INPUT_KEY_PREFIX == "steering_input_"
    assert _OUTPUT_KEY == "output"
    assert _LAST_INPUT_ID_PAYLOAD_KEY == "last_input_id"
    # The attachment-ref discriminator is the ONE key that keeps its markers.
    assert _ATTACHMENT_REF_KEY == "__attachment_ref__"


# --------------------------------------------------------------------------- #
# Change #1 — reserved-tag guard is now an exact-key set, not a prefix
# --------------------------------------------------------------------------- #


def test_reserved_tag_keys_is_exact_set() -> None:
    assert _RESERVED_TAG_KEYS == frozenset({"task_name"})


def test_strip_reserved_tags_drops_exact_reserved_key() -> None:
    out = _strip_reserved_tags({"task_name": "x", "keep": "y"})
    assert out == {"keep": "y"}


def test_strip_reserved_tags_keeps_old_underscore_style_keys() -> None:
    # The old ``_task_``-prefixed guard is gone: a developer key that merely
    # *starts with* the old prefix is no longer stripped (only exact matches).
    out = _strip_reserved_tags({"_task_custom": "v", "task_named": "w"})
    assert out == {"_task_custom": "v", "task_named": "w"}


# --------------------------------------------------------------------------- #
# Changes #2 / #3 — source.hosting_environment + payload.schema_version at create
# --------------------------------------------------------------------------- #


def test_build_source_includes_hosting_not_schema(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(mgr_mod._ENV_HOSTING, "AzureFoundry")
    src = TaskManager._build_source("my-task")
    assert src["type"] == "agentserver.task"
    assert src["name"] == "my-task"
    assert src["hosting_environment"] == "AzureFoundry"
    # schema_version is NOT in source (it must stay PATCH-mutable in payload).
    assert "schema_version" not in src


def test_build_source_hosting_environment_empty_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(mgr_mod._ENV_HOSTING, raising=False)
    src = TaskManager._build_source("my-task")
    assert src["hosting_environment"] == ""


@pytest.mark.asyncio
async def test_created_task_stamps_schema_version_in_payload(tmp_path) -> None:
    captured: dict[str, Any] = {}

    class _CreateSpy(LocalFileTaskProvider):
        async def create(self, request):  # type: ignore[override]
            captured["payload"] = dict(request.payload or {})
            captured["source"] = dict(request.source or {})
            return await super().create(request)

    provider = _CreateSpy(Path(str(tmp_path)))
    manager = TaskManager(config=_config_stub(), provider=provider)
    mgr_mod._manager = manager
    await manager.startup()
    try:

        @task(name="s038-create")
        async def handler(ctx: TaskContext[str]) -> str:
            return "ok"

        run = await handler.start(input="hi", task_id="s038-create-1")
        await run.result()

        # schema_version stamped in payload (mutable bucket) at create.
        assert captured["payload"].get("schema_version") == "1"
        # hosting_environment stamped in source (immutable), empty in local/dev.
        assert captured["source"].get("hosting_environment") == ""
        assert captured["source"].get("type") == "agentserver.task"
    finally:
        await _teardown_manager(manager)


# --------------------------------------------------------------------------- #
# Change #4 — one-time legacy cleanup deletes schema-less stale tasks
# --------------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_recovery_deletes_task_without_schema_version(tmp_path) -> None:
    manager, provider = await _setup_manager(tmp_path)
    invoked: list[str] = []
    try:

        @task(name="s038-legacy")
        async def handler(ctx: TaskContext[str]) -> str:
            invoked.append("ran")
            return "ok"

        # A pre-Spec-038 persisted task: NO payload.schema_version.
        await provider.create(
            TaskCreateRequest(
                id="legacy-1",
                agent_name=manager._config.agent_name,
                session_id=manager._config.session_id,
                status="in_progress",
                title="legacy",
                payload={"input": "old"},
                source={"name": "s038-legacy", "type": "agentserver.task"},
                lease_owner=manager._lease_owner,
                lease_instance_id="prior",
                lease_duration_seconds=60,
            )
        )

        await manager._recover_stale_tasks()

        # It must be DELETED, not recovered/re-invoked.
        assert await provider.get("legacy-1") is None
        assert invoked == []
    finally:
        await _teardown_manager(manager)


@pytest.mark.asyncio
async def test_recovery_keeps_task_with_schema_version(tmp_path) -> None:
    manager, provider = await _setup_manager(tmp_path)
    try:

        @task(name="s038-current")
        async def handler(ctx: TaskContext[str]) -> str:
            return "ok"

        await provider.create(
            TaskCreateRequest(
                id="current-1",
                agent_name=manager._config.agent_name,
                session_id=manager._config.session_id,
                status="in_progress",
                title="current",
                payload={"input": "x", "schema_version": "1"},
                source={"name": "s038-current", "type": "agentserver.task"},
                lease_owner=manager._lease_owner,
                lease_instance_id="prior",
                lease_duration_seconds=60,
            )
        )

        await manager._recover_stale_tasks()

        # A current-schema task must NOT be deleted by the cleanup.
        assert await provider.get("current-1") is not None
    finally:
        await _teardown_manager(manager)
