# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""RED-first tests for  multi-turn return/raise semantics.

Covers,,,,,,,
, plus SC-003 and SC-010. These tests intentionally target the
new ``@multi_turn_task`` primitive and fail RED until  lands.
"""

from __future__ import annotations

import asyncio
import gc
import logging
from pathlib import Path
from typing import Any, cast

import pytest

try:
    from azure.ai.agentserver.core.tasks import (
        TaskCancelled,
        TaskContext,
        TaskFailed,
        multi_turn_task,
        task,
        TaskErrorDict,
    )

    _NEW_SURFACE_AVAILABLE = True
except ImportError:
    _NEW_SURFACE_AVAILABLE = False
    from azure.ai.agentserver.core.tasks import TaskCancelled, TaskContext, TaskFailed, task

    multi_turn_task = None  # type: ignore[assignment]
    TaskErrorDict = None  # type: ignore[assignment]

pytestmark = pytest.mark.skipif(
    not _NEW_SURFACE_AVAILABLE, reason=": requires `multi_turn_task` / `TaskErrorDict` (RED until Phase 2-5)"
)


class MyError(RuntimeError):
    """Sentinel handler failure for multi-turn raise tests."""


async def _setup_manager(tmp_path: Path, provider_wrapper: Any | None = None) -> tuple[Any, Any, Any]:
    from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
    from azure.ai.agentserver.core.tasks._manager import TaskManager
    import azure.ai.agentserver.core.tasks._manager as mgr_mod

    base_provider = LocalFileTaskProvider(Path(str(tmp_path)))
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
    return manager, mgr_mod, provider


async def _teardown_manager(manager: Any, mgr_mod: Any) -> None:
    await manager.shutdown()
    mgr_mod._manager = None


async def _wait_for_record(manager: Any, task_id: str, *, status: str | None = None, timeout: float = 5.0) -> Any:
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    while True:
        record = await manager.provider.get(task_id)
        if record is not None and (status is None or record.status == status):
            return record
        if loop.time() >= deadline:
            actual = None if record is None else record.status
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


def _patch_payload(patch: Any) -> dict[str, Any]:
    return dict(getattr(patch, "payload", None) or {})


def _captured_updates(provider: Any, task_id: str) -> list[tuple[int, Any]]:
    return [(index, call[1]) for index, call in enumerate(getattr(provider, "update_calls", [])) if call[0] == task_id]


def _find_suspend_patch(provider: Any, task_id: str) -> tuple[int, Any]:
    for index, patch in _captured_updates(provider, task_id):
        payload = _patch_payload(patch)
        if (
            getattr(patch, "status", None) == "suspended"
            and getattr(patch, "suspension_reason", None) == "run_completion"
            and payload.get("input") is None
        ):
            return index, patch
    pytest.fail(f"No  suspend patch captured for {task_id!r}")


def _exception_public_fields(exc: BaseException) -> set[str]:
    fields = set(getattr(exc, "__dict__", {}))
    for cls in type(exc).mro():
        slots = getattr(cls, "__slots__", ())
        if isinstance(slots, str):
            slots = slots
        for slot in slots:
            if isinstance(slot, str) and not slot.startswith("_") and hasattr(exc, slot):
                fields.add(slot)
    return fields


class TestReturnIsImplicitSuspend:
    """— Multi-turn handler ``return X`` is implicit suspend."""

    @pytest.mark.asyncio
    async def test_multi_turn_return_X_suspends_chain(self, tmp_path: Path) -> None:
        manager, mgr_mod, _ = await _setup_manager(tmp_path)
        try:
            seen: list[tuple[str, str]] = []

            @multi_turn_task(name="return-x-chain")
            async def chat(ctx: TaskContext[dict[str, str]]) -> dict[str, str]:
                seen.append((ctx.entry_mode, ctx.input_id))
                return {"echo": ctx.input["value"], "input_id": ctx.input_id}

            result1 = await chat.run(task_id="return-x", input_id="turn-1", input={"value": "one"})

            assert result1 == {"echo": "one", "input_id": "turn-1"}
            record = await _wait_for_record(manager, "return-x", status="suspended")
            assert record.suspension_reason == "run_completion"
            assert (record.payload or {}).get("input") is None

            run2 = await chat.start(task_id="return-x", input_id="turn-2", input={"value": "two"})
            assert await run2.result() == {"echo": "two", "input_id": "turn-2"}
            assert seen == [("fresh", "turn-1"), ("resumed", "turn-2")]
        finally:
            await _teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_multi_turn_return_None_suspends_chain(self, tmp_path: Path) -> None:
        manager, mgr_mod, _ = await _setup_manager(tmp_path)
        try:
            inputs: list[str] = []

            @multi_turn_task(name="return-none-chain")
            async def chat(ctx: TaskContext[dict[str, str]]) -> None:
                inputs.append(ctx.input["value"])
                return None

            assert await chat.run(task_id="return-none", input_id="turn-1", input={"value": "one"}) is None

            record = await _wait_for_record(manager, "return-none", status="suspended")
            assert record.suspension_reason == "run_completion"
            assert (record.payload or {}).get("input") is None

            run2 = await chat.start(task_id="return-none", input_id="turn-2", input={"value": "two"})
            assert await run2.result() is None
            assert inputs == ["one", "two"]
        finally:
            await _teardown_manager(manager, mgr_mod)


class TestMultiTurnRaiseDoesNotKillChain:
    """+  — Multi-turn raise → suspended; chain stays alive."""

    @pytest.mark.asyncio
    async def test_handler_raise_transitions_to_suspended(
        self, tmp_path: Path, capturing_provider_factory: Any
    ) -> None:
        manager, mgr_mod, provider = await _setup_manager(tmp_path, capturing_provider_factory)
        try:
            entered = asyncio.Event()
            release = asyncio.Event()

            @multi_turn_task(name="raise-suspends-chain", steerable=True)
            async def chat(ctx: TaskContext[dict[str, str]]) -> str:
                if ctx.input["value"] == "fail":
                    entered.set()
                    await release.wait()
                    raise MyError("planned failure")
                return ctx.input["value"]

            failing = await chat.start(task_id="raise-suspend", input_id="turn-1", input={"value": "fail"})
            await asyncio.wait_for(entered.wait(), timeout=5.0)
            queued = await chat.start(task_id="raise-suspend", input_id="turn-2", input={"value": "queued"})

            release.set()
            with pytest.raises(TaskFailed):
                await asyncio.wait_for(failing.result(), timeout=5.0)
            assert await asyncio.wait_for(queued.result(), timeout=5.0) == "queued"

            record = await _wait_for_record(manager, "raise-suspend", status="suspended")
            payload = record.payload or {}
            assert record.status == "suspended"
            assert record.suspension_reason == "run_completion"
            assert payload.get("input") is None
            assert payload.get("retry_attempt") is None
            assert "error" not in payload
            assert record.error is None
            assert payload.get("last_input_id") == "turn-2"

            _, failure_patch = _find_suspend_patch(provider, "raise-suspend")
            failure_payload = _patch_payload(failure_patch)
            assert failure_payload.get("input") is None
            assert failure_payload.get("retry_attempt") is None
            assert "error" not in failure_payload
            if "steering" in failure_payload:
                pending = failure_payload["steering"].get("pending_inputs", [])
                assert pending, "failure patch must not drop queued steering inputs"
        finally:
            await _teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_subsequent_run_after_raise_succeeds(self, tmp_path: Path) -> None:
        manager, mgr_mod, _ = await _setup_manager(tmp_path)
        try:
            modes: list[str] = []

            @multi_turn_task(name="raise-then-run-chain")
            async def chat(ctx: TaskContext[dict[str, str]]) -> str:
                modes.append(ctx.entry_mode)
                if ctx.input["value"] == "fail":
                    raise MyError("turn failed")
                return f"ok:{ctx.input['value']}"

            failing = await chat.start(task_id="raise-then-run", input_id="turn-1", input={"value": "fail"})
            with pytest.raises(TaskFailed):
                await asyncio.wait_for(failing.result(), timeout=5.0)

            record = await _wait_for_record(manager, "raise-then-run", status="suspended")
            assert record.status == "suspended"

            result = await chat.run(task_id="raise-then-run", input_id="turn-2", input={"value": "success"})
            assert result == "ok:success"
            assert modes == ["fresh", "resumed"]
        finally:
            await _teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_chain_alive_after_N_raises(self, tmp_path: Path) -> None:
        manager, mgr_mod, _ = await _setup_manager(tmp_path)
        try:
            seen: list[tuple[str, str]] = []

            @multi_turn_task(name="many-raises-chain")
            async def chat(ctx: TaskContext[dict[str, str]]) -> str:
                seen.append((ctx.input["value"], ctx.entry_mode))
                if ctx.input["value"].startswith("fail-"):
                    raise MyError(ctx.input["value"])
                return f"ok:{ctx.input['value']}"

            for index in range(5):
                failing = await chat.start(
                    task_id="many-raises", input_id=f"fail-{index}", input={"value": f"fail-{index}"}
                )
                with pytest.raises(TaskFailed):
                    await asyncio.wait_for(failing.result(), timeout=5.0)

                result = await chat.run(
                    task_id="many-raises", input_id=f"success-{index}", input={"value": f"success-{index}"}
                )
                assert result == f"ok:success-{index}"
                record = await _wait_for_record(manager, "many-raises", status="suspended")
                assert (record.payload or {}).get("input") is None

            assert [value for value, _ in seen] == [
                item for index in range(5) for item in (f"fail-{index}", f"success-{index}")
            ]
        finally:
            await _teardown_manager(manager, mgr_mod)


class TestFailingTurnResult:
    """— failing turn's ``TaskRun.result`` raises the new taxonomy."""

    @pytest.mark.asyncio
    async def test_handler_raise_resolves_with_TaskFailed(self, tmp_path: Path) -> None:
        manager, mgr_mod, _ = await _setup_manager(tmp_path)
        try:

            @multi_turn_task(name="taskfailed-result-chain")
            async def chat(ctx: TaskContext[dict[str, str]]) -> str:
                raise MyError(f"bad input: {ctx.input['value']}")

            run = await chat.start(task_id="taskfailed-result", input_id="turn-1", input={"value": "boom"})
            with pytest.raises(TaskFailed) as exc_info:
                await asyncio.wait_for(run.result(), timeout=5.0)

            assert exc_info.value.error["type"] == "MyError"
            assert exc_info.value.error["message"] == "bad input: boom"
            assert "MyError" in exc_info.value.error["traceback"]
            assert exc_info.value.__cause__ is None
        finally:
            await _teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_handler_CancelledError_resolves_with_TaskCancelled(self, tmp_path: Path) -> None:
        manager, mgr_mod, _ = await _setup_manager(tmp_path)
        try:

            @multi_turn_task(name="cancelled-result-chain")
            async def chat(ctx: TaskContext[dict[str, str]]) -> str:
                raise asyncio.CancelledError()

            run = await chat.start(task_id="cancelled-result", input_id="turn-1", input={"value": "cancel"})
            with pytest.raises(TaskCancelled) as exc_info:
                await asyncio.wait_for(run.result(), timeout=5.0)

            assert exc_info.value.args == ()
            assert _exception_public_fields(exc_info.value) == set()
        finally:
            await _teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_TaskFailed_error_dict_shape(self, tmp_path: Path) -> None:
        manager, mgr_mod, _ = await _setup_manager(tmp_path)
        try:

            @multi_turn_task(name="taskfailed-shape-chain")
            async def chat(ctx: TaskContext[dict[str, str]]) -> str:
                raise MyError("shape check")

            run = await chat.start(task_id="taskfailed-shape", input_id="turn-1", input={"value": "boom"})
            with pytest.raises(TaskFailed) as exc_info:
                await asyncio.wait_for(run.result(), timeout=5.0)

            error = cast(TaskErrorDict, exc_info.value.error)
            assert set(error) == {"type", "message", "traceback"}
            assert error["type"] == "MyError"
            assert error["message"] == "shape check"
            assert isinstance(error["traceback"], str)
            assert "MyError" in error["traceback"]
            assert not hasattr(exc_info.value, "task_id")
        finally:
            await _teardown_manager(manager, mgr_mod)


