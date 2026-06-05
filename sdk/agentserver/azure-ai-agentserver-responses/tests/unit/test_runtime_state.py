# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for _RuntimeState with ResponseExecution values."""

from __future__ import annotations

import pytest

from azure.ai.agentserver.responses.hosting._runtime_state import _RuntimeState
from azure.ai.agentserver.responses.models._generated import ResponseObject
from azure.ai.agentserver.responses.models.runtime import ResponseExecution, ResponseModeFlags

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_execution(
    response_id: str,
    *,
    store: bool = True,
    background: bool = False,
    stream: bool = False,
    status: str = "queued",
    input_items: list[dict] | None = None,
    previous_response_id: str | None = None,
) -> ResponseExecution:
    return ResponseExecution(
        response_id=response_id,
        mode_flags=ResponseModeFlags(stream=stream, store=store, background=background),
        status=status,  # type: ignore[arg-type]
        input_items=input_items,
        previous_response_id=previous_response_id,
    )


# ---------------------------------------------------------------------------
# T1 – add + get returns the same object
# ---------------------------------------------------------------------------


async def test_add_and_get() -> None:
    state = _RuntimeState()
    execution = _make_execution("caresp_aaa0000000000000000000000000000")
    await state.add(execution)
    retrieved = await state.get("caresp_aaa0000000000000000000000000000")
    assert retrieved is execution


# ---------------------------------------------------------------------------
# T2 – get unknown returns None
# ---------------------------------------------------------------------------


async def test_get_nonexistent_returns_none() -> None:
    state = _RuntimeState()
    assert await state.get("unknown_id") is None


# ---------------------------------------------------------------------------
# T3 – delete marks deleted; get returns None; is_deleted returns True
# ---------------------------------------------------------------------------


async def test_delete_marks_deleted() -> None:
    state = _RuntimeState()
    execution = _make_execution("caresp_bbb0000000000000000000000000000")
    await state.add(execution)

    result = await state.delete("caresp_bbb0000000000000000000000000000")

    assert result is True
    assert await state.get("caresp_bbb0000000000000000000000000000") is None
    assert await state.is_deleted("caresp_bbb0000000000000000000000000000") is True


# ---------------------------------------------------------------------------
# T4 – delete non-existent returns False
# ---------------------------------------------------------------------------


async def test_delete_nonexistent_returns_false() -> None:
    state = _RuntimeState()
    assert await state.delete("nonexistent_id") is False


# ---------------------------------------------------------------------------
# T5 – get_input_items single execution (no chain)
# ---------------------------------------------------------------------------


async def test_get_input_items_single() -> None:
    state = _RuntimeState()
    items = [{"id": "item_1", "type": "message"}]
    execution = _make_execution(
        "caresp_ccc0000000000000000000000000000",
        input_items=items,
        previous_response_id=None,
    )
    await state.add(execution)

    result = await state.get_input_items("caresp_ccc0000000000000000000000000000")
    assert result == items


# ---------------------------------------------------------------------------
# T6 – get_input_items chain walk (parent items come first)
# ---------------------------------------------------------------------------


async def test_get_input_items_chain_walk() -> None:
    state = _RuntimeState()
    parent_id = "caresp_parent000000000000000000000000"
    child_id = "caresp_child0000000000000000000000000"

    parent = _make_execution(parent_id, input_items=[{"id": "a"}])
    child = _make_execution(child_id, input_items=[{"id": "b"}], previous_response_id=parent_id)

    await state.add(parent)
    await state.add(child)

    result = await state.get_input_items(child_id)
    ids = [item["id"] for item in result]
    assert ids == ["a", "b"]


# ---------------------------------------------------------------------------
# T7 – get_input_items on deleted response raises ValueError
# ---------------------------------------------------------------------------


