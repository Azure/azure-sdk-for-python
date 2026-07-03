"""RED-first cancellation/deletion/shutdown matrix tests for  SC-014."""

from __future__ import annotations

import asyncio
import importlib
import shutil
import uuid
from contextlib import suppress
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest

from azure.ai.agentserver.core.tasks import TaskContext, task, multi_turn_task


PACKAGE_ROOT = Path(__file__).resolve().parents[2]
STORE_ROOT = PACKAGE_ROOT / ".test-runs" / "resilient-cancellation-matrix"


class MyError(RuntimeError):
    """Sentinel handler exception used by matrix tests."""


def _unique(prefix: str) -> str:
    return f"t022_{prefix}_{uuid.uuid4().hex}"


def _public_exception(name: str) -> type[BaseException]:
    resilient = importlib.import_module("azure.ai.agentserver.core.tasks")
    exc_type = getattr(resilient, name, None)
    assert exc_type is not None, f" requires public {name}"
    assert issubclass(exc_type, BaseException)
    return exc_type


def _assert_bare_exception(exc: BaseException) -> None:
    try:
        attrs = vars(exc)
    except TypeError:
        attrs = {}
    assert attrs == {}
    assert not hasattr(exc, "task_id")


def _multi_turn_task(**kwargs: Any) -> Any:
    resilient = importlib.import_module("azure.ai.agentserver.core.tasks")
    decorator = getattr(resilient, "multi_turn_task", None)
    assert decorator is not None, " requires public multi_turn_task"
    return decorator(**kwargs)


async def _delete_chain(multi_task: Any, task_id: str) -> None:
    delete = getattr(multi_task, "delete", None)
    assert delete is not None, " requires multi_turn_task.delete(task_id)"
    await delete(task_id)


async def _result(run: Any, *, timeout: float = 2.0) -> Any:
    return await asyncio.wait_for(run.result(), timeout=timeout)


async def _force_expire_lease(manager: Any, task_id: str) -> None:
    from azure.ai.agentserver.core.tasks._models import TaskPatchRequest

    await manager.provider.update(
        task_id,
        TaskPatchRequest(
            lease_owner=manager._lease_owner,  # noqa: SLF001
            lease_instance_id=manager._instance_id,  # noqa: SLF001
            lease_duration_seconds=0,
        ),
    )


class _ManagerFixture:
    """Set up TaskManager with local storage under the repository, not /tmp."""

    @staticmethod
    async def setup(*, shutdown_grace_seconds: float = 25.0) -> tuple[Any, Any, Path]:
        from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
        from azure.ai.agentserver.core.tasks._manager import TaskManager

        import azure.ai.agentserver.core.tasks._manager as mgr_mod

        store_dir = STORE_ROOT / uuid.uuid4().hex
        store_dir.mkdir(parents=True, exist_ok=False)
        provider = LocalFileTaskProvider(store_dir)
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
        manager = TaskManager(config=config, provider=provider, shutdown_grace_seconds=shutdown_grace_seconds)
        mgr_mod._manager = manager  # noqa: SLF001
        await manager.startup()
        return manager, mgr_mod, store_dir

    @staticmethod
    async def teardown(manager: Any, mgr_mod: Any, store_dir: Path) -> None:
        with suppress(Exception):
            if not manager._shutdown_event.is_set():  # noqa: SLF001
                await manager.shutdown()
        mgr_mod._manager = None  # noqa: SLF001
        shutil.rmtree(store_dir, ignore_errors=True)


