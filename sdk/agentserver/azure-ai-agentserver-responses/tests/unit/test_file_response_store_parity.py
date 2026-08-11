# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Drop-in parity tests for FileResponseStore vs InMemoryResponseProvider.

These tests assert that ``FileResponseStore`` exhibits the same observable
behaviour as ``InMemoryResponseProvider`` for the
:class:`ResponseProviderProtocol` surface: response envelope CRUD, items,
history walking (``previous_response_id`` + ``conversation_id``), and
soft-delete semantics.

The test harness parameterises the same scenario across both providers
and asserts identical results.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import pytest

from azure.ai.agentserver.responses.models import _generated as generated_models
from azure.ai.agentserver.responses.store._base import ResponseAlreadyExistsError
from azure.ai.agentserver.responses.store._file import FileResponseStore
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


def _input_item(item_id: str, text: str = "hello") -> dict[str, Any]:
    return {
        "id": item_id,
        "type": "message",
        "role": "user",
        "content": [{"type": "input_text", "text": text}],
    }


def _output_item(item_id: str, text: str = "world") -> dict[str, Any]:
    return {
        "id": item_id,
        "type": "message",
        "role": "assistant",
        "content": [{"type": "output_text", "text": text}],
    }


def _make_provider_factories(tmp_path: Path) -> list[tuple[str, Callable[[], Any]]]:
    """Return (label, factory) pairs covering both providers."""
    return [
        ("memory", lambda: InMemoryResponseProvider()),
        ("file", lambda: FileResponseStore(storage_dir=tmp_path / "store")),
    ]


# ---------------------------------------------------------------------------
# CRUD parity
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_get_roundtrip(tmp_path: Path) -> None:
    for label, factory in _make_provider_factories(tmp_path):
        provider = factory()
        await provider.create_response(_response("r1"), None, None)
        got = await provider.get_response("r1")
        assert str(got["id"]) == "r1", label


@pytest.mark.asyncio
async def test_create_raises_on_duplicate(tmp_path: Path) -> None:
    for label, factory in _make_provider_factories(tmp_path):
        provider = factory()
        await provider.create_response(_response("r1"), None, None)
        with pytest.raises(ResponseAlreadyExistsError):
            await provider.create_response(_response("r1"), None, None)
        # Type-stable across providers.
        assert label  # marker


@pytest.mark.asyncio
async def test_get_missing_raises_key_error(tmp_path: Path) -> None:
    for label, factory in _make_provider_factories(tmp_path):
        provider = factory()
        with pytest.raises(KeyError):
            await provider.get_response("nope")
        assert label


@pytest.mark.asyncio
async def test_update_existing(tmp_path: Path) -> None:
    for _label, factory in _make_provider_factories(tmp_path):
        provider = factory()
        await provider.create_response(_response("r1", status="in_progress"), None, None)
        await provider.update_response(_response("r1", status="completed"))
        got = await provider.get_response("r1")
        assert str(got["status"]) == "completed"


@pytest.mark.asyncio
async def test_update_missing_raises(tmp_path: Path) -> None:
    for _label, factory in _make_provider_factories(tmp_path):
        provider = factory()
        with pytest.raises(KeyError):
            await provider.update_response(_response("nope"))


@pytest.mark.asyncio
async def test_delete_soft_then_get_raises(tmp_path: Path) -> None:
    for _label, factory in _make_provider_factories(tmp_path):
        provider = factory()
        await provider.create_response(_response("r1"), None, None)
        await provider.delete_response("r1")
        with pytest.raises(KeyError):
            await provider.get_response("r1")
        # Re-create after soft-delete is allowed in both providers.
        await provider.create_response(_response("r1", status="completed"), None, None)
        got = await provider.get_response("r1")
        assert str(got["id"]) == "r1"


@pytest.mark.asyncio
async def test_delete_missing_raises(tmp_path: Path) -> None:
    for _label, factory in _make_provider_factories(tmp_path):
        provider = factory()
        with pytest.raises(KeyError):
            await provider.delete_response("nope")


# ---------------------------------------------------------------------------
# Items / history parity
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_items_round_trip(tmp_path: Path) -> None:
    for _label, factory in _make_provider_factories(tmp_path):
        provider = factory()
        items = [_input_item("i1", "a"), _input_item("i2", "b")]
        await provider.create_response(_response("r1"), items, None)
        # Round-trip via get_items in caller-supplied order.
        got = await provider.get_items(["i2", "i1", "nope"])
        assert got[0] is not None and got[0]["id"] == "i2"
        assert got[1] is not None and got[1]["id"] == "i1"
        assert got[2] is None


@pytest.mark.asyncio
async def test_get_input_items_combines_history_and_input(tmp_path: Path) -> None:
    for _label, factory in _make_provider_factories(tmp_path):
        provider = factory()
        # history_item_ids reference items persisted via a prior turn's response.
        await provider.create_response(
            _response("r_prev"),
            [_input_item("h1", "prior")],
            None,
        )
        await provider.create_response(
            _response("r1"),
            [_input_item("i1", "current")],
            history_item_ids=["h1"],
        )
        # Default: descending, default limit 20.
        listed = await provider.get_input_items("r1", limit=20, ascending=False)
        ids = [it["id"] for it in listed if it is not None]
        # Order: reversed(history + input) = ["i1", "h1"].
        assert ids == ["i1", "h1"]


@pytest.mark.asyncio
async def test_get_input_items_cursor_paging(tmp_path: Path) -> None:
    for _label, factory in _make_provider_factories(tmp_path):
        provider = factory()
        items = [_input_item(f"i{n}") for n in range(5)]
        await provider.create_response(_response("r1"), items, None)
        listed = await provider.get_input_items("r1", limit=3, ascending=True)
        assert [it["id"] for it in listed] == ["i0", "i1", "i2"]
        # After cursor.
        after_listed = await provider.get_input_items("r1", limit=3, ascending=True, after="i1")
        assert [it["id"] for it in after_listed] == ["i2", "i3", "i4"]


