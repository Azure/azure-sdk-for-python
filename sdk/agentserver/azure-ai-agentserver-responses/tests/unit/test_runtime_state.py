# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for _RuntimeState with ResponseExecution values."""

from __future__ import annotations

import asyncio
from typing import cast

import pytest

from azure.ai.agentserver.responses.hosting._runtime_state import _RuntimeState
from azure.ai.agentserver.responses import ResponseContext
from azure.ai.agentserver.responses.models import ResponseObject
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
    user_id_key: str | None = None,
) -> ResponseExecution:
    return ResponseExecution(
        response_id=response_id,
        mode_flags=ResponseModeFlags(stream=stream, store=store, background=background),
        status=status,  # type: ignore[arg-type]
        input_items=input_items,
        previous_response_id=previous_response_id,
        user_id_key=user_id_key,
    )


# ---------------------------------------------------------------------------
# T1 – add + get returns the same object
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_add_and_get() -> None:
    state = _RuntimeState()
    execution = _make_execution("caresp_aaa0000000000000000000000000000")
    await state.add(execution)
    retrieved = await state.get("caresp_aaa0000000000000000000000000000")
    assert retrieved is execution


# ---------------------------------------------------------------------------
# T2 – get unknown returns None
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_nonexistent_returns_none() -> None:
    state = _RuntimeState()
    assert await state.get("unknown_id") is None


@pytest.mark.asyncio
async def test_same_id_records_are_partitioned_by_user() -> None:
    state = _RuntimeState()
    response_id = "caresp_shared000000000000000000000000"
    user_a = _make_execution(response_id, user_id_key="user-A")
    user_b = _make_execution(response_id, user_id_key="user-B")

    await state.add(user_a)
    await state.add(user_b)

    assert await state.get(response_id, "user-A") is user_a
    assert await state.get(response_id, "user-B") is user_b
    assert await state.get(response_id) is None


@pytest.mark.asyncio
async def test_reserve_rejects_duplicate_live_id_only_within_user() -> None:
    state = _RuntimeState()
    response_id = "caresp_reserved0000000000000000000000"

    assert await state.reserve(response_id, "user-A") is True
    assert await state.reserve(response_id, "user-A") is False
    assert await state.reserve(response_id, "user-B") is True

    await state.release_reservation(response_id, "user-A")
    assert await state.reserve(response_id, "user-A") is True
    assert await state.reserve(response_id, "user-B") is False


@pytest.mark.asyncio
@pytest.mark.parametrize("guard", ["none", "reserved", "deleting", "retained", "draining", "deleted"])
async def test_recovered_admission_retires_only_exact_stale_record_after_all_guards(guard: str) -> None:
    state = _RuntimeState()
    assert await state.reserve("shared", "owner")
    stale = _make_execution("shared", user_id_key="owner", status="in_progress")
    stale.execution_task = asyncio.create_task(asyncio.sleep(0))
    await stale.execution_task
    await state.add(stale)
    other = _make_execution("shared", user_id_key="other")
    await state.add(other)
    if guard != "reserved":
        await state.release_reservation("shared", "owner")
    if guard in {"deleting", "retained"}:
        assert await state.begin_deletion("shared", "owner")
        if guard == "retained":
            assert await state.retain_for_deletion(stale)
            await state.end_deletion("shared", "owner")
    elif guard == "draining":
        await state.begin_draining()
    elif guard == "deleted":
        await state.mark_deleted("shared", "owner")
    assert await state.reserve("shared", "owner", recovery=True) is (guard == "none")
    assert await state.get("shared", "owner") is (None if guard == "none" else stale)
    assert await state.get("shared", "other") is other
    if guard == "none":
        assert not await state.begin_deletion("shared", "owner")
        replacement = _make_execution("shared", user_id_key="owner", status="completed")
        await state.add(replacement)
        await state.release_reservation("shared", "owner")
        assert await state.get("shared", "owner") is replacement


@pytest.mark.asyncio
@pytest.mark.parametrize("status", ["in_progress", "completed"])
async def test_recovered_admission_never_removes_a_newer_live_or_terminal_record(status: str) -> None:
    state = _RuntimeState()
    stale = _make_execution("shared", user_id_key="owner", status="in_progress")
    stale.execution_task = asyncio.create_task(asyncio.sleep(0))
    await stale.execution_task
    await state.add(stale)
    current = _make_execution("shared", user_id_key="owner", status=status)
    assert await state.add(current, expected_record=stale)
    assert not await state.reserve("shared", "owner", recovery=True, incarnation_id="b" * 32)
    assert await state.get("shared", "owner") is current


@pytest.mark.asyncio
async def test_deletion_reservation_blocks_eviction_and_admission_until_cleanup():
    state = _RuntimeState()
    record = _make_execution("shared", user_id_key="owner", status="completed")
    assert await state.reserve("shared", "owner")
    await state.add(record)
    assert await state.begin_deletion("shared", "owner")
    assert not await state.try_evict("shared", "owner")
    await state.release_reservation("shared", "owner")
    assert not await state.reserve("shared", "owner")
    assert not await state.begin_deletion("shared", "owner")
    assert await state.reserve("shared", "other")
    await state.end_deletion("shared", "owner")
    assert await state.try_evict("shared", "owner")
    assert await state.reserve("shared", "owner")


