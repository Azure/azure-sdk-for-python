# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
""" metadata facade and lifecycle auto-flush coverage."""

from __future__ import annotations

import asyncio
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest

from azure.ai.agentserver.core.tasks import RetryPolicy, TaskCancelled, TaskContext, TaskFailed, TaskMetadata, task


def _multi_turn_task(*args: Any, **kwargs: Any) -> Any:
    from azure.ai.agentserver.core.tasks import multi_turn_task

    return multi_turn_task(*args, **kwargs)


async def _setup_manager(tmp_path: Path, provider_factory: Any | None = None) -> tuple[Any, Any, Any]:
    from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
    from azure.ai.agentserver.core.tasks._manager import TaskManager
    import azure.ai.agentserver.core.tasks._manager as mgr_mod

    provider = LocalFileTaskProvider(Path(str(tmp_path)))
    if provider_factory is not None:
        provider = provider_factory(provider)
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


def _payload_patches(provider: Any, task_id: str) -> list[dict[str, Any]]:
    return [
        patch.payload
        for observed_id, patch, _ in getattr(provider, "update_calls", [])
        if observed_id == task_id and getattr(patch, "payload", None)
    ]


def _assert_metadata_patch(provider: Any, task_id: str, expected: dict[str, Any]) -> None:
    patches = _payload_patches(provider, task_id)
    assert any(patch.get("metadata", {}).items() >= expected.items() for patch in patches), patches


class TestTaskMetadataDunders:
    """— TaskMetadata exposes standard mapping protocol."""

    def test_getitem(self) -> None:
        meta = TaskMetadata({"k": "v"})
        assert meta["k"] == "v"

    def test_setitem(self) -> None:
        meta = TaskMetadata()
        meta["k"] = {"nested": True}
        assert meta["k"] == {"nested": True}

    def test_delitem(self) -> None:
        meta = TaskMetadata({"k": "v"})
        del meta["k"]
        assert "k" not in meta

    def test_contains(self) -> None:
        meta = TaskMetadata({"k": "v"})
        assert "k" in meta
        assert "missing" not in meta

    def test_iter(self) -> None:
        meta = TaskMetadata({"b": 2, "a": 1})
        assert sorted(iter(meta)) == ["a", "b"]

    def test_get_with_default(self) -> None:
        meta = TaskMetadata({"k": "v"})
        assert meta.get("k", "fallback") == "v"
        assert meta.get("missing", "fallback") == "fallback"


class TestTaskMetadataNamespace:
    """— ctx.metadata(namespace) returns sub-facade; reserved _ prefix raises."""

    def test_namespace_callable_returns_subfacade(self) -> None:
        meta = TaskMetadata()
        meta["k"] = "default"
        ns = meta("my_ns")
        ns["k"] = "namespaced"

        assert meta["k"] == "default"
        assert ns["k"] == "namespaced"
        assert meta("my_ns")["k"] == "namespaced"

    def test_reserved_underscore_prefix_accessible_at_primitive_level(self) -> None:
        """The CORE primitive does NOT enforce the underscore-namespace
        reservation — that's a wrapper-layer (ResilienceContext) concern.

        Framework-layered code (the responses orchestrator) reaches its
        reserved namespaces such as ``_responses`` through this primitive
        API directly; if the primitive rejected the prefix, that
        framework-internal access would break.

        See ``test_metadata.py::test_underscore_namespace_not_enforced_by_primitive``
        for the authoritative version of this contract clause.
        """
        meta = TaskMetadata()
        # No ValueError — primitive accepts the name.
        ns = meta("_framework")
        ns["state"] = "ok"
        assert ns["state"] == "ok"
        assert meta("_framework") is ns


