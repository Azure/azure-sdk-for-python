# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Persistence, native listing, and isolation for the Core-backed task store."""

import base64
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest
from a2a.auth.user import User
from a2a.helpers import new_text_message
from a2a.server.context import ServerCallContext
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import Artifact, ListTasksRequest, Part, Task, TaskState, TaskStatus

from azure.ai.agentserver.a2a import FoundryTaskStore
from azure.ai.agentserver.core import (
    FoundryAgentRequestContext,
    get_request_context,
    reset_request_context,
    set_request_context,
)
from azure.ai.agentserver.core.storage import FoundryStateStore, StateStoreItemKeyPage


class _User(User):
    def __init__(self, name):
        self.name = name

    @property
    def is_authenticated(self):
        return True

    @property
    def user_name(self):
        return self.name


@pytest.fixture(autouse=True)
def local_state(monkeypatch, tmp_path):
    monkeypatch.delenv("FOUNDRY_HOSTING_ENVIRONMENT", raising=False)
    monkeypatch.setenv("AGENTSERVER_STATE_ROOT", str(tmp_path))
    token = set_request_context(FoundryAgentRequestContext())
    yield
    reset_request_context(token)


def _task(task_id="task-1", *, context_id="conversation", state=TaskState.TASK_STATE_COMPLETED):
    message = new_text_message("hello")
    message.message_id = "message-1"
    return Task(
        id=task_id,
        context_id=context_id,
        status=TaskStatus(state=state),
        artifacts=[Artifact(artifact_id="result", parts=[Part(text="saved answer")])],
        history=[message],
    )


@pytest.mark.asyncio
async def test_roundtrip_survives_new_store_instance_and_preserves_snapshot():
    context = ServerCallContext()
    task = _task()
    task.metadata.update({"nested": {"count": 3, "enabled": True}})
    expected = Task()
    expected.CopyFrom(task)
    async with FoundryTaskStore("test") as store:
        await store.save(task, context)
        task.artifacts[0].parts[0].text = "mutated after saving"
        loaded = await store.get("task-1", context)
        assert loaded == expected
        loaded.artifacts[0].parts[0].text = "mutated after reading"
        assert await store.get("task-1", context) == expected
    async with FoundryTaskStore("test") as restarted:
        assert await restarted.get("task-1", context) == expected


@pytest.mark.asyncio
async def test_missing_reads_and_lists_do_not_create_store(tmp_path):
    async with FoundryTaskStore("absent") as store:
        assert await store.get("missing", ServerCallContext()) is None
        assert not (await store.list(ListTasksRequest(), ServerCallContext())).tasks
    assert not list(tmp_path.rglob("*.json"))


@pytest.mark.asyncio
async def test_save_replaces_and_delete_removes_task():
    context = ServerCallContext()
    async with FoundryTaskStore("test") as store:
        await store.save(_task(state=TaskState.TASK_STATE_WORKING), context)
        await store.save(_task(), context)
        assert (await store.get("task-1", context)).status.state == TaskState.TASK_STATE_COMPLETED
        await store.delete("task-1", context)
        assert await store.get("task-1", context) is None
        await store.delete("task-1", context)


@pytest.mark.asyncio
async def test_native_users_and_tenants_are_isolated():
    alice = ServerCallContext(user=_User("alice"), tenant="tenant-1")
    bob = ServerCallContext(user=_User("bob"), tenant="tenant-1")
    other_tenant = ServerCallContext(user=_User("alice"), tenant="tenant-2")
    async with FoundryTaskStore("test") as store:
        await store.save(_task(), alice)
        for other in (bob, other_tenant):
            assert await store.get("task-1", other) is None
            assert not (await store.list(ListTasksRequest(), other)).tasks
            await store.delete("task-1", other)
        assert await store.get("task-1", alice) == _task()


@pytest.mark.asyncio
async def test_platform_callers_are_isolated_with_anonymous_native_context():
    context = ServerCallContext()
    async with FoundryTaskStore("test") as store:
        token = set_request_context(FoundryAgentRequestContext(user_id="user-1"))
        try:
            await store.save(_task(), context)
        finally:
            reset_request_context(token)
        token = set_request_context(FoundryAgentRequestContext(user_id="user-2"))
        try:
            assert await store.get("task-1", context) is None
            assert not (await store.list(ListTasksRequest(), context)).tasks
        finally:
            reset_request_context(token)
        token = set_request_context(FoundryAgentRequestContext(user_id="user-1"))
        try:
            assert await store.get("task-1", context) == _task()
        finally:
            reset_request_context(token)


