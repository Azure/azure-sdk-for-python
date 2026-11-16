# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Retain shared legacy routing deadline coverage after read_items stops using it."""

import asyncio
import inspect
import time
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from azure.cosmos import _base, _operation_deadline
from azure.cosmos._constants import _Constants as Constants, TimeoutScope
from azure.cosmos._cosmos_client_connection import CosmosClientConnection
from azure.cosmos._routing.routing_map_provider import PartitionKeyRangeCache
from azure.cosmos.aio._cosmos_client_connection_async import CosmosClientConnection as AsyncConnection
from azure.cosmos._routing.aio.routing_map_provider import PartitionKeyRangeCache as AsyncRangeCache
from azure.cosmos.exceptions import CosmosClientTimeoutError

LINK = "dbs/db/colls/c"


@pytest.mark.parametrize("asynchronous", [False, True])
def test_page_dispatch_checks_absolute_deadline_before_transport_rust(asynchronous):
    method = (AsyncConnection if asynchronous else CosmosClientConnection)._CosmosClientConnection__QueryFeed
    connection = MagicMock()
    options = {"_item_operation_deadline": time.monotonic() - 1, "timeout": 100,
               Constants.OperationStartTime: time.time()}
    with pytest.raises(CosmosClientTimeoutError):
        result = method(connection, "/docs", "docs", "rid", lambda value: value, None,
                        "SELECT * FROM c", options=options)
        if inspect.isawaitable(result):
            asyncio.run(result)
    assert connection.mock_calls == []


def test_sync_routing_cache_lock_wait_is_bounded_rust():
    provider = PartitionKeyRangeCache(MagicMock())
    key = _base.GetResourceIdOrFullNameFromLink(LINK)
    lock = provider._get_lock_for_collection(key)
    lock.acquire()
    try:
        with pytest.raises(CosmosClientTimeoutError):
            provider.get_routing_map(LINK, {"_item_operation_deadline": time.monotonic() + 0.03})
        provider._document_client._ReadPartitionKeyRanges.assert_not_called()
        assert lock.locked()
    finally:
        lock.release()
        provider.release()


@pytest.mark.asyncio
async def test_async_routing_cache_lock_wait_is_bounded_rust():
    provider = AsyncRangeCache(MagicMock())
    key = _base.GetResourceIdOrFullNameFromLink(LINK)
    lock = await provider._get_lock_for_collection(key)
    await lock.acquire()
    try:
        with pytest.raises(CosmosClientTimeoutError):
            await provider.get_routing_map(LINK, {"_item_operation_deadline": time.monotonic() + 0.03})
        provider._document_client._ReadPartitionKeyRanges.assert_not_called()
        assert lock.locked()
    finally:
        lock.release()
        provider.release()


@pytest.mark.parametrize("asynchronous", [False, True])
def test_routing_change_feed_pages_consume_one_budget_rust(asynchronous, monkeypatch):
    clock = SimpleNamespace(monotonic=lambda: clock.now, time=lambda: clock.now, now=100.0)
    monkeypatch.setattr(_operation_deadline, "time", clock)
    connection = MagicMock()
    budgets = []

    def get_page(_link, options, **kwargs):
        budgets.append(options["timeout"])
        assert options[Constants.TimeoutScope] == TimeoutScope.OPERATION
        kwargs["_internal_response_headers_capture"]["etag"] = "v1"
        kwargs["_internal_response_status_capture"][0] = 200 if len(budgets) == 1 else 304
        clock.now += 1.5
        return [{"id": "0", "minInclusive": "", "maxExclusive": "FF"}] if len(budgets) == 1 else []

    def sync_pages(*args, **kwargs):
        yield from get_page(*args, **kwargs)

    async def async_pages(*args, **kwargs):
        for value in get_page(*args, **kwargs):
            yield value

    connection._ReadPartitionKeyRanges = async_pages if asynchronous else sync_pages
    provider = (AsyncRangeCache if asynchronous else PartitionKeyRangeCache)(connection)
    try:
        result = provider.get_routing_map(LINK, {"_item_operation_deadline": 105.0})
        if inspect.isawaitable(result):
            asyncio.run(result)
        assert budgets == [5.0, 3.5]
    finally:
        provider.release()