@pytest.mark.asyncio
async def test_deletion_cannot_enter_during_unpublished_create():
    state = _RuntimeState()
    assert await state.reserve("shared", "owner")
    assert not await state.begin_deletion("shared", "owner")
    await state.release_reservation("shared", "owner")
    assert await state.begin_deletion("shared", "owner")
    await state.end_deletion("shared", "owner")


@pytest.mark.asyncio
async def test_compare_delete_does_not_remove_a_replacement_record():
    state = _RuntimeState()
    old = _make_execution("shared", user_id_key="owner", status="completed")
    replacement = _make_execution("shared", user_id_key="owner")
    await state.add(old)
    assert await state.add(replacement, expected_record=old)
    assert not await state.delete("shared", "owner", expected_record=old)
    assert await state.get("shared", "owner") is replacement
    assert not await state.is_deleted("shared", "owner")


@pytest.mark.asyncio
@pytest.mark.parametrize("retained", [False, True])
@pytest.mark.parametrize("marked_deleted", [False, True])
async def test_publication_cannot_replace_scoped_deletion_ownership_or_clear_its_marker(
    retained: bool, marked_deleted: bool
) -> None:
    state = _RuntimeState()
    owner = _make_execution("shared", user_id_key="owner", status="completed")
    foreign = _make_execution("shared", user_id_key="other", status="completed")
    assert await state.reserve("shared", "owner")
    assert await state.add(owner)
    assert await state.add(foreign)
    assert await state.begin_deletion("shared", "owner")
    if retained:
        assert await state.retain_for_deletion(owner)
        await state.end_deletion("shared", "owner")
    if marked_deleted:
        await state.mark_deleted("shared", "owner")
    replacement = _make_execution("shared", user_id_key="owner", status="in_progress")
    assert not await state.add(replacement, expected_record=owner)
    assert not await state.add(owner)
    assert not await state.add_pending(replacement)
    assert await state.get("shared", "owner") is owner
    assert await state.get("shared", "other") is foreign
    assert await state.is_deleted("shared", "owner") is marked_deleted
    assert not await state.try_evict("shared", "owner")


@pytest.mark.asyncio
async def test_completed_delete_revokes_old_publication_and_fresh_admission_binds_exact_context() -> None:
    state = _RuntimeState()
    old = _make_execution("shared", user_id_key="owner", status="completed")
    old.response_context = ResponseContext(response_id="shared", mode_flags=old.mode_flags)
    assert await state.reserve("shared", "owner", publication_context=old.response_context)
    assert await state.add(old)
    assert await state.begin_deletion("shared", "owner")
    assert await state.retain_for_deletion(old)
    assert await state.delete("shared", "owner", expected_record=old)
    await state.end_deletion("shared", "owner")
    assert not await state.add(old)
    assert not await state.reserve("shared", "owner")
    assert await state.is_deleted("shared", "owner")
    await state.release_reservation("shared", "owner")
    fresh = _make_execution("shared", user_id_key="owner", status="completed")
    fresh.response_context = ResponseContext(response_id="shared", mode_flags=fresh.mode_flags)
    assert await state.reserve("shared", "owner", publication_context=fresh.response_context)
    assert not await state.add(old)
    assert await state.is_deleted("shared", "owner")
    assert await state.add_pending(fresh)
    assert not await state.add(old)
    assert state._pending_records[("owner", "shared")] is fresh
    assert await state.add(fresh)
    assert not await state.is_deleted("shared", "owner")
    assert not await state.add(old, expected_record=fresh)
    assert not await state.try_evict("shared", "owner", expected_record=old)
    assert await state.get("shared", "owner") is fresh
    await state.release_reservation("shared", "owner")
    assert state._publication_contexts == {}
    assert not await state.add(old)
    assert await state.try_evict("shared", "owner", expected_record=fresh)


@pytest.mark.asyncio
async def test_publication_replaces_only_an_exact_contextless_predecessor() -> None:
    state = _RuntimeState()
    old = _make_execution("shared", status="completed")
    replacement = _make_execution("shared", status="completed")
    assert await state.add(old)
    assert not await state.add(replacement)
    assert await state.add(replacement, expected_record=old)
    assert not await state.add(old, expected_record=old)
    assert await state.get("shared") is replacement


def test_anonymous_user_isolation_is_not_a_wildcard() -> None:
    assert _RuntimeState.check_user_isolation(None, None) is True
    assert _RuntimeState.check_user_isolation(None, "user-A") is False


@pytest.mark.asyncio
async def test_reservation_survives_publication_and_eviction_until_request_cleanup():
    state = _RuntimeState()
    record = _make_execution("shared", user_id_key="user-A", status="completed")
    assert await state.reserve("shared", "user-A")
    assert await state.add_pending(record)
    await state.add(record)
    assert await state.try_evict("shared", "user-A")
    assert not await state.reserve("shared", "user-A")
    assert await state.reserve("shared", "user-B")
    await state.release_reservation("shared", "user-A")
    assert await state.reserve("shared", "user-A")
    assert not await state.reserve("shared", "user-B")


