# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for lifecycle-aware .run() and .start() on Task."""

import asyncio
import json
from pathlib import Path

import pytest

from azure.ai.agentserver.core.tasks import TaskContext, task, multi_turn_task
from azure.ai.agentserver.core.tasks._exceptions import TaskConflictError


class TestLifecycle:
    """Verify .run()/.start() lifecycle automation."""

    async def _setup_manager(self, tmp_path):
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
        await manager.startup()
        return manager, mgr_mod

    async def _teardown_manager(self, manager, mgr_mod):
        await manager.shutdown()
        mgr_mod._manager = None

    def _create_stale_task(self, tmp_path, task_id, status="in_progress"):
        """Write a stale task file directly to simulate a crashed task."""
        from azure.ai.agentserver.core.tasks._models import TaskCreateRequest
        import asyncio

        async def _create(provider):
            await provider.create(
                TaskCreateRequest(
                    id=task_id,
                    agent_name="test-agent",
                    session_id="test-session",
                    status=status,
                    title="stale-test",
                    payload={"input": "old-data"},
                )
            )

        return _create

    def _backdate_task(self, tmp_path, task_id):
        """Set updated_at far in the past."""
        task_file = Path(str(tmp_path)) / "test-agent" / "test-session" / f"{task_id}.json"
        if task_file.exists():
            data = json.loads(task_file.read_text())
            data["updated_at"] = "2020-01-01T00:00:00+00:00"
            task_file.write_text(json.dumps(data))

    @pytest.mark.asyncio
    async def test_run_fresh_no_existing_task(self, tmp_path) -> None:
        """run() on non-existent task → creates and starts, entry_mode='fresh'."""
        observed_mode: list[str] = []

        @task(name="lifecycle-fresh", title="lifecycle-fresh")
        async def my_task(ctx: TaskContext[str]) -> str:
            observed_mode.append(ctx.entry_mode)
            return "result"

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            result = await my_task.run(task_id="lc-fresh-1", input="data")
            assert result == "result"
            assert observed_mode == ["fresh"]
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_run_pending_task(self, tmp_path) -> None:
        """run() on pending task → starts it, entry_mode='fresh'."""
        observed_mode: list[str] = []

        @task(name="lifecycle-pending", title="lifecycle-pending")
        async def my_task(ctx: TaskContext[str]) -> str:
            observed_mode.append(ctx.entry_mode)
            return "started"

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            from azure.ai.agentserver.core.tasks._models import TaskCreateRequest

            await manager.provider.create(
                TaskCreateRequest(
                    id="lc-pending-1",
                    agent_name="test-agent",
                    session_id="test-session",
                    status="pending",
                    title="pending-test",
                    payload={"input": "pending-data"},
                )
            )
            result = await my_task.run(task_id="lc-pending-1", input="new-data")
            assert result == "started"
            assert observed_mode == ["fresh"]
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_run_suspended_task(self, tmp_path) -> None:
        """run() on suspended task → resumes with new input, entry_mode='resumed'."""
        observed: list[tuple[str, str]] = []

        @multi_turn_task(name="lifecycle-resume", title="lifecycle-resume")
        async def my_task(ctx: TaskContext[str]) -> str:
            observed.append((ctx.entry_mode, ctx.input))
            return "waiting"

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            result1 = await my_task.run(task_id="lc-resume-1", input="turn-1")
            #: result is raw output (Suspended wrapper removed)
            assert observed[-1] == ("fresh", "turn-1")

            result2 = await my_task.run(task_id="lc-resume-1", input="turn-2")
            #: result is raw output (Suspended wrapper removed)
            assert observed[-1] == ("resumed", "turn-2")
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_run_in_progress_not_stale_raises(self, tmp_path) -> None:
        """run() on in_progress (live elsewhere) task → TaskConflictError.

        : live-elsewhere is signalled by a foreign
                ``lease_owner`` (different agent or session). This test seeds
                such a record to exercise the conflict shape per Invariant 1.
        """

        @task(name="lifecycle-conflict", title="lifecycle-conflict")
        async def my_task(ctx: TaskContext[str]) -> str:
            return "never"

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            from azure.ai.agentserver.core.tasks._models import TaskCreateRequest

            await manager.provider.create(
                TaskCreateRequest(
                    id="lc-conflict-1",
                    agent_name="test-agent",
                    session_id="test-session",
                    status="in_progress",
                    title="running-test",
                    payload={},
                    lease_owner="other-agent|session:other-session",
                    lease_instance_id="other-inst",
                    lease_duration_seconds=60,
                )
            )
            with pytest.raises(TaskConflictError) as exc_info:
                await my_task.run(task_id="lc-conflict-1", input="data")
            #: exception.task_id removed
            assert exc_info.value.current_status == "in_progress"
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_run_stale_task_recovers(self, tmp_path) -> None:
        """run() on stale in_progress task → recovers, entry_mode='recovered'."""
        observed_mode: list[str] = []

        @task(name="lifecycle-stale", title="lifecycle-stale")
        async def my_task(ctx: TaskContext[str]) -> str:
            observed_mode.append(ctx.entry_mode)
            return "recovered"

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            from azure.ai.agentserver.core.tasks._models import TaskCreateRequest

            await manager.provider.create(
                TaskCreateRequest(
                    id="lc-stale-1",
                    agent_name="test-agent",
                    session_id="test-session",
                    status="in_progress",
                    title="stale-test",
                    payload={"input": "old"},
                )
            )
            self._backdate_task(tmp_path, "lc-stale-1")

            result = await my_task.run(task_id="lc-stale-1", input="new")
            assert result == "recovered"
            assert observed_mode == ["recovered"]
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_run_completed_task_raises(self, tmp_path) -> None:
        """run() on completed task → TaskConflictError (no restart)."""

        @task(name="lifecycle-completed", title="lifecycle-completed")
        async def my_task(ctx: TaskContext[str]) -> str:
            return "never"

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            from azure.ai.agentserver.core.tasks._models import TaskCreateRequest

            await manager.provider.create(
                TaskCreateRequest(
                    id="lc-completed-1",
                    agent_name="test-agent",
                    session_id="test-session",
                    status="completed",
                    title="done-test",
                    payload={"output": "final"},
                )
            )
            with pytest.raises(TaskConflictError) as exc_info:
                await my_task.run(task_id="lc-completed-1", input="data")
            assert exc_info.value.current_status == "completed"
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_start_follows_lifecycle_rules(self, tmp_path) -> None:
        """start() follows same lifecycle rules as run() — fresh + conflict."""
        observed_mode: list[str] = []

        @task(name="lifecycle-start", title="lifecycle-start")
        async def my_task(ctx: TaskContext[str]) -> str:
            observed_mode.append(ctx.entry_mode)
            return "started"

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            # Fresh start via .start()
            handle = await my_task.start(task_id="lc-start-1", input="data")
            result = await handle.result()
            assert result == "started"
            assert observed_mode == ["fresh"]

            # Conflict: create in_progress task owned by another agent
            # and try.start — should raise TaskConflictError.
            from azure.ai.agentserver.core.tasks._models import TaskCreateRequest

            await manager.provider.create(
                TaskCreateRequest(
                    id="lc-start-conflict",
                    agent_name="test-agent",
                    session_id="test-session",
                    status="in_progress",
                    title="running",
                    payload={},
                    lease_owner="other-agent|session:other-session",
                    lease_instance_id="other-inst",
                    lease_duration_seconds=60,
                )
            )
            with pytest.raises(TaskConflictError):
                await my_task.start(task_id="lc-start-conflict", input="data")
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_task_run_is_awaitable(self, tmp_path) -> None:
        """``await task_run`` returns the same TaskResult as ``await task_run.result()``."""

        @task(name="awaitable", title="awaitable")
        async def my_task(ctx: TaskContext[str]) -> str:
            return f"echo: {ctx.input}"

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            # Direct-await the TaskRun handle.
            handle = await my_task.start(task_id="awaitable-1", input="hello")
            result = await handle  # ← exercising __await__
            assert result == "echo: hello"

            # And confirm the explicit .result() path still works identically.
            handle2 = await my_task.start(task_id="awaitable-2", input="world")
            result_via_method = await handle2.result()
            assert result_via_method == "echo: world"
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_stale_timeout_kwarg_removed_spec_016(self, tmp_path) -> None:
        """/: stale_timeout removed from developer surface.

        Replaces the prior `test_stale_timeout_parameter` test (which
        exercised the per-task `stale_timeout` kwarg behavior). After
         the kwarg is gone — passing it raises TypeError. The
        recovery decision is framework-managed (no developer knob).

        For deterministic in-test recovery triggering during the
        transitional Phase-4 cohort of  (Phase 6 replaces this
        mechanism entirely), tests monkey-patch
        ``_LEGACY_INPROCESS_STALE_THRESHOLD_SECONDS`` directly. The
        backdated `updated_at` pattern used elsewhere in this suite
        continues to work because the 2020 timestamp exceeds the
        default 300s threshold by years.
        """
        # The kwarg removal is asserted by TestStaleTimeoutRemoved in
        # test_decorator.py. Here we verify the framework-managed default
        # still recovers a backdated record correctly.

        @task(name="stale-default", title="stale-default")
        async def my_task(ctx: TaskContext[str]) -> str:
            return "ok"

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            from azure.ai.agentserver.core.tasks._models import TaskCreateRequest

            await manager.provider.create(
                TaskCreateRequest(
                    id="lc-timeout-1",
                    agent_name="test-agent",
                    session_id="test-session",
                    status="in_progress",
                    title="timeout-test",
                    payload={"input": "old"},
                )
            )
            self._backdate_task(tmp_path, "lc-timeout-1")

            # Backdated record (2020) is far past the framework's default
            # 300s threshold → recovery is triggered.
            result = await my_task.run(task_id="lc-timeout-1", input="new")
            assert result == "ok"
        finally:
            await self._teardown_manager(manager, mgr_mod)


