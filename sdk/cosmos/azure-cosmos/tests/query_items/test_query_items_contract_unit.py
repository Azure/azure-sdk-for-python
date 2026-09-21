# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Query contract: continuation tokens, scope, and per-page budgets, with no service calls.

``query_items`` returns a lazy pager. Nothing is sent until it is iterated,
and each page is fetched through the compiled driver behind a fake binding.

The recurring themes:

* **Laziness and per-iterator state.** Building a pager snapshots its query
  but does not acquire a driver or native cursor. Two page iterators from the same
  pager are independent and each gets its own cursor, released when it runs
  out.
* **Continuation tokens are bound to a query.** A token records the endpoint,
  container, query text, parameters, and scope. Resuming with a token issued
  for a *different* query or partition must fail rather than silently return
  someone else's rows. Tokens are also prefixed by kind -- ``q1.`` for public
  query tokens, ``c1.`` for raw driver ones -- so the wrong kind is rejected.
* **Not every query can be resumed.** ``DISTINCT`` and similar queries
  enumerate fine but cannot produce a token, and asking for one says so
  instead of handing back something unusable.
* **One budget per public page**, including driver start-up and any empty
  pages consumed along the way.
* **Execution failures do not replay.** After execution may have started, an
  error leaves the pager failed with its last delivered token. Initial setup
  service errors can be retried when the binding confirms execution never began.

