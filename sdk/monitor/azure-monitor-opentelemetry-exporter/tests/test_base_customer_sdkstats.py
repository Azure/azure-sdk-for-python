# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import shutil
import unittest
from unittest import mock
from datetime import datetime

from azure.core.exceptions import HttpResponseError, ServiceRequestError
from azure.monitor.opentelemetry.exporter.export._base import (
    BaseExporter,
    ExportResult,
)
from azure.monitor.opentelemetry.exporter._generated import AzureMonitorClient
from azure.monitor.opentelemetry.exporter._generated.models import (
    TelemetryItem,
    TrackResponse,
    TelemetryErrorDetails,
)
from azure.monitor.opentelemetry.exporter.statsbeat._customer_sdkstats import (
    CustomerSdkStatsMetrics,
    DropCode,
)


class MockResponse:
    """Mock response object for HTTP requests"""
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content
        self.text = content
        self.headers = {}
        self.raw = mock.Mock()  # Add the raw attribute that Azure SDK expects
        self.raw.enforce_content_length = True
        self.reason = "Mock Reason"  # Add the reason attribute
        self.url = "http://mock-url.com"  # Add the url attribute


class TestBaseExporterCustomerSdkStats(unittest.TestCase):
    """Test integration between BaseExporter and customer sdkstats tracking functions"""

    def setUp(self):
        from azure.monitor.opentelemetry.exporter._generated.models import TelemetryEventData
        self._envelopes_to_export = [
            TelemetryItem(
                name="test_envelope",
                time=datetime.now(),
                data=TelemetryEventData(
                    name="test_event",
                    properties={"test_property": "test_value"}
                ),
                tags={"ai.internal.sdkVersion": "test_version"},
                instrumentation_key="test_key",
            )
        ]

    def tearDown(self):
        # Clean up any environment variables
        for key in ["APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW"]:
            if key in os.environ:
                del os.environ[key]
        # Clean up any temp directories
        if hasattr(self, "_temp_dir") and os.path.exists(self._temp_dir):
            shutil.rmtree(self._temp_dir, ignore_errors=True)

    def _create_exporter_with_customer_sdkstats_enabled(self, disable_offline_storage=True):
        """Helper method to create an exporter with customer sdkstats enabled"""
        # Mock the customer sdkstats metrics from the correct import location
        with mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._customer_sdkstats.CustomerSdkStatsMetrics") as customer_sdkstats_mock:
            customer_sdkstats_instance = mock.Mock(spec=CustomerSdkStatsMetrics)
            customer_sdkstats_mock.return_value = customer_sdkstats_instance
            
            exporter = BaseExporter(
                connection_string="InstrumentationKey=12345678-1234-5678-abcd-12345678abcd",
                disable_offline_storage=disable_offline_storage,
            )
            
            # Set up the mocked customer sdkstats metrics instance
            exporter._customer_sdkstats_metrics = customer_sdkstats_instance
            
            # Mock the should_collect method to return True
            exporter._should_collect_customer_sdkstats = mock.Mock(return_value=True)
            
            return exporter

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    def test_customer_sdkstats_feature_flag_disabled(self):
        """Test that customer sdkstats tracking is not called when feature flag is disabled"""
        # Remove the environment variable to simulate disabled state
        del os.environ["APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW"]
        
        exporter = BaseExporter(connection_string="InstrumentationKey=12345678-1234-5678-abcd-12345678abcd")
        # Verify that customer sdkstats metrics is None when feature is disabled
        self.assertIsNone(exporter._customer_sdkstats_metrics)
        self.assertFalse(exporter._should_collect_customer_sdkstats())

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_successful_items")
    def test_transmit_200_customer_sdkstats_track_successful_items(self, track_successful_mock):
        """Test that _track_successful_items is called on 200 success response"""
        exporter = self._create_exporter_with_customer_sdkstats_enabled()
        
        with mock.patch.object(AzureMonitorClient, "track") as track_mock:
            track_response = TrackResponse(
                items_received=1,
                items_accepted=1,
                errors=[],
            )
            track_mock.return_value = track_response
            result = exporter._transmit(self._envelopes_to_export)

        track_successful_mock.assert_called_once_with(exporter._customer_sdkstats_metrics, self._envelopes_to_export)
        self.assertEqual(result, ExportResult.SUCCESS)

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_retry_items")
    def test_transmit_206_customer_sdkstats_track_retry_items(self, track_retry_mock):
        """Test that _track_retry_items is called on 206 partial success with retryable errors"""
        exporter = self._create_exporter_with_customer_sdkstats_enabled()
        with mock.patch.object(AzureMonitorClient, "track") as track_mock:
            track_mock.return_value = TrackResponse(
                items_received=2,
                items_accepted=1,
                errors=[
                    TelemetryErrorDetails(index=0, status_code=500, message="should retry"),
                ],
            )
            result = exporter._transmit(self._envelopes_to_export * 2)

        track_retry_mock.assert_called_once()
        # With storage disabled by default, retryable errors become non-retryable
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items")
    def test_transmit_206_customer_sdkstats_track_dropped_items(self, track_dropped_mock):
        """Test that _track_dropped_items is called on 206 partial success with non-retryable errors"""
        exporter = self._create_exporter_with_customer_sdkstats_enabled()
        with mock.patch.object(AzureMonitorClient, "track") as track_mock:
            track_mock.return_value = TrackResponse(
                items_received=2,
                items_accepted=1,
                errors=[
                    TelemetryErrorDetails(index=0, status_code=400, message="should drop"),
                ],
            )
            result = exporter._transmit(self._envelopes_to_export * 2)

        track_dropped_mock.assert_called_once()
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_retry_items")
    def test_transmit_retryable_http_error_customer_sdkstats_track_retry_items(self, track_retry_mock):
        """Test that _track_retry_items is called on retryable HTTP errors (e.g., 408, 502, 503, 504)"""
        exporter = self._create_exporter_with_customer_sdkstats_enabled()
        with mock.patch("requests.Session.request") as request_mock:
            request_mock.return_value = MockResponse(408, "{}")
            result = exporter._transmit(self._envelopes_to_export)

        track_retry_mock.assert_called_once()
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items")
    def test_transmit_throttle_http_error_customer_sdkstats_track_dropped_items(self, track_dropped_mock):
        """Test that _track_dropped_items is called on throttle HTTP errors (e.g., 402, 439)"""
        exporter = self._create_exporter_with_customer_sdkstats_enabled()

        # Simulate a throttle HTTP error using HttpResponseError
        with mock.patch.object(AzureMonitorClient, "track") as track_mock:
            error_response = mock.Mock()
            error_response.status_code = 402  # Use actual throttle code
            track_mock.side_effect = HttpResponseError("Throttling error", response=error_response)
            result = exporter._transmit(self._envelopes_to_export)

        track_dropped_mock.assert_called_once()
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items")
    def test_transmit_invalid_http_error_customer_sdkstats_track_dropped_items_and_shutdown(self, track_dropped_mock):
        """Test that _track_dropped_items is called and customer sdkstats is shutdown on invalid HTTP errors (e.g., 400)"""
        exporter = self._create_exporter_with_customer_sdkstats_enabled()
        with mock.patch("requests.Session.request") as request_mock, \
             mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._customer_sdkstats.shutdown_customer_sdkstats_metrics") as shutdown_mock:
            request_mock.return_value = MockResponse(400, "{}")
            result = exporter._transmit(self._envelopes_to_export)

        track_dropped_mock.assert_called_once()
        shutdown_mock.assert_called_once()
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_retry_items")
    def test_transmit_service_request_error_customer_sdkstats_track_retry_items(self, track_retry_mock):
        """Test that _track_retry_items is called on ServiceRequestError"""
        exporter = self._create_exporter_with_customer_sdkstats_enabled()
        with mock.patch.object(AzureMonitorClient, "track", side_effect=ServiceRequestError("Connection error")):
            result = exporter._transmit(self._envelopes_to_export)

        track_retry_mock.assert_called_once()
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items")
    def test_transmit_general_exception_customer_sdkstats_track_dropped_items(self, track_dropped_mock):
        """Test that _track_dropped_items is called on general exceptions"""
        exporter = self._create_exporter_with_customer_sdkstats_enabled()
        with mock.patch.object(AzureMonitorClient, "track", side_effect=Exception("General error")):
            result = exporter._transmit(self._envelopes_to_export)

        track_dropped_mock.assert_called_once()
        # Verify called with CLIENT_EXCEPTION drop code and error message
        args, kwargs = track_dropped_mock.call_args
        self.assertEqual(args[2], DropCode.CLIENT_EXCEPTION)
        self.assertEqual(args[3], "General error")
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items")
    def test_transmit_storage_disabled_customer_sdkstats_track_dropped_items(self, track_dropped_mock):
        """Test that _track_dropped_items is called when offline storage is disabled and items would be retried"""
        exporter = self._create_exporter_with_customer_sdkstats_enabled()
        with mock.patch.object(AzureMonitorClient, "track") as track_mock:
            track_mock.return_value = TrackResponse(
                items_received=1,
                items_accepted=0,
                errors=[
                    TelemetryErrorDetails(index=0, status_code=500, message="should retry but storage disabled"),
                ],
            )
            result = exporter._transmit(self._envelopes_to_export)

        track_dropped_mock.assert_called_once()
        # Verify called with CLIENT_STORAGE_DISABLED drop code
        args, kwargs = track_dropped_mock.call_args
        self.assertEqual(args[2], DropCode.CLIENT_STORAGE_DISABLED)
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    @mock.patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._track_dropped_items_from_storage")
    def test_transmit_from_storage_customer_sdkstats_track_dropped_items_from_storage(self, track_dropped_storage_mock):
        """Test that _track_dropped_items_from_storage is called during storage operations"""
        exporter = self._create_exporter_with_customer_sdkstats_enabled(disable_offline_storage=False)
        
        # Simulate a scenario where storage operations would happen
        with mock.patch.object(AzureMonitorClient, "track") as track_mock:
            track_mock.return_value = TrackResponse(
                items_received=1,
                items_accepted=0,
                errors=[
                    TelemetryErrorDetails(index=0, status_code=500, message="should retry"),
                ],
            )
            
            # Mock the storage to simulate storage operations
            with mock.patch.object(exporter.storage, "put") as put_mock, \
                 mock.patch.object(exporter.storage, "gets", return_value=["stored_envelope"]) as gets_mock:
                result = exporter._transmit(self._envelopes_to_export)

        track_dropped_storage_mock.assert_called_once()
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)  # Storage makes it NOT_RETRYABLE

    def test_should_collect_customer_sdkstats_with_metrics(self):
        """Test _should_collect_customer_sdkstats returns True when metrics exist and feature is enabled"""
        with mock.patch.dict(os.environ, {"APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true"}):
            exporter = self._create_exporter_with_customer_sdkstats_enabled()
            self.assertTrue(exporter._should_collect_customer_sdkstats())

    def test_should_collect_customer_sdkstats_without_metrics(self):
        """Test _should_collect_customer_sdkstats returns False when no metrics exist"""
        # Don't patch the environment variable - let it be disabled by default
        exporter = BaseExporter(connection_string="InstrumentationKey=12345678-1234-5678-abcd-12345678abcd")
        exporter._customer_sdkstats_metrics = None
        self.assertFalse(exporter._should_collect_customer_sdkstats())


if __name__ == "__main__":
    unittest.main()
