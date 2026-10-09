# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Conformance tests for the :data:`streams` registry.

Asserts  — 6-method surface, default backing, idempotent
delete, tombstone retention (rule 36a), per-id atomicity (rule 34),
configurator semantics, and the third-party-impl invariant
.

See ``streaming.md`` §7 + §13 rules 33-38.
"""

from __future__ import annotations

import asyncio
import inspect
import json
import re
from pathlib import Path
from types import SimpleNamespace

import pytest
from anyio import CancelScope

from azure.ai.agentserver.core.streaming import (
    EventStream,
    EventStreamNotFoundError,
    EventStreamNotFoundError,
    streams,
)
from azure.ai.agentserver.core.streaming._concrete import (
    BroadcastEventStream,
    FileBackedReplayEventStream,
    ReplayEventStream,
)
from azure.ai.agentserver.core.streaming._registry import _StreamsRegistry


pytestmark = pytest.mark.asyncio(loop_scope="function")


@pytest.mark.parametrize("backing", ["memory", "file"])
async def test_many_missing_lookups_do_not_retain_lifecycle_locks(tmp_path: Path, backing: str) -> None:
    registry = _StreamsRegistry()
    if backing == "file":
        registry.use_file_backed_replay(storage_dir=tmp_path)
    for index in range(1000):
        with pytest.raises(EventStreamNotFoundError):
            await registry.get(f"missing-{index}")
    assert registry._id_locks == {}
    assert registry._slots == {}
    assert list(tmp_path.iterdir()) == []


async def test_lifecycle_locks_are_reclaimed_without_discarding_tombstones() -> None:
    from azure.ai.agentserver.core.streaming._registry import _TOMBSTONE

    registry = _StreamsRegistry()
    registry.use_in_memory_replay()
    for index in range(100):
        identifier = f"lifecycle-{index}"
        original = await registry.get_or_create(identifier)
        assert registry._id_locks == {}
        assert await registry.get(identifier) is original
        assert registry._id_locks == {}
        await registry.delete(identifier)
        assert registry._id_locks == {}
        with pytest.raises(EventStreamNotFoundError):
            await registry.get(identifier)
        assert registry._slots[identifier] is _TOMBSTONE
        assert registry._id_locks == {}
        fresh = await registry.get_or_create(identifier)
        assert fresh is not original
        await registry.delete(identifier)


async def test_cancelled_delete_reclaims_its_lock_without_installing_a_tombstone(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry = _StreamsRegistry()
    registry.use_in_memory_replay()
    original = await registry.get_or_create("shared")
    entered = asyncio.Event()
    release = asyncio.Event()
    on_delete = original._on_delete

    async def interrupted_delete() -> None:
        entered.set()
        await release.wait()
        await on_delete()

    monkeypatch.setattr(original, "_on_delete", interrupted_delete)
    deleting = asyncio.create_task(registry.delete("shared"))
    await asyncio.wait_for(entered.wait(), 2)
    deleting.cancel()
    with pytest.raises(asyncio.CancelledError):
        await deleting
    assert registry._id_locks == {}
    assert registry._slots["shared"] is original
    monkeypatch.setattr(original, "_on_delete", on_delete)
    await registry.delete("shared")
    assert registry._id_locks == {}
    fresh = await registry.get_or_create("shared")
    assert fresh is not original
    assert registry._id_locks == {}


@pytest.mark.parametrize("cancellation", ["task", "scope"])
async def test_cancelled_waiter_never_splits_interleaved_create_get_delete_lock(
    monkeypatch: pytest.MonkeyPatch, cancellation: str
) -> None:
    registry = _StreamsRegistry()
    registry.use_in_memory_replay()
    original = await registry.get_or_create("shared")
    entered = asyncio.Event()
    release = asyncio.Event()
    scope = CancelScope()
    on_delete = original._on_delete

    async def paused_delete() -> None:
        entered.set()
        await release.wait()
        await on_delete()

    monkeypatch.setattr(original, "_on_delete", paused_delete)
    holder = asyncio.create_task(registry.delete("shared"))
    await asyncio.wait_for(entered.wait(), 2)
    entry = registry._id_locks["shared"]
    factory = registry._factory
    lookup = registry._load_existing
    created = []

    def create(identifier: str) -> EventStream:
        assert registry._id_locks[identifier] is entry
        stream = factory(identifier)
        created.append(stream)
        return stream

    def load(identifier: str, *, for_deletion: bool = False):
        assert registry._id_locks[identifier] is entry
        return lookup(identifier, for_deletion=for_deletion)

    monkeypatch.setattr(registry, "_factory", create)
    monkeypatch.setattr(registry, "_load_existing", load)

    async def start(operation, *, cancelled: bool = False) -> asyncio.Task:
        starting = asyncio.Event()

        async def run():
            if cancelled and cancellation == "scope":
                with scope:
                    starting.set()
                    return await operation("shared")
                return None
            starting.set()
            return await operation("shared")

        task = asyncio.create_task(run())
        await starting.wait()
        return task

    pending = []
    try:
        cancelled = await start(registry.get, cancelled=True)
        pending.append(cancelled)
        creating = await start(registry.get_or_create)
        pending.append(creating)
        getting = await start(registry.get)
        pending.append(getting)
        deleting = await start(registry.delete)
        pending.append(deleting)
        assert entry.users == 5
        if cancellation == "scope":
            scope.cancel()
            await asyncio.wait_for(cancelled, 2)
            assert scope.cancelled_caught
        else:
            cancelled.cancel()
            with pytest.raises(asyncio.CancelledError):
                await cancelled
        assert registry._id_locks["shared"] is entry
        assert entry.users == 4
        release.set()
        await asyncio.wait_for(holder, 2)
        instance = await asyncio.wait_for(creating, 2)
        assert await asyncio.wait_for(getting, 2) is instance
        await asyncio.wait_for(deleting, 2)
        assert created == [instance]
        assert registry._id_locks == {}
    finally:
        release.set()
        for task in pending:
            if not task.done():
                task.cancel()
        await asyncio.gather(holder, *pending, return_exceptions=True)


@pytest.mark.parametrize("cancellation", ["task", "scope"])
async def test_cancelled_holder_keeps_waiters_on_the_exact_lock_until_last_release(
    monkeypatch: pytest.MonkeyPatch, cancellation: str
) -> None:
    registry = _StreamsRegistry()
    registry.use_in_memory_replay()
    original = await registry.get_or_create("shared")
    first_entered = asyncio.Event()
    second_entered = asyncio.Event()
    first_release = asyncio.Event()
    second_release = asyncio.Event()
    scope = CancelScope()
    active = 0
    calls = 0

    async def inspect_stream(identifier: str, slot: EventStream) -> bool:
        nonlocal active, calls
        active += 1
        calls += 1
        assert active == 1
        try:
            if calls == 1:
                first_entered.set()
                await first_release.wait()
            elif calls == 2:
                second_entered.set()
                await second_release.wait()
            return False
        finally:
            active -= 1

    monkeypatch.setattr(registry, "_tombstone_if_close_clock_elapsed", inspect_stream)

    async def first():
        if cancellation == "scope":
            with scope:
                return await registry.get("shared")
            return None
        return await registry.get("shared")

    holder = asyncio.create_task(first())
    await asyncio.wait_for(first_entered.wait(), 2)
    entry = registry._id_locks["shared"]
    starting = asyncio.Event()

    async def next_get():
        starting.set()
        return await registry.get("shared")

    waiter = asyncio.create_task(next_get())
    await starting.wait()
    assert entry.users == 2
    tasks = [holder, waiter]
    try:
        if cancellation == "scope":
            scope.cancel()
            await asyncio.wait_for(holder, 2)
            assert scope.cancelled_caught
        else:
            holder.cancel()
            with pytest.raises(asyncio.CancelledError):
                await holder
        await asyncio.wait_for(second_entered.wait(), 2)
        assert registry._id_locks["shared"] is entry
        assert entry.users == 1
        starting.clear()
        last = asyncio.create_task(next_get())
        tasks.append(last)
        await starting.wait()
        assert registry._id_locks["shared"] is entry
        assert entry.users == 2
        second_release.set()
        assert await waiter is original
        assert await last is original
        assert registry._id_locks == {}
        assert active == 0
    finally:
        first_release.set()
        second_release.set()
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


# ----------------------------------------------------------------
# Per-test fixture — snapshot + restore registry private state
# (streaming.md §7.6 — no public reset()).
# ----------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_registry():
    """Snapshot/restore registry private state for test isolation."""
    saved_slots = dict(streams._slots)  # type: ignore[attr-defined]
    saved_locks = dict(streams._id_locks)  # type: ignore[attr-defined]
    saved_factory = streams._factory  # type: ignore[attr-defined]
    saved_restore = streams._restore
    streams._slots.clear()  # type: ignore[attr-defined]
    streams._id_locks.clear()  # type: ignore[attr-defined]
    streams.use_in_memory_live()  # default backing
    yield
    streams._slots.clear()  # type: ignore[attr-defined]
    streams._slots.update(saved_slots)  # type: ignore[attr-defined]
    streams._id_locks.clear()  # type: ignore[attr-defined]
    streams._id_locks.update(saved_locks)  # type: ignore[attr-defined]
    streams._factory = saved_factory  # type: ignore[attr-defined]
    streams._restore = saved_restore


# ----------------------------------------------------------------
#  — 6 methods
# ----------------------------------------------------------------


class TestRegistrySurface:
    def test_three_async_lifecycle_methods(self) -> None:
        for name in ("get", "get_or_create", "delete"):
            method = getattr(streams, name)
            assert inspect.iscoroutinefunction(method), f"streams.{name} MUST be async per "

    def test_three_sync_configurators(self) -> None:
        for name in (
            "use_in_memory_live",
            "use_in_memory_replay",
            "use_file_backed_replay",
        ):
            method = getattr(streams, name)
            assert not inspect.iscoroutinefunction(method)


# ----------------------------------------------------------------
#  — default backing on module import
# ----------------------------------------------------------------


class TestDefaultBacking:
    async def test_default_is_in_memory_live(self) -> None:
        """— module-import default is use_in_memory_live.
        Verify by constructing a stream and inspecting its (SDK-private)
        concrete type."""
        # Don't override default in this test (fixture sets it)
        s = await streams.get_or_create("default-test")
        # Concrete type SHOULD be BroadcastEventStream
        assert isinstance(s, BroadcastEventStream), f"default backing MUST be BroadcastEventStream; " f"got {type(s)}"


# ----------------------------------------------------------------
#  — delete idempotency (rule 35)
# ----------------------------------------------------------------


class TestDeleteIdempotency:
    async def test_delete_unknown_id_is_noop(self) -> None:
        """Rule 35 — delete(unknown) is a no-op, not NotFoundError."""
        # Must not raise
        await streams.delete("never-registered-xyz")

    async def test_delete_already_tombstoned_is_noop(self) -> None:
        """Rule 35 — delete on tombstoned id is a no-op."""
        await streams.get_or_create("tomb-test")
        await streams.delete("tomb-test")
        # Tombstoned — delete again
        await streams.delete("tomb-test")  # must not raise


# ----------------------------------------------------------------
#  — every bundled impl has _on_delete
# ----------------------------------------------------------------


class TestOnDeleteHookPresent:
    @pytest.mark.parametrize(
        "cls",
        [BroadcastEventStream, ReplayEventStream, FileBackedReplayEventStream],
    )
    def test_concrete_impls_expose_on_delete(self, cls) -> None:
        """/ rule 33 — every bundled impl exposes
        ``async def _on_delete(self)`` private hook."""
        method = getattr(cls, "_on_delete", None)
        assert method is not None, f"{cls.__name__} MUST expose private _on_delete per "
        assert inspect.iscoroutinefunction(method), f"{cls.__name__}._on_delete MUST be async"


# ----------------------------------------------------------------
#  — mid-flight configurator switch (rule 37)
# ----------------------------------------------------------------


class TestMidFlightConfigSwitch:
    async def test_existing_instances_retain_type(self) -> None:
        """Rule 37 — switching configurator only affects future
        get_or_create calls; existing instances retain their type."""
        streams.use_in_memory_replay(cursor_fn=lambda e: e["n"])
        s1 = await streams.get_or_create("mid-flight-1")
        assert isinstance(s1, ReplayEventStream)
        # Switch backing
        streams.use_in_memory_live()
        # Same id returns same instance (Replay)
        s1_again = await streams.get_or_create("mid-flight-1")
        assert s1_again is s1, "same id MUST return same instance"
        # New id returns new type
        s2 = await streams.get_or_create("mid-flight-2")
        assert isinstance(s2, BroadcastEventStream), f"new id after switch MUST use new backing; got {type(s2)}"


# ----------------------------------------------------------------
# Acceptance scenarios (spec Subscriber #1-5)
# ----------------------------------------------------------------


class TestFileBackedReplayDefaults:
    """Spec 037 #6 — ``use_file_backed_replay`` has ergonomic defaults: no args
    required; storage under ``resolve_state_subdir("streams")``, 10-minute TTL,
    JSON serialization. The common case collapses to supplying ``cursor_fn``.
    """

    async def test_no_args_builds_working_file_backed_factory(self, monkeypatch, tmp_path: Path) -> None:
        from azure.ai.agentserver.core import _config as _cfg

        # Redirect the state root so the default lands in a temp dir.
        monkeypatch.setenv("AGENTSERVER_STATE_ROOT", str(tmp_path))
        streams.use_file_backed_replay()
        s = await streams.get_or_create("defaults-1")
        assert isinstance(s, FileBackedReplayEventStream)
        await s.emit({"n": 1})
        # Default storage dir is <state-root>/streams; default JSON round-trips.
        expected = _cfg.resolve_state_subdir("streams") / "defaults-1.jsonl"
        assert expected.exists()
        await streams.delete("defaults-1")

    async def test_default_ttl_is_ten_minutes(self, monkeypatch, tmp_path: Path) -> None:
        monkeypatch.setenv("AGENTSERVER_STATE_ROOT", str(tmp_path))
        streams.use_file_backed_replay()
        s = await streams.get_or_create("defaults-ttl")
        assert s._ttl_seconds == 600.0
        await streams.delete("defaults-ttl")

    async def test_explicit_args_override_defaults(self, tmp_path: Path) -> None:
        streams.use_file_backed_replay(storage_dir=tmp_path, ttl_seconds=42.0)
        s = await streams.get_or_create("defaults-override")
        assert s._ttl_seconds == 42.0
        assert (tmp_path / "defaults-override.jsonl").exists()
        await streams.delete("defaults-override")


class TestSubscriberAcceptanceScenarios:
    async def test_use_in_memory_replay_then_get_or_create(self) -> None:
        """Subscriber #1 — use_in_memory_replay configures Replay impl."""
        streams.use_in_memory_replay(cursor_fn=lambda e: e["n"], ttl_seconds=600)
        s = await streams.get_or_create("us5-1")
        assert isinstance(s, ReplayEventStream)

    async def test_use_file_backed_replay_then_get_or_create_idempotent(self, tmp_path: Path) -> None:
        """Subscriber #2 — file-backed configurator + idempotent get_or_create."""
        streams.use_file_backed_replay(
            storage_dir=tmp_path,
            cursor_fn=lambda e: e["n"],
            ttl_seconds=600,
        )
        s1 = await streams.get_or_create("resp-abc")
        s2 = await streams.get_or_create("resp-abc")
        assert s1 is s2, "get_or_create MUST be idempotent per "
        assert (tmp_path / "resp-abc.jsonl").exists()

    async def test_delete_then_get_raises_gone_not_notfound(self) -> None:
        """Subscriber #3 — after delete(id), get(id) raises Gone (not NotFound).
        This is the load-bearing tombstone-retention invariant (rule 36a)."""
        s = await streams.get_or_create("us5-3")
        await streams.delete("us5-3")
        with pytest.raises(EventStreamNotFoundError):
            await streams.get("us5-3")

    async def test_auto_evicted_id_raises_gone_not_notfound(self) -> None:
        """Subscriber #4 — auto-evicted (CLOSED + all expired + had emits)
        stream's id raises Gone, not NotFound."""
        streams.use_in_memory_replay(cursor_fn=lambda e: e["n"], ttl_seconds=0.1)
        s = await streams.get_or_create("us5-4")
        await s.emit({"n": 1})
        await s.close()
        await asyncio.sleep(0.2)  # event 1 expires
        # First subscribe attempt fires CLOSED→GONE auto-transition
        with pytest.raises(EventStreamNotFoundError):
            s.subscribe()
        # Now registry knows it's GONE — but tombstone wasn't installed
        # by auto-transition (instance is GONE but slot still references
        # the GONE instance). Verify the registry behavior.
        with pytest.raises(EventStreamNotFoundError):
            stream = await streams.get("us5-4")
            # If get returns the GONE instance, any operation on it raises:
            await stream.emit({"n": 2})

    async def test_get_unregistered_id_raises_notfound(self) -> None:
        """Subscriber #5 — get(unregistered) raises NotFound."""
        with pytest.raises(EventStreamNotFoundError):
            await streams.get("never-registered")


