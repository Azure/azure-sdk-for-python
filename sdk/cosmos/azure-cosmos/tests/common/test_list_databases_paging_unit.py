# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Unit coverage for listing databases one page at a time (no network).

Listing is different from a single read: the answer arrives in pages, and the
caller can stop between them, hand the pager around, or start a second one from
a saved position. That makes three things easy to get wrong, and this file is
organized around them.

Who owns the continuation token. It is the value a caller saves to resume
listing later, and it must reflect the pages they have actually received. A
callback that runs other work in the middle, or a second pager started from a
different position, must not be able to move it.

What a customer callback is allowed to do. It runs between pages, so a mistake
inside it must surface as their error, not be retried, swallowed, or mistaken
for the end of the list.

How the time limit is spent. One timeout covers a public page fetch, including
driver setup and any empty service pages fetched before delivering results.
The next public page fetch gets a fresh timeout; application processing between
delivered pages does not consume it.

Most tests exercise both selectable transports through the current pager.
They check consistent behavior, not parity with a released legacy SDK.
"""
import asyncio
import json
import time
from copy import deepcopy
from unittest.mock import MagicMock

import pytest
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos import _rust
from azure.cosmos._backend import binding as sync_rust
from azure.cosmos.aio._backend import binding as async_rust
from azure.cosmos._backend.contracts import BackendResponse
from azure.cosmos._backend.errors import BindingProtocolError
from azure.cosmos.exceptions import CosmosClientTimeoutError, CosmosHttpResponseError
from query_items.test_query_backend_routing_unit import (
    listing_client,
    _configure_legacy_database_feed,
    _next_listing_page,
)


@pytest.fixture(params=[False, True], ids=["rust", "legacy"])
def listing(listing_client, request):
    """Give each test the same client twice: once on the Rust path, once on the legacy one.

    The legacy run swaps in the old request method and has it return the same
    page the Rust stand-in would, so both paths answer identically and any
    difference in behavior is the code under test, not the stand-in.

    Both transports use the current listing configuration and pager. This
    fixture does not supply the released legacy API as a comparison baseline.

    Combined with the sync and async split it inherits, every test runs four
    ways.
    """
    client, connection, backend, is_async = listing_client
    legacy = request.param
    if legacy:
        _configure_legacy_database_feed(connection, is_async)
        client._backend = connection._backend

        def respond(*args, **kwargs):
            reply = backend._response
            headers = CaseInsensitiveDict(reply.headers)
            connection.last_response_headers = headers
            return json.loads(reply.body), headers

        connection._CosmosClientConnection__Get.side_effect = respond
    return client, connection, backend, is_async, legacy


def requests(listing):
    """Return whichever recorder counts calls for the path currently running.

    The two paths reach the service through different methods, so a test that
    wants to say "exactly one request went out" needs the right one. This keeps
    that choice in a single place rather than an if-check in every test.
    """
    _, connection, backend, _, legacy = listing
    return connection._CosmosClientConnection__Get if legacy else backend.execute_pages


@pytest.mark.asyncio
async def test_bookmark_is_owned_by_pager_even_when_hook_runs_other_work(listing):
    """The pager's continuation token comes from its own page, not from whatever the
    client did most recently.

    The callback is deliberately hostile: it empties the headers it was given
    and then points the client's shared record of the last response at some
    other operation, imitating a customer who runs a different query from inside
    their callback. The pager still reports its own position.

    Reading that shared record instead would be the bug, and a quiet one: the
    caller would save a position belonging to an unrelated call and resume the
    listing somewhere meaningless, skipping databases without any error.
    """
    client, connection, _, is_async, _ = listing
    def hook(headers):
        assert headers["x-ms-continuation"] == "next-db-page"
        headers.clear()
        connection.last_response_headers = CaseInsensitiveDict({"x-ms-continuation": "other-operation"})
    pager = client.list_databases(response_hook=hook).by_page()
    assert await _next_listing_page(pager, is_async)
    assert pager.continuation_token == "next-db-page"


@pytest.mark.asyncio
@pytest.mark.parametrize("status", [429, 410, 503])
async def test_callback_service_error_is_not_retried_or_swallowed(listing, status):
    """An error raised inside the customer's callback reaches them unchanged and does not
    cause a retry.

    The callback raises the three errors the SDK would normally retry on its
    own: too many requests, a container that moved, and service unavailable.
    Raised from a callback they are not retried, because the request already
    succeeded -- the failure is in the customer's code, and repeating the
    request would bill them again for something that will fail the same way.

    The exact error object is passed through, so their own handling still
    matches on it.

    Afterwards the pager refuses to continue. Its position is no longer known to
    be correct, so resuming could skip a page; a clear refusal beats silently
    missing databases.
    """
    client, _, _, is_async, _ = listing
    error = CosmosHttpResponseError(status_code=status, message="customer hook error")
    hook = MagicMock(side_effect=error)
    pager = client.list_databases(response_hook=hook).by_page()
    with pytest.raises(CosmosHttpResponseError) as raised:
        await _next_listing_page(pager, is_async)
    assert raised.value is error
    requests(listing).assert_called_once()
    hook.assert_called_once()
    with pytest.raises(RuntimeError, match="pager failed"):
        await _next_listing_page(pager, is_async)
    requests(listing).assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", [StopIteration, StopAsyncIteration])
async def test_iteration_stop_callback_cannot_hide_results(listing, kind):
    """A callback that raises one of the end-of-loop signals is reported as a real error
    rather than treated as the end of the list.

    Both the sync and async end-of-loop signals are covered. These are the
    values Python uses to mean "nothing more", so letting one escape a callback
    would end the listing quietly and hand the caller a short list of databases
    with no sign anything went wrong.

    Instead it becomes a plain error with the original attached as its cause, so
    the customer can still see what their callback raised.
    """
    client, _, _, is_async, _ = listing
    error = kind("customer hook error")
    pager = client.list_databases(response_hook=MagicMock(side_effect=error)).by_page()
    with pytest.raises(RuntimeError, match="iteration-stop") as raised:
        await _next_listing_page(pager, is_async)
    assert raised.value.__cause__ is error
    requests(listing).assert_called_once()


@pytest.mark.parametrize("hook", [False, 0, "not callable", {}])
def test_invalid_hook_rejected_without_request(listing, hook):
    """A callback that cannot be called is refused before any request goes out.

    Four values that are not callable are covered, including two that are
    falsey. Checking only whether a value is present would let those two through
    and then fail partway into the listing, after the caller had already been
    billed for a page.

    Nothing reaches the service, so the mistake costs nothing and points at the
    argument.
    """
    with pytest.raises(TypeError, match="callable"):
        listing[0].list_databases(response_hook=hook)
    requests(listing).assert_not_called()


@pytest.mark.parametrize("source", ["keyword", "request_options", "feed_options"])
@pytest.mark.parametrize(
    "name,key",
    [
        ("session_token", "sessionToken"),
        ("populate_query_metrics", "populateQueryMetrics"),
        ("availability_strategy", "availabilityStrategy"),
        ("no_response", "responsePayloadOnWriteDisabled"),
        ("content_type", "contentType"),
    ],
)
@pytest.mark.parametrize("value", [None, False, True, "customer-value"])
def test_inapplicable_options_rejected_through_each_input_route(listing, source, name, key, value):
    kwargs = {name: value} if source == "keyword" else {source: {key: value}}
    original = deepcopy(kwargs)
    with pytest.raises(TypeError, match=name):
        listing[0].list_databases(**kwargs)
    assert kwargs == original
    requests(listing).assert_not_called()


@pytest.mark.parametrize("source", ["initial_headers", "request_options", "feed_options", "raw_option", "default"])
@pytest.mark.parametrize("value", ["0", "-2", str(2**63), str(2**80), "True", "1.5", "invalid"])
def test_invalid_header_page_size_rejected_before_iteration(listing, source, value):
    client, connection, _, _, _ = listing
    headers = {"X-MS-MAX-ITEM-COUNT": value}
    if source == "default":
        connection.default_headers.update(headers)
        kwargs = {}
    elif source == "initial_headers":
        kwargs = {source: headers}
    elif source == "raw_option":
        kwargs = {"request_options": headers}
    else:
        kwargs = {source: {"initialHeaders": headers}}
    original = deepcopy(kwargs)
    with pytest.raises(ValueError, match="max.item.count"):
        client.list_databases(**kwargs)
    assert kwargs == original
    requests(listing).assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("count", [-1, 1, 2**63 - 1])
@pytest.mark.parametrize("typed", [False, True])
async def test_effective_page_size_is_validated_and_forwarded(listing, count, typed):
    client, connection, backend, is_async, legacy = listing
    connection.default_headers["x-ms-max-item-count"] = "0"
    headers = {"X-MS-MAX-ITEM-COUNT": "invalid" if typed else str(count)}
    options = {"initialHeaders": headers}
    kwargs = {"request_options": options, "max_item_count": count} if typed else {"feed_options": options}
    original = deepcopy(kwargs)
    pager = client.list_databases(**kwargs).by_page()
    assert kwargs == original
    headers["X-MS-MAX-ITEM-COUNT"] = "-2"
    assert await _next_listing_page(pager, is_async)
    if legacy:
        sent = CaseInsensitiveDict(requests(listing).call_args.args[2])
        assert str(sent["x-ms-max-item-count"]) == str(count)
    else:
        assert backend.prepared.max_item_count == count
        assert "x-ms-max-item-count" not in backend.prepared.headers
    assert options == {"initialHeaders": {"X-MS-MAX-ITEM-COUNT": "-2"}}


@pytest.mark.asyncio
async def test_raw_option_page_size_overrides_headers_without_mutation(listing):
    client, connection, backend, is_async, legacy = listing
    connection.default_headers["x-ms-max-item-count"] = "0"
    options = {"initialHeaders": {"X-MS-MAX-ITEM-COUNT": "-2"}, "X-MS-MAX-ITEM-COUNT": "3"}
    original = deepcopy(options)
    assert await _next_listing_page(client.list_databases(request_options=options).by_page(), is_async)
    if legacy:
        assert str(CaseInsensitiveDict(requests(listing).call_args.args[2])["x-ms-max-item-count"]) == "3"
    else:
        assert backend.prepared.max_item_count == 3
    assert options == original


@pytest.mark.asyncio
async def test_default_header_page_size_is_snapshotted(listing):
    client, connection, backend, is_async, legacy = listing
    connection.default_headers["X-MS-MAX-ITEM-COUNT"] = "2"
    pager = client.list_databases().by_page()
    connection.default_headers["X-MS-MAX-ITEM-COUNT"] = "0"
    assert await _next_listing_page(pager, is_async)
    if legacy:
        assert str(CaseInsensitiveDict(requests(listing).call_args.args[2])["x-ms-max-item-count"]) == "2"
    else:
        assert backend.prepared.max_item_count == 2


@pytest.mark.asyncio
@pytest.mark.parametrize("named_count", [None, 3])
async def test_effective_option_overrides_invalid_raw_page_sizes(listing, named_count):
    client, _, backend, is_async, legacy = listing
    options = {
        "initialHeaders": {"X-MS-MAX-ITEM-COUNT": "invalid"},
        "x-ms-max-item-count": "0",
        "maxItemCount": 2,
    }
    original = deepcopy(options)
    pages = client.list_databases(
        request_options=options, feed_options={"maxItemCount": -2}, max_item_count=named_count,
    )
    assert await _next_listing_page(pages.by_page(), is_async)
    count = 2 if named_count is None else named_count
    if legacy:
        assert str(CaseInsensitiveDict(requests(listing).call_args.args[2])["x-ms-max-item-count"]) == str(count)
    else:
        assert backend.prepared.max_item_count == count
    assert options == original


@pytest.mark.asyncio
@pytest.mark.parametrize("option_name", ["request_options", "feed_options"])
async def test_nested_input_is_copied_before_iteration(listing, option_name):
    """Options handed in are copied deeply, so later edits by the caller change nothing,
    and the SDK never writes into them.

    The headers inside the options are changed after the call is set up but
    before the first page is fetched, and the page still carries the original
    values. A shallow copy would fail here, because the headers live one level
    down.

    Nothing is written back either. The SDK tracks a start time and a position
    while listing, and both are kept in its own state -- a caller who reuses the
    same options for a second listing must not inherit a stale position from the
    first and silently resume in the middle.

    Both names for the same options are checked.
    """
    client, _, backend, is_async, legacy = listing
    headers = {"x-my-app": "original"}
    options = {"initialHeaders": headers, "maxItemCount": 2}
    pages = client.list_databases(**{option_name: options})
    assert options == {"initialHeaders": {"x-my-app": "original"}, "maxItemCount": 2}
    headers["x-my-app"] = "changed"
    options["maxItemCount"] = 99
    assert await _next_listing_page(pages.by_page(), is_async)
    if legacy:
        sent = requests(listing).call_args.args[2]
        assert sent["x-my-app"] == "original"
        assert str(sent["x-ms-max-item-count"]) == "2"
    else:
        assert backend.prepared.headers["x-my-app"] == "original"
        assert backend.prepared.max_item_count == 2
    assert "operationStartTime" not in options
    assert "continuation" not in options


@pytest.mark.asyncio
async def test_replay_does_not_change_an_existing_pagers_bookmark(listing):
    """Starting a second pager from a saved position leaves the first pager's position
    alone.

    One listing is used to start two pagers, the second from a different saved
    position, and each keeps its own. This is the ordinary shape of resuming
    work: a saved position is used later while the original listing is still
    open.

    If the position were kept on the shared listing rather than on each pager,
    the second would overwrite the first, and a caller holding the first would
    resume from somewhere it never reached.
    """
    client, _, backend, is_async, _ = listing
    items = client.list_databases()
    first = items.by_page()
    await _next_listing_page(first, is_async)
    backend._response = BackendResponse(
        status_code=200, headers=CaseInsensitiveDict(), body=b'{"Databases":[{"id":"last"}]}',
    )
    second = items.by_page("different-start")
    await _next_listing_page(second, is_async)
    assert second.continuation_token is None
    assert first.continuation_token == "next-db-page"


@pytest.mark.asyncio
@pytest.mark.parametrize("spent", [3.0, 4.75])
async def test_empty_service_page_uses_remaining_budget(listing, monkeypatch, spent):
    """Empty service pages share the timeout of the current public page fetch.

    The clock is controlled, and the service returns an empty first page that
    still points at more results -- which is normal, not an error. The first
    request is given the full limit; the second is given the limit minus the
    time the first actually took.

    Restarting the timeout after each empty service page could prevent the
    current public page fetch from ever timing out.
    Two different amounts of elapsed time are covered so the value is being
    subtracted rather than a fixed step.

    The callback still fires for the empty page, because an empty page is a real
    page the customer was charged for.
    """
    client, connection, backend, is_async, legacy = listing
    clock = [100.0]
    monkeypatch.setattr(time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(time, "time", lambda: clock[0])
    budgets = []
    pages = [
        BackendResponse(status_code=200, headers={"x-ms-continuation": "next"}, body=b'{"Databases":[]}'),
        BackendResponse(status_code=200, headers={}, body=b'{"Databases":[{"id":"last"}]}'),
    ]
    original = type(backend).execute_pages
    def response():
        page = pages[len(budgets) - 1]
        if len(budgets) == 1:
            clock[0] += spent
        return page
    if legacy:
        def legacy_request(*args, **kwargs):
            budgets.append(kwargs["timeout"])
            page = response()
            headers = CaseInsensitiveDict(page.headers)
            connection.last_response_headers = headers
            return json.loads(page.body), headers
        requests(listing).side_effect = legacy_request
    else:
        def execute(prepared, *, deadline=None):
            budgets.append(prepared.settings.timeout_seconds)
            assert deadline == 105
            backend._response = response()
            return original(backend, prepared, deadline=deadline)
        requests(listing).side_effect = execute
    hooks = []
    assert await _next_listing_page(client.list_databases(timeout=5, response_hook=hooks.append).by_page(), is_async)
    assert budgets == [5, 5 - spent]
    assert len(hooks) == 2


@pytest.mark.parametrize("timeout", [False, 0, 0.25, "5", float("nan"), float("inf"), 2**64])
def test_invalid_timeout_rejected_before_iteration(listing, timeout):
    """A time limit that is not a usable number is refused before any request goes out.

    Seven values are covered: false, zero, a fraction too small to be useful,
    text, not-a-number, infinity, and a number too large to fit. Each would fail
    differently and later -- text would break where it is compared, not-a-number
    compares false against everything so the limit would never appear to expire,
    and an oversized value overflows when handed to the driver.

    Refusing up front turns all of them into one clear message about the
    argument, at no cost.
    """
    with pytest.raises(ValueError, match="timeout"):
        listing[0].list_databases(timeout=timeout)
    requests(listing).assert_not_called()


@pytest.mark.parametrize("count", [False, 0, -2, 2.5, "2", 2**63])
def test_invalid_page_size_rejected_before_iteration(listing, count):
    """A page size that is not a whole positive number is refused before any request goes
    out.

    Six values are covered: false, zero, a negative number, a fraction, text,
    and a number too large to fit. False and zero matter most -- both would look
    like "no page size given" to a check that only asks whether a value is
    present, so the caller's mistake would be ignored and the service would
    choose a size instead.

    The message names the argument, so the fix is obvious.
    """
    with pytest.raises(ValueError, match="max_item_count"):
        listing[0].list_databases(max_item_count=count)
    requests(listing).assert_not_called()


@pytest.mark.asyncio
async def test_explicit_none_clears_nested_timeout(listing):
    """Passing no time limit directly beats a limit buried in the options, and the
    caller's options are left as they were.

    The argument the caller wrote at the call site is the more specific one, so
    an explicit "no limit" removes the one inherited from a shared options
    object. Treating it as "not supplied" instead would leave the caller unable
    to opt out of a limit they did not set.

    Their options object still reads the same afterwards, so the same object can
    be reused for another call without having been quietly emptied.
    """
    client, _, _, is_async, _ = listing
    options = {"timeout": 2}
    pager = client.list_databases(request_options=options, timeout=None).by_page()
    assert pager.state.config.timeout is None
    await _next_listing_page(pager, is_async)
    assert options == {"timeout": 2}


@pytest.mark.asyncio
@pytest.mark.parametrize("setup_seconds", [2, 4.75, 6])
async def test_real_rust_backend_deducts_setup_before_binding(listing_client, monkeypatch, setup_seconds):
    """Time spent starting the driver comes out of the caller's limit, and if it uses the
    limit up the call is abandoned before any request is sent.

    Starting the driver is not free the first time, and the clock is moved
    forward to imitate that. Under the limit, the driver is handed only what is
    left. At or over it, the call fails as a timeout and nothing is sent at all.

    Both ends matter. Not subtracting would let a call overrun by however long
    startup took; still sending after the limit had passed would bill the
    customer for a request whose answer is already too late to use.

    The real code path is used here rather than a stand-in, so this is where the
    subtraction actually happens.
    """
    client, _, backend, is_async = listing_client
    clock = [100.0]
    monkeypatch.setattr(time, "monotonic", lambda: clock[0])
    module = async_rust if is_async else sync_rust
    captured = []
    def acquire():
        clock[0] += setup_seconds
        return "offline"
    async def acquire_async():
        return acquire()
    def dispatch(handle, prepared, *, timeout_seconds):
        captured.append(timeout_seconds)
        return 200, 0, {}, b'{"Databases":[{"id":"sales"}]}'
    async def dispatch_async(handle, prepared, *, timeout_seconds):
        return dispatch(handle, prepared, timeout_seconds=timeout_seconds)
    backend._ensure_driver_handle = acquire_async if is_async else acquire
    execute = module.AsyncRustBinding.execute_pages if is_async else module.RustBinding.execute_pages
    backend.execute_pages = lambda prepared, deadline=None: execute(backend, prepared, deadline=deadline)
    monkeypatch.setattr(module, "_get_page_dispatch", lambda method: dispatch_async if is_async else dispatch)
    pager = client.list_databases(timeout=5).by_page()
    if setup_seconds >= 5:
        with pytest.raises(CosmosClientTimeoutError):
            await _next_listing_page(pager, is_async)
        assert captured == []
    else:
        await _next_listing_page(pager, is_async)
        assert captured == [5 - setup_seconds]


@pytest.mark.asyncio
async def test_async_cancellation_drains_page_work(listing_client):
    """Cancelling while a page is in flight unwinds the work and fires no callback.

    The fetch is made to hang, then cancelled. The cancellation reaches the
    caller as a cancellation, the hanging work is actually unwound instead of
    being left running, and the customer's callback never fires -- there was no
    page, so calling it would hand them nothing while looking like a result.

    Afterwards the pager refuses to continue, because nobody knows how far the
    cancelled fetch got. Resuming from a position that may or may not include
    that page could skip databases.

    Async only; there is nothing to cancel on the sync client.
    """
    client, _, backend, is_async = listing_client
    if not is_async:
        return
    started = asyncio.Event()
    stopped = asyncio.Event()
    async def execute(prepared, *, deadline=None):
        try:
            started.set()
            await asyncio.Event().wait()
            yield None
        finally:
            stopped.set()
    backend.execute_pages = execute
    hooks = []
    pager = client.list_databases(timeout=5, response_hook=hooks.append).by_page()
    task = asyncio.create_task(_next_listing_page(pager, True))
    await started.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert stopped.is_set()
    assert hooks == []
    with pytest.raises(RuntimeError, match="pager failed"):
        await _next_listing_page(pager, True)


@pytest.mark.asyncio
@pytest.mark.parametrize("seconds", [None, 0.25, 2])
async def test_native_listing_accepts_remaining_duration(listing_client, seconds):
    """The driver's own listing entry point accepts the remaining time in the forms Python
    will hand it.

    Three are covered: no limit at all, a fraction of a second, and a whole
    number of seconds. Fractions arise naturally once earlier time has been
    subtracted, so the entry point must take them rather than only whole
    seconds.

    An unknown client handle is used on purpose, so the call is refused for that
    reason after the arguments have been read. Reaching that refusal is the
    proof: a value the entry point could not accept would fail earlier and
    differently.
    """
    client, _, _, is_async = listing_client
    config = client.list_databases().by_page().state.config
    prepared = sync_rust.build_binding_request_from_page(config.prepared(None, None))
    function = _rust.list_databases_async if is_async else _rust.list_databases
    with pytest.raises(RuntimeError, match="(?i)driver"):
        result = function("unregistered-listing-review", prepared, timeout_seconds=seconds)
        if is_async:
            await result


@pytest.mark.asyncio
async def test_async_timeout_drains_page_and_prevents_hook(listing_client):
    """Running out of time mid-page unwinds the work and fires no callback.

    Only a fraction of the limit is left when the fetch starts, which is normal
    once earlier pages have used most of it. The fetch is made to hang, and the
    timeout surfaces as a timeout error.

    Two things must follow. The hanging work is unwound rather than left
    running, or it would hold the driver's resources for the life of the
    process. And the customer's callback is not called, because no page arrived.

    Async only.
    """
    client, _, backend, is_async = listing_client
    if not is_async:
        return
    stopped = asyncio.Event()
    async def execute(prepared, *, deadline=None):
        try:
            await asyncio.Event().wait()
            yield None
        finally:
            stopped.set()
    backend.execute_pages = execute
    hook = MagicMock()
    pager = client.list_databases(timeout=1, response_hook=hook).by_page()
    # A valid initial budget can have only a fraction remaining.
    pager.state.config.deadline = lambda: time.monotonic() + 0.02
    with pytest.raises(CosmosClientTimeoutError):
        await _next_listing_page(pager, True)
    assert stopped.is_set()
    hook.assert_not_called()


@pytest.mark.asyncio
async def test_failed_fetch_does_not_advance_delivered_bookmark(listing):
    """A failed fetch leaves the position where the last delivered page left it.

    One page is received, the next fetch is refused by the service, and the
    reported position still points just past the page the caller actually got.
    Moving it forward on a failure would mean a caller who saves it resumes past
    a page they never saw.

    The pager then refuses further use and the request count stays at two, so
    the refusal is not itself sending more requests.
    """
    client, _, _, is_async, _ = listing
    pager = client.list_databases().by_page()
    await _next_listing_page(pager, is_async)
    requests(listing).side_effect = CosmosHttpResponseError(status_code=403, message="denied")
    with pytest.raises(CosmosHttpResponseError):
        await _next_listing_page(pager, is_async)
    assert pager.continuation_token == "next-db-page"
    with pytest.raises(RuntimeError, match="pager failed"):
        await _next_listing_page(pager, is_async)
    assert requests(listing).call_count == 2


@pytest.mark.asyncio
async def test_concurrent_fetch_rejected_without_poisoning_first_fetch(listing_client):
    """Asking one pager for two pages at once is refused, and the fetch already running
    still completes normally.

    A fetch is held open, a second is attempted on the same pager and refused,
    then the first is released and returns its page. The pager is not left in a
    failed state.

    Both halves matter. Allowing both would have two fetches writing one
    position, so whichever finished last would win and a page could be lost. But
    the caller's mistake must not damage the fetch they started correctly --
    marking the pager failed would turn a recoverable misuse into a lost
    listing.

    Async only, since two fetches cannot overlap on the sync client this way.
    """
    client, _, backend, is_async = listing_client
    if not is_async:
        return
    started, release = asyncio.Event(), asyncio.Event()
    original = type(backend).execute_pages
    async def execute(prepared, *, deadline=None):
        started.set()
        await release.wait()
        async for page in original(backend, prepared, deadline=deadline):
            yield page
    backend.execute_pages = execute
    pager = client.list_databases().by_page()
    first = asyncio.create_task(_next_listing_page(pager, True))
    await started.wait()
    with pytest.raises(RuntimeError, match="Concurrent"):
        await _next_listing_page(pager, True)
    release.set()
    assert await first
    assert not pager.state.failed


@pytest.mark.asyncio
@pytest.mark.parametrize("body", [b"{}", b'{"Databases":{}}', b'{"Databases":[3]}'])
async def test_malformed_rust_page_is_an_explicit_error(listing_client, body):
    """A page that does not hold a proper list of databases is an error, not an empty
    result.

    Three shapes are covered: the list missing entirely, the list replaced by a
    set of values, and a list holding a number where a database should be.

    Each could plausibly be read as "no databases" by lenient code, and that is
    the danger -- a caller would see an empty list and conclude their account
    has none. The error names the part that was wrong instead.

    The customer's callback is not called, since there is no page to report.
    """
    client, _, backend, is_async = listing_client
    backend._response = BackendResponse(status_code=200, headers={}, body=body)
    hook = MagicMock()
    with pytest.raises(BindingProtocolError, match="invalid Databases"):
        await _next_listing_page(client.list_databases(response_hook=hook).by_page(), is_async)
    hook.assert_not_called()


@pytest.mark.asyncio
async def test_terminal_empty_page_clears_public_bookmark(listing):
    """Reaching the end of the list clears the position, so nothing is left to resume
    from.

    After a first page the position points at more results; after the final
    empty page the iteration ends and the position is cleared. Leaving the old
    value there would invite a caller to save it and fetch the same page again
    forever, since it would never look finished.

    The callback fired for both pages, including the empty final one, which was
    still a real request the customer paid for.
    """
    client, _, backend, is_async, _ = listing
    hook = MagicMock()
    pager = client.list_databases(response_hook=hook).by_page()
    await _next_listing_page(pager, is_async)
    assert pager.continuation_token == "next-db-page"
    backend._response = BackendResponse(status_code=200, headers={}, body=b'{"Databases":[]}')
    if is_async:
        with pytest.raises(StopAsyncIteration):
            await pager.__anext__()
    else:
        with pytest.raises(StopIteration):
            next(pager)
    assert pager.continuation_token is None
    assert hook.call_count == 2


@pytest.mark.asyncio
async def test_repeated_empty_page_bookmark_is_an_explicit_error(listing):
    """A page that is empty and hands back the position it was given is treated as an
    error rather than followed.

    Nothing was returned and the position did not move, so asking again would
    send the identical request and get the identical answer. Following it would
    be an endless loop of billed requests that never finishes and never fails --
    the worst kind of bug to diagnose from the outside.

    Exactly one request is made, and then it stops with a message naming the
    lack of progress.
    """
    client, _, backend, is_async, _ = listing
    backend._response = BackendResponse(
        status_code=200, headers={"x-ms-continuation": "same"}, body=b'{"Databases":[]}',
    )
    pager = client.list_databases().by_page("same")
    with pytest.raises(BindingProtocolError, match="without continuation progress"):
        await _next_listing_page(pager, is_async)
    requests(listing).assert_called_once()


def test_nested_public_sync_listing_preserves_outer_bookmark(listing):
    """A whole second listing run from inside the callback does not disturb the outer
    pager's position.

    The callback lists databases again, start to finish, on the same client.
    That is something customers really do -- look something up in response to a
    page they just received. The outer pager still reports its own position
    afterwards.

    This is the stronger version of the first test in the file: there the
    callback only tampered with shared values, here it drives a complete
    listing. Any position held on the client rather than the pager would be
    overwritten by the inner run.

    Sync only, since it depends on the inner listing finishing inside the
    callback.
    """
    client, _, backend, is_async, _ = listing
    if is_async:
        return
    def hook(headers):
        backend._response = BackendResponse(
            status_code=200, headers={}, body=b'{"Databases":[{"id":"nested"}]}',
        )
        assert list(client.list_databases()) == [{"id": "nested"}]
    pager = client.list_databases(response_hook=hook).by_page()
    assert list(next(pager))
    assert pager.continuation_token == "next-db-page"


def test_sync_guard_covers_public_bookmark_publication(listing):
    """The one-at-a-time protection is still in force while the position is being updated,
    not released a moment early.

    A second fetch is attempted from inside the step where the page is unpacked
    and the position recorded, and it is refused. The natural mistake is to drop
    the protection as soon as the request returns -- but the position has not
    been written yet at that point, so a second fetch slipping in there could
    overwrite it and lose a page.

    The original fetch then finishes normally, the position is correct, the
    pager is not left in a failed state, and only one request was ever sent.

    Sync only.
    """
    client, _, _, is_async, _ = listing
    if is_async:
        return
    pager = client.list_databases().by_page()
    original = pager._extract_data
    def extract(value):
        with pytest.raises(RuntimeError, match="Concurrent"):
            pager.next()
        return original(value)
    pager._extract_data = extract
    assert list(next(pager))
    assert pager.continuation_token == "next-db-page"
    assert not pager.state.failed
    requests(listing).assert_called_once()
