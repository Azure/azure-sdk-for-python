# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Check shared database/container read behavior and database replacement routing.

Supported reads use the Rust path; unsupported read inputs raise rather than
selecting the legacy Python path. The tests also protect response hooks,
typed missing-offer errors, database-specific headers, and the current sync and
async option behavior. Customers need reliable throughput values and errors
they can handle by type.
"""
from __future__ import annotations

import asyncio
from copy import deepcopy
import json
from types import SimpleNamespace
from typing import Any, Dict, List

import pytest

from azure.cosmos import exceptions
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._backend.contracts import BackendResponse
from azure.cosmos._backend.cosmos_backend import CosmosBackend
from azure.cosmos.aio._backend.cosmos_backend import AsyncCosmosBackend
from azure.cosmos.aio._database import DatabaseProxy as AsyncDatabaseProxy
from azure.cosmos.database import DatabaseProxy as SyncDatabaseProxy
from azure.cosmos.container import ContainerProxy as SyncContainerProxy
from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy


class _ReadBackend(CosmosBackend):
    name = "rust"

    def __init__(self) -> None:
        self.requests = []
        self.offers = [_offer(4000)]
        self.status = 200

    def execute(self, prepared, *, deadline=None):
        self.requests.append(prepared)
        return BackendResponse(
            status_code=self.status,
            headers={"x-ms-request-charge": "2.5", "etag": "offer-etag"},
            body=json.dumps({"Offers": self.offers}).encode(),
        )


class _AsyncReadBackend(AsyncCosmosBackend):
    name = "rust"

    def __init__(self, recording) -> None:
        self.recording = recording

    async def execute(self, prepared, *, deadline=None):
        return self.recording.execute(prepared, deadline=deadline)


@pytest.fixture(params=["sync", "async", "container-sync", "container-async"])
def database_read(request):
    recording = _ReadBackend()
    metadata = []
    is_container = request.param.startswith("container-")
    properties = (
        {"_self": "dbs/db/colls/coll/", "_rid": "collRid"}
        if is_container else {"_self": "dbs/db/", "_rid": "dbRid"}
    )
    if request.param in ("async", "container-async"):
        database = _async_database(_AsyncReadBackend(recording), default_headers={})

        async def get_properties():
            metadata.append(True)
            return properties

        def invoke(**kwargs):
            return asyncio.run(database.get_throughput(**kwargs))
    else:
        database = _sync_database(recording, default_headers={})

        def get_properties():
            metadata.append(True)
            return properties

        def invoke(**kwargs):
            return database.get_throughput(**kwargs)

    if is_container:
        proxy = AsyncContainerProxy if request.param == "container-async" else SyncContainerProxy
        container = proxy.__new__(proxy)
        container.client_connection = database.client_connection
        container.container_link = "dbs/db/colls/coll"
        container.read = get_properties
        database = container
    database._get_properties = get_properties
    return invoke, database, recording, metadata


def test_database_read_retains_its_own_headers(database_read):
    invoke, database, recording, _ = database_read
    result = invoke()
    headers = result.get_response_headers()
    assert headers["etag"] == "offer-etag"
    assert float(headers["x-ms-request-charge"]) == 2.5
    headers.clear()
    database.client_connection.last_response_headers = {"etag": "another-operation"}
    assert result.get_response_headers()["etag"] == "offer-etag"
    assert result.offer_throughput == 4000
    assert len(recording.requests) == 1


def test_database_read_hook_cannot_change_result(database_read):
    invoke, database, _, _ = database_read
    calls = []

    def hook(headers, offers):
        calls.append(offers[0]["content"]["offerThroughput"])
        headers.clear()
        offers[0]["content"]["offerThroughput"] = 999
        offers.clear()
        database.client_connection.last_response_headers = {"etag": "another-operation"}

    result = invoke(response_hook=hook)
    assert calls == [4000]
    assert result.offer_throughput == 4000
    assert result.properties["content"]["offerThroughput"] == 4000
    assert result.get_response_headers()["etag"] == "offer-etag"


@pytest.mark.parametrize("hook", [False, 0, "", "not-callable", {}])
def test_database_read_rejects_invalid_hook_before_requests(database_read, hook):
    invoke, _, recording, metadata = database_read
    with pytest.raises(TypeError, match="response_hook must be callable or None"):
        invoke(response_hook=hook)
    assert not metadata
    assert not recording.requests


def test_database_read_invokes_false_valued_callable(database_read):
    invoke, _, _, _ = database_read

    class Hook:
        calls = 0

        def __bool__(self):
            return False

        def __call__(self, headers, offers):
            self.calls += 1

    hook = Hook()
    invoke(response_hook=hook)
    assert hook.calls == 1


def test_database_read_does_not_replay_hook_failure(database_read):
    invoke, _, recording, _ = database_read
    error = RuntimeError("callback failed")

    def hook(headers, offers):
        raise error

    with pytest.raises(RuntimeError) as caught:
        invoke(response_hook=hook)
    assert caught.value is error
    assert len(recording.requests) == 1


@pytest.mark.parametrize("alias", ["request_options", "feed_options"])
def test_database_read_preserves_customer_options(database_read, alias):
    invoke, _, recording, _ = database_read
    options = {"initialHeaders": {"x-customer": "kept"}}
    initial_headers = {"x-customer": "override"}
    original = deepcopy((options, initial_headers))
    invoke(**{alias: options}, initial_headers=initial_headers)
    assert (options, initial_headers) == original
    assert recording.requests[0].headers["x-customer"] == "override"


@pytest.mark.parametrize("alias", ["request_options", "feed_options"])
@pytest.mark.parametrize("value", [None, [], False, "options"])
def test_database_read_rejects_invalid_options_before_requests(database_read, alias, value):
    invoke, _, recording, metadata = database_read
    with pytest.raises(TypeError, match=f"{alias} must be a mapping"):
        invoke(**{alias: value})
    assert not metadata
    assert not recording.requests


def test_database_read_missing_offer_does_not_call_hook(database_read):
    invoke, _, recording, _ = database_read
    recording.offers = []
    calls = []
    with pytest.raises(exceptions.CosmosResourceNotFoundError):
        invoke(response_hook=lambda *_: calls.append(True))
    assert not calls
    assert len(recording.requests) == 1


def test_database_read_service_failure_keeps_headers_and_skips_hook(database_read):
    invoke, _, recording, _ = database_read
    recording.status = 403
    calls = []
    options = {"initialHeaders": {"x-customer": "kept"}}
    original = deepcopy(options)
    with pytest.raises(exceptions.CosmosHttpResponseError) as caught:
        invoke(request_options=options, response_hook=lambda *_: calls.append(True))
    assert caught.value.status_code == 403
    assert caught.value.headers["etag"] == "offer-etag"
    assert not calls
    assert len(recording.requests) == 1
    assert options == original


@pytest.mark.parametrize("fail", [False, True])
@pytest.mark.parametrize("alias", ["request_options", "feed_options", "options"])
def test_explicit_legacy_database_read_preserves_owned_data(database_read, fail, alias):
    invoke, database, recording, _ = database_read
    from azure.cosmos._backend.legacy import LEGACY_BACKEND
    from azure.cosmos.aio._backend.legacy import ASYNC_LEGACY_BACKEND

    database.client_connection._backend = (
        ASYNC_LEGACY_BACKEND if isinstance(database, (AsyncDatabaseProxy, AsyncContainerProxy)) else LEGACY_BACKEND
    )
    options = {"initialHeaders": {"x-customer": "kept"}}
    original = deepcopy(options)
    calls = []

    def query(query_spec, options, **kwargs):
        expected_link = "dbs/db/colls/coll/" if hasattr(database, "container_link") else "dbs/db/"
        assert query_spec["parameters"][0]["value"] == expected_link
        assert kwargs["read_timeout"] == 3
        assert kwargs["timeout"] == 10
        if alias != "options":
            assert options["timeout"] == 10
        assert "request_options" not in kwargs
        assert "feed_options" not in kwargs
        options["initialHeaders"]["x-customer"] = "changed"
        if fail:
            raise RuntimeError("legacy query failed")
        database.client_connection.last_response_headers = {"etag": "legacy-offer"}
        return [_offer(4000)]

    async def query_async(query_spec, options, **kwargs):
        for offer in query(query_spec, options, **kwargs):
            yield offer

    database.client_connection.QueryOffers = (
        query_async if isinstance(database, (AsyncDatabaseProxy, AsyncContainerProxy)) else query
    )

    def hook(headers, offers):
        calls.append(True)
        headers.clear()
        offers.clear()

    if fail:
        with pytest.raises(RuntimeError, match="legacy query failed"):
            invoke(**{alias: options}, read_timeout=3, timeout=10, response_hook=hook)
        assert not calls
    else:
        result = invoke(**{alias: options}, read_timeout=3, timeout=10, response_hook=hook)
        assert result.offer_throughput == 4000
        assert result.get_response_headers()["etag"] == "legacy-offer"
        assert calls == [True]
    assert options == original
    assert not recording.requests


@pytest.mark.parametrize("kwargs", [
    {"read_timeout": 2},
    {"connection_timeout": 2},
    {"availability_strategy": {"type": "hedging"}},
    {"initial_headers": {"Accept": "custom"}},
    {"initial_headers": {"Cache-Control": "custom"}},
    {"initial_headers": {"User-Agent": "custom"}},
    {"initial_headers": {"x-ms-version": "custom"}},
    {"unknown_option": True},
    {"options": {"read_timeout": 2}},
    {"request_options": {"read_timeout": 2}},
    {"feed_options": {"read_timeout": 2}},
    {"request_options": {"initialHeaders": {"Accept": "custom"}}},
    {"timeout": 0.5},
])
def test_database_read_rejects_unsupported_inputs_without_legacy(database_read, kwargs):
    from unittest.mock import Mock
    from azure.cosmos._backend._fallback_metrics import rust_compatibility_fallback_count

    invoke, database, recording, metadata = database_read
    legacy = Mock(side_effect=AssertionError("legacy Python path must not run"))
    database.client_connection.QueryOffers = legacy
    original = deepcopy(kwargs)
    hooks = []
    before = rust_compatibility_fallback_count()
    with pytest.raises(NotImplementedError, match="legacy Python path"):
        invoke(response_hook=lambda *_: hooks.append(True), **kwargs)
    assert kwargs == original
    assert not hooks
    assert not metadata
    assert not recording.requests
    assert rust_compatibility_fallback_count() == before
    legacy.assert_not_called()


def test_database_read_rejects_unknown_nested_option_before_requests(database_read):
    invoke, _, recording, metadata = database_read
    with pytest.raises((TypeError, ValueError)):
        invoke(request_options={"unknown_option": True})
    assert not metadata
    assert not recording.requests


def test_database_read_preserves_autoscale_fields(database_read):
    invoke, _, recording, _ = database_read
    recording.offers[0]["content"] = {
        "offerAutopilotSettings": {
            "maxThroughput": 10000,
            "autoUpgradePolicy": {"throughputPolicy": {"incrementPercent": 10}},
        }
    }
    def hook(headers, offers):
        offers[0]["content"]["offerAutopilotSettings"]["maxThroughput"] = 999

    result = invoke(response_hook=hook)
    assert result.offer_throughput is None
    assert result.auto_scale_max_throughput == 10000
    assert result.auto_scale_increment_percent == 10
    assert result.get_response_headers()["etag"] == "offer-etag"


@pytest.mark.parametrize("proxy", [
    SyncDatabaseProxy, AsyncDatabaseProxy, SyncContainerProxy, AsyncContainerProxy,
])
def test_public_throughput_surface_has_no_offer_aliases(proxy):
    assert callable(proxy.get_throughput)
    assert callable(proxy.replace_throughput)
    instance = proxy.__new__(proxy)
    for name in ("read_offer", "replace_offer"):
        assert not hasattr(proxy, name)
        with pytest.raises(AttributeError):
            getattr(instance, name)


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("continuation", [None, "next-page"])
def test_legacy_retry_keeps_empty_database_offer_pages(asynchronous, continuation):
    from unittest.mock import MagicMock
    from azure.cosmos import _retry_utility
    from azure.cosmos.aio import _retry_utility_async
    from azure.cosmos.documents import ConnectionPolicy

    client = SimpleNamespace(
        connection_policy=ConnectionPolicy(), _container_properties_cache={},
        last_response_headers={},
    )
    headers = {"x-ms-continuation": continuation} if continuation else {}
    page = ({"Offers": []}, headers)

    async def respond():
        return page

    if asynchronous:
        result = asyncio.run(_retry_utility_async.ExecuteAsync(client, MagicMock(), respond))
    else:
        result = _retry_utility.Execute(client, MagicMock(), lambda: page)
    assert result is page


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

    def run_operation(self, *, routing: Any, legacy_call: Any, **_kwargs: Any) -> Any:
        """Record the operation and route to the legacy path or canned offer list."""
        self.calls.append(routing.op)
        self.eligibility.append(routing.supported)
        if not routing.supported:
            return legacy_call()
        return self.offers if routing.op == "read_offer" else _offer(500)


class _AsyncBackend(_Backend):
    """Async variant of ``_Backend`` for exercising the ``await``-able code paths."""

    async def run_operation(self, *, routing: Any, legacy_call: Any, **_kwargs: Any) -> Any:
        """Record the operation and route to the legacy path or canned offer list."""
        self.calls.append(routing.op)
        self.eligibility.append(routing.supported)
        if not routing.supported:
            return await legacy_call()
        return self.offers if routing.op == "read_offer" else _offer(500)


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
        "azure.cosmos._helpers._database_throughput.can_use_rust_backend_for_read_offer", _gate
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
        seen["options"] = options
        return True

    monkeypatch.setattr(
        "azure.cosmos._helpers._container_throughput.can_use_rust_backend_for_read_offer", _gate
    )
    container = ContainerProxy.__new__(ContainerProxy)
    container.container_link = "dbs/db/colls/coll"
    container._get_properties = lambda: {"_self": "dbs/db/colls/coll", "_rid": "collRid"}
    container.client_connection = SimpleNamespace(_backend=_Backend(), last_response_headers={})

    container.get_throughput()

    assert seen["options"][Constants.ContainerRID] == "collRid"


# --- Rust route -----------------------------------------------------------


def test_sync_get_throughput_routes_to_rust(monkeypatch: pytest.MonkeyPatch) -> None:
    """A supported sync read uses Rust and does not call the Python query path."""
    monkeypatch.setattr(
        "azure.cosmos._helpers._database_throughput.can_use_rust_backend_for_read_offer",
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


def test_sync_replace_throughput_routes_both_legs_to_rust(monkeypatch: pytest.MonkeyPatch) -> None:
    """A supported sync replacement uses Rust for its read and write."""
    monkeypatch.setattr(
        "azure.cosmos._helpers._database_throughput.can_use_rust_backend_for_replace_throughput",
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
        "azure.cosmos._helpers._database_throughput.can_use_rust_backend_for_read_offer",
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
        "azure.cosmos._helpers._database_throughput.can_use_rust_backend_for_replace_throughput",
        lambda **_kwargs: True,
    )
    backend = _AsyncBackend()
    database = _async_database(backend)

    result = asyncio.run(database.replace_throughput(500))

    assert result.offer_throughput == 500
    assert backend.calls == ["read_offer", "replace_offer"]


# --- legacy fallback ------------------------------------------------------


def test_sync_explicit_legacy_get_throughput_preserves_options(monkeypatch: pytest.MonkeyPatch) -> None:
    """The separately selected legacy Python path remains available for comparison."""
    monkeypatch.setattr(
        "azure.cosmos._helpers._database_throughput.can_use_rust_backend_for_read_offer",
        lambda **_kwargs: False,
    )
    seen: Dict[str, Any] = {}

    def _query_offers(query_spec: Any, *_args: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        """Capture call kwargs and return the canned offer."""
        seen["query"] = query_spec
        seen["kwargs"] = dict(kwargs)
        return [_offer()]

    from azure.cosmos._backend.legacy import LEGACY_BACKEND

    database = _sync_database(LEGACY_BACKEND, QueryOffers=_query_offers)

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
        "azure.cosmos._helpers._database_throughput.can_use_rust_backend_for_replace_throughput",
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
        "azure.cosmos._helpers._database_throughput.can_use_rust_backend_for_replace_throughput",
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
        "azure.cosmos._helpers._database_throughput.can_use_rust_backend_for_read_offer",
        lambda **_kwargs: True,
    )
    database = _sync_database(_Backend(offers=[]))

    with pytest.raises(exceptions.CosmosResourceNotFoundError) as caught:
        database.get_throughput()

    assert "Could not find ThroughputProperties for database dbs/db" in caught.value.message


def test_sync_replace_throughput_raises_when_no_offer_exists(monkeypatch: pytest.MonkeyPatch) -> None:
    """Missing offer stops the replacement before it attempts a write."""
    monkeypatch.setattr(
        "azure.cosmos._helpers._database_throughput.can_use_rust_backend_for_replace_throughput",
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
        "azure.cosmos._helpers._database_throughput.can_use_rust_backend_for_replace_throughput",
        lambda **_kwargs: True,
    )
    database = _async_database(_AsyncBackend(offers=[]))

    with pytest.raises(exceptions.CosmosResourceNotFoundError) as caught:
        asyncio.run(database.replace_throughput(500))

    assert "Could not find Offer for database dbs/db" in caught.value.message


# --- async-specific regression cases --------------------------------------


def test_async_explicit_legacy_get_throughput_preserves_options(monkeypatch: pytest.MonkeyPatch) -> None:
    """The separately selected legacy Python path remains available for comparison."""
    monkeypatch.setattr(
        "azure.cosmos._helpers._database_throughput.can_use_rust_backend_for_read_offer",
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

    from azure.cosmos.aio._backend.legacy import ASYNC_LEGACY_BACKEND

    database = _async_database(ASYNC_LEGACY_BACKEND, QueryOffers=_query_offers)

    result = asyncio.run(database.get_throughput(read_timeout=3))

    assert result.offer_throughput == 400
    assert seen["kwargs"]["read_timeout"] == 3
    # The database link selects its throughput offer.
    assert seen["query"]["parameters"][0]["value"] == "dbs/db/"


def test_async_get_throughput_raises_when_no_offer_exists(monkeypatch: pytest.MonkeyPatch) -> None:
    """An async read uses the stable typed error and message for no throughput."""
    monkeypatch.setattr(
        "azure.cosmos._helpers._database_throughput.can_use_rust_backend_for_read_offer",
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
        "azure.cosmos._helpers._database_throughput.can_use_rust_backend_for_replace_throughput",
        lambda **_kwargs: True,
    )
    backend = _AsyncBackend(offers=[])
    database = _async_database(backend)

    with pytest.raises(exceptions.CosmosResourceNotFoundError):
        asyncio.run(database.replace_throughput(500))

    assert backend.calls == ["read_offer"]
