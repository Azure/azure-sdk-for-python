# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""
Sync unit tests for partition split (410) retry logic.
"""

import unittest
from unittest.mock import patch
import pytest

from azure.cosmos import exceptions
from azure.cosmos._execution_context.base_execution_context import _DefaultQueryExecutionContext
from azure.cosmos.http_constants import StatusCodes, SubStatusCodes


# =================================
# Shared Test Helpers
# =================================

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


# ==========================
# Test Class
# ==========================

@pytest.mark.cosmosEmulator
class TestPartitionSplitRetryUnit(unittest.TestCase):
    """
    Sync unit tests for 410 partition split retry logic.
    """

    def test_execution_context_state_reset_on_partition_split(self):
        """
        Test that execution context state is properly reset on 410 partition split retry.
        Verifies the fix where the while loop in _fetch_items_helper_no_retries
        would not execute after a retry because _has_started was still True.
        """
        mock_client = MockClient()

        def mock_fetch_function(options):
            return ([{"id": "1"}], {})

        context = _DefaultQueryExecutionContext(mock_client, {}, mock_fetch_function)

        # simulate state after first successful fetch but before 410 error
        context._has_started = True
        context._continuation = None

        # Verify the loop condition without state reset - this is false
        loop_condition_without_reset = context._continuation or not context._has_started
        assert not loop_condition_without_reset, \
            "Without state reset, loop condition should be False"

        # Verify _fetch_items_helper_no_retries returns empty when state is not reset
        fetch_was_called = [False]

        def tracking_fetch(options):
            fetch_was_called[0] = True
            return ([{"id": "1"}], {})

        result = context._fetch_items_helper_no_retries(tracking_fetch)
        assert not fetch_was_called[0], \
            "Fetch should NOT be called when _has_started=True and _continuation=None"
        assert result == [], \
            "Should return empty list when while loop doesn't execute"

        # Now reset state
        context._has_started = False
        context._continuation = None

        # verify the loop condition with state reset
        loop_condition_with_reset = context._continuation or not context._has_started
        assert loop_condition_with_reset, \
            "With state reset, loop condition should be True"

        # verify _fetch_items_helper_no_retries works after state reset
        result = context._fetch_items_helper_no_retries(tracking_fetch)
        assert fetch_was_called[0], \
            "Fetch SHOULD be called after state reset"
        assert result == [{"id": "1"}], \
            "Should return documents after state reset"

    @patch('azure.cosmos._retry_utility.Execute')
    def test_retry_with_410_resets_state_and_succeeds(self, mock_execute):
        """
        Test the full retry flow: 410 partition split error triggers state reset and retry succeeds.
        """
        mock_client = MockClient()
        expected_docs = [{"id": "success"}]
        call_count = [0]

        def execute_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise create_410_partition_split_error()
            return expected_docs

        mock_execute.side_effect = execute_side_effect

        def mock_fetch_function(options):
            return (expected_docs, {})

        context = _DefaultQueryExecutionContext(mock_client, {}, mock_fetch_function)
        result = context._fetch_items_helper_with_retries(mock_fetch_function)

        assert call_count[0] == 2, "Should have retried once after 410"
        assert mock_client.refresh_routing_map_provider_call_count == 1, \
            "refresh_routing_map_provider should be called once on 410"
        assert result == expected_docs, "Should return expected documents after retry"

    @patch('azure.cosmos._retry_utility.Execute')
    def test_pk_range_query_skips_410_retry_to_prevent_recursion(self, mock_execute):
        """
        Test that partition key range queries (marked with _internal_pk_range_fetch=True)
        skip the 410 partition split retry logic to prevent infinite recursion.

        When a 410 partition split error occurs:
        1. SDK calls refresh_routing_map_provider() which clears the routing map cache
        2. SDK retries the query
        3. Retry needs partition key ranges, which triggers _ReadPartitionKeyRanges
        4. If _ReadPartitionKeyRanges also uses 410 retry logic and gets a 410,
           it would call refresh_routing_map_provider() again, creating infinite recursion

        This test verifies that queries with _internal_pk_range_fetch=True do not
        trigger the 410 retry with refresh logic.
        """
        mock_client = MockClient()
        options = {"_internal_pk_range_fetch": True}

        mock_execute.side_effect = raise_410_partition_split_error

        def mock_fetch_function(options):
            return ([{"id": "1"}], {})

        context = _DefaultQueryExecutionContext(mock_client, options, mock_fetch_function)

        with pytest.raises(exceptions.CosmosHttpResponseError) as exc_info:
            context._fetch_items_helper_with_retries(mock_fetch_function)

        assert exc_info.value.status_code == StatusCodes.GONE
        assert mock_client.refresh_routing_map_provider_call_count == 0, \
            "refresh_routing_map_provider should NOT be called for PK range queries"
        assert mock_execute.call_count == 1, \
            "Execute should only be called once - no retry for PK range queries"

    @patch('azure.cosmos._retry_utility.Execute')
    def test_410_retry_behavior_with_and_without_pk_range_flag(self, mock_execute):
        """
        Test that verifies the fix for the partition split recursion problem.

        The fix ensures:
        - Regular queries retry up to 3 times on 410, calling refresh each time
        - PK range queries (with _internal_pk_range_fetch flag) skip retry entirely,
          preventing infinite recursion when refresh_routing_map_provider triggers
          another PK range query that also gets a 410
        """
        mock_client = MockClient()

        mock_execute.side_effect = raise_410_partition_split_error

        def mock_fetch_function(options):
            return ([{"id": "1"}], {})

        # Test 1: Regular query (no flag) - should retry 3 times
        context = _DefaultQueryExecutionContext(mock_client, {}, mock_fetch_function)

        with pytest.raises(exceptions.CosmosHttpResponseError):
            context._fetch_items_helper_with_retries(mock_fetch_function)

        assert mock_client.refresh_routing_map_provider_call_count == 3, \
            f"Expected 3 refresh calls, got {mock_client.refresh_routing_map_provider_call_count}"
        assert mock_execute.call_count == 4, \
            f"Expected 4 Execute calls, got {mock_execute.call_count}"

        # Test 2: PK range query (with flag) - should NOT retry
        mock_client.reset_counts()
        mock_execute.reset_mock()
        mock_execute.side_effect = raise_410_partition_split_error

        options_with_flag = {"_internal_pk_range_fetch": True}
        context_pk_range = _DefaultQueryExecutionContext(mock_client, options_with_flag, mock_fetch_function)

        with pytest.raises(exceptions.CosmosHttpResponseError):
            context_pk_range._fetch_items_helper_with_retries(mock_fetch_function)

        assert mock_client.refresh_routing_map_provider_call_count == 0, \
            f"With flag, expected 0 refresh calls, got {mock_client.refresh_routing_map_provider_call_count}"
        assert mock_execute.call_count == 1, \
            f"With flag, expected 1 Execute call, got {mock_execute.call_count}"


if __name__ == "__main__":
    unittest.main()