Results are not always objects: ``SELECT VALUE`` can yield numbers, nulls,
lists and strings, so the tests check scalars survive the trip.
"""
from common.typed_requests import wire_headers, settings_options, legacy_settings

import asyncio
import inspect
import hashlib
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from common.typed_requests import legacy_partition_key_from_request

from azure.cosmos import _operation_deadline
from azure.cosmos._backend import binding as sync_rust
from azure.cosmos.aio._backend import binding as async_rust
from azure.cosmos.container import ContainerProxy
from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy
from azure.cosmos._helpers import _read_all_items
from azure.cosmos._helpers._item_context import ItemClientContext, ItemClientDefaults
from azure.cosmos.exceptions import CosmosClientTimeoutError, CosmosHttpResponseError
from azure.cosmos.partition_key import NonePartitionKeyValue, NullPartitionKeyValue


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def query(request, monkeypatch):
    """Drive the Rust query path against a fake driver, once sync and once async.

    Serves pages from ``context.pages``: one object row, an empty page, a page
    of bare scalars, then ``None`` to signal the end. Each real page reports a
    charge of 2 plus a custom header, so tests can check charges add up and
    unknown headers survive.

    Paging is driven by the continuation header, so resuming really does jump
    the fake feed to the recorded position rather than just replaying.

    Settings a test can set: ``delay`` (time per page), ``status`` (to force a
    service error), ``failure`` (to raise from the fetch), and ``resumable``
    (to model a query that cannot produce continuation tokens).

    Everything above the binding is real -- proxy, backend, pager -- and the
    clock is faked so budgets can be spent without waiting. ``collect`` drains
    a pager and ``next_page`` takes one page, both hiding the sync/async
    difference.
    """
    async_mode = request.param
    clock = SimpleNamespace(now=100.0)
    clock.monotonic = lambda: clock.now
    monkeypatch.setattr(_read_all_items, "time", clock)
    monkeypatch.setattr(_operation_deadline, "time", clock)
    context = SimpleNamespace(
        calls=[],
        async_mode=async_mode,
        clock=clock,
        status=200,
        delay=0,
        resumable=True,
        failure=None,
        setup_status=0,
        pages=[[{"id": "a", "nested": [1]}], [], [7, None, ["value"], "text"], None],
    )

    def cursor():
        return SimpleNamespace(
            index=0, has_more=False, continuation_supported=True, can_retry_setup=True
        )

    def page(handle, prepared, state, *, timeout_seconds=None):
        context.calls.append((prepared, state, timeout_seconds))
        if context.setup_status:
            return context.setup_status, 0, {}, b'{"message":"setup failed"}', None
        state.can_retry_setup = False
        if context.failure:
            raise context.failure
        if timeout_seconds is not None and context.delay > timeout_seconds:
            raise TimeoutError("query page timed out")
        clock.now += context.delay
        token = wire_headers(prepared).get("x-ms-continuation")
        if token is not None:
            state.index = int(token.removeprefix("c1."))
        rows = context.pages[state.index]
        state.index += 1
        state.has_more = rows is not None
        state.continuation_supported = context.resumable
        headers = {}
        if rows is not None:
            headers = {
                "x-ms-request-charge": "2",
                "x-ms-session-token": "session",
                "x-custom": "preserved",
            }
            if context.resumable:
                headers["x-ms-continuation"] = "c1." + str(state.index)
        return (
            context.status,
            0,
            headers,
            json.dumps({"Documents": rows or []}).encode(),
            None,
        )

    module = async_rust if async_mode else sync_rust
    binding = SimpleNamespace(
        _ItemFeedCursor=MagicMock(side_effect=cursor),
        query_items=MagicMock(),
        query_items_async=AsyncMock(),
        fetch_page_with_cursor=MagicMock(side_effect=page),
        fetch_page_with_cursor_async=AsyncMock(side_effect=page),
    )
    monkeypatch.setattr(module, "_rust_module", binding)
    cls = async_rust.AsyncRustBinding if async_mode else sync_rust.RustBinding
    backend = cls("https://queries.invalid", master_key="ZmFrZQ==")
    monkeypatch.setattr(
        backend,
        "_ensure_driver_handle",
        (
            AsyncMock(return_value="handle")
            if async_mode
            else MagicMock(return_value="handle")
        ),
    )
    connection = MagicMock()
    connection._backend = backend
    context.proxy = (AsyncContainerProxy if async_mode else ContainerProxy)(
        connection,
        "dbs/db",
        "c",
        _item_context=ItemClientContext(
            backend, ItemClientDefaults(priority="Low", throughput_bucket=3)
        ),
    )
    context.connection, context.binding, context.backend = connection, binding, backend

    def collect(pager):
        async def run():
            return [row async for row in pager]

        return asyncio.run(run()) if async_mode else list(pager)

    def next_page(pages):
        async def run():
            return [row async for row in await pages.__anext__()]

        return asyncio.run(run()) if async_mode else list(next(pages))

    context.collect, context.next_page = collect, next_page
    yield context
    closed = backend.close()
    if inspect.isawaitable(closed):
        asyncio.run(closed)


@pytest.mark.parametrize("status", [429, 503])
def test_initial_setup_service_error_can_retry_same_page_iterator(query, status):
    hooks = []
    pages = query.proxy.query_items(
        "SELECT * FROM c", response_hook=lambda headers, body: hooks.append(body)
    ).by_page()
    query.setup_status = status
    with pytest.raises(CosmosHttpResponseError) as caught:
        query.next_page(pages)
    assert caught.value.status_code == status
    cursor = pages.state.cursor
    assert cursor is not None and not pages.state.failed
    assert pages.continuation_token is None
    assert hooks == []
    query.setup_status = 0
    assert query.next_page(pages) == [{"id": "a", "nested": [1]}]
    assert query.calls[0][1] is query.calls[1][1] is cursor
    assert len(hooks) == 1


def test_first_execution_service_error_still_invalidates(query):
    query.status = 503
    pages = query.proxy.query_items("SELECT * FROM c").by_page()
    with pytest.raises(CosmosHttpResponseError):
        query.next_page(pages)
    assert pages.state.cursor is None
    with pytest.raises(RuntimeError, match="failed"):
        query.next_page(pages)
    assert len(query.calls) == 1


def test_setup_failure_preserves_input_query_bookmark(query):
    pager = query.proxy.query_items("SELECT * FROM c")
    original = pager.by_page()
    query.next_page(original)
    bookmark = original.continuation_token
    pages = pager.by_page(continuation_token=bookmark)
    query.setup_status = 503
    with pytest.raises(CosmosHttpResponseError) as caught:
        query.next_page(pages)
    assert caught.value.continuation_token == bookmark
    assert pages.continuation_token == bookmark
    cursor = pages.state.cursor
    assert cursor is not None and not pages.state.failed
    query.setup_status = 0
    assert query.next_page(pages) == [7, None, ["value"], "text"]
    assert query.calls[-1][1] is cursor
    assert pages.continuation_token != bookmark


def test_cursor_is_lazy_per_iterator_and_released_at_completion(query):
    """Each page iterator allocates its own cursor on first use and frees it at the end.

    Two page iterators are taken from one pager. Before anything is iterated
    neither has a cursor, and neither the driver handle nor a cursor has been
    created -- building a pager only prepares its Python-side query state.

    Taking a page from each creates exactly two cursors, one per iterator. If
    they shared one, two loops over the same pager would consume each other's
    pages. Each iterator then keeps its own cursor across later pages.

    When the first iterator is exhausted its cursor is released while the
    second's is untouched, and no third cursor is ever created. Releasing at
    the end is what stops long-lived applications from accumulating driver
    state for every query they run.
    """
    pager = query.proxy.query_items("SELECT * FROM c")
    first, second = pager.by_page(), pager.by_page()
    assert first.state.cursor is second.state.cursor is None
    query.binding._ItemFeedCursor.assert_not_called()
    query.backend._ensure_driver_handle.assert_not_called()

    query.next_page(first)
    cursor = first.state.cursor
    query.next_page(second)
    assert second.state.cursor is not cursor
    assert cursor is not None
    assert query.binding._ItemFeedCursor.call_count == 2
    query.next_page(first)
    assert first.state.cursor is cursor
    assert query.calls[-1][1] is cursor
    with pytest.raises((StopIteration, StopAsyncIteration)):
        query.next_page(first)
    assert first.state.cursor is None
    assert second.state.cursor is not None
    assert query.binding._ItemFeedCursor.call_count == 2


@pytest.mark.parametrize("interval", [None, ("00", "FF")])
def test_typed_scope_keeps_the_previous_bookmark_identity(query, interval):
    """The identity behind a continuation token is computed exactly as it always was.

    A token is only accepted if the query it is replayed against hashes to the
    same identity. That hash is rebuilt here by hand from the endpoint,
    container link, query text, parameters and scope, and must match what the
    pager computed -- with and without a feed range.

    This is a compatibility check. The scope is now held in typed form
    internally, but if the hash input changed shape, every continuation token
    a customer had already saved would stop working.

    Computing the identity must also not create a cursor.
    """
    kwargs = (
        {}
        if interval is None
        else {"feed_range": {"Range": {"min": interval[0], "max": interval[1]}}}
    )
    pager = query.proxy.query_items("SELECT * FROM c", **kwargs)
    config = pager.by_page().state.config
    previous_identity_input = [
        query.backend._endpoint,
        query.proxy.container_link,
        "SELECT * FROM c",
        [],
        {
            "feed_range": list(interval) if interval is not None else None,
            "allow_cross_partition": True,
            "partition_key": None,
        },
    ]
    expected = hashlib.sha256(
        json.dumps(
            previous_identity_input,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode()
    ).hexdigest()
    assert config.identity == expected
    assert config.scope.feed_range == interval
    query.binding._ItemFeedCursor.assert_not_called()


def test_complete_iteration_scalar_results_and_no_legacy_metadata(query):
    """A full enumeration returns scalars untouched and never touches the legacy path.

    Nothing is fetched until iteration starts. Draining the pager then returns
    an object followed by bare scalars -- ``7``, ``None``, a list and a string
    -- because ``SELECT VALUE`` can project any JSON value. A ``None`` row in
    particular must survive rather than being read as "no more rows".

    All four fetches share one cursor. Neither the legacy query method, the
    container metadata read, nor the driver's one-shot query entry points are
    used: a plain query pages through the cursor and nothing else.
    """
    pager = query.proxy.query_items("SELECT VALUE c.value FROM c", max_item_count=1)
    assert query.calls == []
    query.binding._ItemFeedCursor.assert_not_called()
    assert query.collect(pager) == [
        {"id": "a", "nested": [1]},
        7,
        None,
        ["value"],
        "text",
    ]
    assert len(query.calls) == 4
    assert len({id(cursor) for _, cursor, _ in query.calls}) == 1
    query.connection.QueryItems.assert_not_called()
    query.connection.ReadContainer.assert_not_called()
    query.binding.query_items.assert_not_called()
    query.binding.query_items_async.assert_not_called()


def test_bookmarks_resume_independently_and_bind_query_and_scope(query):
    """A token resumes a matching query only, and each pager keeps its own position.

    After one page, the token is a public ``q1.`` one. A second pager resumes
    from it and continues correctly even though the connection's shared
    response headers were meanwhile set to an unrelated token, and even though
    the resumed call uses a different page size. The original pager then
    returns the same next page from its own state.

    The two use different cursors; the original keeps the one it started with.

    Resuming is then refused for a different query text, a different partition
    key, and different parameters. All three would otherwise return rows from
    a position that has no meaning for the new query.
    """
    pages = query.proxy.query_items("SELECT * FROM c").by_page()
    assert query.next_page(pages)[0]["id"] == "a"
    bookmark = pages.continuation_token
    assert bookmark.startswith("q1.")
    query.connection.last_response_headers = {"x-ms-continuation": "unrelated"}
    resumed = query.proxy.query_items("SELECT * FROM c", max_item_count=50).by_page(
        continuation_token=bookmark
    )
    assert query.next_page(resumed) == [7, None, ["value"], "text"]
    assert query.next_page(pages) == [7, None, ["value"], "text"]
    assert query.calls[0][1] is not query.calls[1][1]
    assert query.calls[0][1] is query.calls[-1][1]
    for kwargs in [
        {"query": "SELECT c.id FROM c"},
        {"query": "SELECT * FROM c", "partition_key": "other"},
        {"query": "SELECT * FROM c", "parameters": [{"name": "@p", "value": 2}]},
    ]:
        with pytest.raises(ValueError, match="bookmark"):
            query.proxy.query_items(**kwargs).by_page(continuation_token=bookmark)


def test_nonresumable_queries_enumerate_but_bookmark_access_raises(query):
    """A query that cannot be resumed still enumerates fully; only the token is refused.

    Queries like ``DISTINCT`` hold state the service cannot hand back in a
    token. Paging works normally all the way to the end, but asking for the
    continuation token raises ``NotImplementedError``.

    Refusing is the honest answer: returning a token that silently produced
    wrong or duplicate rows on resume would be far worse than an error at the
    point the customer asks for it.
    """
    query.resumable = False
    pages = query.proxy.query_items("SELECT DISTINCT VALUE c.value FROM c").by_page()
    assert query.next_page(pages)[0]["id"] == "a"
    with pytest.raises(NotImplementedError, match="bookmark"):
        _ = pages.continuation_token
    assert query.next_page(pages) == [7, None, ["value"], "text"]
    with pytest.raises((StopIteration, StopAsyncIteration)):
        query.next_page(pages)
    assert len(query.calls) == 4


@pytest.mark.parametrize(
    "key,expected",
    [
        (None, None),
        ("tenant", '["tenant"]'),
        (False, "[false]"),
        (0, "[0]"),
        (NullPartitionKeyValue, "[null]"),
        (NonePartitionKeyValue, "[{}]"),
        (["tenant"], '["tenant"]'),
        (["tenant", None], '["tenant",null]'),
        (["tenant", NonePartitionKeyValue], '["tenant",{}]'),
    ],
)
def test_partition_scope_normalization(query, key, expected):
    """Every shape of partition key turns into the right wire value, and stays out of the body.

    Covers no key at all, a plain string, ``False`` and ``0`` (which must not
    be mistaken for "unset"), explicit null, the "no partition key" marker,
    and hierarchical keys including ones with null or missing components.

    Each becomes its JSON wire form: ``false`` and ``0`` stay themselves,
    null becomes ``[null]``, and the absent-key marker becomes ``[{}]`` --
    two distinct encodings that must not collapse into one.

    The key is also never written into the request body. It belongs in the
    routing header only, and a stray copy in the body would change the query.
    """
    query.collect(query.proxy.query_items("SELECT * FROM c", partition_key=key))
    prepared = query.calls[0][0]
    actual = legacy_partition_key_from_request(prepared) if prepared.partition_key.kind == "components" else None
    assert actual == expected
    assert "partition_key" not in json.loads(prepared.body_bytes)


@pytest.mark.parametrize("key,wire", [
    (None, None), (False, "[false]"), (NonePartitionKeyValue, "[{}]"),
    (NullPartitionKeyValue, "[null]"), (["tenant", None], '["tenant",null]'),
])
def test_existing_query_bookmark_identity_is_unchanged(query, key, wire):
    """Partition keys hash into the token identity exactly as they did before.

    The companion to the scope-identity test, focused on partition keys that
    are easy to get wrong: ``False``, explicit null, the absent-key marker,
    and a hierarchical key with a null component.

    For each, the identity hash is rebuilt from the original scope shape and
    must match. If any of these started hashing differently, saved
    continuation tokens for those partitions would stop being accepted.
    """
    import hashlib
    from azure.cosmos._helpers._query_items import QueryConfig

    config = QueryConfig(query.proxy, {"query": "SELECT * FROM c", "partition_key": key})
    original_scope = {
        "partition_key": wire, "feed_range": None, "allow_cross_partition": True,
    }
    original = json.dumps(
        [config.backend._endpoint, query.proxy.container_link, config.query, config.parameters, original_scope],
        sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()
    assert config.identity == hashlib.sha256(original).hexdigest()


@pytest.mark.parametrize(
    "parameters",
    [
        None,
        [],
        [
            {"name": "@p", "value": {
                "nested": [None, True, False, -2, 0.125, 9007199254740993, "\u4e2d\U0001f600"],
            }},
            {"name": "@second", "value": "parameter order is preserved"},
        ],
    ],
    ids=["omitted", "empty", "nested-values"],
)
def test_query_body_is_serialized_once_and_reused_without_freezing_page_settings(
    query, monkeypatch, parameters
):
    """Cache only the immutable SQL body; continuation and timeout remain per-page."""
    from copy import deepcopy

    from azure.cosmos._backend import _binding_conversions
    from azure.cosmos._helpers import _query_items

    parameters = deepcopy(parameters)
    serialize = MagicMock(wraps=_query_items.serialize_body_to_bytes)
    monkeypatch.setattr(_query_items, "serialize_body_to_bytes", serialize)
    page_serialize = MagicMock(side_effect=AssertionError("Query body was serialized again"))
    monkeypatch.setattr(_binding_conversions, "json", SimpleNamespace(dumps=page_serialize))
    sql = "SELECT VALUE @p"
    expected: dict[str, object] = {"query": sql}
    if parameters:
        expected["parameters"] = deepcopy(parameters)
    query.delay = 0.25
    pager = query.proxy.query_items(
        sql, parameters=parameters, max_item_count=2, timeout=10,
        feed_range={"Range": {"min": "", "max": "AA"}},
    )
    serialize.assert_called_once_with(expected, allow_nan=False)
    if parameters:
        parameters[0]["value"]["nested"].append("changed after pager construction")
    if parameters is not None:
        parameters.append({"name": "@later", "value": "not part of this query"})
    query.collect(pager)

    assert len(query.calls) == 4
    body = query.calls[0][0].body_bytes
    assert json.loads(body) == expected
    assert all(prepared.body_bytes is body for prepared, _, _ in query.calls)
    assert all(prepared.query_scope.feed_range == ("", "AA") for prepared, _, _ in query.calls)
    assert [
        wire_headers(prepared).get("x-ms-continuation")
        for prepared, _, _ in query.calls
    ] == [None, "c1.1", "c1.2", "c1.3"]
    assert all(prepared.settings.query.max_item_count == 2 for prepared, _, _ in query.calls)
    # Fetching past an empty response shares one page budget; delivered pages reset it.
    assert [timeout for _, _, timeout in query.calls] == [10, 10, 9.75, 10]
    serialize.assert_called_once()
    page_serialize.assert_not_called()


@pytest.mark.parametrize("async_mode", [False, True], ids=["sync", "async"])
def test_native_query_accepts_service_body_and_requires_separate_scope(async_mode):
    """Exercise the installed binding without acquiring a driver or sending a request."""
    from dataclasses import replace

    from azure.cosmos._backend.contracts import PreparedQuery, QueryScope

    native = pytest.importorskip("azure.cosmos._rust")
    cursor = native._ItemFeedCursor()
    body = b'{"query":"SELECT VALUE @p","parameters":[{"name":"@p","value":1}]}'
    prepared = PreparedQuery(
        op="query_items", container_link="dbs/db/colls/c",
        query="SELECT VALUE @p", parameters=({"name": "@p", "value": 1},),
        query_body=body, cursor=cursor, query_scope=QueryScope(("", "AA")),
    )
    module = async_rust if async_mode else sync_rust
    request = module.build_binding_request_from_page(prepared)
    dispatch = native.fetch_page_with_cursor_async if async_mode else native.fetch_page_with_cursor
    assert request.body_bytes is body
    with pytest.raises(RuntimeError, match="no driver registered"):
        dispatch("query-body-contract-unregistered", request, cursor)
    with pytest.raises(TypeError, match="typed query_scope"):
        dispatch("query-body-contract-unregistered", replace(request, query_scope=None), cursor)
    with pytest.raises(TypeError, match="typed QueryScope"):
        replace(request, query_scope={"feed_range": ["", "AA"]})
    with pytest.raises(TypeError, match="immutable bytes"):
        replace(prepared, query_body=bytearray(body))


def test_query_body_scope_options_and_client_defaults_are_preserved(query):
    """A fully loaded query is snapshotted at the call and every option lands in the right place.

    The parameters list, feed range and headers are all mutated *after* the
    pager is built but before it is iterated. The request still carries the
    original values, so they were copied at the call rather than read later --
    otherwise a caller reusing a parameters list across queries would corrupt
    requests already in flight.

    Each option then has to land in its own place: metrics and advice as their
    own headers, index metrics omitted entirely when false rather than sent as
    "False", the client's priority and throughput defaults applied since the
    call did not override them, and availability strategy and excluded
    locations as request settings rather than headers.
    """
    params = [{"name": "@v", "value": [1, 2]}]
    feed = {"Range": {"min": "", "max": "AA"}}
    headers = {"x-custom-request": "before"}
    pager = query.proxy.query_items(
        "SELECT TOP 2 * FROM c ORDER BY VectorDistance(c.v, @v)",
        parameters=params,
        feed_range=feed,
        initial_headers=headers,
        populate_query_metrics=True,
        populate_index_metrics=False,
        populate_query_advice=True,
        enable_scan_in_query=True,
        availability_strategy=False,
        excluded_locations=["East US"],
        max_item_count=2,
        session_token="session",
        max_integrated_cache_staleness_in_ms=0,
    )
    params[0]["value"].append(3)
    feed["Range"]["max"] = "BB"
    headers["x-custom-request"] = "after"
    query.collect(pager)
    prepared = query.calls[0][0]
    body = json.loads(prepared.body_bytes)
    assert body["parameters"] == [{"name": "@v", "value": [1, 2]}]
    assert "feed_range" not in body
    assert prepared.query_scope.feed_range == ("", "AA")
    assert wire_headers(prepared)["x-custom-request"] == "before"
    assert wire_headers(prepared)["x-ms-documentdb-populatequerymetrics"] == "True"
    assert "x-ms-cosmos-populateindexmetrics" not in wire_headers(prepared)
    assert wire_headers(prepared)["x-ms-cosmos-populatequeryadvice"] == "True"
    assert wire_headers(prepared)["x-ms-cosmos-priority-level"] == "Low"
    assert wire_headers(prepared)["x-ms-cosmos-throughput-bucket"] == "3"
    assert settings_options(prepared)["availabilityStrategy"] == "disabled"
    assert settings_options(prepared)["excludedLocations"] == ["East US"]


@pytest.mark.parametrize(
    "kwargs,error",
    [
        ({"query": None}, ValueError),
        ({"query": ""}, ValueError),
        ({"parameters": [{"name": "bad", "value": 1}]}, ValueError),
        ({"parameters": [{"name": "@p", "value": float("nan")}]}, ValueError),
        ({"partition_key": []}, ValueError),
        ({"partition_key": float("inf")}, ValueError),
        (
            {"partition_key": "a", "feed_range": {"Range": {"min": "", "max": "FF"}}},
            ValueError,
        ),
        ({"feed_range": {}}, ValueError),
        ({"enable_cross_partition_query": "false"}, TypeError),
        ({"timeout": 0.5}, ValueError),
        ({"max_item_count": 0}, ValueError),
        ({"max_item_count": True}, ValueError),
        ({"populate_query_metrics": 1}, TypeError),
        ({"full_text_score_scope": "Invalid"}, ValueError),
        ({"full_text_score_scope": "Local"}, NotImplementedError),
        ({"full_text_score_scope": "Global"}, NotImplementedError),
        ({"continuation_token_limit": -1}, ValueError),
        ({"continuation_token_limit": 1}, NotImplementedError),
        ({"read_timeout": 1}, NotImplementedError),
        ({"availability_strategy": "True"}, TypeError),
        ({"initial_headers": {"X-MS-Start-EPK": "00"}}, NotImplementedError),
        ({"initial_headers": {"Authorization": "override"}}, NotImplementedError),
        ({"request_options": {"partitionKeyRangeId": "0"}}, NotImplementedError),
        ({"unknown_option": 1}, NotImplementedError),
        ({"continuation": "legacy"}, ValueError),
        ({"continuation": "c1.raw"}, ValueError),
        ({"continuation": "q1.invalid"}, ValueError),
        ({"continuation": "cf1.feed"}, ValueError),
    ],
)
def test_invalid_or_unsupported_arguments_fail_without_dispatch(query, kwargs, error):
    """Bad or unsupported arguments fail at the call, before anything is sent.

    ``ValueError`` covers right-typed but unusable values: an empty or missing
    query, a parameter name without ``@``, values that are not representable
    in JSON, an empty partition key, a partition key and feed range given
    together (they are two ways to say the same thing), a sub-second timeout,
    and a page size of zero or a bool.

    ``TypeError`` covers wrong types, such as a string where a bool is
    expected.

    ``NotImplementedError`` covers things the Rust path does not support yet
    -- full text score scope, continuation token limits, ``read_timeout``,
    pinned partition key ranges, overriding the authorization or EPK headers,
    and any unrecognised keyword. Accepting and ignoring these would let a
    customer believe a setting took effect.

    Continuation tokens are checked by kind: a legacy token, a raw driver
    ``c1.`` token, a malformed ``q1.`` one, and a change feed ``cf1.`` token
    are each rejected rather than misread.
    """
    values = {"query": "SELECT * FROM c", **kwargs}
    with pytest.raises(error):
        query.proxy.query_items(**values)
    assert not query.calls
    query.connection.QueryItems.assert_not_called()


def test_empty_pages_share_deadline_and_preserve_hook_accounting(query):
    """An empty page consumes budget and charge, and the hook cannot corrupt what follows.

    The first page is empty, so it is skipped internally -- but it still cost
    time and money. The second fetch gets the remaining 0.7 seconds rather
    than a fresh second, and the hook reports a total charge of 4 covering
    both fetches.

    The hook is falsey and must still be called, once, for the one page the
    caller actually sees. Its attempts to rewrite the continuation header and
    clear the rows have no effect: the item is returned and the token is a
    proper ``q1.`` one. An unrecognised header survives untouched.
    """
    query.pages = [[], [{"id": "a"}], None]
    query.delay = 0.3
    calls = []

    class Hook:
        def __bool__(self):
            return False

        def __call__(self, headers, body):
            calls.append((dict(headers), dict(body)))
            headers["x-ms-continuation"] = "corrupt"
            body["Documents"].clear()

    pager = query.proxy.query_items("SELECT * FROM c", timeout=1, response_hook=Hook())
    assert query.collect(pager) == [{"id": "a"}]
    assert len(calls) == 1
    assert calls[0][0]["x-ms-request-charge"] == "4.0"
    assert calls[0][0]["x-custom"] == "preserved"
    assert calls[0][0]["x-ms-continuation"].startswith("q1.")
    assert query.calls[1][2] == pytest.approx(0.7)


def test_errors_do_not_replay_and_keep_last_delivered_bookmark(query):
    """After a failed page the token still points at the last page actually delivered.

    One page succeeds, then the next fetch raises. The token is unchanged from
    before the failure, so a customer saving it resumes from the last page
    they really received -- advancing it would skip the failed page's rows for
    good.

    The pager then refuses further use instead of retrying, the fetch count
    confirms no replay, and the failure never falls back to the legacy path.
    """
    pages = query.proxy.query_items("SELECT * FROM c").by_page()
    query.next_page(pages)
    previous = pages.continuation_token
    query.failure = NotImplementedError("unsupported query feature")
    with pytest.raises(NotImplementedError):
        query.next_page(pages)
    assert pages.continuation_token == previous
    with pytest.raises(RuntimeError, match="failed"):
        query.next_page(pages)
    assert len(query.calls) == 2
    query.connection.QueryItems.assert_not_called()


def test_timeout_and_service_error_surface(query):
    """Timeouts and service errors reach the caller as themselves.

    A page slower than the timeout raises ``CosmosClientTimeoutError``. A page
    the service rejects with 429 raises ``CosmosHttpResponseError`` carrying
    that status.

    Keeping them distinct matters: 429 means throttled and is worth retrying
    with backoff, while a timeout means the caller's own budget ran out. A
    customer cannot choose the right response if both arrive as the same type.
    """
    query.delay = 2
    with pytest.raises(CosmosClientTimeoutError):
        query.collect(query.proxy.query_items("SELECT * FROM c", timeout=1))
    query.delay, query.status = 0, 429
    with pytest.raises(CosmosHttpResponseError) as error:
        query.collect(query.proxy.query_items("SELECT * FROM c"))
    assert error.value.status_code == 429


def test_hook_failure_does_not_advance_public_bookmark(query):
    """A hook that raises on the first page leaves the pager with no token at all.

    The hook fails before any page has been delivered, so there is nothing to
    resume from and the token stays unset rather than pointing at a page the
    caller never received.

    The pager then refuses further use. Together with the error test above,
    this fixes the rule in both directions: the token always names the last
    page that genuinely reached the caller.
    """
    def hook(headers, body):
        raise ValueError("hook failed")

    pages = query.proxy.query_items("SELECT * FROM c", response_hook=hook).by_page()
    with pytest.raises(ValueError, match="hook failed"):
        query.next_page(pages)
    assert pages.continuation_token is None
    with pytest.raises(RuntimeError, match="failed"):
        query.next_page(pages)


def test_core_python_public_query_stays_on_legacy_and_rejects_rust_tokens(query):
    """On the core-python backend queries run the legacy path and refuse Rust tokens.

    With the legacy backend selected, the query returns the legacy iterable
    and the driver is never used. Options the Rust path rejects, such as
    ``read_timeout``, are simply supported here.

    A ``q1.`` token issued by the Rust path is refused as incompatible -- both
    through the public call and through the query iterable directly, since
    customers can construct one themselves. The two backends encode position
    differently, so reading the wrong kind could restart the query or skip
    rows.
    """
    query.proxy._item_context = None
    query.connection._backend = SimpleNamespace(name="core-python")
    query.proxy._get_properties_with_options = MagicMock(
        return_value={
            "_rid": "rid",
            "partitionKey": {"paths": ["/pk"], "kind": "Hash", "version": 2},
        }
    )
    result = query.proxy.query_items("SELECT * FROM c", read_timeout=5)
    assert result is query.connection.QueryItems.return_value
    assert not query.calls
    with pytest.raises(ValueError, match="incompatible"):
        query.proxy.query_items("SELECT * FROM c", continuation="q1.saved")
    iterable = (
        __import__(
            "azure.cosmos.aio._query_iterable_async", fromlist=["QueryIterable"]
        ).QueryIterable
        if query.async_mode
        else __import__(
            "azure.cosmos._query_iterable", fromlist=["QueryIterable"]
        ).QueryIterable
    )
    with pytest.raises(ValueError, match="incompatible"):
        iterable(query.connection, "SELECT * FROM c", {}, continuation_token="q1.saved")


def test_query_advice_and_index_headers_are_decoded_before_hooks(query, monkeypatch):
    """Index and query advice headers are decoded before anyone sees them.

    Both arrive from the service in an encoded form. By the time the response
    hook runs they have been decoded, so a customer reading them gets usable
    text rather than a raw blob they would have to decode themselves.

    The decoded values are also what gets recorded as the last response
    headers on the client, so the two views agree.
    """
    from azure.cosmos._helpers import _query_items

    monkeypatch.setattr(
        _query_items._utils, "get_index_metrics_info", lambda value: "index:" + value
    )
    monkeypatch.setattr(
        _query_items, "get_query_advice_info", lambda value: "advice:" + value
    )
    method = (
        query.binding.fetch_page_with_cursor_async
        if query.async_mode
        else query.binding.fetch_page_with_cursor
    )
    original = method.side_effect

    def page(*args, **kwargs):
        result = original(*args, **kwargs)
        if result[2]:
            result[2]["x-ms-cosmos-index-utilization"] = "raw"
            result[2]["x-ms-cosmos-query-advice"] = "raw"
        return result

    method.side_effect = page
    calls = []
    pager = query.proxy.query_items(
        "SELECT * FROM c",
        response_hook=lambda headers, body: calls.append(dict(headers)),
    )
    query.collect(pager)
    assert calls[0]["x-ms-cosmos-index-utilization"] == "index:raw"
    assert calls[0]["x-ms-cosmos-query-advice"] == "advice:raw"
    assert (
        query.proxy._item_context.response_state.last_response_headers[
            "x-ms-cosmos-query-advice"
        ]
        == "advice:raw"
    )


def test_driver_initialization_consumes_public_page_budget(query, monkeypatch):
    """Starting the driver counts against the first page's timeout.

    Start-up takes 2 seconds against a 1 second budget, so the call times out
    before a page is fetched. Start-up is one-off work that lands on the first
    page, and leaving it outside the budget would let that page overrun its
    timeout by however long the driver took to come up.
    """
    def ensure():
        query.clock.now += 2
        return "handle"

    monkeypatch.setattr(
        query.backend,
        "_ensure_driver_handle",
        (
            AsyncMock(side_effect=ensure)
            if query.async_mode
            else MagicMock(side_effect=ensure)
        ),
    )
    with pytest.raises(CosmosClientTimeoutError):
        query.collect(query.proxy.query_items("SELECT * FROM c", timeout=1))
    assert not query.calls


def test_async_query_cancellation_invalidates_cursor_without_replay(query):
    """Concurrent use is refused, and cancelling a page leaves the pager unusable.

    While one page fetch is in flight, asking the same iterator for another
    page raises about concurrent use rather than corrupting the shared cursor.
    A page iterator is not safe to drive from two places at once, and saying
    so is better than interleaving two fetches on one cursor.

    Cancelling the in-flight page then propagates ``CancelledError``, and
    afterwards the pager refuses further use, reports no token, and has
    released its cursor. A cancelled page was never delivered, so resuming
    would be resuming from an unknown position.

    Sync mode returns early: there is no cancellation to test there.
    """
    if not query.async_mode:
        return

    async def run():
        entered = asyncio.Event()
        blocker = asyncio.Event()

        async def blocked(*args, **kwargs):
            entered.set()
            await blocker.wait()

        query.binding.fetch_page_with_cursor_async.side_effect = blocked
        pages = query.proxy.query_items("SELECT * FROM c").by_page()
        task = asyncio.create_task(pages.__anext__())
        await entered.wait()
        with pytest.raises(RuntimeError, match="Concurrent"):
            await pages.__anext__()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        with pytest.raises(RuntimeError, match="failed"):
            await pages.__anext__()
        assert pages.continuation_token is None
        assert pages.state.cursor is None

    asyncio.run(run())
    query.connection.QueryItems.assert_not_called()


def test_service_error_carries_last_delivered_public_bookmark(query):
    """A service error carries the token for the last page that was delivered.

    After one good page the service returns 429. The raised error carries the
    token from that first page, and the pager still reports it.

    Putting the token on the error is what lets a customer catch a throttling
    failure and resume from exactly where they left off, instead of starting
    the query again and paying for the pages they already read.
    """
    pages = query.proxy.query_items("SELECT * FROM c").by_page()
    query.next_page(pages)
    bookmark = pages.continuation_token
    query.status = 429
    with pytest.raises(CosmosHttpResponseError) as error:
        query.next_page(pages)
    assert error.value.continuation_token == bookmark
    assert pages.continuation_token == bookmark


def test_enabled_request_hedging_uses_client_threshold(query, monkeypatch):
    """Turning on the availability strategy picks up the client's hedging threshold.

    ``availability_strategy=True`` is a request to hedge, not a full
    configuration. The threshold comes from the client, so the request settings
    read ``enabled:250`` rather than just "enabled" -- the driver needs to know
    how long to wait before sending the second copy of the request.
    """
    from azure.cosmos._backend.contracts import PreparedClientConfig

    with monkeypatch.context() as patch:
        patch.setattr(
            query.backend,
            "_client_config",
            PreparedClientConfig(hedging_threshold_ms=250),
        )
        query.collect(
            query.proxy.query_items("SELECT * FROM c", availability_strategy=True)
        )
    assert settings_options(query.calls[0][0])["availabilityStrategy"] == "enabled:250"


def test_invalid_header_name_and_non_document_envelope_fail_explicitly(query):
    """A non-string header name and a malformed response envelope both fail with a clear message.

    A header name that is not a string is rejected at the call. Header names
    have to be strings to be written to the wire, and catching it here beats a
    confusing failure deeper in the driver.

    A response whose ``Documents`` field is an object rather than an array
    raises an error naming both the operation and the field. Rows are iterated
    from that field, so an unexpected shape would otherwise fail somewhere far
    from the cause -- or worse, iterate an object's keys as if they were rows.
    """
    with pytest.raises(TypeError, match="names must be strings"):
        query.proxy.query_items("SELECT * FROM c", initial_headers={1: "value"})
    method = (
        query.binding.fetch_page_with_cursor_async
        if query.async_mode
        else query.binding.fetch_page_with_cursor
    )
    method.side_effect = lambda *args, **kwargs: (200, 0, {}, b'{"Documents":{}}', None)
    with pytest.raises(ValueError, match="query_items.*invalid Documents"):
        query.collect(query.proxy.query_items("SELECT * FROM c", read_timeout=None))
