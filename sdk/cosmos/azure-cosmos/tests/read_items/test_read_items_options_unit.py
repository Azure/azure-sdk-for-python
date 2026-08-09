# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Verify read-many sends customer consistency and routing options."""
from __future__ import annotations

import base64
from unittest.mock import MagicMock

import pytest

from azure.cosmos import documents, http_constants
from azure.cosmos._base import GetHeaders
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._helpers._options import COMMON_OPTIONS
from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy
from azure.cosmos.container import ContainerProxy

_DATABASE_LINK = "dbs/testdb"
_CONTAINER_ID = "testcontainer"
_CONTAINER_LINK = "dbs/testdb/colls/testcontainer"
_ITEMS = [("item1", "pk1")]


def _make_client_connection():
    """Provide the minimum connection used to inspect prepared options."""
    connection = MagicMock()
    connection._container_properties_cache = {_CONTAINER_LINK: {"_rid": "containerrid=="}}
    return connection


def _make_sync_proxy():
    """Provide a sync proxy that records the prepared request options."""
    connection = _make_client_connection()
    proxy = ContainerProxy(connection, _DATABASE_LINK, _CONTAINER_ID)
    captured = {}

    def capture(**kwargs):
        """Record the options dict forwarded to ``read_items``."""
        captured["options"] = kwargs["options"]
        captured["kwargs"] = kwargs
        return []

    connection.read_items = capture
    proxy._get_properties_with_options = lambda options=None: {"id": _CONTAINER_ID}
    proxy._set_partition_key = lambda partition_key: partition_key
    return proxy, captured


def _make_async_proxy():
    """Provide an async proxy that records the prepared request options."""
    connection = _make_client_connection()
    proxy = AsyncContainerProxy(connection, _DATABASE_LINK, _CONTAINER_ID)
    captured = {}

    async def capture(**kwargs):
        """Record the options dict forwarded to ``read_items``."""
        captured["options"] = kwargs["options"]
        captured["kwargs"] = kwargs
        return []

    async def get_properties(options=None):
        """Return a minimal container-properties dict for option-translation tests."""
        return {"id": _CONTAINER_ID}

    async def set_partition_key(partition_key):
        """Pass through the partition key unchanged."""
        return partition_key

    connection.read_items = capture
    proxy._get_properties_with_options = get_properties
    proxy._set_partition_key = set_partition_key
    return proxy, captured


def test_consistency_level_has_no_common_options_entry():
    """Request preparation must set consistency through its dedicated path."""
    assert "consistency_level" not in COMMON_OPTIONS


def test_excluded_locations_is_translated_from_its_snake_case_name():
    """The public excluded-locations name maps to the routing option."""
    assert COMMON_OPTIONS["excluded_locations"] == Constants.Kwargs.EXCLUDED_LOCATIONS
    assert Constants.Kwargs.EXCLUDED_LOCATIONS == "excludedLocations"


def test_consistency_level_header_comes_from_the_options_dict():
    """Prepared consistency becomes the header sent for the request."""
    connection = MagicMock()
    connection.default_headers = {}
    connection._useMultipleWriteLocations = False
    # Use a valid signing key so header preparation reaches the assertion.
    connection.master_key = base64.b64encode(b"0" * 32).decode()
    connection.resource_tokens = None
    connection.aad_credentials = None
    headers = GetHeaders(
        connection,
        {},
        "get",
        "",
        "containerrid==",
        http_constants.ResourceType.Document,
        documents._OperationType.Read,
        {"consistencyLevel": "Eventual"},
    )
    assert headers[http_constants.HttpHeaders.ConsistencyLevel] == "Eventual"


def test_sync_read_items_puts_consistency_level_in_the_options():
    """Sync requests preserve the customer's consistency level."""
    proxy, captured = _make_sync_proxy()

    proxy.read_items(_ITEMS, consistency_level="Eventual")

    assert captured["options"]["consistencyLevel"] == "Eventual"