class TestQueuedSteererPromotion:
    """— On multi-turn raise, queued steerers PROMOTE."""

    @pytest.mark.asyncio
    async def test_queued_steerer_promotes_on_raise(self, tmp_path: Path) -> None:
        manager, mgr_mod, _ = await _setup_manager(tmp_path)
        try:
            entered = asyncio.Event()
            release = asyncio.Event()
            observed: list[dict[str, Any]] = []

            @multi_turn_task(name="queued-promotes-chain", steerable=True)
            async def chat(ctx: TaskContext[dict[str, str]]) -> dict[str, Any]:
                observed.append(
                    {
                        "value": ctx.input["value"],
                        "entry_mode": ctx.entry_mode,
                        "input_id": ctx.input_id,
                    }
                )
                if ctx.input["value"] == "fail":
                    entered.set()
                    await release.wait()
                    raise MyError("first turn failed")
                return observed[-1]

            failing = await chat.start(task_id="queued-promotes", input_id="turn-1", input={"value": "fail"})
            await asyncio.wait_for(entered.wait(), timeout=5.0)
            queued = await chat.start(task_id="queued-promotes", input_id="turn-2", input={"value": "queued"})

            release.set()
            with pytest.raises(TaskFailed):
                await asyncio.wait_for(failing.result(), timeout=5.0)

            assert await asyncio.wait_for(queued.result(), timeout=5.0) == {
                "value": "queued",
                "entry_mode": "resumed",
                "input_id": "turn-2",
            }
            assert observed == [
                {"value": "fail", "entry_mode": "fresh", "input_id": "turn-1"},
                {"value": "queued", "entry_mode": "resumed", "input_id": "turn-2"},
            ]
        finally:
            await _teardown_manager(manager, mgr_mod)