@pytest.mark.asyncio
async def test_agents_using_different_stores_are_isolated():
    context = ServerCallContext()
    async with FoundryTaskStore("agent-1") as first, FoundryTaskStore("agent-2") as second:
        await first.save(_task(), context)
        assert await second.get("task-1", context) is None


@pytest.mark.asyncio
async def test_listing_matches_native_filters_order_and_pagination_across_backend_pages():
    context = ServerCallContext(user=_User("alice"))
    native = InMemoryTaskStore()
    async with FoundryTaskStore("test") as store:
        for index in range(105):
            task = _task(
                f"task-{index:03}",
                context_id="even" if index % 2 == 0 else "odd",
                state=TaskState.TASK_STATE_WORKING if index % 3 == 0 else TaskState.TASK_STATE_COMPLETED,
            )
            task.status.timestamp.FromSeconds(index + 1)
            await store.save(task, context)
            await native.save(task, context)
        request = ListTasksRequest(context_id="even", status=TaskState.TASK_STATE_COMPLETED, page_size=7)
        request.status_timestamp_after.FromSeconds(10)
        backend = await store._store()
        with patch.object(backend, "get_item", wraps=backend.get_item) as read:
            first = await store.list(request, context)
            assert first == await native.list(request, context)
            assert read.await_count == 7
            assert first.next_page_token
            request.page_token = first.next_page_token
            read.reset_mock()
            assert await store.list(request, context) == await native.list(request, context)
            assert read.await_count == 7


@pytest.mark.asyncio
async def test_one_task_page_reads_only_one_full_snapshot_from_105_large_tasks():
    context = ServerCallContext()
    native = InMemoryTaskStore()
    async with FoundryTaskStore("test") as store:
        for index in range(105):
            task = _task(f"task-{index:03}")
            task.artifacts[0].parts[0].text = "large artifact" * 1000
            task.history[0].parts[0].text = "large history" * 1000
            task.status.timestamp.FromNanoseconds(index * 1000000000 + 123)
            await store.save(task, context)
            await native.save(task, context)
        backend = await store._store()
        with patch.object(backend, "get_item", wraps=backend.get_item) as read:
            request = ListTasksRequest(page_size=1)
            for _ in range(2):
                page = await store.list(request, context)
                assert page == await native.list(request, context)
                assert read.await_count == 1
                assert page.total_size == 105
                request.page_token = page.next_page_token
                read.reset_mock()


@pytest.mark.asyncio
async def test_listing_reads_full_snapshot_when_summary_is_absent():
    context = ServerCallContext()
    task = _task()
    async with FoundryTaskStore("test") as store:
        await store.save(task, context)
        backend = await store._store()
        owner = store._owner(context)
        key = store._key(task.id, owner)
        await backend.set_item(
            key,
            {"task": base64.b64encode(task.SerializeToString()).decode("ascii")},
            tags={"a2a_owner": owner},
        )
        with patch.object(backend, "get_item", wraps=backend.get_item) as read:
            assert list((await store.list(ListTasksRequest(), context)).tasks) == [task]
            assert read.await_count == 1


@pytest.mark.asyncio
async def test_listing_metadata_tracks_updates_missing_timestamps_and_deletion():
    context = ServerCallContext()
    native = InMemoryTaskStore()
    async with FoundryTaskStore("test") as store:
        for task in (
            _task("no-timestamp"),
            _task("first", state=TaskState.TASK_STATE_WORKING),
            _task("second"),
        ):
            if task.id != "no-timestamp":
                task.status.timestamp.FromNanoseconds(1000000001)
            await store.save(task, context)
            await native.save(task, context)
        updated = _task("first")
        updated.status.timestamp.FromNanoseconds(2000000002)
        await store.save(updated, context)
        await native.save(updated, context)
        await store.delete("second", context)
        await native.delete("second", context)
        request = ListTasksRequest(page_size=1, status=TaskState.TASK_STATE_COMPLETED)
        page = await store.list(request, context)
        assert page == await native.list(request, context)
        request.page_token = page.next_page_token
        assert await store.list(request, context) == await native.list(request, context)


