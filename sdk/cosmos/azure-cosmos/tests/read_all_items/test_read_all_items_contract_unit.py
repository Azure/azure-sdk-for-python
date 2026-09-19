# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Read-all contract: lazy paging, continuation tokens and per-page budgets, with no service calls.

``read_all_items`` enumerates a whole container. It hands back a pager that
fetches nothing until it is iterated, then walks pages until the service stops
returning a continuation token.

The tests here divide into four areas:

* **Laziness and pinning.** Building the pager must not call anything. The
  backend is fixed when the pager is created, so later changes to the
  container proxy cannot make one enumeration switch backends mid-flight.
* **Continuation tokens.** Each pager keeps its own position. Tokens belong to
  the backend that issued them, so a legacy token must be rejected by the Rust
  path and vice versa rather than being misread. Position must never be taken
  from connection-wide response headers, which a concurrent call could have
  overwritten.
* **One budget per public page.** ``timeout`` applies to each page the caller
  asks for, not to the whole enumeration -- a customer iterating a large
  container should not have the loop die partway. Within a single page, though,
  everything counts: driver start-up and any empty internal pages.
* **Response hooks.** A hook sees each internal page, cannot corrupt the rows
  or the paging state, and if it fails the pager stays failed instead of
  quietly looking exhausted.