class TestRunCancelOneShot:
    """— TaskRun.cancel on a one-shot task."""

    @pytest.mark.asyncio
    async def test_handler_raises_CancelledError_caller_sees_TaskCancelled(self):
        manager, mgr_mod, store_dir = await _ManagerFixture.setup()
        try:
            TaskCancelled = _public_exception("TaskCancelled")

            @task(name=_unique("run_cancel_one_shot_cancelled"))
            async def cancellable(ctx: TaskContext[str]) -> str:
                while not ctx.cancel.is_set():
                    await asyncio.sleep(0.01)
                raise asyncio.CancelledError()

            task_id = _unique("one_shot")
            run = await cancellable.start(task_id=task_id, input="input")
            await asyncio.sleep(0.05)
            await run.cancel()
            with pytest.raises(TaskCancelled) as exc_info:
                await _result(run)
            _assert_bare_exception(exc_info.value)
            assert await manager.provider.get(task_id) is None
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod, store_dir)

    @pytest.mark.asyncio
    async def test_handler_raises_other_exception_caller_sees_TaskFailed(self):
        manager, mgr_mod, store_dir = await _ManagerFixture.setup()
        try:
            TaskFailed = _public_exception("TaskFailed")

            @task(name=_unique("run_cancel_one_shot_failed"))
            async def raises_other(ctx: TaskContext[str]) -> str:
                while not ctx.cancel.is_set():
                    await asyncio.sleep(0.01)
                raise MyError("not cancellation")

            run = await raises_other.start(task_id=_unique("one_shot"), input="input")
            await asyncio.sleep(0.05)
            await run.cancel()
            with pytest.raises(TaskFailed):
                await _result(run)
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod, store_dir)

    @pytest.mark.asyncio
    async def test_handler_returns_X_caller_sees_X(self):
        manager, mgr_mod, store_dir = await _ManagerFixture.setup()
        try:

            @task(name=_unique("run_cancel_one_shot_returns_x"))
            async def returns_x(ctx: TaskContext[str]) -> str:
                while not ctx.cancel.is_set():
                    await asyncio.sleep(0.01)
                return "X"

            run = await returns_x.start(task_id=_unique("one_shot"), input="input")
            await asyncio.sleep(0.05)
            await run.cancel()
            assert await _result(run) == "X"
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod, store_dir)

    @pytest.mark.asyncio
    async def test_handler_ignores_cancel_runs_to_completion(self):
        manager, mgr_mod, store_dir = await _ManagerFixture.setup()
        try:

            @task(name=_unique("run_cancel_one_shot_ignores"))
            async def ignores_cancel(ctx: TaskContext[str]) -> str:
                await asyncio.sleep(0.15)
                return "Y"

            run = await ignores_cancel.start(task_id=_unique("one_shot"), input="input")
            await asyncio.sleep(0.05)
            await run.cancel()
            assert await _result(run) == "Y"
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod, store_dir)


class TestRunCancelMultiTurn:
    """— TaskRun.cancel on a multi-turn in-flight turn. Chain stays alive."""

    @pytest.mark.asyncio
    async def test_handler_raises_CancelledError_caller_sees_TaskCancelled(self):
        manager, mgr_mod, store_dir = await _ManagerFixture.setup()
        try:
            TaskCancelled = _public_exception("TaskCancelled")

            @_multi_turn_task(name=_unique("run_cancel_multi_cancelled"))
            async def cancellable(ctx: TaskContext[str]) -> str:
                while not ctx.cancel.is_set():
                    await asyncio.sleep(0.01)
                raise asyncio.CancelledError()

            run = await cancellable.start(task_id=_unique("multi"), input="input", input_id="i1")
            await asyncio.sleep(0.05)
            await run.cancel()
            with pytest.raises(TaskCancelled) as exc_info:
                await _result(run)
            _assert_bare_exception(exc_info.value)
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod, store_dir)

    @pytest.mark.asyncio
    async def test_chain_alive_after_cancelled_turn(self):
        manager, mgr_mod, store_dir = await _ManagerFixture.setup()
        try:
            seen: list[str] = []

            @_multi_turn_task(name=_unique("run_cancel_multi_chain_alive"))
            async def chain(ctx: TaskContext[str]) -> str:
                seen.append(ctx.input)
                if ctx.input == "cancel":
                    while not ctx.cancel.is_set():
                        await asyncio.sleep(0.01)
                    raise asyncio.CancelledError()
                return "after-cancel-ok"

            task_id = _unique("multi")
            run = await chain.start(task_id=task_id, input="cancel", input_id="i1")
            await asyncio.sleep(0.05)
            await run.cancel()
            with pytest.raises(_public_exception("TaskCancelled")):
                await _result(run)
            assert await chain.run(task_id=task_id, input="next", input_id="i2") == "after-cancel-ok"
            assert seen == ["cancel", "next"]
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod, store_dir)

    @pytest.mark.asyncio
    async def test_queued_steerer_promotes_after_cancelled_turn(self):
        manager, mgr_mod, store_dir = await _ManagerFixture.setup()
        try:
            entered = asyncio.Event()
            seen: list[str] = []

            @_multi_turn_task(name=_unique("run_cancel_multi_queue_promotes"), steerable=True)
            async def steerable(ctx: TaskContext[str]) -> str:
                seen.append(ctx.input)
                if ctx.input == "active":
                    entered.set()
                    while not ctx.cancel.is_set():
                        await asyncio.sleep(0.01)
                    raise asyncio.CancelledError()
                return f"promoted:{ctx.input}"

            task_id = _unique("multi")
            active = await steerable.start(task_id=task_id, input="active", input_id="i1")
            await asyncio.wait_for(entered.wait(), timeout=2.0)
            queued = await steerable.start(task_id=task_id, input="queued", input_id="i2")
            await active.cancel()
            with pytest.raises(_public_exception("TaskCancelled")):
                await _result(active)
            assert await _result(queued) == "promoted:queued"
            assert seen == ["active", "queued"]
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod, store_dir)


