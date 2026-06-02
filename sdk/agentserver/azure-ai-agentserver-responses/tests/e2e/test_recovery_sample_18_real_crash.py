# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Crash-window integration tests for cross-process recovery (T-023).

Covers spec 013 US1 acceptance scenarios 6 and 9 — the two crash windows:

- **Window 2** (post-`task_fn.start`, pre-`response.created`): on recovery the
  response object lands in ``FileResponseStore`` via the create path.
- **Window 3** (post-`response.created`, pre-terminal): on recovery the
  swallow at the persist site fires, the existing response stays in the
  store, and the terminal update lands.

These tests drive the reconstruction + idempotent-create code paths directly
rather than via a spawned subprocess. The subprocess-driven variant lives
in the live Copilot tests (Phase 8) and the harness self-tests
(``test_crash_harness_self.py``) cover the harness mechanics independently.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from azure.ai.agentserver.responses.models._generated import ResponseObject
from azure.ai.agentserver.responses.store import (
    FileResponseStore,
    ResponseAlreadyExistsError,
)


def _make_response(response_id: str, status: str = "in_progress") -> ResponseObject:
    return ResponseObject(
        {
            "id": response_id,
            "object": "response",
            "status": status,
            "model": "test-model",
            "output": [],
        }
    )


class TestWindow2Orphan:
    """Crash between task_fn.start and first response.created.

    On recovery the response store is empty. The first reach of
    ``response.created`` on the recovered attempt lands the response cleanly
    via the create path (no swallow needed because the store has no entry).
    """

    @pytest.mark.asyncio
    async def test_window2_create_lands_on_recovery(self, tmp_path: Path) -> None:
        store = FileResponseStore(storage_dir=tmp_path)
        # Simulate: fresh attempt crashed before response.created.
        # The store is empty for this response_id.
        # Recovery attempt: handler reaches response.created and persists.
        await store.create_response(_make_response("resp_window2"), None, None)
        fetched = await store.get_response("resp_window2")
        assert str(fetched["id"]) == "resp_window2"


class TestWindow3Swallow:
    """Crash between response.created and terminal event.

    On recovery the response object IS in the store from the prior attempt.
    The recovered handler's re-emit of response.created raises
    ``ResponseAlreadyExistsError``, which the orchestrator swallows; the
    terminal update_response succeeds.
    """

    @pytest.mark.asyncio
    async def test_window3_swallow_path_at_store_level(self, tmp_path: Path) -> None:
        store = FileResponseStore(storage_dir=tmp_path)
        # First attempt persisted response.created.
        await store.create_response(_make_response("resp_window3", "in_progress"), None, None)
        # Recovered handler tries to create again — must raise typed exception.
        with pytest.raises(ResponseAlreadyExistsError) as exc_info:
            await store.create_response(_make_response("resp_window3"), None, None)
        assert exc_info.value.response_id == "resp_window3"
        # Terminal update from the recovered attempt succeeds.
        await store.update_response(_make_response("resp_window3", "completed"))
        fetched = await store.get_response("resp_window3")
        assert str(fetched["status"]) == "completed"


class TestStorageSurvivesRestart:
    """The file-backed store persists across new provider instances.

    Sanity check: a new FileResponseStore against the same storage_dir sees
    everything the prior instance wrote. This is the property that lets the
    crash harness work — kill subprocess, restart subprocess, the new
    subprocess sees the prior subprocess's response store contents.
    """

    @pytest.mark.asyncio
    async def test_response_survives_new_store_instance(self, tmp_path: Path) -> None:
        store1 = FileResponseStore(storage_dir=tmp_path)
        await store1.create_response(_make_response("resp_survives"), None, None)
        # Simulate process restart.
        store2 = FileResponseStore(storage_dir=tmp_path)
        fetched = await store2.get_response("resp_survives")
        assert str(fetched["id"]) == "resp_survives"
