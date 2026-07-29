# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Provider round-trip conformance for ``internal_metadata`` (spec 025 §7.5).

Asserts the item-level and response-level internal metadata survive every read
path of the in-tree providers (T28–T28d). The ``FoundryResponseProvider``
variant is exercised by the live test suite.
"""

from __future__ import annotations

import tempfile
from typing import Any, cast

import pytest

from azure.ai.agentserver.responses.models._generated import ResponseObject
from azure.ai.agentserver.responses.store._file import FileResponseStore
from azure.ai.agentserver.responses.store._memory import InMemoryResponseProvider


def _item(item_id: str) -> dict[str, Any]:
    return {
        "type": "message",
        "id": item_id,
        "role": "assistant",
        "content": [],
        "status": "completed",
        "internal_metadata": {"phase": "gather", "n": 7},
    }


def _response(resp_id: str, output: list) -> ResponseObject:
    return cast(
        ResponseObject,
        {
            "id": resp_id,
            "object": "response",
            "status": "completed",
            "output": output,
            "model": "m",
            "metadata": {"_internal_metadata": {"completed_phases": 3}},
        },
    )


def _make_providers():
    providers = [("memory", InMemoryResponseProvider())]
    tmp = tempfile.mkdtemp(prefix="resp_store_")
    providers.append(("file", FileResponseStore(tmp)))
    return providers


@pytest.mark.asyncio
@pytest.mark.parametrize("name,provider", _make_providers())
async def test_t28_t28a_response_output_item_internal_metadata_preserved(name, provider):
    item = _item("item_a")
    resp = _response("resp_a", [item])
    await provider.create_response(resp, [item], None)

    # T28 — create + get
    loaded = await provider.get_response("resp_a")
    assert loaded["output"][0]["internal_metadata"] == {"phase": "gather", "n": 7}

    # T28a — update + get
    resp["metadata"]["_internal_metadata"]["extra"] = "x"
    await provider.update_response(resp)
    loaded2 = await provider.get_response("resp_a")
    assert loaded2["output"][0]["internal_metadata"]["n"] == 7

    # T28d — response-level reserved key round-trips
    assert loaded2["metadata"]["_internal_metadata"] == {"completed_phases": 3, "extra": "x"}


@pytest.mark.asyncio
@pytest.mark.parametrize("name,provider", _make_providers())
async def test_t28b_t28c_get_items_typed_internal_metadata(name, provider):
    item = _item("item_b")
    resp = _response("resp_b", [item])
    await provider.create_response(resp, [item], None)

    # T28b — get_items returns dict-native OutputItem with internal_metadata key
    items = await provider.get_items(["item_b"])
    assert items[0] is not None
    assert items[0]["internal_metadata"] == {"phase": "gather", "n": 7}

    # T28c — get_input_items returns dict-native OutputItem with internal_metadata key
    input_items = await provider.get_input_items("resp_b")
    assert any(it.get("internal_metadata") == {"phase": "gather", "n": 7} for it in input_items)
