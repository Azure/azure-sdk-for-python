# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Tests for RetryPolicy — construction, delay computation, presets, and integration."""

from __future__ import annotations

import asyncio
from datetime import timedelta
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from azure.ai.agentserver.core.durable import (
    RetryPolicy,
    TaskContext,
    TaskFailed,
    task,
    multi_turn_task)


# ---------------------------------------------------------------------------
# Construction & validation
# ---------------------------------------------------------------------------


class TestRetryPolicyConstruction:
    def test_default_construction(self) -> None:
        p = RetryPolicy()
        assert p.initial_delay == timedelta(seconds=1)
        assert p.backoff_coefficient == 2.0
        assert p.max_delay == timedelta(seconds=60)
        assert p.max_attempts == 3
        assert p.retry_on is None
        assert p.jitter is True

    def test_custom_construction(self) -> None:
        p = RetryPolicy(
            initial_delay=timedelta(seconds=5),
            backoff_coefficient=3.0,
            max_delay=timedelta(seconds=120),
            max_attempts=10,
            retry_on=(ValueError, ConnectionError),
            jitter=False)
        assert p.initial_delay == timedelta(seconds=5)
        assert p.backoff_coefficient == 3.0
        assert p.max_delay == timedelta(seconds=120)
        assert p.max_attempts == 10
        assert p.retry_on == (ValueError, ConnectionError)
        assert p.jitter is False

    def test_validation_initial_delay_negative(self) -> None:
        with pytest.raises(ValueError, match="initial_delay must be >= 0"):
            RetryPolicy(initial_delay=timedelta(seconds=-1))

    def test_validation_backoff_coefficient_below_one(self) -> None:
        with pytest.raises(ValueError, match="backoff_coefficient must be >= 1.0"):
            RetryPolicy(backoff_coefficient=0.5)

    def test_validation_max_delay_below_initial(self) -> None:
        with pytest.raises(ValueError, match="max_delay.*must be >= initial_delay"):
            RetryPolicy(
                initial_delay=timedelta(seconds=10), max_delay=timedelta(seconds=5)
            )

    def test_validation_max_attempts_zero(self) -> None:
        with pytest.raises(ValueError, match="max_attempts must be >= 1"):
            RetryPolicy(max_attempts=0)

    def test_validation_retry_on_non_exception(self) -> None:
        with pytest.raises(
            TypeError, match="retry_on entries must be Exception subclasses"
        ):
            RetryPolicy(retry_on=(str))  # type: ignore[arg-type]

    def test_repr(self) -> None:
        p = RetryPolicy(max_attempts=5)
        r = repr(p)
        assert "RetryPolicy" in r
        assert "max_attempts=5" in r

    def test_eq(self) -> None:
        a = RetryPolicy(max_attempts=3)
        b = RetryPolicy(max_attempts=3)
        c = RetryPolicy(max_attempts=5)
        assert a == b
        assert a != c
        assert a != "not a policy"


# ---------------------------------------------------------------------------
# Delay computation
# ---------------------------------------------------------------------------


class TestComputeDelay:
    def test_exponential(self) -> None:
        p = RetryPolicy(
            initial_delay=timedelta(seconds=1),
            backoff_coefficient=2.0,
            max_delay=timedelta(seconds=120),
            jitter=False)
        assert p.compute_delay(0) == 1.0  # 1 * 2^0
        assert p.compute_delay(1) == 2.0  # 1 * 2^1
        assert p.compute_delay(2) == 4.0  # 1 * 2^2
        assert p.compute_delay(3) == 8.0  # 1 * 2^3
        assert p.compute_delay(5) == 32.0  # 1 * 2^5

    def test_fixed_delay(self) -> None:
        p = RetryPolicy(
            initial_delay=timedelta(seconds=5),
            backoff_coefficient=1.0,
            max_delay=timedelta(seconds=5),
            jitter=False)
        for attempt in range(5):
            assert p.compute_delay(attempt) == 5.0

    def test_capped_at_max(self) -> None:
        p = RetryPolicy(
            initial_delay=timedelta(seconds=1),
            backoff_coefficient=10.0,
            max_delay=timedelta(seconds=30),
            jitter=False)
        # 1 * 10^2 = 100, but capped at 30
        assert p.compute_delay(2) == 30.0

    def test_jitter_bounds(self) -> None:
        p = RetryPolicy(
            initial_delay=timedelta(seconds=10),
            backoff_coefficient=1.0,
            max_delay=timedelta(seconds=10),
            jitter=True)
        for _ in range(100):
            delay = p.compute_delay(0)
            assert 7.5 <= delay <= 12.5  # 10 * [0.75, 1.25]

    def test_no_jitter_exact(self) -> None:
        p = RetryPolicy(
            initial_delay=timedelta(seconds=2),
            backoff_coefficient=3.0,
            max_delay=timedelta(seconds=200),
            jitter=False)
        assert p.compute_delay(0) == 2.0  # 2 * 3^0
        assert p.compute_delay(1) == 6.0  # 2 * 3^1
        assert p.compute_delay(2) == 18.0  # 2 * 3^2

    def test_linear_preset_delay(self) -> None:
        p = RetryPolicy.linear_backoff(initial_delay=timedelta(seconds=2))
        assert p.compute_delay(0) == 2.0  # 2 * (0+1) = 2
        assert p.compute_delay(1) == 4.0  # 2 * (1+1) = 4
        assert p.compute_delay(2) == 6.0  # 2 * (2+1) = 6
        assert p.compute_delay(3) == 8.0  # 2 * (3+1) = 8


