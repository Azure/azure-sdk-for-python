# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Conformance tests for :class:`FileBackedReplayEventStream`.

Asserts  /  /  + rules 26-32 (file-backed
specific). Per ``streaming.md`` Constitution Principle X exit
checklist, crash-recovery tests use real signals via
``_crash_harness`` (not mocked) — but for Phase 1's intra-process
construction-recovery tests (re-instantiating the same path
after process resumes), explicit file-content manipulation in the
TEST is acceptable; the real-signal discipline applies to E2E.
"""

from __future__ import annotations

import asyncio
import json
import multiprocessing
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from azure.ai.agentserver.core.streaming import (
    EventStreamClosedError,
    EventStreamNotFoundError,
)
from azure.ai.agentserver.core.streaming._concrete import (
    FileBackedReplayEventStream,
)


pytestmark = pytest.mark.asyncio(loop_scope="function")


def _delayed_replay_writer(path, connection):
    class DelayedWriter(FileBackedReplayEventStream):
        def _acquire_file_lock(self):
            connection.send("opened")
            connection.recv()
            super()._acquire_file_lock()

    stream = None
    try:
        stream = DelayedWriter(path=Path(path))
        asyncio.run(stream.emit({"n": "waiter"}))
        connection.send("acknowledged")
    except Exception as error:
        connection.send(type(error).__name__)
    finally:
        if stream is not None:
            stream._cleanup_locks()
        connection.close()


# ----------------------------------------------------------------
# Rule 26 — persist-before-fanout
# ----------------------------------------------------------------


class TestPersistBeforeFanout:
    async def test_emit_persists_before_returning(self, tmp_path: Path) -> None:
        """Rule 26 — emit() returns only after payload is
        persisted; subscribers receive payload only after persistence."""
        p = tmp_path / "fb-pbf.jsonl"
        s = FileBackedReplayEventStream(path=p, cursor_fn=lambda e: e["n"], ttl_seconds=600)
        await s.emit({"n": 1, "msg": "first"})
        # File MUST contain the record now
        assert p.exists()
        content = p.read_text()
        assert '"n": 1' in content, f"emit MUST persist before returning; file={content!r}"
        await s._on_delete()


# ----------------------------------------------------------------
# Rule 27 — persistence format
# ----------------------------------------------------------------


class TestPersistenceFormat:
    async def test_record_has_emit_time_and_payload(self, tmp_path: Path) -> None:
        """Rule 27 — each record is one jsonl line with at minimum
        emit_time + payload fields."""
        p = tmp_path / "fb-fmt.jsonl"
        s = FileBackedReplayEventStream(path=p, cursor_fn=lambda e: e["n"])
        await s.emit({"n": 1})
        await s.emit({"n": 2})
        lines = [l for l in p.read_text().splitlines() if l]
        assert len(lines) == 2
        for line in lines:
            record = json.loads(line)
            assert "emit_time" in record, f"record missing emit_time: {record}"
            assert isinstance(record["emit_time"], (int, float))
            assert "payload" in record
        await s._on_delete()

    async def test_terminal_marker_format(self, tmp_path: Path) -> None:
        """Spec 037 #2 — the terminal marker is exactly ``{"__terminal__": true}``
        (no ``emit_time``, no ``payload``), matching C-STR-FBR-5 and the .NET port.
        """
        p = tmp_path / "fb-term.jsonl"
        s = FileBackedReplayEventStream(path=p, cursor_fn=lambda e: e["n"])
        await s.emit({"n": 1})
        await s.close()
        lines = [l for l in p.read_text().splitlines() if l]
        assert len(lines) == 2  # 1 payload + 1 terminal
        terminal = json.loads(lines[-1])
        assert terminal == {"__terminal__": True}
        await s._on_delete()

    async def test_rehydrate_closed_from_terminal_without_emit_time(self, tmp_path: Path) -> None:
        """Spec 037 #2 — a file whose terminal record carries no ``emit_time``
        rehydrates as CLOSED (the terminal record's own timestamp is not
        required; close-time is best-effort from the last real event / now).
        """
        p = tmp_path / "fb-noemit.jsonl"
        with open(p, "w", encoding="utf-8") as f:
            f.write(json.dumps({"emit_time": 100.0, "payload": {"n": 1}}) + "\n")
            f.write(json.dumps({"__terminal__": True}) + "\n")
        s = FileBackedReplayEventStream(path=p, cursor_fn=lambda e: e["n"])
        assert s._state == s._STATE_CLOSED
        await s._on_delete()

    async def test_rehydrate_non_terminal_missing_emit_time_still_raises(self, tmp_path: Path) -> None:
        """Regression guard — a NON-terminal record missing ``emit_time`` is
        still malformed and raises at construction.
        """
        p = tmp_path / "fb-badrec.jsonl"
        with open(p, "w", encoding="utf-8") as f:
            f.write(json.dumps({"payload": {"n": 1}}) + "\n")  # no emit_time
        with pytest.raises(RuntimeError, match="emit_time"):
            FileBackedReplayEventStream(path=p)


class TestSafeStreamFilename:
    """Spec 037 #4 — stream ids are sanitized before use as on-disk filenames so
    an attacker-/user-controlled id cannot escape the storage directory or clobber
    a sibling stream.
    """

    def test_wellformed_id_used_verbatim(self) -> None:
        from azure.ai.agentserver.core.streaming._concrete import _safe_stream_filename

        assert _safe_stream_filename("abc-123.def_ID") == "abc-123.def_ID.jsonl"

    def test_path_traversal_and_bad_chars_are_hash_encoded(self) -> None:
        from azure.ai.agentserver.core.streaming._concrete import _safe_stream_filename

        for bad in ("../evil", "a/b", ".", "..", "x\x00y", "a\\b", "co*star", "with space"):
            name = _safe_stream_filename(bad)
            assert name.startswith("h_") and name.endswith(".jsonl"), f"{bad!r} -> {name!r}"
            # Deterministic + cannot contain a path separator.
            assert "/" not in name and "\\" not in name
            assert _safe_stream_filename(bad) == name  # deterministic

    def test_distinct_ids_dont_collide(self) -> None:
        from azure.ai.agentserver.core.streaming._concrete import _safe_stream_filename

        assert _safe_stream_filename("../a") != _safe_stream_filename("../b")

    def test_verbatim_hash_shaped_id_does_not_alias_hash_namespace(self) -> None:
        """Spec 037 #4 — a well-formed id literally shaped like the reserved
        ``h_<64hex>`` stem must NOT be used verbatim, or it would alias the
        hash-encoding of a different unsafe id. It is itself hashed.
        """
        import hashlib

        from azure.ai.agentserver.core.streaming._concrete import _safe_stream_filename

        unsafe = "../evil"
        collider = "h_" + hashlib.sha256(unsafe.encode("utf-8")).hexdigest()
        # The collider looks well-formed but must be hash-encoded, so it does NOT
        # land on the same file as the unsafe id's hash.
        assert _safe_stream_filename(collider) != _safe_stream_filename(unsafe)


# ----------------------------------------------------------------
# Rule 28 — deterministic recovery
# ----------------------------------------------------------------


class TestDeterministicRecovery:
    async def test_rehydrate_active_stream_from_disk(self, tmp_path: Path) -> None:
        """Rule 28 — new instance constructed on same path rehydrates
        in persisted order, no terminal marker → ACTIVE."""
        p = tmp_path / "fb-rehydrate.jsonl"
        s1 = FileBackedReplayEventStream(path=p, cursor_fn=lambda e: e["n"], ttl_seconds=600)
        await s1.emit({"n": 1, "msg": "before crash"})
        await s1.emit({"n": 2, "msg": "before crash 2"})
        # Simulate crash: don't close, just release locks + drop ref
        s1._cleanup_locks()
        del s1

        # New instance from same path
        s2 = FileBackedReplayEventStream(path=p, cursor_fn=lambda e: e["n"], ttl_seconds=600)
        # Should be ACTIVE (no terminal marker on disk)
        assert s2._state == s2._STATE_ACTIVE
        # Subscribe(after=None) yields the buffered events
        results = []

        async def consume():
            async for ev in s2.subscribe():
                results.append(ev["n"])
                if ev["n"] == 3:
                    break

        task = asyncio.create_task(consume())
        await asyncio.sleep(0.01)
        await s2.emit({"n": 3, "msg": "after recovery"})
        await task
        assert results == [1, 2, 3]
        await s2._on_delete()

    async def test_rehydrate_closed_stream_from_disk(self, tmp_path: Path) -> None:
        """Rule 28 — terminal marker present → rehydrate as CLOSED."""
        p = tmp_path / "fb-rehydrate-closed.jsonl"
        s1 = FileBackedReplayEventStream(path=p, cursor_fn=lambda e: e["n"], ttl_seconds=600)
        await s1.emit({"n": 1})
        await s1.close()
        s1._cleanup_locks()
        del s1

        s2 = FileBackedReplayEventStream(path=p, cursor_fn=lambda e: e["n"], ttl_seconds=600)
        assert s2._state == s2._STATE_CLOSED
        # emit on rehydrated-CLOSED → raises ClosedError
        with pytest.raises(EventStreamClosedError):
            await s2.emit({"n": 2})
        # subscribe yields surviving events then terminates
        results = []
        async for ev in s2.subscribe():
            results.append(ev["n"])
        assert results == [1]
        await s2._on_delete()

    async def test_rehydrate_terminal_plus_all_expired_is_gone(self, tmp_path: Path) -> None:
        """Rule 28 — terminal + no surviving records + ever had records →
        constructor returns GONE-state instance."""
        p = tmp_path / "fb-rehydrate-gone.jsonl"
        # Manually write old file with expired records + terminal
        old_time = 1.0  # ancient
        with open(p, "w") as f:
            f.write(json.dumps({"emit_time": old_time, "payload": {"n": 1}}) + "\n")
            f.write(json.dumps({"emit_time": old_time, "__terminal__": True}) + "\n")
        # Rehydrate with ttl 60s → events expired
        s = FileBackedReplayEventStream(path=p, cursor_fn=lambda e: e["n"], ttl_seconds=60)
        assert s._state == s._STATE_GONE
        with pytest.raises(EventStreamNotFoundError):
            await s.emit({"n": 2})
        await s._on_delete()


# ----------------------------------------------------------------
# Rule 29 — corruption handling
# ----------------------------------------------------------------


class TestCorruptionHandling:
    async def test_trailing_partial_record_silently_discarded(self, tmp_path: Path) -> None:
        """Rule 29 (a) — trailing partial (last line lacks \\n or fails
        to decode and is the LAST line) → silent discard."""
        p = tmp_path / "fb-partial.jsonl"
        with open(p, "wb") as f:
            f.write(json.dumps({"emit_time": 1.0, "payload": {"n": 1}}).encode() + b"\n")
            f.write(b"this-is-a-partial-line-no-newline")  # NO trailing \n
        # Construction must SUCCEED (rule 29a)
        s = FileBackedReplayEventStream(path=p, cursor_fn=lambda e: e["n"], ttl_seconds=600)
        # The 1 good record was rehydrated. Its emit_time is 1.0
        # (Jan 1 1970) so with ttl_seconds=600 it has already been
        # evicted from the live buffer; assert via _highest_cursor
        # (set BEFORE eviction in the rehydration loop) that the
        # one good record was indeed parsed.
        assert s._highest_cursor == 1
        await s._on_delete()

    async def test_mid_file_malformed_raises_at_construction(self, tmp_path: Path) -> None:
        """Rule 29 (b) — mid-file decode failure → RuntimeError at
        construction (NOT EventStreamError — no instance was constructed)."""
        p = tmp_path / "fb-malformed.jsonl"
        with open(p, "w") as f:
            f.write(json.dumps({"emit_time": 1.0, "payload": {"n": 1}}) + "\n")
            f.write("garbage line that's not json\n")  # mid-file, with \n
            f.write(json.dumps({"emit_time": 2.0, "payload": {"n": 2}}) + "\n")
        with pytest.raises(RuntimeError, match="malformed"):
            FileBackedReplayEventStream(path=p, cursor_fn=lambda e: e["n"])


# ----------------------------------------------------------------
# Rule 30 — TTL purges disk
# ----------------------------------------------------------------


class TestRehydrationResourceCleanup:
    @pytest.mark.parametrize("callback", ["deserializer", "cursor"])
    @pytest.mark.parametrize("failure", [ValueError, FileNotFoundError, asyncio.CancelledError, GeneratorExit])
    @pytest.mark.parametrize("backend", ["windows", "posix", "native"])
    async def test_callback_failure_releases_exact_owned_resources_and_allows_delete(
        self, tmp_path: Path, monkeypatch, callback, failure, backend
    ) -> None:
        from azure.ai.agentserver.core.streaming import _concrete
        from azure.ai.agentserver.core.streaming._registry import _StreamsRegistry

        if backend == "windows":
            monkeypatch.setattr(_concrete, "fcntl", None)
        elif backend == "posix":
            monkeypatch.setattr(_concrete, "fcntl", SimpleNamespace(LOCK_EX=1, LOCK_NB=2, flock=lambda *args: None))
        path = tmp_path / "failed-recovery.jsonl"
        path.write_text(json.dumps({"emit_time": 1, "payload": {"n": 1}}) + "\n", encoding="utf-8")
        foreign = FileBackedReplayEventStream(path=tmp_path / "foreign.jsonl")
        owners = []
        descriptors = []
        rehydrate = FileBackedReplayEventStream._rehydrate
        primary = failure("callback failed")

        def observe(owner):
            owners.append(owner)
            descriptors.append(owner._lock_fd)
            rehydrate(owner)

        def failed(*args):
            raise primary

        monkeypatch.setattr(FileBackedReplayEventStream, "_rehydrate", observe)
        registry = _StreamsRegistry()
        registry.use_file_backed_replay(
            storage_dir=tmp_path,
            cursor_fn=failed if callback == "cursor" else None,
            serializer=lambda payload: json.dumps(payload).encode("utf-8"),
            deserializer=failed if callback == "deserializer" else json.loads,
        )
        try:
            with pytest.raises(failure) as caught:
                await registry.get("failed-recovery")
            assert caught.value is primary
            assert len(owners) == 1
            assert owners[0]._file.closed
            assert owners[0]._lock_fd is None
            assert owners[0]._lock_path is None
            assert not path.with_suffix(".jsonl.lock").exists()
            assert registry._slots == {}
            assert registry._id_locks == {}
            if descriptors[0] is not None:
                with pytest.raises(OSError):
                    os.fstat(descriptors[0])
            assert not foreign._file.closed
            if foreign._lock_fd is not None:
                os.fstat(foreign._lock_fd)
                assert foreign._lock_path.exists()
            if backend == "posix" and os.name == "nt":
                monkeypatch.setattr(_concrete, "fcntl", None)
            await registry.delete("failed-recovery")
            assert not path.exists()
        finally:
            if backend == "posix" and os.name == "nt":
                foreign._cleanup_locks()
            await foreign._on_delete()

    @pytest.mark.parametrize("artifact", ["file", "descriptor", "lock"])
    @pytest.mark.parametrize("operation", ["direct", "get", "get_or_create"])
    @pytest.mark.parametrize("failure", [ValueError, asyncio.CancelledError])
    async def test_cleanup_failure_surfaces_primary_and_preserves_exact_retry_resources(
        self, tmp_path: Path, monkeypatch, artifact, operation, failure
    ) -> None:
        from azure.ai.agentserver.core.streaming import _concrete
        from azure.ai.agentserver.core.streaming._registry import _StreamsRegistry, _TOMBSTONE

        monkeypatch.setattr(_concrete, "fcntl", None)
        path = tmp_path / "failed-cleanup.jsonl"
        path.write_text(json.dumps({"emit_time": 1, "payload": 1}) + "\n", encoding="utf-8")
        primary = failure("cursor failed")
        cleanup_error = PermissionError("cleanup denied")
        owners = []
        rehydrate = FileBackedReplayEventStream._rehydrate
        close_descriptor = os.close
        unlink = Path.unlink
        active = True

        class FileHandle:
            def __init__(self, handle):
                self.handle = handle

            def __getattr__(self, name):
                return getattr(self.handle, name)

            def close(self):
                if active and artifact == "file":
                    raise cleanup_error
                self.handle.close()

        def observe(owner):
            owners.append(owner)
            owner._file = FileHandle(owner._file)
            rehydrate(owner)

        def denied_close(descriptor):
            if active and artifact == "descriptor" and descriptor == owners[0]._lock_fd:
                raise cleanup_error
            close_descriptor(descriptor)

        def denied_unlink(candidate, *args, **kwargs):
            if active and artifact == "lock" and candidate == path.with_suffix(".jsonl.lock"):
                raise cleanup_error
            return unlink(candidate, *args, **kwargs)

        def failed(payload):
            raise primary

        registry = _StreamsRegistry()
        registry.use_file_backed_replay(storage_dir=tmp_path, cursor_fn=failed)
        with monkeypatch.context() as patch:
            patch.setattr(FileBackedReplayEventStream, "_rehydrate", observe)
            patch.setattr(_concrete.os, "close", denied_close)
            patch.setattr(Path, "unlink", denied_unlink)
            with pytest.raises(PermissionError) as caught:
                if operation == "direct":
                    FileBackedReplayEventStream(path=path, cursor_fn=failed)
                else:
                    await getattr(registry, operation)("failed-cleanup")
            assert caught.value is cleanup_error
            assert caught.value.__context__ is primary
            owner = owners[0]
            assert owner._lock_path == path.with_suffix(".jsonl.lock")
            assert owner._lock_path.exists()
            assert owner._file.closed is (artifact != "file")
            assert (owner._lock_fd is None) is (artifact == "lock")
            assert owner._buffer == []
            assert owner._evictions_since_compaction == 0
            if operation != "direct":
                assert registry._slots["failed-cleanup"] is owner
                assert registry._slots["failed-cleanup"] is not _TOMBSTONE
                assert registry._id_locks == {}
                assert await registry.get_or_create("failed-cleanup") is owner
                with pytest.raises(EventStreamNotFoundError):
                    await owner.emit({"n": 2})
                with pytest.raises(EventStreamNotFoundError):
                    owner._compact_on_disk()
            active = False
            if operation == "direct":
                owner._cleanup_locks()
            else:
                await registry.delete("failed-cleanup")
                assert registry._slots["failed-cleanup"] is _TOMBSTONE
            assert owner._file.closed
            assert owner._lock_fd is None
            assert owner._lock_path is None
        await owner._on_delete()
        assert list(tmp_path.iterdir()) == []

    async def test_callback_error_cannot_retain_another_ids_cleanup_owner(self, tmp_path, monkeypatch) -> None:
        from azure.ai.agentserver.core.streaming import _concrete
        from azure.ai.agentserver.core.streaming._registry import _StreamsRegistry

        monkeypatch.setattr(_concrete, "fcntl", None)
        foreign = FileBackedReplayEventStream(path=tmp_path / "foreign.jsonl")
        path = tmp_path / "current.jsonl"
        path.write_text(json.dumps({"emit_time": 1, "payload": 1}) + "\n", encoding="utf-8")
        primary = OSError("callback failed")
        setattr(primary, "_replay_cleanup_owner", foreign)
        setattr(primary, "_replay_cleanup_id", "current")

        def failed(payload):
            raise primary

        registry = _StreamsRegistry()
        registry.use_file_backed_replay(storage_dir=tmp_path, cursor_fn=failed)
        try:
            with pytest.raises(OSError) as caught:
                await registry.get("current")
            assert caught.value is primary
            assert registry._slots == {}
            assert registry._id_locks == {}
            assert not foreign._file.closed
            os.fstat(foreign._lock_fd)
            assert foreign._lock_path.exists()
            await registry.delete("current")
            assert not path.exists()
        finally:
            await foreign._on_delete()

    async def test_failed_constructor_delete_reacquires_replacement_ownership(self, tmp_path, monkeypatch) -> None:
        from azure.ai.agentserver.core.streaming import _concrete
        from azure.ai.agentserver.core.streaming._registry import _StreamsRegistry, _TOMBSTONE

        monkeypatch.setattr(_concrete, "fcntl", None)
        path = tmp_path / "constructor-owner.jsonl"
        lock_path = path.with_suffix(".jsonl.lock")
        path.write_text(json.dumps({"emit_time": 1, "payload": 1}) + "\n", encoding="utf-8")
        unlink = Path.unlink

        def failed(payload):
            raise ValueError("cursor failed")

        def denied(candidate, *args, **kwargs):
            if candidate == lock_path:
                raise PermissionError("lock removal denied")
            return unlink(candidate, *args, **kwargs)

        registry = _StreamsRegistry()
        registry.use_file_backed_replay(storage_dir=tmp_path, cursor_fn=failed)
        with monkeypatch.context() as patch:
            patch.setattr(Path, "unlink", denied)
            with pytest.raises(PermissionError):
                await registry.get("constructor-owner")
        owner = registry._slots["constructor-owner"]
        assert owner._write_failed
        owner._cleanup_locks()
        foreign = FileBackedReplayEventStream(path=path)
        try:
            with pytest.raises(RuntimeError, match="another process holds"):
                await registry.delete("constructor-owner")
            assert registry._slots["constructor-owner"] is owner
            assert not foreign._file.closed
            os.fstat(foreign._lock_fd)
            assert lock_path.exists()
            assert path.exists()
        finally:
            foreign._cleanup_locks()
        await registry.delete("constructor-owner")
        assert registry._slots["constructor-owner"] is _TOMBSTONE
        assert registry._id_locks == {}
        assert list(tmp_path.iterdir()) == []


class TestTTLPurgesDisk:
    async def test_ttl_eviction_removes_from_buffer(self, tmp_path: Path) -> None:
        """Rule 30 — TTL eviction removes expired records from the
        in-memory buffer (disk compaction is lazy)."""
        p = tmp_path / "fb-ttl.jsonl"
        s = FileBackedReplayEventStream(path=p, cursor_fn=lambda e: e["n"], ttl_seconds=0.2)
        await s.emit({"n": 1})
        await asyncio.sleep(0.3)
        # Trigger eviction via next op — _evict_expired runs as part
        # of emit(); after this call the buffer should hold only n=2.
        await s.emit({"n": 2})
        # event 1 should have been evicted from buffer
        assert len(s._buffer) == 1, f"event 1 should be evicted; buffer has {len(s._buffer)} entries"
        assert s._buffer[0].payload == {"n": 2}
        await s._on_delete()


# ----------------------------------------------------------------
# Rule 31 — _on_delete removes file
# ----------------------------------------------------------------


class TestOnDeleteRemovesFile:
    async def test_on_delete_unlinks_file(self, tmp_path: Path) -> None:
        """Rule 31 — _on_delete removes the file; no orphaned state."""
        p = tmp_path / "fb-del.jsonl"
        s = FileBackedReplayEventStream(path=p, cursor_fn=lambda e: e["n"])
        await s.emit({"n": 1})
        assert p.exists()
        await s._on_delete()
        assert not p.exists(), "file MUST be unlinked after _on_delete per rule 31"


class TestFileLifecycleOrdering:
    @pytest.mark.parametrize("terminal", ["final", "non-final", "absent"])
    async def test_recovery_compaction_preserves_final_terminal_and_close_clock(self, tmp_path, monkeypatch, terminal):
        from azure.ai.agentserver.core.streaming import _concrete
        from azure.ai.agentserver.core.streaming._registry import _StreamsRegistry, _TOMBSTONE

        path = tmp_path / "recovered-compaction.jsonl"
        expired = [{"emit_time": 9000 + index / 1000, "payload": {"cursor": 10000 - index}} for index in range(1000)]
        live = {"emit_time": 9995, "payload": {"cursor": 3}}
        records = list(expired)
        if terminal == "non-final":
            records.append({"__terminal__": True})
        records.append(live)
        if terminal == "final":
            records.append({"__terminal__": True})
        path.write_text("".join(json.dumps(record) + "\n" for record in records), encoding="utf-8")
        monkeypatch.setattr(_concrete.time, "time", lambda: 10000)
        cursors = []

        def cursor(payload):
            cursors.append(payload["cursor"])
            return payload["cursor"]

        # Windows cannot replace the open destination. Model a successful
        # replacement so this test reaches the recovery compaction contract.
        owners = []
        rehydrate = FileBackedReplayEventStream._rehydrate
        replace = os.replace

        def observe(owner):
            owners.append(owner)
            rehydrate(owner)

        def commit(source, destination):
            if os.name == "nt":
                owners[-1]._file.close()
            replace(source, destination)

        monkeypatch.setattr(FileBackedReplayEventStream, "_rehydrate", observe)
        monkeypatch.setattr(_concrete.os, "replace", commit)
        first = FileBackedReplayEventStream(path=path, cursor_fn=cursor, ttl_seconds=10)
        try:
            assert cursors == [record["payload"]["cursor"] for record in expired] + [3]
            assert first._highest_cursor == 10000
            expected = [live] + ([{"__terminal__": True}] if terminal == "final" else [])
            assert [json.loads(line) for line in path.read_text().splitlines()] == expected
            assert len(first._buffer) == 1
        finally:
            first._cleanup_locks()

        restarted = _StreamsRegistry()
        restarted.use_file_backed_replay(storage_dir=tmp_path, cursor_fn=cursor, ttl_seconds=10)
        restored = await restarted.get("recovered-compaction")
        try:
            assert await restored.last_cursor() == 3
            if terminal == "final":
                assert restored._state == "CLOSED"
                assert restored._close_time == 9995
                assert [event async for event in restored.subscribe()] == [{"cursor": 3}]
                with pytest.raises(EventStreamClosedError):
                    await restored.emit({"cursor": 4})
                monkeypatch.setattr(_concrete.time, "time", lambda: 10005)
                with pytest.raises(EventStreamNotFoundError):
                    await restarted.get("recovered-compaction")
                assert restarted._slots["recovered-compaction"] is _TOMBSTONE
                assert list(tmp_path.iterdir()) == []
            else:
                assert restored._state == "ACTIVE"
                await restored.emit({"cursor": 4})
        finally:
            await restarted.delete("recovered-compaction")

    @pytest.mark.parametrize("backend", ["windows", "posix"])
    async def test_delete_keeps_writer_ownership_until_backing_is_removed(self, tmp_path, monkeypatch, backend):
        from azure.ai.agentserver.core.streaming import _concrete

        held = set()

        def flock(descriptor, flags):
            del flags
            if held:
                raise BlockingIOError("owned inode")
            held.add(descriptor)

        monkeypatch.setattr(
            _concrete, "fcntl", None if backend == "windows" else SimpleNamespace(LOCK_EX=1, LOCK_NB=2, flock=flock)
        )
        path = tmp_path / "ownership.jsonl"
        stream = FileBackedReplayEventStream(path=path)
        original = stream._file
        descriptor = original.fileno()
        released = False

        class Handle:
            @property
            def closed(self):
                return released

            def __getattr__(self, name):
                return getattr(original, name)

            def close(self):
                nonlocal released
                if backend == "posix":
                    assert not path.exists(), "POSIX ownership must survive until unlink"
                original.close()
                held.discard(descriptor)
                released = True

        stream._file = Handle()
        unlink = Path.unlink
        observations = []

        def remove(candidate, *args, **kwargs):
            if candidate == path:
                observations.append("removing")
                assert stream._file.closed is (backend == "windows")
                if backend == "windows":
                    os.fstat(stream._lock_fd)
                    assert stream._lock_path.exists()
                else:
                    assert held == {descriptor}
                with pytest.raises(RuntimeError, match="another process holds"):
                    FileBackedReplayEventStream(path=path)
                if backend == "posix" and os.name == "nt":
                    # Model POSIX unlink while keeping the mocked inode lock.
                    original.close()
                result = unlink(candidate, *args, **kwargs)
                if backend == "windows":
                    with pytest.raises(RuntimeError, match="another process holds"):
                        FileBackedReplayEventStream(path=path)
                    assert not path.exists(), "a lock loser must not recreate the deleted log"
                return result
            return unlink(candidate, *args, **kwargs)

        try:
            with monkeypatch.context() as patch:
                patch.setattr(Path, "unlink", remove)
                await stream._on_delete()
        finally:
            stream._file = original
            stream._cleanup_locks()
            held.discard(descriptor)
        assert observations == ["removing"]
        assert list(tmp_path.iterdir()) == []
        successor = FileBackedReplayEventStream(path=path)
        try:
            await successor.emit({"n": "successor"})
            await stream._on_delete()
            assert '"successor"' in path.read_text()
        finally:
            successor._cleanup_locks()

    @pytest.mark.skipif(not hasattr(os, "fork"), reason="inode-lock waiter regression requires POSIX")
    @pytest.mark.parametrize("timing", ["before-unlink", "after-unlink", "after-release", "after-replacement"])
    async def test_cross_process_delayed_open_cannot_acknowledge_a_deleted_inode(self, tmp_path, monkeypatch, timing):
        path = tmp_path / "delayed-writer.jsonl"
        stream = FileBackedReplayEventStream(path=path)
        await stream.emit({"n": "owner"})
        context = multiprocessing.get_context("spawn")
        parent, child = context.Pipe()
        process = context.Process(target=_delayed_replay_writer, args=(str(path), child))
        process.start()
        child.close()
        unlink = Path.unlink
        cleanup = stream._cleanup_locks
        results = []
        successor = None

        def attempt():
            parent.send("acquire")
            assert parent.poll(10), "delayed writer did not finish"
            results.append(parent.recv())

        def remove(candidate, *args, **kwargs):
            if candidate == path and timing == "before-unlink":
                attempt()
            result = unlink(candidate, *args, **kwargs)
            if candidate == path and timing == "after-unlink":
                attempt()
            return result

        def release():
            nonlocal successor
            cleanup()
            if timing == "after-replacement":
                successor = FileBackedReplayEventStream(path=path)
            if timing in ("after-release", "after-replacement"):
                attempt()

        try:
            assert parent.poll(10), "delayed writer did not open the old inode"
            assert parent.recv() == "opened"
            with monkeypatch.context() as patch:
                patch.setattr(Path, "unlink", remove)
                patch.setattr(stream, "_cleanup_locks", release)
                await stream._on_delete()
            process.join(10)
            assert process.exitcode == 0
            assert results == ["_ReplayFileNotFoundError" if timing == "after-release" else "RuntimeError"]
            if successor is not None:
                await successor.emit({"n": "successor"})
                await stream._on_delete()
                assert '"successor"' in path.read_text()
                assert '"waiter"' not in path.read_text()
            else:
                assert not path.exists()
                assert list(tmp_path.iterdir()) == []
        finally:
            if process.is_alive():
                process.terminate()
            process.join(10)
            parent.close()
            process.close()
            stream._cleanup_locks()
            if successor is not None:
                await successor._on_delete()

    @pytest.mark.parametrize("artifact", ["file", "log", "descriptor", "lock"])
    @pytest.mark.parametrize("failure", [PermissionError, asyncio.CancelledError])
    @pytest.mark.parametrize("write_failed", [False, True])
    async def test_windows_failed_delete_preserves_ownership_and_exact_cleanup_retry(
        self, tmp_path, monkeypatch, artifact, failure, write_failed
    ):
        from azure.ai.agentserver.core.streaming import _concrete
        from azure.ai.agentserver.core.streaming._registry import _StreamsRegistry, _TOMBSTONE

        monkeypatch.setattr(_concrete, "fcntl", None)
        registry = _StreamsRegistry()
        registry.use_file_backed_replay(storage_dir=tmp_path)
        stream = await registry.get_or_create("interrupted-delete")
        await stream.emit({"n": "owner"})
        stream._write_failed = write_failed
        path = tmp_path / "interrupted-delete.jsonl"
        lock_path = path.with_suffix(".jsonl.lock")
        original = stream._file
        primary = failure("owned cleanup interrupted")
        active = True
        unlink = Path.unlink
        close_descriptor = os.close

        class Handle:
            def __getattr__(self, name):
                return getattr(original, name)

            def close(self):
                if active and artifact == "file":
                    raise primary
                original.close()

        stream._file = Handle()
        descriptor = stream._lock_fd

        def remove(candidate, *args, **kwargs):
            if (artifact == "log" and candidate == path) or (artifact == "lock" and candidate == lock_path):
                raise primary
            return unlink(candidate, *args, **kwargs)

        def close(candidate):
            if artifact == "descriptor" and candidate == descriptor:
                raise primary
            close_descriptor(candidate)

        try:
            with monkeypatch.context() as patch:
                patch.setattr(Path, "unlink", remove)
                patch.setattr(_concrete.os, "close", close)
                for _ in range(2):
                    with pytest.raises(failure) as caught:
                        await registry.delete("interrupted-delete")
                    assert caught.value is primary
                    assert registry._slots["interrupted-delete"] is stream
                    assert registry._slots["interrupted-delete"] is not _TOMBSTONE
                    assert registry._id_locks == {}
                    assert path.exists() is (artifact in ("file", "log"))
                    assert lock_path.exists()
                    assert (stream._lock_fd is not None) is (artifact != "lock")
                    if stream._lock_fd is not None:
                        os.fstat(stream._lock_fd)
                    with pytest.raises(RuntimeError, match="another process holds"):
                        FileBackedReplayEventStream(path=path)
                    assert path.exists() is (artifact in ("file", "log"))
                if artifact in ("descriptor", "lock"):
                    # Even an externally recreated path is not this owner's
                    # pending sidecar cleanup target.
                    path.write_text('{"emit_time": 1, "payload": "replacement"}\n', encoding="utf-8")
            active = False
            await registry.delete("interrupted-delete")
            assert registry._slots["interrupted-delete"] is _TOMBSTONE
            assert stream._file.closed
            assert stream._lock_fd is None
            assert stream._lock_path is None
            if artifact in ("descriptor", "lock"):
                assert path.read_text() == '{"emit_time": 1, "payload": "replacement"}\n'
            else:
                assert not path.exists()
        finally:
            active = False
            stream._cleanup_locks()

    async def test_delete_rejects_changed_backing_then_reacquires_only_unowned_replacement(self, tmp_path, monkeypatch):
        from azure.ai.agentserver.core.streaming import _concrete

        monkeypatch.setattr(_concrete, "fcntl", None)
        path = tmp_path / "changed-backing.jsonl"
        stream = FileBackedReplayEventStream(path=path)
        await stream.emit({"n": "original"})
        stream._file.close()
        replacement = tmp_path / "replacement.jsonl"
        content = '{"emit_time": 1, "payload": "replacement"}\n'
        replacement.write_text(content, encoding="utf-8")
        os.replace(replacement, path)
        try:
            with pytest.raises(RuntimeError, match="backing file changed"):
                await stream._on_delete()
            assert stream._write_failed
            assert path.read_text() == content
            os.fstat(stream._lock_fd)
            stream._cleanup_locks()
            foreign = FileBackedReplayEventStream(path=path)
            try:
                with pytest.raises(RuntimeError, match="another process holds"):
                    await stream._on_delete()
                assert path.read_text() == content
                assert not foreign._file.closed
            finally:
                foreign._cleanup_locks()
            await stream._on_delete()
            assert list(tmp_path.iterdir()) == []
        finally:
            stream._cleanup_locks()


# ----------------------------------------------------------------
# Rule 32 — single-writer-per-path
# ----------------------------------------------------------------


class TestSingleWriterPerPath:
    @pytest.mark.skipif(
        not hasattr(os, "fork"),
        reason="fcntl-based lock detection requires POSIX",
    )
    async def test_second_constructor_same_path_raises_runtime_error(self, tmp_path: Path) -> None:
        """Rule 32 — second constructor on same path raises RuntimeError
        (NOT EventStreamError — no instance was constructed)."""
        p = tmp_path / "fb-lock.jsonl"
        s1 = FileBackedReplayEventStream(path=p, cursor_fn=lambda e: e["n"])
        try:
            with pytest.raises(RuntimeError, match="lock"):
                FileBackedReplayEventStream(path=p, cursor_fn=lambda e: e["n"])
        finally:
            await s1._on_delete()


# ----------------------------------------------------------------
# Rule 14 — atomic emit+close
# ----------------------------------------------------------------


class TestAtomicEmitCloseFileBacked:
    async def test_emit_close_true_writes_both_records_atomically(self, tmp_path: Path) -> None:
        """Rule 14 — emit(close=True) on file-backed writes payload +
        terminal marker in a single fsync."""
        p = tmp_path / "fb-atom.jsonl"
        s = FileBackedReplayEventStream(path=p, cursor_fn=lambda e: e["n"])
        await s.emit({"n": 1, "final": True}, close=True)
        # Both records should be on disk
        lines = [l for l in p.read_text().splitlines() if l]
        assert len(lines) == 2  # payload + terminal
        terminal = json.loads(lines[-1])
        assert terminal.get("__terminal__") is True
        await s._on_delete()


# ----------------------------------------------------------------
#  — Close-clock tombstone deletes file (/ SC-19)
# ----------------------------------------------------------------


class TestTaskStreamsFileBackedCloseClock:
    """/ SC-19 — File-backed replay stream: TTL-driven
    tombstone deletes the on-disk JSONL file BEFORE installing the
    registry tombstone.

    Reference: docs/task-and-streaming-spec.md §44, §46, §59
    C-STR-FBR-4.
    """

    @pytest.mark.asyncio
    async def test_file_deleted_when_close_clock_elapses(self, tmp_path: Path) -> None:
        """SC-19 /  — emit + close + advance time past
        ``close_time + ttl_seconds`` → JSONL file removed from disk
        AND ``streams.get(id)`` raises ``EventStreamNotFoundError``.
        """
        from azure.ai.agentserver.core.streaming import streams

        streams.use_file_backed_replay(storage_dir=str(tmp_path), ttl_seconds=0.1)
        stream = await streams.get_or_create("t--fbr-tombstone")
        await stream.emit({"n": 1})
        await stream.close()
        file_path = Path(tmp_path) / "t--fbr-tombstone.jsonl"
        # File still exists pre-tombstone.
        assert file_path.exists(), (
            f"file-backed stream's file should exist before close-clock " f"elapses; expected {file_path}"
        )
        # Wait past the close-clock deadline.
        await asyncio.sleep(0.2)
        with pytest.raises(EventStreamNotFoundError):
            await streams.get("t--fbr-tombstone")
        # And the file is removed (: file cleanup BEFORE
        # registry tombstone).
        assert not file_path.exists(), (
            f" / SC-19 — file-backed stream's JSONL file "
            f"MUST be deleted when the close-clock tombstone fires; "
            f"{file_path} still exists."
        )


# ----------------------------------------------------------------
# Rule 30 — lazy compaction must NOT lose post-compaction writes
# (regression: stale file descriptor after os.replace)
# ----------------------------------------------------------------


class TestCompactionPreservesPostCompactionWrites:
    """After an on-disk compaction swaps the file via ``os.replace``, the
    stream must keep writing to the LIVE file — not the orphaned pre-swap
    inode. Regression for the stale-``self._file`` data-loss bug where every
    ``emit``/``close`` after the first compaction was written to an unlinked
    inode and lost on the next process lifetime.
    """

    async def test_compaction_does_not_recreate_a_removed_replacement(self, tmp_path: Path, monkeypatch) -> None:
        from azure.ai.agentserver.core.streaming import _concrete

        path = tmp_path / "removed-replacement.jsonl"
        stream = FileBackedReplayEventStream(path=path)
        await stream.emit({"n": 1})
        replace = _concrete.os.replace

        def remove_after_replace(source, destination):
            # Release the old data handle so this interleaving also works on Windows.
            stream._file.close()
            replace(source, destination)
            Path(destination).unlink()

        monkeypatch.setattr(_concrete.os, "replace", remove_after_replace)
        try:
            with pytest.raises(FileNotFoundError):
                stream._compact_on_disk()
            assert stream._write_failed
            assert stream._file.closed
            with pytest.raises(RuntimeError, match="writer unavailable"):
                await stream.emit({"n": 2})
            assert not path.exists()
            assert not path.with_suffix(".jsonl.compact").exists()
        finally:
            await stream._on_delete()
        assert list(tmp_path.iterdir()) == []

    @pytest.mark.parametrize("failure", [FileNotFoundError, asyncio.CancelledError, GeneratorExit])
    async def test_reopen_failure_retires_writer_and_wakes_waiting_subscriber(
        self, tmp_path: Path, monkeypatch, failure
    ) -> None:
        from azure.ai.agentserver.core.streaming import _concrete

        path = tmp_path / "failed-reopen.jsonl"
        stream = FileBackedReplayEventStream(path=path)
        await stream.emit({"n": 1})
        iterator = stream.subscribe().__aiter__()
        assert await iterator.__anext__() == {"n": 1}
        waiting = asyncio.create_task(iterator.__anext__())
        await asyncio.sleep(0)
        replace = _concrete.os.replace
        open_file = open
        primary = failure("replacement unavailable")

        def commit(source, destination):
            stream._file.close()
            replace(source, destination)

        def failed_open(candidate, mode):
            if candidate == path and mode == "r+b":
                raise primary
            return open_file(candidate, mode)

        try:
            with monkeypatch.context() as patch:
                patch.setattr(_concrete.os, "replace", commit)
                patch.setattr(_concrete, "open", failed_open, raising=False)
                with pytest.raises(failure) as caught:
                    stream._compact_on_disk()
                assert caught.value is primary
            assert stream._file.closed
            assert stream._retired_files == []
            assert stream._write_failed
            before = path.read_bytes()
            with pytest.raises(RuntimeError, match="writer unavailable"):
                await stream.emit({"n": 2})
            with pytest.raises(RuntimeError, match="writer unavailable"):
                await stream.close()
            with pytest.raises(RuntimeError, match="writer unavailable"):
                stream.subscribe()
            with pytest.raises(RuntimeError, match="writer unavailable"):
                await stream.last_cursor()
            with pytest.raises(RuntimeError, match="writer unavailable"):
                await asyncio.wait_for(waiting, 2)
            assert stream._subscriber_queues == []
            assert path.read_bytes() == before
            assert [event.payload for event in stream._buffer] == [{"n": 1}]
        finally:
            if not waiting.done():
                waiting.cancel()
            await asyncio.gather(waiting, return_exceptions=True)
            await stream._on_delete()

    @pytest.mark.parametrize("stage", ["serialize", "replace"])
    async def test_pre_replacement_failure_preserves_valid_writer(self, tmp_path: Path, monkeypatch, stage) -> None:
        from azure.ai.agentserver.core.streaming import _concrete

        path = tmp_path / "preparation-failed.jsonl"
        stream = FileBackedReplayEventStream(path=path)
        await stream.emit({"n": 1})
        original_handle = stream._file

        def failed(*args):
            raise OSError("preparation failed")

        with monkeypatch.context() as patch:
            if stage == "serialize":
                patch.setattr(stream, "_serialize", failed)
            else:
                patch.setattr(_concrete.os, "replace", failed)
            stream._compact_on_disk()
            assert stream._file is original_handle
            assert not original_handle.closed
            assert not stream._write_failed
            assert not path.with_suffix(".jsonl.compact").exists()
        await stream.emit({"n": 2}, close=True)
        stream._cleanup_locks()
        restored = FileBackedReplayEventStream(path=path)
        assert [event async for event in restored.subscribe()] == [{"n": 1}, {"n": 2}]
        await restored._on_delete()

    async def test_failed_writer_deletion_never_removes_foreign_locked_replacement(self, tmp_path, monkeypatch) -> None:
        from azure.ai.agentserver.core.streaming import _concrete

        monkeypatch.setattr(_concrete, "fcntl", None)
        path = tmp_path / "owned-replacement.jsonl"
        stream = FileBackedReplayEventStream(path=path)
        await stream.emit({"n": 1})
        replace = _concrete.os.replace
        open_file = open

        def commit(source, destination):
            stream._file.close()
            replace(source, destination)

        def failed_open(candidate, mode):
            if candidate == path and mode == "r+b":
                raise PermissionError("reopen denied")
            return open_file(candidate, mode)

        with monkeypatch.context() as patch:
            patch.setattr(_concrete.os, "replace", commit)
            patch.setattr(_concrete, "open", failed_open, raising=False)
            with pytest.raises(PermissionError):
                stream._compact_on_disk()
        foreign = FileBackedReplayEventStream(path=path)
        try:
            expected = path.read_bytes()
            with pytest.raises(RuntimeError, match="another process holds"):
                await stream._on_delete()
            assert not foreign._file.closed
            os.fstat(foreign._lock_fd)
            assert foreign._lock_path.exists()
            assert path.read_bytes() == expected
        finally:
            foreign._cleanup_locks()
        await stream._on_delete()
        assert list(tmp_path.iterdir()) == []

    async def test_replacement_lock_failure_closes_new_handle_and_preserves_primary(self, tmp_path, monkeypatch):
        from azure.ai.agentserver.core.streaming import _concrete

        calls = []
        primary = BlockingIOError("replacement lock denied")

        def flock(descriptor, flags):
            calls.append(descriptor)
            if len(calls) == 2:
                raise primary

        monkeypatch.setattr(_concrete, "fcntl", SimpleNamespace(LOCK_EX=1, LOCK_NB=2, flock=flock))
        path = tmp_path / "lock-failed.jsonl"
        stream = FileBackedReplayEventStream(path=path)
        await stream.emit({"n": 1})
        replace = _concrete.os.replace
        open_file = open
        replacement_handles = []

        def commit(source, destination):
            stream._file.close()
            replace(source, destination)

        def tracked_open(candidate, mode):
            handle = open_file(candidate, mode)
            if candidate == path and mode == "r+b":
                replacement_handles.append(handle)
            return handle

        with monkeypatch.context() as patch:
            patch.setattr(_concrete.os, "replace", commit)
            patch.setattr(_concrete, "open", tracked_open, raising=False)
            with pytest.raises(BlockingIOError) as caught:
                stream._compact_on_disk()
            assert caught.value is primary
            assert replacement_handles[0].closed
            assert stream._file.closed
            assert stream._retired_files == []
        with pytest.raises(RuntimeError, match="writer unavailable"):
            await stream.emit({"n": 2})
        if os.name == "nt":
            monkeypatch.setattr(_concrete, "fcntl", None)
        await stream._on_delete()
        assert list(tmp_path.iterdir()) == []

    async def test_post_replacement_cleanup_failure_retains_handle_for_exact_retry(self, tmp_path, monkeypatch):
        from azure.ai.agentserver.core.streaming import _concrete

        calls = []
        primary = BlockingIOError("replacement lock denied")
        cleanup_error = PermissionError("replacement close denied")
        active = True

        def flock(descriptor, flags):
            calls.append(descriptor)
            if len(calls) == 2:
                raise primary

        monkeypatch.setattr(_concrete, "fcntl", SimpleNamespace(LOCK_EX=1, LOCK_NB=2, flock=flock))
        path = tmp_path / "close-failed.jsonl"
        stream = FileBackedReplayEventStream(path=path)
        await stream.emit({"n": 1})
        replace = _concrete.os.replace
        open_file = open
        replacement_handles = []

        class FileHandle:
            def __init__(self, handle):
                self.handle = handle

            def __getattr__(self, name):
                return getattr(self.handle, name)

            def close(self):
                if active:
                    raise cleanup_error
                self.handle.close()

        def commit(source, destination):
            stream._file.close()
            replace(source, destination)

        def tracked_open(candidate, mode):
            handle = open_file(candidate, mode)
            if candidate == path and mode == "r+b":
                handle = FileHandle(handle)
                replacement_handles.append(handle)
            return handle

        with monkeypatch.context() as patch:
            patch.setattr(_concrete.os, "replace", commit)
            patch.setattr(_concrete, "open", tracked_open, raising=False)
            with pytest.raises(PermissionError) as caught:
                stream._compact_on_disk()
            assert caught.value is cleanup_error
            assert caught.value.__context__ is primary
            assert stream._file.closed
            assert stream._retired_files == [replacement_handles[0]]
            assert not replacement_handles[0].closed
            with pytest.raises(RuntimeError, match="writer unavailable"):
                await stream.emit({"n": 2})
            active = False
        if os.name == "nt":
            monkeypatch.setattr(_concrete, "fcntl", None)
        await stream._on_delete()
        assert replacement_handles[0].closed
        assert stream._retired_files == []
        assert list(tmp_path.iterdir()) == []

    @pytest.mark.parametrize("failure", [asyncio.CancelledError, GeneratorExit])
    async def test_pre_replacement_cancellation_removes_temp_but_keeps_writer(self, tmp_path, monkeypatch, failure):
        path = tmp_path / "cancelled-preparation.jsonl"
        stream = FileBackedReplayEventStream(path=path)
        await stream.emit({"n": 1})
        primary = failure("preparation cancelled")

        def failed(*args):
            raise primary

        with monkeypatch.context() as patch:
            patch.setattr(stream, "_serialize", failed)
            with pytest.raises(failure) as caught:
                stream._compact_on_disk()
            assert caught.value is primary
            assert not stream._write_failed
            assert not stream._file.closed
            assert not path.with_suffix(".jsonl.compact").exists()
        await stream.emit({"n": 2}, close=True)
        assert [event async for event in stream.subscribe()] == [{"n": 1}, {"n": 2}]
        await stream._on_delete()

    @pytest.mark.parametrize("stage", ["seek", "old-close"])
    async def test_post_replacement_seek_or_retirement_failure_closes_exact_handles(self, tmp_path, monkeypatch, stage):
        from azure.ai.agentserver.core.streaming import _concrete

        path = tmp_path / "retirement-failed.jsonl"
        stream = FileBackedReplayEventStream(path=path)
        await stream.emit({"n": 1})
        primary = OSError("replacement setup failed")
        replace = _concrete.os.replace
        open_file = open
        replacements = []

        class FileHandle:
            def __init__(self, handle, old=False):
                self.handle = handle
                self.old = old
                self.closed = False
                self.close_calls = 0

            def __getattr__(self, name):
                return getattr(self.handle, name)

            def seek(self, *args):
                if not self.old and stage == "seek":
                    raise primary
                return self.handle.seek(*args)

            def close(self):
                self.close_calls += 1
                if self.old and stage == "old-close" and self.close_calls == 1:
                    raise primary
                self.handle.close()
                self.closed = True

        old = FileHandle(stream._file, old=True)
        stream._file = old

        def commit(source, destination):
            old.handle.close()
            replace(source, destination)

        def tracked_open(candidate, mode):
            handle = open_file(candidate, mode)
            if candidate == path and mode == "r+b":
                handle = FileHandle(handle)
                replacements.append(handle)
            return handle

        with monkeypatch.context() as patch:
            patch.setattr(_concrete.os, "replace", commit)
            patch.setattr(_concrete, "open", tracked_open, raising=False)
            with pytest.raises(OSError) as caught:
                stream._compact_on_disk()
            assert caught.value is primary
            assert old.closed
            assert replacements[0].closed
            assert stream._retired_files == []
            assert old.close_calls == (2 if stage == "old-close" else 1)
            assert replacements[0].close_calls == 1
        with pytest.raises(RuntimeError, match="writer unavailable"):
            await stream.emit({"n": 2})
        await stream._on_delete()
        assert list(tmp_path.iterdir()) == []

    async def test_pre_replacement_temp_cleanup_failure_preserves_error_context(self, tmp_path, monkeypatch):
        from azure.ai.agentserver.core.streaming import _concrete

        path = tmp_path / "temporary-cleanup.jsonl"
        temporary = path.with_suffix(".jsonl.compact")
        stream = FileBackedReplayEventStream(path=path)
        await stream.emit({"n": 1})
        primary = OSError("replace denied")
        cleanup_error = PermissionError("temporary removal denied")
        unlink = Path.unlink

        def failed_replace(*args):
            raise primary

        def denied_unlink(candidate, *args, **kwargs):
            if candidate == temporary:
                raise cleanup_error
            return unlink(candidate, *args, **kwargs)

        with monkeypatch.context() as patch:
            patch.setattr(_concrete.os, "replace", failed_replace)
            patch.setattr(Path, "unlink", denied_unlink)
            with pytest.raises(PermissionError) as caught:
                stream._compact_on_disk()
            assert caught.value is cleanup_error
            assert caught.value.__cause__ is primary
            assert not stream._write_failed
            assert not stream._file.closed
        temporary.unlink()
        await stream.emit({"n": 2}, close=True)
        await stream._on_delete()

    @pytest.mark.parametrize("disruption", ["cancel", "lock"])
    async def test_failed_writer_retains_deletion_owner_through_interrupted_cleanup(
        self, tmp_path, monkeypatch, disruption
    ):
        from azure.ai.agentserver.core.streaming import _concrete

        monkeypatch.setattr(_concrete, "fcntl", None)
        path = tmp_path / "retry-retired.jsonl"
        lock_path = path.with_suffix(".jsonl.lock")
        stream = FileBackedReplayEventStream(path=path)
        await stream.emit({"n": 1})
        replace = _concrete.os.replace
        open_file = open

        def commit(source, destination):
            stream._file.close()
            replace(source, destination)

        def failed_open(candidate, mode):
            if candidate == path and mode == "r+b":
                raise PermissionError("reopen denied")
            return open_file(candidate, mode)

        with monkeypatch.context() as patch:
            patch.setattr(_concrete.os, "replace", commit)
            patch.setattr(_concrete, "open", failed_open, raising=False)
            with pytest.raises(PermissionError):
                stream._compact_on_disk()
        unlink = Path.unlink
        entered = asyncio.Event()
        release = asyncio.Event()

        def denied(candidate, *args, **kwargs):
            if candidate == lock_path:
                raise PermissionError("deletion lock removal denied")
            return unlink(candidate, *args, **kwargs)

        async def paused(owner):
            entered.set()
            await release.wait()

        with monkeypatch.context() as patch:
            if disruption == "lock":
                patch.setattr(Path, "unlink", denied)
                with pytest.raises(PermissionError):
                    await stream._on_delete()
                owner = stream._deletion_owner
                with pytest.raises(PermissionError):
                    await stream._on_delete()
                assert stream._deletion_owner is owner
                assert owner._lock_fd is None
            else:
                patch.setattr(_concrete._FileBackedReplayDeletion, "_on_delete", paused)
                deleting = asyncio.create_task(stream._on_delete())
                try:
                    await asyncio.wait_for(entered.wait(), 2)
                    owner = stream._deletion_owner
                    deleting.cancel()
                    with pytest.raises(asyncio.CancelledError):
                        await deleting
                    assert stream._deletion_owner is owner
                    assert owner._lock_fd is not None
                finally:
                    if not deleting.done():
                        deleting.cancel()
                    release.set()
                    await asyncio.gather(deleting, return_exceptions=True)
            assert path.exists() is (disruption != "lock")
            assert lock_path.exists()
        await stream._on_delete()
        assert stream._deletion_owner is owner
        assert owner._file.closed
        assert owner._lock_fd is None
        assert list(tmp_path.iterdir()) == []

    @pytest.mark.skipif(not hasattr(os, "fork"), reason="unlinked inode regression requires POSIX")
    async def test_removed_replacement_never_acknowledges_writes_to_old_inode(self, tmp_path, monkeypatch):
        from azure.ai.agentserver.core.streaming import _concrete

        path = tmp_path / "old-inode.jsonl"
        stream = FileBackedReplayEventStream(path=path)
        await stream.emit({"n": 1})
        old_handle = stream._file
        old_descriptor = old_handle.fileno()
        replace = _concrete.os.replace

        def remove(source, destination):
            replace(source, destination)
            Path(destination).unlink()

        monkeypatch.setattr(_concrete.os, "replace", remove)
        with pytest.raises(FileNotFoundError):
            stream._compact_on_disk()
        assert old_handle.closed
        with pytest.raises(OSError):
            os.fstat(old_descriptor)
        with pytest.raises(RuntimeError, match="writer unavailable"):
            await stream.emit({"n": 2})
        assert not path.exists()
        await stream._on_delete()

    async def test_emit_after_compaction_persists_to_live_file(self, tmp_path: Path) -> None:
        p = tmp_path / "fb-compact.jsonl"
        s = FileBackedReplayEventStream(path=p, cursor_fn=lambda e: e["n"], ttl_seconds=600)
        await s.emit({"n": 1})
        await s.emit({"n": 2})
        # Force a compaction (in real runs this fires once the eviction
        # interval is crossed; calling it directly is the accepted
        # intra-process construction-recovery pattern for this suite).
        s._compact_on_disk()
        await s.emit({"n": 3})  # post-compaction write — must NOT be lost
        await s.close()  # terminal — must NOT be lost

        content = p.read_text()
        assert '"n": 3' in content, f"post-compaction emit lost to orphaned inode; file={content!r}"
        assert "__terminal__" in content, f"post-compaction terminal lost; file={content!r}"

    async def test_rehydrate_after_compaction_sees_post_compaction_event(self, tmp_path: Path) -> None:
        p = tmp_path / "fb-compact-rehydrate.jsonl"
        s = FileBackedReplayEventStream(path=p, cursor_fn=lambda e: e["n"], ttl_seconds=600)
        await s.emit({"n": 1})
        s._compact_on_disk()
        await s.emit({"n": 2})
        s._cleanup_locks()  # simulate crash: release lock, keep the file
        del s

        # A new lifetime rehydrating from the same path MUST see the
        # post-compaction event (it was written to the live file).
        s2 = FileBackedReplayEventStream(path=p, cursor_fn=lambda e: e["n"], ttl_seconds=600)
        cursors = [e.payload["n"] for e in s2._buffer]
        assert 2 in cursors, f"post-compaction event missing after rehydrate; buffer={cursors}"
        await s2._on_delete()


# ----------------------------------------------------------------
# C-STR-FBR-6 — a non-final terminal sentinel is IGNORED (Spec 041 PY-1)
# ----------------------------------------------------------------


class TestNonFinalTerminalIgnored:
    async def test_non_final_terminal_marker_ignored(self, tmp_path: Path) -> None:
        """C-STR-FBR-6 — a ``__terminal__`` sentinel that is NOT the final line is
        ignored; loading continues and the stream is NOT closed."""
        p = tmp_path / "fb-midterm.jsonl"
        with open(p, "w", encoding="utf-8") as f:
            f.write(json.dumps({"emit_time": 100.0, "payload": {"n": 1}}) + "\n")
            f.write(json.dumps({"__terminal__": True}) + "\n")  # non-final → ignored
            f.write(json.dumps({"emit_time": 101.0, "payload": {"n": 2}}) + "\n")
        s = FileBackedReplayEventStream(path=p, cursor_fn=lambda e: e["n"], ttl_seconds=600)
        # Final line is an event → the mid-file terminal was ignored, stream open.
        assert s._state != s._STATE_CLOSED
        # Both events parsed (cursor is recorded before TTL eviction).
        assert s._highest_cursor == 2
        await s._on_delete()

    async def test_final_terminal_after_mid_file_terminal_still_closes(self, tmp_path: Path) -> None:
        """C-STR-FBR-6 — a mid-file terminal is ignored, but a terminal sentinel
        that IS the final line still closes the stream."""
        p = tmp_path / "fb-twoterms.jsonl"
        with open(p, "w", encoding="utf-8") as f:
            f.write(json.dumps({"emit_time": 100.0, "payload": {"n": 1}}) + "\n")
            f.write(json.dumps({"__terminal__": True}) + "\n")  # ignored (non-final)
            f.write(json.dumps({"emit_time": 101.0, "payload": {"n": 2}}) + "\n")
            f.write(json.dumps({"__terminal__": True}) + "\n")  # final → closes
        s = FileBackedReplayEventStream(path=p, cursor_fn=lambda e: e["n"], ttl_seconds=600)
        # The final terminal closed the stream (it may then auto-transition to
        # GONE because the ancient emit_time is already past the TTL horizon).
        assert s._state in (s._STATE_CLOSED, s._STATE_GONE)
        assert s._highest_cursor == 2
        await s._on_delete()


# ----------------------------------------------------------------
# C-STR-FBR-3 — serializer/deserializer are both-or-neither (Spec 041 PY-2)
# ----------------------------------------------------------------


class TestSerializerDeserializerPairing:
    async def test_serializer_without_deserializer_raises(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="both-or-neither"):
            FileBackedReplayEventStream(
                path=tmp_path / "fb-half-ser.jsonl",
                serializer=lambda payload: json.dumps(payload).encode("utf-8"),
            )

    async def test_deserializer_without_serializer_raises(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="both-or-neither"):
            FileBackedReplayEventStream(
                path=tmp_path / "fb-half-de.jsonl",
                deserializer=lambda b: json.loads(b.decode("utf-8")),
            )

    async def test_both_supplied_is_accepted(self, tmp_path: Path) -> None:
        s = FileBackedReplayEventStream(
            path=tmp_path / "fb-both.jsonl",
            cursor_fn=lambda e: e["n"],
            serializer=lambda payload: json.dumps(payload).encode("utf-8"),
            deserializer=lambda b: json.loads(b.decode("utf-8")),
        )
        await s.emit({"n": 1})
        await s._on_delete()

    async def test_neither_supplied_is_accepted(self, tmp_path: Path) -> None:
        s = FileBackedReplayEventStream(path=tmp_path / "fb-neither.jsonl", cursor_fn=lambda e: e["n"])
        await s.emit({"n": 1})
        await s._on_delete()
