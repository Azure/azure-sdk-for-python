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


class TestCustomerStatsbeat(unittest.TestCase):
    """Tests for CustomerStatsbeatMetrics."""
    
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
        patcher = mock.patch("azure.monitor.opentelemetry.exporter._connection_string_parser.ConnectionStringParser._validate_instrumentation_key")
        patcher.start()
        self.addCleanup(patcher.stop)
        return CustomerStatsbeatMetrics(self.mock_options)
    
    def test_initialization(self):
        """Test initialization of CustomerStatsbeatMetrics."""
        with mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._customer_statsbeat.AzureMonitorStatsbeatExporter"):
            with mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._customer_statsbeat.PeriodicExportingMetricReader"):
                with mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._customer_statsbeat.MeterProvider"):
                    metrics = self._create_test_metrics()
                    self.assertEqual(metrics._language, "python")
                    self.assertTrue(metrics._is_enabled)
    
    def test_customer_statsbeat_not_initialized_when_disabled(self):
        """Test that customer statsbeat is not initialized when disabled by environment variable."""
        with mock.patch.dict(os.environ, {"APPLICATIONINSIGHTS_STATSBEAT_ENABLED_PREVIEW": "false"}):
            metrics = CustomerStatsbeatMetrics(self.mock_options)
            
            # Verify is_enabled flag is False
            self.assertFalse(metrics._is_enabled)
            
            # Verify the metrics methods don"t do anything when disabled
            metrics.count_successful_items(5, TelemetryType.REQUEST)
            metrics.count_dropped_items(3, DropCode.CLIENT_EXCEPTION, TelemetryType.TRACE)
            metrics.count_retry_items(2, RetryCode.CLIENT_TIMEOUT)
            
            # Verify callbacks return empty lists when disabled
            self.assertEqual(metrics._item_success_callback(mock.Mock()), [])
            self.assertEqual(metrics._item_drop_callback(mock.Mock()), [])
            self.assertEqual(metrics._item_retry_callback(mock.Mock()), [])
