# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""A failed response's own items must not be replayed as conversation history.

When a turn fails (for example because its input carried a
``function_call_output`` with no matching call), the input that made it fail
must not be resolved into the history of later turns in the same conversation
or of turns chained through ``previous_response_id``. Otherwise every later
request fails the same way. The failed response's items stay retrievable
through ``get_input_items`` for diagnostics.

The scenarios run against both ``InMemoryResponseProvider`` and
``FileResponseStore`` and assert identical results.
"""

from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import Any, Callable

import pytest

from azure.ai.agentserver.responses.models import _generated as generated_models
from azure.ai.agentserver.responses.store._file import FileResponseStore
from azure.ai.agentserver.responses.store._history import is_replayable_status
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
    return [
        ("memory", lambda: InMemoryResponseProvider()),
        ("file", lambda: FileResponseStore(storage_dir=tmp_path / "store")),
    ]


# ---------------------------------------------------------------------------
# Status rule
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "status,expected",
    [
        ("completed", True),
        ("incomplete", True),
        ("cancelled", True),
        ("in_progress", True),
        ("queued", True),
        (None, True),
        ("failed", False),
    ],
)
def test_is_replayable_status(status: str | None, expected: bool) -> None:
    assert is_replayable_status(status) is expected


class _Status(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"


def test_is_replayable_status_accepts_enum_members() -> None:
    """A provider may hand in an enum member; ``str(member)`` is not its value on Python 3.11+."""
    assert is_replayable_status(_Status.COMPLETED) is True
    assert is_replayable_status(_Status.FAILED) is False


@pytest.mark.asyncio
async def test_file_store_indexes_enum_status_as_its_value(tmp_path: Path) -> None:
    store = FileResponseStore(storage_dir=tmp_path / "store")
    await store.create_response(
        _response("r_failed", status=_Status.FAILED, conversation_id="conv-1"), [_input_item("bad_in")], None
    )
    indexes = json.loads(
        store._indexes_path("r_failed").read_text(encoding="utf-8")
    )  # pylint: disable=protected-access
    assert indexes["status"] == "failed"
    assert await store.get_history_item_ids(None, "conv-1", limit=100) == []


# ---------------------------------------------------------------------------
# Conversation scope
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_failed_turn_input_and_output_excluded_from_conversation_history(tmp_path: Path) -> None:
    """The failed turn's own items are skipped; earlier and later successful turns are kept in order."""
    for label, factory in _make_provider_factories(tmp_path):
        provider = factory()
        await provider.create_response(
            _response("r_ok_1", output=[_output_item("ok1_out")], conversation_id="conv-1"),
            [_input_item("ok1_in")],
            None,
        )
        # A turn whose input carried an unmatched function_call_output and failed.
        await provider.create_response(
            _response("r_failed", status="failed", output=[_output_item("bad_out")], conversation_id="conv-1"),
            [_input_item("bad_in"), _input_item("bad_call_output")],
            None,
        )
        await provider.create_response(
            _response("r_ok_2", output=[_output_item("ok2_out")], conversation_id="conv-1"),
            [_input_item("ok2_in")],
            None,
        )

        ids = await provider.get_history_item_ids(None, "conv-1", limit=100)
        assert ids == ["ok1_in", "ok1_out", "ok2_in", "ok2_out"], label


@pytest.mark.asyncio
async def test_response_that_fails_after_creation_is_excluded_on_update(tmp_path: Path) -> None:
    """The orchestrator persists the response before the terminal; a later ``failed`` update must take effect."""
    for label, factory in _make_provider_factories(tmp_path):
        provider = factory()
        await provider.create_response(
            _response("r_1", status="in_progress", conversation_id="conv-1"),
            [_input_item("in_1")],
            None,
        )
        # While in progress the input is part of the history.
        assert await provider.get_history_item_ids(None, "conv-1", limit=100) == ["in_1"], label

        await provider.update_response(_response("r_1", status="failed", conversation_id="conv-1"))
        assert await provider.get_history_item_ids(None, "conv-1", limit=100) == [], label

        # The stored response itself still reports the failure.
        stored = await provider.get_response("r_1")
        assert stored["status"] == "failed", label