@pytest.mark.asyncio
async def test_owner_tag_is_query_safe_and_identical_for_saving_and_listing(monkeypatch):
    backend = AsyncMock()
    backend.get.return_value = SimpleNamespace(user_isolation=True)
    backend.list_keys.return_value = StateStoreItemKeyPage(keys=[])
    monkeypatch.setattr(FoundryStateStore, "get_or_create", AsyncMock(return_value=backend))
    context = ServerCallContext(user=_User("alice"))
    async with FoundryTaskStore("test") as store:
        await store.save(_task(), context)
        tags = backend.set_item.call_args.kwargs["tags"]
        assert tags["a2a_owner"] == store._owner(context)
        assert all(key.isidentifier() for key in tags)
        summary = Task.FromString(base64.b64decode(tags["a2a_list"]))
        assert summary.id == "task-1" and summary.context_id == "conversation"
        assert summary.status.state == TaskState.TASK_STATE_COMPLETED
        assert not summary.history and not summary.artifacts
        await store.list(ListTasksRequest(), context)
        backend.list_keys.assert_awaited_once_with(tags={"a2a_owner": tags["a2a_owner"]}, limit=100, after=None)


@pytest.mark.asyncio
async def test_hosted_anonymous_operations_fail_before_accessing_storage(monkeypatch):
    monkeypatch.setenv("FOUNDRY_HOSTING_ENVIRONMENT", "hosted")
    create = AsyncMock()
    monkeypatch.setattr(FoundryStateStore, "get_or_create", create)
    async with FoundryTaskStore("test") as store:
        with pytest.raises(PermissionError, match="caller identity"):
            await store.save(_task(), ServerCallContext())
    create.assert_not_awaited()


@pytest.mark.asyncio
async def test_hosted_caller_uses_core_user_isolation_and_retains_request_context(monkeypatch):
    monkeypatch.setenv("FOUNDRY_HOSTING_ENVIRONMENT", "hosted")
    backend = AsyncMock()
    backend.get.return_value = SimpleNamespace(user_isolation=True)
    create = AsyncMock(return_value=backend)
    monkeypatch.setattr(FoundryStateStore, "get_or_create", create)
    token = set_request_context(FoundryAgentRequestContext(call_id="call-1", user_id="caller-1"))
    try:
        async with FoundryTaskStore("agent-store", item_ttl_seconds=600) as store:
            await store.save(_task(), ServerCallContext())
            create.assert_awaited_once_with(
                "agent-store", credential=None, endpoint=None, user_isolation=True, item_ttl_seconds=600
            )
            backend.set_item.assert_awaited_once()
        backend.aclose.assert_awaited_once()
    finally:
        reset_request_context(token)


@pytest.mark.asyncio
async def test_brokered_callers_remain_isolated_without_raw_user_headers(monkeypatch):
    monkeypatch.setenv("FOUNDRY_HOSTING_ENVIRONMENT", "hosted")
    callers = {"alice-1": "alice", "alice-2": "alice", "bob-1": "bob"}
    records = {}
    backend = AsyncMock()

    def caller():
        call_id = get_request_context().call_id
        if call_id not in callers:
            raise PermissionError("Unresolved brokered caller")
        return callers[call_id]

    async def descriptor():
        caller()
        return SimpleNamespace(user_isolation=True)

    async def write(key, value, **kwargs):
        records[(caller(), key)] = SimpleNamespace(key=key, value=value, tags=kwargs["tags"])

    async def read(key, **kwargs):
        return records.get((caller(), key))

    async def delete(key, **kwargs):
        records.pop((caller(), key), None)

    async def keys(**kwargs):
        return StateStoreItemKeyPage(
            keys=[
                SimpleNamespace(key=key, id=key, tags=item.tags)
                for (user, key), item in records.items()
                if user == caller()
            ]
        )

    backend.get.side_effect = descriptor
    backend.set_item.side_effect = write
    backend.get_item.side_effect = read
    backend.delete_item.side_effect = delete
    backend.list_keys.side_effect = keys
    monkeypatch.setattr(FoundryStateStore, "get_or_create", AsyncMock(return_value=backend))
    context = ServerCallContext()
    async with FoundryTaskStore("test") as store:
        token = set_request_context(FoundryAgentRequestContext(call_id="alice-1"))
        try:
            await store.save(_task(), context)
        finally:
            reset_request_context(token)
        token = set_request_context(FoundryAgentRequestContext(call_id="bob-1"))
        try:
            assert await store.get("task-1", context) is None
            assert not (await store.list(ListTasksRequest(), context)).tasks
            await store.delete("task-1", context)
            own = _task()
            own.artifacts[0].parts[0].text = "bob result"
            await store.save(own, context)
            assert await store.get("task-1", context) == own
        finally:
            reset_request_context(token)
        token = set_request_context(FoundryAgentRequestContext(call_id="alice-2"))
        try:
            assert await store.get("task-1", context) == _task()
            assert len((await store.list(ListTasksRequest(), context)).tasks) == 1
        finally:
            reset_request_context(token)
        token = set_request_context(FoundryAgentRequestContext(call_id="invalid"))
        try:
            with pytest.raises(PermissionError, match="Unresolved"):
                await store.get("task-1", context)
        finally:
            reset_request_context(token)


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", ["save", "get", "list", "delete"])
async def test_nonisolated_backing_store_is_rejected_before_item_access(monkeypatch, operation):
    backend = AsyncMock()
    backend.get.return_value = SimpleNamespace(user_isolation=False)
    factory = Mock(return_value=backend)
    factory.get_or_create = AsyncMock(return_value=backend)
    monkeypatch.setattr("azure.ai.agentserver.a2a._foundry_task_store.FoundryStateStore", factory)
    async with FoundryTaskStore("test") as store:
        with pytest.raises(PermissionError, match="user-isolated"):
            if operation == "save":
                await store.save(_task(), ServerCallContext())
            elif operation == "get":
                await store.get("task-1", ServerCallContext())
            elif operation == "list":
                await store.list(ListTasksRequest(), ServerCallContext())
            else:
                await store.delete("task-1", ServerCallContext())
    backend.set_item.assert_not_awaited()
    backend.get_item.assert_not_awaited()
    backend.list_keys.assert_not_awaited()
    backend.delete_item.assert_not_awaited()