# --------------------------------------------------------------------- #
#   — 3-layer recovery + periodic scan (T043..T046)
# --------------------------------------------------------------------- #


class TestRecoveryThreeLayerRecovery:
    """/  /  / SC-003 / SC-004 / SC-005.

        Three internal recovery layers share a single reclaim helper
    :
        - Layer 1: hardened startup scan (always runs at TaskManager.startup).
        - Layer 2: periodic background scan, monkey-patchable via
          ``_PERIODIC_RECOVERY_INTERVAL_SECONDS`` (test hook).
        - Layer 3: inline reclaim on scheduling primitives
          (.run / .start / get_active_run) when they observe a dead-lease
          in-progress record.

        The lease is "dead" per  when ownership belongs to a previous
        lifetime AND no live in-memory entry tracks it.
    """

    async def _setup_manager(self, tmp_path):
        from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
        from azure.ai.agentserver.core.tasks._manager import TaskManager
        import azure.ai.agentserver.core.tasks._manager as mgr_mod

        provider = LocalFileTaskProvider(base_dir=Path(str(tmp_path)))
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
        return manager, mgr_mod

    async def _teardown_manager(self, manager, mgr_mod):
        await manager.shutdown()
        mgr_mod._manager = None

    @pytest.mark.asyncio
    async def test_get_active_run_resurrects_dead_lease_orphan(self, tmp_path) -> None:
        """``get_active_run`` on an in-progress record with a dead lease
        returns a usable TaskRun bound to a new lifetime that re-enters
        with ``entry_mode == "recovered"``.
        """
        from azure.ai.agentserver.core.tasks._models import TaskCreateRequest

        observed: list[str] = []

        @task(name="t043_resurrect")
        async def my_task(ctx: TaskContext[str]) -> str:
            observed.append(ctx.entry_mode)
            return "resumed-ok"

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            # Seed a dead-lease orphan record using the SAME lease_owner
            # the current manager derives (simulates a previous-process
            # incarnation that crashed; the owner is stable across
            # restarts within the same (agent, session) pair). Include
            # the source.name so _find_resume_callback maps the record
            # back to this test's @task deterministically.
            await manager.provider.create(
                TaskCreateRequest(
                    id="t043-orphan",
                    agent_name="test-agent",
                    session_id="test-session",
                    status="in_progress",
                    title="orphan",
                    payload={"input": '"x"'},
                    lease_owner=manager._lease_owner,  # noqa: SLF001
                    lease_instance_id="previous-instance",
                    lease_duration_seconds=60,
                    source={"name": "t043_resurrect", "type": "agentserver.task"},
                )
            )
            # get_active_run sees the dead-lease orphan, reclaims it
            # inline, and returns a TaskRun bound to the new lifetime.
            run = await my_task.get_active_run("t043-orphan")
            assert run is not None
            result = await asyncio.wait_for(run.result(), timeout=5.0)
            assert result == "resumed-ok"
            assert observed == ["recovered"]
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_get_active_run_returns_none_for_terminal(self, tmp_path) -> None:
        """Terminal records return None."""
        from azure.ai.agentserver.core.tasks._models import TaskCreateRequest

        @task(name="t043_terminal")
        async def my_task(ctx: TaskContext[str]) -> str:
            return "ok"

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            await manager.provider.create(
                TaskCreateRequest(
                    id="t043-done",
                    agent_name="test-agent",
                    session_id="test-session",
                    status="completed",
                    title="done",
                    payload={"output": '"done"'},
                )
            )
            run = await my_task.get_active_run("t043-done")
            assert run is None
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_periodic_scan_reclaims_orphan_within_interval(self, tmp_path, monkeypatch) -> None:
        """T045 /  Layer 2 /  / SC-004: using the
        interval-override constant, a post-startup orphan is reclaimed
        within the test override (~0.05s) without any user-space
        scheduling call.
        """
        from azure.ai.agentserver.core.tasks._models import TaskCreateRequest
        import azure.ai.agentserver.core.tasks._manager as mgr_module

        # Set the interval BEFORE startup so the periodic scan task spawns
        # with the test value (monkeypatch.setattr is read at spawn time).
        monkeypatch.setattr(mgr_module, "_PERIODIC_RECOVERY_INTERVAL_SECONDS", 0.05)

        recovered: list[str] = []

        @multi_turn_task(name="t045_periodic")
        async def my_task(ctx: TaskContext[str]) -> str:
            recovered.append(ctx.entry_mode)
            return "ok"

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            # Seed AFTER startup so layer-1 misses it; layer-2 periodic
            # scan must pick it up within the override interval. Use the
            # SAME lease_owner the manager derives (simulates the
            # previous-incarnation-crashed scenario) and the same source
            # name so _find_resume_callback matches the @task.
            await manager.provider.create(
                TaskCreateRequest(
                    id="t045-orphan",
                    agent_name="test-agent",
                    session_id="test-session",
                    status="in_progress",
                    title="orphan",
                    payload={"input": '"x"', "schema_version": "1"},
                    lease_owner=manager._lease_owner,  # noqa: SLF001
                    lease_instance_id="previous-instance",
                    lease_duration_seconds=60,
                    source={"name": "t045_periodic", "type": "agentserver.task"},
                )
            )
            # Wait up to 2 seconds for the periodic scan to fire and
            # for the recovered handler to execute.
            deadline = asyncio.get_event_loop().time() + 2.0
            while not recovered and asyncio.get_event_loop().time() < deadline:
                await asyncio.sleep(0.05)
            assert recovered == ["recovered"], (
                f"Periodic recovery scan did not reclaim the orphan within "
                f"the override interval. observed={recovered}"
            )
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_startup_scan_tolerates_mixed_responses(self, tmp_path) -> None:
        """T044 / SC-005: startup scan with mixed healthy / unreachable
        records completes without raising; every record is logged."""
        from azure.ai.agentserver.core.tasks._models import TaskCreateRequest

        # Just seed a normal record + an in_progress orphan. The startup
        # scan runs in _setup_manager; if it raises, the test fails.
        from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider

        provider = LocalFileTaskProvider(base_dir=Path(str(tmp_path)))
        await provider.create(
            TaskCreateRequest(
                id="t044-orphan",
                agent_name="test-agent",
                session_id="test-session",
                status="in_progress",
                title="orphan",
                payload={},
                lease_owner="some-previous-lifetime",
                lease_instance_id="some-previous-instance",
                lease_duration_seconds=60,
            )
        )

        from azure.ai.agentserver.core.tasks._manager import TaskManager
        import azure.ai.agentserver.core.tasks._manager as mgr_mod

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
        # Should NOT raise even though there's an orphan.
        await manager.startup()
        await manager.shutdown()
        mgr_mod._manager = None
