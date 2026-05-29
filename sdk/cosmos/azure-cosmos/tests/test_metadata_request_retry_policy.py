# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""
Unit tests for the MetadataRequestRetryPolicy and metadata throttle retry behavior.
"""

import unittest
from unittest.mock import MagicMock, patch

import pytest

from azure.cosmos._metadata_request_retry_policy import MetadataRequestRetryPolicy, _RANDOM_SALT_IN_MS
from azure.cosmos._resource_throttle_retry_policy import ResourceThrottleRetryPolicy
from azure.cosmos.http_constants import HttpHeaders


class _MockException:
    """Minimal exception-like object with headers for testing retry policies."""
    def __init__(self, retry_after_ms=None):
        self.headers = {}
        if retry_after_ms is not None:
            self.headers[HttpHeaders.RetryAfterInMilliseconds] = str(retry_after_ms)


class TestMetadataRequestRetryPolicy(unittest.TestCase):
    """Tests for MetadataRequestRetryPolicy."""

    def test_should_retry_always_returns_true(self):
        """MetadataRequestRetryPolicy should always return True (unlimited retries)."""
        policy = MetadataRequestRetryPolicy()
        exception = _MockException(retry_after_ms=100)

        # Retry many more times than the default document throttle policy limit (9)
        for i in range(50):
            result = policy.ShouldRetry(exception)
            self.assertTrue(result, f"ShouldRetry should return True on attempt {i + 1}")

        self.assertEqual(policy.current_retry_attempt_count, 50)

    def test_retry_after_from_exception_headers(self):
        """MetadataRequestRetryPolicy should honor the server Retry-After header."""
        policy = MetadataRequestRetryPolicy()
        exception = _MockException(retry_after_ms=500)

        policy.ShouldRetry(exception)

        # The retry_after should be the server value + some random jitter (0 to 100ms)
        self.assertGreaterEqual(policy.retry_after_in_milliseconds, 500)
        self.assertLessEqual(policy.retry_after_in_milliseconds, 500 + _RANDOM_SALT_IN_MS)

    def test_retry_after_without_header(self):
        """When no Retry-After header is present, retry delay is just jitter."""
        policy = MetadataRequestRetryPolicy()
        exception = _MockException(retry_after_ms=None)

        policy.ShouldRetry(exception)

        # Should only have jitter (0 to 100ms)
        self.assertGreaterEqual(policy.retry_after_in_milliseconds, 0)
        self.assertLessEqual(policy.retry_after_in_milliseconds, _RANDOM_SALT_IN_MS)

    def test_cumulative_wait_time_tracks_total(self):
        """Cumulative wait time should accumulate across retries."""
        policy = MetadataRequestRetryPolicy()
        exception = _MockException(retry_after_ms=100)

        for _ in range(5):
            policy.ShouldRetry(exception)

        # Each retry adds at least 100ms, so cumulative should be at least 500ms
        self.assertGreaterEqual(policy.cumulative_wait_time_in_milliseconds, 500)
        # And at most 500 + 5 * 100ms jitter = 1000ms
        self.assertLessEqual(policy.cumulative_wait_time_in_milliseconds, 500 + 5 * _RANDOM_SALT_IN_MS)

    def test_retry_count_increments(self):
        """Retry attempt count should increment on each call."""
        policy = MetadataRequestRetryPolicy()
        exception = _MockException(retry_after_ms=0)

        for expected in range(1, 11):
            policy.ShouldRetry(exception)
            self.assertEqual(policy.current_retry_attempt_count, expected)


class TestDocumentThrottleRetryPolicy(unittest.TestCase):
    """Comparison tests to verify document policy still has max retries."""

    def test_document_policy_stops_after_max_retries(self):
        """Document throttle retry policy should stop after max retry attempts."""
        max_retries = 3
        policy = ResourceThrottleRetryPolicy(
            max_retry_attempt_count=max_retries,
            fixed_retry_interval_in_milliseconds=None,
            max_wait_time_in_seconds=30,
        )
        exception = _MockException(retry_after_ms=100)

        for i in range(max_retries):
            result = policy.ShouldRetry(exception)
            self.assertTrue(result, f"Should retry on attempt {i + 1}")

        # Should NOT retry after max retries exhausted
        result = policy.ShouldRetry(exception)
        self.assertFalse(result, "Should NOT retry after exhausting max retries")


class TestMetadataThrottleRetryPolicySelection(unittest.TestCase):
    """Tests to verify the correct throttle retry policy is selected based on request type."""

    def _make_mock_client(self, max_retry_count=9, max_wait_time=30):
        """Create a mock client with connection policy for testing Execute()."""
        client = MagicMock()
        client.connection_policy.RetryOptions.MaxRetryAttemptCount = max_retry_count
        client.connection_policy.RetryOptions.FixedRetryIntervalInMilliseconds = None
        client.connection_policy.RetryOptions.MaxWaitTimeInSeconds = max_wait_time
        client.connection_policy.EnableEndpointDiscovery = False
        client.connection_policy.RetryNonIdempotentWrites = 0
        client.last_response_headers = {}
        client._container_properties_cache = {}
        client._enable_diagnostics_logging = False
        client.session = None
        return client

    def _make_mock_gem(self):
        """Create a mock GlobalEndpointManager."""
        gem = MagicMock()
        gem.is_per_partition_automatic_failover_applicable.return_value = False
        gem.is_circuit_breaker_applicable.return_value = False
        return gem

    @patch('azure.cosmos._retry_utility.ExecuteFunction')
    def test_document_request_uses_document_throttle_policy(self, mock_execute_fn):
        """Non-PK-range requests should use ResourceThrottleRetryPolicy with max retries."""
        from azure.cosmos import _retry_utility
        from azure.cosmos.exceptions import CosmosHttpResponseError

        mock_client = self._make_mock_client(max_retry_count=1)
        mock_gem = self._make_mock_gem()

        # Simulate 429 errors on every call
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.sub_status = None
        mock_response.headers = {HttpHeaders.RetryAfterInMilliseconds: "1"}

        error = CosmosHttpResponseError(
            status_code=429,
            message="Too many requests",
            response=mock_response,
        )
        error.headers = {HttpHeaders.RetryAfterInMilliseconds: "1"}
        error.sub_status = None
        mock_execute_fn.side_effect = error

        # Execute with NO _internal_pk_range_fetch — should use document policy
        with self.assertRaises(CosmosHttpResponseError):
            _retry_utility.Execute(
                mock_client,
                mock_gem,
                lambda **kw: None,
            )

        # With max_retry_count=1, should have retried once then raised
        # 1 original call + 1 retry = 2 total calls
        self.assertEqual(mock_execute_fn.call_count, 2)

    @patch('azure.cosmos._retry_utility.ExecuteFunction')
    def test_pk_range_request_uses_metadata_throttle_policy(self, mock_execute_fn):
        """PK range requests should use MetadataRequestRetryPolicy with unlimited retries."""
        from azure.cosmos import _retry_utility
        from azure.cosmos.exceptions import CosmosHttpResponseError

        mock_client = self._make_mock_client(max_retry_count=1)
        mock_gem = self._make_mock_gem()

        call_count = 0
        max_calls = 15  # Well beyond the document policy limit

        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.sub_status = None
        mock_response.headers = {HttpHeaders.RetryAfterInMilliseconds: "1"}

        def side_effect_fn(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count >= max_calls:
                return ({"result": "success"}, {})
            error = CosmosHttpResponseError(
                status_code=429,
                message="Too many requests",
                response=mock_response,
            )
            error.headers = {HttpHeaders.RetryAfterInMilliseconds: "1"}
            error.sub_status = None
            raise error

        mock_execute_fn.side_effect = side_effect_fn

        # Execute WITH _internal_pk_range_fetch=True — should use metadata policy
        result = _retry_utility.Execute(
            mock_client,
            mock_gem,
            lambda **kw: None,
            _internal_pk_range_fetch=True,
        )

        # Should have retried well beyond the document policy limit (1)
        self.assertEqual(call_count, max_calls)
        self.assertEqual(result[0]["result"], "success")


if __name__ == "__main__":
    unittest.main()