@pytest.mark.asyncio
async def test_failed_response_input_items_remain_retrievable(tmp_path: Path) -> None:
    """Exclusion from replayable history does not delete the stored items (diagnostics)."""
    for label, factory in _make_provider_factories(tmp_path):
        provider = factory()
        await provider.create_response(
            _response("r_failed", status="failed", conversation_id="conv-1"),
            [_input_item("bad_in"), _input_item("bad_call_output")],
            history_item_ids=["hist_1"],
        )

        items = await provider.get_input_items("r_failed", limit=100, ascending=True)
        assert [item["id"] for item in items] == ["bad_in", "bad_call_output"], label
        assert await provider.get_history_item_ids(None, "conv-1", limit=100) == ["hist_1"], label


# ---------------------------------------------------------------------------
# previous_response_id scope
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_chaining_from_failed_response_keeps_only_inherited_history(tmp_path: Path) -> None:
    """``previous_response_id`` pointing at a failed response yields its inherited history only."""
    for label, factory in _make_provider_factories(tmp_path):
        provider = factory()
        await provider.create_response(
            _response("r_prev", output=[_output_item("prev_out")]),
            [_input_item("prev_in")],
            None,
        )
        chain = await provider.get_history_item_ids("r_prev", None, limit=100)
        assert chain == ["prev_in", "prev_out"], label

        await provider.create_response(
            _response("r_failed", status="failed", output=[_output_item("bad_out")]),
            [_input_item("bad_in")],
            history_item_ids=chain,
        )

        ids = await provider.get_history_item_ids("r_failed", None, limit=100)
        assert ids == ["prev_in", "prev_out"], label


@pytest.mark.asyncio
async def test_successful_chain_through_failed_response_stays_clean(tmp_path: Path) -> None:
    """A successful response chained after a failed one carries forward only clean history."""
    for label, factory in _make_provider_factories(tmp_path):
        provider = factory()
        await provider.create_response(
            _response("r_failed", status="failed"),
            [_input_item("bad_in")],
            history_item_ids=["hist_1"],
        )
        inherited = await provider.get_history_item_ids("r_failed", None, limit=100)
        assert inherited == ["hist_1"], label

        await provider.create_response(
            _response("r_next", output=[_output_item("next_out")]),
            [_input_item("next_in")],
            history_item_ids=inherited,
        )
        ids = await provider.get_history_item_ids("r_next", None, limit=100)
        assert ids == ["hist_1", "next_in", "next_out"], label


# ---------------------------------------------------------------------------
# Interaction with the history limit
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_failed_items_do_not_consume_history_limit(tmp_path: Path) -> None:
    """Exclusion happens before truncation, so failed items never displace replayable ones."""
    for label, factory in _make_provider_factories(tmp_path):
        provider = factory()
        await provider.create_response(
            _response("r_ok", output=[_output_item("ok_out")], conversation_id="conv-1"),
            [_input_item("ok_in")],
            None,
        )
        await provider.create_response(
            _response("r_failed", status="failed", conversation_id="conv-1"),
            [_input_item("bad_1"), _input_item("bad_2"), _input_item("bad_3")],
            None,
        )

        ids = await provider.get_history_item_ids(None, "conv-1", limit=2)
        assert ids == ["ok_in", "ok_out"], label


# ---------------------------------------------------------------------------
# File store: stores written before the status was indexed
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_file_store_reads_status_from_envelope_when_indexes_predate_it(tmp_path: Path) -> None:
    """Indexes written by older versions have no ``status``; the envelope decides instead."""
    store = FileResponseStore(storage_dir=tmp_path / "store")
    await store.create_response(
        _response("r_failed", status="failed", conversation_id="conv-1"),
        [_input_item("bad_in")],
        None,
    )
    await store.create_response(
        _response("r_ok", conversation_id="conv-1"),
        [_input_item("ok_in")],
        None,
    )

    # Simulate a pre-existing store by dropping the indexed status.
    for response_id in ("r_failed", "r_ok"):
        indexes_path = store._indexes_path(response_id)  # pylint: disable=protected-access
        indexes = json.loads(indexes_path.read_text(encoding="utf-8"))
        assert indexes.pop("status") is not None
        indexes_path.write_text(json.dumps(indexes), encoding="utf-8")

    assert await store.get_history_item_ids(None, "conv-1", limit=100) == ["ok_in"]