# ----------------------------------------------------------------
# Rule 36a — tombstone retention
# ----------------------------------------------------------------


class TestTombstoneRetention:
    async def test_delete_installs_tombstone(self) -> None:
        """Rule 36a — delete installs tombstone; get raises Gone."""
        await streams.get_or_create("tr-1")
        await streams.delete("tr-1")
        with pytest.raises(EventStreamNotFoundError):
            await streams.get("tr-1")

    async def test_re_creation_clears_tombstone(self) -> None:
        """Rule 36a — get_or_create on tombstoned id creates fresh
        stream + clears tombstone."""
        await streams.get_or_create("tr-2")
        await streams.delete("tr-2")
        # Re-create
        s2 = await streams.get_or_create("tr-2")
        # Tombstone cleared — get returns it
        s2_via_get = await streams.get("tr-2")
        assert s2 is s2_via_get


# ----------------------------------------------------------------
# Rule 34 — get_or_create atomicity under concurrency
# ----------------------------------------------------------------


class TestGetOrCreateAtomicity:
    async def test_10_concurrent_get_or_create_returns_same_instance(
        self,
    ) -> None:
        """Rule 34 — concurrent callers with same id all receive the
        SAME instance (no split-brain construction)."""
        results = await asyncio.gather(*[streams.get_or_create("atomicity-test") for _ in range(10)])
        first = results[0]
        for r in results[1:]:
            assert r is first, "concurrent get_or_create MUST be atomic"


