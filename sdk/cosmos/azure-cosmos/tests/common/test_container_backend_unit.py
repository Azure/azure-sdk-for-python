# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit coverage for container backend routing (no network).

Three of ``DatabaseProxy``'s container methods land here. ``create_container``
sends one request. ``list_containers`` and ``query_containers`` each return a
feed, one page at a time.

What these protect, and the customer behavior behind each:

* the request the rust engine is handed. A container create is scoped to a
  database, not to a container -- the container does not exist yet -- so the
  database name rides in ``item_id`` and the definition the caller assembled
  rides in the body. Get either wrong and the container is created in the wrong
  database or with the wrong policies.
* the feed pages carrying the owning database. ``PreparedQuery`` has no field for
  a database name, so the ``dbs/{id}`` link rides in ``container_link``. If the
  path cannot be parsed the gate must say no, so the call stays on the legacy
  path instead of running against nothing.
* the ``DocumentCollections`` envelope. The legacy reader pulls containers out of
  that key; a database feed uses ``Databases``. Getting it wrong yields a
  silently empty list rather than an error, which is the worst kind of wrong.
* routing away from rust when rust cannot honor an option exactly -- a
  sub-second ``timeout``, a socket-level ``read_timeout``, a query in the
  legacy-only string form that goes on the wire as ``text/plain``.
* the four ``DeprecationWarning``s ``create_container`` raises for options it
  says it ignores. Those fire on both engines, and -- matching the released v4
  SDK -- the options are still forwarded to ``build_options``, so what goes on
  the wire is unchanged by the migration.

