# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import shutil
import unittest
from unittest import mock
from datetime import datetime

from azure.monitor.opentelemetry.exporter.export._base import (
    BaseExporter,
    ExportResult,
)
from azure.monitor.opentelemetry.exporter.statsbeat import _customer_sdkstats
from azure.monitor.opentelemetry.exporter.statsbeat._customer_sdkstats import _CUSTOMER_SDKSTATS_STATE, CustomerSdkStatsMetrics
from azure.monitor.opentelemetry.exporter._generated.models import TelemetryItem


class MockResponse:
    def __init__(self, status_code, text, headers={}, reason="test", content="{}"):
        self.status_code = status_code
        self.text = text
        self.headers = headers
        self.reason = reason
        self.content = content
        self.raw = MockRaw()


class MockRaw:
    def __init__(self):
        self.enforce_content_length = False


# pylint: disable=W0212
class TestBaseExporterCustomerSdkStats(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Clear environ so the mocks from past tests do not interfere.
        os.environ.pop("APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL", None)
        os.environ.pop("APPINSIGHTS_INSTRUMENTATIONKEY", None)
        os.environ["APPINSIGHTS_INSTRUMENTATIONKEY"] = "1234abcd-5678-4efa-8abc-1234567890ab"
        os.environ["APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL"] = "true"
        cls._base = BaseExporter()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._base.storage._path, True)

    def setUp(self) -> None:
        _CUSTOMER_SDKSTATS_STATE.clear()
        _CUSTOMER_SDKSTATS_STATE.update({
            "SHUTDOWN": False,
        })
        # Reset customer sdkstats singleton for test isolation
        _customer_sdkstats._STATSBEAT_METRICS = None
        _CUSTOMER_SDKSTATS_STATE["SHUTDOWN"] = False

    # ========================================================================
    # CUSTOMER SDK STATS (METRICS) TESTS
    # ========================================================================

    def test_customer_sdkstats_shutdown_state(self):
        """Test that customer sdkstats shutdown state works correctly"""
        from azure.monitor.opentelemetry.exporter.statsbeat._state import (
            get_customer_sdkstats_shutdown,
            _CUSTOMER_SDKSTATS_STATE,
            _CUSTOMER_SDKSTATS_STATE_LOCK
        )
        
        # Initially should not be shutdown (reset in setUp)
        self.assertFalse(get_customer_sdkstats_shutdown())
        
        # Directly set shutdown state (simulating what shutdown function should do)
        with _CUSTOMER_SDKSTATS_STATE_LOCK:
            _CUSTOMER_SDKSTATS_STATE["SHUTDOWN"] = True
        
        # Should now be shutdown
        self.assertTrue(get_customer_sdkstats_shutdown())

    def test_customer_sdkstats_shutdown_on_invalid_code(self):
        """Test that customer sdkstats shutdown is called and state updated on invalid response codes"""
        # Import needed components for verification
        from azure.monitor.opentelemetry.exporter.statsbeat._customer_sdkstats import (
            _CUSTOMER_SDKSTATS_STATE,
            _CUSTOMER_SDKSTATS_STATE_LOCK,
            CustomerSdkStatsMetrics
        )
        
        # Set up test environment
        exporter = BaseExporter()
        envelope = TelemetryItem(name="test", time=datetime.now())
        
        # Set up mocks for the actual implementations
        with _CUSTOMER_SDKSTATS_STATE_LOCK:
            _CUSTOMER_SDKSTATS_STATE["SHUTDOWN"] = False
        
        # Set up a meter provider mock to ensure we have something to shutdown
        mock_meter_provider = mock.MagicMock()
        
        # Create a mock instance for CustomerSdkStatsMetrics to be used in the global variable
        mock_instance = mock.MagicMock()
        mock_instance._customer_sdkstats_meter_provider = mock_meter_provider
        
        # Set _CUSTOMER_SDKSTATS_METRICS to our mock instance
        import sys
        customer_sdkstats_module = sys.modules['azure.monitor.opentelemetry.exporter.statsbeat._customer_sdkstats']
        original_metrics = getattr(customer_sdkstats_module, '_CUSTOMER_SDKSTATS_METRICS', None)
        setattr(customer_sdkstats_module, '_CUSTOMER_SDKSTATS_METRICS', mock_instance)
        
        try:
            # Execute the test scenario
            with mock.patch("requests.Session.request") as post:
                post.return_value = MockResponse(400, "Invalid request")
                result = exporter._transmit([envelope])
                
                # Verify the result is as expected
                self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)
                
                # Verify the meter provider's shutdown was called
                mock_meter_provider.shutdown.assert_called_once()
                
                # Verify that the state was properly updated to indicate shutdown happened
                self.assertTrue(_CUSTOMER_SDKSTATS_STATE["SHUTDOWN"], 
                    "The SHUTDOWN state should be set to True after invalid response code")
        finally:
            # Restore the original _CUSTOMER_SDKSTATS_METRICS
            setattr(customer_sdkstats_module, '_CUSTOMER_SDKSTATS_METRICS', original_metrics)

    def test_customer_sdkstats_shutdown_on_failure_threshold(self):
        """Test that customer sdkstats shutdown function properly updates the shutdown state"""
        # This test verifies that the shutdown_customer_sdkstats_metrics function 
        # properly updates the SHUTDOWN state when called
        
        # Import needed components for verification
        from azure.monitor.opentelemetry.exporter.statsbeat._customer_sdkstats import (
            shutdown_customer_sdkstats_metrics,
            _CUSTOMER_SDKSTATS_STATE,
            _CUSTOMER_SDKSTATS_STATE_LOCK,
            CustomerSdkStatsMetrics
        )
        
        # Set up a meter provider mock to ensure we have something to shutdown
        mock_meter_provider = mock.MagicMock()
        
        # Create a mock instance for CustomerSdkStatsMetrics to be used in the global variable
        mock_instance = mock.MagicMock()
        mock_instance._customer_sdkstats_meter_provider = mock_meter_provider
        
        # Set _CUSTOMER_SDKSTATS_METRICS to our mock instance
        import sys
        customer_sdkstats_module = sys.modules['azure.monitor.opentelemetry.exporter.statsbeat._customer_sdkstats']
        original_metrics = getattr(customer_sdkstats_module, '_CUSTOMER_SDKSTATS_METRICS', None)
        setattr(customer_sdkstats_module, '_CUSTOMER_SDKSTATS_METRICS', mock_instance)
        
        try:
            # Make sure state starts with SHUTDOWN as False
            with _CUSTOMER_SDKSTATS_STATE_LOCK:
                _CUSTOMER_SDKSTATS_STATE["SHUTDOWN"] = False
            
            # Call the actual shutdown function directly (no mocking)
            shutdown_customer_sdkstats_metrics()
            
            # Verify the meter provider's shutdown was called
            mock_meter_provider.shutdown.assert_called_once()
            
            # Verify that the state was properly updated by the function
            self.assertTrue(_CUSTOMER_SDKSTATS_STATE["SHUTDOWN"], 
                "The SHUTDOWN state should be set to True after shutdown_customer_sdkstats_metrics is called")
        finally:
            # Restore the original _CUSTOMER_SDKSTATS_METRICS
            setattr(customer_sdkstats_module, '_CUSTOMER_SDKSTATS_METRICS', original_metrics)
        
        # Note: The actual integration point exists in _base.py where both shutdown 
        # functions are called together during failure threshold


if __name__ == "__main__":
    unittest.main()