class TestTimeoutOneShot:
    """— timeout= expiry on one-shot. Cooperative-only signaling."""

    @pytest.mark.asyncio
    async def test_timeout_sets_ctx_flags(self):
        manager, mgr_mod, store_dir = await _ManagerFixture.setup()
        try:
            observed: dict[str, bool] = {}

            @task(name=_unique("timeout_flags"), timeout=timedelta(seconds=0.1))
            async def slow(ctx: TaskContext[str]) -> str:
                while not ctx.cancel.is_set():
                    await asyncio.sleep(0.01)
                observed["timeout_exceeded"] = ctx.timeout_exceeded
                observed["cancel"] = ctx.cancel.is_set()
                return "flags"

            run = await slow.start(task_id=_unique("one_shot"), input="input")
            assert await _result(run) == "flags"
            assert observed == {"timeout_exceeded": True, "cancel": True}
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod, store_dir)

    @pytest.mark.asyncio
    async def test_framework_never_raises_automatically(self):
        manager, mgr_mod, store_dir = await _ManagerFixture.setup()
        try:

            @task(name=_unique("timeout_ignores"), timeout=timedelta(seconds=0.1))
            async def ignores_timeout(ctx: TaskContext[str]) -> str:
                await asyncio.sleep(0.25)
                return "completed-after-timeout"

            run = await ignores_timeout.start(task_id=_unique("one_shot"), input="input")
            assert await _result(run) == "completed-after-timeout"
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod, store_dir)

    @pytest.mark.asyncio
    async def test_handler_honors_with_CancelledError_caller_sees_TaskCancelled(self):
        manager, mgr_mod, store_dir = await _ManagerFixture.setup()
        try:
            TaskCancelled = _public_exception("TaskCancelled")

            @task(name=_unique("timeout_cancelled"), timeout=timedelta(seconds=0.1))
            async def honors_timeout(ctx: TaskContext[str]) -> str:
                while not ctx.cancel.is_set():
                    await asyncio.sleep(0.01)
                assert ctx.timeout_exceeded is True
                raise asyncio.CancelledError()

            run = await honors_timeout.start(task_id=_unique("one_shot"), input="input")
            with pytest.raises(TaskCancelled) as exc_info:
                await _result(run)
            _assert_bare_exception(exc_info.value)
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod, store_dir)

    @pytest.mark.asyncio
    async def test_handler_returns_X_after_timeout_caller_sees_X(self):
        manager, mgr_mod, store_dir = await _ManagerFixture.setup()
        try:

            @task(name=_unique("timeout_returns_x"), timeout=timedelta(seconds=0.1))
            async def returns_x(ctx: TaskContext[str]) -> str:
                while not ctx.timeout_exceeded:
                    await asyncio.sleep(0.01)
                assert ctx.cancel.is_set()
                return "X"

            run = await returns_x.start(task_id=_unique("one_shot"), input="input")
            assert await _result(run) == "X"
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod, store_dir)


