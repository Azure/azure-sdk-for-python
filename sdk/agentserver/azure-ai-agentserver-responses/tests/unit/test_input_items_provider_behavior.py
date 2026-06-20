# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for input-items provider paging and error semantics."""

from __future__ import annotations

import asyncio

import pytest

from azure.ai.agentserver.responses.models import _generated as generated_models
from azure.ai.agentserver.responses.store._memory import InMemoryResponseProvider


def _response(response_id: str, *, store: bool = True) -> generated_models.ResponseObject:
    return generated_models.ResponseObject(
        {
            "id": response_id,
            "object": "response",
            "output": [],
            "store": store,
            "status": "completed",
        }
    )


def _item(item_id: str, text: str) -> dict[str, object]:
    return {
        "id": item_id,
        "type": "message",
        "role": "user",
        "content": [{"type": "input_text", "text": text}],
    }


def _ids(items: list[object]) -> list[str]:
    result: list[str] = []
    for item in items:
        if isinstance(item, dict):
            item_id = item.get("id")
            if isinstance(item_id, str):
                result.append(item_id)
    return result


def test_provider_input_items__supports_after_before_combination() -> None:
    provider = InMemoryResponseProvider()

    asyncio.run(
        provider.create_response(
            _response("resp_combo"),
            [
                _item("msg_001", "one"),
                _item("msg_002", "two"),
                _item("msg_003", "three"),
                _item("msg_004", "four"),
                _item("msg_005", "five"),
            ],
            history_item_ids=None,
        )
    )

    items = asyncio.run(
        provider.get_input_items(
            "resp_combo",
            ascending=True,
            after="msg_002",
            before="msg_005",
        )
    )

    assert _ids(items) == ["msg_003", "msg_004"]


def test_provider_input_items__returns_empty_page_after_last_cursor() -> None:
    provider = InMemoryResponseProvider()

    asyncio.run(
        provider.create_response(
            _response("resp_empty"),
            [
                _item("msg_001", "one"),
                _item("msg_002", "two"),
            ],
            history_item_ids=None,
        )
    )

    items = asyncio.run(provider.get_input_items("resp_empty", ascending=True, after="msg_002"))

    assert items == []


def test_provider_input_items__returns_history_only_items_when_current_input_is_empty() -> None:
    provider = InMemoryResponseProvider()

    asyncio.run(
        provider.create_response(
            _response("resp_base"),
            [
                _item("msg_hist_001", "history-1"),
                _item("msg_hist_002", "history-2"),
            ],
            history_item_ids=None,
        )
    )

    asyncio.run(
        provider.create_response(
            _response("resp_history_only"),
            [],
            history_item_ids=["msg_hist_001", "msg_hist_002"],
        )
    )

    items = asyncio.run(provider.get_input_items("resp_history_only", ascending=True))

    assert _ids(items) == ["msg_hist_001", "msg_hist_002"]


def test_provider_input_items__returns_current_only_items_when_no_history() -> None:
    provider = InMemoryResponseProvider()

    asyncio.run(
        provider.create_response(
            _response("resp_current_only"),
            [
                _item("msg_curr_001", "current-1"),
                _item("msg_curr_002", "current-2"),
            ],
            history_item_ids=None,
        )
    )

    items = asyncio.run(provider.get_input_items("resp_current_only", ascending=True))

    assert _ids(items) == ["msg_curr_001", "msg_curr_002"]


def test_provider_input_items__respects_limit_boundaries_1_and_100() -> None:
    provider = InMemoryResponseProvider()

    asyncio.run(
        provider.create_response(
            _response("resp_limits"),
            [_item(f"msg_{index:03d}", f"item-{index:03d}") for index in range(1, 151)],
            history_item_ids=None,
        )
    )

    one_item = asyncio.run(provider.get_input_items("resp_limits", ascending=True, limit=1))
    hundred_items = asyncio.run(provider.get_input_items("resp_limits", ascending=True, limit=100))

    assert len(one_item) == 1
    assert _ids(one_item) == ["msg_001"]
    assert len(hundred_items) == 100
    assert _ids(hundred_items)[0] == "msg_001"
    assert _ids(hundred_items)[-1] == "msg_100"


def test_provider_input_items__raises_for_deleted_and_missing_response() -> None:
    provider = InMemoryResponseProvider()

    asyncio.run(
        provider.create_response(
            _response("resp_deleted"),
            [_item("msg_001", "one")],
            history_item_ids=None,
        )
    )

    asyncio.run(provider.delete_response("resp_deleted"))

    with pytest.raises(ValueError):
        asyncio.run(provider.get_input_items("resp_deleted"))

    with pytest.raises(KeyError):
        asyncio.run(provider.get_input_items("resp_missing"))
