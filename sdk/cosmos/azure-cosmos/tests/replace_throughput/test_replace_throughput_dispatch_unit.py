# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit coverage for replace_throughput dispatch (Rust route vs fallback).

These lock in the throughput-dispatch behavior: the public ``ContainerProxy.replace_throughput``
holds no engine logic. It delegates to the throughput coordinator, which routes the
read-modify-write (read the offer, then replace it) to the rust backend when the call
is eligible, and otherwise falls back to the legacy ``QueryOffers`` / ``ReplaceOffer``
calls -- all without the public method knowing which engine ran. No network: the
backend and the client connection are test doubles.
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Dict, List

import pytest

from azure.cosmos._constants import _Constants as Constants
from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy
from azure.cosmos.container import ContainerProxy as SyncContainerProxy


def _offer(throughput: int = 400) -> Dict[str, Any]:
    return {
        "id": "off-1",
        "_rid": "AAAAAA==",
        "_self": "offers/AAAAAA==/",
        "content": {"offerThroughput": throughput},
    }


def test_sync_replace_throughput_routes_to_rust_when_supported(monkeypatch: pytest.MonkeyPatch) -> None:
    """Rust route (sync): when the eligibility gate says yes, both read_offer and
    replace_offer run through the backend and the legacy QueryOffers/ReplaceOffer
    are never called. Also checks the end-to-end timeout is lifted into options and
    no stray kwargs reach the gate. Without this, a regression could quietly keep
    throughput writes on the legacy path or drop the timeout.
    """
    container = SyncContainerProxy.__new__(SyncContainerProxy)
    container.container_link = "dbs/db/colls/coll"
    container._get_properties = lambda: {"_self": "dbs/db/colls/coll", "_rid": "collRid"}

    gate_inputs: Dict[str, Any] = {}
    query_offers_called = False
    replace_offer_called = False

    class _Backend:
        def __init__(self) -> None:
            self.calls: List[str] = []

        def run_operation(self, *, legacy_operation: Any, rust_eligible: bool, **_kwargs: Any) -> Any:
            assert rust_eligible is True
            self.calls.append(legacy_operation.op)
            return [_offer()] if legacy_operation.op == "read_offer" else _offer(500)

    backend = _Backend()

    def _query_offers(*_args: Any, **_kwargs: Any) -> List[Dict[str, Any]]:
        nonlocal query_offers_called
        query_offers_called = True
        return [_offer()]

    def _replace_offer(*_args: Any, **_kwargs: Any) -> Dict[str, Any]:
        nonlocal replace_offer_called
        replace_offer_called = True
        return _offer(500)

    container.client_connection = SimpleNamespace(
        _backend=backend,
        QueryOffers=_query_offers,
        ReplaceOffer=_replace_offer,
        last_response_headers={},
    )

    def _gate(*, backend: Any, options: Dict[str, Any], kwargs: Dict[str, Any]) -> bool:
        gate_inputs["backend"] = backend
        gate_inputs["options"] = dict(options)
        gate_inputs["kwargs"] = dict(kwargs)
        return True

    monkeypatch.setattr("azure.cosmos._helpers.throughput_helper.can_use_rust_backend_for_replace_throughput", _gate)

    result = container.replace_throughput(500, timeout=9)

    assert result.offer_throughput == 500
    assert query_offers_called is False
    assert replace_offer_called is False
    assert gate_inputs["kwargs"] == {}
    assert gate_inputs["options"][Constants.Kwargs.TIMEOUT] == 9
    assert backend.calls == ["read_offer", "replace_offer"]


def test_sync_replace_throughput_falls_back_on_read_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """Legacy fallback (sync): an unsupported knob (``read_timeout``) makes the call
    rust-ineligible, so the coordinator runs the legacy operation and still returns
    the updated offer. Guards against silently dropping an option the rust engine
    cannot honor yet.
    """
    container = SyncContainerProxy.__new__(SyncContainerProxy)
    container.container_link = "dbs/db/colls/coll"
    container._get_properties = lambda: {"_self": "dbs/db/colls/coll", "_rid": "collRid"}

    source_offer = _offer()
    replaced: Dict[str, Any] = {}

    def _query_offers(*_args: Any, **_kwargs: Any) -> List[Dict[str, Any]]:
        return [source_offer]

    def _replace_offer(*_args: Any, **kwargs: Any) -> Dict[str, Any]:
        replaced["offer"] = kwargs["offer"]
        return kwargs["offer"]

    class _Backend:
        def run_operation(self, *, legacy_operation: Any, rust_eligible: bool, **_kwargs: Any) -> Any:
            assert rust_eligible is False
            return legacy_operation.invoke()

    container.client_connection = SimpleNamespace(
        _backend=_Backend(),
        QueryOffers=_query_offers,
        ReplaceOffer=_replace_offer,
        last_response_headers={},
    )

    result = container.replace_throughput(500, read_timeout=2)

    assert result.offer_throughput == 500
    assert replaced["offer"]["content"]["offerThroughput"] == 500


