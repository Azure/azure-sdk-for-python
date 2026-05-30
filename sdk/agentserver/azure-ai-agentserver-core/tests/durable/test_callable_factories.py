# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for callable tag and description factories on @task."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

import pytest

from azure.ai.agentserver.core.durable import (
    TaskContext,
    task,
)


class _ManagerFixture:
    """Helper to set up a TaskManager with local file storage."""

    @staticmethod
    async def setup(tmp_path):
        from azure.ai.agentserver.core.durable._local_provider import (
            LocalFileTaskProvider,
        )
        from azure.ai.agentserver.core.durable._manager import (
            TaskManager,
        )

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
            },
        )()
        manager = TaskManager(config=config, provider=provider)
        mgr_mod._manager = manager
        await manager.startup()
        return manager, mgr_mod

    @staticmethod
    async def teardown(manager, mgr_mod):
        await manager.shutdown()
        mgr_mod._manager = None


class TestCallableTags:
    """Tests for callable tag factories on @task."""

    @pytest.mark.asyncio
    async def test_static_tags_preserved(self, tmp_path):
        """Static dict tags still work as before."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:

            @task(name="static_tags", tags={"env": "prod"}, ephemeral=False)
            async def my_task(ctx: TaskContext[Any]) -> str:
                return "done"

            task_id = uuid.uuid4().hex
            await my_task.run(task_id=task_id, input=None)

            task_record = await manager.provider.get(task_id)
            assert task_record.tags["env"] == "prod"

        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_callable_tags_factory(self, tmp_path):
        """Callable tags factory receives (input, task_id) and sets tags."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:

            @task(
                name="callable_tags",
                tags=lambda inp, tid: {"tenant": inp["tenant"], "tid": tid[:8]},
                ephemeral=False,
            )
            async def my_task(ctx: TaskContext[Any]) -> str:
                return "done"

            task_id = uuid.uuid4().hex
            await my_task.run(task_id=task_id, input={"tenant": "acme"})

            task_record = await manager.provider.get(task_id)
            assert task_record.tags["tenant"] == "acme"
            assert task_record.tags["tid"] == task_id[:8]

        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_callable_tags_merged_with_callsite(self, tmp_path):
        """Per-call tags merge on top of callable-resolved tags."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:

            @task(
                name="merge_tags",
                tags=lambda inp, tid: {"source": "factory"},
                ephemeral=False,
            )
            async def my_task(ctx: TaskContext[Any]) -> str:
                return "done"

            task_id = uuid.uuid4().hex
            await my_task.run(task_id=task_id, input=None, tags={"extra": "call-site"})

            task_record = await manager.provider.get(task_id)
            assert task_record.tags["source"] == "factory"
            assert task_record.tags["extra"] == "call-site"

        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_callable_tags_error_propagates(self, tmp_path):
        """If callable tags factory raises, the error propagates at creation."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:

            @task(
                name="bad_tags",
                tags=lambda inp, tid: 1 / 0,  # type: ignore[return-value]
            )
            async def my_task(ctx: TaskContext[Any]) -> str:
                return "done"

            with pytest.raises(ZeroDivisionError):
                await my_task.run(task_id=uuid.uuid4().hex, input=None)

        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)


class TestCallableDescription:
    """Tests for callable description factory on @task.

    Spec 015 Phase 3 FR-006: the per-task ``description`` knob (static + callable)
    has been removed from ``@task``. These tests are kept as a tombstone (the
    class is empty; pytest will skip the no-method case) so the historical
    intent is preserved alongside ``test_public_api_surface.py``'s coverage
    that ``description`` is no longer accepted.
    """


class TestFactoryValidation:
    """Tests for return type validation on callable factories."""

    @pytest.mark.asyncio
    async def test_tags_callable_bad_return_type(self, tmp_path):
        """Tags callable returning non-dict raises TypeError."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:

            @task(
                name="bad_tags_type",
                tags=lambda inp, tid: "not-a-dict",  # type: ignore[return-value]
            )
            async def my_task(ctx: TaskContext[Any]) -> str:
                return "done"

            with pytest.raises(TypeError, match="tags callable must return dict"):
                await my_task.run(task_id=uuid.uuid4().hex, input=None)

        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    def test_options_mixing_callable_and_dict_tags_raises(self):
        """Mixing callable and dict tags in options() raises TypeError."""

        @task(
            name="callable_tags_task",
            tags=lambda inp, tid: {"k": "v"},
        )
        async def my_task(ctx: TaskContext[Any]) -> str:
            return "done"

        with pytest.raises(TypeError, match="Cannot mix callable and dict"):
            my_task.options(tags={"override": "val"})

    def test_options_callable_to_callable_ok(self):
        """Replacing callable tags with another callable in options() works."""

        @task(
            name="callable_swap",
            tags=lambda inp, tid: {"old": "factory"},
        )
        async def my_task(ctx: TaskContext[Any]) -> str:
            return "done"

        updated = my_task.options(
            tags=lambda inp, tid: {"new": "factory"},
        )
        assert callable(updated._opts.tags)
