# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""CRUD tests for InMemoryResponseProvider.

Covers create, read, update, delete of response envelopes,
output item storage, history resolution via previous_response_id
and conversation_id, and defensive-copy isolation.
"""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from azure.ai.agentserver.responses.models import _generated as generated_models
from azure.ai.agentserver.responses.store._memory import InMemoryResponseProvider

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _response(
    response_id: str,
    *,
    status: str = "completed",
    output: list[dict[str, Any]] | None = None,
    conversation_id: str | None = None,
) -> generated_models.ResponseObject:
    payload: dict[str, Any] = {
        "id": response_id,
        "object": "response",
        "output": output or [],
        "store": True,
        "status": status,
    }
    if conversation_id is not None:
        payload["conversation"] = {"id": conversation_id}
    return generated_models.ResponseObject(payload)


def _input_item(item_id: str, text: str) -> dict[str, Any]:
    return {
        "id": item_id,
        "type": "message",
        "role": "user",
        "content": [{"type": "input_text", "text": text}],
    }


def _output_message(item_id: str, text: str) -> dict[str, Any]:
    return {
        "id": item_id,
        "type": "output_message",
        "role": "assistant",
        "status": "completed",
        "content": [{"type": "output_text", "text": text}],
    }


# ===========================================================================
# Create
# ===========================================================================


def test_create__stores_response_envelope() -> None:
    provider = InMemoryResponseProvider()
    asyncio.run(provider.create_response(_response("resp_1"), None, None))

    result = asyncio.run(provider.get_response("resp_1"))
    assert str(getattr(result, "id")) == "resp_1"


def test_create__duplicate_raises_value_error() -> None:
    provider = InMemoryResponseProvider()
    asyncio.run(provider.create_response(_response("resp_dup"), None, None))

    with pytest.raises(ValueError, match="already exists"):
        asyncio.run(provider.create_response(_response("resp_dup"), None, None))


def test_create__stores_input_items_in_item_store() -> None:
    provider = InMemoryResponseProvider()
    items = [_input_item("in_1", "hello"), _input_item("in_2", "world")]
    asyncio.run(provider.create_response(_response("resp_in"), items, None))

    fetched = asyncio.run(provider.get_items(["in_1", "in_2"]))
    assert len(fetched) == 2
    assert fetched[0]["id"] == "in_1"
    assert fetched[1]["id"] == "in_2"


def test_create__stores_output_items_in_item_store() -> None:
    provider = InMemoryResponseProvider()
    resp = _response(
        "resp_out",
        output=[_output_message("out_1", "hi"), _output_message("out_2", "there")],
    )
    asyncio.run(provider.create_response(resp, None, None))

    fetched = asyncio.run(provider.get_items(["out_1", "out_2"]))
    assert len(fetched) == 2
    assert fetched[0]["id"] == "out_1"
    assert fetched[1]["id"] == "out_2"


def test_create__returns_defensive_copy() -> None:
    """Mutating the returned response must not affect the stored copy."""
    provider = InMemoryResponseProvider()
    asyncio.run(provider.create_response(_response("resp_copy"), None, None))

    r1 = asyncio.run(provider.get_response("resp_copy"))
    r1["status"] = "failed"

    r2 = asyncio.run(provider.get_response("resp_copy"))
    assert str(getattr(r2, "status")) == "completed"


# ===========================================================================
# Read (get)
# ===========================================================================


def test_get__raises_key_error_for_missing() -> None:
    provider = InMemoryResponseProvider()
    with pytest.raises(KeyError, match="not found"):
        asyncio.run(provider.get_response("nonexistent"))


def test_get__raises_key_error_for_deleted() -> None:
    provider = InMemoryResponseProvider()
    asyncio.run(provider.create_response(_response("resp_del"), None, None))
    asyncio.run(provider.delete_response("resp_del"))

    with pytest.raises(KeyError, match="not found"):
        asyncio.run(provider.get_response("resp_del"))


def test_get_items__missing_ids_return_none() -> None:
    provider = InMemoryResponseProvider()
    result = asyncio.run(provider.get_items(["no_such_item"]))
    assert result == [None]


# ===========================================================================
# Update
# ===========================================================================


def test_update__replaces_envelope() -> None:
    provider = InMemoryResponseProvider()
    asyncio.run(provider.create_response(_response("resp_upd", status="in_progress"), None, None))

    updated = _response("resp_upd", status="completed")
    asyncio.run(provider.update_response(updated))

    result = asyncio.run(provider.get_response("resp_upd"))
    assert str(getattr(result, "status")) == "completed"


def test_update__stores_new_output_items() -> None:
    """Updating a response with new output items must index them in the item store."""
    provider = InMemoryResponseProvider()
    asyncio.run(provider.create_response(_response("resp_upd2", status="in_progress"), None, None))

    updated = _response(
        "resp_upd2",
        status="completed",
        output=[_output_message("out_upd_1", "answer")],
    )
    asyncio.run(provider.update_response(updated))

    fetched = asyncio.run(provider.get_items(["out_upd_1"]))
    assert fetched[0] is not None
    assert fetched[0]["id"] == "out_upd_1"


def test_update__raises_key_error_for_missing() -> None:
    provider = InMemoryResponseProvider()
    with pytest.raises(KeyError, match="not found"):
        asyncio.run(provider.update_response(_response("ghost")))


def test_update__raises_key_error_for_deleted() -> None:
    provider = InMemoryResponseProvider()
    asyncio.run(provider.create_response(_response("resp_d"), None, None))
    asyncio.run(provider.delete_response("resp_d"))

    with pytest.raises(KeyError, match="not found"):
        asyncio.run(provider.update_response(_response("resp_d")))


# ===========================================================================
# Delete
# ===========================================================================


def test_delete__marks_entry_as_deleted() -> None:
    provider = InMemoryResponseProvider()
    asyncio.run(provider.create_response(_response("resp_del2"), None, None))
    asyncio.run(provider.delete_response("resp_del2"))

    with pytest.raises(KeyError):
        asyncio.run(provider.get_response("resp_del2"))


def test_delete__raises_key_error_for_missing() -> None:
    provider = InMemoryResponseProvider()
    with pytest.raises(KeyError, match="not found"):
        asyncio.run(provider.delete_response("nonexistent"))


def test_delete__double_delete_raises() -> None:
    provider = InMemoryResponseProvider()
    asyncio.run(provider.create_response(_response("resp_dd"), None, None))
    asyncio.run(provider.delete_response("resp_dd"))

    with pytest.raises(KeyError, match="not found"):
        asyncio.run(provider.delete_response("resp_dd"))


# ===========================================================================
# History resolution — previous_response_id path
# ===========================================================================


def test_history__previous_response_returns_input_and_output_ids() -> None:
    """get_history_item_ids via previous_response_id must include
    history + input + output item IDs from the previous response."""
    provider = InMemoryResponseProvider()
    resp = _response(
        "resp_prev",
        output=[_output_message("out_h1", "reply")],
    )
    asyncio.run(
        provider.create_response(
            resp,
            [_input_item("in_h1", "question")],
            history_item_ids=None,
        )
    )

    ids = asyncio.run(provider.get_history_item_ids("resp_prev", None, 100))
    assert "in_h1" in ids
    assert "out_h1" in ids


def test_history__previous_response_chains_history_ids() -> None:
    """History chain: resp_1 (with input) → resp_2 (previous_response_id=resp_1)
    should yield resp_1's history + input + output when queried from resp_2."""
    provider = InMemoryResponseProvider()
    resp1 = _response(
        "resp_chain1",
        output=[_output_message("out_c1", "first reply")],
    )
    asyncio.run(
        provider.create_response(
            resp1,
            [_input_item("in_c1", "first question")],
            history_item_ids=None,
        )
    )

    # Build resp_2 with history referencing resp_1's items
    history_from_1 = asyncio.run(provider.get_history_item_ids("resp_chain1", None, 100))
    resp2 = _response(
        "resp_chain2",
        output=[_output_message("out_c2", "second reply")],
    )
    asyncio.run(
        provider.create_response(
            resp2,
            [_input_item("in_c2", "second question")],
            history_item_ids=history_from_1,
        )
    )

    # Now query history from resp_2's perspective
    ids = asyncio.run(provider.get_history_item_ids("resp_chain2", None, 100))
    # Should include: history (in_c1, out_c1) + input (in_c2) + output (out_c2)
    assert "in_c1" in ids
    assert "out_c1" in ids
    assert "in_c2" in ids
    assert "out_c2" in ids


