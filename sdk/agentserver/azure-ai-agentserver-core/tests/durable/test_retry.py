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
    durable_task,
)


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
            jitter=False,
        )
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
            RetryPolicy(retry_on=(str,))  # type: ignore[arg-type]

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
            jitter=False,
        )
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
            jitter=False,
        )
        for attempt in range(5):
            assert p.compute_delay(attempt) == 5.0

    def test_capped_at_max(self) -> None:
        p = RetryPolicy(
            initial_delay=timedelta(seconds=1),
            backoff_coefficient=10.0,
            max_delay=timedelta(seconds=30),
            jitter=False,
        )
        # 1 * 10^2 = 100, but capped at 30
        assert p.compute_delay(2) == 30.0

    def test_jitter_bounds(self) -> None:
        p = RetryPolicy(
            initial_delay=timedelta(seconds=10),
            backoff_coefficient=1.0,
            max_delay=timedelta(seconds=10),
            jitter=True,
        )
        for _ in range(100):
            delay = p.compute_delay(0)
            assert 7.5 <= delay <= 12.5  # 10 * [0.75, 1.25]

    def test_no_jitter_exact(self) -> None:
        p = RetryPolicy(
            initial_delay=timedelta(seconds=2),
            backoff_coefficient=3.0,
            max_delay=timedelta(seconds=200),
            jitter=False,
        )
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
        p = RetryPolicy(max_attempts=5, retry_on=(ValueError,), jitter=False)
        assert p.should_retry(0, ValueError("bad")) is True

    def test_non_matching_exception(self) -> None:
        p = RetryPolicy(max_attempts=5, retry_on=(ValueError,), jitter=False)
        assert p.should_retry(0, RuntimeError("nope")) is False

    def test_none_means_all_exceptions(self) -> None:
        p = RetryPolicy(max_attempts=5, retry_on=None, jitter=False)
        assert p.should_retry(0, ValueError("a")) is True
        assert p.should_retry(0, ConnectionError("b")) is True
        assert p.should_retry(0, RuntimeError("c")) is True

    def test_subclass_matching(self) -> None:
        p = RetryPolicy(max_attempts=5, retry_on=(OSError,), jitter=False)
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
    """Integration tests that run tasks through the full DurableTaskManager."""

    async def _setup_manager(self, tmp_path):
        """Create a manager with local file provider pointing to tmp_path."""
        from azure.ai.agentserver.core.durable._local_provider import (
            LocalFileDurableTaskProvider,
        )
        from azure.ai.agentserver.core.durable._manager import (
            DurableTaskManager,
        )

        import azure.ai.agentserver.core.durable._manager as mgr_mod

        provider = LocalFileDurableTaskProvider(Path(str(tmp_path)))
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
        manager = DurableTaskManager(config=config, provider=provider)
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

        @durable_task(title="retry-test")
        async def flaky(ctx: TaskContext[str]) -> str:
            call_log.append(ctx.run_attempt)
            if ctx.run_attempt < 2:
                raise ConnectionError(f"fail attempt {ctx.run_attempt}")
            return "success"

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            with patch("asyncio.sleep", new_callable=AsyncMock):
                result = await flaky.run(
                    task_id="retry-1",
                    input="test",
                    retry=RetryPolicy.exponential_backoff(max_attempts=3),
                )
            assert result.output == "success"
            assert call_log == [0, 1, 2]
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_retry_exhausted(self, tmp_path) -> None:
        """Task always fails — retries exhaust and TaskFailed is raised."""

        @durable_task(title="always-fail")
        async def always_fail(ctx: TaskContext[str]) -> str:
            raise ValueError(f"boom on attempt {ctx.run_attempt}")

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            with patch("asyncio.sleep", new_callable=AsyncMock):
                with pytest.raises(TaskFailed) as exc_info:
                    await always_fail.run(
                        task_id="exhaust-1",
                        input="test",
                        retry=RetryPolicy(
                            max_attempts=3,
                            retry_on=(ValueError,),
                            jitter=False,
                        ),
                    )
            error = exc_info.value.error
            assert error["type"] == "exhausted_retries"
            assert error["attempts"] == 3
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_non_retryable_exception(self, tmp_path) -> None:
        """Wrong exception type — fails immediately without retry."""
        attempts: list[int] = []

        @durable_task(title="wrong-exc")
        async def wrong_exc(ctx: TaskContext[str]) -> str:
            attempts.append(ctx.run_attempt)
            raise TypeError("not retryable")

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            with pytest.raises(TaskFailed):
                await wrong_exc.run(
                    task_id="nonretry-1",
                    input="test",
                    retry=RetryPolicy(
                        max_attempts=5,
                        retry_on=(ValueError,),
                        jitter=False,
                    ),
                )
            # Only ran once — no retries for TypeError
            assert attempts == [0]
        finally:
            await self._teardown_manager(manager, mgr_mod)
