# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Read-many contracts without service calls, through both coordinators and proxies."""
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
    mode.proxy._get_properties_with_options = mode.mock(side_effect=AssertionError("metadata"))
    with pytest.raises(error):
        mode.run(mode.proxy.read_items(items, **kwargs))
    assert not mode.captured


def test_request_options_and_input_keys_are_snapshots(mode):
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
    helper = mode.make([("a", "p")], response_hook=MagicMock())
    helper.client._routing_map_provider.get_overlapping_ranges = mode.mock(return_value=ranges)
    with pytest.raises(CosmosHttpResponseError, match="unique physical range"):
        mode.run(helper.read_items())
    helper.client.QueryItems.assert_not_called()
    helper.kwargs["response_hook"].assert_not_called()


def test_typed_keys_do_not_share_routing_lookups(mode):
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
    query = _QueryBuilder.build_pk_and_id_in_query([("a", "p"), ("b", "p")], {"paths": [path]})
    assert f"{expression} = @pk_0" in query["query"]
    assert {"name": "@pk_0", "value": "p"} in query["parameters"]


def test_hierarchical_predicates_and_identity_preserve_null_and_undefined():
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
    helper = mode.make([("same", "a"), ("other", "a")], [(2, [{"id": "same", "pk": "wrong"}])])
    with pytest.raises(CosmosHttpResponseError, match="outside the requested"):
        mode.run(helper.read_items())


def test_metadata_consumes_budget_before_dispatch(mode, monkeypatch):
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
    method = (AsyncConnection if mode.asynchronous else CosmosClientConnection)._CosmosClientConnection__QueryFeed
    connection = MagicMock()
    options = {"_item_operation_deadline": time.monotonic() - 1, "timeout": 100,
               Constants.OperationStartTime: time.time()}
    with pytest.raises(CosmosClientTimeoutError):
        mode.run(method(connection, "/docs", "docs", "rid", lambda value: value, None, "SELECT * FROM c",
                        options=options))
    assert connection.mock_calls == []


def test_sync_routing_cache_lock_wait_is_bounded():
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