def test_sync_read_items_keeps_consistency_level_out_of_the_transport_kwargs():
    """Sync requests do not expose consistency as an unknown transport option."""
    proxy, captured = _make_sync_proxy()

    proxy.read_items(_ITEMS, consistency_level="Eventual")

    assert "consistencyLevel" not in captured["kwargs"]
    assert "consistency_level" not in captured["kwargs"]


def test_sync_read_items_translates_excluded_locations_into_the_options():
    """Sync requests send the customer's excluded locations for routing."""
    proxy, captured = _make_sync_proxy()

    proxy.read_items(_ITEMS, excluded_locations=["West US"])

    assert captured["options"]["excludedLocations"] == ["West US"]
    assert "excluded_locations" not in captured["kwargs"]
    assert "excludedLocations" not in captured["kwargs"]


def test_sync_read_items_omits_both_keys_when_the_caller_omits_them():
    """Sync requests do not invent consistency or routing choices."""
    proxy, captured = _make_sync_proxy()

    proxy.read_items(_ITEMS)

    assert "consistencyLevel" not in captured["options"]
    assert "excludedLocations" not in captured["options"]


def test_sync_read_items_carries_both_new_keys_alongside_the_existing_ones():
    """Sync request preparation preserves all customer options together."""
    proxy, captured = _make_sync_proxy()

    proxy.read_items(
        _ITEMS,
        consistency_level="Session",
        excluded_locations=["West US"],
        session_token="token",
        priority="High",
        throughput_bucket=2,
    )

    options = captured["options"]
    assert options["consistencyLevel"] == "Session"
    assert options["excludedLocations"] == ["West US"]
    assert options["sessionToken"] == "token"
    assert options["priorityLevel"] == "High"
    assert options["throughputBucket"] == 2


@pytest.mark.asyncio
async def test_async_read_items_puts_consistency_level_in_the_options():
    """Async requests preserve the customer's consistency level."""
    proxy, captured = _make_async_proxy()

    await proxy.read_items(_ITEMS, consistency_level="Eventual")

    assert captured["options"]["consistencyLevel"] == "Eventual"


@pytest.mark.asyncio
async def test_async_read_items_keeps_consistency_level_out_of_the_transport_kwargs():
    """Async requests do not expose consistency as an unknown transport option."""
    proxy, captured = _make_async_proxy()

    await proxy.read_items(_ITEMS, consistency_level="Eventual")

    assert "consistencyLevel" not in captured["kwargs"]
    assert "consistency_level" not in captured["kwargs"]


@pytest.mark.asyncio
async def test_async_read_items_translates_excluded_locations_into_the_options():
    """Async requests send the customer's excluded locations for routing."""
    proxy, captured = _make_async_proxy()

    await proxy.read_items(_ITEMS, excluded_locations=["West US"])

    assert captured["options"]["excludedLocations"] == ["West US"]
    assert "excluded_locations" not in captured["kwargs"]
    assert "excludedLocations" not in captured["kwargs"]


@pytest.mark.asyncio
async def test_async_read_items_omits_both_keys_when_the_caller_omits_them():
    """Async requests do not invent consistency or routing choices."""
    proxy, captured = _make_async_proxy()

    await proxy.read_items(_ITEMS)

    assert "consistencyLevel" not in captured["options"]
    assert "excludedLocations" not in captured["options"]


@pytest.mark.asyncio
async def test_async_read_items_carries_both_new_keys_alongside_the_existing_ones():
    """Async request preparation preserves all customer options together."""
    proxy, captured = _make_async_proxy()

    await proxy.read_items(
        _ITEMS,
        consistency_level="Session",
        excluded_locations=["West US"],
        session_token="token",
        priority="High",
        throughput_bucket=2,
    )

    options = captured["options"]
    assert options["consistencyLevel"] == "Session"
    assert options["excludedLocations"] == ["West US"]
    assert options["sessionToken"] == "token"
    assert options["priorityLevel"] == "High"
    assert options["throughputBucket"] == 2
