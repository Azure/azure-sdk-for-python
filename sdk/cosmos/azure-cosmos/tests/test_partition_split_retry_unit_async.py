# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""
Async unit tests for partition split (410) retry logic.
"""

import gc
import time
import unittest
from unittest.mock import patch, MagicMock, AsyncMock

import pytest
from azure.core.exceptions import ServiceRequestError

from azure.cosmos import exceptions
from azure.cosmos.aio import _retry_utility_async
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos.http_constants import HttpHeaders, StatusCodes, SubStatusCodes
from azure.cosmos.aio import CosmosClient  # noqa: F401 - needed to resolve circular imports
from azure.cosmos.aio._cosmos_client_connection_async import CosmosClientConnection
from azure.cosmos._execution_context.aio.base_execution_context import _DefaultQueryExecutionContext

# tracemalloc is not available in PyPy, so we import conditionally
try:
    import tracemalloc
    HAS_TRACEMALLOC = True
except ImportError:
    HAS_TRACEMALLOC = False


# ====================================
# Shared Test Helpers
# ====================================

class MockGlobalEndpointManager:
    """Mock global endpoint manager for testing."""
    def is_per_partition_automatic_failover_applicable(self, request):
        return False

    def is_circuit_breaker_applicable(self, request):
        return False


class _NoRetryPolicy:
    """Simple retry policy stub used to isolate ExecuteAsync() 410 behavior in tests."""

    def __init__(self, *args, **kwargs):
        self.retry_after_in_milliseconds = 0

    def ShouldRetry(self, exception):
        return False


class _NoRetryResourceThrottlePolicy(_NoRetryPolicy):
    def __init__(self, *args, **kwargs):
        super(_NoRetryResourceThrottlePolicy, self).__init__(*args, **kwargs)
        self.current_retry_attempt_count = 0
        self.cumulative_wait_time_in_milliseconds = 0


class MockRoutingMapProvider:
    """Mock routing map provider with a collection routing map cache."""
    def __init__(self):
        self._collection_routing_map_by_item = {}


class MockClient:
    """Mock Cosmos client for testing partition split retry logic."""
    def __init__(self):
        self._global_endpoint_manager = MockGlobalEndpointManager()
        self._routing_map_provider = MockRoutingMapProvider()
        self.last_response_headers = {}
        self.refresh_routing_map_provider_call_count = 0
        self.last_refresh_collection_link = None
        self.last_refresh_previous_map = None
        self.last_refresh_feed_options = None

    async def refresh_routing_map_provider(self, collection_link=None, previous_routing_map=None, feed_options=None):
        self.refresh_routing_map_provider_call_count += 1
        self.last_refresh_collection_link = collection_link
        self.last_refresh_previous_map = previous_routing_map
        self.last_refresh_feed_options = feed_options

    def reset_counts(self):
        """Reset call counts for reuse in tests."""
        self.refresh_routing_map_provider_call_count = 0
        self.last_refresh_collection_link = None
        self.last_refresh_previous_map = None
        self.last_refresh_feed_options = None


def create_410_partition_split_error():
    """Create a 410 partition split error for testing."""
    error = exceptions.CosmosHttpResponseError(
        status_code=StatusCodes.GONE,
        message="Partition key range is gone"
    )
    error.sub_status = SubStatusCodes.PARTITION_KEY_RANGE_GONE
    return error


def raise_410_partition_split_error(*args, **kwargs):
    """Raise a 410 partition split error - for use as mock side_effect."""
    raise create_410_partition_split_error()


# ===============================
# Test Class
# ===============================



@pytest.mark.cosmosEmulator
class TestPartitionSplitRetryUnitAsync(unittest.IsolatedAsyncioTestCase):
    """
    Async unit tests for 410 partition split retry logic.
    """

    async def test_execution_context_state_reset_on_partition_split_async(self):
        """
        Test that execution context state is properly reset on 410 partition split retry (async).
        Verifies the fix for a bug where the while loop in _fetch_items_helper_no_retries
        would not execute after a retry because _has_started was still True.

        """
        mock_client = MockClient()

        async def mock_fetch_function(options):
            return ([{"id": "1"}], {})

        context = _DefaultQueryExecutionContext(mock_client, {}, mock_fetch_function)

        # Simulate state AFTER first successful fetch but BEFORE 410 error
        context._has_started = True
        context._continuation = None

        # Verify the loop condition WITHOUT state reset - this is FALSE
        loop_condition_without_reset = context._continuation or not context._has_started
        assert not loop_condition_without_reset, \
            "Without state reset, loop condition should be False"

        # Verify _fetch_items_helper_no_retries returns empty when state is not reset
        fetch_was_called = [False]

        async def tracking_fetch(options):
            fetch_was_called[0] = True
            return ([{"id": "1"}], {})

        result = await context._fetch_items_helper_no_retries(tracking_fetch)
        assert not fetch_was_called[0], \
            "Fetch should NOT be called when _has_started=True and _continuation=None"
        assert result == [], \
            "Should return empty list when while loop doesn't execute"

        # reset state
        context._has_started = False
        context._continuation = None

        # Verify _fetch_items_helper_no_retries works after state reset
        result = await context._fetch_items_helper_no_retries(tracking_fetch)
        assert fetch_was_called[0], \
            "Fetch SHOULD be called after state reset"
        assert result == [{"id": "1"}], \
            "Should return documents after state reset"

    @patch('azure.cosmos.aio._retry_utility_async.ExecuteAsync')
    async def test_retry_with_410_resets_state_and_succeeds_async(self, mock_execute):
        """
        Test the full retry flow: 410 partition split error triggers state reset and retry succeeds (async).
        """
        mock_client = MockClient()
        expected_docs = [{"id": "success"}]
        call_count = [0]

        async def execute_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise create_410_partition_split_error()
            return expected_docs

        mock_execute.side_effect = execute_side_effect

        async def mock_fetch_function(options):
            return (expected_docs, {})

        context = _DefaultQueryExecutionContext(mock_client, {}, mock_fetch_function)
        result = await context._fetch_items_helper_with_retries(mock_fetch_function)

        assert call_count[0] == 2, "Should have retried once after 410"
        assert mock_client.refresh_routing_map_provider_call_count == 1, \
            "refresh_routing_map_provider should be called once on 410"
        assert result == expected_docs, "Should return expected documents after retry"

    @patch('azure.cosmos.aio._retry_utility_async.ExecuteAsync')
    async def test_retry_with_410_uses_checkpoint_continuation_from_internal_capture_async(self, mock_execute):
        """410 retry should resume from checkpoint continuation stamped by __QueryFeed (async)."""
        mock_client = MockClient()
        expected_docs = [{"id": "success"}]
        seen_continuations = []
        call_count = [0]
        context = _DefaultQueryExecutionContext(mock_client, {}, lambda _options: (expected_docs, {}))

        async def execute_side_effect(client, _global_endpoint_manager, callback, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                context._internal_response_headers_capture[HttpHeaders.Continuation] = "checkpoint-token"
                raise create_410_partition_split_error()
            return await callback()

        mock_execute.side_effect = execute_side_effect

        async def mock_fetch_function(options):
            seen_continuations.append(options.get("continuation"))
            return (expected_docs, {})

        context._fetch_function = mock_fetch_function
        result = await context._fetch_items_helper_with_retries(mock_fetch_function)

        assert call_count[0] == 2
        assert seen_continuations == ["checkpoint-token"]
        assert result == expected_docs

    @patch('azure.cosmos.aio._retry_utility_async.ExecuteAsync')
    async def test_retry_with_410_ignores_stale_shared_client_headers_async(self, mock_execute):
        """Retry resumes from request-local captured headers, not shared client headers."""
        mock_client = MockClient()
        mock_client.last_response_headers = {HttpHeaders.Continuation: "stale-global-token"}
        expected_docs = [{"id": "success"}]
        seen_continuations = []
        call_count = [0]
        context = _DefaultQueryExecutionContext(mock_client, {}, lambda _options: (expected_docs, {}))

        async def execute_side_effect(_client, _global_endpoint_manager, callback, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                context._internal_response_headers_capture[HttpHeaders.Continuation] = "fresh-checkpoint"
                raise create_410_partition_split_error()
            return await callback()

        mock_execute.side_effect = execute_side_effect

        async def mock_fetch_function(options):
            seen_continuations.append(options.get("continuation"))
            return (expected_docs, {})

        context._fetch_function = mock_fetch_function
        result = await context._fetch_items_helper_with_retries(mock_fetch_function)

        assert call_count[0] == 2
        assert seen_continuations == ["fresh-checkpoint"]
        assert result == expected_docs

    @patch('azure.cosmos.aio._retry_utility_async.ExecuteAsync')
    async def test_retry_with_410_without_checkpoint_continuation_retries_from_none_async(self, mock_execute):
        """If no checkpoint header is stamped, continuation should remain None on retry (async)."""
        mock_client = MockClient()
        expected_docs = [{"id": "success"}]
        seen_continuations = []
        call_count = [0]

        async def execute_side_effect(client, _global_endpoint_manager, callback, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                context._internal_response_headers_capture.clear()
                raise create_410_partition_split_error()
            return await callback()

        mock_execute.side_effect = execute_side_effect

        async def mock_fetch_function(options):
            seen_continuations.append(options.get("continuation"))
            return (expected_docs, {})

        context = _DefaultQueryExecutionContext(mock_client, {}, mock_fetch_function)
        result = await context._fetch_items_helper_with_retries(mock_fetch_function)

        assert call_count[0] == 2
        assert seen_continuations == [None]
        assert result == expected_docs

    @patch('azure.cosmos.aio._retry_utility_async.ExecuteAsync')
    async def test_retry_with_multiple_410_uses_latest_checkpoint_continuation_async(self, mock_execute):
        """Across repeated 410 retries, execution should resume using the latest checkpoint token (async)."""
        mock_client = MockClient()
        expected_docs = [{"id": "success"}]
        seen_continuations = []
        call_count = [0]

        async def execute_side_effect(client, _global_endpoint_manager, callback, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                context._internal_response_headers_capture[HttpHeaders.Continuation] = "checkpoint-token-1"
                raise create_410_partition_split_error()
            if call_count[0] == 2:
                context._internal_response_headers_capture[HttpHeaders.Continuation] = "checkpoint-token-2"
                raise create_410_partition_split_error()
            return await callback()

        mock_execute.side_effect = execute_side_effect

        async def mock_fetch_function(options):
            seen_continuations.append(options.get("continuation"))
            return (expected_docs, {})

        context = _DefaultQueryExecutionContext(mock_client, {}, mock_fetch_function)
        result = await context._fetch_items_helper_with_retries(mock_fetch_function)

        assert call_count[0] == 3
        assert seen_continuations == ["checkpoint-token-2"]
        assert result == expected_docs

    @patch('azure.cosmos.aio._retry_utility_async.ExecuteAsync')
    async def test_mid_pagination_split_retries_from_checkpoint_without_duplicates_async(self, mock_execute):
        """Simulate page2 split and verify async retry resumes from checkpoint token, not from page1."""
        mock_client = MockClient()

        docs_page_1 = [{"id": "1"}, {"id": "2"}, {"id": "3"}, {"id": "4"}, {"id": "5"}]
        docs_page_2 = [{"id": "6"}, {"id": "7"}, {"id": "8"}, {"id": "9"}, {"id": "10"}]

        async def execute_side_effect(client, _global_endpoint_manager, callback, **kwargs):
            return await callback()

        mock_execute.side_effect = execute_side_effect

        fetch_calls = []

        async def mock_fetch_function(options):
            continuation = options.get("continuation")
            fetch_calls.append(continuation)

            if continuation is None:
                return (docs_page_1, {HttpHeaders.Continuation: "token-after-page-1"})

            if continuation == "token-after-page-1":
                # Simulate __QueryFeed writing a checkpoint before re-raising split error.
                context._internal_response_headers_capture[HttpHeaders.Continuation] = "checkpoint-after-split"
                raise create_410_partition_split_error()

            if continuation == "checkpoint-after-split":
                return (docs_page_2, {})

            self.fail(f"Unexpected continuation seen by fetch: {continuation}")

        context = _DefaultQueryExecutionContext(mock_client, {}, mock_fetch_function)

        first_result = await context._fetch_items_helper_with_retries(mock_fetch_function)
        self.assertListEqual(first_result, docs_page_1)

        second_result = await context._fetch_items_helper_with_retries(mock_fetch_function)
        self.assertListEqual(second_result, docs_page_2)

        # Validate the second page did not replay page-1 items and resumed from checkpoint.
        self.assertEqual(fetch_calls, [None, "token-after-page-1", "checkpoint-after-split"])

    @patch('azure.cosmos.aio._retry_utility_async.ExecuteAsync')
    async def test_pk_range_query_skips_410_retry_to_prevent_recursion_async(self, mock_execute):
        """
        Test that partition key range queries skip 410 retry to prevent recursion (async).
        """
        mock_client = MockClient()
        options = {"_internal_pk_range_fetch": True}

        mock_execute.side_effect = raise_410_partition_split_error

        async def mock_fetch_function(options):
            return ([{"id": "1"}], {})

        context = _DefaultQueryExecutionContext(mock_client, options, mock_fetch_function)

        with pytest.raises(exceptions.CosmosHttpResponseError) as exc_info:
            await context._fetch_items_helper_with_retries(mock_fetch_function)

        assert exc_info.value.status_code == StatusCodes.GONE
        assert mock_client.refresh_routing_map_provider_call_count == 0, \
            "refresh_routing_map_provider should NOT be called for PK range queries"
        assert mock_execute.call_count == 1, \
            "ExecuteAsync should only be called once - no retry for PK range queries"

    @patch('azure.cosmos.aio._retry_utility_async.ExecuteAsync')
    async def test_410_retry_behavior_with_and_without_pk_range_flag_async(self, mock_execute):
        """
        Test that verifies the fix for the partition split recursion problem (async).

        The fix ensures:
        - Regular queries retry up to 3 times on 410, calling refresh each time
        - PK range queries (with _internal_pk_range_fetch flag) skip retry entirely,
          preventing infinite recursion when refresh_routing_map_provider triggers
          another PK range query that also gets a 410
        """
        mock_client = MockClient()

        mock_execute.side_effect = raise_410_partition_split_error

        async def mock_fetch_function(options):
            return ([{"id": "1"}], {})

        # Test 1: Regular query (no flag) - should retry 3 times
        context = _DefaultQueryExecutionContext(mock_client, {}, mock_fetch_function)

        with pytest.raises(exceptions.CosmosHttpResponseError):
            await context._fetch_items_helper_with_retries(mock_fetch_function)

        assert mock_client.refresh_routing_map_provider_call_count == 3, \
            f"Expected 3 refresh calls, got {mock_client.refresh_routing_map_provider_call_count}"
        assert mock_execute.call_count == 4, \
            f"Expected 4 ExecuteAsync calls, got {mock_execute.call_count}"

        # Test 2: PK range query (with flag) - should NOT retry
        mock_client.reset_counts()
        mock_execute.reset_mock()
        mock_execute.side_effect = raise_410_partition_split_error

        options_with_flag = {"_internal_pk_range_fetch": True}
        context_pk_range = _DefaultQueryExecutionContext(mock_client, options_with_flag, mock_fetch_function)

        with pytest.raises(exceptions.CosmosHttpResponseError):
            await context_pk_range._fetch_items_helper_with_retries(mock_fetch_function)

        assert mock_client.refresh_routing_map_provider_call_count == 0, \
            f"With flag, expected 0 refresh calls, got {mock_client.refresh_routing_map_provider_call_count}"
        assert mock_execute.call_count == 1, \
            f"With flag, expected 1 ExecuteAsync call, got {mock_execute.call_count}"

    @pytest.mark.skipif(not HAS_TRACEMALLOC, reason="tracemalloc not available in PyPy")
    @patch('azure.cosmos.aio._retry_utility_async.ExecuteAsync')
    async def test_memory_bounded_no_leak_on_410_retries_async(self, mock_execute):
        """
        Test that memory usage is bounded during 410 partition split retries.
        - Execute calls are bounded (max 4: 1 initial + 3 retries)
        - Refresh calls are bounded (max 3)
        - Memory growth is minimal (no recursive accumulation)
        - No infinite recursion (max depth = 0 for PK range queries)
        """
        # tracemalloc.start() begins tracing memory allocations to detect leaks
        tracemalloc.start()
        # gc.collect() forces garbage collection to get accurate baseline memory measurement
        gc.collect()
        # take_snapshot() captures current memory state for comparison after test
        snapshot_before = tracemalloc.take_snapshot()
        start_time = time.time()

        mock_client = MockClient()

        mock_execute.side_effect = raise_410_partition_split_error

        async def mock_fetch_function(options):
            return ([{"id": "1"}], {})

        # Test regular query - should have bounded retries
        context = _DefaultQueryExecutionContext(mock_client, {}, mock_fetch_function)

        with pytest.raises(exceptions.CosmosHttpResponseError):
            await context._fetch_items_helper_with_retries(mock_fetch_function)

        elapsed_time = time.time() - start_time
        # gc.collect() before snapshot ensures we measure actual leaks, not pending garbage
        gc.collect()
        snapshot_after = tracemalloc.take_snapshot()
        # compare_to() shows memory difference between snapshots to identify growth
        top_stats = snapshot_after.compare_to(snapshot_before, 'lineno')
        memory_growth = sum(stat.size_diff for stat in top_stats if stat.size_diff > 0)
        peak_memory = tracemalloc.get_traced_memory()[1]
        # tracemalloc.stop() ends memory tracing and frees tracing overhead
        tracemalloc.stop()

        # Collect metrics
        execute_calls = mock_execute.call_count
        refresh_calls = mock_client.refresh_routing_map_provider_call_count

        # Print metrics
        print(f"\n{'=' * 60}")
        print("MEMORY METRICS (Async) - Partition Split Memory Verification")
        print(f"{'=' * 60}")
        print(f"Metrics:")
        print(f"  - Execute calls:   {execute_calls} (bounded)")
        print(f"  - Refresh calls:   {refresh_calls}")
        print(f"  - Elapsed time:    {elapsed_time:.2f}s")
        print(f"  - Memory growth:   {memory_growth / 1024:.2f} KB")
        print(f"  - Peak memory:     {peak_memory / 1024:.2f} KB")
        print(f"{'=' * 60}")

        assert execute_calls == 4, \
            f"Execute calls should be bounded to 4, got {execute_calls}"
        assert refresh_calls == 3, \
            f"Refresh calls should be bounded to 3, got {refresh_calls}"
        assert elapsed_time < 1.0, \
            f"Should complete quickly (< 1s), took {elapsed_time:.2f}s - indicates no infinite loop"
        assert memory_growth < 500 * 1024, \
            f"Memory growth should be < 500KB, got {memory_growth / 1024:.2f} KB - indicates no memory leak"

        # Test PK range query - should have NO retries (prevents recursion)
        mock_client.reset_counts()
        mock_execute.reset_mock()
        mock_execute.side_effect = raise_410_partition_split_error

        options_with_flag = {"_internal_pk_range_fetch": True}
        context_pk = _DefaultQueryExecutionContext(mock_client, options_with_flag, mock_fetch_function)

        with pytest.raises(exceptions.CosmosHttpResponseError):
            await context_pk._fetch_items_helper_with_retries(mock_fetch_function)

        pk_execute_calls = mock_execute.call_count
        pk_refresh_calls = mock_client.refresh_routing_map_provider_call_count

        print(f"\nPK Range Query:")
        print(f"  - Execute calls:   {pk_execute_calls} (no retry)")
        print(f"  - Refresh calls:   {pk_refresh_calls} (no recursion)")
        print(f"{'=' * 60}\n")

        assert pk_execute_calls == 1, \
            f"PK range query should have 1 execute call, got {pk_execute_calls}"
        assert pk_refresh_calls == 0, \
            f"PK range query should have 0 refresh calls, got {pk_refresh_calls}"

    @patch('azure.cosmos.aio._retry_utility_async.ExecuteAsync')
    async def test_targeted_refresh_with_resource_link_async(self, mock_execute):
        """
        Test that when resource_link is provided and a cached routing map exists,
        the 410 retry uses targeted refresh (passing collection_link and previous_map)
        instead of the global refresh.
        """
        mock_client = MockClient()
        # Simulate a cached routing map for this collection
        fake_routing_map = {"etag": "fake-etag", "ranges": ["range1"]}
        mock_client._routing_map_provider._collection_routing_map_by_item[
            "dbs/testdb/colls/testcoll"
        ] = fake_routing_map

        expected_docs = [{"id": "success"}]
        call_count = [0]

        async def execute_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise create_410_partition_split_error()
            return expected_docs

        mock_execute.side_effect = execute_side_effect

        async def mock_fetch_function(options):
            return (expected_docs, {})

        resource_link = "dbs/testdb/colls/testcoll"
        options = {
            Constants.ContainerRID: "rid123",
            "excludedLocations": ["West US", "North Europe"],
        }
        context = _DefaultQueryExecutionContext(
            mock_client, options, mock_fetch_function, resource_link=resource_link
        )
        result = await context._fetch_items_helper_with_retries(mock_fetch_function)

        assert call_count[0] == 2, "Should have retried once after 410"
        assert mock_client.refresh_routing_map_provider_call_count == 1
        # Verify targeted refresh was used (collection_link and previous_map passed)
        assert mock_client.last_refresh_collection_link == resource_link, \
            "Should pass collection_link for targeted refresh"
        assert mock_client.last_refresh_previous_map == fake_routing_map, \
            "Should pass previous routing map for targeted refresh"
        assert mock_client.last_refresh_feed_options == options
        assert result == expected_docs

    @patch('azure.cosmos.aio._retry_utility_async.ExecuteAsync')
    async def test_global_refresh_fallback_without_resource_link_async(self, mock_execute):
        """
        Test that when no resource_link is provided, the 410 retry falls back
        to the global refresh (no arguments to refresh_routing_map_provider).
        """
        mock_client = MockClient()
        expected_docs = [{"id": "success"}]
        call_count = [0]

        async def execute_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise create_410_partition_split_error()
            return expected_docs

        mock_execute.side_effect = execute_side_effect

        async def mock_fetch_function(options):
            return (expected_docs, {})

        # No resource_link — should use global refresh
        context = _DefaultQueryExecutionContext(mock_client, {}, mock_fetch_function)
        result = await context._fetch_items_helper_with_retries(mock_fetch_function)

        assert mock_client.refresh_routing_map_provider_call_count == 1
        assert mock_client.last_refresh_collection_link is None, \
            "Should NOT pass collection_link when resource_link is not set"
        assert mock_client.last_refresh_previous_map is None, \
            "Should NOT pass previous_map when resource_link is not set"
        assert result == expected_docs

    @patch('azure.cosmos.aio._retry_utility_async.ExecuteAsync')
    async def test_targeted_repopulation_when_no_cached_map_async(self, mock_execute):
        """
        Test that when resource_link is provided but there's no cached routing map
        for that collection, the 410 retry still refreshes only that collection.
        """
        mock_client = MockClient()
        expected_docs = [{"id": "success"}]
        call_count = [0]

        async def execute_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise create_410_partition_split_error()
            return expected_docs

        mock_execute.side_effect = execute_side_effect

        async def mock_fetch_function(options):
            return (expected_docs, {})

        # resource_link provided but no cached map for it
        resource_link = "dbs/testdb/colls/testcoll"
        context = _DefaultQueryExecutionContext(
            mock_client, {}, mock_fetch_function, resource_link=resource_link
        )
        result = await context._fetch_items_helper_with_retries(mock_fetch_function)

        assert mock_client.refresh_routing_map_provider_call_count == 1
        assert mock_client.last_refresh_collection_link == resource_link, \
            "Should target collection repopulation when no cached map exists"
        assert mock_client.last_refresh_previous_map is None, \
            "No cached map should pass previous_map=None"
        assert result == expected_docs

    @patch('azure.cosmos.aio._retry_utility_async.ContainerRecreateRetryPolicy', _NoRetryPolicy)
    @patch('azure.cosmos.aio._retry_utility_async._service_unavailable_retry_policy._ServiceUnavailableRetryPolicy', _NoRetryPolicy)
    @patch('azure.cosmos.aio._retry_utility_async._service_request_retry_policy.ServiceRequestRetryPolicy', _NoRetryPolicy)
    @patch('azure.cosmos.aio._retry_utility_async._service_response_retry_policy.ServiceResponseRetryPolicy', _NoRetryPolicy)
    @patch('azure.cosmos.aio._retry_utility_async._timeout_failover_retry_policy._TimeoutFailoverRetryPolicy', _NoRetryPolicy)
    @patch('azure.cosmos.aio._retry_utility_async._session_retry_policy._SessionRetryPolicy', _NoRetryPolicy)
    @patch('azure.cosmos.aio._retry_utility_async._default_retry_policy.DefaultRetryPolicy', _NoRetryPolicy)
    @patch('azure.cosmos.aio._retry_utility_async._resource_throttle_retry_policy.ResourceThrottleRetryPolicy', _NoRetryResourceThrottlePolicy)
    @patch('azure.cosmos.aio._retry_utility_async._health_check_retry_policy.HealthCheckRetryPolicy', _NoRetryPolicy)
    @patch('azure.cosmos.aio._retry_utility_async._endpoint_discovery_retry_policy.EndpointDiscoveryRetryPolicy', _NoRetryPolicy)
    @patch('azure.cosmos.aio._retry_utility_async.PartitionKeyRangeGoneRetryPolicyAsync')
    async def test_execute_async_410_path_skips_refresh_when_context_missing_and_no_request_args(self, mock_gone_policy):
        """ExecuteAsync() should skip refresh when 410 context is missing in callback/no-request path."""
        mock_client = MagicMock()
        mock_client.connection_policy = MagicMock()
        mock_client.connection_policy.RetryOptions = MagicMock(
            MaxRetryAttemptCount=0,
            FixedRetryIntervalInMilliseconds=0,
            MaxWaitTimeInSeconds=0,
        )
        mock_client.connection_policy.EnableEndpointDiscovery = False
        mock_client.last_response_headers = {}
        mock_client._container_properties_cache = {}
        mock_client._enable_diagnostics_logging = False
        mock_client.session = None
        mock_client._UpdateSessionIfRequired = MagicMock()
        mock_client.refresh_routing_map_provider = MagicMock()

        gone_policy = mock_gone_policy.return_value
        gone_policy.pop_refresh_context.return_value = (None, None, None)
        gone_policy.ShouldRetry.return_value = False
        gone_policy.retry_after_in_milliseconds = 0

        async def always_410(*args, **kwargs):
            raise create_410_partition_split_error()

        with pytest.raises(exceptions.CosmosHttpResponseError) as exc_info:
            await _retry_utility_async.ExecuteAsync(
                mock_client,
                MockGlobalEndpointManager(),
                always_410,
            )

        assert exc_info.value.status_code == StatusCodes.GONE
        mock_client.refresh_routing_map_provider.assert_not_called()
        gone_policy.pop_refresh_context.assert_called_once()

    @patch('azure.cosmos.aio._cosmos_client_connection_async.SmartRoutingMapProvider')
    async def test_refresh_routing_map_provider_collection_scoped_repopulation_without_previous_map_async(self, mock_provider_ctor):
        """Collection link without previous map should still trigger targeted repopulation."""
        conn = object.__new__(CosmosClientConnection)
        conn._routing_map_provider = MagicMock()
        conn._routing_map_provider.get_routing_map = AsyncMock(return_value=None)

        await conn.refresh_routing_map_provider(
            collection_link="dbs/db/colls/c1",
            previous_routing_map=None,
            feed_options={}
        )

        conn._routing_map_provider.get_routing_map.assert_awaited_once_with(
            "dbs/db/colls/c1",
            feed_options={},
            force_refresh=True,
            previous_routing_map=None,
        )
        mock_provider_ctor.assert_not_called()

    @patch('azure.cosmos.aio._cosmos_client_connection_async.SmartRoutingMapProvider')
    async def test_refresh_routing_map_provider_transient_targeted_error_falls_back_to_full_async(self, mock_provider_ctor):
        """Async targeted refresh should degrade to full refresh on transient transport errors."""
        conn = object.__new__(CosmosClientConnection)
        conn._routing_map_provider = MagicMock()

        async def _raise_transport(*args, **kwargs):
            raise ServiceRequestError("network down")

        conn._routing_map_provider.get_routing_map = _raise_transport
        replacement_provider = MagicMock()
        mock_provider_ctor.return_value = replacement_provider

        await conn.refresh_routing_map_provider(
            collection_link="dbs/db/colls/c1",
            previous_routing_map=object(),
            feed_options={}
        )

        self.assertIs(conn._routing_map_provider, replacement_provider)
        mock_provider_ctor.assert_called_once_with(conn)

    @patch('azure.cosmos.aio._cosmos_client_connection_async.SmartRoutingMapProvider')
    async def test_refresh_routing_map_provider_410_targeted_error_falls_back_to_full_async(self, mock_provider_ctor):
        """Async targeted refresh should treat 410 as transient and fall back to full refresh with warning."""
        conn = object.__new__(CosmosClientConnection)
        conn._routing_map_provider = MagicMock()

        async def _raise_410(*args, **kwargs):
            raise exceptions.CosmosHttpResponseError(
                status_code=StatusCodes.GONE,
                message="partition split while refreshing routing map"
            )

        conn._routing_map_provider.get_routing_map = _raise_410
        replacement_provider = MagicMock()
        mock_provider_ctor.return_value = replacement_provider

        with self.assertLogs("azure.cosmos.aio._cosmos_client_connection_async", level="WARNING") as logs:
            await conn.refresh_routing_map_provider(
                collection_link="dbs/db/colls/c1",
                previous_routing_map=object(),
                feed_options={}
            )

        self.assertIs(conn._routing_map_provider, replacement_provider)
        mock_provider_ctor.assert_called_once_with(conn)
        self.assertTrue(any("transient status code 410" in message for message in logs.output))

    @patch('azure.cosmos.aio._cosmos_client_connection_async.SmartRoutingMapProvider')
    async def test_refresh_routing_map_provider_non_transient_targeted_error_re_raises_async(self, mock_provider_ctor):
        """Async targeted refresh should surface non-transient errors instead of masking them."""
        conn = object.__new__(CosmosClientConnection)
        conn._routing_map_provider = MagicMock()

        async def _raise_non_transient(*args, **kwargs):
            raise exceptions.CosmosHttpResponseError(status_code=StatusCodes.BAD_REQUEST, message="bad request")

        conn._routing_map_provider.get_routing_map = _raise_non_transient

        with self.assertRaises(exceptions.CosmosHttpResponseError):
            await conn.refresh_routing_map_provider(
                collection_link="dbs/db/colls/c1",
                previous_routing_map=object(),
                feed_options={}
            )

        mock_provider_ctor.assert_not_called()

    @patch('azure.cosmos.aio._retry_utility_async.ContainerRecreateRetryPolicy', _NoRetryPolicy)
    @patch('azure.cosmos.aio._retry_utility_async._service_unavailable_retry_policy._ServiceUnavailableRetryPolicy', _NoRetryPolicy)
    @patch('azure.cosmos.aio._retry_utility_async._service_request_retry_policy.ServiceRequestRetryPolicy', _NoRetryPolicy)
    @patch('azure.cosmos.aio._retry_utility_async._service_response_retry_policy.ServiceResponseRetryPolicy', _NoRetryPolicy)
    @patch('azure.cosmos.aio._retry_utility_async._timeout_failover_retry_policy._TimeoutFailoverRetryPolicy', _NoRetryPolicy)
    @patch('azure.cosmos.aio._retry_utility_async._session_retry_policy._SessionRetryPolicy', _NoRetryPolicy)
    @patch('azure.cosmos.aio._retry_utility_async._default_retry_policy.DefaultRetryPolicy', _NoRetryPolicy)
    @patch('azure.cosmos.aio._retry_utility_async._resource_throttle_retry_policy.ResourceThrottleRetryPolicy', _NoRetryResourceThrottlePolicy)
    @patch('azure.cosmos.aio._retry_utility_async._health_check_retry_policy.HealthCheckRetryPolicy', _NoRetryPolicy)
    @patch('azure.cosmos.aio._retry_utility_async._endpoint_discovery_retry_policy.EndpointDiscoveryRetryPolicy', _NoRetryPolicy)
    @patch('azure.cosmos.aio._retry_utility_async.PartitionKeyRangeGoneRetryPolicyAsync')
    async def test_execute_async_410_path_uses_targeted_refresh_when_collection_link_exists_without_previous_map(self, mock_gone_policy):
        """ExecuteAsync() should still do targeted refresh when collection link exists and previous map is None."""
        mock_client = MagicMock()
        mock_client.connection_policy = MagicMock()
        mock_client.connection_policy.RetryOptions = MagicMock(
            MaxRetryAttemptCount=0,
            FixedRetryIntervalInMilliseconds=0,
            MaxWaitTimeInSeconds=0,
        )
        mock_client.connection_policy.EnableEndpointDiscovery = False
        mock_client.last_response_headers = {}
        mock_client._container_properties_cache = {}
        mock_client._enable_diagnostics_logging = False
        mock_client.session = None
        mock_client._UpdateSessionIfRequired = MagicMock()
        mock_client.refresh_routing_map_provider = AsyncMock()

        request_obj = MagicMock()
        request_obj.should_clear_session_token_on_session_read_failure = False
        request_obj.headers = {HttpHeaders.IntendedCollectionRID: "rid1"}

        request = MagicMock()
        request.headers = {HttpHeaders.IntendedCollectionRID: "rid1"}

        targeted_collection = "dbs/db1/colls/coll1"
        feed_options = {"x-ms-documentdb-collection-rid": "rid1"}

        gone_policy = mock_gone_policy.return_value
        gone_policy.pop_refresh_context.return_value = (targeted_collection, None, feed_options)
        gone_policy.ShouldRetry.return_value = False
        gone_policy.retry_after_in_milliseconds = 0

        async def always_410(*args, **kwargs):
            raise create_410_partition_split_error()

        with pytest.raises(exceptions.CosmosHttpResponseError) as exc_info:
            await _retry_utility_async.ExecuteAsync(
                mock_client,
                MockGlobalEndpointManager(),
                always_410,
                request_obj,
                None,
                None,
                request,
            )

        assert exc_info.value.status_code == StatusCodes.GONE
        mock_client.refresh_routing_map_provider.assert_awaited_once_with(
            targeted_collection,
            None,
            feed_options,
        )
        gone_policy.pop_refresh_context.assert_called_once()


    @pytest.mark.asyncio
    async def test_querfeed_populates_capture_dict_from_options_async(self):
        """Async `__QueryFeed` must read the capture dict from `options`
        and populate it from the underlying response headers, with no
        test-side injection. Catches the `options`-vs-`kwargs`
        extraction regression on the async path.
        """
        from unittest.mock import patch as _patch

        # Build a CosmosClientConnection without running __init__; we
        # only need the attributes that the no-query (read-feed) branch
        # of async __QueryFeed touches.
        conn = object.__new__(CosmosClientConnection)
        conn.default_headers = {}
        conn.last_response_headers = {}
        conn.availability_strategy = None
        conn.availability_strategy_max_concurrency = None
        conn._global_endpoint_manager = MockGlobalEndpointManager()
        conn._routing_map_provider = MagicMock(_collection_routing_map_by_item={})
        conn.session = None
        conn.connection_policy = MagicMock()
        conn._UpdateSessionIfRequired = MagicMock()

        capture_dict = {}
        options = {
            "_internal_response_headers_capture": capture_dict,
        }

        canned_headers = {HttpHeaders.Continuation: "checkpoint-from-real-querfeed-async"}

        request_obj_mock = MagicMock(
            set_excluded_location_from_options=MagicMock(),
            set_availability_strategy=MagicMock(),
            headers={},
            operation_type="ReadFeed",
        )

        # Patch the heavy collaborators inside async __QueryFeed's
        # no-query branch so we can drive it without a real pipeline.
        with _patch(
                 "azure.cosmos.aio._cosmos_client_connection_async.base.GetHeaders",
                 return_value={},
             ), \
             _patch(
                 "azure.cosmos.aio._cosmos_client_connection_async.base.set_session_token_header_async",
                 new=AsyncMock(),
             ), \
             _patch(
                 "azure.cosmos.aio._cosmos_client_connection_async._request_object.RequestObject",
                 return_value=request_obj_mock,
             ), \
             _patch.object(
                 CosmosClientConnection,
                 "_CosmosClientConnection__Get",
                 new=AsyncMock(return_value=(
                     {"Documents": [{"id": "1"}], "_count": 1},
                     canned_headers,
                 )),
             ) as mock_get:

            # Invoke the name-mangled private async method directly.
            result = await conn._CosmosClientConnection__QueryFeed(
                "/dbs/db/colls/c/docs",
                "docs",
                "rid1",
                lambda r: r["Documents"],
                lambda _c, b: b,
                None,                # query=None -> read-feed branch -> __Get
                options,
                None,                # partition_key_range_id
            )

            assert mock_get.await_count >= 1, "expected __Get to be awaited on the no-query path"


        assert capture_dict.get(HttpHeaders.Continuation) == "checkpoint-from-real-querfeed-async", (
            f"capture dict was not populated by async __QueryFeed; got {capture_dict!r}. "
            "This indicates async __QueryFeed is not reading "
            "'_internal_response_headers_capture' from options."
        )

        # the marker key must have been removed from options so it
        # never leaks downstream into header construction or RequestObject.
        assert "_internal_response_headers_capture" not in options, (
            "async __QueryFeed should pop the capture marker out of options"
        )

        # Sanity check: async no-query branch returns just the body list.
        assert result == [{"id": "1"}]
