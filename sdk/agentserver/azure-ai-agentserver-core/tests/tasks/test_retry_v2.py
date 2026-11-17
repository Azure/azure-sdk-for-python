# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""RED-first retry conformance tests.

Covers,,, and SC-012. These tests target the
redesigned public surface and are expected to fail until the redesigned
one-shot / multi-turn retry lifecycle is implemented.
"""

from __future__ import annotations

import asyncio
import importlib
import json
import shutil
import uuid
from contextlib import suppress
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest

from azure.ai.agentserver.core.tasks import RetryPolicy, TaskContext, TaskFailed, task


PACKAGE_ROOT = Path(__file__).resolve().parents[2]
STORE_ROOT = PACKAGE_ROOT / ".test-runs" / "resilient-retry-v2"


class RetryV2Error(RuntimeError):
    """Sentinel exception for retry-v2 tests."""


def _unique(prefix: str) -> str:
    return f"retry_v2_{prefix}_{uuid.uuid4().hex}"


def _fast_retry(max_attempts: int) -> RetryPolicy:
    return RetryPolicy(
        max_attempts=max_attempts, initial_delay=timedelta(milliseconds=1), backoff_coefficient=1.0, jitter=False
    )


def _multi_turn_task(**kwargs: Any) -> Any:
    resilient = importlib.import_module("azure.ai.agentserver.core.tasks")
    decorator = getattr(resilient, "multi_turn_task", None)
    assert decorator is not None, " requires public multi_turn_task"
    return decorator(**kwargs)


async def _setup_manager(provider_wrapper: Any | None = None) -> tuple[Any, Any, Any, Path]:
    from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
    from azure.ai.agentserver.core.tasks._manager import TaskManager

    import azure.ai.agentserver.core.tasks._manager as mgr_mod

    store_dir = STORE_ROOT / uuid.uuid4().hex
    store_dir.mkdir(parents=True, exist_ok=False)
    base_provider = LocalFileTaskProvider(store_dir)
    provider = provider_wrapper(base_provider) if provider_wrapper else base_provider
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
    await manager.startup()
    return manager, mgr_mod, provider, store_dir


async def _teardown_manager(manager: Any, mgr_mod: Any, store_dir: Path) -> None:
    with suppress(Exception):
        await manager.shutdown()
    mgr_mod._manager = None
    shutil.rmtree(store_dir, ignore_errors=True)


async def _wait_for_record(manager: Any, task_id: str, *, status: str | None = None, timeout: float = 5.0) -> Any:
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    last_record = None
    while True:
        last_record = await manager.provider.get(task_id)
        if last_record is not None and (status is None or last_record.status == status):
            return last_record
        if loop.time() >= deadline:
            actual = None if last_record is None else last_record.status
            pytest.fail(f"Timed out waiting for {task_id!r} status {status!r}; actual={actual!r}")
        await asyncio.sleep(0.01)


async def _wait_for_deleted(manager: Any, task_id: str, *, timeout: float = 5.0) -> None:
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    while True:
        if await manager.provider.get(task_id) is None:
            return
        if loop.time() >= deadline:
            pytest.fail(f"Timed out waiting for {task_id!r} to be deleted")
        await asyncio.sleep(0.01)


async def _seed_stale_task(
    manager: Any, store_dir: Path, *, task_id: str, retry_attempt: int, input_value: Any
) -> None:
    from azure.ai.agentserver.core.tasks._models import TaskCreateRequest

    await manager.provider.create(
        TaskCreateRequest(
            id=task_id,
            agent_name="test-agent",
            session_id="test-session",
            status="in_progress",
            title="retry-v2-stale",
            payload={"input": input_value, "retry_attempt": retry_attempt},
        )
    )
    task_file = store_dir / "test-agent" / "test-session" / f"{task_id}.json"
    data = json.loads(task_file.read_text())
    data["updated_at"] = "2020-01-01T00:00:00+00:00"
    task_file.write_text(json.dumps(data))


def _assert_exhausted_retry_error(error: dict[str, Any], *, max_attempts: int) -> None:
    assert error["type"] == "exhausted_retries"
    assert error["attempts"] >= max_attempts
    assert isinstance(error["last_error"], str)
    assert isinstance(error["last_error_type"], str)
    assert isinstance(error["traceback"], str)
    assert error["traceback"]


def _patch_payload(patch: Any) -> dict[str, Any]:
    return dict(getattr(patch, "payload", None) or {})


def _captured_updates(provider: Any, task_id: str) -> list[Any]:
    return [call[1] for call in getattr(provider, "update_calls", []) if call[0] == task_id]


class TestPerHandlerRetryBudget:
    """— RetryPolicy is per-handler-invocation."""

    @pytest.mark.asyncio
    async def test_retry_policy_per_attempt(self) -> None:
        attempts: list[int] = []
        task_id = _unique("per_attempt")

        @task(name=_unique("per_attempt_task"), retry=_fast_retry(3))
        async def flaky(ctx: TaskContext[str]) -> str:
            attempts.append(ctx.retry_attempt)
            if ctx.retry_attempt < 2:
                raise RetryV2Error(f"fail attempt {ctx.retry_attempt}")
            return f"ok:{ctx.input}:{ctx.retry_attempt}"

        manager, mgr_mod, _, store_dir = await _setup_manager()
        try:
            run = await flaky.start(task_id=task_id, input="payload")
            assert await asyncio.wait_for(run.result(), timeout=5.0) == "ok:payload:2"
            assert attempts == [0, 1, 2]
        finally:
            await _teardown_manager(manager, mgr_mod, store_dir)

    @pytest.mark.asyncio
    async def test_ctx_retry_attempt_increments(self) -> None:
        observed: list[int] = []
        task_id = _unique("attempt_increments")

        @task(name=_unique("attempt_increments_task"), retry=_fast_retry(3))
        async def flaky(ctx: TaskContext[str]) -> str:
            observed.append(ctx.retry_attempt)
            if len(observed) < 3:
                raise RetryV2Error("retry me")
            return "done"

        manager, mgr_mod, _, store_dir = await _setup_manager()
        try:
            run = await flaky.start(task_id=task_id, input="payload")
            assert await asyncio.wait_for(run.result(), timeout=5.0) == "done"
            assert observed == [0, 1, 2]
        finally:
            await _teardown_manager(manager, mgr_mod, store_dir)

    @pytest.mark.asyncio
    async def test_crash_recovery_does_not_consume_budget(self) -> None:
        observed: list[int] = []
        task_id = _unique("crash_recovery")

        @task(name=_unique("crash_recovery_task"), retry=_fast_retry(3))
        async def recovered(ctx: TaskContext[str]) -> str:
            observed.append(ctx.retry_attempt)
            return f"recovered@{ctx.retry_attempt}"

        manager, mgr_mod, _, store_dir = await _setup_manager()
        try:
            await _seed_stale_task(manager, store_dir, task_id=task_id, retry_attempt=1, input_value="same-attempt")
            run = await recovered.start(task_id=task_id, input="ignored")
            assert await asyncio.wait_for(run.result(), timeout=5.0) == "recovered@1"
            assert observed == [1]
        finally:
            await _teardown_manager(manager, mgr_mod, store_dir)

    @pytest.mark.asyncio
    async def test_suspend_bypasses_retry(self) -> None:
        observed: list[int] = []
        task_id = _unique("suspend_bypasses_retry")

        @_multi_turn_task(name=_unique("suspend_bypasses_retry_task"), retry=_fast_retry(3))
        async def chat(ctx: TaskContext[str]) -> str:
            observed.append(ctx.retry_attempt)
            return f"suspended:{ctx.input}"

        manager, mgr_mod, _, store_dir = await _setup_manager()
        try:
            run = await chat.start(task_id=task_id, input_id="turn-1", input="hello")
            assert await asyncio.wait_for(run.result(), timeout=5.0) == "suspended:hello"
            record = await _wait_for_record(manager, task_id, status="suspended")
            assert (record.payload or {}).get("retry_attempt") is None
            assert observed == [0]
        finally:
            await _teardown_manager(manager, mgr_mod, store_dir)


class TestOneShotPostExhaustion:
    """— One-shot post-retry-exhaustion: record deleted + TaskFailed."""

    @pytest.mark.asyncio
    async def test_one_shot_exhausted_deletes_record(self) -> None:
        task_id = _unique("one_shot_exhausted")

        @task(name=_unique("one_shot_exhausted_task"), retry=_fast_retry(2))
        async def always_fail(ctx: TaskContext[str]) -> str:
            raise RetryV2Error(f"boom {ctx.retry_attempt}")

        manager, mgr_mod, _, store_dir = await _setup_manager()
        try:
            run = await always_fail.start(task_id=task_id, input="payload")
            with pytest.raises(TaskFailed) as exc_info:
                await asyncio.wait_for(run.result(), timeout=5.0)
            await _wait_for_deleted(manager, task_id)
            _assert_exhausted_retry_error(exc_info.value.error, max_attempts=2)
        finally:
            await _teardown_manager(manager, mgr_mod, store_dir)

    @pytest.mark.asyncio
    async def test_one_shot_exhausted_TaskFailed_error_shape(self) -> None:
        task_id = _unique("one_shot_error_shape")

        @task(name=_unique("one_shot_error_shape_task"), retry=_fast_retry(2))
        async def always_fail(ctx: TaskContext[str]) -> str:
            raise RetryV2Error(f"last failure {ctx.retry_attempt}")

        manager, mgr_mod, _, store_dir = await _setup_manager()
        try:
            run = await always_fail.start(task_id=task_id, input="payload")
            with pytest.raises(TaskFailed) as exc_info:
                await asyncio.wait_for(run.result(), timeout=5.0)
            _assert_exhausted_retry_error(exc_info.value.error, max_attempts=2)
        finally:
            await _teardown_manager(manager, mgr_mod, store_dir)


class TestMultiTurnPostExhaustion:
    """— Multi-turn post-retry-exhaustion: suspended + TaskFailed; subsequent turns fresh."""

    @pytest.mark.asyncio
    async def test_multi_turn_exhausted_chain_alive(self) -> None:
        task_id = _unique("multi_exhausted_alive")

        @_multi_turn_task(name=_unique("multi_exhausted_alive_task"), retry=_fast_retry(2))
        async def chat(ctx: TaskContext[dict[str, str]]) -> str:
            if ctx.input["value"] == "fail":
                raise RetryV2Error(f"turn failed {ctx.retry_attempt}")
            return f"ok:{ctx.input['value']}:{ctx.retry_attempt}"

        manager, mgr_mod, _, store_dir = await _setup_manager()
        try:
            failing = await chat.start(task_id=task_id, input_id="turn-1", input={"value": "fail"})
            with pytest.raises(TaskFailed):
                await asyncio.wait_for(failing.result(), timeout=5.0)

            record = await _wait_for_record(manager, task_id, status="suspended")
            assert record.status == "suspended"
            assert record.status != "completed"
            assert await chat.run(task_id=task_id, input_id="turn-2", input={"value": "success"}) == "ok:success:0"
        finally:
            await _teardown_manager(manager, mgr_mod, store_dir)

    @pytest.mark.asyncio
    async def test_multi_turn_subsequent_turn_fresh_retry_budget(self) -> None:
        task_id = _unique("multi_fresh_budget")
        attempts_by_turn: dict[str, list[int]] = {"turn-1": [], "turn-2": []}

        @_multi_turn_task(name=_unique("multi_fresh_budget_task"), retry=_fast_retry(2))
        async def chat(ctx: TaskContext[dict[str, str]]) -> str:
            turn = ctx.input["turn"]
            attempts_by_turn[turn].append(ctx.retry_attempt)
            if turn == "turn-1":
                raise RetryV2Error(f"{turn} exhausts")
            if ctx.retry_attempt == 0:
                raise RetryV2Error(f"{turn} first attempt fails")
            return f"{turn}:ok:{ctx.retry_attempt}"

        manager, mgr_mod, _, store_dir = await _setup_manager()
        try:
            failing = await chat.start(task_id=task_id, input_id="turn-1", input={"turn": "turn-1"})
            with pytest.raises(TaskFailed):
                await asyncio.wait_for(failing.result(), timeout=5.0)

            result = await chat.run(task_id=task_id, input_id="turn-2", input={"turn": "turn-2"})
            assert result == "turn-2:ok:1"
            assert attempts_by_turn == {"turn-1": [0, 1], "turn-2": [0, 1]}
        finally:
            await _teardown_manager(manager, mgr_mod, store_dir)

    @pytest.mark.asyncio
    async def test_multi_turn_exhausted_retry_attempt_cleared(self) -> None:
        task_id = _unique("multi_exhausted_cleared")

        @_multi_turn_task(name=_unique("multi_exhausted_cleared_task"), retry=_fast_retry(2))
        async def chat(ctx: TaskContext[str]) -> str:
            raise RetryV2Error(f"exhaust {ctx.retry_attempt}")

        manager, mgr_mod, _, store_dir = await _setup_manager()
        try:
            run = await chat.start(task_id=task_id, input_id="turn-1", input="fail")
            with pytest.raises(TaskFailed):
                await asyncio.wait_for(run.result(), timeout=5.0)
            record = await _wait_for_record(manager, task_id, status="suspended")
            assert (record.payload or {}).get("retry_attempt") is None
        finally:
            await _teardown_manager(manager, mgr_mod, store_dir)


class TestSC012RetryConformance:
    """SC-012 — retry policy conformance bundle."""

    @pytest.mark.asyncio
    async def test_retry_max_attempts_respected(self) -> None:
        attempts: list[int] = []
        task_id = _unique("max_attempts")

        @task(name=_unique("max_attempts_task"), retry=_fast_retry(3))
        async def always_fail(ctx: TaskContext[str]) -> str:
            attempts.append(ctx.retry_attempt)
            raise RetryV2Error("always")

        manager, mgr_mod, _, store_dir = await _setup_manager()
        try:
            run = await always_fail.start(task_id=task_id, input="payload")
            with pytest.raises(TaskFailed):
                await asyncio.wait_for(run.result(), timeout=5.0)
            assert attempts == [0, 1, 2]
        finally:
            await _teardown_manager(manager, mgr_mod, store_dir)

    @pytest.mark.asyncio
    async def test_retry_attempt_cleared_on_suspend(self) -> None:
        task_id = _unique("cleared_on_suspend")

        @_multi_turn_task(name=_unique("cleared_on_suspend_task"), retry=_fast_retry(2))
        async def chat(ctx: TaskContext[str]) -> str:
            if ctx.retry_attempt == 0:
                raise RetryV2Error("first attempt")
            return "suspended-after-retry"

        manager, mgr_mod, _, store_dir = await _setup_manager()
        try:
            run = await chat.start(task_id=task_id, input_id="turn-1", input="payload")
            assert await asyncio.wait_for(run.result(), timeout=5.0) == "suspended-after-retry"
            record = await _wait_for_record(manager, task_id, status="suspended")
            assert (record.payload or {}).get("retry_attempt") is None
        finally:
            await _teardown_manager(manager, mgr_mod, store_dir)

    @pytest.mark.asyncio
    async def test_no_interim_error_patch_during_retry(self, capturing_provider_factory: Any) -> None:
        task_id = _unique("no_interim_error")
        second_attempt_started = asyncio.Event()
        release_second_attempt = asyncio.Event()

        @task(name=_unique("no_interim_error_task"), retry=_fast_retry(2))
        async def flaky(ctx: TaskContext[str]) -> str:
            if ctx.retry_attempt == 0:
                raise RetryV2Error("first attempt fails")
            second_attempt_started.set()
            await release_second_attempt.wait()
            return "ok"

        manager, mgr_mod, provider, store_dir = await _setup_manager(capturing_provider_factory)
        try:
            run = await flaky.start(task_id=task_id, input="payload")
            await asyncio.wait_for(second_attempt_started.wait(), timeout=5.0)

            for patch in _captured_updates(provider, task_id):
                assert getattr(patch, "error", None) is None
                assert "error" not in _patch_payload(patch)

            release_second_attempt.set()
            assert await asyncio.wait_for(run.result(), timeout=5.0) == "ok"
        finally:
            release_second_attempt.set()
            await _teardown_manager(manager, mgr_mod, store_dir)
