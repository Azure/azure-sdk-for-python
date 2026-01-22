# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import unittest
from unittest import mock
from datetime import datetime

from azure.core.exceptions import ServiceRequestTimeoutError, HttpResponseError
from requests.exceptions import ConnectionError, ReadTimeout, Timeout

from azure.monitor.opentelemetry.exporter._generated.exporter.models import (
    TelemetryItem,
    TelemetryEventData,
    RequestData,
    RemoteDependencyData,
    MonitorBase,
)
from azure.monitor.opentelemetry.exporter._constants import (
    DropCode,
    RetryCode,
    _APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW,
    _APPLICATIONINSIGHTS_SDKSTATS_EXPORT_INTERVAL,
    _DEFAULT_STATS_SHORT_EXPORT_INTERVAL,
    _exception_categories,
)
from azure.monitor.opentelemetry.exporter._storage import StorageExportResult
from azure.monitor.opentelemetry.exporter.statsbeat.customer._utils import (
    get_customer_sdkstats_export_interval,
    is_customer_sdkstats_enabled,
    categorize_status_code,
    _determine_client_retry_code,
    _get_telemetry_success_flag,
    track_successful_items,
    track_dropped_items,
    track_retry_items,
    track_dropped_items_from_storage,
)
from azure.monitor.opentelemetry.exporter.statsbeat.customer._state import (
    get_customer_stats_manager,
)


