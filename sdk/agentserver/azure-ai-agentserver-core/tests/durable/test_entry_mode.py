# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for TaskContext.entry_mode across all lifecycle paths."""

from pathlib import Path

import pytest

from azure.ai.agentserver.core.durable import (
    TaskContext,
    task)


class TestEntryMode:
    """Verify ctx.entry_mode is set correctly for each lifecycle path."""

    async def _setup_manager(self, tmp_path):
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
    async def test_fresh_start_entry_mode(self, tmp_path) -> None:
        """First call to .run() produces entry_mode='fresh'."""
        observed_modes: list[str] = []

        @task(title="test-fresh")
        async def my_task(ctx: TaskContext[str]) -> str:
            observed_modes.append(ctx.entry_mode)
            return "done"

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            result = await my_task.run(task_id="fresh-1", input="hello")
            assert result == "done"
            assert observed_modes == ["fresh"]
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_developer_resume_entry_mode(self, tmp_path) -> None:
        """Calling .run() on a suspended task produces entry_mode='resumed' with new input."""
        observed: list[tuple[str, str]] = []

        @multi_turn_task(title="test-resume")
        async def my_task(ctx: TaskContext[str]) -> str:
            observed.append((ctx.entry_mode, ctx.input))
            return {"partial": True}

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            # First call — fresh start, suspends
            result1 = await my_task.run(task_id="resume-1", input="turn-1")
    # spec 022: result is raw output (Suspended wrapper removed)
            assert observed == [("fresh", "turn-1")]

            # Second call — should resume with new input
            result2 = await my_task.run(task_id="resume-1", input="turn-2")
    # spec 022: result is raw output (Suspended wrapper removed)
            assert observed[-1] == ("resumed", "turn-2")
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.skip(reason="spec 022 FR-049: handle_resume removed; resume is via .start() against suspended task")
    @pytest.mark.asyncio
    async def test_platform_resume_entry_mode(self, tmp_path) -> None:
        """Platform-initiated resume (handle_resume) produces entry_mode='resumed'."""
        observed: list[str] = []

        @multi_turn_task(title="test-platform-resume")
        async def my_task(ctx: TaskContext[str]) -> str:
            observed.append(ctx.entry_mode)
            return "waiting"

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            # Fresh start — suspends
            result = await my_task.run(task_id="platform-resume-1", input="init")
    # spec 022: result is raw output (Suspended wrapper removed)
            assert observed == ["fresh"]

            # Platform-initiated resume
            # spec 022 FR-049: manager.handle_resume removed; resume is via .start()/.run() against suspended task
            pass
            # Give the background task time to run
            import asyncio

            await asyncio.sleep(0.2)
            assert "resumed" in observed
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_recovered_entry_mode(self, tmp_path) -> None:
        """Calling .run() on a stale in_progress task produces entry_mode='recovered'."""
        observed: list[str] = []

        @multi_turn_task(title="test-recover")
        async def my_task(ctx: TaskContext[str]) -> str:
            observed.append(ctx.entry_mode)
            return "recovered-ok"

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            from azure.ai.agentserver.core.durable._models import (
                TaskCreateRequest)

            # Manually create a stale in_progress task
            await manager.provider.create(
                TaskCreateRequest(
                    id="stale-1",
                    agent_name="test-agent",
                    session_id="test-session",
                    status="in_progress",
                    title="stale-test",
                    payload={"input": "old-data"})
            )

            # Backdate the updated_at to make it stale
            task_file = (
                Path(str(tmp_path)) / "test-agent" / "test-session" / "stale-1.json"
            )
            if task_file.exists():
                import json

                data = json.loads(task_file.read_text())
                data["updated_at"] = "2020-01-01T00:00:00+00:00"
                task_file.write_text(json.dumps(data))

            result = await my_task.run(
                task_id="stale-1",
                input="new-data")
            assert result == "recovered-ok"
            assert observed == ["recovered"]
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_ignoring_entry_mode_works(self, tmp_path) -> None:
        """A function that never reads entry_mode still works fine."""

        @task(title="test-ignore")
        async def my_task(ctx: TaskContext[str]) -> str:
            # Deliberately NOT reading ctx.entry_mode
            return f"processed: {ctx.input}"

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            result = await my_task.run(task_id="ignore-1", input="data")
            assert result == "processed: data"
        finally:
            await self._teardown_manager(manager, mgr_mod)


class TestContextFieldsSpec015:
    """Spec 015 Phase 3 (FR-007) surface contract for renamed TaskContext fields."""

    def test_task_context_retry_attempt_field_present(self) -> None:
        """FR-007: ``ctx.run_attempt`` is renamed to ``ctx.retry_attempt``.

        Permanent rename — no deprecation alias.
        """
        from azure.ai.agentserver.core.durable._context import TaskContext

        assert "retry_attempt" in TaskContext.__slots__, (
            "retry_attempt must be a TaskContext slot after Spec 015 "
            "Phase 3 (FR-007 rename)."
        )
        assert "run_attempt" not in TaskContext.__slots__, (
            "Old field name 'run_attempt' must be removed (no deprecation alias)."
        )

    def test_task_context_recovery_count_field_present(self) -> None:
        """FR-007: ``ctx.lease_generation`` is renamed to ``ctx.recovery_count``.

        Permanent rename — no deprecation alias.
        """
        from azure.ai.agentserver.core.durable._context import TaskContext

        assert "recovery_count" in TaskContext.__slots__, (
            "recovery_count must be a TaskContext slot after Spec 015 "
            "Phase 3 (FR-007 rename)."
        )
        assert "lease_generation" not in TaskContext.__slots__, (
            "Old field name 'lease_generation' must be removed (no deprecation alias)."
        )