class TestTimeoutMultiTurn:
    """— timeout= on multi-turn (per-turn). Chain stays alive; watchdog re-armed per turn."""

    @pytest.mark.asyncio
    async def test_timeout_per_turn(self):
        manager, mgr_mod, store_dir = await _ManagerFixture.setup()
        try:
            observed: list[tuple[str, bool, bool]] = []

            @_multi_turn_task(name=_unique("timeout_multi_per_turn"), timeout=timedelta(seconds=0.1))
            async def per_turn(ctx: TaskContext[str]) -> str:
                while not ctx.timeout_exceeded:
                    await asyncio.sleep(0.01)
                observed.append((ctx.input, ctx.timeout_exceeded, ctx.cancel.is_set()))
                return f"timed:{ctx.input}"

            task_id = _unique("multi")
            assert await per_turn.run(task_id=task_id, input="first", input_id="i1") == "timed:first"
            assert await per_turn.run(task_id=task_id, input="second", input_id="i2") == "timed:second"
            assert observed == [("first", True, True), ("second", True, True)]
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod, store_dir)

    @pytest.mark.asyncio
    async def test_watchdog_rearmed_on_steering_drain(self):
        manager, mgr_mod, store_dir = await _ManagerFixture.setup()
        try:
            starts: list[float] = []
            timed_out: list[str] = []
            first_entered = asyncio.Event()

            @_multi_turn_task(
                name=_unique("timeout_multi_watchdog_rearmed"), timeout=timedelta(seconds=0.2), steerable=True
            )
            async def steerable(ctx: TaskContext[str]) -> str:
                starts.append(asyncio.get_event_loop().time())
                if ctx.input == "active":
                    first_entered.set()
                    while not ctx.cancel.is_set():
                        await asyncio.sleep(0.01)
                    return "active-done"
                while not ctx.timeout_exceeded:
                    await asyncio.sleep(0.01)
                timed_out.append(ctx.input)
                return f"timeout:{ctx.input}"

            task_id = _unique("multi")
            active = await steerable.start(task_id=task_id, input="active", input_id="i1")
            await asyncio.wait_for(first_entered.wait(), timeout=2.0)
            queued = await steerable.start(task_id=task_id, input="queued", input_id="i2")
            assert await _result(active) == "active-done"
            assert await _result(queued, timeout=3.0) == "timeout:queued"
            assert timed_out == ["queued"]
            assert len(starts) == 2
            assert starts[1] - starts[0] < 0.5
            assert hasattr(manager, "_timeout_watchdogs")
            assert task_id not in manager._timeout_watchdogs  # noqa: SLF001
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod, store_dir)


class TestExitForRecovery:
    """+  — ctx.exit_for_recovery raises TaskDeferred."""

    @pytest.mark.asyncio
    async def test_exit_for_recovery_caller_sees_TaskDeferred(self):
        manager, mgr_mod, store_dir = await _ManagerFixture.setup()
        try:
            TaskDeferred = _public_exception("TaskDeferred")

            @multi_turn_task(name=_unique("exit_deferred"))
            async def defer(ctx: TaskContext[str]) -> str:
                ctx.shutdown.set()
                return await ctx.exit_for_recovery()

            run = await defer.start(task_id=_unique("one_shot"), input="input")
            with pytest.raises(TaskDeferred) as exc_info:
                await _result(run)
            _assert_bare_exception(exc_info.value)
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod, store_dir)

    @pytest.mark.asyncio
    async def test_exit_for_recovery_record_stays_in_progress(self):
        manager, mgr_mod, store_dir = await _ManagerFixture.setup()
        try:
            TaskDeferred = _public_exception("TaskDeferred")

            @_multi_turn_task(name=_unique("exit_deferred_preserves_queue"), steerable=True)
            async def defer(ctx: TaskContext[str]) -> str:
                ctx.shutdown.set()
                return await ctx.exit_for_recovery()

            task_id = _unique("multi")
            active = await defer.start(task_id=task_id, input="active", input_id="i1")
            queued = await defer.start(task_id=task_id, input="queued", input_id="i2")
            with pytest.raises(TaskDeferred):
                await _result(active)
            info = await manager.provider.get(task_id)
            assert info is not None
            assert info.status == "in_progress"
            assert info.payload is not None
            assert info.payload["input"] == "active"
            assert info.payload["steering"]["pending_inputs"] == ["queued"]
            assert info.lease is not None
            assert info.lease.expires_at <= info.lease.heartbeat_at
            assert not queued._result_future.done()  # noqa: SLF001
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod, store_dir)


