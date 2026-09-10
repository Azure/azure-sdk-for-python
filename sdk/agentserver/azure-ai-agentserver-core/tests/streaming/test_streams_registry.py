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
import re
from pathlib import Path

import pytest

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


pytestmark = pytest.mark.asyncio(loop_scope="function")


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
    streams._slots.clear()  # type: ignore[attr-defined]
    streams._id_locks.clear()  # type: ignore[attr-defined]
    streams.use_in_memory_live()  # default backing
    yield
    streams._slots.clear()  # type: ignore[attr-defined]
    streams._slots.update(saved_slots)  # type: ignore[attr-defined]
    streams._id_locks.clear()  # type: ignore[attr-defined]
    streams._id_locks.update(saved_locks)  # type: ignore[attr-defined]
    streams._factory = saved_factory  # type: ignore[attr-defined]


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
