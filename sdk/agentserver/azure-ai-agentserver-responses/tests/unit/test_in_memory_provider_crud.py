# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""CRUD tests for InMemoryResponseProvider.

Covers create, read, update, delete of response envelopes,
output item storage, history resolution via previous_response_id
and conversation_id, and defensive-copy platform context.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any, cast

import pytest

from azure.ai.agentserver.responses._response_context import PlatformContext, ResponseContext
from azure.ai.agentserver.responses.models import ResponseObject
from azure.ai.agentserver.responses.models.runtime import ResponseExecution, ResponseModeFlags, StreamEventRecord
from azure.ai.agentserver.responses.store import ResponseAlreadyExistsError
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
) -> ResponseObject:
    payload: dict[str, Any] = {
        "id": response_id,
        "object": "response",
        "output": output or [],
        "store": True,
        "status": status,
    }
    if conversation_id is not None:
        payload["conversation"] = {"id": conversation_id}
    return cast(ResponseObject, payload)


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


_USER_KEYS = ["user_A", "user_B", None, "", " ", " user_A "]


@pytest.mark.asyncio
@pytest.mark.parametrize("owner_key,other_key", [(a, b) for a in _USER_KEYS for b in _USER_KEYS if a != b])
async def test_partitions__foreign_response_and_items_are_missing(owner_key: str | None, other_key: str | None) -> None:
    provider = InMemoryResponseProvider()
    owner = PlatformContext(user_id_key=owner_key, call_id="shared-call")
    other = PlatformContext(user_id_key=other_key, call_id="shared-call")
    response = _response("owned", output=[_output_message("output", "private")], conversation_id="conversation")
    await provider.create_response(response, [_input_item("input", "private")], None, context=owner)

    for operation in (
        provider.get_response("owned", context=other),
        provider.update_response(_response("owned", status="failed"), context=other),
        provider.delete_response("owned", context=other),
        provider.get_input_items("owned", after="input", before="output", context=other),
    ):
        with pytest.raises(KeyError, match="not found"):
            await operation
    assert await provider.get_items(["input", "output"], context=other) == [None, None]
    assert await provider.get_history_item_ids("owned", None, 100, context=other) == []
    assert await provider.get_history_item_ids(None, "conversation", 100, context=other) == []
    assert await provider.get_response("owned", context=owner) == response


@pytest.mark.asyncio
async def test_partitions__colliding_response_item_and_conversation_ids() -> None:
    provider = InMemoryResponseProvider()
    contexts = [PlatformContext(user_id_key=key, call_id="create") for key in _USER_KEYS]
    for index, context in enumerate(contexts):
        await provider.create_response(
            _response("same", output=[_output_message("output", str(index))], conversation_id="same"),
            [_input_item("input", str(index))],
            None,
            context=context,
        )
        with pytest.raises(ResponseAlreadyExistsError):
            await provider.create_response(_response("same"), None, None, context=context)
        await provider.create_response(
            _response(f"next_{index}", conversation_id="same"),
            [_input_item(f"next_input_{index}", str(index))],
            await provider.get_history_item_ids("same", None, 100, context=context),
            context=context,
        )

    for index, context in enumerate(contexts):
        later = PlatformContext(user_id_key=context.user_id_key, call_id="different-call")
        items = await provider.get_items(["input", "output", "missing"], context=later)
        assert items == [_input_item("input", str(index)), _output_message("output", str(index)), None]
        history = await provider.get_history_item_ids(None, "same", 100, context=later)
        assert history == ["input", "output", "input", "output", f"next_input_{index}"]
        assert await provider.get_history_item_ids(f"next_{index}", None, 100, context=later) == [
            "input",
            "output",
            f"next_input_{index}",
        ]
        assert await provider.get_input_items(
            f"next_{index}", ascending=True, limit=1, after="input", context=later
        ) == [_output_message("output", str(index))]
        assert await provider.get_input_items(f"next_{index}", before="input", context=later) == [
            _input_item(f"next_input_{index}", str(index)),
            _output_message("output", str(index)),
        ]
        # An ID from another partition must behave like any other unknown cursor.
        foreign_cursor = f"next_input_{(index + 1) % len(contexts)}"
        assert await provider.get_input_items("same", after=foreign_cursor, context=later) == [
            _input_item("input", str(index))
        ]
        items[0]["content"][0]["text"] = "mutated"
        assert (await provider.get_items(["input"], context=later))[0] == _input_item("input", str(index))
        await provider.update_response(
            _response("same", output=[_output_message("output", f"updated_{index}")]), context=later
        )

    for index, context in enumerate(contexts):
        assert (await provider.get_items(["output"], context=context))[0] == _output_message(
            "output", f"updated_{index}"
        )

    await provider.delete_response("same", context=contexts[0])
    with pytest.raises(ValueError, match="deleted"):
        await provider.get_input_items("same", context=contexts[0])
    for context in contexts[1:]:
        assert (await provider.get_response("same", context=context))["id"] == "same"
        assert await provider.get_history_item_ids("same", None, 100, context=context) == ["input", "output"]


