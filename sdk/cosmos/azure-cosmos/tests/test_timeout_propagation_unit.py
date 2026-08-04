# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Unit tests for per-call timeout propagation to the container read, query
plan, and partition-key ranges metadata calls.

These tests are deliberately mock-light and do not touch the network, so they
validate the propagation logic in isolation:

* ``build_options`` carries ``connection_timeout`` into the options dict.
* ``_copy_per_call_timeouts_to_options`` forwards only the timeouts actually set,
  plus the operation start time (``OperationStartTime``) when present.
* ``_build_routing_feed_options`` builds a fresh routing feed_options dict that
  copies the requested routing keys and carries the per-call timeouts.
* ``format_pk_range_options`` carries the timers and the operation start time.
* The query-plan dispatcher (sync + async) forwards the per-call timeouts and
  ``OperationStartTime`` only when set -- never as ``None`` -- so an unset value
  cannot override the client/policy default in the request layer.
* The container read (``_get_properties_with_options``) copies the timeouts and
  the operation start time from options into the kwargs it hands down.
"""

import unittest
from unittest import mock

import pytest

from azure.cosmos import _base
from azure.cosmos import exceptions
from azure.cosmos import http_constants
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos.container import ContainerProxy
from azure.cosmos._cosmos_client_connection import CosmosClientConnection as _SyncCosmosClientConnection
from azure.cosmos.aio._cosmos_client_connection_async import CosmosClientConnection as _AsyncCosmosClientConnection
from azure.cosmos._execution_context.execution_dispatcher import _ProxyQueryExecutionContext
from azure.cosmos._execution_context.aio.execution_dispatcher import (
    _ProxyQueryExecutionContext as _AsyncProxyQueryExecutionContext,
)
from azure.cosmos._execution_context.hybrid_search_aggregator import _HybridSearchContextAggregator
from azure.cosmos._execution_context.aio.hybrid_search_aggregator import (
    _HybridSearchContextAggregator as _AsyncHybridSearchContextAggregator,
)
from azure.cosmos._change_feed import change_feed_fetcher as cff
from azure.cosmos._change_feed.aio import change_feed_fetcher as cff_async
from azure.cosmos._change_feed.change_feed_state import ChangeFeedStateVersion


class _StopBeforePipeline(Exception):
    """Raised by the recording client's query-plan stub to short-circuit
    ``_create_execution_context_with_query_plan`` right after the gateway call,
    before it tries to build a real pipelined execution context."""


class _RecordingQueryPlanClient:
    """Minimal stand-in for CosmosClientConnection that records the kwargs the
    query-plan dispatcher forwards to ``_GetQueryPlanThroughGateway``."""

    def __init__(self):
        self.captured_kwargs = None

    def _GetQueryPlanThroughGateway(self, query, resource_link, excluded_locations=None, **kwargs):
        self.captured_kwargs = dict(kwargs)
        raise _StopBeforePipeline()


class _AsyncRecordingQueryPlanClient:
    """Async counterpart of :class:`_RecordingQueryPlanClient`."""

    def __init__(self):
        self.captured_kwargs = None

    async def _GetQueryPlanThroughGateway(self, query, resource_link, excluded_locations=None, **kwargs):
        self.captured_kwargs = dict(kwargs)
        raise _StopBeforePipeline()


def _noop_fetch(_options):
    return [], {}


class TestBuildOptionsConnectionTimeout(unittest.TestCase):
    """build_options copies connection_timeout into the options dict (like
    read_timeout and timeout) while leaving it in kwargs for the page fetch."""

    def test_connection_timeout_copied_into_options(self):
        kwargs = {"connection_timeout": 0.5, "read_timeout": 30, "timeout": 2}
        options = _base.build_options(kwargs)
        assert options[Constants.Kwargs.CONNECTION_TIMEOUT] == 0.5
        assert options[Constants.Kwargs.READ_TIMEOUT] == 30
        assert options[Constants.Kwargs.TIMEOUT] == 2

    def test_connection_timeout_stays_in_kwargs(self):
        # A copy (not a pop): the page fetch consumes connection_timeout from
        # kwargs, so build_options must not remove it.
        kwargs = {"connection_timeout": 0.5}
        _base.build_options(kwargs)
        assert kwargs["connection_timeout"] == 0.5

    def test_connection_timeout_absent_not_added(self):
        options = _base.build_options({})
        assert Constants.Kwargs.CONNECTION_TIMEOUT not in options


class TestCopyPerCallTimeoutsToOptions(unittest.TestCase):
    """The shared helper that copies the per-call timeouts into an options dict."""

    def test_carries_only_present_keys(self):
        destination = {}
        _base._copy_per_call_timeouts_to_options(
            {"read_timeout": 30, "timeout": 2, "unrelated": 9}, destination
        )
        assert destination == {"read_timeout": 30, "timeout": 2}

    def test_explicit_none_value_is_skipped(self):
        # Mirrors _copy_per_call_timeouts_to_kwargs: an explicit None must not be
        # carried, or an intermediate options dict could reintroduce a
        # read_timeout=None that disables the socket read timeout downstream.
        destination = {}
        _base._copy_per_call_timeouts_to_options(
            {"read_timeout": None, "connection_timeout": None, "timeout": 2}, destination
        )
        assert destination == {"timeout": 2}

    def test_empty_source_leaves_destination_untouched(self):
        destination = {"containerRID": "rid"}
        _base._copy_per_call_timeouts_to_options({}, destination)
        assert destination == {"containerRID": "rid"}

    def test_none_source_is_noop(self):
        # A None source must be a no-op rather than raising, mirroring the
        # options->kwargs helper. Callers today never pass None, so this guards
        # against a latent TypeError if a future caller does.
        destination = {"containerRID": "rid"}
        _base._copy_per_call_timeouts_to_options(None, destination)
        assert destination == {"containerRID": "rid"}


class TestBuildRoutingFeedOptions(unittest.TestCase):
    """The shared builder every side path uses to construct a routing/pkranges
    feed_options dict: it copies the requested routing keys and carries the timers."""

    def test_copies_requested_keys_and_timers(self):
        source = {
            "containerRID": "rid",
            "excludedLocations": ["West US"],
            "read_timeout": 30,
            "connection_timeout": 0.5,
            "timeout": 2,
            Constants.OperationStartTime: 123.0,
            "unrelated": 9,
        }
        feed_options = _base._build_routing_feed_options(
            source, ("excludedLocations", Constants.ContainerRID))
        assert feed_options == {
            "containerRID": "rid",
            "excludedLocations": ["West US"],
            "read_timeout": 30,
            "connection_timeout": 0.5,
            "timeout": 2,
            Constants.OperationStartTime: 123.0,
        }

    def test_copies_only_requested_routing_keys(self):
        # The hybrid all-ranges path asks for containerRID only, so excludedLocations
        # must not leak in and change its region routing.
        source = {"containerRID": "rid", "excludedLocations": ["West US"], "read_timeout": 30}
        feed_options = _base._build_routing_feed_options(source, (Constants.ContainerRID,))
        assert feed_options == {"containerRID": "rid", "read_timeout": 30}

    def test_default_copies_no_routing_keys(self):
        feed_options = _base._build_routing_feed_options({"read_timeout": 30, "containerRID": "rid"})
        assert feed_options == {"read_timeout": 30}

    def test_none_or_empty_source_returns_empty_dict(self):
        assert _base._build_routing_feed_options(None, ("excludedLocations",)) == {}
        assert _base._build_routing_feed_options({}, ("excludedLocations",)) == {}



def _make_sync_ctx(client, options):
    return _ProxyQueryExecutionContext(
        client,
        "dbs/db/colls/coll",
        "SELECT * FROM c",
        options,
        _noop_fetch,
        None,
        None,
        "docs",
    )


def _make_async_ctx(client, options):
    return _AsyncProxyQueryExecutionContext(
        client,
        "dbs/db/colls/coll",
        "SELECT * FROM c",
        options,
        _noop_fetch,
        None,
        None,
        "docs",
    )


class TestQueryPlanDispatcherForwarding(unittest.TestCase):
    """The sync query-plan dispatcher forwards the per-call timeouts, and does
    not pass connection_timeout or timeout as None when the caller left them
    unset."""

    def test_forwards_all_three_when_set(self):
        client = _RecordingQueryPlanClient()
        ctx = _make_sync_ctx(client, {"read_timeout": 30, "connection_timeout": 0.5, "timeout": 2})
        with pytest.raises(_StopBeforePipeline):
            ctx._create_execution_context_with_query_plan()
        assert client.captured_kwargs == {
            "read_timeout": 30,
            "connection_timeout": 0.5,
            "timeout": 2,
        }

    def test_omits_all_timeouts_when_unset(self):
        # No timer is forwarded as None: each goes to the request as a kwarg, where
        # None would override the client default. An unset timer is omitted so
        # _Request falls back to the policy default.
        client = _RecordingQueryPlanClient()
        ctx = _make_sync_ctx(client, {})
        with pytest.raises(_StopBeforePipeline):
            ctx._create_execution_context_with_query_plan()
        assert client.captured_kwargs == {}

    def test_forwards_only_connection_timeout_when_only_it_is_set(self):
        client = _RecordingQueryPlanClient()
        ctx = _make_sync_ctx(client, {"connection_timeout": 0.5})
        with pytest.raises(_StopBeforePipeline):
            ctx._create_execution_context_with_query_plan()
        assert client.captured_kwargs == {"connection_timeout": 0.5}


class TestAsyncQueryPlanDispatcherForwarding(unittest.IsolatedAsyncioTestCase):
    """The async query-plan dispatcher has the same contract as the sync one."""

    async def test_forwards_all_three_when_set(self):
        client = _AsyncRecordingQueryPlanClient()
        ctx = _make_async_ctx(client, {"read_timeout": 30, "connection_timeout": 0.5, "timeout": 2})
        with pytest.raises(_StopBeforePipeline):
            await ctx._create_execution_context_with_query_plan()
        assert client.captured_kwargs == {
            "read_timeout": 30,
            "connection_timeout": 0.5,
            "timeout": 2,
        }

    async def test_omits_all_timeouts_when_unset(self):
        client = _AsyncRecordingQueryPlanClient()
        ctx = _make_async_ctx(client, {})
        with pytest.raises(_StopBeforePipeline):
            await ctx._create_execution_context_with_query_plan()
        assert client.captured_kwargs == {}


class TestDeadlineAnchorCarry(unittest.TestCase):
    """The carry must move OperationStartTime as well as the three timeouts, so the
    /pkranges and query-plan setup calls measure the deadline from the operation's
    start instead of their own."""

    def test_deadline_keys_are_the_three_timeouts_plus_anchor(self):
        assert _base._PER_CALL_DEADLINE_OPTION_KEYS == (
            Constants.Kwargs.READ_TIMEOUT,
            Constants.Kwargs.CONNECTION_TIMEOUT,
            Constants.Kwargs.TIMEOUT,
            Constants.OperationStartTime,
        )

    def test_helper_carries_operation_start_time(self):
        destination = {}
        _base._copy_per_call_timeouts_to_options(
            {Constants.OperationStartTime: 123.0, "read_timeout": 30}, destination
        )
        assert destination[Constants.OperationStartTime] == 123.0
        assert destination["read_timeout"] == 30

    def test_helper_omits_operation_start_time_when_absent(self):
        destination = {}
        _base._copy_per_call_timeouts_to_options({"timeout": 2}, destination)
        assert Constants.OperationStartTime not in destination

    def test_format_pk_range_options_carries_anchor_and_timers(self):
        options = {
            Constants.ContainerRID: "rid",
            "read_timeout": 30,
            "connection_timeout": 0.5,
            "timeout": 2,
            Constants.OperationStartTime: 123.0,
        }
        pk = _base.format_pk_range_options(options)
        assert pk[Constants.ContainerRID] == "rid"
        assert pk["read_timeout"] == 30
        assert pk["connection_timeout"] == 0.5
        assert pk["timeout"] == 2
        assert pk[Constants.OperationStartTime] == 123.0

    def test_format_pk_range_options_omits_unset(self):
        pk = _base.format_pk_range_options({Constants.ContainerRID: "rid"})
        assert Constants.OperationStartTime not in pk
        assert "read_timeout" not in pk
        assert "timeout" not in pk


class TestQueryPlanDeadlineAnchorSync(unittest.TestCase):
    """The sync query-plan dispatcher forwards OperationStartTime when set (so the
    deadline is measured from the shared start) and omits it when unset (so the
    request layer default is not overwritten)."""

    def test_forwards_operation_start_time_when_set(self):
        client = _RecordingQueryPlanClient()
        ctx = _make_sync_ctx(client, {"timeout": 2, Constants.OperationStartTime: 123.0})
        with pytest.raises(_StopBeforePipeline):
            ctx._create_execution_context_with_query_plan()
        assert client.captured_kwargs["timeout"] == 2
        assert client.captured_kwargs[Constants.OperationStartTime] == 123.0

    def test_omits_operation_start_time_when_unset(self):
        client = _RecordingQueryPlanClient()
        ctx = _make_sync_ctx(client, {"timeout": 2})
        with pytest.raises(_StopBeforePipeline):
            ctx._create_execution_context_with_query_plan()
        assert Constants.OperationStartTime not in client.captured_kwargs


class TestQueryPlanDeadlineAnchorAsync(unittest.IsolatedAsyncioTestCase):
    """The async query-plan dispatcher has the same contract as the sync one."""

    async def test_forwards_operation_start_time_when_set(self):
        client = _AsyncRecordingQueryPlanClient()
        ctx = _make_async_ctx(client, {"timeout": 2, Constants.OperationStartTime: 123.0})
        with pytest.raises(_StopBeforePipeline):
            await ctx._create_execution_context_with_query_plan()
        assert client.captured_kwargs["timeout"] == 2
        assert client.captured_kwargs[Constants.OperationStartTime] == 123.0

    async def test_omits_operation_start_time_when_unset(self):
        client = _AsyncRecordingQueryPlanClient()
        ctx = _make_async_ctx(client, {"timeout": 2})
        with pytest.raises(_StopBeforePipeline):
            await ctx._create_execution_context_with_query_plan()
        assert Constants.OperationStartTime not in client.captured_kwargs


class TestContainerReadForwarding(unittest.TestCase):
    """``_get_properties_with_options`` copies ``connection_timeout`` and
    ``OperationStartTime`` (plus ``read_timeout`` / ``timeout`` /
    ``excludedLocations``) from the options dict into the kwargs it hands to the
    container read. Exercised without a live client by stubbing ``_get_properties``
    to capture the kwargs."""

    @staticmethod
    def _capture(options):
        proxy = ContainerProxy.__new__(ContainerProxy)
        captured = {}
        proxy._get_properties = lambda **kwargs: captured.update(kwargs) or {}
        proxy._get_properties_with_options(options)
        return captured

    def test_forwards_all_timers_and_anchor(self):
        captured = self._capture({
            Constants.Kwargs.CONNECTION_TIMEOUT: 0.5,
            Constants.Kwargs.READ_TIMEOUT: 30,
            Constants.Kwargs.TIMEOUT: 2,
            Constants.OperationStartTime: 123.0,
            "excludedLocations": ["West US"],
        })
        assert captured[Constants.Kwargs.CONNECTION_TIMEOUT] == 0.5
        assert captured[Constants.Kwargs.READ_TIMEOUT] == 30
        assert captured[Constants.Kwargs.TIMEOUT] == 2
        assert captured[Constants.OperationStartTime] == 123.0
        assert captured["excluded_locations"] == ["West US"]

    def test_omits_connection_timeout_when_unset(self):
        captured = self._capture({Constants.Kwargs.READ_TIMEOUT: 30})
        assert Constants.Kwargs.CONNECTION_TIMEOUT not in captured
        assert captured[Constants.Kwargs.READ_TIMEOUT] == 30


class _RecordingReadPKRangesClient:
    """Captures the ``feed_options`` the hybrid all-ranges path hands to
    ``_ReadPartitionKeyRanges``."""

    def __init__(self):
        self.captured_feed_options = None

    def _ReadPartitionKeyRanges(self, collection_link, feed_options=None, **kwargs):  # noqa: N802
        self.captured_feed_options = feed_options
        return []


class _AsyncRecordingReadPKRangesClient:
    """Async counterpart for hybrid all-ranges feed-options capture."""

    def __init__(self):
        self.captured_feed_options = None

    def _ReadPartitionKeyRanges(self, collection_link, feed_options=None, **kwargs):  # noqa: N802
        self.captured_feed_options = feed_options

        async def _empty_async_iter():
            if False:
                yield None

        return _empty_async_iter()


class TestHybridAllRangesCarry(unittest.TestCase):
    """The hybrid-search all-ranges ``/pkranges`` fetch builds ``feed_options`` by
    hand instead of using ``format_pk_range_options``, so it must still carry the
    timeouts and ``OperationStartTime`` through the shared helper."""

    def _capture_feed_options(self, options):
        agg = _HybridSearchContextAggregator.__new__(_HybridSearchContextAggregator)
        client = _RecordingReadPKRangesClient()
        agg._client = client
        agg._resource_link = "dbs/db/colls/coll"
        agg._options = options
        agg._get_target_partition_key_range(target_all_ranges=True)
        return client.captured_feed_options

    def test_all_ranges_feed_options_carries_timers_and_anchor(self):
        fo = self._capture_feed_options({
            Constants.ContainerRID: "rid",
            "read_timeout": 30,
            "connection_timeout": 0.5,
            "timeout": 2,
            Constants.OperationStartTime: 123.0,
        })
        assert fo[Constants.ContainerRID] == "rid"
        assert fo["read_timeout"] == 30
        assert fo["connection_timeout"] == 0.5
        assert fo["timeout"] == 2
        assert fo[Constants.OperationStartTime] == 123.0

    def test_all_ranges_feed_options_omits_unset_timers(self):
        fo = self._capture_feed_options({Constants.ContainerRID: "rid"})
        assert fo[Constants.ContainerRID] == "rid"
        assert "read_timeout" not in fo
        assert "connection_timeout" not in fo
        assert "timeout" not in fo
        assert Constants.OperationStartTime not in fo


class TestAsyncHybridAllRangesCarry(unittest.IsolatedAsyncioTestCase):
    """Async hybrid-search all-ranges `/pkranges` carry has the same contract as sync."""

    async def _capture_feed_options(self, options):
        agg = _AsyncHybridSearchContextAggregator.__new__(_AsyncHybridSearchContextAggregator)
        client = _AsyncRecordingReadPKRangesClient()
        agg._client = client
        agg._resource_link = "dbs/db/colls/coll"
        agg._options = options
        await agg._get_target_partition_key_range(target_all_ranges=True)
        return client.captured_feed_options

    async def test_all_ranges_feed_options_carries_timers_and_anchor(self):
        fo = await self._capture_feed_options({
            Constants.ContainerRID: "rid",
            "read_timeout": 30,
            "connection_timeout": 0.5,
            "timeout": 2,
            Constants.OperationStartTime: 123.0,
        })
        assert fo[Constants.ContainerRID] == "rid"
        assert fo["read_timeout"] == 30
        assert fo["connection_timeout"] == 0.5
        assert fo["timeout"] == 2
        assert fo[Constants.OperationStartTime] == 123.0

    async def test_all_ranges_feed_options_omits_unset_timers(self):
        fo = await self._capture_feed_options({Constants.ContainerRID: "rid"})
        assert fo[Constants.ContainerRID] == "rid"
        assert "read_timeout" not in fo
        assert "connection_timeout" not in fo
        assert "timeout" not in fo
        assert Constants.OperationStartTime not in fo


class TestCopyPerCallTimeoutsToKwargs(unittest.TestCase):
    """The shared helper that copies the per-call timeouts and the operation start time
    into kwargs, used by the container read, the page fetch, and the query-plan
    dispatcher."""

    def test_copies_present_values(self):
        kwargs = {}
        _base._copy_per_call_timeouts_to_kwargs(
            {"read_timeout": 30, "connection_timeout": 0.5, "timeout": 2,
             Constants.OperationStartTime: 123.0}, kwargs)
        assert kwargs == {
            "read_timeout": 30,
            "connection_timeout": 0.5,
            "timeout": 2,
            Constants.OperationStartTime: 123.0,
        }

    def test_does_not_copy_none_values(self):
        # A present-but-None timer must not be copied: forwarding None would make
        # _Request's kwargs.pop(name, default) return None and override the default.
        kwargs = {}
        _base._copy_per_call_timeouts_to_kwargs({"read_timeout": None, "timeout": 2}, kwargs)
        assert "read_timeout" not in kwargs
        assert kwargs["timeout"] == 2

    def test_setdefault_existing_kwarg_wins(self):
        kwargs = {"read_timeout": 99}
        _base._copy_per_call_timeouts_to_kwargs({"read_timeout": 30}, kwargs)
        assert kwargs["read_timeout"] == 99

    def test_none_or_empty_options_is_noop(self):
        kwargs = {}
        _base._copy_per_call_timeouts_to_kwargs(None, kwargs)
        _base._copy_per_call_timeouts_to_kwargs({}, kwargs)
        assert kwargs == {}


def _make_query_feed_conn(connection_cls, get_fn):
    """Build a connection stub so __QueryFeed can reach __Get without network or
    header setup. Returns the bound (name-mangled) __QueryFeed to call."""
    conn = connection_cls.__new__(connection_cls)
    conn.default_headers = {}
    conn.availability_strategy = None
    # Sync reads availability_strategy_executor; async reads
    # availability_strategy_max_concurrency. Set both so one helper serves both.
    conn.availability_strategy_executor = None
    conn.availability_strategy_max_concurrency = None
    # _UpdateSessionIfRequired runs after __Get on the async ReadFeed branch.
    conn._UpdateSessionIfRequired = lambda *_args, **_kwargs: None
    # The change-feed branch of __QueryFeed reads self._routing_map_provider; set
    # it so that branch can run. The non-change-feed ReadFeed path never reads it.
    conn._routing_map_provider = None
    # __Get is name-mangled; both sync and async classes are named
    # CosmosClientConnection, so the mangled attribute name is identical.
    setattr(conn, "_CosmosClientConnection__Get", get_fn)
    return getattr(conn, "_CosmosClientConnection__QueryFeed")


_QUERY_FEED_OPTIONS = {
    "read_timeout": 30,
    "connection_timeout": 0.5,
    "timeout": 2,
    Constants.OperationStartTime: 123.0,
}


def _assert_query_feed_timers_lifted(captured_kwargs):
    assert captured_kwargs["read_timeout"] == 30
    assert captured_kwargs["connection_timeout"] == 0.5
    assert captured_kwargs["timeout"] == 2
    assert captured_kwargs[Constants.OperationStartTime] == 123.0


class TestSyncQueryFeedLift(unittest.TestCase):
    """__QueryFeed is where both the /pkranges fetch and the query plan copy the
    per-call timeouts from options into the kwargs _Request reads. This drives
    that copy through the ReadFeed branch into __Get, which the helper tests
    above do not cover."""

    def test_queryfeed_lifts_timers_from_options_into_get_kwargs(self):
        captured_kwargs = {}

        def _fake_get(_path, _request_params, _headers, **kwargs):
            captured_kwargs.update(kwargs)
            return {}, {}

        query_feed = _make_query_feed_conn(_SyncCosmosClientConnection, _fake_get)
        with mock.patch.object(_base, "GetHeaders", return_value={}), \
                mock.patch.object(_base, "set_session_token_header", return_value=None):
            # query=None drives the ReadFeed branch, which ends in __Get.
            query_feed(
                "dbs/db/colls/coll/pkranges",
                http_constants.ResourceType.PartitionKeyRange,
                "rid",
                lambda _r: [],
                lambda _client, body: body,
                None,
                _QUERY_FEED_OPTIONS,
            )

        _assert_query_feed_timers_lifted(captured_kwargs)


class TestAsyncQueryFeedLift(unittest.IsolatedAsyncioTestCase):
    """Async __QueryFeed makes the same options-to-kwargs copy as the sync one."""

    async def test_queryfeed_lifts_timers_from_options_into_get_kwargs(self):

        captured_kwargs = {}

        async def _fake_get(_path, _request_params, _headers, **kwargs):
            captured_kwargs.update(kwargs)
            return {}, {}

        async def _noop_session_async(*_args, **_kwargs):
            return None

        query_feed = _make_query_feed_conn(_AsyncCosmosClientConnection, _fake_get)
        with mock.patch.object(_base, "GetHeaders", return_value={}), \
                mock.patch.object(_base, "set_session_token_header_async", new=_noop_session_async):
            await query_feed(
                "dbs/db/colls/coll/pkranges",
                http_constants.ResourceType.PartitionKeyRange,
                "rid",
                lambda _r: [],
                lambda _client, body: body,
                None,
                _QUERY_FEED_OPTIONS,
            )

        _assert_query_feed_timers_lifted(captured_kwargs)


def _assert_change_feed_carry(carried):
    assert carried["read_timeout"] == 30
    assert carried["connection_timeout"] == 0.5
    assert carried["timeout"] == 2
    assert carried[Constants.OperationStartTime] == 123.0


class _RecordingChangeFeedState:
    """Records the feed_options handed to populate_request_headers so the test can
    assert the change-feed branch carried the per-call timers into it."""

    def __init__(self, sink):
        self._sink = sink

    def populate_request_headers(self, _routing_provider, _request_headers, feed_options=None):
        self._sink.update(feed_options or {})

    async def populate_request_headers_async(self, _routing_provider, _request_headers, feed_options=None):
        self._sink.update(feed_options or {})


class TestSyncChangeFeedBranchCarry(unittest.TestCase):
    """The change-feed branch of __QueryFeed builds its own feed_options for the
    /pkranges resolution (it never reaches format_pk_range_options), so it must
    carry the per-call timeouts into that dict itself."""

    def test_change_feed_branch_carries_timers_into_feed_options(self):
        carried = {}

        def _fake_get(_path, _request_params, _headers, **_kwargs):
            return {}, {}

        query_feed = _make_query_feed_conn(_SyncCosmosClientConnection, _fake_get)
        options = dict(_QUERY_FEED_OPTIONS)
        options["changeFeedState"] = _RecordingChangeFeedState(carried)
        with mock.patch.object(_base, "GetHeaders", return_value={}), \
                mock.patch.object(_base, "set_session_token_header", return_value=None):
            query_feed(
                "dbs/db/colls/coll/docs",
                http_constants.ResourceType.PartitionKeyRange,
                "rid",
                lambda _r: [],
                lambda _client, body: body,
                None,
                options,
            )

        _assert_change_feed_carry(carried)


class TestAsyncChangeFeedBranchCarry(unittest.IsolatedAsyncioTestCase):
    """Async change-feed branch carries the timers the same way the sync one does."""

    async def test_change_feed_branch_carries_timers_into_feed_options(self):
        carried = {}

        async def _fake_get(_path, _request_params, _headers, **_kwargs):
            return {}, {}

        async def _noop_session_async(*_args, **_kwargs):
            return None

        query_feed = _make_query_feed_conn(_AsyncCosmosClientConnection, _fake_get)
        options = dict(_QUERY_FEED_OPTIONS)
        options["changeFeedState"] = _RecordingChangeFeedState(carried)
        with mock.patch.object(_base, "GetHeaders", return_value={}), \
                mock.patch.object(_base, "set_session_token_header_async", new=_noop_session_async):
            await query_feed(
                "dbs/db/colls/coll/docs",
                http_constants.ResourceType.PartitionKeyRange,
                "rid",
                lambda _r: [],
                lambda _client, body: body,
                None,
                options,
            )

        _assert_change_feed_carry(carried)


def _gone_feed_options():

    class _FakeState:
        version = ChangeFeedStateVersion.V2

    return {
        "changeFeedState": _FakeState(),
        Constants.ContainerRID: "rid",
        "read_timeout": 30,
        "connection_timeout": 0.5,
        "timeout": 2,
        Constants.OperationStartTime: 123.0,
    }


def _assert_gone_carry(opts):
    assert opts is not None
    assert opts["read_timeout"] == 30
    assert opts["connection_timeout"] == 0.5
    assert opts["timeout"] == 2
    assert opts[Constants.OperationStartTime] == 123.0
    assert opts[Constants.ContainerRID] == "rid"


class TestSyncChangeFeedFetcherGonePathCarry(unittest.TestCase):
    """The change-feed fetcher's feed-range-gone (post-split) refresh rebuilds its
    own options dict for the /pkranges resolution; it must carry the per-call
    timeouts into that dict the same way the cold-start branch does. This is a
    separate drop site from the __QueryFeed branch above."""

    def test_gone_path_carries_timers_and_anchor(self):

        recorded = {}

        class _FakeClient:
            _global_endpoint_manager = object()
            _routing_map_provider = object()

        feed_options = _gone_feed_options()
        feed_options["changeFeedState"].handle_feed_range_gone = (
            lambda _rp, _link, feed_options=None: recorded.update(options=feed_options)
        )
        fetcher = cff.ChangeFeedFetcherV2(_FakeClient(), "dbs/db/colls/c", feed_options, lambda _o: ([], {}))

        calls = {"n": 0}

        def _fake_execute(_client, _gem, _callback):
            calls["n"] += 1
            if calls["n"] == 1:
                raise exceptions.CosmosHttpResponseError(status_code=410, message="gone")
            return []

        with mock.patch.object(cff._retry_utility, "Execute", side_effect=_fake_execute), \
                mock.patch.object(cff.exceptions, "_partition_range_is_gone", return_value=True):
            fetcher.fetch_next_block()

        _assert_gone_carry(recorded["options"])


class TestAsyncChangeFeedFetcherGonePathCarry(unittest.IsolatedAsyncioTestCase):
    """Async change-feed fetcher gone-path carries the timers the same way the sync
    one does."""

    async def test_gone_path_carries_timers_and_anchor(self):

        recorded = {}

        async def _record_gone(_rp, _link, feed_options=None):
            recorded["options"] = feed_options

        class _FakeClient:
            _global_endpoint_manager = object()
            _routing_map_provider = object()

        feed_options = _gone_feed_options()
        feed_options["changeFeedState"].handle_feed_range_gone_async = _record_gone
        fetcher = cff_async.ChangeFeedFetcherV2(_FakeClient(), "dbs/db/colls/c", feed_options, lambda _o: ([], {}))

        calls = {"n": 0}

        async def _fake_execute_async(_client, _gem, _callback):
            calls["n"] += 1
            if calls["n"] == 1:
                raise exceptions.CosmosHttpResponseError(status_code=410, message="gone")
            return []

        with mock.patch.object(cff_async._retry_utility_async, "ExecuteAsync", new=_fake_execute_async), \
                mock.patch.object(cff_async.exceptions, "_partition_range_is_gone", return_value=True):
            await fetcher.fetch_next_block()

        _assert_gone_carry(recorded["options"])


if __name__ == "__main__":
    unittest.main()