@pytest.mark.asyncio
async def test_get_input_items_missing_raises_key_error(tmp_path: Path) -> None:
    for _label, factory in _make_provider_factories(tmp_path):
        provider = factory()
        with pytest.raises(KeyError):
            await provider.get_input_items("nope")


@pytest.mark.asyncio
async def test_get_input_items_deleted_raises_value_error(tmp_path: Path) -> None:
    for _label, factory in _make_provider_factories(tmp_path):
        provider = factory()
        await provider.create_response(_response("r1"), [_input_item("i1")], None)
        await provider.delete_response("r1")
        with pytest.raises(ValueError):
            await provider.get_input_items("r1")


# ---------------------------------------------------------------------------
# History walking parity (previous_response_id + conversation_id)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_history_via_previous_response_id(tmp_path: Path) -> None:
    """previous_response_id contributes that response's history+input+output ids."""
    for _label, factory in _make_provider_factories(tmp_path):
        provider = factory()
        await provider.create_response(
            _response(
                "r_prev",
                output=[_output_item("out1"), _output_item("out2")],
            ),
            [_input_item("in1")],
            history_item_ids=["hist1"],
        )
        ids = await provider.get_history_item_ids("r_prev", None, limit=100)
        # Order: history + input + output.
        assert ids == ["hist1", "in1", "out1", "out2"]


@pytest.mark.asyncio
async def test_history_via_conversation_id(tmp_path: Path) -> None:
    """conversation_id contributes every member response's history+input+output ids."""
    for _label, factory in _make_provider_factories(tmp_path):
        provider = factory()
        await provider.create_response(
            _response(
                "rA",
                output=[_output_item("a_out")],
                conversation_id="conv-1",
            ),
            [_input_item("a_in")],
            None,
        )
        await provider.create_response(
            _response(
                "rB",
                output=[_output_item("b_out")],
                conversation_id="conv-1",
            ),
            [_input_item("b_in")],
            None,
        )
        ids = await provider.get_history_item_ids(None, "conv-1", limit=100)
        # Both responses' history+input+output ids, in insertion order.
        assert ids == ["a_in", "a_out", "b_in", "b_out"]


@pytest.mark.asyncio
async def test_history_combined_previous_and_conversation(tmp_path: Path) -> None:
    """Both previous_response_id and conversation_id contribute (concatenated)."""
    for _label, factory in _make_provider_factories(tmp_path):
        provider = factory()
        await provider.create_response(
            _response("r_prev", output=[_output_item("prev_out")]),
            [_input_item("prev_in")],
            None,
        )
        await provider.create_response(
            _response("rA", output=[_output_item("a_out")], conversation_id="conv-1"),
            [_input_item("a_in")],
            None,
        )
        ids = await provider.get_history_item_ids("r_prev", "conv-1", limit=100)
        # previous_response_id contributions first, then conversation members.
        assert ids == ["prev_in", "prev_out", "a_in", "a_out"]


@pytest.mark.asyncio
async def test_history_skips_deleted_responses(tmp_path: Path) -> None:
    """Deleted responses are skipped both via previous_response_id and conversation_id."""
    for _label, factory in _make_provider_factories(tmp_path):
        provider = factory()
        await provider.create_response(
            _response("rA", output=[_output_item("a_out")], conversation_id="conv-1"),
            [_input_item("a_in")],
            None,
        )
        await provider.create_response(
            _response("rB", output=[_output_item("b_out")], conversation_id="conv-1"),
            [_input_item("b_in")],
            None,
        )
        await provider.delete_response("rA")
        # Conversation walk skips the deleted rA.
        ids = await provider.get_history_item_ids(None, "conv-1", limit=100)
        assert ids == ["b_in", "b_out"]
        # previous_response_id pointing at a deleted response yields nothing.
        ids2 = await provider.get_history_item_ids("rA", None, limit=100)
        assert ids2 == []


@pytest.mark.asyncio
async def test_history_respects_limit(tmp_path: Path) -> None:
    for _label, factory in _make_provider_factories(tmp_path):
        provider = factory()
        await provider.create_response(
            _response(
                "r_prev",
                output=[_output_item("out1"), _output_item("out2"), _output_item("out3")],
            ),
            [_input_item("in1"), _input_item("in2")],
            history_item_ids=["hist1", "hist2"],
        )
        ids = await provider.get_history_item_ids("r_prev", None, limit=3)
        assert ids == ["hist1", "hist2", "in1"]
        # Non-positive limit returns empty.
        ids_zero = await provider.get_history_item_ids("r_prev", None, limit=0)
        assert ids_zero == []


@pytest.mark.asyncio
async def test_history_neither_arg_returns_empty(tmp_path: Path) -> None:
    for _label, factory in _make_provider_factories(tmp_path):
        provider = factory()
        ids = await provider.get_history_item_ids(None, None, limit=10)
        assert ids == []


@pytest.mark.asyncio
async def test_update_refreshes_output_index(tmp_path: Path) -> None:
    """update_response should reindex output items so history walks see them."""
    for _label, factory in _make_provider_factories(tmp_path):
        provider = factory()
        await provider.create_response(_response("r1"), None, None)
        # Update with output items present.
        await provider.update_response(_response("r1", output=[_output_item("out1")]))
        ids = await provider.get_history_item_ids("r1", None, limit=10)
        assert "out1" in ids
        got = await provider.get_items(["out1"])
        assert got[0] is not None and got[0]["id"] == "out1"