class TestOneShotRaise:
    """— One-shot raise → completed + deleted + TaskFailed."""

    @pytest.mark.asyncio
    async def test_one_shot_raise_deletes_record(self, tmp_path: Path) -> None:
        manager, mgr_mod, _ = await _setup_manager(tmp_path)
        try:

            @task(name="one-shot-raise")
            async def fail_once(ctx: TaskContext[dict[str, str]]) -> str:
                raise MyError(ctx.input["value"])

            run = await fail_once.start(task_id="one-shot-raise-id", input_id="one-shot-input", input={"value": "boom"})
            with pytest.raises(TaskFailed):
                await asyncio.wait_for(run.result(), timeout=5.0)

            await _wait_for_deleted(manager, "one-shot-raise-id")
        finally:
            await _teardown_manager(manager, mgr_mod)


class TestStructuredFailureLog:
    """— Framework emits structured failure log/telemetry for failures."""

    @pytest.mark.asyncio
    async def test_failure_emits_structured_log_event(self, tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level(logging.ERROR, logger="azure.ai.agentserver.tasks")
        manager, mgr_mod, _ = await _setup_manager(tmp_path)
        try:

            @multi_turn_task(name="structured-log-chain")
            async def chat(ctx: TaskContext[dict[str, str]]) -> str:
                raise MyError("log me")

            await chat.start(task_id="structured-log", input_id="turn-1", input={"value": "boom"})
            await _wait_for_record(manager, "structured-log", status="suspended")

            failure_records = [
                record
                for record in caplog.records
                if getattr(record, "event", None) == "resilient_task_handler_failure"
                or getattr(record, "event_name", None) == "resilient_task_handler_failure"
            ]
            assert len(failure_records) == 1
            record = failure_records[0]
            assert getattr(record, "task_id", None) == "structured-log"
            assert getattr(record, "input_id", None) == "turn-1"
            assert getattr(record, "error_type", None) == "MyError"
            assert getattr(record, "error_message", None) == "log me"
        finally:
            await _teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_failure_consumes_future_exception(self, tmp_path: Path) -> None:
        manager, mgr_mod, _ = await _setup_manager(tmp_path)
        loop = asyncio.get_running_loop()
        prior_handler = loop.get_exception_handler()
        contexts: list[dict[str, Any]] = []

        def capture_unhandled(loop: asyncio.AbstractEventLoop, context: dict[str, Any]) -> None:
            contexts.append(context)

        loop.set_exception_handler(capture_unhandled)
        try:

            @multi_turn_task(name="unawaited-failure-chain")
            async def chat(ctx: TaskContext[dict[str, str]]) -> str:
                raise MyError("nobody awaits this")

            handle = await chat.start(task_id="unawaited-failure", input_id="turn-1", input={"value": "boom"})
            del handle
            await _wait_for_record(manager, "unawaited-failure", status="suspended")

            for _ in range(3):
                gc.collect()
                await asyncio.sleep(0)

            assert not any("exception was never retrieved" in str(context.get("message", "")) for context in contexts)
        finally:
            loop.set_exception_handler(prior_handler)
            await _teardown_manager(manager, mgr_mod)


class TestSevenStepOrdering:
    """Ordering on multi-turn handler raise."""

    @pytest.mark.asyncio
    async def test_current_TaskFailed_resolves_before_queued_promotes(self, tmp_path: Path) -> None:
        manager, mgr_mod, _ = await _setup_manager(tmp_path)
        try:
            entered = asyncio.Event()
            release = asyncio.Event()
            current_failed_observed = asyncio.Event()
            events: list[str] = []

            @multi_turn_task(name="current-before-queued-chain", steerable=True)
            async def chat(ctx: TaskContext[dict[str, str]]) -> str:
                if ctx.input["value"] == "fail":
                    events.append("handler-a-entered")
                    entered.set()
                    await release.wait()
                    raise MyError("fail before queued")
                assert current_failed_observed.is_set(), "queued handler ran before current TaskFailed was observed"
                events.append("handler-b-entered")
                return "queued-ok"

            failing = await chat.start(task_id="current-before-queued", input_id="turn-1", input={"value": "fail"})
            await asyncio.wait_for(entered.wait(), timeout=5.0)

            async def observe_failure() -> None:
                with pytest.raises(TaskFailed):
                    await failing.result()
                events.append("caller-a-failed")
                current_failed_observed.set()

            observer = asyncio.create_task(observe_failure())
            await asyncio.sleep(0)
            queued = await chat.start(task_id="current-before-queued", input_id="turn-2", input={"value": "queued"})

            release.set()
            await asyncio.wait_for(observer, timeout=5.0)
            assert await asyncio.wait_for(queued.result(), timeout=5.0) == "queued-ok"
            assert events.index("caller-a-failed") < events.index("handler-b-entered")
        finally:
            await _teardown_manager(manager, mgr_mod)