# ---------------------------------------------------------------------------
# T3 – delete marks deleted; get returns None; is_deleted returns True
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
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


@pytest.mark.asyncio
async def test_delete_nonexistent_returns_false() -> None:
    state = _RuntimeState()
    assert await state.delete("nonexistent_id") is False


# ---------------------------------------------------------------------------
# T5 – get_input_items single execution (no chain)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_input_items_single() -> None:
    state = _RuntimeState()
    items = [{"id": "item_1", "type": "message"}]
    execution = _make_execution(
        "caresp_ccc0000000000000000000000000000",
        input_items=items,
        previous_response_id=None,
        status="completed",
    )
    await state.add(execution)

    result = await state.get_input_items("caresp_ccc0000000000000000000000000000")
    assert result == items


# ---------------------------------------------------------------------------
# T6 – get_input_items chain walk (parent items come first)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_input_items_chain_walk() -> None:
    state = _RuntimeState()
    parent_id = "caresp_parent000000000000000000000000"
    child_id = "caresp_child0000000000000000000000000"

    parent = _make_execution(parent_id, input_items=[{"id": "a"}], status="completed")
    child = _make_execution(child_id, input_items=[{"id": "b"}], previous_response_id=parent_id, status="completed")

    await state.add(parent)
    await state.add(child)

    result = await state.get_input_items(child_id)
    ids = [item["id"] for item in result]
    assert ids == ["a", "b"]


# ---------------------------------------------------------------------------
# T7 – get_input_items on deleted response raises ValueError
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
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
    execution.response = cast(
        ResponseObject,
        {
            "id": rid,
            "response_id": rid,
            "agent_reference": {"name": "test-agent"},
            "object": "response",
            "status": "completed",
            "output": [],
        },
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
    execution.response = cast(ResponseObject, {"id": rid, "status": "completed", "output": []})

    snapshot = _RuntimeState.to_snapshot(execution)

    assert snapshot["status"] == "in_progress"


# ---------------------------------------------------------------------------
# Extra: to_snapshot injects id/response_id defaults when missing from response
# ---------------------------------------------------------------------------


def test_to_snapshot_injects_defaults_when_response_missing_ids() -> None:
    rid = "caresp_hhh0000000000000000000000000000"
    execution = _make_execution(rid, status="completed")
    # Response without id/response_id
    execution.response = cast(ResponseObject, {"status": "completed", "output": []})

    snapshot = _RuntimeState.to_snapshot(execution)

    assert snapshot["id"] == rid
    assert snapshot["response_id"] == rid
    assert snapshot["object"] == "response"


# ---------------------------------------------------------------------------
# Extra: list_records returns all stored executions
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
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


@pytest.mark.asyncio
async def test_begin_draining_rejects_new_pending_work() -> None:
    state = _RuntimeState()
    accepted = _make_execution("caresp_pending00000000000000000000000")
    rejected = _make_execution("caresp_rejected0000000000000000000000")

    assert await state.add_pending(accepted) is True
    records = await state.begin_draining()
    assert records == [accepted]
    assert await state.add_pending(rejected) is False
    assert await state.list_records() == [accepted]


# ---------------------------------------------------------------------------
# T1 (Task 7.1) – _ExecutionRecord is no longer exported from _runtime_state
# ---------------------------------------------------------------------------


def test_import_does_not_expose_execution_record() -> None:
    """_ExecutionRecord was deleted in Task 7.1; the module must not export it."""
    import importlib

    mod = importlib.import_module("azure.ai.agentserver.responses.hosting._runtime_state")
    assert not hasattr(
        mod, "_ExecutionRecord"
    ), "_ExecutionRecord should have been removed from _runtime_state in Phase 7 / Task 7.1"


def test_to_snapshot_agent_reference_is_json_safe() -> None:
    """Status-only snapshot must coerce an AgentReference model to a JSON-safe dict.

    Regression: a steered/in-progress turn polled via GET hit the status-only
    fallback snapshot, which deep-copied the gateway-injected ``AgentReference``
    model straight into a ``JSONResponse`` — raising ``TypeError: Object of type
    AgentReference is not JSON serializable``.
    """
    import json

    from azure.ai.agentserver.responses.models import AgentReference

    record = ResponseExecution(
        response_id="caresp_agentref0000000000000000000000",
        mode_flags=ResponseModeFlags(stream=False, background=True, store=True),
        status="in_progress",
        initial_agent_reference=AgentReference(name="my-agent", version="3"),
    )
    snapshot = _RuntimeState.to_snapshot(record)
    # Must be JSON-serializable (no leaked model) ...
    json.dumps(snapshot)
    # ... and preserve the reference fields as a plain dict.
    assert isinstance(snapshot["agent_reference"], dict)
    assert snapshot["agent_reference"].get("name") == "my-agent"
    assert snapshot["agent_reference"].get("version") == "3"