@pytest.mark.asyncio
async def test_partitions__missing_context_and_unkeyed_context_share_anonymous_crud() -> None:
    provider = InMemoryResponseProvider()
    unkeyed = PlatformContext(call_id="opaque")
    await provider.create_response(_response("anonymous"), [_input_item("input", "local")], None)
    assert (await provider.get_response("anonymous", context=unkeyed))["id"] == "anonymous"
    await provider.update_response(_response("anonymous", status="failed"), context=unkeyed)
    assert (await provider.get_response("anonymous"))["status"] == "failed"
    assert await provider.get_items(["input"], context=unkeyed) == [_input_item("input", "local")]
    assert await provider.get_input_items("anonymous", context=unkeyed) == [_input_item("input", "local")]
    assert await provider.get_history_item_ids("anonymous", None, 100, context=unkeyed) == ["input"]
    await provider.delete_response("anonymous", context=unkeyed)
    with pytest.raises(KeyError):
        await provider.get_response("anonymous")
    await provider.create_response(_response("anonymous"), None, None, context=unkeyed)
    assert (await provider.get_response("anonymous"))["id"] == "anonymous"


@pytest.mark.asyncio
@pytest.mark.parametrize("reader_key", ["user_A", "user_B", None])
@pytest.mark.parametrize("prefetched", [False, True])
async def test_partitions__response_context_resolves_only_owned_references(
    reader_key: str | None, prefetched: bool
) -> None:
    provider = InMemoryResponseProvider()
    owner = PlatformContext(user_id_key="user_A")
    item = _input_item("owned_item", "private")
    await provider.create_response(_response("owned", conversation_id="conversation"), [item], None, context=owner)
    reader = PlatformContext(user_id_key=reader_key, call_id="next-request")
    ctx = ResponseContext(
        response_id="next",
        mode_flags=ResponseModeFlags(stream=False, store=True, background=False),
        provider=provider,
        input_items=[{"type": "item_reference", "id": "owned_item"}],
        previous_response_id="owned",
        conversation_id="conversation",
        platform_context=reader,
        prefetched_history_ids=["owned_item"] if prefetched else None,
    )
    inputs = await ctx.get_input_items()
    history = await ctx.get_history()
    if reader_key == "user_A":
        assert len(inputs) == 1
        assert inputs[0]["content"] == item["content"]
        assert history and all(entry == item for entry in history)
    else:
        assert inputs == ()
        assert history == ()
    # Foreign history pointers supplied by a caller never resolve foreign payloads.
    await provider.create_response(_response("next"), None, ["owned_item"], context=reader)
    assert await provider.get_input_items("next", context=reader) == ([item] if reader_key == "user_A" else [])


@pytest.mark.asyncio
@pytest.mark.parametrize("other_key", ["user_B", None])
async def test_partitions__legacy_helpers_do_not_bypass_identity(other_key: str | None) -> None:
    provider = InMemoryResponseProvider()
    owner = PlatformContext(user_id_key="user_A")
    other = PlatformContext(user_id_key=other_key)
    execution = ResponseExecution(
        response_id="execution",
        mode_flags=ResponseModeFlags(stream=True, store=True, background=True),
    )
    await provider.create_execution(execution, context=owner)
    event = StreamEventRecord(sequence_number=0, event_type="response.created", payload={"owner": "A"})
    assert await provider.get_execution("execution", context=other) is None
    assert await provider.get_replay_events("execution", context=other) is None
    assert not await provider.set_response_snapshot("execution", _response("execution"), context=other)
    assert not await provider.transition_execution_status("execution", "in_progress", context=other)
    assert not await provider.set_cancel_requested("execution", context=other)
    assert not await provider.append_stream_event("execution", event, context=other)
    assert not await provider.delete("execution", context=other)
    assert await provider.append_stream_event("execution", event, context=owner)
    assert (await provider.get_replay_events("execution", context=owner))[0].payload == {"owner": "A"}
    assert (await provider.get_execution("execution", context=owner)).status == execution.status