class TestAutoFlushLifecycle:
    """— auto-flush at suspend/success/cancel/retry-exhausted boundaries."""

    @pytest.mark.asyncio
    async def test_metadata_flushed_at_suspend(self, tmp_path: Path, capturing_provider_factory: Any) -> None:
        @_multi_turn_task(name="fr045-flush-suspend")
        async def handler(ctx: TaskContext[str]) -> str:
            ctx.metadata["boundary"] = "suspend"
            return "turn-complete"

        manager, mgr_mod, provider = await _setup_manager(tmp_path, capturing_provider_factory)
        try:
            result = await handler.run(task_id="fr045-suspend", input="one")
            assert result == "turn-complete"
            _assert_metadata_patch(provider, "fr045-suspend", {"boundary": "suspend"})
        finally:
            await _teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_metadata_flushed_at_success(self, tmp_path: Path, capturing_provider_factory: Any) -> None:
        @task(name="fr045-flush-success")
        async def handler(ctx: TaskContext[str]) -> str:
            ctx.metadata["boundary"] = "success"
            return "done"

        manager, mgr_mod, provider = await _setup_manager(tmp_path, capturing_provider_factory)
        try:
            result = await handler.run(task_id="fr045-success", input="one")
            assert result == "done"
            _assert_metadata_patch(provider, "fr045-success", {"boundary": "success"})
        finally:
            await _teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_metadata_flushed_at_cancel(self, tmp_path: Path, capturing_provider_factory: Any) -> None:
        @_multi_turn_task(name="fr045-flush-cancel")
        async def handler(ctx: TaskContext[str]) -> str:
            ctx.metadata["boundary"] = "cancel"
            raise asyncio.CancelledError()

        manager, mgr_mod, provider = await _setup_manager(tmp_path, capturing_provider_factory)
        try:
            run = await handler.start(task_id="fr045-cancel", input="one")
            with pytest.raises(TaskCancelled):
                await run.result()
            _assert_metadata_patch(provider, "fr045-cancel", {"boundary": "cancel"})
        finally:
            await _teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_metadata_flushed_at_retry_exhausted(self, tmp_path: Path, capturing_provider_factory: Any) -> None:
        @_multi_turn_task(
            name="fr045-flush-retry-exhausted", retry=RetryPolicy.fixed_delay(delay=timedelta(0), max_attempts=2)
        )
        async def handler(ctx: TaskContext[str]) -> str:
            ctx.metadata["boundary"] = f"retry-{ctx.retry_attempt}"
            raise RuntimeError("boom")

        manager, mgr_mod, provider = await _setup_manager(tmp_path, capturing_provider_factory)
        try:
            run = await handler.start(task_id="fr045-retry", input="one")
            with pytest.raises(TaskFailed):
                await run.result()
            _assert_metadata_patch(provider, "fr045-retry", {"boundary": "retry-1"})
        finally:
            await _teardown_manager(manager, mgr_mod)


class TestAutoFlushLoadBearingOnRaise:
    """+ SC-011 — multi-turn raise auto-flush is load-bearing for next turn."""

    @pytest.mark.asyncio
    async def test_metadata_visible_to_next_turn_after_raise(self, tmp_path: Path) -> None:
        observed: list[str | None] = []

        @_multi_turn_task(name="fr045-raise-visible")
        async def handler(ctx: TaskContext[str]) -> str:
            if ctx.input == "fail":
                ctx.metadata["last_failure"] = "X"
                raise RuntimeError("first turn failed")
            observed.append(ctx.metadata.get("last_failure"))
            return "ok"

        manager, mgr_mod, _ = await _setup_manager(tmp_path)
        try:
            with pytest.raises(TaskFailed):
                await handler.run(task_id="fr045-raise", input="fail")
            assert await handler.run(task_id="fr045-raise", input="next") == "ok"
            assert observed == ["X"]
        finally:
            await _teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_metadata_visible_after_cooperative_cancel(self, tmp_path: Path) -> None:
        observed: list[str | None] = []

        @_multi_turn_task(name="fr045-cancel-visible")
        async def handler(ctx: TaskContext[str]) -> str:
            if ctx.input == "cancel":
                ctx.metadata["cancel_marker"] = "seen"
                raise asyncio.CancelledError()
            observed.append(ctx.metadata.get("cancel_marker"))
            return "ok"

        manager, mgr_mod, _ = await _setup_manager(tmp_path)
        try:
            run = await handler.start(task_id="fr045-cancel-visible", input="cancel")
            with pytest.raises(TaskCancelled):
                await run.result()
            assert await handler.run(task_id="fr045-cancel-visible", input="next") == "ok"
            assert observed == ["seen"]
        finally:
            await _teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_metadata_visible_after_retry_exhausted(self, tmp_path: Path) -> None:
        observed: list[str | None] = []

        @_multi_turn_task(name="fr045-retry-visible", retry=RetryPolicy.fixed_delay(delay=timedelta(0), max_attempts=2))
        async def handler(ctx: TaskContext[str]) -> str:
            if ctx.input == "fail":
                ctx.metadata["retry_marker"] = f"attempt-{ctx.retry_attempt}"
                raise RuntimeError("fail until exhausted")
            observed.append(ctx.metadata.get("retry_marker"))
            return "ok"

        manager, mgr_mod, _ = await _setup_manager(tmp_path)
        try:
            with pytest.raises(TaskFailed):
                await handler.run(task_id="fr045-retry-visible", input="fail")
            assert await handler.run(task_id="fr045-retry-visible", input="next") == "ok"
            assert observed == ["attempt-1"]
        finally:
            await _teardown_manager(manager, mgr_mod)


class TestOneShotMetadataInvocationLocal:
    """— one-shot metadata has no cross-invocation visibility (record deleted)."""

    @pytest.mark.asyncio
    async def test_one_shot_metadata_gone_after_terminal(self, tmp_path: Path) -> None:
        @task(name="fr046-one-shot-local")
        async def handler(ctx: TaskContext[str]) -> str:
            ctx.metadata["x"] = "y"
            return "done"

        manager, mgr_mod, _ = await _setup_manager(tmp_path)
        try:
            assert await handler.run(task_id="fr046-one-shot", input="one") == "done"
            assert await manager.provider.get("fr046-one-shot") is None
        finally:
            await _teardown_manager(manager, mgr_mod)
