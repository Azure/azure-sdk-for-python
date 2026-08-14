# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""RED-first tests for  persistence rules.

Covers.. plus SC-001. These tests intentionally assert the
new zero-output/error-persistence contract and will fail against the
current output/error persistence behavior.
"""

from __future__ import annotations

import asyncio
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest

import azure.ai.agentserver.core.tasks as resilient
import azure.ai.agentserver.core.tasks._manager as mgr_mod
from azure.ai.agentserver.core.tasks import RetryPolicy, TaskContext, TaskFailed, task
from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
from azure.ai.agentserver.core.tasks._manager import TaskManager
from azure.ai.agentserver.core.tasks._models import TaskCreateRequest, TaskPatchRequest


class PlannedError(RuntimeError):
    """Sentinel exception used by persistence tests."""


class UnserializableOutput:
    """Return value that is intentionally not JSON-serializable."""

    def __init__(self) -> None:
        self.value = object()


class RecordingProvider:
    """TaskProvider spy that keeps raw state around write/delete boundaries."""

    def __init__(self, delegate: LocalFileTaskProvider) -> None:
        self._delegate = delegate
        self.create_results: list[Any] = []
        self.update_calls: list[tuple[str, Any]] = []
        self.update_results: list[Any] = []
        self.delete_calls: list[tuple[str, dict[str, Any]]] = []
        self.before_delete: dict[str, Any] = {}

    async def create(self, request: Any) -> Any:
        result = await self._delegate.create(request)
        self.create_results.append(result)
        return result

    async def get(self, task_id: str) -> Any:
        return await self._delegate.get(task_id)

    async def update(self, task_id: str, patch: Any) -> Any:
        self.update_calls.append((task_id, patch))
        result = await self._delegate.update(task_id, patch)
        self.update_results.append(result)
        return result

    async def delete(self, task_id: str, **kwargs: Any) -> None:
        self.before_delete[task_id] = await self._delegate.get(task_id)
        self.delete_calls.append((task_id, dict(kwargs)))
        await self._delegate.delete(task_id, **kwargs)

    async def list(self, **kwargs: Any) -> Any:
        return await self._delegate.list(**kwargs)


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


async def _setup_manager(
    tmp_path: Path, provider_wrapper: type[RecordingProvider] | None = None
) -> tuple[TaskManager, Any]:
    base_provider = LocalFileTaskProvider(Path(str(tmp_path)))
    provider = provider_wrapper(base_provider) if provider_wrapper else base_provider
    manager = TaskManager(config=_config_stub(), provider=provider)
    mgr_mod._manager = manager
    await manager.startup()
    return manager, provider


async def _teardown_manager(manager: TaskManager) -> None:
    await manager.shutdown()
    mgr_mod._manager = None


async def _wait_for_record(provider: Any, task_id: str, *, status: str | None = None, timeout: float = 5.0) -> Any:
    deadline = asyncio.get_running_loop().time() + timeout
    record = None
    while True:
        record = await provider.get(task_id)
        if record is not None and (status is None or record.status == status):
            return record
        if asyncio.get_running_loop().time() >= deadline:
            actual = None if record is None else record.status
            pytest.fail(f"Timed out waiting for {task_id!r} status {status!r}; actual={actual!r}")
        await asyncio.sleep(0.01)


async def _wait_for_payload_value(provider: Any, task_id: str, key: str, expected: Any, *, timeout: float = 5.0) -> Any:
    deadline = asyncio.get_running_loop().time() + timeout
    while True:
        record = await provider.get(task_id)
        if record is not None and (record.payload or {}).get(key) == expected:
            return record
        if asyncio.get_running_loop().time() >= deadline:
            payload = None if record is None else record.payload
            pytest.fail(f"Timed out waiting for payload[{key!r}] == {expected!r}; payload={payload!r}")
        await asyncio.sleep(0.01)


def _multi_turn_task(**kwargs: Any) -> Any:
    decorator = getattr(resilient, "multi_turn_task", None)
    assert decorator is not None, " requires public multi_turn_task"
    return decorator(**kwargs)


def _payload(record: Any) -> dict[str, Any]:
    return dict(getattr(record, "payload", None) or {})


def _attachment_keys(record: Any) -> set[str]:
    return set((getattr(record, "attachments", None) or {}).keys())


def _assert_no_output_storage(record: Any) -> None:
    payload = _payload(record)
    assert "output" not in payload, f"payload['output'] MUST NOT be persisted; payload={payload!r}"
    assert not any(
        key.startswith("output") for key in _attachment_keys(record)
    ), f"_output attachment MUST NOT be persisted; attachments={getattr(record, 'attachments', None)!r}"


def _assert_no_error_storage(record: Any) -> None:
    payload = _payload(record)
    assert "error" not in payload, f"payload['error'] MUST NOT be persisted; payload={payload!r}"
    assert getattr(record, "error", None) is None, "provider record error field MUST NOT be persisted"


def _assert_no_output_attachment_patches(provider: RecordingProvider, task_id: str) -> None:
    for _, patch in [call for call in provider.update_calls if call[0] == task_id]:
        attachment_patch = getattr(patch, "attachments", None) or {}
        assert not any(
            key.startswith("output") for key in attachment_patch
        ), f"_output attachment MUST NOT be written or deleted; patch={patch!r}"


def _assert_no_error_patches(provider: RecordingProvider, task_id: str) -> None:
    for _, patch in [call for call in provider.update_calls if call[0] == task_id]:
        assert getattr(patch, "error", None) is None, f"PATCH MUST NOT carry error; patch={patch!r}"
        assert "error" not in (
            getattr(patch, "payload", None) or {}
        ), f"PATCH payload MUST NOT carry error; patch={patch!r}"


class TestNoOutputPersistence:
    """/  — no payload["output"] / no _output attachment / no serialization."""

    @pytest.mark.asyncio
    async def test_one_shot_terminal_no_output_written(self, tmp_path: Path) -> None:
        manager, provider = await _setup_manager(tmp_path, RecordingProvider)
        try:

            @task(name="persistence-one-shot-no-output")
            async def one_shot(ctx: TaskContext[dict[str, str]]) -> dict[str, str]:
                return {"echo": ctx.input["value"]}

            await one_shot.run(task_id="one-shot-no-output", input={"value": "x"})

            assert isinstance(provider, RecordingProvider)
            all_records = (
                provider.create_results + provider.update_results + [provider.before_delete["one-shot-no-output"]]
            )
            for record in all_records:
                _assert_no_output_storage(record)
        finally:
            await _teardown_manager(manager)

    @pytest.mark.asyncio
    async def test_one_shot_terminal_no_output_attachment(self, tmp_path: Path) -> None:
        manager, provider = await _setup_manager(tmp_path, RecordingProvider)
        try:

            @task(name="persistence-one-shot-no-output-attachment")
            async def one_shot(ctx: TaskContext[str]) -> str:
                return ctx.input

            await one_shot.run(task_id="one-shot-no-output-attachment", input="x")

            assert isinstance(provider, RecordingProvider)
            before_delete = provider.before_delete["one-shot-no-output-attachment"]
            assert not any(key.startswith("output") for key in _attachment_keys(before_delete))
            _assert_no_output_attachment_patches(provider, "one-shot-no-output-attachment")
        finally:
            await _teardown_manager(manager)

    @pytest.mark.asyncio
    async def test_multi_turn_suspend_no_output_written(self, tmp_path: Path) -> None:
        manager, provider = await _setup_manager(tmp_path)
        try:

            @_multi_turn_task(name="persistence-multi-turn-no-output")
            async def chat(ctx: TaskContext[dict[str, str]]) -> dict[str, str]:
                return {"echo": ctx.input["value"]}

            assert await chat.run(task_id="multi-no-output", input_id="turn-a", input={"value": "x"}) == {"echo": "x"}

            record = await _wait_for_record(provider, "multi-no-output", status="suspended")
            _assert_no_output_storage(record)
        finally:
            await _teardown_manager(manager)

    @pytest.mark.asyncio
    async def test_no_serialization_of_output_value(self, tmp_path: Path) -> None:
        manager, _ = await _setup_manager(tmp_path)
        try:
            returned = UnserializableOutput()

            @task(name="persistence-unserializable-output")
            async def one_shot(ctx: TaskContext[str]) -> UnserializableOutput:
                assert ctx.input == "x"
                return returned

            result = await one_shot.run(task_id="unserializable-output", input="x")

            assert result is returned
        finally:
            await _teardown_manager(manager)


class TestNoErrorPersistence:
    """/  — no payload["error"] / no interim retry error PATCH."""

    @pytest.mark.asyncio
    async def test_one_shot_failure_no_error_written(self, tmp_path: Path) -> None:
        manager, provider = await _setup_manager(tmp_path, RecordingProvider)
        try:

            @task(name="persistence-one-shot-no-error")
            async def fail_once(ctx: TaskContext[str]) -> str:
                raise PlannedError(ctx.input)

            with pytest.raises(TaskFailed):
                await fail_once.run(task_id="one-shot-no-error", input="boom")

            assert isinstance(provider, RecordingProvider)
            _assert_no_error_storage(provider.before_delete["one-shot-no-error"])
            _assert_no_error_patches(provider, "one-shot-no-error")
        finally:
            await _teardown_manager(manager)

    @pytest.mark.asyncio
    async def test_multi_turn_failure_no_error_written(self, tmp_path: Path) -> None:
        manager, provider = await _setup_manager(tmp_path)
        try:

            @_multi_turn_task(name="persistence-multi-turn-no-error")
            async def fail_turn(ctx: TaskContext[str]) -> str:
                raise PlannedError(ctx.input)

            run = await fail_turn.start(task_id="multi-no-error", input_id="turn-a", input="boom")
            with pytest.raises(TaskFailed):
                await asyncio.wait_for(run.result(), timeout=5.0)

            record = await _wait_for_record(provider, "multi-no-error", status="suspended")
            _assert_no_error_storage(record)
        finally:
            await _teardown_manager(manager)

    @pytest.mark.asyncio
    async def test_no_interim_error_patch_between_retries(self, tmp_path: Path) -> None:
        manager, provider = await _setup_manager(tmp_path, RecordingProvider)
        try:
            attempts = 0

            @task(
                name="persistence-no-interim-error",
                retry=RetryPolicy(max_attempts=3, initial_delay=timedelta(0), jitter=False),
            )
            async def always_fails(ctx: TaskContext[str]) -> str:
                nonlocal attempts
                attempts += 1
                raise PlannedError(f"{ctx.input}-{attempts}")

            with pytest.raises(TaskFailed):
                await always_fails.run(task_id="no-interim-error", input="boom")

            assert attempts == 3
            assert isinstance(provider, RecordingProvider)
            _assert_no_error_patches(provider, "no-interim-error")
        finally:
            await _teardown_manager(manager)


class TestInputClearingRules:
    """— payload["input"] cleared at suspend/terminal; NOT mid-handler."""

    @pytest.mark.asyncio
    async def test_multi_turn_input_cleared_at_suspend(self, tmp_path: Path) -> None:
        manager, provider = await _setup_manager(tmp_path)
        try:

            @_multi_turn_task(name="persistence-multi-input-cleared")
            async def chat(ctx: TaskContext[dict[str, str]]) -> str:
                return ctx.input["value"]

            assert await chat.run(task_id="multi-input-cleared", input_id="turn-a", input={"value": "x"}) == "x"

            record = await _wait_for_record(provider, "multi-input-cleared", status="suspended")
            assert _payload(record).get("input") is None
        finally:
            await _teardown_manager(manager)

    @pytest.mark.asyncio
    async def test_input_present_while_in_progress(self, tmp_path: Path) -> None:
        manager, provider = await _setup_manager(tmp_path)
        entered = asyncio.Event()
        release = asyncio.Event()
        try:

            @task(name="persistence-input-present")
            async def one_shot(ctx: TaskContext[dict[str, str]]) -> str:
                entered.set()
                await release.wait()
                return ctx.input["value"]

            run = await one_shot.start(task_id="input-present", input={"value": "recoverable"})
            await asyncio.wait_for(entered.wait(), timeout=5.0)

            record = await _wait_for_record(provider, "input-present", status="in_progress")
            assert _payload(record).get("input") == {"value": "recoverable"}

            release.set()
            await asyncio.wait_for(run.result(), timeout=5.0)
        finally:
            release.set()
            await _teardown_manager(manager)


class TestLastInputIdRetention:
    """— payload["last_input_id"] kept across suspend; NOT used as recovery input source."""

    @pytest.mark.asyncio
    async def test_last_input_id_preserved_across_suspend(self, tmp_path: Path) -> None:
        manager, provider = await _setup_manager(tmp_path)
        try:

            @_multi_turn_task(name="persistence-last-input-id")
            async def chat(ctx: TaskContext[dict[str, str]]) -> str:
                return ctx.input["value"]

            assert await chat.run(task_id="last-input-id", input_id="a", input={"value": "one"}) == "one"
            record = await _wait_for_record(provider, "last-input-id", status="suspended")
            assert _payload(record).get("last_input_id") == "a"

            assert await chat.run(task_id="last-input-id", input_id="b", input={"value": "two"}) == "two"
            record = await _wait_for_record(provider, "last-input-id", status="suspended")
            assert _payload(record).get("last_input_id") == "b"
        finally:
            await _teardown_manager(manager)

    @pytest.mark.asyncio
    async def test_last_input_id_NOT_recovery_input_source(self, tmp_path: Path) -> None:
        manager, provider = await _setup_manager(tmp_path)
        observed: list[tuple[str, Any]] = []
        try:

            @_multi_turn_task(name="persistence-last-input-id-recovery")
            async def chat(ctx: TaskContext[dict[str, str]]) -> str:
                observed.append((ctx.entry_mode, ctx.input))
                return ctx.input["value"]

            await provider.create(
                TaskCreateRequest(
                    id="last-input-id-recovery",
                    agent_name="test-agent",
                    session_id="test-session",
                    status="in_progress",
                    title="last-input-id-recovery",
                    payload={
                        "input": {"value": "active-in-flight"},
                        "last_input_id": "not-the-input",
                        "schema_version": "1",
                    },
                    lease_owner=manager._lease_owner,  # noqa: SLF001
                    lease_instance_id="prior-incarnation",
                    lease_duration_seconds=60,
                    source={"name": "persistence-last-input-id-recovery", "type": "agentserver.task"},
                )
            )

            await manager._recover_stale_tasks()  # noqa: SLF001
            record = await _wait_for_record(provider, "last-input-id-recovery", status="suspended")

            assert observed == [("recovered", {"value": "active-in-flight"})]
            assert _payload(record).get("last_input_id") == "not-the-input"
        finally:
            await _teardown_manager(manager)


class TestRetryAttemptClearing:
    """— payload["retry_attempt"] cleared at suspend/terminal; kept while in_progress."""

    @pytest.mark.asyncio
    async def test_retry_attempt_cleared_at_suspend(self, tmp_path: Path) -> None:
        manager, provider = await _setup_manager(tmp_path)
        try:
            attempts = 0

            @_multi_turn_task(
                name="persistence-retry-cleared",
                retry=RetryPolicy(max_attempts=3, initial_delay=timedelta(0), jitter=False),
            )
            async def chat(ctx: TaskContext[str]) -> str:
                nonlocal attempts
                attempts += 1
                if attempts == 1:
                    raise PlannedError("retry me")
                return f"ok:{ctx.retry_attempt}"

            assert await chat.run(task_id="retry-cleared", input_id="turn-a", input="x") == "ok:1"

            record = await _wait_for_record(provider, "retry-cleared", status="suspended")
            assert _payload(record).get("retry_attempt") is None
        finally:
            await _teardown_manager(manager)

    @pytest.mark.asyncio
    async def test_retry_attempt_kept_while_in_progress(self, tmp_path: Path) -> None:
        manager, provider = await _setup_manager(tmp_path)
        first_attempt = asyncio.Event()
        release_second_attempt = asyncio.Event()
        try:

            @task(
                name="persistence-retry-kept",
                retry=RetryPolicy(max_attempts=3, initial_delay=timedelta(seconds=0.2), jitter=False),
            )
            async def retrying(ctx: TaskContext[str]) -> str:
                if ctx.retry_attempt == 0:
                    first_attempt.set()
                    raise PlannedError("retry me")
                await release_second_attempt.wait()
                return f"ok:{ctx.retry_attempt}"

            run = await retrying.start(task_id="retry-kept", input="x")
            await asyncio.wait_for(first_attempt.wait(), timeout=5.0)

            record = await _wait_for_payload_value(provider, "retry-kept", "retry_attempt", 1)
            assert record.status == "in_progress"

            release_second_attempt.set()
            await asyncio.wait_for(run.result(), timeout=5.0)
        finally:
            release_second_attempt.set()
            await _teardown_manager(manager)

    @pytest.mark.asyncio
    async def test_new_turn_starts_with_retry_attempt_zero(self, tmp_path: Path) -> None:
        manager, _ = await _setup_manager(tmp_path)
        try:
            turn_attempts: list[tuple[str, int]] = []
            first_turn_invocations = 0

            @_multi_turn_task(
                name="persistence-retry-new-turn",
                retry=RetryPolicy(max_attempts=3, initial_delay=timedelta(0), jitter=False),
            )
            async def chat(ctx: TaskContext[str]) -> str:
                nonlocal first_turn_invocations
                turn_attempts.append((ctx.input, ctx.retry_attempt))
                if ctx.input == "first":
                    first_turn_invocations += 1
                    if first_turn_invocations == 1:
                        raise PlannedError("retry first turn")
                return f"{ctx.input}:{ctx.retry_attempt}"

            assert await chat.run(task_id="retry-new-turn", input_id="a", input="first") == "first:1"
            assert await chat.run(task_id="retry-new-turn", input_id="b", input="second") == "second:0"

            assert turn_attempts == [("first", 0), ("first", 1), ("second", 0)]
        finally:
            await _teardown_manager(manager)


class TestSteeringQueueLocation:
    """— steering queue lives in payload["steering"] (no separate record kind)."""

    @pytest.mark.asyncio
    async def test_queued_steerer_stored_in_payload_steering(self, tmp_path: Path) -> None:
        manager, provider = await _setup_manager(tmp_path)
        entered = asyncio.Event()
        release = asyncio.Event()
        try:

            @_multi_turn_task(name="persistence-steering-payload", steerable=True)
            async def chat(ctx: TaskContext[dict[str, str]]) -> str:
                if ctx.input["value"] == "active":
                    entered.set()
                    await release.wait()
                return ctx.input["value"]

            active = await chat.start(task_id="steering-payload", input_id="a", input={"value": "active"})
            await asyncio.wait_for(entered.wait(), timeout=5.0)
            queued_1 = await chat.start(task_id="steering-payload", input_id="b", input={"value": "queued-1"})
            queued_2 = await chat.start(task_id="steering-payload", input_id="c", input={"value": "queued-2"})

            record = await _wait_for_record(provider, "steering-payload", status="in_progress")
            steering = _payload(record).get("steering") or {}
            assert steering.get("pending_inputs") == [{"value": "queued-1"}, {"value": "queued-2"}]

            release.set()
            assert await asyncio.wait_for(active.result(), timeout=5.0) == "active"
            assert await asyncio.wait_for(queued_1.result(), timeout=5.0) == "queued-1"
            assert await asyncio.wait_for(queued_2.result(), timeout=5.0) == "queued-2"
        finally:
            release.set()
            await _teardown_manager(manager)

    @pytest.mark.asyncio
    async def test_no_separate_pending_record(self, tmp_path: Path) -> None:
        manager, provider = await _setup_manager(tmp_path)
        entered = asyncio.Event()
        release = asyncio.Event()
        try:

            @_multi_turn_task(name="persistence-no-pending-record", steerable=True)
            async def chat(ctx: TaskContext[dict[str, str]]) -> str:
                if ctx.input["value"] == "active":
                    entered.set()
                    await release.wait()
                return ctx.input["value"]

            await chat.start(task_id="no-pending-record", input_id="a", input={"value": "active"})
            await asyncio.wait_for(entered.wait(), timeout=5.0)
            await chat.start(task_id="no-pending-record", input_id="b", input={"value": "queued-1"})
            await chat.start(task_id="no-pending-record", input_id="c", input={"value": "queued-2"})

            records = await provider.list(agent_name="test-agent", session_id="test-session")
            assert {record.id for record in records} == {"no-pending-record"}
            assert len(records) == 1
            assert "steering" in _payload(records[0])
        finally:
            release.set()
            await _teardown_manager(manager)


class TestSC001ZeroPersistence:
    """SC-001 — record disappears the moment one-shot handler exits."""

    @pytest.mark.asyncio
    async def test_one_shot_record_count_unchanged_before_after(self, tmp_path: Path) -> None:
        manager, provider = await _setup_manager(tmp_path)
        try:
            before = await provider.list(agent_name="test-agent", session_id="test-session")

            @task(name="persistence-sc001")
            async def one_shot(ctx: TaskContext[str]) -> str:
                return f"ok:{ctx.input}"

            await one_shot.run(task_id="sc001-zero-persistence", input="x")

            after = await provider.list(agent_name="test-agent", session_id="test-session")
            assert len(after) == len(before)
            assert {record.id for record in after} == {record.id for record in before}
        finally:
            await _teardown_manager(manager)
