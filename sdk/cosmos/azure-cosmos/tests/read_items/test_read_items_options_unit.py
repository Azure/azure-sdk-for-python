# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Customer options reach the typed Rust read-many request, without legacy transport."""

from copy import deepcopy
from unittest.mock import MagicMock

import pytest

from azure.cosmos._helpers._item_context import ItemClientDefaults
from ._helpers import make_proxy, page


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("level", ["Eventual", "ConsistentPrefix", "Session", "BoundedStaleness", "Strong"])
async def test_consistency_and_routing_options_reach_typed_request_rust(asynchronous, level):
    proxy, backend = make_proxy(asynchronous)
    options = {"sessionToken": "old", "initialHeaders": {"x-test": "yes"}}
    original = deepcopy(options)
    kwargs = dict(
        consistency_level=level, session_token="new", excluded_locations=["West US"],
        priority="High", throughput_bucket=2, request_options=options, max_item_count=1,
        availability_strategy=False, timeout=5,
    )
    result = proxy.read_items([("a", "p")], **kwargs)
    if asynchronous:
        await result
    prepared = backend.calls[0]
    assert prepared.op == "read_items" and prepared.query is None
    assert prepared.settings.consistency_level == level
    assert prepared.settings.session_token == "new"
    assert prepared.settings.excluded_locations == ("West US",)
    assert prepared.settings.priority == "High"
    assert prepared.settings.throughput_bucket == 2
    assert prepared.settings.query.max_item_count == 1
    assert 0 < prepared.settings.timeout_seconds <= 5
    assert prepared.headers == {"x-test": "yes"}
    assert prepared.read_many_items[0].item_id == "a"
    assert prepared.read_many_items[0].partition_key.values == ("p",)
    assert options == original
    assert backend.deadlines[0] == backend.get_container_metadata.call_args.kwargs["deadline"]


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("defaults", [None, ItemClientDefaults(priority="Low", throughput_bucket=4)])
async def test_omitted_options_and_client_defaults_rust(asynchronous, defaults):
    proxy, backend = make_proxy(asynchronous, defaults=defaults)
    result = proxy.read_items([("a", "p")])
    if asynchronous:
        await result
    settings = backend.calls[0].settings
    assert settings.consistency_level is None and settings.excluded_locations is None
    assert settings.priority == (None if defaults is None else "Low")
    assert settings.throughput_bucket == (None if defaults is None else 4)


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("diagnosed_ids", [(), ("b",), ("b", "a", "missing")])
async def test_available_page_diagnostics_and_missing_item_charge_rust(asynchronous, diagnosed_ids):
    rows = [{"id": "b", "pk": "p"}, {"id": "a", "pk": "p"}]
    pages = [
        page(
            [rows[index]] if index < 2 else [], 2, more=index < 2,
            diagnostics=f"activity={name} requests=1" if name in diagnosed_ids else None,
        )
        for index, name in enumerate(("b", "a", "missing"))
    ]
    proxy, backend = make_proxy(asynchronous, pages)
    hook = MagicMock()
    result = proxy.read_items([("b", "p"), ("a", "p"), ("missing", "p")], response_hook=hook)
    result = await result if asynchronous else result
    assert result == rows
    headers = result.get_response_headers()
    assert headers["x-ms-request-charge"] == "6.0"
    if diagnosed_ids:
        assert set(headers["x-ms-cosmos-sdk-diagnostics"].split("; ")) == {
            f"activity={name} requests=1" for name in diagnosed_ids
        }
    else:
        assert "x-ms-cosmos-sdk-diagnostics" not in headers
    hook.assert_called_once_with(headers, result)
    assert backend.closed == 3


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_absent_charge_is_not_invented_rust(asynchronous):
    proxy, _ = make_proxy(asynchronous, [page([{"id": "a", "pk": "p"}])])
    result = proxy.read_items([("a", "p")])
    result = await result if asynchronous else result
    assert result.get_response_headers() == {}
