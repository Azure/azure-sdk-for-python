# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import unittest
import json
import requests
from unittest import mock

from opentelemetry.metrics import CallbackOptions

from azure.monitor.opentelemetry.exporter.statsbeat._customer_statsbeat import CustomerStatsbeatMetrics
from azure.monitor.opentelemetry.exporter.statsbeat._customer_statsbeat_types import (
    TelemetryType,
    DropCode,
    RetryCode
)


class MockResponse:
    """Mock HTTP response compatible with Azure SDK pipeline."""
    
    def __init__(self, status_code=200, text="", raise_exception=None):
        self.status_code = status_code
        self.text = text
        self.raise_exception = raise_exception
        self.content_type = "application/json"
        self.headers = {"Content-Type": "application/json", "Retry-After": "30"}
        self.http_response = self  # Reference to self for compatibility with Azure SDK pipeline
        self.body = text  # Body attribute expected by some SDK components
        self.context = {}  # Context for tracking response state
        
    def raise_for_status(self):
        if self.raise_exception:
            raise self.raise_exception
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP error: {self.status_code}")
            
    def json(self):
        """Parse body text as JSON."""
        if not self.text:
            return {}
        try:
            return json.loads(self.text)
        except json.JSONDecodeError:
            return {}


class TestCustomerStatsbeatIntegration(unittest.TestCase):
    """Integration tests for CustomerStatsbeatMetrics."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock the environment variable to enable customer statsbeat
        self.env_patcher = mock.patch.dict(os.environ, {
            "APPLICATIONINSIGHTS_STATSBEAT_ENABLED_PREVIEW": "true"
        })
        self.env_patcher.start()
        
        # Create mock options with test instrumentation key
        self.mock_options = mock.Mock()
        self.mock_options.instrumentation_key = "test-key"
        self.mock_options.endpoint_url = "https://example.com"
        self.mock_options.network_collection_interval = 900000  # 15 minutes
        
        # Set up HTTP response mock
        self.http_patcher = mock.patch("azure.core.pipeline.transport._requests_basic.RequestsTransport.send")
        self.mock_http = self.http_patcher.start()
        self.mock_http.return_value = MockResponse(200, json.dumps({"itemsReceived": 1, "itemsAccepted": 1, "errors": []}))
        
        # Mock the instrumentation key validation
        self.key_patcher = mock.patch('azure.monitor.opentelemetry.exporter._connection_string_parser.ConnectionStringParser._validate_instrumentation_key')
        self.key_patcher.start()

    def tearDown(self):
        """Clean up test fixtures."""
        self.env_patcher.stop()
        self.http_patcher.stop()
        self.key_patcher.stop()

    def test_metrics_sent_to_backend(self):
        """Test that metrics are correctly sent to the backend."""
        # Arrange
        metrics = CustomerStatsbeatMetrics(self.mock_options)
        
        # Add data to the counters
        metrics.count_successful_items(10, TelemetryType.REQUEST)
        metrics.count_dropped_items(5, DropCode.CLIENT_EXCEPTION, TelemetryType.TRACE, exception_message="Error")
        metrics.count_retry_items(3, RetryCode.CLIENT_TIMEOUT, TelemetryType.DEPENDENCY)
        
        # Manually trigger callbacks to generate observations
        success_observations = metrics._item_success_callback(CallbackOptions())
        dropped_observations = metrics._item_drop_callback(CallbackOptions())
        retry_observations = metrics._item_retry_callback(CallbackOptions())
        
        # Act
        # Force metrics export by calling shutdown which flushes pending metrics
        with mock.patch('azure.monitor.opentelemetry.exporter.export._base.logger') as mock_logger:
            metrics.shutdown()
            
            # Assert
            # Verify metrics were exported
            self.mock_http.assert_called()
            
            # Verify the correct number of observations was generated
            self.assertEqual(len(success_observations), 1)  # One observation for REQUEST
            self.assertEqual(len(dropped_observations), 1)  # One observation for CLIENT_EXCEPTION
            self.assertEqual(len(retry_observations), 1)    # One observation for CLIENT_TIMEOUT
            
            # Verify observation values
            self.assertEqual(success_observations[0].value, 10)
            self.assertEqual(dropped_observations[0].value, 5)
            self.assertEqual(retry_observations[0].value, 3)
            
            # Verify telemetry types in attributes
            self.assertEqual(success_observations[0].attributes.get("telemetry_type"), TelemetryType.REQUEST)
            self.assertEqual(dropped_observations[0].attributes.get("telemetry_type"), TelemetryType.TRACE)
            self.assertEqual(retry_observations[0].attributes.get("telemetry_type"), TelemetryType.DEPENDENCY)
            
            # No errors should be logged
            mock_logger.error.assert_not_called()
            
    def test_network_failure_handling(self):
        """Test handling of network failures when sending metrics."""
        # Arrange - Setup HTTP to simulate network failure
        self.mock_http.return_value = MockResponse(0, "", raise_exception=requests.ConnectionError("Failed to connect"))
        
        # Need to patch at the exporter level where the error is actually handled
        with mock.patch('azure.monitor.opentelemetry.exporter.export._base.logger') as mock_logger:
            metrics = CustomerStatsbeatMetrics(self.mock_options)
            metrics.count_successful_items(10, TelemetryType.REQUEST)
            
            # Act - Force metrics export
            metrics.shutdown()
            
            # Assert - The error should be caught and logged
            self.assertTrue(mock_logger.warning.called or mock_logger.error.called)
            
            # Verify the network request was attempted
            self.mock_http.assert_called()

    def test_metrics_with_http_errors(self):
        """Test handling of HTTP error responses."""
        # Test HTTP 429 (Too Many Requests)
        self.mock_http.return_value = MockResponse(429, json.dumps({"error": "Too many requests"}))
        
        # Need to patch at the exporter level where the exception is actually handled
        with mock.patch('azure.monitor.opentelemetry.exporter.export._base.logger') as mock_logger:
            metrics = CustomerStatsbeatMetrics(self.mock_options)
            metrics.count_successful_items(10, TelemetryType.REQUEST)
            
            # Act
            metrics.shutdown()
            
            # Assert
            self.mock_http.assert_called()
            # Warning or error should be logged
            self.assertTrue(mock_logger.warning.called or mock_logger.error.called)
        
    def test_malformed_response_handling(self):
        """Test handling of malformed responses from the backend."""
        # Return malformed JSON
        self.mock_http.return_value = MockResponse(200, "Not valid JSON")
        
        # Need to patch at the exporter level where the exception is actually handled
        with mock.patch('azure.monitor.opentelemetry.exporter.export._base.logger') as mock_logger:
            metrics = CustomerStatsbeatMetrics(self.mock_options)
            metrics.count_successful_items(10, TelemetryType.REQUEST)
            
            # Act
            metrics.shutdown()
            
            # Assert
            self.mock_http.assert_called()
            self.assertTrue(mock_logger.warning.called or mock_logger.error.called)  # Warning should be logged
            
    def test_partial_success_response(self):
        """Test handling of partial success responses (some items accepted, some rejected)."""
        # Return a response with errors
        self.mock_http.return_value = MockResponse(
            206,  # Partial success
            json.dumps({
                "itemsReceived": 3,
                "itemsAccepted": 1,
                "errors": [
                    {
                        "index": 1,
                        "statusCode": 400,
                        "message": "Invalid format"
                    },
                    {
                        "index": 2,
                        "statusCode": 403,
                        "message": "Quota exceeded"
                    }
                ]
            })
        )
        
        # Need to patch at the exporter level where the exception is actually handled
        with mock.patch('azure.monitor.opentelemetry.exporter.export._base.logger') as mock_logger:
            metrics = CustomerStatsbeatMetrics(self.mock_options)
            metrics.count_successful_items(10, TelemetryType.REQUEST)
            metrics.count_dropped_items(5, DropCode.CLIENT_EXCEPTION, TelemetryType.TRACE)
            
            # Act
            metrics.shutdown()
            
            # Assert
            self.mock_http.assert_called()
            self.assertTrue(mock_logger.warning.called or mock_logger.error.called)
            
    def test_large_metric_count_handling(self):
        """Test handling of a large number of metrics."""
        metrics = CustomerStatsbeatMetrics(self.mock_options)
        
        # Add a large number of metrics with different telemetry types
        for telemetry_type in TelemetryType:
            metrics.count_successful_items(100, telemetry_type)
            metrics.count_dropped_items(50, DropCode.CLIENT_EXCEPTION, telemetry_type)
            metrics.count_retry_items(25, RetryCode.RETRYABLE_STATUS_CODE, telemetry_type)
        
        # Manually trigger callbacks
        success_observations = metrics._item_success_callback(CallbackOptions())
        dropped_observations = metrics._item_drop_callback(CallbackOptions())
        retry_observations = metrics._item_retry_callback(CallbackOptions())
        
        # Assert
        # Should have one observation per telemetry type
        self.assertEqual(len(success_observations), len(TelemetryType))
        self.assertEqual(len(dropped_observations), len(TelemetryType))
        self.assertEqual(len(retry_observations), len(TelemetryType))
        
        # Verify observation values
        for observation in success_observations:
            self.assertEqual(observation.value, 100)
        
        for observation in dropped_observations:
            self.assertEqual(observation.value, 50)
        
        for observation in retry_observations:
            self.assertEqual(observation.value, 25)
