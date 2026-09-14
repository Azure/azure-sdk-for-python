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
import os
from pathlib import Path

import pytest

from azure.ai.agentserver.core.streaming import (
    EventStreamClosedError,
    EventStreamNotFoundError,
)
from azure.ai.agentserver.core.streaming._concrete import (
    FileBackedReplayEventStream,
)


pytestmark = pytest.mark.asyncio(loop_scope="function")


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