@pytest.mark.asyncio
async def test_partitions__legacy_execution_replay_expiry_and_cleanup_collisions() -> None:
    provider = InMemoryResponseProvider()
    contexts = [PlatformContext(user_id_key="user_A"), PlatformContext(user_id_key="user_B"), None]
    execution = ResponseExecution(
        response_id="same",
        mode_flags=ResponseModeFlags(stream=True, store=True, background=True),
    )
    for index, context in enumerate(contexts):
        await provider.create_execution(execution, context=context)
        with pytest.raises(ValueError, match="already exists"):
            await provider.create_execution(execution, context=context)
        assert await provider.set_response_snapshot("same", _response("same", status="in_progress"), context=context)
        assert await provider.transition_execution_status("same", "in_progress", context=context)
        old_event = StreamEventRecord(
            sequence_number=0,
            event_type="response.created",
            payload={"owner": index},
            emitted_at=datetime.now(timezone.utc) - timedelta(seconds=601),
        )
        live_event = StreamEventRecord(
            sequence_number=1,
            event_type="response.in_progress",
            payload={"owner": index},
        )
        assert await provider.append_stream_event("same", old_event, context=context)
        assert await provider.append_stream_event("same", live_event, context=context)
        assert (await provider.get_execution("same", context=context)).status == "in_progress"
        replay = await provider.get_replay_events("same", context=context)
        assert len(replay) == 1
        assert replay[0].payload == {"owner": index}
        replay[0].payload["owner"] = "mutated"
        assert (await provider.get_replay_events("same", context=context))[0].payload == {"owner": index}

    # Legacy event bookkeeping shares the same composite keys as response entries.
    provider._stream_events[("user_A", "same")] = []
    provider._stream_events[("user_B", "same")] = []
    provider._stream_events[(None, "same")] = []
    provider._stream_events[("user_A", "orphan")] = []
    assert await provider.set_cancel_requested("same", ttl_seconds=10, context=contexts[0])
    assert (await provider.get_execution("same", context=contexts[0])).cancel_requested
    assert not (await provider.get_execution("same", context=contexts[1])).cancel_requested
    assert await provider.purge_expired(now=datetime.now(timezone.utc) + timedelta(seconds=11)) == 1
    assert await provider.get_execution("same", context=contexts[0]) is None
    assert ("user_A", "same") not in provider._stream_events
    assert ("user_A", "orphan") not in provider._stream_events
    for context in contexts[1:]:
        assert (await provider.get_execution("same", context=context)).status == "in_progress"
        assert len(await provider.get_replay_events("same", context=context)) == 1
    assert await provider.delete("same", context=contexts[1])
    assert ("user_B", "same") not in provider._stream_events
    assert (None, "same") in provider._stream_events
    assert await provider.get_execution("same") is not None
    # Exercise automatic purge on normal lookups, not only the explicit maintenance method.
    provider._entries[(None, "same")].expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    assert await provider.get_execution("same") is None
    assert provider._stream_events == {}


@pytest.mark.asyncio
async def test_partitions__expired_response_leaves_other_users_history_intact() -> None:
    provider = InMemoryResponseProvider()
    contexts = [PlatformContext(user_id_key="user_A"), PlatformContext(user_id_key="user_B"), None]
    for context in contexts:
        await provider.create_response(
            _response("same", conversation_id="conversation"), [_input_item("input", "text")], None, context=context
        )
    assert await provider.set_response_snapshot("same", _response("same"), ttl_seconds=10, context=contexts[0])
    assert await provider.purge_expired(now=datetime.now(timezone.utc) + timedelta(seconds=11)) == 1
    with pytest.raises(KeyError):
        await provider.get_response("same", context=contexts[0])
    assert await provider.get_history_item_ids(None, "conversation", 100, context=contexts[0]) == []
    for context in contexts[1:]:
        assert await provider.get_history_item_ids(None, "conversation", 100, context=context) == ["input"]
        assert await provider.get_input_items("same", context=context) == [_input_item("input", "text")]


# ===========================================================================
# Create
# ===========================================================================


def test_create__stores_response_envelope() -> None:
    provider = InMemoryResponseProvider()
    asyncio.run(provider.create_response(_response("resp_1"), None, None))

    result = asyncio.run(provider.get_response("resp_1"))
    assert result["id"] == "resp_1"


def test_create__duplicate_raises_response_already_exists() -> None:
    from azure.ai.agentserver.responses.store import ResponseAlreadyExistsError

    provider = InMemoryResponseProvider()
    asyncio.run(provider.create_response(_response("resp_dup"), None, None))

    with pytest.raises(ResponseAlreadyExistsError) as exc_info:
        asyncio.run(provider.create_response(_response("resp_dup"), None, None))
    assert exc_info.value.response_id == "resp_dup"


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
    assert r2["status"] == "completed"


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


def test_append_stream_event__stores_replay_record() -> None:
    provider = InMemoryResponseProvider()
    future_saved_at = datetime.now(timezone.utc) + timedelta(days=365)
    asyncio.run(
        provider.create_response(
            _response("resp_stream"),
            None,
            None,
        )
    )
    event = StreamEventRecord(
        sequence_number=0,
        event_type="response.created",
        payload={"type": "response.created", "sequence_number": 0},
        emitted_at=future_saved_at,
    )

    appended = asyncio.run(provider.append_stream_event("resp_stream", event))
    stored = asyncio.run(provider.get_replay_events("resp_stream"))

    assert appended is True
    assert stored is not None
    assert stored[0].emitted_at == future_saved_at


# ===========================================================================
# Update
# ===========================================================================


def test_update__replaces_envelope() -> None:
    provider = InMemoryResponseProvider()
    asyncio.run(provider.create_response(_response("resp_upd", status="in_progress"), None, None))

    updated = _response("resp_upd", status="completed")
    asyncio.run(provider.update_response(updated))

    result = asyncio.run(provider.get_response("resp_upd"))
    assert result["status"] == "completed"


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
