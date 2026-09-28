# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Container-specific recovery is bounded and never changes execution paths."""

import asyncio
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from azure.cosmos import exceptions
from azure.cosmos.container import ContainerProxy
from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy
from azure.cosmos._backend.contracts import BackendResponse
from azure.cosmos._backend.cosmos_backend import CosmosBackend
from azure.cosmos.aio._backend.cosmos_backend import AsyncCosmosBackend
from azure.cosmos.http_constants import HttpHeaders, SubStatusCodes
from common.typed_requests import wire_headers


def response(offers=(), status=200, substatus=0):
    return BackendResponse(
        status_code=status,
        headers={HttpHeaders.SubStatus: str(substatus), "etag": "last-page"},
        body=json.dumps({"Offers": list(offers)}).encode(),
    )


OFFER = {"content": {"offerThroughput": 800}, "_self": "offers/offer/"}


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def read(request):
    state = SimpleNamespace(requests=[], responses=[response([OFFER])])

    def execute(prepared):
        state.requests.append(prepared)
        return state.responses.pop(0)

    class Backend(CosmosBackend):
        name = "rust"

        def execute(self, prepared, *, deadline=None):
            return execute(prepared)

    class AsyncBackend(AsyncCosmosBackend):
        name = "rust"

        async def execute(self, prepared, *, deadline=None):
            return execute(prepared)

    proxy = AsyncContainerProxy if request.param else ContainerProxy
    state.container = proxy.__new__(proxy)
    state.container.container_link = "dbs/sales/colls/orders"
    state.container.client_connection = SimpleNamespace(
        _backend=AsyncBackend() if request.param else Backend(),
        default_headers={}, last_response_headers={},
        QueryOffers=Mock(side_effect=AssertionError("legacy query must not execute")),
    )
    mock = AsyncMock if request.param else Mock
    state.container._get_properties = mock(return_value={"_rid": "old", "_self": "dbs/db/colls/old/"})
    state.container.read = mock(return_value={"_rid": "new", "_self": "dbs/db/colls/new/"})

    def invoke(**kwargs):
        result = state.container.get_throughput(**kwargs)
        return asyncio.run(result) if request.param else result

    state.invoke = invoke
    return state


@pytest.mark.parametrize("first", [
    response(),
    response(status=400, substatus=SubStatusCodes.COLLECTION_RID_MISMATCH),
    response(status=404, substatus=SubStatusCodes.THROUGHPUT_OFFER_NOT_FOUND),
])
def test_recreated_container_rebuilds_query_once(read, first):
    read.responses = [first, response([OFFER])]
    hook = Mock()
    result = read.invoke(response_hook=hook)
    assert result.offer_throughput == 800
    assert result.get_response_headers()["etag"] == "last-page"
    assert [json.loads(p.body_bytes)["parameters"][0]["value"] for p in read.requests] == [
        "dbs/db/colls/old/", "dbs/db/colls/new/",
    ]
    assert [wire_headers(p)[HttpHeaders.IntendedCollectionRID] for p in read.requests] == ["old", "new"]
    read.container.read.assert_called_once()
    hook.assert_called_once()
    read.container.client_connection.QueryOffers.assert_not_called()


@pytest.mark.parametrize("changed", [False, True])
def test_missing_dedicated_offer_is_typed_and_bounded(read, changed):
    if not changed:
        read.container.read.return_value = read.container._get_properties.return_value
    read.responses = [response(), response()]
    hook = Mock()
    with pytest.raises(exceptions.CosmosResourceNotFoundError) as caught:
        read.invoke(response_hook=hook)
    assert caught.value.status_code == 404
    assert caught.value.sub_status == SubStatusCodes.THROUGHPUT_OFFER_NOT_FOUND
    assert len(read.requests) == (2 if changed else 1)
    read.container.read.assert_called_once()
    hook.assert_not_called()


def test_failed_retry_does_not_return_partial_success(read):
    read.responses = [response(), response(status=403)]
    with pytest.raises(exceptions.CosmosHttpResponseError) as caught:
        read.invoke()
    assert caught.value.status_code == 403
    assert caught.value.headers["etag"] == "last-page"
    assert len(read.requests) == 2
    read.container.read.assert_called_once()