The ``feed`` fixture drives the Rust path and ``legacy_feed`` the legacy one;
both run once sync and once async.
"""
from common.typed_requests import key_from_legacy_header

import asyncio
import inspect
import json
from types import MethodType, SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos import _operation_deadline
from azure.cosmos.container import ContainerProxy
from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy
from azure.cosmos._backend import binding as sync_rust
from azure.cosmos.aio._backend import binding as async_rust
from azure.cosmos._helpers import _read_all_items
from azure.cosmos._helpers._item_context import ItemClientContext, ItemClientDefaults
from azure.cosmos.exceptions import CosmosClientTimeoutError


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def feed(request, monkeypatch):
    """Drive the Rust read-all path against a fake driver, once sync and once async.

    Replaces the driver binding so page fetches are served from
    ``context.pages`` -- four pages by default, two of which are empty, ending
    with a page that returns no continuation token. Each page reports a charge
    of 2, so tests can check charges add up.

    Everything above the binding is real: the container proxy, the backend,
    and the pager. The clock is faked, so ``delay`` (time per page) and
    ``init_delay`` (time to start the driver) let a test spend budget without
    actually waiting.

    Provides ``collect`` to drain a pager and ``next_page`` to take one page,
    both hiding the sync/async difference. The backend is closed on teardown.
    """
    async_mode = request.param
    clock = SimpleNamespace(now=100.0)
    clock.monotonic = lambda: clock.now
    monkeypatch.setattr(_read_all_items, "time", clock)
    monkeypatch.setattr(_operation_deadline, "time", clock)
    context = SimpleNamespace(
        clock=clock,
        calls=[],
        pages=[
            ([{"id": "a", "nested": [1]}], "c1.a"),
            ([], "c1.b"),
            ([{"id": "b"}], "c1.c"),
            ([], None),
        ],
        delay=0,
        init_delay=0,
        async_mode=async_mode,
        status=200,
    )

    def page(handle, prepared, cursor, *, timeout_seconds=None):
        context.calls.append((prepared, cursor, timeout_seconds))
        if timeout_seconds is not None and context.delay > timeout_seconds:
            raise TimeoutError("native page budget exhausted")
        clock.now += context.delay
        token = prepared.settings.query.continuation
        index = (
            0
            if token is None
            else next(i + 1 for i, (_, t) in enumerate(context.pages) if t == token)
        )
        rows, following = context.pages[index]
        headers = {"x-ms-request-charge": "2", "x-ms-session-token": "session"}
        if following is not None:
            headers["x-ms-continuation"] = following
        context.prepared = prepared
        return (
            context.status,
            0,
            headers,
            json.dumps({"Documents": rows}).encode(),
            None,
        )

    def ensure():
        clock.now += context.init_delay
        return "handle"

    module = async_rust if async_mode else sync_rust
    binding = SimpleNamespace(
        _ItemFeedCursor=MagicMock(side_effect=object),
        read_all_items=MagicMock(),
        read_all_items_async=AsyncMock(),
        fetch_page_with_cursor=MagicMock(side_effect=page),
        fetch_page_with_cursor_async=AsyncMock(side_effect=page),
    )
    monkeypatch.setattr(module, "_rust_module", binding)
    backend_type = async_rust.AsyncRustBinding if async_mode else sync_rust.RustBinding
    backend = backend_type("https://read-all.invalid", master_key="ZmFrZQ==")
    monkeypatch.setattr(
        backend,
        "_ensure_driver_handle",
        AsyncMock(side_effect=ensure) if async_mode else MagicMock(side_effect=ensure),
    )
    connection = MagicMock()
    connection._backend = backend
    context.item_context = ItemClientContext(backend)
    context.proxy = (AsyncContainerProxy if async_mode else ContainerProxy)(
        connection,
        "dbs/db",
        "c",
        _item_context=context.item_context,
    )
    context.binding, context.connection, context.backend = binding, connection, backend

    def collect(pager):
        async def collect_async():
            return [row async for row in pager]

        return asyncio.run(collect_async()) if async_mode else list(pager)

    def next_page(pages):
        async def fetch():
            page = await pages.__anext__()
            return [row async for row in page]

        return asyncio.run(fetch()) if async_mode else list(next(pages))

    context.collect, context.next_page = collect, next_page
    yield context
    closed = backend.close()
    if inspect.isawaitable(closed):
        asyncio.run(closed)


@pytest.mark.parametrize("kwargs,priority,bucket", [
    ({}, "Low", 3),
    ({"priority": "High", "throughput_bucket": 5}, "High", 5),
])
def test_read_all_inherits_client_priority_defaults(feed, kwargs, priority, bucket):
    """Client-level priority and throughput bucket apply to every page, unless overridden.

    The client is configured with a low priority and bucket 3. With no
    arguments, every page request carries those defaults; when the call passes
    its own values, every page carries those instead.

    The check is on *all* pages rather than the first, since settings applied
    only to the opening request would leave the rest of a long enumeration
    running at the wrong priority.
    """
    feed.proxy._item_context = ItemClientContext(
        feed.backend, ItemClientDefaults(priority="Low", throughput_bucket=3)
    )
    feed.collect(feed.proxy.read_all_items(**kwargs))
    assert all(p.settings.priority == priority for p, _, _ in feed.calls)
    assert all(p.settings.throughput_bucket == bucket for p, _, _ in feed.calls)


def test_complete_enumeration_retains_cursor_and_skips_empty_pages(feed):
    """A full enumeration is lazy, reuses one cursor, and hides empty pages from the caller.

    Nothing is fetched until iteration starts. Draining the pager then walks
    all four pages but returns only the two real items -- the two empty pages
    in the middle are consumed internally rather than surfacing as empty
    results the caller would have to filter out.

    All four fetches share one cursor object. A fresh cursor per page would
    lose the driver's place in the feed. The page size reaches every request,
    and the legacy path is never touched.
    """
    pager = feed.proxy.read_all_items(max_item_count=1)
    assert feed.calls == []
    assert feed.collect(pager) == [{"id": "a", "nested": [1]}, {"id": "b"}]
    assert len(feed.calls) == 4
    assert len({id(cursor) for _, cursor, _ in feed.calls}) == 1
    assert all(p.settings.query.max_item_count == 1 for p, _, _ in feed.calls)
    feed.connection.ReadItems.assert_not_called()


def test_resume_and_independent_pagers_ignore_global_headers(feed):
    """Two pagers keep separate positions, and neither reads its position from the connection.

    One pager takes a page, then a second is resumed from its continuation
    token. Between the two, the connection's shared response headers are set
    to an unrelated token -- if either pager consulted those instead of its
    own state it would jump to the wrong place. In a real application that
    header could have been written by a completely different call.

    The resumed pager continues correctly, and the original still returns its
    own next page afterwards. The two use different cursors, while the
    original keeps the cursor it started with.
    """
    first = feed.proxy.read_all_items().by_page()
    assert feed.next_page(first)[0]["id"] == "a"
    token = first.continuation_token
    feed.connection.last_response_headers = {"x-ms-continuation": "unrelated"}
    resumed = feed.proxy.read_all_items().by_page(continuation_token=token)
    assert feed.next_page(resumed) == [{"id": "b"}]
    assert feed.next_page(first) == [{"id": "b"}]
    assert feed.calls[0][1] is not feed.calls[1][1]
    assert feed.calls[0][1] is feed.calls[-1][1]


@pytest.mark.parametrize(
    "kwargs,error",
    [
        ({"populate_query_metrics": None}, TypeError),
        ({"populate_query_metrics": False}, TypeError),
        ({"populate_query_metrics": True}, TypeError),
        ({"max_item_count": 0}, ValueError),
        ({"max_item_count": -2}, ValueError),
        ({"max_item_count": True}, ValueError),
        ({"max_item_count": 1.5}, ValueError),
        ({"max_integrated_cache_staleness_in_ms": False}, ValueError),
        ({"max_integrated_cache_staleness_in_ms": -1}, ValueError),
        ({"timeout": float("nan")}, ValueError),
        ({"timeout": 0}, ValueError),
        ({"timeout": True}, ValueError),
        ({"response_hook": 4}, TypeError),
        ({"read_timeout": 2}, NotImplementedError),
        ({"availability_strategy": False}, NotImplementedError),
        ({"feed_range": {}}, NotImplementedError),
        ({"request_options": {"partitionKeyRangeId": "0"}}, NotImplementedError),
        ({"initial_headers": {"authorization": "override"}}, NotImplementedError),
        ({"continuation": "legacy"}, ValueError),
    ],
)
def test_invalid_or_unsupported_settings_fail_without_dispatch(feed, kwargs, error):
    """Bad or unsupported arguments fail at the call, before any page is fetched.

    Three groups, each with its own exception type:

    * ``TypeError`` for arguments that no longer exist or have the wrong type
      -- ``populate_query_metrics`` in any form, a non-callable hook.
    * ``ValueError`` for right-typed but unusable values: a page size of zero,
      negative, a bool, or fractional; a negative cache staleness; a timeout
      that is zero, ``nan``, or a bool; and a legacy continuation passed as
      ``continuation``.
    * ``NotImplementedError`` for settings the Rust path genuinely does not
      support yet -- ``read_timeout``, ``availability_strategy``,
      ``feed_range``, a pinned partition key range, or an attempt to override
      the authorization header.

    The last group matters most: silently ignoring an unsupported setting
    would let a customer believe it took effect. Nothing is dispatched in any
    case, so no argument mistake can cost a request.
    """
    with pytest.raises(error):
        feed.proxy.read_all_items(**kwargs)
    assert feed.calls == []


def test_positional_settings_rejected(feed):
    """Every option must be passed by name.

    ``read_all_items`` takes no positional arguments, so a stray positional is
    a ``TypeError`` rather than being silently bound to whichever parameter
    happens to come first. That keeps the signature free to change without
    breaking callers in surprising ways.
    """
    with pytest.raises(TypeError):
        feed.proxy.read_all_items(1)


@pytest.mark.parametrize("count", [None, -1, 1, 100])
def test_page_size_is_a_hint_not_total_limit(feed, count):
    """``max_item_count`` shapes pages; it never caps how many items come back.

    Whether the page size is unset, -1, 1, or 100, enumerating the container
    yields both items. It is a request for how much to fetch at a time, not a
    limit on the result -- reading a container with ``max_item_count=1`` and
    getting one item back would silently lose data.
    """
    assert len(feed.collect(feed.proxy.read_all_items(max_item_count=count))) == 2


def test_options_snapshotted_and_false_callback_isolated(feed):
    """The options dict is copied at the call, and a falsey hook still runs but cannot do harm.

    The options are changed *after* the pager is built but before it is
    iterated. The request still carries the original header value, so the
    options were copied when the call was made rather than read lazily at
    fetch time -- otherwise a later edit would change requests already in
    flight.

    The hook is an object whose ``__bool__`` returns ``False``. It must still
    be called; a plain truth check would skip it. It then tries to rewrite the
    continuation header and empty the rows, and neither takes effect: paging
    continues to the real end and both items are returned.

    The caller's dict is left holding only their own edit.
    """
    options = {"maxItemCount": 1, "initialHeaders": {"x-test": "before"}}
    calls = []

    class Hook:
        def __bool__(self):
            return False

        def __call__(self, headers, body):
            calls.append(dict(headers))
            headers["x-ms-continuation"] = "corrupt"
            body["Documents"].clear()

    pager = feed.proxy.read_all_items(request_options=options, response_hook=Hook())
    options["initialHeaders"]["x-test"] = "after"
    assert len(feed.collect(pager)) == 2
    assert feed.calls[0][0].headers["x-test"] == "before"
    assert all(headers.get("x-ms-continuation") != "corrupt" for headers in calls)
    assert options == {"maxItemCount": 1, "initialHeaders": {"x-test": "after"}}


def test_hook_error_not_replayed_and_bookmark_not_advanced(feed):
    """If the caller's hook raises, the page is not retried and the position does not move.

    The hook raises on the first page. The caller gets their own exception
    object back, and the continuation token stays unset -- treating a failed
    page as delivered would skip those items on the next call.

    Asking for another page raises a clear "pager failed" error rather than
    trying again, and the underlying fetch ran exactly once. Retrying would
    charge the customer twice for a page their own code rejected.
    """
    error = TimeoutError("customer callback")
    hook = MagicMock(side_effect=error)
    pages = feed.proxy.read_all_items(response_hook=hook).by_page()
    with pytest.raises(TimeoutError) as caught:
        feed.next_page(pages)
    assert caught.value is error
    assert pages.continuation_token is None
    with pytest.raises(RuntimeError, match="pager failed"):
        feed.next_page(pages)
    assert len(feed.calls) == 1
    hook.assert_called_once()


def test_new_budget_each_public_page_including_internal_empty_pages(feed):
    """Each page the caller asks for gets a fresh timeout; internal pages share it.

    The clock jumps 500 seconds between the caller's two page requests, far
    past any timeout, and neither fails -- ``timeout`` bounds a single page,
    not the whole enumeration. A customer looping over a large container must
    not have iteration die because the loop as a whole took a while.

    Within one page the budget is shared: the second public page needs two
    fetches because one internal page is empty, and the second fetch gets the
    remaining 0.7 seconds rather than a full second.
    """
    feed.delay = 0.3
    pages = feed.proxy.read_all_items(timeout=1).by_page()
    feed.clock.now += 500
    feed.next_page(pages)
    feed.clock.now += 500
    feed.next_page(pages)
    assert [timeout for _, _, timeout in feed.calls] == pytest.approx([1, 1, 0.7])


def test_handle_initialization_is_in_page_budget(feed):
    """Starting the driver counts against the page timeout.

    Driver start-up takes 1.1 seconds against a 1 second budget, so the call
    times out before a single page is fetched.

    Start-up is one-off work that happens on the first page, and leaving it
    outside the budget would make the first page of an enumeration able to
    overrun its timeout by however long the driver took to come up.
    """
    feed.init_delay = 1.1
    with pytest.raises(CosmosClientTimeoutError):
        feed.collect(feed.proxy.read_all_items(timeout=1))
    assert feed.calls == []


def test_internal_empty_pages_do_not_restart_budget(feed):
    """Skipping an empty page does not buy the next one a fresh timeout.

    The feed returns an empty page and then a real one, each taking 0.6
    seconds against a 1 second budget. Together they exceed it, so the call
    times out.

    Empty pages are invisible to the caller but still cost real time. If each
    restarted the clock, a container with a long run of empty pages could keep
    a ``timeout=1`` call going indefinitely.
    """
    feed.pages = [([], "c1.a"), ([{"id": "late"}], None)]
    feed.delay = 0.6
    with pytest.raises(CosmosClientTimeoutError):
        feed.collect(feed.proxy.read_all_items(timeout=1))


def test_backend_pinned_at_iterator_creation(feed):
    """The backend is fixed when the pager is created, not looked up per page.

    After the pager exists, both the container's item context and the
    connection's backend are replaced with unrelated mocks. The enumeration
    still completes against the original backend and returns both items.

    Re-reading the backend on each page would let a client reconfigured
    mid-enumeration send later pages somewhere else, carrying a continuation
    token the new backend cannot understand.
    """
    pager = feed.proxy.read_all_items()
    feed.proxy._item_context = ItemClientContext(MagicMock())
    feed.connection._backend = MagicMock()
    assert len(feed.collect(pager)) == 2


def test_wrong_backend_by_page_bookmark_rejected(feed):
    """A legacy continuation token cannot be used to resume on the Rust path.

    Resuming with a token the Rust backend did not issue raises about an
    incompatible backend, and nothing is fetched.

    The two backends encode position differently, so a token from the wrong
    one is not merely unusable -- interpreting it could silently restart the
    enumeration or skip a section of the container.
    """
    with pytest.raises(ValueError, match="incompatible backend"):
        feed.proxy.read_all_items().by_page(continuation_token="legacy")
    assert feed.calls == []


def test_internal_page_charges_accumulate_and_hook_failure_keeps_headers(feed):
    """Charges add up across the internal pages behind one public page.

    The second public page needs two fetches because one internal page is
    empty. The hook sees a running charge of 4, not the 2 from the last fetch
    alone -- reporting only the final page would under-report what the caller
    was billed.

    The headers also carry the newest continuation token, and the pager's own
    headers agree with what the hook was shown.
    """
    calls = []
    pager = feed.proxy.read_all_items(response_hook=lambda h, _: calls.append(h))
    pages = pager.by_page()
    feed.next_page(pages)
    feed.next_page(pages)
    assert float(calls[1]["x-ms-request-charge"]) == 4
    assert calls[1]["x-ms-continuation"] == "c1.c"
    assert pager.get_response_headers()["x-ms-continuation"] == "c1.c"


def test_hook_iteration_stop_is_a_failure_not_silent_exhaustion(feed):
    """A hook raising StopIteration is reported as an error, not treated as the end of the feed.

    ``StopIteration`` is how Python signals a finished iterator, so a hook
    raising it could easily be mistaken for "no more pages" -- and the caller
    would get a short read that looks like a complete one.

    Instead it surfaces as a ``RuntimeError`` naming the response hook, and
    the pager stays failed on the next attempt rather than quietly reporting
    exhaustion.
    """
    pages = feed.proxy.read_all_items(
        response_hook=MagicMock(side_effect=StopIteration("hook"))
    ).by_page()
    with pytest.raises(RuntimeError, match="response_hook"):
        feed.next_page(pages)
    with pytest.raises(RuntimeError, match="pager failed"):
        feed.next_page(pages)


def test_empty_container_hook_once_and_state_released(feed):
    """An empty container ends cleanly, calls the hook once, and frees its cursor.

    Both pages are empty, so there is nothing to hand back and iteration stops
    immediately. The hook is still called once rather than never, so callers
    watching charges see that a request happened.

    Afterwards the cursor is released and no continuation token is reported.
    Holding driver state open after the feed is exhausted would leak for every
    enumeration a long-running application performs.
    """
    feed.pages = [([], "c1.empty"), ([], None)]
    hook = MagicMock()
    pager = feed.proxy.read_all_items(response_hook=hook)
    pages = pager.by_page()
    feed.collect_pages = pages
    with pytest.raises((StopIteration, StopAsyncIteration)):
        feed.next_page(pages)
    hook.assert_called_once()
    assert pages.state.cursor is None
    assert "x-ms-continuation" not in pager.get_response_headers()


def test_async_cancellation_drains_work_and_prevents_replay(feed):
    """Cancelling an in-flight page cleans up and leaves the pager unusable.

    The fetch hangs, the caller cancels, and ``CancelledError`` propagates
    unchanged. The fetch's cleanup block runs, so nothing is left pending
    against the driver.

    The cursor is released and any further page request fails outright. A
    cancelled page was never delivered, so resuming afterwards would be
    resuming from an unknown position -- refusing is the safe answer.

    Sync mode is skipped: there is no cancellation to test there.
    """
    if not feed.async_mode:
        pytest.skip("async cancellation")

    async def scenario():
        started, dropped = asyncio.Event(), asyncio.Event()

        async def slow(*args, **kwargs):
            started.set()
            try:
                await asyncio.Future()
            finally:
                dropped.set()

        feed.binding.fetch_page_with_cursor_async.side_effect = slow
        pages = feed.proxy.read_all_items(timeout=1).by_page()
        task = asyncio.create_task(pages.__anext__())
        await started.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert dropped.is_set()
        assert pages.state.cursor is None
        with pytest.raises(RuntimeError, match="pager failed"):
            await pages.__anext__()

    asyncio.run(scenario())


@pytest.fixture(params=[False, True], ids=["sync-legacy", "async-legacy"])
def legacy_feed(request, monkeypatch):
    """Drive the legacy read-all path against a fake transport, once sync and once async.

    The counterpart to ``feed``. The real ``ReadItems`` and ``QueryItems``
    methods are bound to a mock connection and only the lowest-level page
    fetch is replaced, so the legacy paging logic itself is exercised.

    Serves three pages keyed by continuation token, the middle one empty, and
    records every options dict it was called with. Retry handling is stubbed
    out to call straight through, keeping tests focused on paging.

    Two details are deliberate traps for the tests to catch: the connection's
    ``last_response_headers`` is set to an unrelated token after every fetch,
    and each page carries an ``etag`` that must never be mistaken for a
    position marker.
    """
    from azure.cosmos._cosmos_client_connection import CosmosClientConnection
    from azure.cosmos.aio._cosmos_client_connection_async import (
        CosmosClientConnection as AsyncConnection,
    )
    from azure.cosmos._backend.legacy import LEGACY_BACKEND
    from azure.cosmos.aio._backend.legacy import ASYNC_LEGACY_BACKEND
    from azure.cosmos import _retry_utility
    from azure.cosmos.aio import _retry_utility_async

    async_mode = request.param
    cls = AsyncConnection if async_mode else CosmosClientConnection
    backend = ASYNC_LEGACY_BACKEND if async_mode else LEGACY_BACKEND
    connection = MagicMock()
    connection._backend = backend
    connection.ReadItems = MethodType(cls.ReadItems, connection)
    connection.QueryItems = MethodType(cls.QueryItems, connection)
    connection._CosmosClientConnection__container_properties_cache = {
        "dbs/db/colls/c": {"_rid": "rid"}
    }
    context = SimpleNamespace(calls=[], metadata=[], async_mode=async_mode)

    def metadata(options):
        context.metadata.append(dict(options))
        return {"_rid": "rid"}

    def fetch(*args, **kwargs):
        options = args[6]
        context.calls.append((dict(options), kwargs.get("_read_all_backend")))
        assert kwargs["_read_all_backend"] is backend
        token = options.get("continuation")
        rows, following = {
            None: ([{"id": "a"}], "legacy-a"),
            "legacy-a": ([], "legacy-empty"),
            "legacy-empty": ([{"id": "b"}], None),
        }[token]
        headers = CaseInsensitiveDict(
            {"x-ms-request-charge": "2", "etag": "not-a-bookmark"}
        )
        if following is not None:
            headers["x-ms-continuation"] = following
        kwargs["response_headers"].clear()
        kwargs["response_headers"].update(headers)
        kwargs["response_hook"](headers, {"Documents": rows})
        connection.last_response_headers = {"x-ms-continuation": "unrelated"}
        return rows if async_mode else (rows, headers)

    async def execute_async(_client, _manager, callback, **kwargs):
        return await callback()

    monkeypatch.setattr(
        _retry_utility, "Execute", lambda _c, _m, callback, **kw: callback()
    )
    monkeypatch.setattr(_retry_utility_async, "ExecuteAsync", execute_async)
    connection._CosmosClientConnection__QueryFeed = (
        AsyncMock(side_effect=fetch) if async_mode else fetch
    )
    context.proxy = (AsyncContainerProxy if async_mode else ContainerProxy)(
        connection,
        "dbs/db",
        "c",
        _item_context=ItemClientContext(backend),
    )
    context.proxy._get_properties_with_options = (
        AsyncMock(side_effect=metadata) if async_mode else metadata
    )

    def next_page(pages):
        async def fetch_page():
            page = await pages.__anext__()
            return [row async for row in page]

        return asyncio.run(fetch_page()) if async_mode else list(next(pages))

    context.next_page, context.connection = next_page, connection
    return context


def test_legacy_remains_lazy_pinned_and_uses_per_pager_bookmarks(legacy_feed):
    """The legacy path keeps the same laziness, isolation and accounting guarantees.

    Building the pager fetches nothing and does not even load container
    metadata. Settings the Rust path rejects -- ``read_timeout`` and
    ``availability_strategy`` -- are accepted here, since legacy supports them.

    Paging then walks three fetches to produce two public pages, the middle
    one being empty. The continuation token comes from the pager's own state:
    the fixture overwrites the connection's shared headers after every fetch,
    so a pager reading from there would go astray. The ``etag`` on each page
    is likewise not mistaken for a position.

    The token clears at the end, charges total 4 across all three fetches, the
    hook fires once per public page, and the caller's options dict is
    untouched.
    """
    hook = MagicMock()
    options = {"maxItemCount": 1}
    pager = legacy_feed.proxy.read_all_items(
        request_options=options,
        read_timeout=2,
        availability_strategy=False,
        response_hook=hook,
    )
    pages = pager.by_page()
    assert legacy_feed.calls == legacy_feed.metadata == []
    assert legacy_feed.next_page(pages) == [{"id": "a"}]
    assert pages.continuation_token == "legacy-a"
    assert legacy_feed.next_page(pages) == [{"id": "b"}]
    assert pages.continuation_token is None
    assert len(legacy_feed.calls) == 3
    assert float(pager.get_response_headers()["x-ms-request-charge"]) == 4
    assert hook.call_count == 2
    assert options == {"maxItemCount": 1}


def test_legacy_rejects_driver_bookmarks_before_metadata(legacy_feed):
    """A Rust continuation token cannot be used to resume on the legacy path.

    The mirror of the Rust-side check. Resuming with a driver token raises
    about an incompatible backend, and the rejection happens before the
    container metadata lookup -- so a mismatched token costs nothing at all.
    """
    with pytest.raises(ValueError, match="incompatible backend"):
        legacy_feed.proxy.read_all_items().by_page(continuation_token="c1.driver")
    assert legacy_feed.metadata == []


def test_legacy_resume_does_not_use_connection_headers(legacy_feed):
    """Resuming on the legacy path starts from the supplied token, not the connection's headers.

    The pager is resumed from the token for the second page, and returns the
    item that follows it. The fixture keeps the connection's shared headers
    pointing at an unrelated token throughout, so reading position from there
    would produce the wrong page.

    Two fetches are needed because the page in between is empty.
    """
    pages = legacy_feed.proxy.read_all_items().by_page(continuation_token="legacy-a")
    assert legacy_feed.next_page(pages) == [{"id": "b"}]
    assert len(legacy_feed.calls) == 2


@pytest.mark.parametrize("method", ["fetch_page_with_cursor", "fetch_page_with_cursor_async"])
def test_compiled_page_entrypoint_rejects_legacy_token_without_io(method):
    """The compiled driver itself refuses a legacy token, without opening a connection.

    The other token tests work through the Python wrapper. This one calls the
    compiled page function directly, sync and async, with a legacy
    continuation and an unusable handle.

    It raises about the continuation before the handle is ever used, which
    proves the check lives in the driver rather than only in the Python layer
    above it. Skipped when the compiled module is not built.
    """
    from azure.cosmos._backend.request_settings import RequestSettings, QuerySettings

    native = pytest.importorskip("azure.cosmos._rust")
    prepared = SimpleNamespace(
        container_link="dbs/db/colls/c",
        protocol_version=3, partition_key=key_from_legacy_header("[]"),
        headers={},
        settings=RequestSettings(query=QuerySettings(continuation="legacy-bookmark")),
    )
    with pytest.raises(ValueError, match="Rust driver continuation"):
        getattr(native, method)("unused-handle", prepared, native._ItemFeedCursor())


def test_hook_preserves_envelope_fields_and_does_not_alias_rows(feed):
    """The hook sees the full response envelope, and editing its rows does not change the result.

    Each page is given the ``_rid`` and ``_count`` fields a real response
    carries. The hook sees both, so callers relying on them are not handed a
    stripped-down body.

    The hook then rewrites the first row's id on every page. The returned
    items still read "a" and "b", so the hook was working on a copy -- sharing
    row objects would let a hook that merely inspects data accidentally alter
    what the customer receives.
    """
    calls = []
    original = (
        feed.binding.fetch_page_with_cursor_async.side_effect
        if feed.async_mode
        else feed.binding.fetch_page_with_cursor.side_effect
    )

    def with_envelope(*args, **kwargs):
        status, substatus, headers, body, diagnostics = original(*args, **kwargs)
        envelope = json.loads(body)
        envelope["_rid"] = "container-rid"
        envelope["_count"] = len(envelope["Documents"])
        return status, substatus, headers, json.dumps(envelope).encode(), diagnostics

    feed.binding.fetch_page_with_cursor.side_effect = with_envelope
    feed.binding.fetch_page_with_cursor_async.side_effect = with_envelope

    def hook(headers, body):
        calls.append((body["_rid"], body["_count"]))
        if body["Documents"]:
            body["Documents"][0]["id"] = "hook-change"

    rows = feed.collect(feed.proxy.read_all_items(response_hook=hook))
    assert [row["id"] for row in rows] == ["a", "b"]
    assert calls[:2] == [("container-rid", 1), ("container-rid", 1)]