# ---------------------------------------------------------------------------
# Spec 015 Phase 4 (FR-001 / FR-003) — recovery x retry_attempt interaction
# ---------------------------------------------------------------------------


class TestRecoveryRetryAttempt:
    """FR-001 / FR-003 — the recovery code path MUST surface (not consume)
    the persisted retry_attempt on the first handler invocation.

    This sits next to TestEntryMode because the assertion is about the
    intersection of ``entry_mode == 'recovered'`` and ``ctx.retry_attempt``;
    the deeper budget arithmetic lives in
    ``test_retry.py::TestRetryAttemptDurability``.
    """

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

    async def _seed_stale(self, manager, tmp_path, task_id, retry_attempt):
        import json

        from azure.ai.agentserver.core.durable._models import TaskCreateRequest

        await manager.provider.create(
            TaskCreateRequest(
                id=task_id,
                agent_name="test-agent",
                session_id="test-session",
                status="in_progress",
                title="recovered-retry",
                payload={"input": "x", "_retry_attempt": retry_attempt})
        )
        task_file = (
            Path(str(tmp_path)) / "test-agent" / "test-session" / f"{task_id}.json"
        )
        data = json.loads(task_file.read_text())
        data["updated_at"] = "2020-01-01T00:00:00+00:00"
        task_file.write_text(json.dumps(data))

    @pytest.mark.asyncio
    async def test_recovered_handler_sees_persisted_retry_attempt(
        self, tmp_path
    ) -> None:
        """FR-001: a handler entering via ``entry_mode='recovered'`` MUST
        see ``ctx.retry_attempt`` populated from ``payload["_retry_attempt"]``.

        Equivalent to the test in ``test_retry.py`` but asserts the
        entry-mode invariant alongside the counter value, since both must
        be true *at the same time* on the first handler invocation of a
        recovered lifetime.
        """
        observed: list[tuple[str, int]] = []

        @multi_turn_task(title="rec-attempt")
        async def my_task(ctx: TaskContext[str]) -> str:
            observed.append((ctx.entry_mode, ctx.retry_attempt))
            return "done"

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            await self._seed_stale(manager, tmp_path, "rec-attempt-1", retry_attempt=3)
            result = await my_task.run(
                task_id="rec-attempt-1",
                input="ignored")
            assert result == "done"
            assert observed == [("recovered", 3)], (
                "FR-001 violated: recovered handler must see entry_mode="
                "'recovered' AND retry_attempt=3 (the persisted value) on "
                f"the first invocation; got {observed!r}."
            )
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_recovery_entry_mode_does_not_increment_retry_attempt(
        self, tmp_path
    ) -> None:
        """FR-003: entering with ``entry_mode='recovered'`` MUST NOT bump
        the counter — the persisted value is observed verbatim.

        Pairs with ``test_crash_recovery_does_not_consume_retry_budget`` but
        asserts the per-invocation behavior at the entry boundary, before
        any handler-raised exception is observed.
        """
        observed: list[int] = []

        @multi_turn_task(title="rec-no-bump")
        async def my_task(ctx: TaskContext[str]) -> str:
            observed.append(ctx.retry_attempt)
            return "ok"

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            await self._seed_stale(manager, tmp_path, "rec-no-bump-1", retry_attempt=1)
            await my_task.run(
                task_id="rec-no-bump-1",
                input="ignored")
            assert observed == [1], (
                "FR-003 violated: recovery entry MUST surface "
                f"retry_attempt=1 verbatim; got {observed!r}. "
                "(Recovery is not a failure-retry.)"
            )
        finally:
            await self._teardown_manager(manager, mgr_mod)


