# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""
Sync unit tests for partition split (410) retry logic.
"""

import gc
import time
import unittest
from unittest.mock import MagicMock, patch

import pytest

from azure.cosmos import exceptions
from azure.cosmos._cosmos_client_connection import CosmosClientConnection
from azure.cosmos._execution_context.base_execution_context import _DefaultQueryExecutionContext
from azure.cosmos._routing.feed_range_continuation import _FIELD_VERSION, _TOKEN_VERSION, _decode_token
from azure.cosmos.http_constants import StatusCodes, SubStatusCodes, HttpHeaders


# tracemalloc is not available in PyPy, so we import conditionally
try:
    import tracemalloc
    HAS_TRACEMALLOC = True
except ImportError:
    HAS_TRACEMALLOC = False


# =================================
# Shared Test Helpers
# =================================

class MockGlobalEndpointManager:
    """Mock global endpoint manager for testing."""
    def is_circuit_breaker_applicable(self, request):
        return False


class MockRoutingMapProvider:
    """Mock routing map provider with a collection routing map cache."""
    def __init__(self):
        self._collection_routing_map_by_item = {}


class MockClient:
    """Mock Cosmos client for testing partition split retry logic."""
    def __init__(self):
        self._global_endpoint_manager = MockGlobalEndpointManager()
        self.last_response_headers = {}
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

    @staticmethod
    def _create_minimal_connection() -> CosmosClientConnection:
        client = CosmosClientConnection.__new__(CosmosClientConnection)
        client.default_headers = {}
        client.last_response_headers = {}
        client._UpdateSessionIfRequired = lambda *args, **kwargs: None
        return client

    def test_queryfeed_internal_capture_uses_options_dict(self):
        """QueryFeed should honor _internal_response_headers_capture from options."""
        client = self._create_minimal_connection()
        captured_headers = {"stale": "value"}
        expected_headers = {HttpHeaders.Continuation: "checkpoint-token", "x-ms-request-charge": "1.0"}

        with patch('azure.cosmos._cosmos_client_connection.base.GetHeaders', return_value={}):
            with patch('azure.cosmos._cosmos_client_connection.base.set_session_token_header', return_value=None):
                with patch.object(
                    client,
                    '_CosmosClientConnection__Get',
                    return_value=({"Documents": [{"id": "doc1"}]}, expected_headers),
                ):
                    docs, response_headers = client.QueryFeed(
                        path="/dbs/db/colls/c1/docs",
                        collection_id="rid-c1",
                        query=None,
                        options={"_internal_response_headers_capture": captured_headers},
                    )

        self.assertEqual(docs, [{"id": "doc1"}])
        self.assertEqual(response_headers, expected_headers)
        self.assertEqual(captured_headers, expected_headers)

    def test_queryfeed_internal_capture_falls_back_to_kwargs(self):
        """QueryFeed should still support kwargs-based internal capture for compatibility."""
        client = self._create_minimal_connection()
        kwargs_capture = {"stale": "value"}
        expected_headers = {HttpHeaders.Continuation: "checkpoint-token-kwargs", "x-ms-request-charge": "1.0"}

        with patch('azure.cosmos._cosmos_client_connection.base.GetHeaders', return_value={}):
            with patch('azure.cosmos._cosmos_client_connection.base.set_session_token_header', return_value=None):
                with patch.object(
                    client,
                    '_CosmosClientConnection__Get',
                    return_value=({"Documents": [{"id": "doc2"}]}, expected_headers),
                ):
                    docs, response_headers = client.QueryFeed(
                        path="/dbs/db/colls/c1/docs",
                        collection_id="rid-c1",
                        query=None,
                        options={},
                        _internal_response_headers_capture=kwargs_capture,
                    )

        self.assertEqual(docs, [{"id": "doc2"}])
        self.assertEqual(response_headers, expected_headers)
        self.assertEqual(kwargs_capture, expected_headers)

    def test_queryfeed_internal_capture_both_present_populates_one(self):
        """When both options- and kwargs-based capture dicts are present
        (a configuration that does not occur in production — the two
        upstream paths are mutually exclusive by design), QueryFeed must
        populate exactly one of the two capture dicts with the response
        headers. Precedence is intentionally unspecified.
        """
        client = self._create_minimal_connection()
        options_capture: dict = {}
        kwargs_capture: dict = {}
        expected_headers = {HttpHeaders.Continuation: "checkpoint-token-both", "x-ms-request-charge": "1.0"}

        with patch('azure.cosmos._cosmos_client_connection.base.GetHeaders', return_value={}):
            with patch('azure.cosmos._cosmos_client_connection.base.set_session_token_header', return_value=None):
                with patch.object(
                    client,
                    '_CosmosClientConnection__Get',
                    return_value=({"Documents": [{"id": "doc3"}]}, expected_headers),
                ):
                    docs, response_headers = client.QueryFeed(
                        path="/dbs/db/colls/c1/docs",
                        collection_id="rid-c1",
                        query=None,
                        options={"_internal_response_headers_capture": options_capture},
                        _internal_response_headers_capture=kwargs_capture,
                    )

        self.assertEqual(docs, [{"id": "doc3"}])
        self.assertEqual(response_headers, expected_headers)
        populated = [d for d in (options_capture, kwargs_capture) if d == expected_headers]
        self.assertEqual(
            len(populated), 1,
            f"expected exactly one capture dict populated; got options={options_capture!r}, kwargs={kwargs_capture!r}",
        )

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
    def test_retry_with_410_uses_checkpoint_continuation_from_internal_capture(self, mock_execute):
        """410 retry should resume from checkpoint continuation stamped by __QueryFeed."""
        mock_client = MockClient()
        expected_docs = [{"id": "success"}]
        seen_continuations = []
        call_count = [0]
        context = _DefaultQueryExecutionContext(mock_client, {}, lambda _options: (expected_docs, {}))

        def execute_side_effect(client, _global_endpoint_manager, callback, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                context._internal_response_headers_capture[HttpHeaders.Continuation] = "checkpoint-token"
                raise create_410_partition_split_error()
            return callback()

        mock_execute.side_effect = execute_side_effect

        def mock_fetch_function(options):
            seen_continuations.append(options.get("continuation"))
            return (expected_docs, {})

        context._fetch_function = mock_fetch_function
        result = context._fetch_items_helper_with_retries(mock_fetch_function)

        assert call_count[0] == 2
        assert seen_continuations == ["checkpoint-token"]
        assert result == expected_docs

    @patch('azure.cosmos._retry_utility.Execute')
    def test_retry_with_410_uses_queryfeed_captured_checkpoint_end_to_end(self, mock_execute):
        """End-to-end: QueryFeed stamps capture dict, 410 occurs, retry resumes from checkpoint token."""
        mock_client = MockClient()
        query_client = self._create_minimal_connection()
        query_client._query_compatibility_mode = query_client._QueryCompatibilityMode.Default

        context = None
        seen_continuations = []
        execute_call_count = [0]

        def post_side_effect(_path, _request_params, _query, req_headers, **_kwargs):
            continuation = req_headers.get(HttpHeaders.Continuation)
            if continuation:
                return ({"Documents": [{"id": "resumed"}]}, {})
            return ({"Documents": [{"id": "checkpoint-page"}]}, {HttpHeaders.Continuation: "checkpoint-token"})

        def execute_side_effect(_client, _global_endpoint_manager, callback, **kwargs):
            execute_call_count[0] += 1
            if execute_call_count[0] == 1:
                callback()
                raise create_410_partition_split_error()
            return callback()

        mock_execute.side_effect = execute_side_effect

        def fetch_function(options):
            seen_continuations.append(options.get("continuation"))
            docs, headers = query_client.QueryFeed(
                path="/dbs/db/colls/c1/docs",
                collection_id="rid-c1",
                query="SELECT * FROM c",
                options=options,
            )
            return docs, headers

        def mock_get_headers(*args, **kwargs):
            options = args[7] if len(args) > 7 else kwargs.get("options", {})
            headers = {}
            if options and options.get("continuation") is not None:
                headers[HttpHeaders.Continuation] = options.get("continuation")
            return headers

        context = _DefaultQueryExecutionContext(mock_client, {}, fetch_function)

        with patch('azure.cosmos._cosmos_client_connection.base.GetHeaders', side_effect=mock_get_headers):
            with patch('azure.cosmos._cosmos_client_connection.base.set_session_token_header', return_value=None):
                with patch.object(query_client, '_CosmosClientConnection__Post', side_effect=post_side_effect):
                    result = context._fetch_items_helper_with_retries(fetch_function)

        assert execute_call_count[0] == 2
        assert seen_continuations == [None, "checkpoint-token"]
        assert result == [{"id": "resumed"}]

    @patch('azure.cosmos._retry_utility.Execute')
    def test_retry_with_410_ignores_stale_shared_client_headers(self, mock_execute):
        """Retry resumes from request-local captured headers, not shared client headers."""
        mock_client = MockClient()
        mock_client.last_response_headers = {HttpHeaders.Continuation: "stale-global-token"}
        expected_docs = [{"id": "success"}]
        seen_continuations = []
        call_count = [0]
        context = _DefaultQueryExecutionContext(mock_client, {}, lambda _options: (expected_docs, {}))

        def execute_side_effect(_client, _global_endpoint_manager, callback, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                context._internal_response_headers_capture[HttpHeaders.Continuation] = "fresh-checkpoint"
                raise create_410_partition_split_error()
            return callback()

        mock_execute.side_effect = execute_side_effect

        def mock_fetch_function(options):
            seen_continuations.append(options.get("continuation"))
            return (expected_docs, {})

        context._fetch_function = mock_fetch_function
        result = context._fetch_items_helper_with_retries(mock_fetch_function)

        assert call_count[0] == 2
        assert seen_continuations == ["fresh-checkpoint"]
        assert result == expected_docs

    @patch('azure.cosmos._retry_utility.Execute')
    def test_retry_with_410_without_checkpoint_continuation_retries_from_none(self, mock_execute):
        """If no checkpoint header is stamped, continuation should remain None on retry."""
        mock_client = MockClient()
        expected_docs = [{"id": "success"}]
        seen_continuations = []
        call_count = [0]

        def execute_side_effect(client, _global_endpoint_manager, callback, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                context._internal_response_headers_capture.clear()
                raise create_410_partition_split_error()
            return callback()

        mock_execute.side_effect = execute_side_effect

        def mock_fetch_function(options):
            seen_continuations.append(options.get("continuation"))
            return (expected_docs, {})

        context = _DefaultQueryExecutionContext(mock_client, {}, mock_fetch_function)
        result = context._fetch_items_helper_with_retries(mock_fetch_function)

        assert call_count[0] == 2
        assert seen_continuations == [None]
        assert result == expected_docs

    @patch('azure.cosmos._retry_utility.Execute')
    def test_retry_with_multiple_410_uses_latest_checkpoint_continuation(self, mock_execute):
        """Across repeated 410 retries, execution should resume using the latest checkpoint token."""
        mock_client = MockClient()
        expected_docs = [{"id": "success"}]
        seen_continuations = []
        call_count = [0]

        def execute_side_effect(client, _global_endpoint_manager, callback, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                context._internal_response_headers_capture[HttpHeaders.Continuation] = "checkpoint-token-1"
                raise create_410_partition_split_error()
            if call_count[0] == 2:
                context._internal_response_headers_capture[HttpHeaders.Continuation] = "checkpoint-token-2"
                raise create_410_partition_split_error()
            return callback()

        mock_execute.side_effect = execute_side_effect

        def mock_fetch_function(options):
            seen_continuations.append(options.get("continuation"))
            return (expected_docs, {})

        context = _DefaultQueryExecutionContext(mock_client, {}, mock_fetch_function)
        result = context._fetch_items_helper_with_retries(mock_fetch_function)

        assert call_count[0] == 3
        assert seen_continuations == ["checkpoint-token-2"]
        assert result == expected_docs

    @patch('azure.cosmos._retry_utility.Execute')
    def test_mid_pagination_split_retries_from_checkpoint_without_duplicates(self, mock_execute):
        """Simulate page2 split and verify retry resumes from checkpoint token, not from page1."""
        mock_client = MockClient()

        docs_page_1 = [{"id": "1"}, {"id": "2"}, {"id": "3"}, {"id": "4"}, {"id": "5"}]
        docs_page_2 = [{"id": "6"}, {"id": "7"}, {"id": "8"}, {"id": "9"}, {"id": "10"}]

        def execute_side_effect(client, _global_endpoint_manager, callback, **kwargs):
            return callback()

        mock_execute.side_effect = execute_side_effect

        fetch_calls = []

        def mock_fetch_function(options):
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

        first_result = context._fetch_items_helper_with_retries(mock_fetch_function)
        self.assertListEqual(first_result, docs_page_1)

        second_result = context._fetch_items_helper_with_retries(mock_fetch_function)
        self.assertListEqual(second_result, docs_page_2)

        # Validate the second page did not replay page-1 items and resumed from checkpoint.
        self.assertEqual(fetch_calls, [None, "token-after-page-1", "checkpoint-after-split"])

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

    @pytest.mark.skipif(not HAS_TRACEMALLOC, reason="tracemalloc not available in PyPy")
    @patch('azure.cosmos._retry_utility.Execute')
    def test_memory_bounded_no_leak_on_410_retries(self, mock_execute):
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

        def mock_fetch_function(options):
            return ([{"id": "1"}], {})

        # Test regular query - should have bounded retries
        context = _DefaultQueryExecutionContext(mock_client, {}, mock_fetch_function)

        with pytest.raises(exceptions.CosmosHttpResponseError):
            context._fetch_items_helper_with_retries(mock_fetch_function)

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
        print("MEMORY METRICS - Partition Split Memory Verification")
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
            context_pk._fetch_items_helper_with_retries(mock_fetch_function)

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

    def test_querfeed_populates_capture_dict_from_options(self):
        """`__QueryFeed` must read the capture dict from `options` and
        populate it from the underlying response headers.

        This is the producer-side counterpart to the checkpoint tests
        above: it does not inject into the capture dict, it asserts that
        `__QueryFeed` itself does the population. Catches the
        `options`-vs-`kwargs` extraction regression.
        """
        from unittest.mock import patch as _patch

        # Build a CosmosClientConnection without running __init__; we
        # only need the attributes that the no-query (read-feed) branch
        # of __QueryFeed touches.
        conn = object.__new__(CosmosClientConnection)
        conn.default_headers = {}
        conn.last_response_headers = {}
        conn.availability_strategy = None
        conn.availability_strategy_executor = None
        conn._global_endpoint_manager = MockGlobalEndpointManager()
        conn._routing_map_provider = MockRoutingMapProvider()
        conn.session = None
        conn.connection_policy = MagicMock()

        capture_dict = {}
        options = {
            "_internal_response_headers_capture": capture_dict,
        }

        canned_headers = {HttpHeaders.Continuation: "checkpoint-from-real-querfeed"}

        request_obj_mock = MagicMock(
            set_excluded_location_from_options=MagicMock(),
            set_availability_strategy=MagicMock(),
            headers={},
        )

        # Patch the heavy collaborators inside __QueryFeed's no-query
        # branch so we can drive it without a real pipeline.
        with _patch(
                 "azure.cosmos._cosmos_client_connection.base.GetHeaders",
                 return_value={},
             ), \
             _patch(
                 "azure.cosmos._cosmos_client_connection.base.set_session_token_header"
             ), \
             _patch(
                 "azure.cosmos._cosmos_client_connection.RequestObject",
                 return_value=request_obj_mock,
             ) as request_obj_ctor, \
             _patch.object(
                 CosmosClientConnection,
                 "_CosmosClientConnection__Get",
                 return_value=(
                     {"Documents": [{"id": "1"}], "_count": 1},
                     canned_headers,
                 ),
             ) as mock_get:

            _ = request_obj_ctor  # silence unused-warning

            # Invoke the name-mangled private method directly.
            result, headers = conn._CosmosClientConnection__QueryFeed(
                "/dbs/db/colls/c/docs",
                "docs",
                "rid1",
                lambda r: r["Documents"],
                lambda _c, b: b,
                None,                # query=None -> read-feed branch -> __Get
                options,
                None,                # partition_key_range_id
            )

            assert mock_get.called, "expected __Get to be invoked on the no-query path"

        assert capture_dict.get(HttpHeaders.Continuation) == "checkpoint-from-real-querfeed", (
            f"capture dict was not populated by __QueryFeed; got {capture_dict!r}. "
            "This indicates __QueryFeed is not reading "
            "'_internal_response_headers_capture' from options."
        )

        # the marker key must have been removed from options so it
        # never leaks downstream into header construction or RequestObject.
        assert "_internal_response_headers_capture" not in options, (
            "__QueryFeed should pop the capture marker out of options"
        )

        # Sanity check on the result tuple shape.
        assert result == [{"id": "1"}]
        assert headers is canned_headers

    def test_queryfeed_feed_range_legacy_inbound_single_partition_honors_and_emits_legacy(self):
        """Legacy inbound continuation is honored when feed_range currently maps to one partition."""
        client = self._create_minimal_connection()
        client._query_compatibility_mode = client._QueryCompatibilityMode.Default
        client._routing_map_provider = MagicMock()

        single_overlap = [{"id": "0", "minInclusive": "00", "maxExclusive": "FF"}]

        def overlap_side_effect(_rid, ranges, _opts):
            _ = ranges
            return single_overlap

        client._routing_map_provider.get_overlapping_ranges.side_effect = overlap_side_effect

        seen_request_continuations = []

        def post_side_effect(_path, _request_params, _query, req_headers, **_kwargs):
            seen_request_continuations.append(req_headers.get(HttpHeaders.Continuation))
            return {"Documents": [{"id": "doc-1"}]}, {HttpHeaders.Continuation: "legacy-next-token"}

        with patch("azure.cosmos._cosmos_client_connection.base.GetHeaders", return_value={}):
            with patch("azure.cosmos._cosmos_client_connection.base.set_session_token_header", return_value=None):
                with patch.object(client, "_CosmosClientConnection__Post", side_effect=post_side_effect):
                    docs, headers = client.QueryFeed(
                        path="/dbs/db/colls/c1/docs",
                        collection_id="rid-c1",
                        query="SELECT * FROM c",
                        options={"continuation": "legacy-inbound-token"},
                        feed_range={
                            "Range": {
                                "min": "00",
                                "max": "FF",
                                "isMinInclusive": True,
                                "isMaxInclusive": False,
                            }
                        },
                    )

        assert docs == [{"id": "doc-1"}]
        assert seen_request_continuations == ["legacy-inbound-token"]
        assert headers.get(HttpHeaders.Continuation) == "legacy-next-token"

    def test_queryfeed_feed_range_legacy_inbound_multi_partition_restarts_and_emits_v1(self):
        """Legacy inbound continuation is ignored when scope is multi-partition; outbound becomes v=1."""
        client = self._create_minimal_connection()
        client._query_compatibility_mode = client._QueryCompatibilityMode.Default
        client._routing_map_provider = MagicMock()

        child_left = {"id": "0", "minInclusive": "00", "maxExclusive": "7F"}
        child_right = {"id": "1", "minInclusive": "7F", "maxExclusive": "FF"}

        def overlap_side_effect(_rid, ranges, _opts):
            requested = ranges[0]
            if requested.min == "00" and requested.max == "FF":
                return [child_left, child_right]
            if requested.min == "00" and requested.max == "7F":
                return [child_left]
            if requested.min == "7F" and requested.max == "FF":
                return [child_right]
            return []

        client._routing_map_provider.get_overlapping_ranges.side_effect = overlap_side_effect

        seen_request_continuations = []

        def post_side_effect(_path, _request_params, _query, req_headers, **_kwargs):
            seen_request_continuations.append(req_headers.get(HttpHeaders.Continuation))
            return {"Documents": [{"id": "doc-1"}]}, {HttpHeaders.Continuation: "child-legacy-token"}

        with patch("azure.cosmos._cosmos_client_connection.base.GetHeaders", return_value={}):
            with patch("azure.cosmos._cosmos_client_connection.base.set_session_token_header", return_value=None):
                with patch.object(client, "_CosmosClientConnection__Post", side_effect=post_side_effect):
                    docs, headers = client.QueryFeed(
                        path="/dbs/db/colls/c1/docs",
                        collection_id="rid-c1",
                        query="SELECT * FROM c",
                        options={"continuation": "legacy-inbound-token"},
                        feed_range={
                            "Range": {
                                "min": "00",
                                "max": "FF",
                                "isMinInclusive": True,
                                "isMaxInclusive": False,
                            }
                        },
                    )

        assert docs == [{"id": "doc-1"}]
        assert seen_request_continuations == [None]
        outbound = headers.get(HttpHeaders.Continuation)
        decoded = _decode_token(outbound)
        assert decoded is not None
        assert decoded[_FIELD_VERSION] == _TOKEN_VERSION

    def test_queryfeed_feed_range_routing_lookup_failure_stamps_checkpoint(self):
        """A failure inside the mid-page routing-map lookup must stamp a resumable
        checkpoint into ``last_response_headers[Continuation]`` before re-raising,
        not just failures from the backend POST.
        """
        client = self._create_minimal_connection()
        client._query_compatibility_mode = client._QueryCompatibilityMode.Default
        client._routing_map_provider = MagicMock()

        single_overlap = [{"id": "0", "minInclusive": "00", "maxExclusive": "FF"}]
        routing_call_count = {"n": 0}

        def overlap_side_effect(_rid, _ranges, _opts):
            routing_call_count["n"] += 1
            # First call (legacy bridge classification) succeeds; the mid-page
            # iteration call fails so we exercise the widened try block.
            if routing_call_count["n"] >= 2:
                raise RuntimeError("routing-map-down")
            return single_overlap

        client._routing_map_provider.get_overlapping_ranges.side_effect = overlap_side_effect

        with patch("azure.cosmos._cosmos_client_connection.base.GetHeaders", return_value={}):
            with patch("azure.cosmos._cosmos_client_connection.base.set_session_token_header", return_value=None):
                with patch.object(client, "_CosmosClientConnection__Post") as post_mock:
                    with pytest.raises(RuntimeError, match="routing-map-down"):
                        client.QueryFeed(
                            path="/dbs/db/colls/c1/docs",
                            collection_id="rid-c1",
                            query="SELECT * FROM c",
                            options={"continuation": "legacy-inbound-token"},
                            feed_range={
                                "Range": {
                                    "min": "00",
                                    "max": "FF",
                                    "isMinInclusive": True,
                                    "isMaxInclusive": False,
                                }
                            },
                        )
                    post_mock.assert_not_called()

        # Checkpoint must be present so the caller can resume on retry.
        # Single-partition scope => legacy-format checkpoint (the original inbound token).
        continuation = client.last_response_headers.get(HttpHeaders.Continuation)
        assert continuation == "legacy-inbound-token"


if __name__ == "__main__":
    unittest.main()
