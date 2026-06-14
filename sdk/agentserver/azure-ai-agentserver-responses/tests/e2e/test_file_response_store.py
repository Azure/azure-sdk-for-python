# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Tests for the file-backed response store provider (T-020, T-053).

Covers spec 013 US1 deliverable (c) acceptance scenario 4: ``create_response``,
``update_response``, ``get_response``, ``delete_response``, and input/history
lookups against a ``FileResponseStore(storage_dir=<tmp_path>)`` exhibit the
same contract as the in-memory provider, with atomic writes and
``ResponseAlreadyExistsError`` on duplicate-create.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from azure.ai.agentserver.responses.models._generated import ResponseObject
from azure.ai.agentserver.responses.store import (
    FileResponseStore,
    ResponseAlreadyExistsError,
)


def _make_response(response_id: str = "resp_test", status: str = "in_progress") -> ResponseObject:
    """Build a minimal ResponseObject for store tests."""
    data: dict[str, Any] = {
        "id": response_id,
        "object": "response",
        "status": status,
        "model": "test-model",
        "output": [],
    }
    return ResponseObject(data)


@pytest.mark.asyncio
async def test_create_response_persists_to_file(tmp_path: Path) -> None:
    """``create_response`` writes a JSON file at the documented layout."""
    store = FileResponseStore(storage_dir=tmp_path)
    response = _make_response("resp_001")
    await store.create_response(response, input_items=None, history_item_ids=None)
    assert (tmp_path / "responses" / "resp_001.json").exists()


@pytest.mark.asyncio
async def test_get_response_round_trips(tmp_path: Path) -> None:
    """A response written via create is retrievable via get."""
    store = FileResponseStore(storage_dir=tmp_path)
    original = _make_response("resp_002")
    await store.create_response(original, input_items=None, history_item_ids=None)
    fetched = await store.get_response("resp_002")
    assert str(fetched["id"]) == "resp_002"
    assert str(fetched["status"]) == "in_progress"


@pytest.mark.asyncio
async def test_create_response_raises_on_duplicate(tmp_path: Path) -> None:
    """A second create for the same response_id raises ResponseAlreadyExistsError."""
    store = FileResponseStore(storage_dir=tmp_path)
    response = _make_response("resp_dup")
    await store.create_response(response, input_items=None, history_item_ids=None)
    with pytest.raises(ResponseAlreadyExistsError) as exc_info:
        await store.create_response(response, input_items=None, history_item_ids=None)
    assert exc_info.value.response_id == "resp_dup"


@pytest.mark.asyncio
async def test_update_response_replaces_persisted_content(tmp_path: Path) -> None:
    """update_response overwrites the persisted JSON."""
    store = FileResponseStore(storage_dir=tmp_path)
    initial = _make_response("resp_003", status="in_progress")
    await store.create_response(initial, input_items=None, history_item_ids=None)
    terminal = _make_response("resp_003", status="completed")
    await store.update_response(terminal)
    fetched = await store.get_response("resp_003")
    assert str(fetched["status"]) == "completed"


@pytest.mark.asyncio
async def test_update_response_raises_when_missing(tmp_path: Path) -> None:
    """update_response on a non-existent response raises KeyError."""
    store = FileResponseStore(storage_dir=tmp_path)
    with pytest.raises(KeyError):
        await store.update_response(_make_response("resp_missing"))


@pytest.mark.asyncio
async def test_delete_response_marks_deleted(tmp_path: Path) -> None:
    """delete_response marks the entry deleted; subsequent get raises KeyError."""
    store = FileResponseStore(storage_dir=tmp_path)
    response = _make_response("resp_004")
    await store.create_response(response, input_items=None, history_item_ids=None)
    await store.delete_response("resp_004")
    with pytest.raises(KeyError):
        await store.get_response("resp_004")


@pytest.mark.asyncio
async def test_storage_survives_new_provider_instance(tmp_path: Path) -> None:
    """A fresh FileResponseStore against the same storage_dir sees the persisted response."""
    store1 = FileResponseStore(storage_dir=tmp_path)
    await store1.create_response(_make_response("resp_persist"), input_items=None, history_item_ids=None)
    # Simulate process restart: new store instance, same storage dir
    store2 = FileResponseStore(storage_dir=tmp_path)
    fetched = await store2.get_response("resp_persist")
    assert str(fetched["id"]) == "resp_persist"


@pytest.mark.asyncio
async def test_history_item_ids_round_trip(tmp_path: Path) -> None:
    """history_item_ids passed to create_response are retrievable via get_history_item_ids."""
    store = FileResponseStore(storage_dir=tmp_path)
    response = _make_response("resp_with_history")
    await store.create_response(response, input_items=None, history_item_ids=["item_a", "item_b", "item_c"])
    ids = await store.get_history_item_ids("resp_with_history", conversation_id=None, limit=10)
    assert ids == ["item_a", "item_b", "item_c"]


@pytest.mark.asyncio
async def test_atomic_write_no_partial_file_on_concurrent_read(tmp_path: Path) -> None:
    """Writes are atomic — reader sees either the full prior state or the full new state.

    This is a smoke test for the ``os.replace()`` pattern. We can't truly race
    reads against writes in a single-threaded async test, but we can verify
    that the tempfile is gone after a write completes (i.e., the write was
    finalised via replace, not left as a half-write).
    """
    store = FileResponseStore(storage_dir=tmp_path)
    response = _make_response("resp_atomic")
    await store.create_response(response, input_items=None, history_item_ids=None)
    # Tempfile should not survive a completed write.
    tmp_files = list((tmp_path / "responses").glob("*.tmp"))
    assert tmp_files == []