class TestEntryModeV2Matrix:
    """FR-063 + SC-013 — entry_mode matrix (6 scenarios)."""

    async def _setup_manager(self, tmp_path, *, startup=True):
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
        if startup:
            await manager.startup()
        return manager, mgr_mod, provider

    async def _teardown_manager(self, manager, mgr_mod):
        await manager.shutdown()
        mgr_mod._manager = None

    def _multi_turn_task(self, *args, **kwargs):
        from azure.ai.agentserver.core.durable import multi_turn_task

        return multi_turn_task(*args, **kwargs)

    async def _eventually(self, predicate, *, attempts=40):
        import asyncio

        for _ in range(attempts):
            if predicate():
                return
            await asyncio.sleep(0.05)
        assert predicate()

    async def _seed_recoverable_record(self, provider, *, task_id, task_name, input_value):
        import datetime

        from azure.ai.agentserver.core.durable._lease import derive_lease_owner
        from azure.ai.agentserver.core.durable._models import TaskCreateRequest

        created = await provider.create(
            TaskCreateRequest(
                id=task_id,
                agent_name="test-agent",
                session_id="test-session",
                status="in_progress",
                title=task_name,
                payload={"input": input_value, "_last_input_id": "seed-input"},
                tags={"_task_name": task_name},
                source={"name": task_name, "type": "agentserver.task"},
                lease_owner=derive_lease_owner("test-agent", "test-session"),
                lease_instance_id="previous-instance",
                lease_duration_seconds=60)
        )
        created.lease.expires_at = (
            datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=10)
        ).isoformat()
        provider._write_task(created)  # noqa: SLF001

    @pytest.mark.asyncio
    async def test_entry_mode_fresh_one_shot(self, tmp_path) -> None:
        observed_modes: list[str] = []

        @task(title="fr063-fresh-one-shot")
        async def my_task(ctx: TaskContext[str]) -> str:
            observed_modes.append(ctx.entry_mode)
            return "done"

        manager, mgr_mod, _ = await self._setup_manager(tmp_path)
        try:
            assert await my_task.run(task_id="fr063-fresh-one-shot", input="hello") == "done"
            assert observed_modes == ["fresh"]
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_entry_mode_fresh_multi_turn(self, tmp_path) -> None:
        observed_modes: list[str] = []

        @self._multi_turn_task(name="fr063-fresh-multi-turn")
        async def my_task(ctx: TaskContext[str]) -> str:
            observed_modes.append(ctx.entry_mode)
            return "done"

        manager, mgr_mod, _ = await self._setup_manager(tmp_path)
        try:
            assert await my_task.run(task_id="fr063-fresh-multi-turn", input="hello") == "done"
            assert observed_modes == ["fresh"]
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_entry_mode_resumed_after_suspend(self, tmp_path) -> None:
        observed: list[tuple[str, str]] = []

        @self._multi_turn_task(name="fr063-resumed-after-suspend")
        async def my_task(ctx: TaskContext[str]) -> str:
            observed.append((ctx.entry_mode, ctx.input))
            return f"done-{ctx.input}"

        manager, mgr_mod, _ = await self._setup_manager(tmp_path)
        try:
            assert await my_task.run(task_id="fr063-resumed", input="one") == "done-one"
            assert await my_task.run(task_id="fr063-resumed", input="two") == "done-two"
            assert observed == [("fresh", "one"), ("resumed", "two")]
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_entry_mode_resumed_steering_promotion(self, tmp_path) -> None:
        import asyncio

        observed: list[tuple[str, str, bool]] = []

        @self._multi_turn_task(name="fr063-steering-promotion", steerable=True)
        async def my_task(ctx: TaskContext[str]) -> str:
            observed.append((ctx.entry_mode, ctx.input, ctx.is_steered_turn))
            if ctx.input == "one":
                await asyncio.wait_for(ctx.cancel.wait(), timeout=1.0)
            return f"done-{ctx.input}"

        manager, mgr_mod, _ = await self._setup_manager(tmp_path)
        try:
            first = await my_task.start(task_id="fr063-steer", input="one", input_id="i1")
            await asyncio.sleep(0)
            second = await my_task.start(task_id="fr063-steer", input="two", input_id="i2")
            assert await first.result() == "done-one"
            assert await second.result() == "done-two"
            assert ("resumed", "two", True) in observed
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_entry_mode_recovered_scanner_reclaim(self, tmp_path) -> None:
        observed: list[tuple[str, str]] = []

        @self._multi_turn_task(name="fr063-scanner-reclaim")
        async def my_task(ctx: TaskContext[str]) -> str:
            observed.append((ctx.entry_mode, ctx.input))
            return "recovered"

        manager, mgr_mod, provider = await self._setup_manager(tmp_path, startup=False)
        await self._seed_recoverable_record(
            provider,
            task_id="fr063-scanner",
            task_name="fr063-scanner-reclaim",
            input_value="persisted")
        try:
            await manager.startup()
            await self._eventually(lambda: observed)
            assert observed == [("recovered", "persisted")]
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_entry_mode_recovered_inline_reclaim(self, tmp_path) -> None:
        observed: list[tuple[str, str]] = []

        @self._multi_turn_task(name="fr063-inline-reclaim")
        async def my_task(ctx: TaskContext[str]) -> str:
            observed.append((ctx.entry_mode, ctx.input))
            return "recovered"

        manager, mgr_mod, provider = await self._setup_manager(tmp_path)
        await self._seed_recoverable_record(
            provider,
            task_id="fr063-inline",
            task_name="fr063-inline-reclaim",
            input_value="persisted")
        try:
            run = await my_task.start(task_id="fr063-inline", input="new-caller-input")
            assert await run.result() == "recovered"
            assert observed == [("recovered", "persisted")]
        finally:
            await self._teardown_manager(manager, mgr_mod)