All fakes, no Cosmos account.
"""

from __future__ import annotations

import asyncio
import json
import warnings
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos import _base as base
from azure.cosmos import http_constants
from azure.cosmos._backend.base import (
    BackendResponse,
    CosmosBackend,
    QueryPage,
    OP_CREATE_CONTAINER,
    OP_LIST_CONTAINERS,
    OP_READ_CONTAINER,
    OP_QUERY_CONTAINERS,
    OP_TO_BINDING_METHOD,
    QUERY_TO_BINDING_METHOD,
)
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._cosmos_responses import CosmosDict
from azure.cosmos._helpers._request_prep import (
    build_create_container_prepared,
    build_read_container_prepared,
    is_create_container_rust_eligible,
    is_read_container_rust_eligible,
)
from azure.cosmos._helpers.container_helper import ContainerHelper
from azure.cosmos._query_rust_routing import (
    build_list_containers_prepared_query,
    build_query_containers_prepared_query,
    can_use_rust_backend_for_list_containers_page,
    can_use_rust_backend_for_query_containers_page,
)
from azure.cosmos.aio._helpers.container_helper import AsyncContainerHelper
from azure.cosmos.aio._backend.base import AsyncCosmosBackend
from azure.cosmos.aio._cosmos_client_connection_async import (
    CosmosClientConnection as AsyncConnection,
)
from azure.cosmos._cosmos_client_connection import (
    CosmosClientConnection as SyncConnection,
)
from azure.cosmos.documents import ConnectionPolicy


_COLLECTION = http_constants.ResourceType.Collection


def _created_container_response() -> BackendResponse:
    """Return a canned 201 Created reply carrying a new container body and a request-charge header."""
    # A canned "201 Created" reply: the new container's body plus a
    # request-charge header, used by the fake backends below.
    return BackendResponse(
        status_code=201,
        headers=CaseInsensitiveDict({"x-ms-request-charge": "5.25"}),
        body=b'{"id":"c1","_rid":"rid1"}',
    )


class _RustBackend(CosmosBackend):
    """Stand-in rust backend: records the request it was handed and returns a
    canned reply, so a test can check what would have gone on the wire."""
    name = "rust"

    def __init__(self, response=None):
        """Store an optional canned reply; default to a 201 Created container response."""
        self.response = response or _created_container_response()
        self.prepared = None

    def execute(self, prepared):
        """Record the prepared request and return the canned reply."""
        self.prepared = prepared
        return self.response


class _AsyncRustBackend(AsyncCosmosBackend):
    """Async stand-in rust backend: records the request it was handed and returns
    a canned reply.

    Subclasses the real ``AsyncCosmosBackend`` and overrides only ``execute``, so
    the engine-selection and legacy-fallback logic under test is the shipping one
    rather than a copy of it that could drift.
    """
    name = "rust"

    def __init__(self, response=None):
        """Store an optional canned reply; default to a 201 Created container response."""
        self.response = response or _created_container_response()
        self.prepared = None

    async def execute(self, prepared):
        """Record the prepared request and return the canned reply."""
        self.prepared = prepared
        return self.response


# --- dispatch registration ------------------------------------------------


def test_create_container_is_a_single_response_operation():
    """One create, one reply: it dispatches through ``execute``, not the paged path."""
    assert OP_TO_BINDING_METHOD[OP_CREATE_CONTAINER] == "create_container"
    assert OP_CREATE_CONTAINER not in QUERY_TO_BINDING_METHOD


def test_container_feeds_are_paged_operations():
    """Both feeds dispatch through ``execute_pages``, never the single-reply path."""
    assert QUERY_TO_BINDING_METHOD[OP_LIST_CONTAINERS] == "list_containers"
    assert QUERY_TO_BINDING_METHOD[OP_QUERY_CONTAINERS] == "query_containers"
    assert OP_LIST_CONTAINERS not in OP_TO_BINDING_METHOD
    assert OP_QUERY_CONTAINERS not in OP_TO_BINDING_METHOD


# --- create_container request shape --------------------------------------


def test_create_container_prepared_names_the_database_and_carries_the_definition():
    """The database name rides in ``item_id`` because the container has no id yet,
    and the whole definition -- partition key, indexing policy, TTL -- rides in the
    body. Scope is account-shaped: empty container link, ``"[]"`` partition header."""
    definition = {
        "id": "c1",
        "partitionKey": {"paths": ["/pk"], "kind": "Hash"},
        "defaultTtl": 60,
    }
    prepared = build_create_container_prepared(
        "dbs/db1",
        definition,
        {"offerThroughput": 400, "initialHeaders": {"x-custom": "value"}},
        kwargs={"timeout": 3.5},
    )

    assert prepared.op == OP_CREATE_CONTAINER
    assert prepared.item_id == "db1"
    assert prepared.container_link == ""
    assert prepared.partition_key_header == "[]"
    assert json.loads(prepared.body_bytes) == definition
    assert prepared.headers["offerThroughput"] == 400
    assert prepared.headers["initialHeaders"] == {"x-custom": "value"}
    assert prepared.headers[Constants.OVERALL_TIMEOUT_SECONDS] == 3.5


def test_create_container_prepared_drops_the_session_token():
    """A collection is a master resource, so the legacy path never attaches a
    session token to this request either. Leaving one in would send a token the
    other engine does not send."""
    prepared = build_create_container_prepared(
        "dbs/db1",
        {"id": "c1"},
        {"sessionToken": "s1", "offerThroughput": 400},
    )

    assert "sessionToken" not in prepared.headers
    assert prepared.headers["offerThroughput"] == 400


def test_create_container_prepared_rejects_a_link_with_no_database():
    """A link with the prefix but no name would otherwise create the container in a
    database literally named ``dbs``."""
    with pytest.raises(ValueError):
        build_create_container_prepared("dbs/", {"id": "c1"}, {})


def test_create_container_prepared_drops_a_null_initial_headers():
    """``create_container_if_not_exists`` forwards ``initial_headers=None`` unguarded
    when it falls through to the create, which puts a ``None`` in the options. That
    is not a header value -- copying it through makes the binding reject the whole
    request with a type error, so a customer who never passed any headers cannot
    create a container at all."""
    prepared = build_create_container_prepared(
        "dbs/db1",
        {"id": "c1"},
        {"initialHeaders": None, "offerThroughput": 400},
    )

    assert "initialHeaders" not in prepared.headers
    assert prepared.headers["offerThroughput"] == 400


def test_list_containers_sends_no_query_body():
    """A read feed has no SQL. The page adapter refuses a feed op that is not on its
    parameterless list, so leaving ``list_containers`` off it makes every
    ``list_containers`` call fail once it reaches the binding."""
    from azure.cosmos._backend.rust import _binding_request_from_page

    request = _binding_request_from_page(
        build_list_containers_prepared_query(
            path="dbs/db1/colls",
            options={},
            req_headers={},
        )
    )

    assert request.body_bytes == b""
    assert request.container_link == "dbs/db1"


def test_query_containers_sends_the_query_body():
    """The query payload must arrive as JSON in ``body_bytes``, not as a URL parameter."""
    from azure.cosmos._backend.rust import _binding_request_from_page

    request = _binding_request_from_page(
        build_query_containers_prepared_query(
            path="dbs/db1/colls",
            query_payload={"query": "SELECT * FROM c"},
            options={},
            req_headers={},
        )
    )

    assert json.loads(request.body_bytes) == {"query": "SELECT * FROM c"}


# --- create_container eligibility ----------------------------------------


def test_create_container_is_rust_eligible_for_a_plain_create():
    """A create with only standard options must be routed to the Rust backend."""
    assert is_create_container_rust_eligible({"offerThroughput": 400}, {"timeout": 3.5}) is True


def test_create_container_is_not_rust_eligible_with_a_read_timeout():
    """A socket-level timeout has no rust equivalent, so the call stays on legacy
    and the customer gets the timeout they asked for."""
    assert is_create_container_rust_eligible({}, {"read_timeout": 2}) is False


def test_create_container_is_not_rust_eligible_with_an_intended_container_rid():
    """``_base.GetHeaders`` emits ``x-ms-cosmos-intended-collection-rid`` for every
    resource type except ``dbs``, which includes this one. The rust path has no
    equivalent, so running it there would drop a header legacy sends."""
    assert is_create_container_rust_eligible({Constants.ContainerRID: "rid1"}, {}) is False


# --- create_container routing --------------------------------------------


def test_sync_create_container_routes_to_rust_and_fires_the_hook_once():
    """The coordinator runs the create through the backend, returns the created
    container, records the response headers, and fires ``response_hook`` once."""
    connection = SimpleNamespace(
        CreateContainer=MagicMock(side_effect=AssertionError("legacy create called")),
        last_response_headers={},
    )
    backend = _RustBackend()
    hooks = []

    result = ContainerHelper(connection, backend).create_container(
        "dbs/db1",
        {"id": "c1"},
        {"offerThroughput": 400},
        response_hook=lambda headers, body: hooks.append((headers, body)),
    )

    assert result["id"] == "c1"
    assert backend.prepared.op == OP_CREATE_CONTAINER
    assert backend.prepared.item_id == "db1"
    connection.CreateContainer.assert_not_called()
    assert connection.last_response_headers["x-ms-request-charge"] == "5.25"
    assert len(hooks) == 1
    assert hooks[0][1] == {"id": "c1", "_rid": "rid1"}


def test_sync_create_container_falls_back_to_legacy_for_a_read_timeout():
    """The legacy call gets the definition and options unchanged, and the hook still
    fires exactly once with the same shape as on the rust path."""
    legacy_headers = CaseInsensitiveDict({"x-ms-request-charge": "1.0"})
    legacy_body = CosmosDict({"id": "c1", "_rid": "legacy"}, response_headers=legacy_headers)
    connection = SimpleNamespace(
        CreateContainer=MagicMock(return_value=legacy_body),
        last_response_headers=legacy_headers,
    )
    hooks = []

    result = ContainerHelper(connection, None).create_container(
        "dbs/db1",
        {"id": "c1"},
        {"offerThroughput": 400},
        response_hook=lambda headers, body: hooks.append((headers, body)),
        kwargs={"read_timeout": 2},
    )

    assert result == legacy_body
    call = connection.CreateContainer.call_args
    assert call.kwargs["database_link"] == "dbs/db1"
    assert call.kwargs["collection"] == {"id": "c1"}
    assert call.kwargs["read_timeout"] == 2
    assert len(hooks) == 1
    assert hooks[0][0] == legacy_headers
    assert hooks[0][1] == legacy_body


def test_async_create_container_routes_to_rust():
    """The async coordinator builds the same request as the sync one. It is separate
    code -- the async backend awaits its request builder -- so it can break alone."""
    connection = SimpleNamespace(
        CreateContainer=MagicMock(side_effect=AssertionError("legacy create called")),
        last_response_headers={},
    )
    backend = _AsyncRustBackend()

    result = asyncio.run(
        AsyncContainerHelper(connection, backend).create_container(
            "dbs/db1",
            {"id": "c1"},
            {"offerThroughput": 400},
        )
    )

    assert result["id"] == "c1"
    assert backend.prepared.op == OP_CREATE_CONTAINER
    assert backend.prepared.item_id == "db1"
    connection.CreateContainer.assert_not_called()


# --- feed request shape ---------------------------------------------------


def test_list_containers_prepared_carries_the_owning_database_link():
    """``container_link`` holds a database link, not a container link: the feed is
    scoped to a database and this is the only typed field that can carry it."""
    path = base.GetPathFromLink("dbs/db1", _COLLECTION)
    prepared = build_list_containers_prepared_query(
        path=path,
        options={"maxItemCount": 10, "continuation": "ct-1"},
        req_headers={},
    )

    assert prepared.op == OP_LIST_CONTAINERS
    assert prepared.container_link == "dbs/db1"
    assert prepared.max_item_count == 10
    assert prepared.continuation == "ct-1"
    assert prepared.query is None


def test_query_containers_prepared_carries_the_query_and_the_database_link():
    """The prepared query must name the owning database and carry the full query string and parameters."""
    path = base.GetPathFromLink("dbs/db1", _COLLECTION)
    prepared = build_query_containers_prepared_query(
        path=path,
        query_payload={
            "query": "SELECT * FROM c WHERE c.id=@id",
            "parameters": [{"name": "@id", "value": "c1"}],
        },
        options={},
        req_headers={},
    )

    assert prepared.op == OP_QUERY_CONTAINERS
    assert prepared.container_link == "dbs/db1"
    assert prepared.query == "SELECT * FROM c WHERE c.id=@id"
    assert prepared.parameters == ({"name": "@id", "value": "c1"},)


def test_container_feed_headers_keep_the_customers_own_headers():
    """A plain header the customer set survives into the nested ``initialHeaders``
    entry the binding forwards verbatim. Left flat it would be dropped by the
    option-key translation on the rust side."""
    path = base.GetPathFromLink("dbs/db1", _COLLECTION)
    prepared = build_list_containers_prepared_query(
        path=path,
        options={"initialHeaders": {"x-custom-tag": "value"}},
        req_headers={"x-custom-tag": "value"},
    )

    assert prepared.headers["initialHeaders"] == {"x-custom-tag": "value"}


# --- feed eligibility -----------------------------------------------------


def _list_gate(path="dbs/db1/colls", options=None, kwargs=None, resource_type=_COLLECTION):
    """Thin wrapper over ``can_use_rust_backend_for_list_containers_page`` so test cases read cleanly."""
    return can_use_rust_backend_for_list_containers_page(
        path=path,
        options=options or {},
        kwargs=kwargs or {},
        is_query_plan=False,
        resource_type=resource_type,
    )


def test_list_containers_page_is_rust_eligible_for_a_plain_feed():
    """A feed page with no special options must be eligible for the Rust backend."""
    assert _list_gate() is True


def test_list_containers_page_is_not_eligible_when_the_path_names_no_database():
    """Without a database name the rust page has nothing to run against, so the call
    belongs on legacy rather than failing."""
    assert _list_gate(path="dbs//colls") is False
    assert _list_gate(path="dbs/db1/docs") is False


def test_list_containers_page_is_not_eligible_for_another_resource_type():
    """The database and item feeds have their own gates and their own binding entry
    points; this one must not claim them."""
    assert _list_gate(resource_type=http_constants.ResourceType.Database) is False


def test_list_containers_page_is_not_eligible_with_a_read_timeout():
    """A socket-level timeout or sub-second timeout must stay on the legacy path."""
    assert _list_gate(kwargs={"read_timeout": 2}) is False
    assert _list_gate(options={Constants.Kwargs.TIMEOUT: 0.5}) is False


def test_query_containers_page_is_rust_eligible_for_a_dict_query():
    """A dict-form query (``application/query+json``) must be routed to the Rust backend."""
    assert can_use_rust_backend_for_query_containers_page(
        path="dbs/db1/colls",
        query_payload={"query": "SELECT * FROM c"},
        options={},
        kwargs={},
        is_query_plan=False,
        resource_type=_COLLECTION,
    ) is True


def test_query_containers_page_is_not_eligible_for_a_string_query():
    """The legacy-only SqlQuery mode posts a bare string as ``text/plain`` while the
    driver always posts ``application/query+json``. Different bytes on the wire, so
    that case stays on legacy."""
    assert can_use_rust_backend_for_query_containers_page(
        path="dbs/db1/colls",
        query_payload="SELECT * FROM c",
        options={},
        kwargs={},
        is_query_plan=False,
        resource_type=_COLLECTION,
    ) is False


def test_query_containers_page_is_not_eligible_for_a_query_plan():
    """A query-plan request must stay on legacy; Rust has no query-plan endpoint for containers."""
    assert can_use_rust_backend_for_query_containers_page(
        path="dbs/db1/colls",
        query_payload={"query": "SELECT * FROM c"},
        options={},
        kwargs={},
        is_query_plan=True,
        resource_type=_COLLECTION,
    ) is False


# --- public method behavior ----------------------------------------------


def test_create_container_warns_and_forwards_the_options_it_says_it_ignores():
    """``session_token``, ``etag`` and ``match_condition`` each raise a warning, and --
    exactly as in the released v4 SDK -- are still forwarded to ``build_options``
    rather than dropped. Dropping them here would change what goes on the wire
    relative to core python, which is the one thing this migration must not do:
    ``match_condition`` still has to produce an ``accessCondition``, and the
    leftover kwargs still have to decide the engine."""
    from azure.core import MatchConditions
    from azure.cosmos.database import DatabaseProxy
    from azure.cosmos.partition_key import PartitionKey

    captured = {}

    def fake_create_container(self, database_link, definition, request_options, *, response_hook=None, kwargs=None):
        """Capture the arguments so the test can inspect what the public method forwarded."""
        captured["kwargs"] = dict(kwargs or {})
        captured["request_options"] = dict(request_options or {})
        captured["definition"] = definition
        return {"id": "c1"}

    connection = SimpleNamespace(
        _get_database_link=lambda proxy: "dbs/db1",
        _set_container_properties_cache=lambda link, properties: None,
        last_response_headers={},
    )
    proxy = DatabaseProxy(connection, "db1")

    original = ContainerHelper.create_container
    ContainerHelper.create_container = fake_create_container
    try:
        with warnings.catch_warnings(record=True) as raised:
            warnings.simplefilter("always")
            proxy.create_container(
                "c1",
                PartitionKey(path="/pk"),
                session_token="s1",
                etag="e1",
                match_condition=MatchConditions.IfNotModified,
            )
    finally:
        ContainerHelper.create_container = original

    messages = [str(w.message) for w in raised]
    assert any("session_token" in m for m in messages)
    assert any("etag" in m for m in messages)
    assert any("match_condition" in m for m in messages)
    # build_options consumed all three: etag/match_condition became an
    # accessCondition and session_token became sessionToken, and none of them is
    # left over as a stray kwarg.
    assert captured["request_options"]["accessCondition"] == {"type": "IfMatch", "condition": "e1"}
    assert captured["request_options"]["sessionToken"] == "s1"
    assert "session_token" not in captured["kwargs"]
    assert "etag" not in captured["kwargs"]
    assert "match_condition" not in captured["kwargs"]
    assert captured["definition"]["id"] == "c1"


def test_create_container_still_rejects_an_etag_without_a_match_condition():
    """v4 raises ``ValueError`` here. Swallowing it -- by popping ``etag`` before
    ``build_options`` -- would silently send an unconditional create for a caller who
    asked for a conditional one."""
    from azure.cosmos.database import DatabaseProxy
    from azure.cosmos.partition_key import PartitionKey

    connection = SimpleNamespace(
        _get_database_link=lambda proxy: "dbs/db1",
        _set_container_properties_cache=lambda link, properties: None,
        last_response_headers={},
    )
    proxy = DatabaseProxy(connection, "db1")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with pytest.raises(ValueError, match="'etag' specified without 'match_condition'"):
            proxy.create_container("c1", PartitionKey(path="/pk"), etag="e1")


# --- end-to-end feed dispatch --------------------------------------------
#
# The gates and builders above are only half of it. The other half is the
# dispatch inside the client connection that picks them: it tells a container
# feed apart from a database feed and an item feed by resource type alone, and a
# wrong arm there sends the call to the wrong binding entry point. These drive
# the real dispatch with a fake backend.


class _CapturingPagedBackend(CosmosBackend):
    """Records the paged request it was handed and yields one canned page."""

    def __init__(self, body: bytes) -> None:
        """Store the canned page body to yield and a slot to capture the prepared request."""
        self.body = body
        self.prepared = None

    def execute_pages(self, prepared):
        """Record the prepared query and yield one canned page."""
        self.prepared = prepared
        yield QueryPage(
            status_code=200,
            continuation=None,
            headers=CaseInsensitiveDict({"x-ms-request-charge": "2.0"}),
            body=self.body,
        )

    def execute(self, prepared):
        """Fail immediately — a paged backend must never be called through the single-reply path."""
        raise AssertionError("a feed must not dispatch through the single-reply path")


class _CapturingAsyncPagedBackend(AsyncCosmosBackend):
    """Record the page request produced by asynchronous container methods."""

    def __init__(self, body: bytes) -> None:
        """Store the canned page body and a slot to capture the prepared request."""
        self.body = body
        self.prepared = None

    async def execute_pages(self, prepared):
        """Record the prepared query and yield one canned page."""
        self.prepared = prepared
        yield QueryPage(
            status_code=200,
            continuation=None,
            headers=CaseInsensitiveDict({"x-ms-request-charge": "2.0"}),
            body=self.body,
        )

    async def execute(self, prepared):
        """Fail immediately — a paged backend must never be called through the single-reply path."""
        raise AssertionError("a feed must not dispatch through the single-reply path")


def _new_sync_connection() -> SyncConnection:
    """Build a minimal ``SyncConnection`` with no live transport, for dispatch tests."""
    conn = SyncConnection.__new__(SyncConnection)
    conn._backend = None
    conn._query_compatibility_mode = SyncConnection._QueryCompatibilityMode.Query
    conn.default_headers = {}
    conn.connection_policy = ConnectionPolicy()
    conn._global_endpoint_manager = MagicMock()
    conn._routing_map_provider = MagicMock()
    conn.pipeline_client = MagicMock()
    conn._CosmosClientConnection__container_properties_cache = {}
    conn.last_response_headers = CaseInsensitiveDict()
    conn.session = None
    conn.UseMultipleWriteLocations = False
    conn.master_key = None
    conn.resource_tokens = None
    conn.aad_credentials = None
    conn.client_id = None
    conn.availability_strategy = None
    conn.availability_strategy_executor = None
    return conn


def _new_async_connection() -> AsyncConnection:
    """Build a minimal ``AsyncConnection`` with no live transport, for dispatch tests."""
    conn = AsyncConnection.__new__(AsyncConnection)
    conn._backend = None
    conn._query_compatibility_mode = AsyncConnection._QueryCompatibilityMode.Query
    conn.default_headers = {}
    conn.connection_policy = ConnectionPolicy()
    conn._global_endpoint_manager = MagicMock()
    conn._routing_map_provider = MagicMock()
    conn.pipeline_client = MagicMock()
    conn._CosmosClientConnection__container_properties_cache = {}
    conn.last_response_headers = CaseInsensitiveDict()
    conn.session = None
    conn.UseMultipleWriteLocations = False
    conn.master_key = None
    conn.resource_tokens = None
    conn.aad_credentials = None
    conn.client_id = None
    conn.availability_strategy = None
    conn.availability_strategy_max_concurrency = None
    return conn


_CONTAINER_PAGE = b'{"DocumentCollections":[{"id":"c1"},{"id":"c2"}]}'


def test_sync_list_containers_dispatches_to_the_container_feed():
    """The read-feed arm keyed on ``Collection`` builds a container page carrying
    the owning database, and the containers come back out of the
    ``DocumentCollections`` envelope. A database feed uses ``Databases``; reading
    the wrong key yields an empty list instead of an error."""
    conn = _new_sync_connection()
    backend = _CapturingPagedBackend(_CONTAINER_PAGE)
    conn._backend = backend

    result, _headers = conn._CosmosClientConnection__QueryFeed(
        "/dbs/db1/colls/",
        _COLLECTION,
        "db1",
        lambda payload: payload["DocumentCollections"],
        lambda _connection, body: body,
        None,
        {},
    )

    assert backend.prepared.op == OP_LIST_CONTAINERS
    assert backend.prepared.container_link == "dbs/db1"
    assert [c["id"] for c in result] == ["c1", "c2"]


def test_sync_query_containers_dispatches_to_the_container_query_feed():
    """The query arm keys on ``Collection`` and a query payload, producing a ``OP_QUERY_CONTAINERS`` request."""
    conn = _new_sync_connection()
    backend = _CapturingPagedBackend(_CONTAINER_PAGE)
    conn._backend = backend

    result, _headers = conn._CosmosClientConnection__QueryFeed(
        "/dbs/db1/colls/",
        _COLLECTION,
        "db1",
        lambda payload: payload["DocumentCollections"],
        lambda _connection, body: body,
        {"query": "SELECT * FROM c"},
        {},
    )

    assert backend.prepared.op == OP_QUERY_CONTAINERS
    assert backend.prepared.container_link == "dbs/db1"
    assert backend.prepared.query == "SELECT * FROM c"
    assert [c["id"] for c in result] == ["c1", "c2"]


def test_async_list_containers_dispatches_to_the_container_feed():
    """The async dispatch is separate code with its own arm, so it can break alone."""
    async def _run():
        """Drive the async dispatch arm for a list feed so it can be verified independently."""
        conn = _new_async_connection()
        backend = _CapturingAsyncPagedBackend(_CONTAINER_PAGE)
        conn._backend = backend

        result = await conn._CosmosClientConnection__QueryFeed(
            "/dbs/db1/colls/",
            _COLLECTION,
            "db1",
            lambda payload: payload["DocumentCollections"],
            lambda _connection, body: body,
            None,
            {},
        )

        assert backend.prepared.op == OP_LIST_CONTAINERS
        assert backend.prepared.container_link == "dbs/db1"
        assert [c["id"] for c in result] == ["c1", "c2"]

    asyncio.run(_run())


def test_async_query_containers_dispatches_to_the_container_query_feed():
    """The async query arm builds an ``OP_QUERY_CONTAINERS`` request, separate from the list arm."""
    async def _run():
        """Drive the async dispatch for a query feed."""
        conn = _new_async_connection()
        backend = _CapturingAsyncPagedBackend(_CONTAINER_PAGE)
        conn._backend = backend

        result = await conn._CosmosClientConnection__QueryFeed(
            "/dbs/db1/colls/",
            _COLLECTION,
            "db1",
            lambda payload: payload["DocumentCollections"],
            lambda _connection, body: body,
            {"query": "SELECT * FROM c"},
            {},
        )

        assert backend.prepared.op == OP_QUERY_CONTAINERS
        assert backend.prepared.query == "SELECT * FROM c"
        assert [c["id"] for c in result] == ["c1", "c2"]

    asyncio.run(_run())


# --- container read -------------------------------------------------------


def _read_container_response() -> BackendResponse:
    """Return a canned 200 OK reply carrying a container body with a partition key."""
    return BackendResponse(
        status_code=200,
        headers=CaseInsensitiveDict({"x-ms-request-charge": "1.0"}),
        body=b'{"id":"c1","_rid":"rid1","partitionKey":{"paths":["/pk"],"kind":"Hash"}}',
    )


def test_read_container_prepared_carries_both_names():
    """The driver reads a container by name, so the request has to name the database
    and the container. Both come out of the one link the proxy holds."""
    prepared = build_read_container_prepared("dbs/db1/colls/c1", {})

    assert prepared.op == OP_READ_CONTAINER
    assert prepared.container_link == "dbs/db1/colls/c1"


def test_read_container_prepared_accepts_a_link_with_slashes():
    """Leading and trailing slashes in the link must be stripped before the request is built."""
    prepared = build_read_container_prepared("/dbs/db1/colls/c1/", {})

    assert prepared.container_link == "dbs/db1/colls/c1"


@pytest.mark.parametrize(
    "link",
    ["dbs/db1", "dbs/db1/colls", "dbs/db1/colls/", "dbs//colls/c1", "colls/c1"],
)
def test_read_container_prepared_rejects_a_link_missing_either_name(link):
    """A half-formed link would reach the service as a request for a container
    literally named ``colls``, and the not-found that came back would say nothing
    about the real problem."""
    with pytest.raises(ValueError):
        build_read_container_prepared(link, {})


def test_read_container_prepared_drops_the_session_token():
    """A container is a master resource, so neither engine sends a session token on
    this read. Sending one on rust only would be a difference between the two."""
    prepared = build_read_container_prepared(
        "dbs/db1/colls/c1",
        {"sessionToken": "0:1#22"},
    )

    assert "sessionToken" not in prepared.headers


def test_read_container_is_rust_eligible_for_a_plain_read():
    """A read with no special options must be eligible for the Rust backend."""
    assert is_read_container_rust_eligible({}, {}) is True


@pytest.mark.parametrize(
    "option",
    ["populatePartitionKeyRangeStatistics", "populateQuotaInfo"],
)
def test_read_container_is_not_rust_eligible_when_statistics_were_asked_for(option):
    """The legacy path turns each of these into a response header the rust path has
    no way to request. A customer who asked for statistics and got a reply without
    them would read that as "this container has none"."""
    assert is_read_container_rust_eligible({option: True}, {}) is False


def test_sync_read_container_routes_to_rust_and_fires_the_hook_once():
    """The helper must use Rust, return the container, and fire ``response_hook`` exactly once."""
    connection = SimpleNamespace(
        ReadContainer=MagicMock(side_effect=AssertionError("legacy read called")),
        last_response_headers={},
    )
    backend = _RustBackend(_read_container_response())
    hooks = []

    result = ContainerHelper(connection, backend).read_container(
        "dbs/db1/colls/c1",
        {},
        response_hook=lambda headers, body: hooks.append((headers, body)),
    )

    assert result["id"] == "c1"
    assert backend.prepared.op == OP_READ_CONTAINER
    connection.ReadContainer.assert_not_called()
    assert connection.last_response_headers["x-ms-request-charge"] == "1.0"
    assert len(hooks) == 1


def test_sync_read_container_falls_back_to_legacy_for_a_read_timeout():
    """A socket-level timeout must be honored via the legacy path, not silently dropped by Rust."""
    legacy_headers = CaseInsensitiveDict({"x-ms-request-charge": "1.0"})
    legacy_body = CosmosDict({"id": "c1", "_rid": "legacy"}, response_headers=legacy_headers)
    connection = SimpleNamespace(
        ReadContainer=MagicMock(return_value=legacy_body),
        last_response_headers=legacy_headers,
    )
    hooks = []

    result = ContainerHelper(connection, None).read_container(
        "dbs/db1/colls/c1",
        {},
        response_hook=lambda headers, body: hooks.append((headers, body)),
        kwargs={"read_timeout": 2},
    )

    assert result == legacy_body
    call = connection.ReadContainer.call_args
    assert call.args[0] == "dbs/db1/colls/c1"
    assert call.kwargs["read_timeout"] == 2
    assert len(hooks) == 1


def test_read_container_does_not_pass_the_hook_to_the_legacy_call():
    """The helper owns the hook on both engines: it strips ``response_hook`` from the
    kwargs it forwards, so the legacy pipeline cannot fire it a second time."""
    legacy_body = CosmosDict({"id": "c1"}, response_headers=CaseInsensitiveDict())
    connection = SimpleNamespace(
        ReadContainer=MagicMock(return_value=legacy_body),
        last_response_headers={},
    )
    hooks = []

    ContainerHelper(connection, None).read_container(
        "dbs/db1/colls/c1",
        {},
        response_hook=lambda headers, body: hooks.append(body),
        kwargs={"read_timeout": 2, "response_hook": lambda *a: hooks.append("legacy")},
    )

    assert "response_hook" not in connection.ReadContainer.call_args.kwargs
    assert hooks == [{"id": "c1"}]


def test_async_read_container_routes_to_rust():
    """Async read must use the Rust backend without falling through to the legacy path."""
    connection = SimpleNamespace(
        ReadContainer=MagicMock(side_effect=AssertionError("legacy read called")),
        last_response_headers={},
    )
    backend = _AsyncRustBackend(_read_container_response())

    result = asyncio.run(
        AsyncContainerHelper(connection, backend).read_container(
            "dbs/db1/colls/c1",
            {},
        )
    )

    assert result["id"] == "c1"
    assert backend.prepared.op == OP_READ_CONTAINER
    connection.ReadContainer.assert_not_called()


# --- async legacy fallback -------------------------------------------------
#
# ``AsyncContainerHelper`` is a separate module from the sync helper: it awaits
# its request builder and its legacy call. The rust-path tests above prove the
# request it builds; these prove the other branch -- that an option rust cannot
# honor still reaches the legacy call, and that the hook fires exactly once with
# the response's own headers on that branch too. Without them the async legacy
# arm is the one code path in this family with no coverage at all.


def test_async_create_container_falls_back_to_legacy_for_a_read_timeout():
    """Async create with ``read_timeout`` must reach the legacy path with the kwarg intact."""
    legacy_headers = CaseInsensitiveDict({"x-ms-request-charge": "1.0"})
    legacy_body = CosmosDict({"id": "c1", "_rid": "legacy"}, response_headers=legacy_headers)
    connection = SimpleNamespace(
        CreateContainer=AsyncMock(return_value=legacy_body),
        last_response_headers=legacy_headers,
    )
    hooks = []

    result = asyncio.run(
        AsyncContainerHelper(connection, _AsyncRustBackend()).create_container(
            "dbs/db1",
            {"id": "c1"},
            {"offerThroughput": 400},
            response_hook=lambda headers, body: hooks.append((headers, body)),
            kwargs={"read_timeout": 2},
        )
    )

    assert result == legacy_body
    call = connection.CreateContainer.call_args
    assert call.kwargs["database_link"] == "dbs/db1"
    assert call.kwargs["collection"] == {"id": "c1"}
    assert call.kwargs["options"] == {"offerThroughput": 400}
    assert call.kwargs["read_timeout"] == 2
    assert "response_hook" not in call.kwargs
    assert len(hooks) == 1
    assert hooks[0][0] == legacy_headers
    assert hooks[0][1] == legacy_body


def test_async_read_container_falls_back_to_legacy_for_a_read_timeout():
    """Async read with ``read_timeout`` must not strip the hook or fire it twice."""
    legacy_headers = CaseInsensitiveDict({"x-ms-request-charge": "1.0"})
    legacy_body = CosmosDict({"id": "c1", "_rid": "legacy"}, response_headers=legacy_headers)
    connection = SimpleNamespace(
        ReadContainer=AsyncMock(return_value=legacy_body),
        last_response_headers=legacy_headers,
    )
    hooks = []

    result = asyncio.run(
        AsyncContainerHelper(connection, _AsyncRustBackend()).read_container(
            "dbs/db1/colls/c1",
            {},
            response_hook=lambda headers, body: hooks.append((headers, body)),
            kwargs={"read_timeout": 2, "response_hook": lambda *a: hooks.append("legacy")},
        )
    )

    assert result == legacy_body
    call = connection.ReadContainer.call_args
    assert call.args[0] == "dbs/db1/colls/c1"
    assert call.kwargs["read_timeout"] == 2
    # The helper owns the hook, so the legacy pipeline must not get a copy and
    # fire it a second time.
    assert "response_hook" not in call.kwargs
    assert len(hooks) == 1
    assert hooks[0][0] == legacy_headers


def test_async_create_container_fires_the_hook_once_on_the_rust_path():
    """The async Rust create calls the customer's response hook exactly once."""
    connection = SimpleNamespace(
        CreateContainer=AsyncMock(side_effect=AssertionError("legacy create called")),
        last_response_headers={},
    )
    hooks = []

    result = asyncio.run(
        AsyncContainerHelper(connection, _AsyncRustBackend()).create_container(
            "dbs/db1",
            {"id": "c1"},
            {},
            response_hook=lambda headers, body: hooks.append((headers, body)),
        )
    )

    assert len(hooks) == 1
    assert hooks[0][1] is result
    assert hooks[0][0] == result.get_response_headers()
    connection.CreateContainer.assert_not_called()


def test_async_read_container_fires_the_hook_once_on_the_rust_path():
    """Async Rust read must fire the customer's response hook exactly once with the real headers."""
    connection = SimpleNamespace(
        ReadContainer=AsyncMock(side_effect=AssertionError("legacy read called")),
        last_response_headers={},
    )
    hooks = []

    result = asyncio.run(
        AsyncContainerHelper(connection, _AsyncRustBackend(_read_container_response())).read_container(
            "dbs/db1/colls/c1",
            {},
            response_hook=lambda headers, body: hooks.append((headers, body)),
        )
    )

    assert len(hooks) == 1
    assert hooks[0][1] is result
    assert hooks[0][0] == result.get_response_headers()
    connection.ReadContainer.assert_not_called()