# ---------------------------------------------------------------------------
# should_retry
# ---------------------------------------------------------------------------


class TestShouldRetry:
    def test_within_attempts(self) -> None:
        p = RetryPolicy(max_attempts=3, jitter=False)
        assert p.should_retry(0, RuntimeError("test")) is True
        assert p.should_retry(1, RuntimeError("test")) is True

    def test_exhausted(self) -> None:
        p = RetryPolicy(max_attempts=3, jitter=False)
        assert (
            p.should_retry(2, RuntimeError("test")) is False
        )  # attempt 2 is the 3rd try
        assert p.should_retry(5, RuntimeError("test")) is False

    def test_matching_exception(self) -> None:
        p = RetryPolicy(max_attempts=5, retry_on=(ValueError), jitter=False)
        assert p.should_retry(0, ValueError("bad")) is True

    def test_non_matching_exception(self) -> None:
        p = RetryPolicy(max_attempts=5, retry_on=(ValueError), jitter=False)
        assert p.should_retry(0, RuntimeError("nope")) is False

    def test_none_means_all_exceptions(self) -> None:
        p = RetryPolicy(max_attempts=5, retry_on=None, jitter=False)
        assert p.should_retry(0, ValueError("a")) is True
        assert p.should_retry(0, ConnectionError("b")) is True
        assert p.should_retry(0, RuntimeError("c")) is True

    def test_subclass_matching(self) -> None:
        p = RetryPolicy(max_attempts=5, retry_on=(OSError), jitter=False)
        assert (
            p.should_retry(0, ConnectionError("net")) is True
        )  # ConnectionError is OSError subclass


# ---------------------------------------------------------------------------
# Presets
# ---------------------------------------------------------------------------


class TestPresets:
    def test_exponential_backoff(self) -> None:
        p = RetryPolicy.exponential_backoff(max_attempts=5)
        assert p.backoff_coefficient == 2.0
        assert p.max_attempts == 5
        assert p.jitter is True
        assert p.initial_delay == timedelta(seconds=1)

    def test_fixed_delay(self) -> None:
        p = RetryPolicy.fixed_delay(delay=timedelta(seconds=10), max_attempts=4)
        assert p.backoff_coefficient == 1.0
        assert p.initial_delay == timedelta(seconds=10)
        assert p.max_delay == timedelta(seconds=10)
        assert p.max_attempts == 4
        assert p.jitter is False

    def test_linear_backoff(self) -> None:
        p = RetryPolicy.linear_backoff(
            initial_delay=timedelta(seconds=2), max_attempts=6
        )
        assert p.backoff_coefficient == 1.0
        assert p.initial_delay == timedelta(seconds=2)
        assert p.max_attempts == 6
        assert p.jitter is False

    def test_no_retry(self) -> None:
        p = RetryPolicy.no_retry()
        assert p.max_attempts == 1
        assert p.jitter is False
        assert p.should_retry(0, RuntimeError("x")) is False


# ---------------------------------------------------------------------------
# Integration tests (require manager)
# ---------------------------------------------------------------------------