async def test_get_input_items_deleted_raises_value_error() -> None:
    state = _RuntimeState()
    execution = _make_execution("caresp_ddd0000000000000000000000000000")
    await state.add(execution)
    await state.delete("caresp_ddd0000000000000000000000000000")

    with pytest.raises(ValueError, match="deleted"):
        await state.get_input_items("caresp_ddd0000000000000000000000000000")


# ---------------------------------------------------------------------------
# T8 – to_snapshot with response set returns dict with required fields
# ---------------------------------------------------------------------------


def test_to_snapshot_with_response() -> None:
    rid = "caresp_eee0000000000000000000000000000"
    execution = _make_execution(rid, status="completed")
    execution.response = ResponseObject(
        {
            "id": rid,
            "response_id": rid,
            "agent_reference": {"name": "test-agent"},
            "object": "response",
            "status": "completed",
            "output": [],
        }
    )

    snapshot = _RuntimeState.to_snapshot(execution)

    assert isinstance(snapshot, dict)
    assert snapshot["status"] == "completed"
    assert snapshot["id"] == rid
    assert snapshot["response_id"] == rid


# ---------------------------------------------------------------------------
# T9 – to_snapshot with no response returns minimal dict for queued state
# ---------------------------------------------------------------------------


def test_to_snapshot_queued_no_response() -> None:
    rid = "caresp_fff0000000000000000000000000000"
    execution = _make_execution(rid, status="queued")
    # execution.response is None

    snapshot = _RuntimeState.to_snapshot(execution)

    assert snapshot["id"] == rid
    assert snapshot["response_id"] == rid
    assert snapshot["object"] == "response"
    assert snapshot["status"] == "queued"


# ---------------------------------------------------------------------------
# Extra: to_snapshot status field overrides response payload status
# ---------------------------------------------------------------------------


def test_to_snapshot_status_matches_execution_status() -> None:
    """to_snapshot should authoritative-stamp status from execution.status."""
    rid = "caresp_ggg0000000000000000000000000000"
    execution = _make_execution(rid, status="in_progress")
    # Give a response that says completed but execution.status says in_progress
    execution.response = ResponseObject({"id": rid, "status": "completed", "output": []})

    snapshot = _RuntimeState.to_snapshot(execution)

    assert snapshot["status"] == "in_progress"


# ---------------------------------------------------------------------------
# Extra: to_snapshot injects id/response_id defaults when missing from response
# ---------------------------------------------------------------------------


def test_to_snapshot_injects_defaults_when_response_missing_ids() -> None:
    rid = "caresp_hhh0000000000000000000000000000"
    execution = _make_execution(rid, status="completed")
    # Response without id/response_id
    execution.response = ResponseObject({"status": "completed", "output": []})

    snapshot = _RuntimeState.to_snapshot(execution)

    assert snapshot["id"] == rid
    assert snapshot["response_id"] == rid
    assert snapshot["object"] == "response"


# ---------------------------------------------------------------------------
# Extra: list_records returns all stored executions
# ---------------------------------------------------------------------------


async def test_list_records_returns_all() -> None:
    state = _RuntimeState()
    e1 = _make_execution("caresp_iii0000000000000000000000000000")
    e2 = _make_execution("caresp_jjj0000000000000000000000000000")
    await state.add(e1)
    await state.add(e2)

    records = await state.list_records()
    assert len(records) == 2
    ids = {r.response_id for r in records}
    assert ids == {"caresp_iii0000000000000000000000000000", "caresp_jjj0000000000000000000000000000"}


# ---------------------------------------------------------------------------
# T1 (Task 7.1) – _ExecutionRecord is no longer exported from _runtime_state
# ---------------------------------------------------------------------------


def test_import_does_not_expose_execution_record() -> None:
    """_ExecutionRecord was deleted in Task 7.1; the module must not export it."""
    import importlib

    mod = importlib.import_module("azure.ai.agentserver.responses.hosting._runtime_state")
    assert not hasattr(mod, "_ExecutionRecord"), (
        "_ExecutionRecord should have been removed from _runtime_state in Phase 7 / Task 7.1"
    )