def test_no_refresh_on_access_error(read):
    read.responses = [response(status=403)]
    with pytest.raises(exceptions.CosmosHttpResponseError):
        read.invoke()
    read.container.read.assert_not_called()


def test_refresh_failure_propagates_without_retry(read):
    error = exceptions.CosmosResourceNotFoundError(status_code=404, message="container deleted")
    read.responses = [response()]
    read.container.read.side_effect = error
    with pytest.raises(exceptions.CosmosResourceNotFoundError) as caught:
        read.invoke()
    assert caught.value is error
    assert len(read.requests) == 1


def test_callback_error_is_not_a_recovery_signal(read):
    error = exceptions.CosmosResourceNotFoundError(
        status_code=404, sub_status=SubStatusCodes.THROUGHPUT_OFFER_NOT_FOUND,
    )
    with pytest.raises(exceptions.CosmosResourceNotFoundError) as caught:
        read.invoke(response_hook=Mock(side_effect=error))
    assert caught.value is error
    read.container.read.assert_not_called()


def test_recovery_error_with_unchanged_metadata_is_not_replayed(read):
    read.responses = [response(status=400, substatus=SubStatusCodes.COLLECTION_RID_MISMATCH)]
    read.container.read.return_value = read.container._get_properties.return_value
    with pytest.raises(exceptions.CosmosHttpResponseError) as caught:
        read.invoke()
    assert caught.value.status_code == 400
    assert caught.value.sub_status == SubStatusCodes.COLLECTION_RID_MISMATCH
    assert len(read.requests) == 1


@pytest.mark.parametrize("asynchronous", [False, True])
def test_outer_legacy_retry_preserves_inner_missing_offer(asynchronous):
    from azure.cosmos import _retry_utility
    from azure.cosmos.aio import _retry_utility_async
    from azure.cosmos.documents import ConnectionPolicy

    error = exceptions.CosmosResourceNotFoundError(
        status_code=404, sub_status=SubStatusCodes.THROUGHPUT_OFFER_NOT_FOUND,
    )
    client = SimpleNamespace(
        connection_policy=ConnectionPolicy(), _container_properties_cache={},
        last_response_headers={},
        _refresh_container_properties_cache=Mock(side_effect=AssertionError("no container context")),
    )
    with pytest.raises(exceptions.CosmosResourceNotFoundError) as caught:
        if asynchronous:
            asyncio.run(_retry_utility_async.ExecuteAsync(client, MagicMock(), AsyncMock(side_effect=error)))
        else:
            _retry_utility.Execute(client, MagicMock(), Mock(side_effect=error))
    assert caught.value is error
    client._refresh_container_properties_cache.assert_not_called()


@pytest.mark.parametrize("asynchronous", [False, True])
def test_empty_legacy_container_page_with_continuation_is_not_not_found(monkeypatch, asynchronous):
    from azure.cosmos import _retry_utility, _container_recreate_retry_policy
    from azure.cosmos.aio import _retry_utility_async
    from azure.cosmos.documents import ConnectionPolicy
    from azure.cosmos._request_object import RequestObject
    from azure.core.pipeline.transport import HttpRequest

    policy = Mock(container_link="dbs/sales/colls/orders")
    monkeypatch.setattr(_container_recreate_retry_policy, "ContainerRecreateRetryPolicy", Mock(return_value=policy))
    request = RequestObject(resource_type="offers", operation_type="Query", headers={})
    http_request = HttpRequest("POST", "https://example.test/offers")
    client = Mock(connection_policy=ConnectionPolicy(), last_response_headers={})
    manager = MagicMock()
    manager.is_per_partition_automatic_failover_applicable.return_value = False
    manager.is_circuit_breaker_applicable.return_value = False
    if asynchronous:
        manager.record_success = AsyncMock()
    args = (request, client.connection_policy, Mock(), http_request)
    page = ({"Offers": []}, {HttpHeaders.Continuation: "next"})
    if asynchronous:
        result = asyncio.run(_retry_utility_async.ExecuteAsync(client, manager, AsyncMock(return_value=page), *args))
    else:
        result = _retry_utility.Execute(client, manager, Mock(return_value=page), *args)
    assert result is page
    client._refresh_container_properties_cache.assert_not_called()