class TestRetryIntegration:
    """Integration tests that run tasks through the full TaskManager."""

    async def _setup_manager(self, tmp_path):
        """Create a manager with local file provider pointing to tmp_path."""
        from azure.ai.agentserver.core.durable._local_provider import (
            LocalFileTaskProvider)
        from azure.ai.agentserver.core.durable._manager import (
            TaskManager)

        import azure.ai.agentserver.core.durable._manager as mgr_mod

        provider = LocalFileTaskProvider(Path(str(tmp_path)))
        config = type(
            "C",
            (),
            {
                "agent_name": "test-agent",
                "session_id": "test-session",
                "agent_version": "1.0.0",
                "is_hosted": False,
            })()
        manager = TaskManager(config=config, provider=provider)
        mgr_mod._manager = manager
        await manager.startup()
        return manager, mgr_mod

    async def _teardown_manager(self, manager, mgr_mod):
        await manager.shutdown()
        mgr_mod._manager = None

    @pytest.mark.asyncio
    async def test_retry_success_after_failures(self, tmp_path) -> None:
        """Task fails twice then succeeds on attempt 2."""
        call_log: list[int] = []

        @task(
            title="retry-test",
            retry=RetryPolicy.exponential_backoff(max_attempts=3))
        async def flaky(ctx: TaskContext[str]) -> str:
            call_log.append(ctx.retry_attempt)
            if ctx.retry_attempt < 2:
                raise ConnectionError(f"fail attempt {ctx.retry_attempt}")
            return "success"

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            with patch("asyncio.sleep", new_callable=AsyncMock):
                result = await flaky.run(
                    task_id="retry-1",
                    input="test")
            assert result == "success"
            assert call_log == [0, 1, 2]
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_retry_exhausted(self, tmp_path) -> None:
        """Task always fails — retries exhaust and TaskFailed is raised."""

        @task(
            title="always-fail",
            retry=RetryPolicy(
                max_attempts=3,
                retry_on=(ValueError),
                jitter=False))
        async def always_fail(ctx: TaskContext[str]) -> str:
            raise ValueError(f"boom on attempt {ctx.retry_attempt}")

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            with patch("asyncio.sleep", new_callable=AsyncMock):
                with pytest.raises(TaskFailed) as exc_info:
                    await always_fail.run(
                        task_id="exhaust-1",
                        input="test")
            error = exc_info.value.error
            assert error["type"] == "exhausted_retries"
            assert error["attempts"] == 3
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_non_retryable_exception(self, tmp_path) -> None:
        """Wrong exception type — fails immediately without retry."""
        attempts: list[int] = []

        @task(
            title="wrong-exc",
            retry=RetryPolicy(
                max_attempts=5,
                retry_on=(ValueError),
                jitter=False))
        async def wrong_exc(ctx: TaskContext[str]) -> str:
            attempts.append(ctx.retry_attempt)
            raise TypeError("not retryable")

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            with pytest.raises(TaskFailed):
                await wrong_exc.run(
                    task_id="nonretry-1",
                    input="test")
            # Only ran once — no retries for TypeError
            assert attempts == [0]
        finally:
            await self._teardown_manager(manager, mgr_mod)


# ---------------------------------------------------------------------------
# Spec 015 Phase 4 (FR-001 / FR-002 / FR-003) — retry_attempt durability
# ---------------------------------------------------------------------------
#
# These tests pin the cross-lifetime contract for ``ctx.retry_attempt`` and
# ``RetryPolicy.max_attempts``:
#
#   FR-001  ``ctx.retry_attempt`` MUST persist across in-process boundaries
#           via ``payload["_retry_attempt"]`` and MUST be restored verbatim
#           on recovery.
#   FR-002  ``RetryPolicy.max_attempts`` MUST count failure-retries across
#           ALL lifetimes — one durable budget, not a per-lifetime quota.
#   FR-003  Crash recovery MUST NOT consume any of the retry budget; only
#           a handler-raised exception consumes it.
#
# The tests below use the local file provider + a manually-created stale
# ``in_progress`` task to simulate a "prior lifetime" without spawning a
# subprocess. This is the same simulation pattern used by
# ``test_entry_mode.py::TestEntryMode::test_recovered_entry_mode``.