def test_history__items_resolvable_after_chain() -> None:
    """Full round-trip: create resp_1, then resp_2 referencing resp_1, and
    verify all history items are resolvable via get_items."""
    provider = InMemoryResponseProvider()
    resp1 = _response(
        "resp_rt1",
        output=[_output_message("out_rt1", "answer one")],
    )
    asyncio.run(
        provider.create_response(
            resp1,
            [_input_item("in_rt1", "question one")],
            history_item_ids=None,
        )
    )

    history_ids = asyncio.run(provider.get_history_item_ids("resp_rt1", None, 100))
    resp2 = _response("resp_rt2", output=[_output_message("out_rt2", "answer two")])
    asyncio.run(
        provider.create_response(
            resp2,
            [_input_item("in_rt2", "question two")],
            history_item_ids=history_ids,
        )
    )

    all_ids = asyncio.run(provider.get_history_item_ids("resp_rt2", None, 100))
    items = asyncio.run(provider.get_items(all_ids))
    assert all(item is not None for item in items), f"Some history items not found: {all_ids}"
    resolved_ids = [item["id"] for item in items]
    assert "in_rt1" in resolved_ids
    assert "out_rt1" in resolved_ids
    assert "in_rt2" in resolved_ids
    assert "out_rt2" in resolved_ids


