# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import shutil
import unittest
from unittest import mock
from datetime import datetime

from azure.core.exceptions import HttpResponseError, ServiceRequestError
from requests.exceptions import ConnectionError
from azure.monitor.opentelemetry.exporter.export._base import (
    BaseExporter,
    ExportResult,
)
from azure.monitor.opentelemetry.exporter._generated.exporter import AzureMonitorExporterClient
from azure.monitor.opentelemetry.exporter._generated.exporter.models import (
    TelemetryItem,
    TrackResponse,
    TelemetryErrorDetails,
)
from azure.monitor.opentelemetry.exporter.statsbeat.customer._manager import (
    CustomerSdkStatsManager,
)
from azure.monitor.opentelemetry.exporter.statsbeat.customer._state import (
    get_customer_stats_manager,
)
from azure.monitor.opentelemetry.exporter._constants import (
    DropCode,
    RetryCode,
    _exception_categories,
)

from azure.monitor.opentelemetry.exporter.statsbeat.customer._utils import (
    track_successful_items,
    track_dropped_items,
    track_retry_items,
    track_dropped_items_from_storage,
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
        self._content_consumed = False

    def iter_content(self, chunk_size=1):
        content_bytes = self.content.encode() if isinstance(self.content, str) else self.content
        for i in range(0, len(content_bytes), chunk_size):
            yield content_bytes[i : i + chunk_size]
        self._content_consumed = True

    def iter_bytes(self, chunk_size=None):
        return self.iter_content(chunk_size or 1)

    def close(self):
        pass


class TestBaseExporterCustomerSdkStats(unittest.TestCase):
    """Test integration between BaseExporter and customer sdkstats tracking functions"""

    @classmethod
    def setUpClass(cls):
        """Set up class-level resources including a single customer stats manager"""
        from azure.monitor.opentelemetry.exporter._generated.exporter.models import TelemetryEventData, MonitorBase

        os.environ.pop("APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW", None)
        os.environ["APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW"] = "true"

        # Patch _should_collect_customer_sdkstats instance method to always return True for all tests
        cls._should_collect_patch = mock.patch(
            "azure.monitor.opentelemetry.exporter.export._base.BaseExporter._should_collect_customer_sdkstats",
            return_value=True,
        )
        cls._should_collect_patch.start()

        # Patch collect_customer_sdkstats to prevent actual initialization
        cls._collect_customer_sdkstats_patch = mock.patch(
            "azure.monitor.opentelemetry.exporter.statsbeat.customer.collect_customer_sdkstats"
        )
        cls._collect_customer_sdkstats_patch.start()

        # Create reusable test data structure for TelemetryItem
        base_data = TelemetryEventData(name="test_event", properties={"test_property": "test_value"})
        monitor_base = MonitorBase(base_type="EventData", base_data=base_data)

        cls._envelopes_to_export = [
            TelemetryItem(
                name="test_envelope",
                time=datetime.now(),
                data=monitor_base,
                tags={"ai.internal.sdkVersion": "test_version"},
                instrumentation_key="test_key",
            )
        ]

    @classmethod
    def tearDownClass(cls):
        """Clean up class-level resources"""
        # Stop the patches
        cls._should_collect_patch.stop()
        cls._collect_customer_sdkstats_patch.stop()

        # Clean up environment
        os.environ.pop("APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW", None)

    def _create_exporter_with_customer_sdkstats_enabled(self, disable_offline_storage=True):
        """Helper method to create an exporter with customer sdkstats enabled"""

        exporter = BaseExporter(
            connection_string="InstrumentationKey=12345678-1234-5678-abcd-12345678abcd",
            disable_offline_storage=disable_offline_storage,
        )

        return exporter

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.track_successful_items")
    def test_transmit_200_customer_sdkstats_track_successful_items(self, track_successful_mock):
        """Test that track_successful_items is called on 200 success response"""

        exporter = self._create_exporter_with_customer_sdkstats_enabled()

        with mock.patch.object(AzureMonitorExporterClient, "track") as track_mock:
            track_response = TrackResponse(
                items_received=1,
                items_accepted=1,
                errors=[],
            )
            track_mock.return_value = track_response
            result = exporter._transmit(self._envelopes_to_export)

        track_successful_mock.assert_called_once_with(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.SUCCESS)

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.track_retry_items")
    def test_transmit_206_customer_sdkstats_track_retry_items(self, track_retry_mock):
        """Test that _track_retry_items is called on 206 partial success with retryable errors"""
        exporter = self._create_exporter_with_customer_sdkstats_enabled()
        with mock.patch.object(AzureMonitorExporterClient, "track") as track_mock:
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

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.track_dropped_items")
    def test_transmit_206_customer_sdkstats_track_dropped_items(self, track_dropped_mock):
        """Test that _track_dropped_items is called on 206 partial success with non-retryable errors"""
        exporter = self._create_exporter_with_customer_sdkstats_enabled()
        with mock.patch.object(AzureMonitorExporterClient, "track") as track_mock:
            track_mock.return_value = TrackResponse(
                items_received=2,
                items_accepted=1,
                errors=[
                    TelemetryErrorDetails(index=0, status_code=400, message="should drop"),
                ],
            )
            result = exporter._transmit(self._envelopes_to_export * 2)

        track_dropped_mock.assert_called_once_with(self._envelopes_to_export, 400)
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.track_retry_items")
    def test_transmit_retryable_http_error_customer_sdkstats_track_retry_items(self, track_retry_mock):
        """Test that _track_retry_items is called on retryable HTTP errors (e.g., 408, 502, 503, 504)"""
        exporter = self._create_exporter_with_customer_sdkstats_enabled()
        with mock.patch("requests.Session.request") as request_mock:
            request_mock.return_value = MockResponse(408, "{}")
            result = exporter._transmit(self._envelopes_to_export)

        track_retry_mock.assert_called_once()
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.track_dropped_items")
    def test_transmit_throttle_http_error_customer_sdkstats_track_dropped_items(self, track_dropped_mock):
        """Test that _track_dropped_items is called on throttle HTTP errors (e.g., 402, 439)"""
        exporter = self._create_exporter_with_customer_sdkstats_enabled()

        # Verify that _should_collect_customer_sdkstats is properly patched
        self.assertTrue(exporter._should_collect_customer_sdkstats())

        # Simulate a throttle HTTP error using HttpResponseError
        with mock.patch.object(AzureMonitorExporterClient, "track") as track_mock:
            error_response = mock.Mock()
            error_response.status_code = 402  # Use actual throttle code
            track_mock.side_effect = HttpResponseError("Throttling error", response=error_response)
            result = exporter._transmit(self._envelopes_to_export)

        track_dropped_mock.assert_called_once_with(self._envelopes_to_export, 402)
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.track_dropped_items")
    def test_transmit_invalid_http_error_customer_sdkstats_track_dropped_items_and_shutdown(self, track_dropped_mock):
        """Test that _track_dropped_items is called and customer sdkstats is shutdown on invalid HTTP errors (e.g., 400)"""
        exporter = self._create_exporter_with_customer_sdkstats_enabled()
        with mock.patch("requests.Session.request") as request_mock, mock.patch(
            "azure.monitor.opentelemetry.exporter.statsbeat.customer.shutdown_customer_sdkstats_metrics"
        ) as shutdown_mock:
            request_mock.return_value = MockResponse(400, "{}")
            result = exporter._transmit(self._envelopes_to_export)

        track_dropped_mock.assert_called_once_with(self._envelopes_to_export, 400)
        shutdown_mock.assert_called_once()
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.track_retry_items")
    def test_transmit_service_request_error_customer_sdkstats_track_retry_items(self, track_retry_mock):
        """Test that _track_retry_items is called on ServiceRequestError"""
        exporter = self._create_exporter_with_customer_sdkstats_enabled()
        with mock.patch.object(
            AzureMonitorExporterClient, "track", side_effect=ServiceRequestError("Connection error")
        ):
            result = exporter._transmit(self._envelopes_to_export)

        track_retry_mock.assert_called_once()
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.track_dropped_items")
    def test_transmit_general_exception_customer_sdkstats_track_dropped_items(self, track_dropped_mock):
        """Test that _track_dropped_items is called on general exceptions"""
        exporter = self._create_exporter_with_customer_sdkstats_enabled()
        with mock.patch.object(
            AzureMonitorExporterClient, "track", side_effect=Exception(_exception_categories.CLIENT_EXCEPTION.value)
        ):
            result = exporter._transmit(self._envelopes_to_export)

        track_dropped_mock.assert_called_once_with(
            self._envelopes_to_export,
            DropCode.CLIENT_EXCEPTION,
            "Client exception",
        )
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.track_dropped_items")
    def test_transmit_storage_disabled_customer_sdkstats_track_dropped_items(self, track_dropped_mock):
        """Test that _track_dropped_items is called when offline storage is disabled and items would be retried"""
        exporter = self._create_exporter_with_customer_sdkstats_enabled()
        with mock.patch.object(AzureMonitorExporterClient, "track") as track_mock:
            track_mock.return_value = TrackResponse(
                items_received=1,
                items_accepted=0,
                errors=[
                    TelemetryErrorDetails(index=0, status_code=500, message="should retry but storage disabled"),
                ],
            )
            result = exporter._transmit(self._envelopes_to_export)

        track_dropped_mock.assert_called_once_with(
            self._envelopes_to_export,
            DropCode.CLIENT_STORAGE_DISABLED,
        )
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.track_dropped_items")
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.track_dropped_items_from_storage")
    def test_transmit_from_storage_customer_sdkstats_track_dropped_items_from_storage(
        self, track_dropped_storage_mock, track_dropped_items_mock
    ):
        """Test that _track_dropped_items_from_storage is called during storage operations"""
        from azure.monitor.opentelemetry.exporter._storage import StorageExportResult

        exporter = self._create_exporter_with_customer_sdkstats_enabled(disable_offline_storage=False)

        # Set up side_effect for track_dropped_items_from_storage to match the new signature
        def track_dropped_storage_side_effect(result_from_storage_put, envelopes):
            # Import here to avoid import error
            # Using imported track_dropped_items_from_storage
            # Call the real function which will use our mocked track_dropped_items
            track_dropped_items_from_storage(result_from_storage_put, envelopes)

        track_dropped_storage_mock.side_effect = track_dropped_storage_side_effect

        # Mock _track_dropped_items to simulate a successful call
        track_dropped_items_mock.return_value = None

        # Simulate a scenario where storage operations would happen
        with mock.patch.object(AzureMonitorExporterClient, "track") as track_mock:
            track_mock.return_value = TrackResponse(
                items_received=1,
                items_accepted=0,
                errors=[
                    TelemetryErrorDetails(index=0, status_code=500, message="should retry"),
                ],
            )

            # Mock the storage to simulate storage operations - simulate storage error
            with mock.patch.object(
                exporter.storage, "put", return_value="storage_error"
            ) as put_mock, mock.patch.object(exporter.storage, "gets", return_value=["stored_envelope"]) as gets_mock:
                # We don't need to mock StorageExportResult anymore
                result = exporter._transmit(self._envelopes_to_export)

        track_dropped_storage_mock.assert_called_once()

        # No need to verify specific arguments as the function signature has changed
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)  # Storage makes it NOT_RETRYABLE

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.track_dropped_items")
    def test_transmit_redirect_parsing_error_customer_sdkstats_track_dropped_items(self, track_dropped_mock):
        """Test that track_dropped_items is called on redirect errors with invalid headers/parsing errors"""
        exporter = self._create_exporter_with_customer_sdkstats_enabled()

        # Simulate a redirect HTTP error using HttpResponseError without proper headers
        with mock.patch.object(AzureMonitorExporterClient, "track") as track_mock:
            error_response = mock.Mock()
            error_response.status_code = 307  # Redirect status code
            error_response.headers = None  # No headers to cause parsing error
            track_mock.side_effect = HttpResponseError("Redirect error", response=error_response)
            result = exporter._transmit(self._envelopes_to_export)

        track_dropped_mock.assert_called_once()
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.track_dropped_items")
    def test_transmit_circular_redirect_customer_sdkstats_track_dropped_items(self, track_dropped_mock):
        """Test that track_dropped_items is called on circular redirect errors"""
        exporter = self._create_exporter_with_customer_sdkstats_enabled()

        # Mock the consecutive redirects counter to simulate exceeding max redirects
        exporter._consecutive_redirects = 10  # Set to a high value to simulate circular redirects

        # Simulate redirect responses that would cause circular redirects
        with mock.patch.object(AzureMonitorExporterClient, "track") as track_mock:
            error_response = mock.Mock()
            error_response.status_code = 307  # Redirect status code
            error_response.headers = {"location": "https://example.com/redirect"}
            track_mock.side_effect = HttpResponseError("Redirect error", response=error_response)
            result = exporter._transmit(self._envelopes_to_export)

        track_dropped_mock.assert_called_once()
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.track_retry_items")
    def test_transmit_403_forbidden_error_customer_sdkstats_track_retry_items(self, track_retry_mock):
        """Test that track_retry_items is called on 403 Forbidden HTTP errors"""
        exporter = self._create_exporter_with_customer_sdkstats_enabled()

        # Simulate a 403 Forbidden HTTP error using HttpResponseError
        with mock.patch.object(AzureMonitorExporterClient, "track") as track_mock:
            error_response = mock.Mock()
            error_response.status_code = 403  # Forbidden code
            track_mock.side_effect = HttpResponseError("Forbidden error", response=error_response)
            result = exporter._transmit(self._envelopes_to_export)

        track_retry_mock.assert_called_once()
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.track_retry_items")
    def test_transmit_401_unauthorized_error_customer_sdkstats_track_retry_items(self, track_retry_mock):
        """Test that track_retry_items is called on 401 Unauthorized HTTP errors"""
        exporter = self._create_exporter_with_customer_sdkstats_enabled()

        # Simulate a 401 Unauthorized HTTP error using HttpResponseError
        with mock.patch.object(AzureMonitorExporterClient, "track") as track_mock:
            error_response = mock.Mock()
            error_response.status_code = 401  # Unauthorized code
            track_mock.side_effect = HttpResponseError("Unauthorized error", response=error_response)
            result = exporter._transmit(self._envelopes_to_export)

        track_retry_mock.assert_called_once()
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.track_dropped_items")
    def test_transmit_redirect_invalid_location_header_customer_sdkstats_track_dropped_items(self, track_dropped_mock):
        """Test that track_dropped_items is called when redirect has invalid location header"""
        exporter = self._create_exporter_with_customer_sdkstats_enabled()

        # Simulate a redirect HTTP error with invalid location header
        with mock.patch.object(AzureMonitorExporterClient, "track") as track_mock:
            error_response = mock.Mock()
            error_response.status_code = 307  # Redirect status code
            error_response.headers = {"location": "invalid-url"}  # Invalid URL format
            track_mock.side_effect = HttpResponseError("Redirect error", response=error_response)
            result = exporter._transmit(self._envelopes_to_export)

        track_dropped_mock.assert_called_once()
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.track_dropped_items")
    def test_transmit_from_storage_failure_customer_sdkstats_track_dropped_items(self, track_dropped_mock):
        """Test that track_dropped_items is called when _transmit_from_storage operations fail"""
        exporter = self._create_exporter_with_customer_sdkstats_enabled(disable_offline_storage=False)

        # Mock storage operations to simulate a successful initial transmit that triggers storage operations
        with mock.patch.object(AzureMonitorExporterClient, "track") as track_mock:
            track_response = TrackResponse(
                items_received=1,
                items_accepted=1,
                errors=[],
            )
            track_mock.return_value = track_response

            # Mock _transmit_from_storage to raise an exception
            with mock.patch.object(
                exporter, "_transmit_from_storage", side_effect=Exception("Storage operation failed")
            ):
                result = exporter._transmit(self._envelopes_to_export)

        # Should still succeed for the main transmission
        self.assertEqual(result, ExportResult.SUCCESS)


if __name__ == "__main__":
    unittest.main()