class TestRetryAttemptDurability:
    """FR-001 / FR-002 / FR-003 cross-lifetime retry contract."""

    async def _setup_manager(self, tmp_path):
        from azure.ai.agentserver.core.durable._local_provider import (
            LocalFileTaskProvider)
        from azure.ai.agentserver.core.durable._manager import TaskManager

        import azure.ai.agentserver.core.durable._manager as mgr_mod

        provider = LocalFileTaskProvider(Path(str(tmp_path)))
        config = type(
            "C",
            (),
            {
                "agent_name": "test-agent",
                "session_id": "test-session",
                "agent_version": "1.0.0",
                "is_hosted": False,
            })()
        manager = TaskManager(config=config, provider=provider)
        mgr_mod._manager = manager
        await manager.startup()
        return manager, mgr_mod

    async def _teardown_manager(self, manager, mgr_mod):
        await manager.shutdown()
        mgr_mod._manager = None

    async def _seed_stale_task(
        self,
        manager,
        tmp_path,
        *,
        task_id: str,
        retry_attempt: int,
        input_value: str = "carry-over") -> None:
        """Create a stale ``in_progress`` task that simulates a prior lifetime.

        ``payload["_retry_attempt"]`` is the durable counter that FR-001
        promises to restore on recovery.
        """
        import json

        from azure.ai.agentserver.core.durable._models import TaskCreateRequest

        await manager.provider.create(
            TaskCreateRequest(
                id=task_id,
                agent_name="test-agent",
                session_id="test-session",
                status="in_progress",
                title="retry-durable-test",
                payload={
                    "input": input_value,
                    "_retry_attempt": retry_attempt,
                })
        )
        task_file = (
            Path(str(tmp_path)) / "test-agent" / "test-session" / f"{task_id}.json"
        )
        assert task_file.exists(), (
            "expected provider to materialize a JSON file for the stale task; "
            "this test relies on LocalFileTaskProvider's on-disk layout"
        )
        data = json.loads(task_file.read_text())
        data["updated_at"] = "2020-01-01T00:00:00+00:00"
        task_file.write_text(json.dumps(data))

    @pytest.mark.asyncio
    async def test_retry_attempt_cross_lifetime_durability(self, tmp_path) -> None:
        """FR-001: a recovered task's handler MUST see the persisted retry_attempt.

        Setup simulates a prior lifetime that already burned 2 failure-retries
        (``payload["_retry_attempt"] == 2``). On recovery the handler MUST
        observe ``ctx.retry_attempt == 2`` on its very first invocation —
        not the hardcoded 0 the current implementation supplies.
        """
        observed: list[int] = []

        @multi_turn_task(title="recovered-retry-aware")
        async def handler(ctx: TaskContext[str]) -> str:
            observed.append(ctx.retry_attempt)
            return "ok"

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            await self._seed_stale_task(
                manager, tmp_path, task_id="durable-1", retry_attempt=2
            )
            result = await handler.run(
                task_id="durable-1",
                input="ignored-by-recovery")
            assert result == "ok"
            assert observed == [2], (
                "FR-001 violated: handler MUST observe the persisted "
                "retry_attempt (2) on the first invocation after recovery; "
                f"got {observed!r}. The manager is still hardcoding "
                "retry_attempt=0 on every recovered entry."
            )
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_retry_attempt_budget_exhausts_across_crash(self, tmp_path) -> None:
        """FR-002: max_attempts is a single durable budget across lifetimes.

        With ``max_attempts=3`` and 2 retries already consumed in a prior
        lifetime (``payload["_retry_attempt"] == 2``), recovery has exactly
        ONE retry remaining. If the handler always fails, it must be
        invoked at most once before the budget exhausts; today the
        implementation resets the counter and lets the handler fail 3
        more times.
        """
        from unittest.mock import AsyncMock, patch as _patch

        invocations: list[int] = []

        @task(
            title="always-fail-recovered",
            ephemeral=False,
            retry=RetryPolicy(
                max_attempts=3,
                retry_on=(ValueError),
                jitter=False))
        async def always_fail(ctx: TaskContext[str]) -> str:
            invocations.append(ctx.retry_attempt)
            raise ValueError(f"boom at retry_attempt={ctx.retry_attempt}")

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            await self._seed_stale_task(
                manager, tmp_path, task_id="budget-1", retry_attempt=2
            )
            with _patch("asyncio.sleep", new_callable=AsyncMock):
                with pytest.raises(TaskFailed):
                    await always_fail.run(
                        task_id="budget-1",
                        input="ignored")
            assert invocations == [2], (
                "FR-002 violated: with max_attempts=3 and 2 retries already "
                "consumed across a crash, recovery has exactly ONE attempt "
                "remaining (the retry that the prior lifetime did not get "
                "to make). Handler MUST be invoked exactly once at "
                f"retry_attempt=2; got {invocations!r}."
            )
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_crash_recovery_does_not_consume_retry_budget(
        self, tmp_path
    ) -> None:
        """FR-003: surviving a crash MUST NOT consume any retry budget.

        Setup: a prior lifetime persisted ``_retry_attempt == 2`` and crashed
        BEFORE the handler returned. On recovery the handler succeeds on its
        first invocation. The persisted retry_attempt MUST remain at 2
        (the count of failure-retries the developer's handler raised) —
        the act of recovering itself does not bump the counter.
        """
        observed: list[int] = []

        @task(
            title="recover-then-succeed",
            ephemeral=False,
            retry=RetryPolicy(
                max_attempts=3,
                retry_on=(ValueError),
                jitter=False))
        async def succeed_now(ctx: TaskContext[str]) -> str:
            observed.append(ctx.retry_attempt)
            return f"done@{ctx.retry_attempt}"

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            await self._seed_stale_task(
                manager, tmp_path, task_id="no-consume-1", retry_attempt=2
            )
            result = await succeed_now.run(
                task_id="no-consume-1",
                input="ignored")
            assert result == "done@2"
            assert observed == [2], (
                "FR-003 violated: handler must observe persisted "
                f"retry_attempt=2, got {observed!r}."
            )

            # And the persisted counter must still be 2 — recovery did NOT
            # consume the budget. (Re-fetch via provider to read the on-disk
            # state, not the in-memory cache.)
            info = await manager.provider.get("no-consume-1")
            assert info is not None
            persisted = (info.payload or {}).get("_retry_attempt", 0)
            assert persisted == 2, (
                "FR-003 violated: payload['_retry_attempt'] must NOT be "
                "bumped by recovery — the act of recovering is not a "
                f"failure-retry. Expected 2, found {persisted!r}."
            )
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_steering_drain_resets_retry_attempt_to_zero(
        self, tmp_path
    ) -> None:
        """FR-001: steering drain MUST reset both ``ctx.retry_attempt`` AND
        ``payload["_retry_attempt"]`` to 0.

        Rationale: a steering input is a new logical request from the
        developer; carrying a stale retry count across it would silently
        eat budget. The in-process loop already resets the local
        ``attempt`` variable on drain (see ``_execute_task_loop``
        steering-drain branches); the missing piece is persisting the
        reset so a *subsequent* crash-and-recover does not resurrect the
        old counter.
        """
        from azure.ai.agentserver.core.durable._models import TaskCreateRequest

        observed: list[int] = []

        @task(
            title="steerable-retry-aware",
            ephemeral=False,
            steerable=True)
        async def steer_handler(ctx: TaskContext[str]) -> str:
            observed.append(ctx.retry_attempt)
            # Spec 016 FR-012 (US5): the completion path no longer drains
            # queued steerers — they receive TaskConflictError. To exercise
            # the steering-drain reset of _retry_attempt, the handler MUST
            # suspend rather than return so the drain re-enters for the
            # queued input.
            from azure.ai.agentserver.core.durable._run import Suspended  # noqa: PLC0415
            return None

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            # Seed a stale task that has BOTH _retry_attempt > 0 AND pending
            # steering inputs. On recovery, the steering-drain branch must
            # fire, which is the moment the reset semantics apply.
            import json

            await manager.provider.create(
                TaskCreateRequest(
                    id="steer-reset-1",
                    agent_name="test-agent",
                    session_id="test-session",
                    status="in_progress",
                    title="steer-reset",
                    payload={
                        "input": "first",
                        "_retry_attempt": 2,
                        "_steering": {
                            "pending_inputs": ["second"],
                            "generation": 1,
                        },
                    })
            )
            task_file = (
                Path(str(tmp_path)) / "test-agent" / "test-session" / "steer-reset-1.json"
            )
            data = json.loads(task_file.read_text())
            data["updated_at"] = "2020-01-01T00:00:00+00:00"
            task_file.write_text(json.dumps(data))

            await steer_handler.run(
                task_id="steer-reset-1",
                input="ignored")

            info = await manager.provider.get("steer-reset-1")
            assert info is not None
            persisted = (info.payload or {}).get("_retry_attempt", 0)
            assert persisted == 0, (
                "FR-001 violated: steering drain MUST persist "
                "payload['_retry_attempt'] = 0 so that a subsequent crash "
                "does not resurrect a stale counter. Expected 0, found "
                f"{persisted!r}."
            )
        finally:
            await self._teardown_manager(manager, mgr_mod)