class TestLeaseExpiryCrash:
    """— Process lease expiry mid-handler (crash). Recovery uses persisted input."""

    @pytest.mark.asyncio
    async def test_crash_recovery_re_invokes_with_persisted_input(self):
        manager, mgr_mod, store_dir = await _ManagerFixture.setup()
        try:
            invocations: list[tuple[str, str]] = []
            first_entered = asyncio.Event()

            @multi_turn_task(name=_unique("crash_recovery"))
            async def crashy(ctx: TaskContext[str]) -> str:
                invocations.append((ctx.entry_mode, ctx.input))
                if ctx.entry_mode == "recovered":
                    return f"recovered:{ctx.input}"
                first_entered.set()
                await asyncio.Event().wait()
                return "unreachable"

            task_id = _unique("one_shot")
            run = await crashy.start(task_id=task_id, input="persisted", input_id="persisted")
            await asyncio.wait_for(first_entered.wait(), timeout=2.0)

            # Simulate an OS-level crash by silently abandoning the
            # in-process bookkeeping WITHOUT giving the handler's cancel
            # handler a chance to transition the chain to suspended.
            # A real crash (OOM kill / SIGKILL) leaves the resilient
            # record as "in_progress" with our lease still in place —
            # which is exactly the state we need the new lifetime to
            # recover from.
            #
            # The asyncio CancelledError path would normally transition
            # the chain to suspended (chains stay alive across cancel),
            # so we cannot use ``execution_task.cancel()`` here; we
            # instead detach the bookkeeping and rewrite the record
            # back to its pre-cancel "in_progress" shape.
            active = manager._active_tasks.pop(task_id)  # noqa: SLF001
            active.renewal_cancel.set()
            active.execution_task._log_destroy_pending = False  # type: ignore[attr-defined]
            active.execution_task.cancel()
            with suppress(asyncio.CancelledError, BaseException):
                await active.execution_task
            # The cancel handler ran and transitioned the chain to
            # suspended; rewrite the record back to in_progress with
            # the persisted input to recreate the crashed-mid-handler
            # shape that recovery is designed to pick up.
            from azure.ai.agentserver.core.tasks._models import TaskPatchRequest

            await manager.provider.update(
                task_id,
                TaskPatchRequest(
                    status="in_progress",
                    payload={
                        "input": "persisted",
                        "last_input_id": "persisted",
                    },
                    lease_owner=manager._lease_owner,  # noqa: SLF001
                    lease_instance_id=manager._instance_id,  # noqa: SLF001
                    lease_duration_seconds=60,
                ),
            )
            await _force_expire_lease(manager, task_id)

            from azure.ai.agentserver.core.tasks._manager import TaskManager

            replacement = TaskManager(config=manager._config, provider=manager.provider)  # noqa: SLF001
            mgr_mod._manager = replacement  # noqa: SLF001
            await replacement.startup()
            recovered = await crashy.get_active_run(task_id, "persisted")
            assert recovered is not None
            assert await _result(recovered) == "recovered:persisted"
            assert invocations == [("fresh", "persisted"), ("recovered", "persisted")]
            run._result_future.cancel()  # noqa: SLF001
            manager = replacement
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod, store_dir)