def test_history__deleted_response_excluded() -> None:
    provider = InMemoryResponseProvider()
    asyncio.run(
        provider.create_response(
            _response("resp_hist_del", output=[_output_message("out_hist_del", "msg")]),
            [_input_item("in_hist_del", "q")],
            None,
        )
    )
    asyncio.run(provider.delete_response("resp_hist_del"))

    ids = asyncio.run(provider.get_history_item_ids("resp_hist_del", None, 100))
    assert ids == []


def test_history__respects_limit() -> None:
    provider = InMemoryResponseProvider()
    many_inputs = [_input_item(f"in_lim_{i}", f"msg {i}") for i in range(10)]
    asyncio.run(provider.create_response(_response("resp_lim"), many_inputs, None))

    ids = asyncio.run(provider.get_history_item_ids("resp_lim", None, 3))
    assert len(ids) == 3


def test_history__zero_limit_returns_empty() -> None:
    provider = InMemoryResponseProvider()
    asyncio.run(
        provider.create_response(
            _response("resp_z"),
            [_input_item("in_z", "q")],
            None,
        )
    )

    ids = asyncio.run(provider.get_history_item_ids("resp_z", None, 0))
    assert ids == []


# ===========================================================================
# History resolution — conversation_id path
# ===========================================================================


def test_history__conversation_id_collects_across_responses() -> None:
    """All input + output item IDs from responses in a conversation should be returned."""
    provider = InMemoryResponseProvider()

    resp1 = _response(
        "resp_cv1",
        conversation_id="conv_1",
        output=[_output_message("out_cv1", "reply 1")],
    )
    asyncio.run(
        provider.create_response(
            resp1,
            [_input_item("in_cv1", "q1")],
            None,
        )
    )

    resp2 = _response(
        "resp_cv2",
        conversation_id="conv_1",
        output=[_output_message("out_cv2", "reply 2")],
    )
    asyncio.run(
        provider.create_response(
            resp2,
            [_input_item("in_cv2", "q2")],
            None,
        )
    )

    ids = asyncio.run(provider.get_history_item_ids(None, "conv_1", 100))
    assert "in_cv1" in ids
    assert "out_cv1" in ids
    assert "in_cv2" in ids
    assert "out_cv2" in ids


def test_history__conversation_excludes_deleted_responses() -> None:
    provider = InMemoryResponseProvider()

    asyncio.run(
        provider.create_response(
            _response("resp_cvd1", conversation_id="conv_d"),
            [_input_item("in_cvd1", "q1")],
            None,
        )
    )
    asyncio.run(
        provider.create_response(
            _response("resp_cvd2", conversation_id="conv_d"),
            [_input_item("in_cvd2", "q2")],
            None,
        )
    )
    asyncio.run(provider.delete_response("resp_cvd1"))

    ids = asyncio.run(provider.get_history_item_ids(None, "conv_d", 100))
    assert "in_cvd1" not in ids
    assert "in_cvd2" in ids


def test_history__no_previous_no_conversation_returns_empty() -> None:
    provider = InMemoryResponseProvider()
    ids = asyncio.run(provider.get_history_item_ids(None, None, 100))
    assert ids == []


# ===========================================================================
# Output items updated on update_response
# ===========================================================================


def test_update__output_items_reflected_in_history() -> None:
    """After updating a response with new output, history resolution should
    include the updated output item IDs."""
    provider = InMemoryResponseProvider()
    asyncio.run(
        provider.create_response(
            _response("resp_uo", status="in_progress"),
            [_input_item("in_uo", "question")],
            None,
        )
    )

    # Initially no output
    ids_before = asyncio.run(provider.get_history_item_ids("resp_uo", None, 100))
    assert "out_uo" not in ids_before

    # Update adds output
    updated = _response(
        "resp_uo",
        status="completed",
        output=[_output_message("out_uo", "answer")],
    )
    asyncio.run(provider.update_response(updated))

    ids_after = asyncio.run(provider.get_history_item_ids("resp_uo", None, 100))
    assert "in_uo" in ids_after
    assert "out_uo" in ids_after