class TestCustomerSdkStatsUtils(unittest.TestCase):
    """Test suite for customer SDK stats utility functions."""

    def setUp(self):
        """Set up test environment."""
        # Enable customer SDK stats for testing
        os.environ[_APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW] = "true"

        # Reset the customer stats manager for each test
        manager = get_customer_stats_manager()
        manager.shutdown()

        # Create sample telemetry items for testing
        self._create_test_envelopes()

    def tearDown(self):
        """Clean up test environment."""
        # Clean up environment variables
        os.environ.pop(_APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW, None)
        os.environ.pop(_APPLICATIONINSIGHTS_SDKSTATS_EXPORT_INTERVAL, None)

        # Shutdown customer stats
        manager = get_customer_stats_manager()
        manager.shutdown()

    def _create_test_envelopes(self):
        """Create test telemetry envelopes for various telemetry types."""
        # Event envelope
        event_data = TelemetryEventData(name="test_event", properties={"test_property": "test_value"})
        event_monitor_base = MonitorBase(base_type="EventData", base_data=event_data)
        self.event_envelope = TelemetryItem(
            name="test_event_envelope",
            time=datetime.now(),
            data=event_monitor_base,
            tags={"ai.internal.sdkVersion": "test_version"},
            instrumentation_key="test_key",
        )

        # Request envelope (successful)
        request_data = RequestData(
            id="test_request",
            name="GET /test",
            url="https://example.com/test",
            success=True,
            response_code="200",
            duration="PT0.1S",
        )
        request_monitor_base = MonitorBase(base_type="RequestData", base_data=request_data)
        self.request_envelope_success = TelemetryItem(
            name="test_request_envelope",
            time=datetime.now(),
            data=request_monitor_base,
            tags={"ai.internal.sdkVersion": "test_version"},
            instrumentation_key="test_key",
        )

        # Request envelope (failed)
        failed_request_data = RequestData(
            id="test_failed_request",
            name="GET /test",
            url="https://example.com/test",
            success=False,
            response_code="500",
            duration="PT0.1S",
        )
        failed_request_monitor_base = MonitorBase(base_type="RequestData", base_data=failed_request_data)
        self.request_envelope_failed = TelemetryItem(
            name="test_failed_request_envelope",
            time=datetime.now(),
            data=failed_request_monitor_base,
            tags={"ai.internal.sdkVersion": "test_version"},
            instrumentation_key="test_key",
        )

        # Dependency envelope (successful)
        dependency_data = RemoteDependencyData(
            name="test_dependency",
            type="HTTP",
            target="example.com",
            success=True,
            result_code="200",
            duration="PT0.1S",
        )
        dependency_monitor_base = MonitorBase(base_type="RemoteDependencyData", base_data=dependency_data)
        self.dependency_envelope_success = TelemetryItem(
            name="test_dependency_envelope",
            time=datetime.now(),
            data=dependency_monitor_base,
            tags={"ai.internal.sdkVersion": "test_version"},
            instrumentation_key="test_key",
        )

        # Dependency envelope (failed)
        failed_dependency_data = RemoteDependencyData(
            name="test_failed_dependency",
            type="HTTP",
            target="example.com",
            success=False,
            result_code="500",
            duration="PT0.1S",
        )
        failed_dependency_monitor_base = MonitorBase(base_type="RemoteDependencyData", base_data=failed_dependency_data)
        self.dependency_envelope_failed = TelemetryItem(
            name="test_failed_dependency_envelope",
            time=datetime.now(),
            data=failed_dependency_monitor_base,
            tags={"ai.internal.sdkVersion": "test_version"},
            instrumentation_key="test_key",
        )

    def test_get_customer_sdkstats_export_interval_default(self):
        """Test getting default export interval when environment variable is not set."""
        # Ensure environment variable is not set
        os.environ.pop(_APPLICATIONINSIGHTS_SDKSTATS_EXPORT_INTERVAL, None)

        interval = get_customer_sdkstats_export_interval()

        self.assertEqual(interval, _DEFAULT_STATS_SHORT_EXPORT_INTERVAL)

    def test_get_customer_sdkstats_export_interval_custom(self):
        """Test getting custom export interval from environment variable."""
        # Set custom interval
        os.environ[_APPLICATIONINSIGHTS_SDKSTATS_EXPORT_INTERVAL] = "30"

        interval = get_customer_sdkstats_export_interval()

        self.assertEqual(interval, 30)

    def test_get_customer_sdkstats_export_interval_invalid(self):
        """Test getting export interval with invalid environment variable value."""
        # Set invalid interval
        os.environ[_APPLICATIONINSIGHTS_SDKSTATS_EXPORT_INTERVAL] = "invalid"

        interval = get_customer_sdkstats_export_interval()

        # Should return default when invalid
        self.assertEqual(interval, _DEFAULT_STATS_SHORT_EXPORT_INTERVAL)

    def test_get_customer_sdkstats_export_interval_empty(self):
        """Test getting export interval with empty environment variable."""
        # Set empty interval
        os.environ[_APPLICATIONINSIGHTS_SDKSTATS_EXPORT_INTERVAL] = ""

        interval = get_customer_sdkstats_export_interval()

        # Should return default when empty
        self.assertEqual(interval, _DEFAULT_STATS_SHORT_EXPORT_INTERVAL)

    def test_is_customer_sdkstats_enabled_true(self):
        """Test checking if customer SDK stats is enabled (true case)."""
        os.environ[_APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW] = "true"

        result = is_customer_sdkstats_enabled()

        self.assertTrue(result)

    def test_is_customer_sdkstats_enabled_false(self):
        """Test checking if customer SDK stats is enabled (false case)."""
        os.environ[_APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW] = "false"

        result = is_customer_sdkstats_enabled()

        self.assertFalse(result)

    def test_is_customer_sdkstats_enabled_not_set(self):
        """Test checking if customer SDK stats is enabled when not set."""
        os.environ.pop(_APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW, None)

        result = is_customer_sdkstats_enabled()

        self.assertFalse(result)

    def test_is_customer_sdkstats_enabled_case_insensitive(self):
        """Test that enabled check is case insensitive."""
        test_cases = ["TRUE", "True", "tRuE", "true"]

        for case in test_cases:
            with self.subTest(case=case):
                os.environ[_APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW] = case
                result = is_customer_sdkstats_enabled()
                self.assertTrue(result)

    def test_categorize_status_code_specific_codes(self):
        """Test categorization of specific HTTP status codes."""
        test_cases = {
            400: "Bad request",
            401: "Unauthorized",
            402: "Daily quota exceeded",
            403: "Forbidden",
            404: "Not found",
            408: "Request timeout",
            413: "Payload too large",
            429: "Too many requests",
            500: "Internal server error",
            502: "Bad gateway",
            503: "Service unavailable",
            504: "Gateway timeout",
        }

        for status_code, expected_message in test_cases.items():
            with self.subTest(status_code=status_code):
                result = categorize_status_code(status_code)
                self.assertEqual(result, expected_message)

    def test_categorize_status_code_generic_4xx(self):
        """Test categorization of generic 4xx status codes."""
        test_codes = [405, 410, 418, 499]  # Various 4xx codes not in specific map

        for status_code in test_codes:
            with self.subTest(status_code=status_code):
                result = categorize_status_code(status_code)
                self.assertEqual(result, "Client error 4xx")

    def test_categorize_status_code_generic_5xx(self):
        """Test categorization of generic 5xx status codes."""
        test_codes = [501, 505, 550, 599]  # Various 5xx codes not in specific map

        for status_code in test_codes:
            with self.subTest(status_code=status_code):
                result = categorize_status_code(status_code)
                self.assertEqual(result, "Server error 5xx")

    def test_categorize_status_code_other(self):
        """Test categorization of status codes outside 4xx/5xx ranges."""
        test_cases = {
            200: "status_200",
            301: "status_301",
            600: "status_600",
            100: "status_100",
        }

        for status_code, expected_message in test_cases.items():
            with self.subTest(status_code=status_code):
                result = categorize_status_code(status_code)
                self.assertEqual(result, expected_message)

    def test_determine_client_retry_code_http_errors(self):
        """Test determining retry code for HTTP errors with status codes."""
        test_status_codes = [401, 403, 408, 429, 500, 502, 503, 504]

        for status_code in test_status_codes:
            with self.subTest(status_code=status_code):
                error = HttpResponseError("Test error")
                error.status_code = status_code

                retry_code, message = _determine_client_retry_code(error)

                self.assertEqual(retry_code, status_code)
                self.assertIsNotNone(message)

    def test_determine_client_retry_code_http_error_with_message(self):
        """Test determining retry code for HTTP error with custom message."""
        error = HttpResponseError("Custom error message")
        error.status_code = 500
        error.message = "Custom error message"

        retry_code, message = _determine_client_retry_code(error)

        self.assertEqual(retry_code, 500)
        self.assertEqual(message, "Custom error message")

    def test_determine_client_retry_code_timeout_errors(self):
        """Test determining retry code for various timeout errors."""
        timeout_errors = [
            ServiceRequestTimeoutError("Service timeout"),
            ReadTimeout("Read timeout"),
            TimeoutError("Generic timeout"),
            Timeout("Requests timeout"),
        ]

        for error in timeout_errors:
            with self.subTest(error_type=type(error).__name__):
                retry_code, message = _determine_client_retry_code(error)

                self.assertEqual(retry_code, RetryCode.CLIENT_TIMEOUT)
                self.assertEqual(message, _exception_categories.TIMEOUT_EXCEPTION.value)

    def test_determine_client_retry_code_timeout_in_message(self):
        """Test determining retry code for errors with timeout in message."""

        class CustomError(Exception):
            def __init__(self, message):
                self.message = message
                super().__init__(message)

        timeout_messages = ["Connection timeout occurred", "Request timed out"]

        for message in timeout_messages:
            with self.subTest(message=message):
                error = CustomError(message)

                retry_code, result_message = _determine_client_retry_code(error)

                self.assertEqual(retry_code, RetryCode.CLIENT_TIMEOUT)
                self.assertEqual(result_message, _exception_categories.TIMEOUT_EXCEPTION.value)

    def test_determine_client_retry_code_network_errors(self):
        """Test determining retry code for network errors."""
        network_errors = [
            ConnectionError("Connection failed"),
            OSError("OS error occurred"),
        ]

        for error in network_errors:
            with self.subTest(error_type=type(error).__name__):
                retry_code, message = _determine_client_retry_code(error)

                self.assertEqual(retry_code, RetryCode.CLIENT_EXCEPTION)
                self.assertEqual(message, _exception_categories.NETWORK_EXCEPTION.value)

    def test_determine_client_retry_code_generic_error(self):
        """Test determining retry code for generic errors."""
        generic_error = ValueError("Generic error")

        retry_code, message = _determine_client_retry_code(generic_error)

        self.assertEqual(retry_code, RetryCode.CLIENT_EXCEPTION)
        self.assertEqual(message, _exception_categories.CLIENT_EXCEPTION.value)

    def test_get_telemetry_success_flag_request_success(self):
        """Test extracting success flag from successful request envelope."""
        success_flag = _get_telemetry_success_flag(self.request_envelope_success)

        self.assertTrue(success_flag)

    def test_get_telemetry_success_flag_request_failed(self):
        """Test extracting success flag from failed request envelope."""
        success_flag = _get_telemetry_success_flag(self.request_envelope_failed)

        self.assertFalse(success_flag)

    def test_get_telemetry_success_flag_dependency_success(self):
        """Test extracting success flag from successful dependency envelope."""
        success_flag = _get_telemetry_success_flag(self.dependency_envelope_success)

        self.assertTrue(success_flag)

    def test_get_telemetry_success_flag_dependency_failed(self):
        """Test extracting success flag from failed dependency envelope."""
        success_flag = _get_telemetry_success_flag(self.dependency_envelope_failed)

        self.assertFalse(success_flag)

    def test_get_telemetry_success_flag_event_envelope(self):
        """Test extracting success flag from event envelope (should return None)."""
        success_flag = _get_telemetry_success_flag(self.event_envelope)

        self.assertIsNone(success_flag)

    def test_get_telemetry_success_flag_no_data(self):
        """Test extracting success flag from envelope with no data."""
        envelope = TelemetryItem(
            name="test_envelope",
            time=datetime.now(),
            data=None,
            tags={"ai.internal.sdkVersion": "test_version"},
            instrumentation_key="test_key",
        )

        success_flag = _get_telemetry_success_flag(envelope)

        self.assertIsNone(success_flag)

    def test_get_telemetry_success_flag_no_base_type(self):
        """Test extracting success flag from envelope with no base_type."""
        monitor_base = MonitorBase(base_type=None, base_data=None)
        envelope = TelemetryItem(
            name="test_envelope",
            time=datetime.now(),
            data=monitor_base,
            tags={"ai.internal.sdkVersion": "test_version"},
            instrumentation_key="test_key",
        )

        success_flag = _get_telemetry_success_flag(envelope)

        self.assertIsNone(success_flag)

    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat.customer._utils.get_customer_stats_manager")
    def test_track_successful_items(self, mock_get_manager):
        """Test tracking successful items calls the manager correctly."""
        mock_manager = mock.Mock()
        mock_get_manager.return_value = mock_manager

        envelopes = [self.request_envelope_success, self.event_envelope]

        track_successful_items(envelopes)

        # Verify manager was called for each envelope
        self.assertEqual(mock_manager.count_successful_items.call_count, 2)

    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat.customer._utils.get_customer_stats_manager")
    def test_track_dropped_items_without_message(self, mock_get_manager):
        """Test tracking dropped items without error message."""
        mock_manager = mock.Mock()
        mock_get_manager.return_value = mock_manager

        envelopes = [self.request_envelope_success, self.event_envelope]

        track_dropped_items(envelopes, 400)  # Use HTTP status code 400 as DropCodeType

        # Verify manager was called for each envelope
        self.assertEqual(mock_manager.count_dropped_items.call_count, 2)

    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat.customer._utils.get_customer_stats_manager")
    def test_track_dropped_items_with_message(self, mock_get_manager):
        """Test tracking dropped items with error message."""
        mock_manager = mock.Mock()
        mock_get_manager.return_value = mock_manager

        envelopes = [self.request_envelope_success]
        error_message = "Custom error message"

        track_dropped_items(envelopes, DropCode.CLIENT_EXCEPTION, error_message)

        # Verify manager was called with error message
        mock_manager.count_dropped_items.assert_called_once()
        args = mock_manager.count_dropped_items.call_args
        self.assertEqual(args[1]["exception_message"], error_message)

    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat.customer._utils.get_customer_stats_manager")
    def test_track_retry_items(self, mock_get_manager):
        """Test tracking retry items calls the manager correctly."""
        mock_manager = mock.Mock()
        mock_get_manager.return_value = mock_manager

        envelopes = [self.request_envelope_success, self.dependency_envelope_success]
        error = ConnectionError("Network error")

        track_retry_items(envelopes, error)

        # Verify manager was called for each envelope
        self.assertEqual(mock_manager.count_retry_items.call_count, 2)

    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat.customer._utils.track_dropped_items")
    def test_track_dropped_items_from_storage_disabled(self, mock_track_dropped):
        """Test tracking dropped items from storage when storage is disabled."""
        envelopes = [self.event_envelope]

        track_dropped_items_from_storage(StorageExportResult.CLIENT_STORAGE_DISABLED, envelopes)

        mock_track_dropped.assert_called_once_with(envelopes, DropCode.CLIENT_STORAGE_DISABLED)

    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat.customer._utils.track_dropped_items")
    def test_track_dropped_items_from_storage_readonly(self, mock_track_dropped):
        """Test tracking dropped items from storage when storage is readonly."""
        envelopes = [self.event_envelope]

        track_dropped_items_from_storage(StorageExportResult.CLIENT_READONLY, envelopes)

        mock_track_dropped.assert_called_once_with(envelopes, DropCode.CLIENT_READONLY)

    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat.customer._utils.track_dropped_items")
    def test_track_dropped_items_from_storage_capacity_reached(self, mock_track_dropped):
        """Test tracking dropped items from storage when capacity is reached."""
        envelopes = [self.event_envelope]

        track_dropped_items_from_storage(StorageExportResult.CLIENT_PERSISTENCE_CAPACITY_REACHED, envelopes)

        mock_track_dropped.assert_called_once_with(envelopes, DropCode.CLIENT_PERSISTENCE_CAPACITY)

    @mock.patch(
        "azure.monitor.opentelemetry.exporter.statsbeat.customer._utils.get_local_storage_setup_state_exception"
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat.customer._utils.track_dropped_items")
    def test_track_dropped_items_from_storage_exception_state(self, mock_track_dropped, mock_get_exception):
        """Test tracking dropped items from storage when exception state is set."""
        mock_get_exception.return_value = "Storage exception occurred"
        envelopes = [self.event_envelope]

        track_dropped_items_from_storage("some_result", envelopes)

        mock_track_dropped.assert_called_once_with(
            envelopes, DropCode.CLIENT_EXCEPTION, _exception_categories.STORAGE_EXCEPTION.value
        )

    @mock.patch(
        "azure.monitor.opentelemetry.exporter.statsbeat.customer._utils.get_local_storage_setup_state_exception"
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat.customer._utils.track_dropped_items")
    def test_track_dropped_items_from_storage_string_result(self, mock_track_dropped, mock_get_exception):
        """Test tracking dropped items from storage when result is a string (exception)."""
        mock_get_exception.return_value = ""  # No exception state
        envelopes = [self.event_envelope]

        track_dropped_items_from_storage("Exception string", envelopes)

        mock_track_dropped.assert_called_once_with(
            envelopes, DropCode.CLIENT_EXCEPTION, _exception_categories.STORAGE_EXCEPTION.value
        )

    @mock.patch(
        "azure.monitor.opentelemetry.exporter.statsbeat.customer._utils.get_local_storage_setup_state_exception"
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat.customer._utils.track_dropped_items")
    def test_track_dropped_items_from_storage_success(self, mock_track_dropped, mock_get_exception):
        """Test tracking dropped items from storage when operation is successful."""
        mock_get_exception.return_value = ""  # No exception state
        envelopes = [self.event_envelope]

        # Simulate successful storage operation
        track_dropped_items_from_storage(StorageExportResult.LOCAL_FILE_BLOB_SUCCESS, envelopes)

        # Should not call track_dropped_items for successful operations
        mock_track_dropped.assert_not_called()


if __name__ == "__main__":
    unittest.main()
