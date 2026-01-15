# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""
Async unit tests for partition split (410) retry logic.
"""

import gc
import time
import tracemalloc
import unittest
from unittest.mock import patch

import pytest

from azure.cosmos import exceptions
from azure.cosmos.http_constants import StatusCodes, SubStatusCodes
from azure.cosmos.aio import CosmosClient  # noqa: F401 - needed to resolve circular imports
from azure.cosmos._execution_context.aio.base_execution_context import _DefaultQueryExecutionContext


# ====================================
# Shared Test Helpers
# ====================================

class MockGlobalEndpointManager:
    """Mock global endpoint manager for testing."""
    def is_circuit_breaker_applicable(self, request):
        return False


class MockClient:
    """Mock Cosmos client for testing partition split retry logic."""
    def __init__(self):
        self._global_endpoint_manager = MockGlobalEndpointManager()
        self.refresh_routing_map_provider_call_count = 0

    def refresh_routing_map_provider(self):
        self.refresh_routing_map_provider_call_count += 1

    def reset_counts(self):
        """Reset call counts for reuse in tests."""
        self.refresh_routing_map_provider_call_count = 0


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


if __name__ == "__main__":
    unittest.main()

