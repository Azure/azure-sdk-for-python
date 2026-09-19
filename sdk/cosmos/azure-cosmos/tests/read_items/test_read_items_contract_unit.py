# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Read-many contract: batching, routing, ordering and time budget, with no service calls.

``read_items`` takes a list of ``(id, partition_key)`` pairs and has to turn
that into as few requests as possible. It groups the requested keys by the
physical partition range that owns them, then reads each group -- as a query
when a group holds several keys, or as a single point read when it holds one.
The results are then put back into the caller's original order.

That fan-out is where the interesting failures live, and most tests here
target one of four areas:

* **Identity and ordering.** ``True`` and ``1`` are different partition keys
  even though Python treats them as equal, duplicates must each get their own
  result, and missing ids are simply absent rather than an error.
* **Routing honesty.** If the SDK cannot work out exactly which partition
  owns a key, it must fail loudly. Quietly returning fewer items than were
  asked for would look like "those items do not exist".
* **One time budget.** ``timeout`` covers metadata, routing, and every page
  of every group together -- not each leg separately.
* **Isolation.** The caller's input list, options dict, and the objects handed
  to a response hook must all be copies.

Most tests take the ``mode`` fixture, so they run once sync and once async
against the real helper classes.
"""
import asyncio
import inspect
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos import CosmosList, _operation_deadline
from azure.cosmos import _base
from azure.cosmos._cosmos_client_connection import CosmosClientConnection
from azure.cosmos.aio._cosmos_client_connection_async import CosmosClientConnection as AsyncConnection
from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy
from azure.cosmos._routing.routing_map_provider import PartitionKeyRangeCache
from azure.cosmos._routing.aio.routing_map_provider import PartitionKeyRangeCache as AsyncRangeCache
from azure.cosmos._constants import _Constants as Constants, TimeoutScope
from azure.cosmos._helpers import _read_items
from azure.cosmos._helpers._read_items import (
    index_query_results, index_requested_items, normalize_read_items, partition_key_identity,
)
from azure.cosmos._query_builder import _QueryBuilder
from azure.cosmos._read_items_helper import ReadItemsHelperSync
from azure.cosmos.aio._read_items_helper_async import ReadItemsHelperAsync
from azure.cosmos.exceptions import CosmosClientTimeoutError, CosmosHttpResponseError
from azure.cosmos.partition_key import NonePartitionKeyValue, NullPartitionKeyValue, _Undefined

from .test_read_items_options_unit import _make_async_proxy, _make_sync_proxy
from read_item.test_read_item_contract_unit import point_read  # noqa: F401


DEFINITION = {"paths": ["/pk"], "kind": "Hash", "version": 2}
LINK = "dbs/db/colls/c"


class Feed:
    """A stand-in for a paged query result, usable from sync or async code.

    Built from ``(charge, rows)`` pairs, one per page. Iterating it calls the
    response hook once per page with that page's request charge and
    diagnostics string, then yields the rows -- which is how the tests check
    that per-page charges are added up rather than overwritten.

    ``__iter__`` serves the sync helper and ``by_page`` the async one, from
    the same page definitions, so both modes see identical data.
    """

    def __init__(self, pages, hook):
        self.pages = deepcopy(pages)
        self.hook = hook

    def __iter__(self):
        for charge, rows in self.pages:
            self.hook({"X-MS-REQUEST-CHARGE": str(charge), "x-ms-cosmos-sdk-diagnostics": f"page={charge}"}, rows)
            yield from rows

    def by_page(self):
        async def rows_in_page(rows):
            for row in rows:
                yield row

        async def pages():
            for charge, rows in self.pages:
                self.hook({"X-MS-REQUEST-CHARGE": str(charge), "x-ms-cosmos-sdk-diagnostics": f"page={charge}"}, rows)
                yield rows_in_page(rows)
        return pages()


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def mode(request):
    """Run the test twice: once against the sync helper, once against the async one.

    Returns a namespace holding everything a test needs to stay mode-agnostic:

    * ``run`` -- awaits a result if it is awaitable, otherwise returns it, so
      tests can call the helper without caring which mode they are in.
    * ``make`` -- builds a real ``ReadItemsHelper`` wired to a mocked
      connection whose routing returns a single range and whose ``QueryItems``
      returns a ``Feed`` of the supplied pages.
    * ``proxy`` / ``captured`` -- a real container proxy plus a record of what
      reached the connection, for tests that go through the public entry point.
    * ``mock`` -- ``AsyncMock`` or ``MagicMock`` to match the mode.
    """
    asynchronous = request.param
    mock = AsyncMock if asynchronous else MagicMock

    def run(value):
        return asyncio.run(value) if inspect.isawaitable(value) else value

    def make(items, pages=(), definition=None, **kwargs):
        connection = MagicMock()
        connection._routing_map_provider.get_overlapping_ranges = mock(return_value=[{"id": "0"}])
        connection.QueryItems.side_effect = lambda *a, **kw: Feed(pages, kw["response_hook"])
        helper = (ReadItemsHelperAsync if asynchronous else ReadItemsHelperSync)(
            connection, LINK, items, {}, definition or DEFINITION, **kwargs
        )
        return helper

    proxy, captured = (_make_async_proxy if asynchronous else _make_sync_proxy)()
    return SimpleNamespace(asynchronous=asynchronous, run=run, make=make, mock=mock, proxy=proxy, captured=captured)


def test_order_duplicate_occurrences_missing_items_and_all_page_charges(mode):
    """One batch exercises ordering, duplicates, missing ids and charge totals together.

    The request asks for five keys, one of which appears twice and one of
    which does not exist. The service answers out of order, across three
    pages, one of them empty.

    Four things must hold:

    * the results come back in the caller's order, not the service's;
    * the repeated key appears twice, as two separate objects -- sharing one
      object would let a caller mutating the first silently change the second;
    * the missing id is simply absent, not an error and not a gap;
    * the request charge is the **sum** over all pages (2 + 0.5 + 3), and the
      diagnostics string keeps every page. Overwriting instead of adding would
      under-report what the call actually cost.

    The hook fires once for the whole call, not once per page, and the
    internal marker that flags the query leg must not leak into the caller's
    options.
    """
    items = [("same", "a"), ("other", "a"), ("same", "b"), ("same", "a"), ("missing", "b")]
    pages = [
        (2, [{"id": "same", "pk": "b", "nested": [1]}]),
        (0.5, []),
        (3, [{"id": "other", "pk": "a"}, {"id": "same", "pk": "a", "nested": [2]}]),
    ]
    hook = MagicMock()
    helper = mode.make(items, pages, response_hook=hook)
    result = mode.run(helper.read_items())
    assert [(item["id"], item["pk"]) for item in result] == items[:-1]
    assert result.get_response_headers()["x-ms-request-charge"] == "5.5"
    assert result.get_response_headers()["x-ms-cosmos-sdk-diagnostics"] == "page=2; page=0.5; page=3"
    assert result[0] is not result[3] and result[0]["nested"] is not result[3]["nested"]
    hook.assert_called_once()
    call = helper.client.QueryItems.call_args
    assert call.args[2][Constants.ReadItemsQueryLeg] is True
    assert Constants.ReadItemsQueryLeg not in helper.options


@pytest.mark.parametrize("hook_kind", ["none", "mutating", "false-valued", "raising"])
def test_hook_isolation_and_no_replay(mode, hook_kind):
    """A response hook cannot corrupt the result, and never causes a second request.

    Four kinds of hook: absent, one that mutates everything it is handed, one
    that is falsey, and one that raises.

    The mutating hook edits the headers, the body's response headers, a nested
    list inside a row, and then clears the whole body. None of that may reach
    the caller's result: the rows survive, the charge is the real one, and the
    hook's added key is absent.

    The falsey hook must still be called -- a plain truth check would skip it.
    The raising hook's error reaches the caller unchanged.

    In every case the underlying query runs exactly once. A hook failure that
    triggered a retry would double-charge the customer for the same read.
    """
    calls = []

    class Hook:
        def __bool__(self):
            return False

        def __call__(self, headers, body):
            calls.append((headers, body))
            assert body.get_response_headers() is not headers
            headers["x-ms-request-charge"] = "changed"
            body.get_response_headers()["test"] = "changed"
            body[0]["nested"].append(99)
            body.clear()
            if hook_kind == "raising":
                raise RuntimeError("customer callback")

    callback = None if hook_kind == "none" else Hook()
    helper = mode.make(
        [("a", "p"), ("b", "p")],
        [(2, [{"id": "a", "pk": "p", "nested": [1]}, {"id": "b", "pk": "p"}])],
        response_hook=callback,
    )
    if hook_kind == "raising":
        with pytest.raises(RuntimeError, match="customer callback"):
            mode.run(helper.read_items())
    else:
        result = mode.run(helper.read_items())
        assert len(result) == 2 and result[0]["nested"] == [1]
        assert result.get_response_headers()["x-ms-request-charge"] == "2.0"
        assert "test" not in result.get_response_headers()
    assert len(calls) == (0 if callback is None else 1)
    helper.client.QueryItems.assert_called_once()


def test_empty_public_input_skips_metadata_and_calls_hook_once(mode):
    """Asking for nothing costs nothing, but still behaves like a real call.

    An empty batch must not trigger the container metadata lookup or any
    request -- the metadata call is rigged to fail the test if reached.

    It still returns a proper empty ``CosmosList`` and still calls the hook
    once, with empty headers and an empty body, so callers that rely on the
    hook firing do not have to special-case the empty batch. The body handed
    to the hook is a separate object from the returned one.
    """
    hook = MagicMock()
    mode.proxy._get_properties_with_options = mode.mock(side_effect=AssertionError("metadata"))
    result = mode.run(mode.proxy.read_items([], response_hook=hook))
    assert isinstance(result, CosmosList) and result == []
    hook.assert_called_once_with({}, [])
    assert hook.call_args.args[1] is not result
    assert not mode.captured


@pytest.mark.parametrize("items,kwargs,error", [
    (None, {}, TypeError), ("ab", {}, TypeError), ([("a",)], {}, TypeError),
    ([("a", "p", "extra")], {}, TypeError), ([(3, "p")], {}, TypeError),
    ([("", "p")], {}, ValueError), ([("a/b", "p")], {}, ValueError),
    ([("a", [])], {}, ValueError), ([("a", {"bad": 1})], {}, TypeError),
    ([("a", float("nan"))], {}, ValueError), ([("a", float("inf"))], {}, ValueError),
    ([("a", [object()])], {}, TypeError),
    ([], {"max_concurrency": 0}, ValueError), ([], {"max_concurrency": -1}, ValueError),
    ([], {"max_concurrency": True}, TypeError), ([], {"max_concurrency": 1.5}, TypeError),
    ([], {"response_hook": False}, TypeError), ([], {"timeout": 0.5}, ValueError),
    ([], {"timeout": float("nan")}, ValueError), ([], {"timeout": True}, ValueError),
])
def test_validation_before_metadata_including_empty_input(mode, items, kwargs, error):
    """Every bad argument is rejected before the metadata lookup, let alone a request.

    Covers three families:

    * the batch itself -- not a list, a string mistaken for a sequence, tuples
      of the wrong length, a non-string id, an empty or path-like id, and
      partition key values that are empty, wrongly typed, or not representable
      in JSON (``nan``, ``inf``, an arbitrary object);
    * ``max_concurrency`` -- zero, negative, a bool, a fraction;
    * ``response_hook`` and ``timeout`` -- wrong type, or a timeout too small
      to be meaningful.

    ``TypeError`` means the wrong type, ``ValueError`` means the right type
    with an unusable value. The rigged metadata call proves none of these get
    far enough to cost anything.
    """
    mode.proxy._get_properties_with_options = mode.mock(side_effect=AssertionError("metadata"))
    with pytest.raises(error):
        mode.run(mode.proxy.read_items(items, **kwargs))
    assert not mode.captured


def test_request_options_and_input_keys_are_snapshots(mode):
    """The caller's options dict and key list are copied, not adopted.

    The SDK merges ``session_token`` over ``request_options``, so it must work
    on a copy -- the caller's dict is compared against a deep copy taken
    beforehand and must be untouched.

    The same applies to the batch itself. Mutating a partition key value
    inside the original list after the call must not change what the SDK
    recorded, which means the keys were snapshotted rather than held by
    reference.
    """
    options = {"sessionToken": "old", "initialHeaders": {"x-test": "yes"}}
    before = deepcopy(options)
    keys = [("a", ["tenant", None])]
    mode.run(mode.proxy.read_items(keys, request_options=options, session_token="new"))
    assert options == before
    assert mode.captured["options"]["sessionToken"] == "new"
    keys[0][1][0] = "changed"
    assert mode.captured["kwargs"]["items"] == [("a", ["tenant", None])]


@pytest.mark.parametrize("ranges", [[], None, [{"id": "0"}, {"id": "1"}]])
def test_unresolved_or_ambiguous_routing_fails_instead_of_omitting_items(mode, ranges):
    """If routing cannot name one owning range, the call fails rather than returning less.

    Three bad answers: no ranges, ``None``, and two ranges for a single key.
    Each must raise, and neither the query nor the response hook may run.

    This is the safety rule behind the whole batch path. ``read_items``
    already returns fewer results than requested when items genuinely do not
    exist, so silently dropping a key the SDK merely could not route would be
    indistinguishable from "not found" -- a wrong answer that looks normal.
    """
    helper = mode.make([("a", "p")], response_hook=MagicMock())
    helper.client._routing_map_provider.get_overlapping_ranges = mode.mock(return_value=ranges)
    with pytest.raises(CosmosHttpResponseError, match="unique physical range"):
        mode.run(helper.read_items())
    helper.client.QueryItems.assert_not_called()
    helper.kwargs["response_hook"].assert_not_called()


def test_typed_keys_do_not_share_routing_lookups(mode):
    """Keys that Python considers equal still get their own routing lookup.

    ``True == 1`` and ``False == 0`` in Python, and ``None`` hashes like any
    other value, so a naive cache keyed on the raw value would collapse these
    six keys into fewer lookups and lose items.

    All six survive grouping, and routing is consulted six times -- the values
    are kept distinct by type, not just by equality.
    """
    helper = mode.make([("a", True), ("b", 1), ("c", False), ("d", 0), ("e", None), ("f", NonePartitionKeyValue)])
    groups = mode.run(helper._partition_items_by_range())
    assert len(groups["0"]) == 6
    assert helper.client._routing_map_provider.get_overlapping_ranges.call_count == 6


@pytest.mark.parametrize("path,expression", [
    ("/tenant/id", 'c["tenant"]["id"]'),
    ('/"tenant/id"', 'c["tenant/id"]'),
    ("/a-b", 'c["a-b"]'),
    ("/na\u00efve", 'c["na\\u00efve"]'),
])
def test_single_partition_queries_use_escaped_path_components(path, expression):
    """Partition key paths are turned into bracket syntax, never pasted into the query.

    A nested path becomes chained brackets, a quoted path keeps its embedded
    slash as one component, a hyphenated name stays valid, and a non-ASCII
    name is escaped.

    Bracket syntax with bound parameters is what keeps a container whose
    partition key path contains punctuation from producing invalid -- or
    injectable -- SQL. The value itself always travels as ``@pk_0``.
    """
    query = _QueryBuilder.build_pk_and_id_in_query([("a", "p"), ("b", "p")], {"paths": [path]})
    assert f"{expression} = @pk_0" in query["query"]
    assert {"name": "@pk_0", "value": "p"} in query["parameters"]


def test_hierarchical_predicates_and_identity_preserve_null_and_undefined():
    """With hierarchical keys, a null component and a missing one stay different.

    For a two-level key, the query compares both components joined by ``AND``,
    and a ``None`` component is bound as SQL ``NULL`` -- a real value.

    A component that is *absent* is a different thing, and is matched with
    ``IS_DEFINED(...) = false``. The mixed batch emits that test exactly once,
    so the two senses are not merged.

    The last part matters most: three requested keys, two of which are
    identical, are matched against only two returned rows, and all three
    original positions still come back. The row that stored ``user: null``
    does not get confused with the row where ``user`` is missing.
    """
    definition = {"paths": ["/tenant/id", "/user"], "kind": "MultiHash"}
    items = [(0, "same", ["t", None]), (1, "same", ["t", NonePartitionKeyValue]),
             (2, "same", ["t", None])]
    query = _QueryBuilder.build_pk_and_id_in_query(
        [("a", ["t", None]), ("b", ["t", None])], definition
    )
    assert 'c["tenant"]["id"] = @pk_0 AND c["user"] = @pk_1' in query["query"]
    assert {"name": "@pk_1", "value": None} in query["parameters"]
    mixed = _QueryBuilder.build_parameterized_query_for_items({"0": [(i, k) for _, i, k in items]}, definition)
    assert mixed["query"].count('IS_DEFINED(c["user"]) = false') == 1
    indexed = index_query_results(
        [{"id": "same", "tenant": {"id": "t"}}, {"id": "same", "tenant": {"id": "t"}, "user": None}],
        index_requested_items(items), definition,
    )
    assert sorted(index for index, _ in indexed) == [0, 1, 2]
    assert "user" not in next(row for index, row in indexed if index == 1)


def test_typed_identity_and_logical_partition_classification():
    """The rules for when two partition key values count as the same one.

    Different: ``True`` vs ``1`` and ``False`` vs ``0``, because type is part
    of the identity. Also ``None`` vs the "no partition key" marker -- one is
    a stored null, the other is an absent key.

    The same: ``1`` and ``1.0``, since JSON has a single number type; and
    ``None`` and the explicit null marker, which are two spellings of null.
    An empty dict and the "undefined" marker are likewise one value.

    Because ``True`` and ``1`` are distinct, a batch holding both is not a
    single-partition batch and cannot use the cheaper single-partition query.

    Finally, a hierarchical key must be given in full: supplying one component
    of a two-component key is rejected rather than guessed at.
    """
    assert partition_key_identity(True) != partition_key_identity(1)
    assert partition_key_identity(False) != partition_key_identity(0)
    assert partition_key_identity(1) == partition_key_identity(1.0)
    assert partition_key_identity(None) == partition_key_identity(NullPartitionKeyValue)
    assert partition_key_identity(None) != partition_key_identity(NonePartitionKeyValue)
    assert partition_key_identity({}) == partition_key_identity(_Undefined())
    assert not _QueryBuilder.is_single_logical_partition_query([("a", True), ("b", 1)])
    with pytest.raises(ValueError, match="every component"):
        normalize_read_items([("a", ["t"])], {"paths": ["/tenant", "/user"], "kind": "MultiHash"})


def test_wrong_partition_response_is_not_accepted_by_id(mode):
    """A row is matched on id *and* partition key, so a stray row is an error.

    Two items are requested from partition ``a`` and the service answers with
    the right id but partition ``b``. Matching on id alone would hand the
    caller an item they never asked for, under a key they do not own, so the
    call raises instead.
    """
    helper = mode.make([("same", "a"), ("other", "a")], [(2, [{"id": "same", "pk": "wrong"}])])
    with pytest.raises(CosmosHttpResponseError, match="outside the requested"):
        mode.run(helper.read_items())


def test_metadata_consumes_budget_before_dispatch(mode, monkeypatch):
    """Time spent reading container metadata comes out of the caller's timeout.

    With a fake clock, a 5 second timeout, and a metadata lookup that takes 6
    seconds, the call must time out. The metadata lookup also has to see the
    deadline, so it can bound itself rather than run unlimited.

    Nothing reaches the connection. Restarting the budget after metadata would
    let a ``timeout=5`` call take far longer than five seconds.
    """
    clock = SimpleNamespace(monotonic=lambda: clock.now, time=lambda: clock.now, now=100.0)
    monkeypatch.setattr(_read_items, "time", clock)
    monkeypatch.setattr(_operation_deadline, "time", clock)

    def metadata(options):
        assert options["_item_operation_deadline"] == 105.0
        clock.now += 6
    mode.proxy._get_properties_with_options = mode.mock(side_effect=metadata)
    with pytest.raises(CosmosClientTimeoutError):
        mode.run(mode.proxy.read_items([("a", "p")], timeout=5))
    assert not mode.captured


def test_routing_consumes_budget_before_any_item(mode, monkeypatch):
    """The routing lookup is inside the budget too, and exhausting it stops the read.

    Routing is handed the remaining 5 seconds, then burns 6. The call times
    out and not a single item is read.

    Same rule as metadata, one stage later: every preparation step spends the
    caller's time, and once it is gone no request is sent.
    """
    clock = SimpleNamespace(monotonic=lambda: clock.now, time=lambda: clock.now, now=100.0)
    monkeypatch.setattr(_operation_deadline, "time", clock)
    helper = mode.make([("a", "p")], _item_operation_deadline=105.0)

    def routing(*args):
        assert args[2]["timeout"] == 5.0
        clock.now = 106
        return [{"id": "0"}]
    helper.client._routing_map_provider.get_overlapping_ranges = mode.mock(side_effect=routing)
    helper._execute_point_read = mode.mock()
    with pytest.raises(CosmosClientTimeoutError):
        mode.run(helper.read_items())
    helper._execute_point_read.assert_not_called()


def test_native_point_leg_receives_remaining_read_many_budget(point_read):
    """An existing deadline limits the point leg more tightly than timeout=5.

    The fixture starts with 0.5 seconds remaining; simulated metadata consumes
    0.2 seconds, leaving about 0.3 for the read. Both dispatch paths are mocked.
    """
    context = point_read
    context.clock.time = context.clock.monotonic
    context.metadata_delay = 0.2
    if not context.rust:
        metadata = context.proxy.read.side_effect

        def read_container(_link, options, **kwargs):
            return metadata(timeout=options.get("timeout"))

        context.cc.ReadContainer = (
            AsyncMock if isinstance(context.proxy.read, AsyncMock) else MagicMock
        )(side_effect=read_container)
        legacy_read = context.cc.ReadItem.side_effect

        def read_with_hook(**kwargs):
            hook = kwargs.pop("response_hook", None)
            result = legacy_read(**kwargs)
            if hook is not None:
                hook(result.get_response_headers(), result)
            return result
        context.cc.ReadItem.side_effect = read_with_hook
    kwargs = {"timeout": 5, "_item_operation_deadline": 100.5}
    helper = (ReadItemsHelperAsync if isinstance(context.proxy, AsyncContainerProxy) else ReadItemsHelperSync)(
        context.cc, LINK, [("item", "p")], {}, DEFINITION,
        _item_context=context.proxy._item_context, **kwargs,
    )
    result = helper._execute_point_read("item", "p", dict(kwargs))
    if inspect.isawaitable(result):
        result = asyncio.run(result)
    assert result[0]["id"] == "item"
    assert context.events == [("metadata", 0.5), ("read", pytest.approx(0.3))]


def test_public_hook_timeout_error_is_not_reclassified(mode):
    """A ``TimeoutError`` raised by the caller's own hook reaches them unchanged.

    The hook raises ``TimeoutError``, and the exact object the caller raised
    comes back out -- not a ``CosmosClientTimeoutError``.

    The SDK raises its own timeout type when *it* runs out of budget, so
    blanket-converting any ``TimeoutError`` would relabel the caller's bug as
    an SDK timeout and send them looking in the wrong place.
    """
    error = TimeoutError("customer callback, not the operation timer")

    def hook(_headers, _body):
        raise error

    helper = mode.make([("a", "p"), ("b", "p")], [(2, [{"id": "a", "pk": "p"}])], response_hook=hook)

    async def async_read(**kwargs):
        return await helper.read_items()

    def sync_read(**kwargs):
        return helper.read_items()

    mode.proxy.client_connection.read_items = async_read if mode.asynchronous else sync_read
    with pytest.raises(TimeoutError) as raised:
        mode.run(mode.proxy.read_items([("a", "p"), ("b", "p")], timeout=5, response_hook=hook))
    assert raised.value is error


@pytest.mark.asyncio
@pytest.mark.parametrize("cancel", [False, True])
async def test_async_timeout_or_caller_cancellation_drains_work(cancel):
    """Timeout and cancellation both stop cleanly and leave no task running.

    Two items in two ranges with a concurrency of one, so the second is still
    queued while the first hangs forever. The run then ends either by the
    deadline passing or by the caller cancelling the task.

    Either way: the right error surfaces -- ``CancelledError`` when the caller
    cancelled, ``CosmosClientTimeoutError`` when time ran out -- the in-flight
    read's cleanup block runs, and the queued second item never starts.

    A leaked task here would keep using a connection after the caller has
    moved on.
    """
    entered, cleaned = asyncio.Event(), asyncio.Event()
    helper = ReadItemsHelperAsync(MagicMock(), LINK, [("a", "p"), ("b", "q")], {}, DEFINITION,
                                  max_concurrency=1, _item_operation_deadline=None if cancel else time.monotonic() + 0.05)
    helper._partition_items_by_range = AsyncMock(return_value={"0": [(0, "a", "p")], "1": [(1, "b", "q")]})
    called = []

    async def read(item_id, *args):
        called.append(item_id)
        entered.set()
        try:
            await asyncio.Event().wait()
        finally:
            cleaned.set()
    helper._execute_point_read = read
    task = asyncio.create_task(helper.read_items())
    await entered.wait()
    if cancel:
        task.cancel()
    with pytest.raises(asyncio.CancelledError if cancel else CosmosClientTimeoutError):
        await task
    assert cleaned.is_set()
    assert called == ["a"]


@pytest.mark.parametrize("owned", [False, True])
def test_sync_timeout_does_not_wait_for_running_work_or_start_queued_work(owned):
    """A sync timeout returns straight away and does not break a borrowed thread pool.

    Threads cannot be cancelled, so the rule is different from async: on
    timeout the caller is released immediately rather than blocked until the
    running read finishes. The running read is held open for the whole test,
    and the assertion inside it fails the test if the caller waited.

    The queued second item never starts, and when the caller supplied their
    own executor it is still usable afterwards -- the SDK shuts down only a
    pool it created itself. Shutting down a borrowed pool would break
    unrelated work in the caller's application.
    """
    release, entered = threading.Event(), threading.Event()
    external = None if owned else ThreadPoolExecutor(max_workers=1)
    helper = ReadItemsHelperSync(MagicMock(), LINK, [("a", "p"), ("b", "q")], {}, DEFINITION,
                                 max_concurrency=1, executor=external,
                                 _item_operation_deadline=time.monotonic() + 0.1)
    helper._partition_items_by_range = MagicMock(return_value={"0": [(0, "a", "p")], "1": [(1, "b", "q")]})
    calls = []

    def read(item_id, *args):
        calls.append(item_id)
        entered.set()
        assert release.wait(3), "caller waited for already-running work after timeout"
        return {"id": item_id}, CaseInsensitiveDict()
    helper._execute_point_read = read
    try:
        with pytest.raises(CosmosClientTimeoutError):
            helper.read_items()
        assert entered.is_set()
        assert calls == ["a"]
    finally:
        release.set()
        if external is not None:
            assert external.submit(lambda: 42).result(timeout=3) == 42
            external.shutdown()


def test_query_budget_is_not_restarted_between_pages(mode, monkeypatch):
    """Paging through a query does not hand each page a fresh timeout.

    The first page arrives, then the clock jumps past the deadline before the
    second. The call must time out mid-paging.

    The query is checked to receive the *remaining* 5 seconds scoped to the
    whole operation, and the internal deadline keys must not leak through to
    the query as keyword arguments. If each page restarted the clock, a query
    with many pages could run for arbitrarily long under a short timeout.
    """
    clock = SimpleNamespace(monotonic=lambda: clock.now, time=lambda: clock.now, now=100.0)
    monkeypatch.setattr(_operation_deadline, "time", clock)
    helper = mode.make([("a", "p"), ("b", "p")], _item_operation_deadline=105.0, timeout=10)

    class ExpiringFeed(Feed):
        def __iter__(self):
            yield {"id": "a", "pk": "p"}
            clock.now = 106.0
            yield {"id": "b", "pk": "p"}

        def by_page(self):
            async def rows():
                for row in self:
                    yield row
            async def pages():
                yield rows()
            return pages()

    def query(*args, **kwargs):
        assert args[2]["timeout"] == 5.0
        assert args[2][Constants.TimeoutScope] == TimeoutScope.OPERATION
        assert "timeout" not in kwargs and "_item_operation_deadline" not in kwargs
        return ExpiringFeed([], kwargs["response_hook"])
    helper.client.QueryItems.side_effect = query
    with pytest.raises(CosmosClientTimeoutError):
        mode.run(helper.read_items())


def test_legacy_page_dispatch_checks_absolute_deadline_before_transport(mode):
    """An already-expired deadline stops the legacy query path before it touches the network.

    The deadline is in the past while the per-request timeout still says 100
    seconds. The deadline wins, and the connection records no calls at all.

    Checking the absolute deadline first is what stops an expired operation
    from opening one more connection on its way out.
    """
    method = (AsyncConnection if mode.asynchronous else CosmosClientConnection)._CosmosClientConnection__QueryFeed
    connection = MagicMock()
    options = {"_item_operation_deadline": time.monotonic() - 1, "timeout": 100,
               Constants.OperationStartTime: time.time()}
    with pytest.raises(CosmosClientTimeoutError):
        mode.run(method(connection, "/docs", "docs", "rid", lambda value: value, None, "SELECT * FROM c",
                        options=options))
    assert connection.mock_calls == []


def test_sync_routing_cache_lock_wait_is_bounded():
    """Waiting for another thread's routing refresh is bounded by the deadline.

    The routing cache serialises refreshes per container so several threads do
    not all reload the same map. With the lock already held elsewhere, a
    caller arriving with a 30 millisecond budget must give up with a timeout
    instead of waiting indefinitely.

    It must also not sneak past: the underlying range read is never called,
    and the lock is left held by its real owner.
    """
    provider = PartitionKeyRangeCache(MagicMock())
    key = _base.GetResourceIdOrFullNameFromLink(LINK)
    lock = provider._get_lock_for_collection(key)
    lock.acquire()
    try:
        with pytest.raises(CosmosClientTimeoutError):
            provider.get_routing_map(LINK, {"_item_operation_deadline": time.monotonic() + 0.03})
        provider._document_client._ReadPartitionKeyRanges.assert_not_called()
        assert lock.locked()
    finally:
        lock.release()
        provider.release()


@pytest.mark.asyncio
async def test_async_routing_cache_lock_wait_is_bounded():
    """The async routing cache bounds its lock wait exactly like the sync one.

    Same setup with the async cache: the lock is held, the arriving caller has
    30 milliseconds, and it times out without reading ranges and without
    disturbing the lock. Kept as a separate test because the two caches use
    different lock types and the bound is easy to lose in one of them.
    """
    provider = AsyncRangeCache(MagicMock())
    key = _base.GetResourceIdOrFullNameFromLink(LINK)
    lock = await provider._get_lock_for_collection(key)
    await lock.acquire()
    try:
        with pytest.raises(CosmosClientTimeoutError):
            await provider.get_routing_map(LINK, {"_item_operation_deadline": time.monotonic() + 0.03})
        provider._document_client._ReadPartitionKeyRanges.assert_not_called()
        assert lock.locked()
    finally:
        lock.release()
        provider.release()


def test_routing_change_feed_pages_consume_one_budget(mode, monkeypatch):
    """Refreshing the routing map across pages spends a single shared budget.

    The range list arrives over two pages and each takes 1.5 seconds. Starting
    from a 5 second budget, the pages are handed 5.0 then 3.5 -- the second
    page sees what the first left behind, not another full 5.

    Both pages are scoped to the operation rather than the request, so a
    routing refresh that needs several pages cannot outlast the read that
    triggered it.
    """
    clock = SimpleNamespace(monotonic=lambda: clock.now, time=lambda: clock.now, now=100.0)
    monkeypatch.setattr(_operation_deadline, "time", clock)
    connection = MagicMock()
    budgets = []

    def get_page(_link, options, **kwargs):
        budgets.append(options["timeout"])
        assert options[Constants.TimeoutScope] == TimeoutScope.OPERATION
        kwargs["_internal_response_headers_capture"]["etag"] = "v1"
        kwargs["_internal_response_status_capture"][0] = 200 if len(budgets) == 1 else 304
        clock.now += 1.5
        return [{"id": "0", "minInclusive": "", "maxExclusive": "FF"}] if len(budgets) == 1 else []

    def sync_pages(*args, **kwargs):
        yield from get_page(*args, **kwargs)

    async def async_pages(*args, **kwargs):
        for value in get_page(*args, **kwargs):
            yield value
    connection._ReadPartitionKeyRanges = async_pages if mode.asynchronous else sync_pages
    provider = (AsyncRangeCache if mode.asynchronous else PartitionKeyRangeCache)(connection)
    try:
        mode.run(provider.get_routing_map(LINK, {"_item_operation_deadline": 105.0}))
        assert budgets == [5.0, 3.5]
    finally:
        provider.release()
