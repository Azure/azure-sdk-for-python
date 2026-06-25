# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Bootstrap tests for the responses host's streams-registry wiring.

Assertions:

1. Constructing ``ResponsesAgentServerHost`` with
   ``resilient_background=True`` configures the registry's file-backed
   replay backing — verified by inspecting that the next stream we mint
   for an arbitrary id lands on disk under the configured directory.
2. ``await streams.get_or_create("resp-abc")`` returns the same
   instance across calls (idempotency).
3. ``await streams.delete("resp-abc")`` removes the registry entry
   AND the on-disk log; subsequent ``get`` raises Gone.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator

import pytest

from azure.ai.agentserver.core.streaming import (
    EventStream,
    EventStreamNotFoundError,
    streams,
)
from azure.ai.agentserver.responses import (
    ResponsesAgentServerHost,
    ResponsesServerOptions,
)

# ---------------------------------------------------------------------------
# Per-test fixture: snapshot/restore the registry's private state so the
# bootstrap calls below do not leak across tests.
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _isolate_streams_registry() -> Iterator[None]:
    saved_slots = dict(streams._slots)  # type: ignore[attr-defined]
    saved_locks = dict(streams._id_locks)  # type: ignore[attr-defined]
    saved_factory = streams._factory  # type: ignore[attr-defined]
    streams._slots.clear()  # type: ignore[attr-defined]
    streams._id_locks.clear()  # type: ignore[attr-defined]
    streams.use_in_memory_live()
    try:
        yield
    finally:
        streams._slots.clear()  # type: ignore[attr-defined]
        streams._slots.update(saved_slots)  # type: ignore[attr-defined]
        streams._id_locks.clear()  # type: ignore[attr-defined]
        streams._id_locks.update(saved_locks)  # type: ignore[attr-defined]
        streams._factory = saved_factory  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_host_construction_configures_file_backed_replay(tmp_path: Path) -> None:
    """``resilient_background=True`` selects the file-backed backing and
    points it at the operator-supplied storage directory.

    (Spec 024 Phase 3a) ``AGENTSERVER_STATE_ROOT`` is the single env
    var; streams live at ``<root>/streams/``.
    """
    os.environ["AGENTSERVER_STATE_ROOT"] = str(tmp_path)
    try:
        ResponsesAgentServerHost(options=ResponsesServerOptions(resilient_background=True))

        stream = await streams.get_or_create("resp-bootstrap-1")
        assert isinstance(stream, EventStream)
        # File-backed backing materialises the on-disk log eagerly so that
        # rehydration on restart sees the same file. The file is named
        # ``<id>.jsonl`` per the SDK's file-backed contract and lives
        # under ``<root>/streams/``.
        assert (tmp_path / "streams" / "resp-bootstrap-1.jsonl").exists()
    finally:
        os.environ.pop("AGENTSERVER_STATE_ROOT", None)


@pytest.mark.asyncio
async def test_get_or_create_is_idempotent(tmp_path: Path) -> None:
    os.environ["AGENTSERVER_STATE_ROOT"] = str(tmp_path)
    try:
        ResponsesAgentServerHost(options=ResponsesServerOptions(resilient_background=True))

        s1 = await streams.get_or_create("resp-abc")
        s2 = await streams.get_or_create("resp-abc")
        assert s1 is s2
    finally:
        os.environ.pop("AGENTSERVER_STATE_ROOT", None)


@pytest.mark.asyncio
async def test_delete_removes_registry_entry_and_on_disk_file(tmp_path: Path) -> None:
    os.environ["AGENTSERVER_STATE_ROOT"] = str(tmp_path)
    try:
        ResponsesAgentServerHost(options=ResponsesServerOptions(resilient_background=True))

        await streams.get_or_create("resp-abc")
        assert (tmp_path / "streams" / "resp-abc.jsonl").exists()

        await streams.delete("resp-abc")
        assert not (tmp_path / "streams" / "resp-abc.jsonl").exists()
        with pytest.raises(EventStreamNotFoundError):
            await streams.get("resp-abc")
    finally:
        os.environ.pop("AGENTSERVER_STATE_ROOT", None)


@pytest.mark.asyncio
async def test_non_resilient_host_uses_in_memory_replay(tmp_path: Path) -> None:
    """``resilient_background=False`` selects the in-memory replay
    backing — verified by minting a stream and confirming no on-disk
    log is created (file-backed would create one eagerly)."""
    os.environ["AGENTSERVER_STATE_ROOT"] = str(tmp_path)
    try:
        ResponsesAgentServerHost(options=ResponsesServerOptions(resilient_background=False))

        stream = await streams.get_or_create("resp-mem")
        assert isinstance(stream, EventStream)
        # In-memory backing must not touch the storage dir.
        assert not (tmp_path / "streams" / "resp-mem.jsonl").exists()
    finally:
        os.environ.pop("AGENTSERVER_STATE_ROOT", None)
