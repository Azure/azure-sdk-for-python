# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Database-query input ownership and independent paging, without service access.

Both transport selections use the current public API. Released-version
compatibility is assessed separately; these comparisons do not supply a
released legacy wrapper.
"""
import json
from copy import deepcopy
from unittest.mock import MagicMock

import pytest
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos._backend.contracts import BackendResponse
from azure.cosmos._backend.errors import BindingProtocolError
from azure.cosmos.exceptions import CosmosHttpResponseError
from query_items.test_query_backend_routing_unit import (
    listing_client,
    _configure_legacy_database_feed,
    _next_listing_page,
)

SQL = "SELECT * FROM db WHERE db.id = @id"


@pytest.fixture(params=[False, True], ids=["rust", "core-python"])
def query_client(listing_client, request):
    client, connection, backend, is_async = listing_client
    legacy = request.param
    if legacy:
        _configure_legacy_database_feed(connection, is_async)
        client._backend = connection._backend

        def respond(*_args, **_kwargs):
            response = backend._response
            headers = CaseInsensitiveDict(response.headers)
            connection.last_response_headers = headers
            return json.loads(response.body), headers

        connection._CosmosClientConnection__Get.side_effect = respond
        connection._CosmosClientConnection__Post.side_effect = respond
    return client, connection, backend, is_async, legacy


def request_count(query_client):
    _, connection, backend, _, _ = query_client
    return (
        backend.execute_pages.call_count
        + connection._CosmosClientConnection__Get.call_count
        + connection._CosmosClientConnection__Post.call_count
    )


@pytest.mark.parametrize("source", ["keyword", "request_options", "feed_options"])
@pytest.mark.parametrize(
    "name,key",
    [
        ("session_token", "sessionToken"),
        ("populate_query_metrics", "populateQueryMetrics"),
        ("availability_strategy", "availabilityStrategy"),
        ("enable_cross_partition_query", "enableCrossPartitionQuery"),
        ("no_response", "responsePayloadOnWriteDisabled"),
        ("content_type", "contentType"),
    ],
)
@pytest.mark.parametrize("value", [None, False, True, "customer-value"])
def test_rejected_options_have_no_nested_bypass(query_client, source, name, key, value):
    kwargs = {name: value} if source == "keyword" else {source: {key: value}}
    original = deepcopy(kwargs)
    with pytest.raises(TypeError, match=name):
        query_client[0].query_databases(SQL, **kwargs)
    assert kwargs == original
    assert request_count(query_client) == 0


@pytest.mark.parametrize("value", [0, -2, 2**63, 2**80, True, 1.5, "invalid"])
@pytest.mark.parametrize("source", ["typed", "initial", "nested", "raw", "default"])
def test_invalid_effective_page_size_fails_before_iteration(query_client, value, source):
    client, connection, _, _, _ = query_client
    header = {"X-MS-MAX-ITEM-COUNT": str(value)}
    if source == "typed":
        kwargs = {"max_item_count": value}
    elif source == "initial":
        kwargs = {"initial_headers": header}
    elif source == "nested":
        kwargs = {"feed_options": {"initialHeaders": header}}
    elif source == "raw":
        kwargs = {"request_options": header}
    else:
        connection.default_headers.update(header)
        kwargs = {}
    original = deepcopy(kwargs)
    with pytest.raises(ValueError, match="max.item.count"):
        client.query_databases(SQL, **kwargs)
    assert kwargs == original
    assert request_count(query_client) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("count", [-1, 1, 2**63 - 1])
async def test_named_page_size_wins_over_invalid_headers(query_client, count):
    client, connection, backend, is_async, legacy = query_client
    connection.default_headers["x-ms-max-item-count"] = "0"
    options = {"initialHeaders": {"X-MS-MAX-ITEM-COUNT": "invalid"}}
    original = deepcopy(options)
    pager = client.query_databases(SQL, max_item_count=count, request_options=options).by_page()
    await _next_listing_page(pager, is_async)
    assert options == original
    if legacy:
        assert connection._CosmosClientConnection__Post.call_args.args[3]["x-ms-max-item-count"] == count
    else:
        assert backend.prepared.max_item_count == count
        assert "x-ms-max-item-count" not in backend.prepared.headers


@pytest.mark.asyncio
@pytest.mark.parametrize("specification", [False, True])
async def test_query_parameters_and_options_are_snapshotted(query_client, specification):
    client, connection, backend, is_async, legacy = query_client
    parameters = [{"name": "@id", "value": {"nested": ["original"]}}]
    query = {"query": SQL, "parameters": parameters} if specification else SQL
    options = {"maxItemCount": 1, "initialHeaders": {"x-trace-id": "original"}}
    original = deepcopy(options)
    iterable = client.query_databases(
        query, request_options=options, **({} if specification else {"parameters": parameters}),
    )
    assert options == original
    assert request_count(query_client) == 0
    parameters[0]["value"]["nested"][0] = "changed"
    options["maxItemCount"] = 5
    options["initialHeaders"]["x-trace-id"] = "changed"
    if specification:
        query["query"] = "SELECT * FROM different"
    pager = iterable.by_page()
    for _ in range(2):
        await _next_listing_page(pager, is_async)
        if legacy:
            call = connection._CosmosClientConnection__Post.call_args
            payload = call.args[2]
            assert call.args[3]["x-ms-max-item-count"] == 1
            assert call.args[3]["x-trace-id"] == "original"
            assert payload["query"] == SQL
            values = payload["parameters"]
        else:
            assert backend.prepared.query == SQL
            assert backend.prepared.max_item_count == 1
            assert backend.prepared.headers["x-trace-id"] == "original"
            values = backend.prepared.parameters
        assert values[0]["value"]["nested"][0] == "original"


@pytest.mark.parametrize(
    "query,parameters",
    [
        ("", None), ("  ", None), (False, None), (12, None),
        ({}, None), ({"query": ""}, None), ({"query": SQL, "extra": True}, None),
        ({"query": SQL, "parameters": []}, []),
        (SQL, {}), (SQL, [{"name": "id", "value": 1}]),
        (SQL, [{"name": "@id"}]), (SQL, [{"name": 1, "value": 2}]),
    ],
)
def test_invalid_query_inputs_fail_before_iteration(query_client, query, parameters):
    with pytest.raises(ValueError):
        query_client[0].query_databases(query, parameters=parameters)
    assert request_count(query_client) == 0


@pytest.mark.parametrize("hook", [False, 0, "not callable", {}])
def test_invalid_hook_does_not_fetch_a_page(query_client, hook):
    with pytest.raises(TypeError, match="callable"):
        query_client[0].query_databases(SQL, response_hook=hook)
    assert request_count(query_client) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("error_type", [StopIteration, StopAsyncIteration, CosmosHttpResponseError])
async def test_hook_failure_never_replays_or_silently_ends(query_client, error_type):
    client, _, _, is_async, _ = query_client
    error = (
        error_type(status_code=429, message="hook failure")
        if error_type is CosmosHttpResponseError else error_type("hook failure")
    )
    hook = MagicMock(side_effect=error)
    pager = client.query_databases(SQL, response_hook=hook).by_page()
    expected = CosmosHttpResponseError if error_type is CosmosHttpResponseError else RuntimeError
    with pytest.raises(expected) as raised:
        await _next_listing_page(pager, is_async)
    if error_type is CosmosHttpResponseError:
        assert raised.value is error
    else:
        assert raised.value.__cause__ is error
    with pytest.raises(RuntimeError, match="pager failed"):
        await _next_listing_page(pager, is_async)
    assert request_count(query_client) == 1
    hook.assert_called_once()


@pytest.mark.asyncio
async def test_hook_isolation_and_false_valued_callable(query_client):
    client, connection, _, is_async, _ = query_client
    calls = []

    class Hook:
        def __bool__(self):
            return False

        def __call__(self, headers):
            calls.append(dict(headers))
            headers.clear()
            connection.last_response_headers = CaseInsensitiveDict({"x-ms-continuation": "unrelated"})

    pager = client.query_databases(SQL, response_hook=Hook()).by_page()
    assert calls == []
    await _next_listing_page(pager, is_async)
    assert len(calls) == 1
    assert pager.continuation_token == "next-db-page"


@pytest.mark.asyncio
@pytest.mark.parametrize("rows", [[{"id": "sales"}], ["sales", 1, None, True, ["nested"]]])
async def test_query_projection_rows_are_not_forced_into_property_dicts(query_client, rows):
    client, _, backend, is_async, _ = query_client
    backend._response = BackendResponse(
        status_code=200, headers=CaseInsensitiveDict(), body=json.dumps({"Databases": rows}).encode(),
    )
    assert await _next_listing_page(client.query_databases(SQL).by_page(), is_async) == rows


@pytest.mark.asyncio
async def test_rust_query_does_not_use_legacy_query_orchestrators(listing_client):
    client, connection, _, is_async = listing_client
    for name in ("QueryDatabases", "ReadDatabases", "_CosmosClientConnection__QueryFeed",
                 "_CosmosClientConnection__CheckAndUnifyQueryFormat"):
        setattr(connection, name, MagicMock(side_effect=AssertionError("legacy orchestration")))
    assert await _next_listing_page(client.query_databases(SQL).by_page(), is_async)


@pytest.mark.asyncio
async def test_empty_page_must_advance_before_retrying(query_client):
    client, _, backend, is_async, _ = query_client
    backend._response = BackendResponse(
        status_code=200, headers=CaseInsensitiveDict({"x-ms-continuation": "same"}),
        body=b'{"Databases":[]}',
    )
    with pytest.raises(BindingProtocolError, match="without continuation progress"):
        await _next_listing_page(client.query_databases(SQL).by_page("same"), is_async)
    assert request_count(query_client) == 1