@pytest.mark.asyncio
async def test_backing_isolation_is_rechecked_after_configuration_changes(monkeypatch):
    backend = AsyncMock()
    backend.get.return_value = SimpleNamespace(user_isolation=True)
    backend.get_item.return_value = None
    monkeypatch.setattr("azure.ai.agentserver.a2a._foundry_task_store.FoundryStateStore", lambda *a, **k: backend)
    async with FoundryTaskStore("test") as store:
        assert await store.get("missing", ServerCallContext()) is None
        backend.get.return_value = SimpleNamespace(user_isolation=False)
        with pytest.raises(PermissionError, match="user-isolated"):
            await store.get("missing", ServerCallContext())
    backend.get_item.assert_awaited_once()


@pytest.mark.asyncio
async def test_storage_failure_is_propagated_without_memory_fallback(monkeypatch):
    create = AsyncMock(side_effect=RuntimeError("storage unavailable"))
    monkeypatch.setattr(FoundryStateStore, "get_or_create", create)
    async with FoundryTaskStore("test") as store:
        with pytest.raises(RuntimeError, match="storage unavailable"):
            await store.save(_task(), ServerCallContext())
    create.assert_awaited_once()


@pytest.mark.asyncio
async def test_corrupt_record_does_not_return_another_task():
    context = ServerCallContext()
    async with FoundryTaskStore("test") as store:
        await store.save(_task(), context)
        async with FoundryStateStore("test") as backend:
            key = (await backend.list_keys()).keys[0].key
            wrong = _task("another-task")
            await backend.set_item(key, {"task": base64.b64encode(wrong.SerializeToString()).decode("ascii")})
        with pytest.raises(ValueError, match="identity"):
            await store.get("task-1", context)


@pytest.mark.asyncio
async def test_corrupt_listing_metadata_does_not_read_another_task():
    context = ServerCallContext()
    async with FoundryTaskStore("test") as store:
        await store.save(_task(), context)
        backend = await store._store()
        owner = store._owner(context)
        key = store._key("task-1", owner)
        item = await backend.get_item(key)
        tags = dict(item.tags)
        tags["a2a_list"] = base64.b64encode(_task("another-task").SerializeToString()).decode("ascii")
        await backend.set_item(key, item.value, tags=tags)
        with patch.object(backend, "get_item", wraps=backend.get_item) as read:
            with pytest.raises(ValueError, match="identity"):
                await store.list(ListTasksRequest(), context)
            read.assert_not_awaited()


@pytest.mark.asyncio
async def test_close_is_idempotent_and_closed_store_rejects_operations():
    store = FoundryTaskStore("test")
    await store.save(_task(), ServerCallContext())
    await store.aclose()
    await store.aclose()
    with pytest.raises(RuntimeError, match="closed"):
        await store.get("task-1", ServerCallContext())


def test_empty_store_name_is_rejected():
    with pytest.raises(ValueError, match="name"):
        FoundryTaskStore("")
