# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit checks for legacy replace_throughput fallback payload wiring.

These tests lock down one subtle but important contract in the non-Rust fallback:
the offer document handed to ReplaceOffer must be the mutated document produced by
_replace_throughput, not the pre-mutation source object.
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Dict, Iterable, List

import pytest

from azure.cosmos.container import ContainerProxy as SyncContainerProxy
from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy


def _make_offer() -> Dict[str, Any]:
    return {
        "id": "off-1",
        "_rid": "AAAAAA==",
        "_self": "offers/AAAAAA==/",
        "content": {"offerThroughput": 400},
    }


def test_sync_fallback_replace_offer_uses_mutated_offer_object(monkeypatch):
    """Legacy path (sync, ``_backend=None``): ReplaceOffer must receive the mutated
    offer copy that _replace_throughput produced, and the original queried offer must
    stay untouched. A marker set only on the mutated copy proves the right object was
    sent; without this a fallback regression could PUT back the old throughput.
    """
    container = SyncContainerProxy.__new__(SyncContainerProxy)
    source_offer = _make_offer()
    captured: Dict[str, Any] = {}

    def _query_offers(*_args, **_kwargs) -> List[Dict[str, Any]]:
        return [source_offer]

    def _replace_offer(*_args, **kwargs) -> Dict[str, Any]:
        captured["offer"] = kwargs["offer"]
        return kwargs["offer"]

    container.client_connection = SimpleNamespace(
        _backend=None,
        QueryOffers=_query_offers,
        ReplaceOffer=_replace_offer,
    )
    container.container_link = "dbs/db/colls/coll"

    container._get_properties = lambda: {"_self": "dbs/db/colls/coll", "_rid": "collRid"}

    def _mark_only_mutated_copy(
        *, throughput: Any, new_throughput_properties: Dict[str, Any]
    ) -> None:
        del throughput
        new_throughput_properties["__mutated_marker__"] = True

    monkeypatch.setattr("azure.cosmos._helpers.throughput_helper._replace_throughput", _mark_only_mutated_copy)

    container.replace_throughput(500)

    assert captured["offer"].get("__mutated_marker__") is True
    assert source_offer.get("__mutated_marker__") is None


class _AsyncIterable:
    def __init__(self, rows: Iterable[Dict[str, Any]]) -> None:
        self._rows = list(rows)
        self._index = 0

    def __aiter__(self) -> "_AsyncIterable":
        return self

    async def __anext__(self) -> Dict[str, Any]:
        if self._index >= len(self._rows):
            raise StopAsyncIteration
        row = self._rows[self._index]
        self._index += 1
        return row


@pytest.mark.asyncio
async def test_async_fallback_replace_offer_uses_mutated_offer_object(monkeypatch):
    """Async twin: the async legacy fallback also PUTs the mutated offer copy, not the
    source object.
    """
    container = AsyncContainerProxy.__new__(AsyncContainerProxy)
    source_offer = _make_offer()
    captured: Dict[str, Any] = {}

    def _query_offers(*_args, **_kwargs) -> _AsyncIterable:
        return _AsyncIterable([source_offer])

    async def _replace_offer(*_args, **kwargs) -> Dict[str, Any]:
        captured["offer"] = kwargs["offer"]
        return kwargs["offer"]

    container.client_connection = SimpleNamespace(
        _backend=None,
        QueryOffers=_query_offers,
        ReplaceOffer=_replace_offer,
    )
    container.container_link = "dbs/db/colls/coll"

    async def _get_properties() -> Dict[str, Any]:
        return {"_self": "dbs/db/colls/coll", "_rid": "collRid"}

    container._get_properties = _get_properties

    def _mark_only_mutated_copy(
        *, throughput: Any, new_throughput_properties: Dict[str, Any]
    ) -> None:
        del throughput
        new_throughput_properties["__mutated_marker__"] = True

    monkeypatch.setattr("azure.cosmos._helpers.throughput_helper._replace_throughput", _mark_only_mutated_copy)

    await container.replace_throughput(500)

    assert captured["offer"].get("__mutated_marker__") is True
    assert source_offer.get("__mutated_marker__") is None