class TestMultiTurnDelete:
    """— multi_turn_task.delete(task_id) while in-flight."""

    @pytest.mark.asyncio
    async def test_delete_resolves_active_caller_with_TaskCancelled(self):
        manager, mgr_mod, store_dir = await _ManagerFixture.setup()
        try:
            TaskCancelled = _public_exception("TaskCancelled")
            entered = asyncio.Event()

            @_multi_turn_task(name=_unique("delete_active"))
            async def running(ctx: TaskContext[str]) -> str:
                entered.set()
                await asyncio.Event().wait()
                return "unreachable"

            task_id = _unique("multi")
            active = await running.start(task_id=task_id, input="active", input_id="i1")
            await asyncio.wait_for(entered.wait(), timeout=2.0)
            await _delete_chain(running, task_id)
            with pytest.raises(TaskCancelled):
                await _result(active)
            assert await manager.provider.get(task_id) is None
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod, store_dir)

    @pytest.mark.asyncio
    async def test_delete_resolves_all_queued_with_TaskCancelled(self):
        manager, mgr_mod, store_dir = await _ManagerFixture.setup()
        try:
            TaskCancelled = _public_exception("TaskCancelled")
            entered = asyncio.Event()

            @_multi_turn_task(name=_unique("delete_queued"), steerable=True)
            async def running(ctx: TaskContext[str]) -> str:
                entered.set()
                await asyncio.Event().wait()
                return "unreachable"

            task_id = _unique("multi")
            active = await running.start(task_id=task_id, input="active", input_id="i1")
            await asyncio.wait_for(entered.wait(), timeout=2.0)
            queued_a = await running.start(task_id=task_id, input="a", input_id="i2")
            queued_b = await running.start(task_id=task_id, input="b", input_id="i3")
            await _delete_chain(running, task_id)
            for run in (active, queued_a, queued_b):
                with pytest.raises(TaskCancelled):
                    await _result(run)
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod, store_dir)

    @pytest.mark.asyncio
    async def test_delete_is_idempotent(self):
        manager, mgr_mod, store_dir = await _ManagerFixture.setup()
        try:

            @_multi_turn_task(name=_unique("delete_idempotent"))
            async def quick(ctx: TaskContext[str]) -> str:
                await asyncio.Event().wait()
                return "unreachable"

            task_id = _unique("multi")
            await quick.start(task_id=task_id, input="active", input_id="i1")
            await _delete_chain(quick, task_id)
            await _delete_chain(quick, task_id)
            assert await manager.provider.get(task_id) is None
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod, store_dir)


class TestDeleteVsPromotionRace:
    """— Race: delete happens mid-promotion."""

    @pytest.mark.asyncio
    async def test_delete_after_promotion_cas_still_resolves_TaskCancelled(self):
        manager, mgr_mod, store_dir = await _ManagerFixture.setup()
        try:
            TaskCancelled = _public_exception("TaskCancelled")
            promoted_entered = asyncio.Event()

            @_multi_turn_task(name=_unique("delete_after_promotion"), steerable=True)
            async def race(ctx: TaskContext[str]) -> str:
                if ctx.input == "active":
                    return "active-complete"
                promoted_entered.set()
                await asyncio.Event().wait()
                return "unreachable"

            task_id = _unique("multi")
            active = await race.start(task_id=task_id, input="active", input_id="i1")
            queued = await race.start(task_id=task_id, input="queued", input_id="i2")
            assert await _result(active) == "active-complete"
            await asyncio.wait_for(promoted_entered.wait(), timeout=2.0)
            await _delete_chain(race, task_id)
            with pytest.raises(TaskCancelled):
                await _result(queued)
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod, store_dir)

    @pytest.mark.asyncio
    async def test_delete_before_promotion_cas_queued_head_never_runs(self):
        manager, mgr_mod, store_dir = await _ManagerFixture.setup()
        try:
            TaskCancelled = _public_exception("TaskCancelled")
            active_entered = asyncio.Event()
            release_active = asyncio.Event()
            seen: list[str] = []

            @_multi_turn_task(name=_unique("delete_before_promotion"), steerable=True)
            async def race(ctx: TaskContext[str]) -> str:
                seen.append(ctx.input)
                if ctx.input == "active":
                    active_entered.set()
                    await release_active.wait()
                    return "active-complete"
                return "queued-ran"

            task_id = _unique("multi")
            active = await race.start(task_id=task_id, input="active", input_id="i1")
            await asyncio.wait_for(active_entered.wait(), timeout=2.0)
            queued = await race.start(task_id=task_id, input="queued", input_id="i2")
            await _delete_chain(race, task_id)
            release_active.set()
            with pytest.raises(TaskCancelled):
                await _result(queued)
            with pytest.raises(TaskCancelled):
                await _result(active)
            assert seen == ["active"]
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod, store_dir)