class TestPersistedLookup:
    @pytest.mark.parametrize(
        "invalid_record",
        [b"not json\n", b"\xff\n", b'{"payload": {"n": 2}}\n'],
        ids=["malformed-json", "invalid-encoding", "missing-time"],
    )
    async def test_cold_delete_removes_corrupt_log_and_allows_recreation(
        self, tmp_path: Path, invalid_record: bytes
    ) -> None:
        from azure.ai.agentserver.core.streaming._registry import _TOMBSTONE

        original_registry = _StreamsRegistry()
        original_registry.use_file_backed_replay(storage_dir=tmp_path)
        original = await original_registry.get_or_create("corrupt")
        await original.emit({"n": 1})
        await original.emit({"n": 3})
        await original.close()
        original._cleanup_locks()
        path = tmp_path / "corrupt.jsonl"
        records = path.read_bytes().splitlines(keepends=True)
        path.write_bytes(records[0] + invalid_record + b"".join(records[1:]))

        restarted = _StreamsRegistry()
        restarted.use_file_backed_replay(storage_dir=tmp_path)
        with pytest.raises(RuntimeError, match="malformed|missing 'emit_time'"):
            await restarted.get("corrupt")
        assert restarted._slots == {}
        assert restarted._id_locks == {}
        await restarted.delete("corrupt")
        assert list(tmp_path.iterdir()) == []
        assert restarted._slots["corrupt"] is _TOMBSTONE
        assert restarted._id_locks == {}
        with pytest.raises(EventStreamNotFoundError):
            await restarted.get("corrupt")
        fresh = await restarted.get_or_create("corrupt")
        await fresh.emit({"n": 4}, close=True)
        assert [event async for event in fresh.subscribe()] == [{"n": 4}]
        await restarted.delete("corrupt")

    async def test_valid_cold_delete_never_rehydrates_or_calls_payload_callbacks(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        registry = _StreamsRegistry()
        registry.use_file_backed_replay(storage_dir=tmp_path)
        original = await registry.get_or_create("valid")
        await original.emit({"n": 1}, close=True)
        original._cleanup_locks()

        def forbidden(*args, **kwargs):
            raise AssertionError("cold deletion must not read replay events")

        restarted = _StreamsRegistry()
        restarted.use_file_backed_replay(
            storage_dir=tmp_path,
            cursor_fn=forbidden,
            serializer=forbidden,
            deserializer=forbidden,
        )
        monkeypatch.setattr(FileBackedReplayEventStream, "_rehydrate", forbidden)
        await restarted.delete("valid")
        assert list(tmp_path.iterdir()) == []
        assert restarted._id_locks == {}

    @pytest.mark.parametrize("windows", [False, True])
    async def test_cold_delete_lock_contention_preserves_log_and_allows_retry(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, windows: bool
    ) -> None:
        from azure.ai.agentserver.core.streaming import _concrete

        if windows:
            monkeypatch.setattr(_concrete, "fcntl", None)
        writer = _StreamsRegistry()
        writer.use_file_backed_replay(storage_dir=tmp_path)
        original = await writer.get_or_create("locked")
        await original.emit({"n": 1})
        path = tmp_path / "locked.jsonl"
        expected = path.read_bytes()
        restarted = _StreamsRegistry()
        restarted.use_file_backed_replay(storage_dir=tmp_path)
        try:
            for _ in range(2):
                with pytest.raises(RuntimeError, match="another process holds"):
                    await restarted.delete("locked")
                assert path.read_bytes() == expected
                assert restarted._slots == {}
                assert restarted._id_locks == {}
        finally:
            original._cleanup_locks()
        await restarted.delete("locked")
        assert list(tmp_path.iterdir()) == []
        assert restarted._id_locks == {}

    @pytest.mark.parametrize("artifact", ["log", "lock", "descriptor"])
    async def test_corrupt_cold_delete_cleanup_failure_keeps_exact_owner_for_retry(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, artifact: str
    ) -> None:
        from azure.ai.agentserver.core.streaming import _concrete
        from azure.ai.agentserver.core.streaming._registry import _TOMBSTONE

        monkeypatch.setattr(_concrete, "fcntl", None)
        path = tmp_path / "retry.jsonl"
        path.write_bytes(b'{"emit_time": 1, "payload": 1}\nnot json\n')
        lock_path = path.with_suffix(".jsonl.lock")
        denied_path = path if artifact == "log" else lock_path
        unlink = Path.unlink

        def denied(candidate: Path, *args, **kwargs):
            if candidate == denied_path:
                raise PermissionError("artifact removal denied")
            return unlink(candidate, *args, **kwargs)

        def denied_close(descriptor: int):
            raise PermissionError("artifact removal denied")

        restarted = _StreamsRegistry()
        restarted.use_file_backed_replay(storage_dir=tmp_path)
        with monkeypatch.context() as patch:
            patch.setattr(Path, "unlink", denied)
            if artifact == "descriptor":
                patch.setattr(_concrete.os, "close", denied_close)
            with pytest.raises(PermissionError, match="artifact removal denied"):
                await restarted.delete("retry")
            owner = restarted._slots["retry"]
            descriptor = owner._lock_fd
            assert owner is not _TOMBSTONE
            for _ in range(2):
                with pytest.raises(PermissionError, match="artifact removal denied"):
                    await restarted.delete("retry")
                assert restarted._slots["retry"] is owner
                assert restarted._id_locks == {}
                assert path.exists()
                assert lock_path.exists() is (artifact != "log")
                assert owner._file.closed
                assert owner._lock_fd == descriptor
                assert (owner._lock_fd is not None) is (artifact == "descriptor")
            assert await restarted.get_or_create("retry") is owner
            with pytest.raises(EventStreamNotFoundError):
                await owner.emit({"n": 2})

        await restarted.delete("retry")
        assert list(tmp_path.iterdir()) == []
        assert restarted._slots["retry"] is _TOMBSTONE
        assert restarted._id_locks == {}
        fresh = await restarted.get_or_create("retry")
        await fresh.emit({"n": 2}, close=True)
        assert [event async for event in fresh.subscribe()] == [{"n": 2}]
        await restarted.delete("retry")

    @pytest.mark.parametrize("windows", [False, True])
    @pytest.mark.parametrize("failure", [PermissionError, FileNotFoundError])
    @pytest.mark.parametrize("operation", ["get", "delete", "get_or_create"])
    async def test_cold_access_lock_acquisition_errors_propagate_and_close_handle(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, windows: bool, failure, operation: str
    ) -> None:
        from azure.ai.agentserver.core.streaming import _concrete

        path = tmp_path / "restricted.jsonl"
        expected = b"not json\n"
        path.write_bytes(expected)
        registry = _StreamsRegistry()
        registry.use_file_backed_replay(storage_dir=tmp_path)
        opened = []
        open_file = open

        def tracked_open(*args, **kwargs):
            handle = open_file(*args, **kwargs)
            opened.append(handle)
            return handle

        def denied(*args, **kwargs):
            raise failure("lock acquisition denied")

        with monkeypatch.context() as patch:
            patch.setattr(_concrete, "open", tracked_open, raising=False)
            if windows:
                patch.setattr(_concrete, "fcntl", None)
                patch.setattr(_concrete.os, "open", denied)
            else:
                patch.setattr(_concrete, "fcntl", SimpleNamespace(LOCK_EX=1, LOCK_NB=2, flock=denied))
            with pytest.raises(failure, match="lock acquisition denied"):
                await getattr(registry, operation)("restricted")
            assert len(opened) == 1
            assert opened[0].closed
            assert registry._slots == {}
            assert registry._id_locks == {}
            assert path.read_bytes() == expected
            assert sorted(tmp_path.iterdir()) == [path]

        await registry.delete("restricted")
        assert list(tmp_path.iterdir()) == []

    async def test_cold_lookup_file_disappearing_before_open_does_not_create_or_retain_a_log(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from azure.ai.agentserver.core.streaming import _concrete

        registry = _StreamsRegistry()
        registry.use_file_backed_replay(storage_dir=tmp_path)
        original = await registry.get_or_create("disappearing")
        await original.emit({"n": 1}, close=True)
        original._cleanup_locks()
        path = tmp_path / "disappearing.jsonl"
        restarted = _StreamsRegistry()
        restarted.use_file_backed_replay(storage_dir=tmp_path)
        open_file = open
        modes = []

        def remove_before_open(candidate, mode):
            assert candidate == path
            assert candidate.stat().st_size > 0
            candidate.unlink()
            modes.append(mode)
            return open_file(candidate, mode)

        with monkeypatch.context() as patch:
            patch.setattr(_concrete, "open", remove_before_open, raising=False)
            with pytest.raises(EventStreamNotFoundError):
                await restarted.get("disappearing")
            assert modes == ["r+b"]
            assert restarted._slots == {}
            assert restarted._id_locks == {}
            assert list(tmp_path.iterdir()) == []
        with pytest.raises(EventStreamNotFoundError):
            await restarted.get("disappearing")
        assert restarted._slots == {}
        assert restarted._id_locks == {}
        fresh = await restarted.get_or_create("disappearing")
        assert path.exists()
        await fresh.emit({"n": 2}, close=True)
        assert [event async for event in fresh.subscribe()] == [{"n": 2}]
        await restarted.delete("disappearing")

    @pytest.mark.parametrize("operation", ["get", "get_or_create"])
    @pytest.mark.parametrize("custom_payload", [False, True])
    async def test_cold_lookup_and_creation_preserve_recovery_and_append_semantics(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, operation: str, custom_payload: bool
    ) -> None:
        from azure.ai.agentserver.core.streaming import _concrete

        def serialize(payload):
            return json.dumps({"value": payload}).encode("utf-8")

        def deserialize(payload):
            return json.loads(payload)["value"]

        configuration = {
            "storage_dir": tmp_path,
            "cursor_fn": lambda event: event["n"],
            "serializer": serialize if custom_payload else None,
            "deserializer": deserialize if custom_payload else None,
        }
        registry = _StreamsRegistry()
        registry.use_file_backed_replay(**configuration)
        original = await registry.get_or_create("retained")
        await original.emit({"n": 1})
        original._cleanup_locks()
        restarted = _StreamsRegistry()
        restarted.use_file_backed_replay(**configuration)
        open_file = open
        modes = []

        def track_open(candidate, mode):
            modes.append(mode)
            return open_file(candidate, mode)

        with monkeypatch.context() as patch:
            patch.setattr(_concrete, "open", track_open, raising=False)
            restored = await getattr(restarted, operation)("retained")
        assert modes == (["r+b"] if operation == "get" else ["a+b"])
        assert await restored.last_cursor() == 1
        await restored.emit({"n": 2}, close=True)
        assert [event async for event in restored.subscribe()] == [{"n": 1}, {"n": 2}]
        restored._cleanup_locks()
        final_registry = _StreamsRegistry()
        final_registry.use_file_backed_replay(**configuration)
        final = await final_registry.get("retained")
        assert await final.last_cursor() == 2
        assert [event async for event in final.subscribe()] == [{"n": 1}, {"n": 2}]
        await final_registry.delete("retained")
        assert list(tmp_path.iterdir()) == []

    async def test_cold_delete_file_disappearing_before_open_never_creates_a_log(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from azure.ai.agentserver.core.streaming import _concrete
        from azure.ai.agentserver.core.streaming._registry import _TOMBSTONE

        path = tmp_path / "disappearing.jsonl"
        path.write_bytes(b"not json\n")
        registry = _StreamsRegistry()
        registry.use_file_backed_replay(storage_dir=tmp_path)
        open_file = open
        modes = []

        def remove_before_open(candidate, mode):
            assert candidate == path
            modes.append(mode)
            candidate.unlink()
            return open_file(candidate, mode)

        monkeypatch.setattr(_concrete, "open", remove_before_open, raising=False)
        await registry.delete("disappearing")
        assert modes == ["r+b"]
        assert list(tmp_path.iterdir()) == []
        assert registry._slots["disappearing"] is _TOMBSTONE
        assert registry._id_locks == {}

    @pytest.mark.parametrize("cancellation", ["task", "scope"])
    async def test_cancelled_cold_delete_retains_cleanup_owner_until_retry(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, cancellation: str
    ) -> None:
        from azure.ai.agentserver.core.streaming import _concrete
        from azure.ai.agentserver.core.streaming._registry import _TOMBSTONE

        monkeypatch.setattr(_concrete, "fcntl", None)
        path = tmp_path / "cancelled.jsonl"
        path.write_bytes(b"not json\n")
        registry = _StreamsRegistry()
        registry.use_file_backed_replay(storage_dir=tmp_path)
        entered = asyncio.Event()
        release = asyncio.Event()
        scope = CancelScope()
        owners = []

        async def paused_delete(owner):
            owners.append(owner)
            entered.set()
            await release.wait()

        async def delete():
            if cancellation == "scope":
                with scope:
                    await registry.delete("cancelled")
            else:
                await registry.delete("cancelled")

        with monkeypatch.context() as patch:
            patch.setattr(FileBackedReplayEventStream, "_on_delete", paused_delete)
            deleting = asyncio.create_task(delete())
            try:
                await asyncio.wait_for(entered.wait(), 2)
                owner = owners[0]
                assert registry._slots["cancelled"] is owner
                assert registry._id_locks["cancelled"].users == 1
                if cancellation == "scope":
                    scope.cancel()
                    await asyncio.wait_for(deleting, 2)
                    assert scope.cancelled_caught
                else:
                    deleting.cancel()
                    with pytest.raises(asyncio.CancelledError):
                        await deleting
                assert registry._slots["cancelled"] is owner
                assert registry._slots["cancelled"] is not _TOMBSTONE
                assert not owner._file.closed
                assert owner._lock_fd is not None
                assert path.exists()
                assert registry._id_locks == {}
            finally:
                if not deleting.done():
                    deleting.cancel()
                    await asyncio.gather(deleting, return_exceptions=True)
                release.set()

        await registry.delete("cancelled")
        assert list(tmp_path.iterdir()) == []
        assert registry._slots["cancelled"] is _TOMBSTONE
        assert registry._id_locks == {}
        fresh = await registry.get_or_create("cancelled")
        await fresh.emit({"n": 1}, close=True)
        assert [event async for event in fresh.subscribe()] == [{"n": 1}]
        await registry.delete("cancelled")

    async def test_windows_lock_file_removal_failure_is_retryable(self, tmp_path: Path, monkeypatch):
        from azure.ai.agentserver.core.streaming import _concrete
        from azure.ai.agentserver.core.streaming._registry import _TOMBSTONE

        monkeypatch.setattr(_concrete, "fcntl", None)
        streams.use_file_backed_replay(storage_dir=tmp_path)
        original = await streams.get_or_create("windows-retry")
        await original.emit({"n": 1})
        await original.close()
        lock_path = tmp_path / "windows-retry.jsonl.lock"
        unlink = Path.unlink

        def denied(path, *args, **kwargs):
            if path == lock_path:
                raise PermissionError("lock removal denied")
            return unlink(path, *args, **kwargs)

        with monkeypatch.context() as patch:
            patch.setattr(Path, "unlink", denied)
            for _ in range(2):
                with pytest.raises(PermissionError, match="lock removal denied"):
                    await streams.delete("windows-retry")
                assert streams._slots["windows-retry"] is not _TOMBSTONE
                assert original._lock_fd is None
                assert lock_path.exists()
                assert (tmp_path / "windows-retry.jsonl").exists()

        await streams.delete("windows-retry")
        assert list(tmp_path.iterdir()) == []
        fresh = await streams.get_or_create("windows-retry")
        await fresh.emit({"n": 2})
        await fresh.close()
        assert [event async for event in fresh.subscribe()] == [{"n": 2}]
        await streams.delete("windows-retry")

    @pytest.mark.parametrize("expired", [False, True])
    async def test_unlink_failure_preserves_slot_until_cleanup_retry(self, tmp_path: Path, monkeypatch, expired):
        from azure.ai.agentserver.core.streaming import _concrete
        from azure.ai.agentserver.core.streaming._registry import _StreamsRegistry, _TOMBSTONE

        monkeypatch.setattr(_concrete.time, "time", lambda: 1000.0)
        streams.use_file_backed_replay(storage_dir=tmp_path, ttl_seconds=60)
        original = await streams.get_or_create("retry-delete")
        await original.emit({"n": 1})
        await original.close()
        original._cleanup_locks()
        streams._slots.clear()
        if expired:
            monkeypatch.setattr(_concrete.time, "time", lambda: 1061.0)

        unlink = Path.unlink
        log_path = tmp_path / "retry-delete.jsonl"

        def denied(path, *args, **kwargs):
            if path == log_path:
                raise PermissionError("replay removal denied")
            return unlink(path, *args, **kwargs)

        with monkeypatch.context() as patch:
            patch.setattr(Path, "unlink", denied)
            with pytest.raises(PermissionError, match="replay removal denied"):
                if expired:
                    await streams.get("retry-delete")
                else:
                    await streams.delete("retry-delete")
            assert log_path.exists()
            assert streams._slots["retry-delete"] is not _TOMBSTONE
            existing = await streams.get_or_create("retry-delete")
            with pytest.raises(EventStreamNotFoundError):
                await existing.emit({"n": 2})
            with pytest.raises(PermissionError, match="replay removal denied"):
                await streams.get("retry-delete")

        await streams.delete("retry-delete")
        assert not log_path.exists()
        restarted = _StreamsRegistry()
        restarted.use_file_backed_replay(storage_dir=tmp_path)
        with pytest.raises(EventStreamNotFoundError):
            await restarted.get("retry-delete")
        fresh = await streams.get_or_create("retry-delete")
        await fresh.emit({"n": 2})
        await fresh.close()
        assert [event async for event in fresh.subscribe()] == [{"n": 2}]
        await streams.delete("retry-delete")

    async def test_missing_lookup_and_delete_do_not_create_files(self, tmp_path: Path) -> None:
        streams.use_file_backed_replay(storage_dir=tmp_path)
        with pytest.raises(EventStreamNotFoundError):
            await streams.get("missing")
        await streams.delete("missing")
        assert list(tmp_path.iterdir()) == []

    async def test_concurrent_lookup_restores_one_instance(self, tmp_path: Path) -> None:
        streams.use_file_backed_replay(storage_dir=tmp_path, cursor_fn=lambda event: event["n"])
        original = await streams.get_or_create("retained")
        await original.emit({"n": 1})
        await original.close()
        original._cleanup_locks()
        streams._slots.clear()

        restored = await asyncio.gather(
            *(streams.get("retained") for _ in range(10)),
            streams.get_or_create("retained"),
        )
        assert all(stream is restored[0] for stream in restored)
        assert [event async for event in restored[0].subscribe()] == [{"n": 1}]
        await streams.delete("retained")

    async def test_cold_delete_removes_persisted_log(self, tmp_path: Path) -> None:
        streams.use_file_backed_replay(storage_dir=tmp_path)
        original = await streams.get_or_create("retained")
        await original.emit({"n": 1})
        await original.close()
        original._cleanup_locks()
        streams._slots.clear()

        await streams.delete("retained")
        assert list(tmp_path.iterdir()) == []
        with pytest.raises(EventStreamNotFoundError):
            await streams.get("retained")

    async def test_expired_cold_lookup_cleans_up_and_allows_fresh_creation(self, tmp_path: Path, monkeypatch) -> None:
        from azure.ai.agentserver.core.streaming import _concrete

        monkeypatch.setattr(_concrete.time, "time", lambda: 1000.0)
        streams.use_file_backed_replay(storage_dir=tmp_path, ttl_seconds=60)
        original = await streams.get_or_create("expired")
        await original.emit({"n": 1})
        await original.close()
        original._cleanup_locks()
        streams._slots.clear()
        monkeypatch.setattr(_concrete.time, "time", lambda: 1061.0)

        with pytest.raises(EventStreamNotFoundError):
            await streams.get("expired")
        assert list(tmp_path.iterdir()) == []
        fresh = await streams.get_or_create("expired")
        assert fresh is not original
        await fresh.emit({"n": 2})
        await fresh.close()
        assert [event async for event in fresh.subscribe()] == [{"n": 2}]
        await streams.delete("expired")

    async def test_locked_persisted_log_is_not_reported_missing(self, tmp_path: Path) -> None:
        from azure.ai.agentserver.core.streaming._registry import _StreamsRegistry

        streams.use_file_backed_replay(storage_dir=tmp_path)
        original = await streams.get_or_create("locked")
        await original.emit({"n": 1})
        restarted = _StreamsRegistry()
        restarted.use_file_backed_replay(storage_dir=tmp_path)
        try:
            with pytest.raises(RuntimeError, match="another process holds"):
                await restarted.get("locked")
        finally:
            await streams.delete("locked")

    async def test_lookup_permission_failure_is_not_reported_missing(self, tmp_path: Path, monkeypatch) -> None:
        from azure.ai.agentserver.core.streaming import _concrete

        streams.use_file_backed_replay(storage_dir=tmp_path)

        def denied(path, *args, **kwargs):
            raise PermissionError("replay access denied")

        with monkeypatch.context() as patch:
            patch.setattr(_concrete, "open", denied, raising=False)
            with pytest.raises(PermissionError, match="replay access denied"):
                await streams.get("restricted")
        assert list(tmp_path.iterdir()) == []

    @pytest.mark.parametrize("backing", ["use_in_memory_live", "use_in_memory_replay"])
    async def test_switching_to_memory_disables_disk_lookup(self, tmp_path: Path, backing: str) -> None:
        streams.use_file_backed_replay(storage_dir=tmp_path)
        original = await streams.get_or_create("retained")
        await original.emit({"n": 1})
        await original.close()
        original._cleanup_locks()
        streams._slots.clear()
        getattr(streams, backing)()
        with pytest.raises(EventStreamNotFoundError):
            await streams.get("retained")
        streams.use_file_backed_replay(storage_dir=tmp_path)
        await streams.delete("retained")


# ----------------------------------------------------------------
#  — third-party-impl invariant
# ----------------------------------------------------------------


class TestThirdPartyImplInvariant:
    """— the SDK ``streams`` namespace MUST expose NO public
    method that accepts an arbitrary ``EventStream`` instance for
    registration. Third-party impls live in their own peer registry."""

    def test_no_public_registration_methods(self) -> None:
        """Introspect ``dir(streams)`` — assert no method name matches
        ``register|add|insert|put|set_instance|adopt`` (anything that
        would let a caller plant a third-party impl into the SDK
        registry)."""
        forbidden_pattern = re.compile(
            r"^(register|add|insert|put|set_instance|adopt)",
            re.IGNORECASE,
        )
        for name in dir(streams):
            if name.startswith("_"):
                continue  # private — out of scope
            assert not forbidden_pattern.match(name), (
                f"streams.{name} would let third-party impls bypass the " f"_on_delete cleanup contract per "
            )

    async def test_third_party_impl_cannot_be_planted_via_public_api(
        self,
    ) -> None:
        """Concretely: there is no public API that accepts an arbitrary
        EventStream instance and stores it. The only public path is
        ``use_*`` configurators + ``get_or_create`` (which constructs
        bundled impls only)."""

        class _FakeStream:
            """Third-party EventStream impl (Protocol-compliant)."""

            async def emit(self, payload, *, close=False):
                pass

            async def close(self):
                pass

            def subscribe(self, *, after=None):
                async def _it():
                    if False:
                        yield

                return _it()

            async def last_cursor(self):
                return None

        fake = _FakeStream()
        # Every plausible public path to plant `fake` must fail.
        # We test that no method on streams accepts an instance arg
        # and stores it.
        for method_name in [
            "register",
            "add",
            "insert",
            "put",
            "set_instance",
            "adopt",
            "set_default_factory",
        ]:
            assert not hasattr(streams, method_name), (
                f"streams.{method_name} exists — would let third parties "
                f"plant impls bypassing _on_delete contract per "
            )
