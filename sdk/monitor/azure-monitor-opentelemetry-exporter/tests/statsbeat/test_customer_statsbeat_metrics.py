import os
import unittest
import sys
import json
import time
import requests
from unittest import mock

from opentelemetry.metrics import Observation, CallbackOptions

# Import directly from module to avoid circular imports
from azure.monitor.opentelemetry.exporter.statsbeat._customer_statsbeat import CustomerStatsbeatMetrics
from azure.monitor.opentelemetry.exporter.statsbeat._customer_statsbeat_types import (
    TelemetryType,
    DropCode,
    RetryCode,
    CustomerStatsbeat,
    CustomStatsbeatCounter
)
from azure.monitor.opentelemetry.exporter.export._base import BaseExporter, ExportResult
from azure.monitor.opentelemetry.exporter._generated.models import TelemetryItem
class TestCustomerStatsbeatMetrics(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.env_patcher = mock.patch.dict(os.environ, {
            "APPLICATIONINSIGHTS_STATSBEAT_ENABLED_PREVIEW": "true"
        })
        self.env_patcher.start()
        self.mock_options = mock.Mock()
        self.mock_options.instrumentation_key = "test-key"
        self.mock_options.endpoint_url = "https://example.com"
        self.mock_options.network_collection_interval = 900000
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.env_patcher.stop()

    def _create_test_metrics(self):
        """Helper method to create test metrics with proper mocking."""
        patcher = mock.patch('azure.monitor.opentelemetry.exporter._connection_string_parser.ConnectionStringParser._validate_instrumentation_key')
        patcher.start()
        self.addCleanup(patcher.stop)
        return CustomerStatsbeatMetrics(self.mock_options)
        
    @mock.patch('azure.monitor.opentelemetry.exporter.statsbeat._customer_statsbeat.AzureMonitorStatsbeatExporter')
    @mock.patch('azure.monitor.opentelemetry.exporter.statsbeat._customer_statsbeat.PeriodicExportingMetricReader')
    @mock.patch('azure.monitor.opentelemetry.exporter.statsbeat._customer_statsbeat.MeterProvider')
    def test_initialization(self, mock_meter_provider, mock_metric_reader, mock_exporter):
        """Test CustomerStatsbeatMetrics initialization."""
        # Arrange
        mock_meter = mock.Mock()
        mock_meter_provider.return_value.get_meter.return_value = mock_meter
        
        # Act
        metrics = self._create_test_metrics()
        
        # Assert
        mock_exporter.assert_called_once()
        mock_metric_reader.assert_called_once()
        mock_meter_provider.assert_called_once()
        self.assertEqual(metrics._language, "python")
        self.assertIsNotNone(metrics._version)
        self.assertIsNotNone(metrics._attach)
        self.assertTrue(metrics._is_enabled)

    def test_count_successful_items(self):
        """Test counting successful items."""
        metrics = self._create_test_metrics()
        
        # Act
        metrics.count_successful_items(5, TelemetryType.REQUEST)
        metrics.count_successful_items(3, TelemetryType.REQUEST)
        metrics.count_successful_items(2, TelemetryType.DEPENDENCY)
        
        # Assert
        counter = metrics._customer_statsbeat_counter
        self.assertEqual(len(counter.total_item_success_count), 2)
        
        request_entry = next(e for e in counter.total_item_success_count if e["telemetry_type"] == TelemetryType.REQUEST)
        self.assertEqual(request_entry["count"], 8)
        
        dependency_entry = next(e for e in counter.total_item_success_count if e["telemetry_type"] == TelemetryType.DEPENDENCY)
        self.assertEqual(dependency_entry["count"], 2)

    def test_count_dropped_items(self):
        """Test counting dropped items."""
        metrics = self._create_test_metrics()
        
        # Act
        metrics.count_dropped_items(3, DropCode.CLIENT_PERSISTENCE_CAPACITY, TelemetryType.TRACE)
        metrics.count_dropped_items(2, DropCode.CLIENT_EXCEPTION, TelemetryType.TRACE, exception_message="Test error")
        metrics.count_dropped_items(4, "403", TelemetryType.REQUEST, drop_reason="Forbidden")
        
        # Assert
        counter = metrics._customer_statsbeat_counter
        self.assertEqual(len(counter.total_item_drop_count), 3)  # One for each unique drop code
        
        capacity_entry = next(e for e in counter.total_item_drop_count if e["drop_code"] == DropCode.CLIENT_PERSISTENCE_CAPACITY)
        self.assertEqual(capacity_entry["count"], 3)
        
        exception_entry = next(e for e in counter.total_item_drop_count if e["drop_code"] == DropCode.CLIENT_EXCEPTION)
        self.assertEqual(exception_entry["count"], 2)
        self.assertEqual(exception_entry.get("exception_message"), "Test error")
        
        # Verify the status code entry
        status_entry = next(e for e in counter.total_item_drop_count if e["drop_code"] == "403")
        self.assertEqual(status_entry["count"], 4)
        self.assertEqual(status_entry.get("drop_reason"), "Forbidden")

    def test_count_retry_items(self):
        """Test counting retry items."""
        metrics = self._create_test_metrics()
        
        # Act
        metrics.count_retry_items(4, RetryCode.RETRYABLE_STATUS_CODE, telemetry_type=TelemetryType.CUSTOM_METRIC)
        metrics.count_retry_items(2, RetryCode.CLIENT_TIMEOUT, telemetry_type=TelemetryType.CUSTOM_METRIC, exception_message="Timeout occurred")
        metrics.count_retry_items(3, "429", telemetry_type=TelemetryType.REQUEST, retry_reason="Too Many Requests")
        
        # Assert
        counter = metrics._customer_statsbeat_counter
        self.assertEqual(len(counter.total_item_retry_count), 3)  # One for each unique retry code
        
        status_entry = next(e for e in counter.total_item_retry_count if e["retry_code"] == RetryCode.RETRYABLE_STATUS_CODE)
        self.assertEqual(status_entry["count"], 4)
        
        timeout_entry = next(e for e in counter.total_item_retry_count if e["retry_code"] == RetryCode.CLIENT_TIMEOUT)
        self.assertEqual(timeout_entry["count"], 2)
        self.assertEqual(timeout_entry.get("exception_message"), "Timeout occurred")
        
        # Verify the status code entry
        too_many_requests_entry = next(e for e in counter.total_item_retry_count if e["retry_code"] == "429")
        self.assertEqual(too_many_requests_entry["count"], 3)
        self.assertEqual(too_many_requests_entry.get("retry_reason"), "Too Many Requests")

    def test_customer_statsbeat_not_initialized_when_disabled(self):
        """Test that customer statsbeat is not initialized when disabled by environment variable."""
        with mock.patch.dict(os.environ, {"APPLICATIONINSIGHTS_STATSBEAT_ENABLED_PREVIEW": "false"}):
            metrics = CustomerStatsbeatMetrics(self.mock_options)
            
            # Verify is_enabled flag is False
            self.assertFalse(metrics._is_enabled)
            
            # Verify the metrics methods don't do anything when disabled
            metrics.count_successful_items(5, TelemetryType.REQUEST)
            metrics.count_dropped_items(3, DropCode.CLIENT_EXCEPTION, TelemetryType.TRACE)
            metrics.count_retry_items(2, RetryCode.CLIENT_TIMEOUT)
            
            # Verify callbacks return empty lists when disabled
            self.assertEqual(metrics._item_success_callback(mock.Mock()), [])
            self.assertEqual(metrics._item_drop_callback(mock.Mock()), [])
            self.assertEqual(metrics._item_retry_callback(mock.Mock()), [])