class TestQueuedSteererCancel:
    """— TaskRun.cancel on a handle bound to queued (not-yet-promoted) steerer."""

    @pytest.mark.asyncio
    async def test_queued_cancel_removes_from_queue(self):
        manager, mgr_mod, store_dir = await _ManagerFixture.setup()
        try:
            TaskCancelled = _public_exception("TaskCancelled")
            release_active = asyncio.Event()
            seen: list[str] = []

            @_multi_turn_task(name=_unique("queued_cancel"), steerable=True)
            async def steerable(ctx: TaskContext[str]) -> str:
                seen.append(ctx.input)
                if ctx.input == "active":
                    await release_active.wait()
                    return "active-done"
                return f"done:{ctx.input}"

            task_id = _unique("multi")
            active = await steerable.start(task_id=task_id, input="active", input_id="i1")
            queued_a = await steerable.start(task_id=task_id, input="A", input_id="i2")
            queued_b = await steerable.start(task_id=task_id, input="B", input_id="i3")
            await queued_a.cancel()
            with pytest.raises(TaskCancelled):
                await _result(queued_a)
            info = await manager.provider.get(task_id)
            assert info is not None
            assert info.payload is not None
            assert info.payload["steering"]["pending_inputs"] == ["B"]
            release_active.set()
            assert await _result(active) == "active-done"
            assert await _result(queued_b) == "done:B"
            assert seen == ["active", "B"]
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod, store_dir)


class TestShutdown:
    """— Process shutdown ctx.shutdown set, graceful."""

    @pytest.mark.asyncio
    async def test_handler_returns_within_grace_normal_result(self):
        manager, mgr_mod, store_dir = await _ManagerFixture.setup(shutdown_grace_seconds=0.5)
        try:
            entered = asyncio.Event()

            @multi_turn_task(name=_unique("shutdown_returns"))
            async def shutdown_aware(ctx: TaskContext[str]) -> str:
                entered.set()
                while not ctx.shutdown.is_set():
                    await asyncio.sleep(0.01)
                return "graceful-output"

            run = await shutdown_aware.start(task_id=_unique("one_shot"), input="input")
            await asyncio.wait_for(entered.wait(), timeout=2.0)
            await manager.shutdown()
            assert await _result(run) == "graceful-output"
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod, store_dir)

    @pytest.mark.asyncio
    async def test_grace_expires_treated_like_crash(self):
        manager, mgr_mod, store_dir = await _ManagerFixture.setup(shutdown_grace_seconds=0.1)
        try:
            entered = asyncio.Event()
            task_id = _unique("one_shot")

            @multi_turn_task(name=_unique("shutdown_crash"))
            async def ignores_shutdown(ctx: TaskContext[str]) -> str:
                entered.set()
                await asyncio.Event().wait()
                return "unreachable"

            await ignores_shutdown.start(task_id=task_id, input="input")
            await asyncio.wait_for(entered.wait(), timeout=2.0)
            await manager.shutdown()
            info = await manager.provider.get(task_id)
            assert info is not None
            assert info.status == "in_progress"
            assert info.payload is not None
            assert info.payload["input"] == "input"
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod, store_dir)
