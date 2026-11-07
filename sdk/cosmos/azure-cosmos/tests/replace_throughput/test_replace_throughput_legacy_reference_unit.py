# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit checks for explicitly selected legacy comparison payload wiring.

These tests lock down one contract in the isolated comparison backend:
the offer document handed to ReplaceOffer must be the mutated document produced by
_replace_throughput, not the pre-mutation source object.
"""
from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any, Dict, Iterable, List

import pytest

from azure.cosmos._backend.legacy import LEGACY_BACKEND
from azure.cosmos.aio._backend.legacy import ASYNC_LEGACY_BACKEND
from azure.cosmos.container import ContainerProxy as SyncContainerProxy
from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy


def _make_offer() -> Dict[str, Any]:
    """Return a minimal offer document with an initial ``offerThroughput`` of 400."""
    return {
        "id": "off-1",
        "_rid": "AAAAAA==",
        "_self": "offers/AAAAAA==/",
        "content": {"offerThroughput": 400},
    }


@pytest.mark.parametrize("asynchronous", [False, True])
def test_reference_replace_offer_forwards_normalized_options_once_rust(asynchronous):
    from azure.cosmos._cosmos_client_connection import CosmosClientConnection
    from azure.cosmos.aio._cosmos_client_connection_async import (
        CosmosClientConnection as AsyncCosmosClientConnection,
    )

    options = {"initialHeaders": {"x-customer": "kept"}}
    seen = []

    def replace(resource, path, resource_type, resource_id, headers, options=None, **kwargs):
        seen.append((options, kwargs))
        return resource

    async def replace_async(*args, **kwargs):
        return replace(*args, **kwargs)

    connection_type = AsyncCosmosClientConnection if asynchronous else CosmosClientConnection
    connection = connection_type.__new__(connection_type)
    connection.Replace = replace_async if asynchronous else replace
    result = connection.ReplaceOffer(
        "offers/AAAAAA==/", _make_offer(), options=options, timeout=10,
    )
    if asynchronous:
        result = asyncio.run(result)
    assert result == _make_offer()
    assert seen == [(options, {"timeout": 10})]


def test_sync_reference_replace_throughput_uses_mutated_offer_object_rust(monkeypatch):
    """Legacy path: ReplaceOffer must receive the mutated
    offer copy that _replace_throughput produced, and the original queried offer must
    stay untouched. A marker set only on the mutated copy proves the right object was
    sent; without this a regression could PUT back the old throughput.
    """
    container = SyncContainerProxy.__new__(SyncContainerProxy)
    source_offer = _make_offer()
    captured: Dict[str, Any] = {}

    def _query_offers(*_args, **_kwargs) -> List[Dict[str, Any]]:
        """Return the source offer, standing in for a ``QueryOffers`` legacy call."""
        return [source_offer]

    def _replace_throughput(*_args, **kwargs) -> Dict[str, Any]:
        """Capture the offer passed to ``ReplaceOffer`` and return it as-is."""
        captured["offer"] = kwargs["offer"]
        return kwargs["offer"]

    container.client_connection = SimpleNamespace(
        _backend=LEGACY_BACKEND,
        last_response_headers={},
        QueryOffers=_query_offers,
        ReplaceOffer=_replace_throughput,
    )
    container.container_link = "dbs/db/colls/coll"

    container._get_properties = lambda: {"_self": "dbs/db/colls/coll", "_rid": "collRid"}

    def _mark_only_mutated_copy(
        *, throughput: Any, new_throughput_properties: Dict[str, Any]
    ) -> None:
        """Set a marker on the mutated copy only, leaving the source offer untouched."""
        del throughput
        new_throughput_properties["__mutated_marker__"] = True

    monkeypatch.setattr("azure.cosmos._helpers._container_throughput._replace_throughput", _mark_only_mutated_copy)

    container.replace_throughput(500)

    assert captured["offer"].get("__mutated_marker__") is True
    assert source_offer.get("__mutated_marker__") is None


class _AsyncIterable:
    """Async iterator over a fixed list of rows, standing in for a paginated query result."""

    def __init__(self, rows: Iterable[Dict[str, Any]]) -> None:
        """Store the rows and initialise the cursor."""
        self._rows = list(rows)
        self._index = 0

    def __aiter__(self) -> "_AsyncIterable":
        """Return self as the async iterator."""
        return self

    async def __anext__(self) -> Dict[str, Any]:
        """Yield the next row or raise ``StopAsyncIteration`` when exhausted."""
        if self._index >= len(self._rows):
            raise StopAsyncIteration
        row = self._rows[self._index]
        self._index += 1
        return row


@pytest.mark.asyncio
async def test_async_reference_replace_throughput_uses_mutated_offer_object_rust(monkeypatch):
    """Async twin: the explicit legacy reference PUTs the mutated offer copy, not the
    source object.
    """
    container = AsyncContainerProxy.__new__(AsyncContainerProxy)
    source_offer = _make_offer()
    captured: Dict[str, Any] = {}

    def _query_offers(*_args, **_kwargs) -> _AsyncIterable:
        """Wrap the source offer in an ``_AsyncIterable``, standing in for ``QueryOffers``."""
        return _AsyncIterable([source_offer])

    async def _replace_throughput(*_args, **kwargs) -> Dict[str, Any]:
        """Capture the offer passed to ``ReplaceOffer`` and return it as-is."""
        captured["offer"] = kwargs["offer"]
        return kwargs["offer"]

    container.client_connection = SimpleNamespace(
        _backend=ASYNC_LEGACY_BACKEND,
        last_response_headers={},
        QueryOffers=_query_offers,
        ReplaceOffer=_replace_throughput,
    )
    container.container_link = "dbs/db/colls/coll"

    async def _get_properties() -> Dict[str, Any]:
        """Return canned container properties including ``_self`` and ``_rid``."""
        return {"_self": "dbs/db/colls/coll", "_rid": "collRid"}

    container._get_properties = _get_properties

    def _mark_only_mutated_copy(
        *, throughput: Any, new_throughput_properties: Dict[str, Any]
    ) -> None:
        """Set a marker on the mutated copy only, leaving the source offer untouched."""
        del throughput
        new_throughput_properties["__mutated_marker__"] = True

    monkeypatch.setattr("azure.cosmos._helpers._container_throughput._replace_throughput", _mark_only_mutated_copy)

    await container.replace_throughput(500)

    assert captured["offer"].get("__mutated_marker__") is True
    assert source_offer.get("__mutated_marker__") is None
