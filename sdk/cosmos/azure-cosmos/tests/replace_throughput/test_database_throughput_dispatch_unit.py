# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Check database throughput routing and regression cases.

Supported reads and replacements must use Rust, while unsupported options stay
on Python with their values intact. The tests also protect response hooks,
typed missing-offer errors, database-specific headers, and the current sync and
async option behavior. Customers need reliable throughput values and errors
they can handle by type.
"""
from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any, Dict, List

import pytest

from azure.cosmos import exceptions
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos.aio._database import DatabaseProxy as AsyncDatabaseProxy
from azure.cosmos.database import DatabaseProxy as SyncDatabaseProxy


def _offer(throughput: int = 400) -> Dict[str, Any]:
    """Return a minimal canned offer document at the given throughput."""
    return {
        "id": "off-1",
        "_rid": "AAAAAA==",
        "_self": "offers/AAAAAA==/",
        "content": {"offerThroughput": throughput},
    }


class _Backend:
    """Stand-in backend that records which operations ran and returns canned offers."""

    def __init__(self, offers: List[Dict[str, Any]] | None = None) -> None:
        """Initialise with an optional list of canned offer documents to return."""
        self.calls: List[str] = []
        self.eligibility: List[bool] = []
        self.offers = [_offer()] if offers is None else offers

    def run_operation(self, *, legacy_operation: Any, rust_eligible: bool, **_kwargs: Any) -> Any:
        """Record the operation and route to the legacy path or canned offer list."""
        self.calls.append(legacy_operation.op)
        self.eligibility.append(rust_eligible)
        if not rust_eligible:
            return legacy_operation.invoke()
        return self.offers if legacy_operation.op == "read_offer" else _offer(500)


class _AsyncBackend(_Backend):
    """Async variant of ``_Backend`` for exercising the ``await``-able code paths."""

    async def run_operation(self, *, legacy_operation: Any, rust_eligible: bool, **_kwargs: Any) -> Any:
        """Record the operation and route to the legacy path or canned offer list."""
        self.calls.append(legacy_operation.op)
        self.eligibility.append(rust_eligible)
        if not rust_eligible:
            return await legacy_operation.invoke()
        return self.offers if legacy_operation.op == "read_offer" else _offer(500)


def _sync_database(backend: Any, **connection: Any) -> SyncDatabaseProxy:
    """Build a minimal ``SyncDatabaseProxy`` wired to the given backend stub."""
    database = SyncDatabaseProxy.__new__(SyncDatabaseProxy)
    database.database_link = "dbs/db"
    database._get_properties = lambda: {"_self": "dbs/db/", "_rid": "dbRid"}
    database.client_connection = SimpleNamespace(
        _backend=backend,
        last_response_headers={},
        **connection,
    )
    return database


def _async_database(backend: Any, **connection: Any) -> AsyncDatabaseProxy:
    """Build a minimal ``AsyncDatabaseProxy`` wired to the given backend stub."""
    database = AsyncDatabaseProxy.__new__(AsyncDatabaseProxy)
    database.database_link = "dbs/db"

    async def _properties() -> Dict[str, Any]:
        """Return canned database properties for the stub."""
        return {"_self": "dbs/db/", "_rid": "dbRid"}

    database._get_properties = _properties
    database.client_connection = SimpleNamespace(
        _backend=backend,
        last_response_headers={},
        **connection,
    )
    return database


# --- the option a database offer must not carry ---------------------------


def test_database_read_sends_no_intended_collection_rid(monkeypatch: pytest.MonkeyPatch) -> None:
    """A database throughput read does not send a container-only header."""
    seen: Dict[str, Any] = {}

    def _gate(*, backend: Any, options: Dict[str, Any], kwargs: Dict[str, Any]) -> bool:
        """Intercept the eligibility check and record the options dict."""
        seen["options"] = dict(options)
        return True

    monkeypatch.setattr(
        "azure.cosmos._helpers.throughput_helper.can_use_rust_backend_for_read_offer", _gate
    )
    database = _sync_database(_Backend())

    database.get_throughput()

    assert Constants.ContainerRID not in seen["options"]


def test_container_read_still_sends_the_intended_collection_rid(monkeypatch: pytest.MonkeyPatch) -> None:
    """A container throughput read still sends its required container ID."""
    from azure.cosmos.container import ContainerProxy

    seen: Dict[str, Any] = {}

    def _gate(*, backend: Any, options: Dict[str, Any], kwargs: Dict[str, Any]) -> bool:
        """Intercept the eligibility check and record the options dict."""
        seen["options"] = dict(options)
        return True

    monkeypatch.setattr(
        "azure.cosmos._helpers.throughput_helper.can_use_rust_backend_for_read_offer", _gate
    )
    container = ContainerProxy.__new__(ContainerProxy)
    container.container_link = "dbs/db/colls/coll"
    container._get_properties = lambda: {"_self": "dbs/db/colls/coll", "_rid": "collRid"}
    container.client_connection = SimpleNamespace(_backend=_Backend(), last_response_headers={})

    container.get_throughput()

    assert seen["options"][Constants.ContainerRID] == "collRid"


# --- rust route -----------------------------------------------------------


def test_sync_get_throughput_routes_to_rust(monkeypatch: pytest.MonkeyPatch) -> None:
    """A supported sync read uses Rust and does not call the Python query path."""
    monkeypatch.setattr(
        "azure.cosmos._helpers.throughput_helper.can_use_rust_backend_for_read_offer",
        lambda **_kwargs: True,
    )
    called = False

    def _query_offers(*_args: Any, **_kwargs: Any) -> List[Dict[str, Any]]:
        """Mark that the legacy query path was called; should never be reached."""
        nonlocal called
        called = True
        return [_offer()]

    backend = _Backend()
    database = _sync_database(backend, QueryOffers=_query_offers)
    hooks: List[Any] = []

    result = database.get_throughput(response_hook=lambda headers, body: hooks.append(body))

    assert result.offer_throughput == 400
    assert backend.calls == ["read_offer"]
    assert called is False
    assert len(hooks) == 1


def test_read_offer_is_get_throughput_under_a_deprecated_name(monkeypatch: pytest.MonkeyPatch) -> None:
    """The deprecated name uses the same route and still warns."""
    monkeypatch.setattr(
        "azure.cosmos._helpers.throughput_helper.can_use_rust_backend_for_read_offer",
        lambda **_kwargs: True,
    )
    backend = _Backend()
    database = _sync_database(backend)

    with pytest.warns(DeprecationWarning):
        result = database.read_offer()

    assert result.offer_throughput == 400
    assert backend.calls == ["read_offer"]


def test_sync_replace_throughput_routes_both_legs_to_rust(monkeypatch: pytest.MonkeyPatch) -> None:
    """A supported sync replacement uses Rust for its read and write."""
    monkeypatch.setattr(
        "azure.cosmos._helpers.throughput_helper.can_use_rust_backend_for_replace_throughput",
        lambda **_kwargs: True,
    )
    backend = _Backend()
    database = _sync_database(backend)

    result = database.replace_throughput(500)

    assert result.offer_throughput == 500
    assert backend.calls == ["read_offer", "replace_offer"]
    assert backend.eligibility == [True, True]


def test_async_get_throughput_routes_to_rust(monkeypatch: pytest.MonkeyPatch) -> None:
    """A supported async read uses Rust and does not call the Python query path."""
    monkeypatch.setattr(
        "azure.cosmos._helpers.throughput_helper.can_use_rust_backend_for_read_offer",
        lambda **_kwargs: True,
    )
    backend = _AsyncBackend()
    database = _async_database(backend)

    result = asyncio.run(database.get_throughput())

    assert result.offer_throughput == 400
    assert backend.calls == ["read_offer"]


def test_async_replace_throughput_routes_both_legs_to_rust(monkeypatch: pytest.MonkeyPatch) -> None:
    """A supported async replacement uses Rust for its read and write."""
    monkeypatch.setattr(
        "azure.cosmos._helpers.throughput_helper.can_use_rust_backend_for_replace_throughput",
        lambda **_kwargs: True,
    )
    backend = _AsyncBackend()
    database = _async_database(backend)

    result = asyncio.run(database.replace_throughput(500))

    assert result.offer_throughput == 500
    assert backend.calls == ["read_offer", "replace_offer"]


# --- legacy fallback ------------------------------------------------------


def test_sync_get_throughput_falls_back_to_legacy(monkeypatch: pytest.MonkeyPatch) -> None:
    """An unsupported option stays on Python with its value intact."""
    monkeypatch.setattr(
        "azure.cosmos._helpers.throughput_helper.can_use_rust_backend_for_read_offer",
        lambda **_kwargs: False,
    )
    seen: Dict[str, Any] = {}

    def _query_offers(query_spec: Any, *_args: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        """Capture call kwargs and return the canned offer."""
        seen["query"] = query_spec
        seen["kwargs"] = dict(kwargs)
        return [_offer()]

    database = _sync_database(_Backend(), QueryOffers=_query_offers)

    result = database.get_throughput(read_timeout=3)

    assert result.offer_throughput == 400
    assert seen["kwargs"]["read_timeout"] == 3
    # The database link selects its throughput offer.
    assert seen["query"]["parameters"][0]["value"] == "dbs/db/"


def test_sync_replace_throughput_reads_the_offer_without_caller_keywords(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Sync replacement options apply to the write, as the public API promises."""
    monkeypatch.setattr(
        "azure.cosmos._helpers.throughput_helper.can_use_rust_backend_for_replace_throughput",
        lambda **_kwargs: False,
    )
    read_kwargs: Dict[str, Any] = {}
    replace_kwargs: Dict[str, Any] = {}

    def _query_offers(_query: Any, *_args: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        """Record kwargs forwarded to the read leg; return a canned offer."""
        read_kwargs.update(kwargs)
        return [_offer()]

    def _replace_offer(*, offer_link: str, offer: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """Record kwargs and offer details forwarded to the write leg."""
        replace_kwargs.update(kwargs)
        replace_kwargs["offer_link"] = offer_link
        replace_kwargs["sent_throughput"] = offer["content"]["offerThroughput"]
        return _offer(500)

    database = _sync_database(_Backend(), QueryOffers=_query_offers, ReplaceOffer=_replace_offer)

    result = database.replace_throughput(500, read_timeout=3)

    assert result.offer_throughput == 500
    assert read_kwargs == {}
    assert replace_kwargs["read_timeout"] == 3
    assert replace_kwargs["offer_link"] == "offers/AAAAAA==/"
    # The sent offer contains the requested value.
    assert replace_kwargs["sent_throughput"] == 500


def test_async_replace_throughput_reads_the_offer_with_caller_keywords(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Async replacement options continue to reach both operations."""
    monkeypatch.setattr(
        "azure.cosmos._helpers.throughput_helper.can_use_rust_backend_for_replace_throughput",
        lambda **_kwargs: False,
    )
    read_kwargs: Dict[str, Any] = {}

    class _Offers:
        """Async iterable stub that records kwargs passed to the read leg."""

        def __init__(self, _query: Any, *_args: Any, **kwargs: Any) -> None:
            """Record kwargs forwarded to the read query."""
            read_kwargs.update(kwargs)

        def __aiter__(self) -> "_Offers":
            """Return self as the async iterator."""
            self._sent = False
            return self

        async def __anext__(self) -> Dict[str, Any]:
            """Yield the single canned offer then stop."""
            if self._sent:
                raise StopAsyncIteration
            self._sent = True
            return _offer()

    async def _replace_offer(*, offer_link: str, offer: Dict[str, Any], **_kwargs: Any) -> Dict[str, Any]:
        """Return a canned updated offer to simulate a successful write."""
        return _offer(500)

    database = _async_database(_AsyncBackend(), QueryOffers=_Offers, ReplaceOffer=_replace_offer)

    result = asyncio.run(database.replace_throughput(500, read_timeout=3))

    assert result.offer_throughput == 500
    assert read_kwargs["read_timeout"] == 3


# --- a database with no provisioned throughput ----------------------------


def test_sync_get_throughput_raises_when_no_offer_exists(monkeypatch: pytest.MonkeyPatch) -> None:
    """Missing database throughput raises a typed error instead of ``IndexError``."""
    monkeypatch.setattr(
        "azure.cosmos._helpers.throughput_helper.can_use_rust_backend_for_read_offer",
        lambda **_kwargs: True,
    )
    database = _sync_database(_Backend(offers=[]))

    with pytest.raises(exceptions.CosmosResourceNotFoundError) as caught:
        database.get_throughput()

    assert "Could not find ThroughputProperties for database dbs/db" in caught.value.message


def test_sync_replace_throughput_raises_when_no_offer_exists(monkeypatch: pytest.MonkeyPatch) -> None:
    """Missing offer stops the replacement before it attempts a write."""
    monkeypatch.setattr(
        "azure.cosmos._helpers.throughput_helper.can_use_rust_backend_for_replace_throughput",
        lambda **_kwargs: True,
    )
    backend = _Backend(offers=[])
    database = _sync_database(backend)

    with pytest.raises(exceptions.CosmosResourceNotFoundError):
        database.replace_throughput(500)

    # No write occurs when there is no offer to update.
    assert backend.calls == ["read_offer"]


def test_async_replace_throughput_uses_its_own_not_found_wording(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The async replacement keeps its current typed error message."""
    monkeypatch.setattr(
        "azure.cosmos._helpers.throughput_helper.can_use_rust_backend_for_replace_throughput",
        lambda **_kwargs: True,
    )
    database = _async_database(_AsyncBackend(offers=[]))

    with pytest.raises(exceptions.CosmosResourceNotFoundError) as caught:
        asyncio.run(database.replace_throughput(500))

    assert "Could not find Offer for database dbs/db" in caught.value.message


# --- async-specific regression cases --------------------------------------


def test_async_get_throughput_falls_back_to_legacy(monkeypatch: pytest.MonkeyPatch) -> None:
    """An unsupported async option stays on Python with its value intact."""
    monkeypatch.setattr(
        "azure.cosmos._helpers.throughput_helper.can_use_rust_backend_for_read_offer",
        lambda **_kwargs: False,
    )
    seen: Dict[str, Any] = {}

    def _query_offers(query_spec: Any, *_args: Any, **kwargs: Any) -> Any:
        """Capture call kwargs and return an async-iterable of the canned offer."""
        # The async helper consumes the returned rows with ``async for``.
        seen["query"] = query_spec
        seen["kwargs"] = dict(kwargs)

        async def _pages() -> Any:
            """Yield the single canned offer as an async generator."""
            for offer in [_offer()]:
                yield offer

        return _pages()

    database = _async_database(_AsyncBackend(), QueryOffers=_query_offers)

    result = asyncio.run(database.get_throughput(read_timeout=3))

    assert result.offer_throughput == 400
    assert seen["kwargs"]["read_timeout"] == 3
    # The database link selects its throughput offer.
    assert seen["query"]["parameters"][0]["value"] == "dbs/db/"


def test_async_get_throughput_raises_when_no_offer_exists(monkeypatch: pytest.MonkeyPatch) -> None:
    """An async read uses the stable typed error and message for no throughput."""
    monkeypatch.setattr(
        "azure.cosmos._helpers.throughput_helper.can_use_rust_backend_for_read_offer",
        lambda **_kwargs: True,
    )
    database = _async_database(_AsyncBackend(offers=[]))

    with pytest.raises(exceptions.CosmosResourceNotFoundError) as caught:
        asyncio.run(database.get_throughput())

    assert "Could not find ThroughputProperties for database dbs/db" in caught.value.message


def test_async_replace_throughput_raises_before_writing_an_offer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An async replacement does not write when no throughput offer exists."""
    monkeypatch.setattr(
        "azure.cosmos._helpers.throughput_helper.can_use_rust_backend_for_replace_throughput",
        lambda **_kwargs: True,
    )
    backend = _AsyncBackend(offers=[])
    database = _async_database(backend)

    with pytest.raises(exceptions.CosmosResourceNotFoundError):
        asyncio.run(database.replace_throughput(500))

    assert backend.calls == ["read_offer"]