@pytest.mark.asyncio
async def test_async_replace_throughput_routes_to_rust_when_supported(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Async twin of the rust-route test: same guarantee on the async proxy -- both
    offer operations go through the backend, legacy is untouched, timeout is lifted,
    and no stray kwargs reach the gate.
    """
    container = AsyncContainerProxy.__new__(AsyncContainerProxy)
    container.container_link = "dbs/db/colls/coll"

    async def _get_properties() -> Dict[str, Any]:
        return {"_self": "dbs/db/colls/coll", "_rid": "collRid"}

    container._get_properties = _get_properties

    gate_inputs: Dict[str, Any] = {}
    query_offers_called = False
    replace_offer_called = False

    class _Backend:
        def __init__(self) -> None:
            self.calls: List[str] = []

        async def run_operation(
            self, *, legacy_operation: Any, rust_eligible: bool, **_kwargs: Any
        ) -> Any:
            assert rust_eligible is True
            self.calls.append(legacy_operation.op)
            return [_offer()] if legacy_operation.op == "read_offer" else _offer(500)

    backend = _Backend()

    def _query_offers(*_args: Any, **_kwargs: Any) -> Any:
        nonlocal query_offers_called
        query_offers_called = True

        class _EmptyAsyncIterator:
            def __aiter__(self) -> "_EmptyAsyncIterator":
                return self

            async def __anext__(self) -> Dict[str, Any]:
                raise StopAsyncIteration

        return _EmptyAsyncIterator()

    async def _replace_offer(*_args: Any, **_kwargs: Any) -> Dict[str, Any]:
        nonlocal replace_offer_called
        replace_offer_called = True
        return _offer(500)

    container.client_connection = SimpleNamespace(
        _backend=backend,
        QueryOffers=_query_offers,
        ReplaceOffer=_replace_offer,
        last_response_headers={},
    )

    def _gate(*, backend: Any, options: Dict[str, Any], kwargs: Dict[str, Any]) -> bool:
        gate_inputs["backend"] = backend
        gate_inputs["options"] = dict(options)
        gate_inputs["kwargs"] = dict(kwargs)
        return True

    monkeypatch.setattr("azure.cosmos._helpers.throughput_helper.can_use_rust_backend_for_replace_throughput", _gate)

    result = await container.replace_throughput(500, timeout=11)

    assert result.offer_throughput == 500
    assert query_offers_called is False
    assert replace_offer_called is False
    assert gate_inputs["kwargs"] == {}
    assert gate_inputs["options"][Constants.Kwargs.TIMEOUT] == 11
    assert backend.calls == ["read_offer", "replace_offer"]


@pytest.mark.asyncio
async def test_async_replace_throughput_falls_back_on_read_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Async twin of the fallback test: an unsupported knob forces the legacy
    operation on the async proxy and still returns the updated offer.
    """
    container = AsyncContainerProxy.__new__(AsyncContainerProxy)
    container.container_link = "dbs/db/colls/coll"
    source_offer = _offer()
    replaced: Dict[str, Any] = {}

    async def _get_properties() -> Dict[str, Any]:
        return {"_self": "dbs/db/colls/coll", "_rid": "collRid"}

    class _SingleAsyncOffer:
        def __init__(self, row: Dict[str, Any]) -> None:
            self._row = row
            self._yielded = False

        def __aiter__(self) -> "_SingleAsyncOffer":
            return self

        async def __anext__(self) -> Dict[str, Any]:
            if self._yielded:
                raise StopAsyncIteration
            self._yielded = True
            return self._row

    def _query_offers(*_args: Any, **_kwargs: Any) -> _SingleAsyncOffer:
        return _SingleAsyncOffer(source_offer)

    async def _replace_offer(*_args: Any, **kwargs: Any) -> Dict[str, Any]:
        replaced["offer"] = kwargs["offer"]
        return kwargs["offer"]

    container._get_properties = _get_properties
    class _Backend:
        async def run_operation(
            self, *, legacy_operation: Any, rust_eligible: bool, **_kwargs: Any
        ) -> Any:
            assert rust_eligible is False
            return await legacy_operation.invoke()

    container.client_connection = SimpleNamespace(
        _backend=_Backend(),
        QueryOffers=_query_offers,
        ReplaceOffer=_replace_offer,
        last_response_headers={},
    )

    result = await container.replace_throughput(500, read_timeout=2)

    assert result.offer_throughput == 500
    assert replaced["offer"]["content"]["offerThroughput"] == 500
