# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
""" input-precondition v2 coverage."""

from __future__ import annotations

import asyncio
import datetime
from pathlib import Path
from typing import Any

import pytest

from azure.ai.agentserver.core.tasks import LastInputIdPreconditionFailed, TaskContext


def _multi_turn_task(*args: Any, **kwargs: Any) -> Any:
    from azure.ai.agentserver.core.tasks import multi_turn_task

    return multi_turn_task(*args, **kwargs)


async def _setup_manager(tmp_path: Path, *, startup: bool = True) -> tuple[Any, Any, Any]:
    from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
    from azure.ai.agentserver.core.tasks._manager import TaskManager
    import azure.ai.agentserver.core.tasks._manager as mgr_mod

    provider = LocalFileTaskProvider(Path(str(tmp_path)))
    config = type(
        "C",
        (),
        {
            "agent_name": "test-agent",
            "session_id": "test-session",
            "agent_version": "1.0.0",
            "is_hosted": False,
        },
    )()
    manager = TaskManager(config=config, provider=provider)
    mgr_mod._manager = manager
    if startup:
        await manager.startup()
    return manager, mgr_mod, provider


async def _teardown_manager(manager: Any, mgr_mod: Any) -> None:
    await manager.shutdown()
    mgr_mod._manager = None


async def _seed_recoverable_record(provider: Any, *, task_id: str, task_name: str, input_value: Any) -> None:
    from azure.ai.agentserver.core.tasks._lease import derive_lease_owner
    from azure.ai.agentserver.core.tasks._models import TaskCreateRequest

    created = await provider.create(
        TaskCreateRequest(
            id=task_id,
            agent_name="test-agent",
            session_id="test-session",
            status="in_progress",
            title=task_name,
            payload={"input": input_value, "last_input_id": "a", "schema_version": "1"},
            tags={"task_name": task_name},
            source={"name": task_name, "type": "agentserver.task"},
            lease_owner=derive_lease_owner("test-agent", "test-session"),
            lease_instance_id="previous-instance",
            lease_duration_seconds=60,
        )
    )
    past = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=10)).isoformat()
    created.lease.expires_at = past
    provider._write_task(created)  # noqa: SLF001


class TestLastInputIdRetention:
    """— _last_input_id preserved across suspend cycles."""

    @pytest.mark.asyncio
    async def test_last_input_id_kept_across_suspend(self, tmp_path: Path) -> None:
        @_multi_turn_task(name="fr029-retention")
        async def handler(ctx: TaskContext[dict[str, str]]) -> str:
            return ctx.input["value"]

        manager, mgr_mod, _ = await _setup_manager(tmp_path)
        try:
            assert await handler.run(task_id="fr029-retain", input={"value": "one"}, input_id="a") == "one"
            record = await manager.provider.get("fr029-retain")
            assert record is not None
            assert record.payload["last_input_id"] == "a"

            assert await handler.run(task_id="fr029-retain", input={"value": "two"}, input_id="b") == "two"
            record = await manager.provider.get("fr029-retain")
            assert record is not None
            assert record.payload["last_input_id"] == "b"
        finally:
            await _teardown_manager(manager, mgr_mod)


class TestIfLastInputIdPrecondition:
    """— LastInputIdPreconditionFailed carries only actual_last_input_id."""

    @pytest.mark.asyncio
    async def test_precondition_mismatch_raises_LastInputIdPreconditionFailed(self, tmp_path: Path) -> None:
        @_multi_turn_task(name="fr076-mismatch")
        async def handler(ctx: TaskContext[str]) -> str:
            return ctx.input

        manager, mgr_mod, _ = await _setup_manager(tmp_path)
        try:
            assert await handler.run(task_id="fr076-mismatch", input="one", input_id="a") == "one"
            with pytest.raises(LastInputIdPreconditionFailed) as excinfo:
                await handler.run(task_id="fr076-mismatch", input="two", input_id="c", if_last_input_id="b")
            assert excinfo.value.actual_last_input_id == "a"
        finally:
            await _teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_LastInputIdPreconditionFailed_no_expected_field(self, tmp_path: Path) -> None:
        @_multi_turn_task(name="fr076-no-expected")
        async def handler(ctx: TaskContext[str]) -> str:
            return ctx.input

        manager, mgr_mod, _ = await _setup_manager(tmp_path)
        try:
            assert await handler.run(task_id="fr076-no-expected", input="one", input_id="a") == "one"
            with pytest.raises(LastInputIdPreconditionFailed) as excinfo:
                await handler.run(task_id="fr076-no-expected", input="two", input_id="c", if_last_input_id="b")
            assert excinfo.value.actual_last_input_id == "a"
            assert not hasattr(excinfo.value, "expected_last_input_id")
        finally:
            await _teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_precondition_match_succeeds(self, tmp_path: Path) -> None:
        @_multi_turn_task(name="fr076-match")
        async def handler(ctx: TaskContext[str]) -> str:
            return ctx.input

        manager, mgr_mod, _ = await _setup_manager(tmp_path)
        try:
            assert await handler.run(task_id="fr076-match", input="one", input_id="a") == "one"
            assert await handler.run(task_id="fr076-match", input="two", input_id="b", if_last_input_id="a") == "two"
        finally:
            await _teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_precondition_None_means_no_check(self, tmp_path: Path) -> None:
        @_multi_turn_task(name="fr076-none-no-check")
        async def handler(ctx: TaskContext[str]) -> str:
            return ctx.input

        manager, mgr_mod, _ = await _setup_manager(tmp_path)
        try:
            assert await handler.run(task_id="fr076-none", input="one", input_id="a") == "one"
            assert await handler.run(task_id="fr076-none", input="two", input_id="c", if_last_input_id=None) == "two"
        finally:
            await _teardown_manager(manager, mgr_mod)


class TestLastInputIdNotRecoveryInputSource:
    """negative rule — _last_input_id is NOT the recovery input source."""

    @pytest.mark.asyncio
    async def test_recovery_uses_payload_input_not_last_input_id(self, tmp_path: Path) -> None:
        observed: list[str] = []

        @_multi_turn_task(name="fr029-recovery-input-source")
        async def handler(ctx: TaskContext[str]) -> str:
            observed.append(ctx.input)
            return ctx.input

        manager, mgr_mod, provider = await _setup_manager(tmp_path, startup=False)
        await _seed_recoverable_record(
            provider, task_id="fr029-recovery", task_name="fr029-recovery-input-source", input_value="b"
        )
        try:
            await manager.startup()
            for _ in range(40):
                if observed:
                    break
                await asyncio.sleep(0.05)
            assert observed == ["b"]
        finally:
            await _teardown_manager(manager, mgr_mod)
