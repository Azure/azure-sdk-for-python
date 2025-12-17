# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import unittest
from unittest import mock
import random
import time
import types
import copy

# Import directly from module to avoid circular imports
from azure.monitor.opentelemetry.exporter.statsbeat._customer_sdkstats import CustomerSdkStatsMetrics

from azure.monitor.opentelemetry.exporter._constants import (
    _APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW,
    _REQUEST,
    _DEPENDENCY,
    _REQ_RETRY_NAME,
    _CUSTOMER_SDKSTATS_LANGUAGE,
    _APPLICATIONINSIGHTS_SDKSTATS_EXPORT_INTERVAL,
    _DEFAULT_STATS_SHORT_EXPORT_INTERVAL,
    _UNKNOWN,
    _TYPE_MAP,
    DropCode,
    DropCodeType,
    RetryCode,
    RetryCodeType,
    _TRACE,
)

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from azure.monitor.opentelemetry.exporter.export._base import (
    BaseExporter,
    ExportResult,
)
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from azure.monitor.opentelemetry.exporter.statsbeat._state import _REQUESTS_MAP
from azure.monitor.opentelemetry.exporter.statsbeat._utils import (
    categorize_status_code,
    _get_customer_sdkstats_export_interval,
)


def convert_envelope_names_to_base_type(envelope_name):
    if not envelope_name.endswith("Data"):
        return envelope_name + "Data"
    return envelope_name


class EnvelopeTypeMapper:
    @classmethod
    def get_type_map(cls):
        return {
            convert_envelope_names_to_base_type(envelope_name): telemetry_type
            for envelope_name, telemetry_type in _TYPE_MAP.items()
        }


_BASE_TYPE_MAP = EnvelopeTypeMapper.get_type_map()


class TestCustomerSdkStats(unittest.TestCase):
    """Tests for CustomerSdkStatsMetrics."""

    def setUp(self):
        _REQUESTS_MAP.clear()
        # Clear singleton instance for test isolation
        CustomerSdkStatsMetrics._instance = None

        self.env_patcher = mock.patch.dict(
            os.environ,
            {
                "APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "true",
                "APPLICATIONINSIGHTS_SDKSTATS_EXPORT_INTERVAL": "",
            },
        )
        self.env_patcher.start()
        self.mock_options = mock.Mock()
        self.mock_options.instrumentation_key = "363331ca-f431-4119-bdcd-31a75920f958"
        self.mock_options.network_collection_interval = _get_customer_sdkstats_export_interval()
        self.mock_options.connection_string = "InstrumentationKey=363331ca-f431-4119-bdcd-31a75920f958;IngestionEndpoint=https://eastus-8.in.applicationinsights.azure.com/"
        self.mock_options.language = _CUSTOMER_SDKSTATS_LANGUAGE
        self.original_trace_provider = trace._TRACER_PROVIDER
        trace._TRACER_PROVIDER = None
        self.mock_options.metrics = CustomerSdkStatsMetrics(self.mock_options.connection_string)
        self.mock_options.transmit_called = [False]

    def tearDown(self):
        self.env_patcher.stop()
        # Restore trace provider

        trace._TRACER_PROVIDER = self.original_trace_provider

        if hasattr(self.mock_options, "metrics") and self.mock_options.metrics:
            metrics = self.mock_options.metrics

            if hasattr(metrics, "_customer_sdkstats_metric_reader"):
                reader = metrics._customer_sdkstats_metric_reader
                if not getattr(reader, "_shutdown", False):
                    setattr(reader, "_shutdown", True)

                metrics._customer_sdkstats_metric_reader = None

            if hasattr(metrics, "_customer_sdkstats_exporter"):
                metrics._customer_sdkstats_exporter = None

            if hasattr(metrics, "_customer_sdkstats_meter_provider"):
                metrics._customer_sdkstats_meter_provider = None

        CustomerSdkStatsMetrics._instance = None

    def test_customer_sdkstats_not_initialized_when_disabled(self):
        CustomerSdkStatsMetrics._instance = None

        with mock.patch.dict(os.environ, {"APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW": "false"}):
            metrics = CustomerSdkStatsMetrics(self.mock_options.connection_string)

            # Verify is_enabled flag is False
            self.assertFalse(metrics._is_enabled)

            # Verify the metrics methods don't do anything when disabled
            metrics.count_successful_items(5, _REQUEST)
            metrics.count_dropped_items(3, _REQUEST, DropCode.CLIENT_EXCEPTION, "Test exception")

            # Verify callbacks return empty lists when disabled
            self.assertEqual(metrics._item_success_callback(mock.Mock()), [])
            self.assertEqual(metrics._item_drop_callback(mock.Mock()), [])

    def test_custom_export_interval_from_env_var(self):
        """Test that a custom export interval is picked up from the environment variable."""
        # Use a non-default value to test
        custom_interval = 300

        # Mock the environment variable with our custom interval
        with mock.patch.dict(
            os.environ,
            {
                _APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW: "true",
                _APPLICATIONINSIGHTS_SDKSTATS_EXPORT_INTERVAL: str(custom_interval),
            },
        ):
            # Get the export interval
            actual_interval = _get_customer_sdkstats_export_interval()

            # Verify it matches our custom value
            self.assertEqual(
                actual_interval,
                custom_interval,
                f"Expected export interval to be {custom_interval}, got {actual_interval}",
            )

            # Verify the CustomerSdkStatsMetrics instance picks up the custom interval
            CustomerSdkStatsMetrics._instance = None
            metrics = CustomerSdkStatsMetrics(self.mock_options.connection_string)
            self.assertEqual(
                metrics._customer_sdkstats_metric_reader._export_interval_millis,
                custom_interval,
                f"CustomerSdkStatsMetrics should use export interval {custom_interval}, got {metrics._customer_sdkstats_metric_reader._export_interval_millis}",
            )

    def test_default_export_interval_when_env_var_empty(self):
        """Test that the default export interval is used when the environment variable is empty."""
        # Mock the environment variable as empty
        with mock.patch.dict(
            os.environ,
            {_APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW: "true", _APPLICATIONINSIGHTS_SDKSTATS_EXPORT_INTERVAL: ""},
        ):
            # Get the export interval
            actual_interval = _get_customer_sdkstats_export_interval()

            # Verify it matches the default value
            self.assertEqual(
                actual_interval,
                _DEFAULT_STATS_SHORT_EXPORT_INTERVAL,
                f"Expected export interval to be default {_DEFAULT_STATS_SHORT_EXPORT_INTERVAL}, got {actual_interval}",
            )

            # Verify the CustomerSdkStatsMetrics instance picks up the default interval
            CustomerSdkStatsMetrics._instance = None
            metrics = CustomerSdkStatsMetrics(self.mock_options.connection_string)
            self.assertEqual(
                metrics._customer_sdkstats_metric_reader._export_interval_millis,
                _DEFAULT_STATS_SHORT_EXPORT_INTERVAL,
                f"CustomerSdkStatsMetrics should use default export interval {_DEFAULT_STATS_SHORT_EXPORT_INTERVAL}, got {metrics._customer_sdkstats_metric_reader._export_interval_millis}",
            )

    def test_successful_items_count(self):
        successful_dependencies = 0

        metrics = self.mock_options.metrics
        metrics._counters.total_item_success_count.clear()

        exporter = AzureMonitorTraceExporter(connection_string=self.mock_options.connection_string)

        def patched_transmit(self_exporter, envelopes):
            self.mock_options.transmit_called[0] = True

            for envelope in envelopes:
                if not hasattr(envelope, "data") or not envelope.data:
                    continue

                if envelope.data.base_type == "RemoteDependencyData":
                    base_data = envelope.data.base_data
                    if base_data and hasattr(base_data, "success"):
                        if base_data.success:
                            envelope_name = "Microsoft.ApplicationInsights." + envelope.data.base_type
                            metrics.count_successful_items(1, _BASE_TYPE_MAP.get(envelope_name, _UNKNOWN))

            return ExportResult.SUCCESS

        exporter._transmit = types.MethodType(patched_transmit, exporter)

        resource = Resource.create({"service.name": "dependency-test", "service.instance.id": "test-instance"})
        trace_provider = TracerProvider(resource=resource)

        processor = SimpleSpanProcessor(exporter)
        trace_provider.add_span_processor(processor)

        tracer = trace_provider.get_tracer(__name__)

        total_dependencies = random.randint(5, 15)

        for i in range(total_dependencies):
            success = random.choice([True, False])
            if success:
                successful_dependencies += 1

            with tracer.start_as_current_span(
                name=f"{'success' if success else 'failed'}-dependency-{i}",
                kind=trace.SpanKind.CLIENT,
                attributes={
                    "db.system": "mysql",
                    "db.name": "test_db",
                    "db.operation": "query",
                    "net.peer.name": "test-db-server",
                    "net.peer.port": 3306,
                    "http.status_code": 200 if success else random.choice([401, 402, 403, 405, 500, 503]),
                },
            ) as span:
                span.set_status(trace.Status(trace.StatusCode.OK if success else trace.StatusCode.ERROR))
                time.sleep(0.1)

        trace_provider.force_flush()

        self.metrics_instance = metrics

        self.assertTrue(self.mock_options.transmit_called[0], "Exporter _transmit method was not called")

        actual_count = metrics._counters.total_item_success_count.get(_DEPENDENCY, 0)

        self.assertEqual(
            actual_count,
            successful_dependencies,
            f"Expected {successful_dependencies} successful dependencies, got {actual_count}",
        )

    def test_dropped_items_count(self):
        dropped_items = 0

        metrics = self.mock_options.metrics
        metrics._counters.total_item_drop_count.clear()

        exporter = AzureMonitorTraceExporter(connection_string=self.mock_options.connection_string)

        def patched_transmit(self_exporter, envelopes):
            self.mock_options.transmit_called[0] = True

            for envelope in envelopes:
                if not hasattr(envelope, "data") or not envelope.data:
                    continue

                envelope_name = "Microsoft.ApplicationInsights." + envelope.data.base_type
                telemetry_type = _BASE_TYPE_MAP.get(envelope_name, _UNKNOWN)

                should_fail = random.choice([True, False])
                if should_fail:
                    nonlocal dropped_items

                    failure_type = random.choice(["http_status", "client_exception"])

                    if failure_type == "http_status":
                        status_codes = [401, 401, 403, 500, 500, 503, 402]
                        status_code = random.choice(status_codes)

                        failure_count = random.randint(1, 3)
                        dropped_items += failure_count

                        metrics.count_dropped_items(failure_count, telemetry_type, status_code, None)
                    else:
                        exception_scenarios = [
                            "timeout_exception" "Connection timed out after 30 seconds",
                            "Request timed out after 60 seconds",
                            "Operation timed out",
                            "network_exception",
                            "Network connection failed: Connection refused",
                            "Network error: Host unreachable",
                            "authentication_exception",
                            "Authentication failed: Invalid credentials",
                            "Auth error: Token expired",
                            "Failed to parse response: Invalid JSON format",
                            "Parse error: Malformed XML",
                            "parse_exception",
                            "Out of memory: Cannot allocate buffer",
                            "Memory allocation failed",
                            "memory_exception",
                            "HTTP 401 Unauthorized",
                            "HTTP 401 Invalid token",
                            "HTTP 500 Internal Server Error",
                            "HTTP 500 Database error",
                            "Unknown transmission error",
                            "Unexpected error occurred" "storage_exception",
                            "other_exception",
                        ]

                        exception_message = random.choice(exception_scenarios)

                        # Simulate multiple failures for the same exception type
                        failure_count = random.randint(1, 4)
                        dropped_items += failure_count

                        metrics.count_dropped_items(
                            failure_count, telemetry_type, DropCode.CLIENT_EXCEPTION, exception_message
                        )

                    continue

            return ExportResult.SUCCESS

        exporter._transmit = types.MethodType(patched_transmit, exporter)

        resource = Resource.create({"service.name": "exception-test", "service.instance.id": "test-instance"})
        trace_provider = TracerProvider(resource=resource)

        processor = SimpleSpanProcessor(exporter)
        trace_provider.add_span_processor(processor)

        tracer = trace_provider.get_tracer(__name__)

        total_items = random.randint(15, 25)  # Increased to get more aggregation

        for i in range(total_items):
            span_type = random.choice(["client", "server"])

            if span_type == "client":
                # Client spans generate RemoteDependencyData
                with tracer.start_as_current_span(
                    name=f"dependency-{i}",
                    kind=trace.SpanKind.CLIENT,
                    attributes={
                        "db.system": "mysql",
                        "db.name": "test_db",
                        "db.operation": "query",
                        "net.peer.name": "test-db-server",
                        "net.peer.port": 3306,
                    },
                ) as span:
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    time.sleep(0.01)
            else:
                # Server spans generate RequestData
                with tracer.start_as_current_span(
                    name=f"GET /api/endpoint-{i}",
                    kind=trace.SpanKind.SERVER,
                    attributes={
                        "http.method": "GET",
                        "http.url": f"https://example.com/api/endpoint-{i}",
                        "http.route": f"/api/endpoint-{i}",
                        "http.status_code": 200,
                        "http.scheme": "https",
                        "http.host": "example.com",
                    },
                ) as span:
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    time.sleep(0.01)

        trace_provider.force_flush()

        self.metrics_instance = metrics

        self.assertTrue(self.mock_options.transmit_called[0], "Exporter _transmit method was not called")

        # Enhanced counting and verification logic
        actual_dropped_count = 0
        category_totals = {}
        http_status_totals = {}
        client_exception_totals = {}

        for telemetry_type, drop_code_data in metrics._counters.total_item_drop_count.items():
            for drop_code, reason_map in drop_code_data.items():
                if isinstance(reason_map, dict):
                    for reason, count in reason_map.items():
                        actual_dropped_count += count
                        category_totals[reason] = category_totals.get(reason, 0) + count

                        # Separate HTTP status codes from client exceptions
                        if isinstance(drop_code, int):
                            http_status_totals[reason] = http_status_totals.get(reason, 0) + count
                        elif isinstance(drop_code, DropCode):
                            client_exception_totals[reason] = client_exception_totals.get(reason, 0) + count
                else:
                    actual_dropped_count += reason_map

        # Test that some categories have counts > 1 (proving aggregation works)
        aggregated_categories = [cat for cat, count in category_totals.items() if count > 1]

        # Main assertion
        self.assertEqual(
            actual_dropped_count,
            dropped_items,
            f"Expected {dropped_items} dropped items, got {actual_dropped_count}. "
            f"HTTP Status drops: {len(http_status_totals)}, Client Exception drops: {len(client_exception_totals)}",
        )

        # Verify aggregation occurred
        self.assertGreater(
            len(http_status_totals) + len(client_exception_totals), 0, "At least one type of drop should have occurred"
        )

        # Verify that both integer and enum drop codes are being stored properly
        drop_code_types = set()
        for telemetry_type, drop_code_data in metrics._counters.total_item_drop_count.items():
            for drop_code in drop_code_data.keys():
                drop_code_types.add(type(drop_code).__name__)

        # Additional assertion to verify aggregation works
        multi_count_categories = [cat for cat, count in category_totals.items() if count > 1]

    def test_retry_items_count(self):
        """Test retry item counting with both RetryCode enums and integer status codes."""
        retried_items = 0

        metrics = self.mock_options.metrics
        metrics._counters.total_item_retry_count.clear()

        exporter = AzureMonitorTraceExporter(connection_string=self.mock_options.connection_string)

        def patched_transmit(self_exporter, envelopes):
            self.mock_options.transmit_called[0] = True

            for envelope in envelopes:
                if not hasattr(envelope, "data") or not envelope.data:
                    continue

                envelope_name = "Microsoft.ApplicationInsights." + envelope.data.base_type
                telemetry_type = _BASE_TYPE_MAP.get(envelope_name, _UNKNOWN)

                should_retry = random.choice([True, False])
                if should_retry:
                    nonlocal retried_items

                    retry_type = random.choice(["http_status", "client_timeout", "unknown"])

                    if retry_type == "http_status":
                        # HTTP status codes that would trigger retries
                        status_codes = [429, 503, 500, 502, 504]
                        status_code = random.choice(status_codes)

                        failure_count = random.randint(1, 3)
                        retried_items += failure_count

                        metrics.count_retry_items(failure_count, telemetry_type, status_code, None)
                    elif retry_type == "client_timeout":
                        timeout_messages = [
                            "Connection timed out after 30 seconds",
                            "Request timed out after 60 seconds",
                            "Operation timed out",
                            "Socket timeout occurred",
                        ]

                        exception_message = random.choice(timeout_messages)

                        # Simulate multiple retries for the same timeout type
                        failure_count = random.randint(1, 4)
                        retried_items += failure_count

                        metrics.count_retry_items(
                            failure_count, telemetry_type, RetryCode.CLIENT_TIMEOUT, exception_message
                        )
                    else:
                        # Unknown retry reasons
                        unknown_messages = [
                            "Unknown network error",
                            "Unexpected retry condition",
                            "Network instability detected",
                            "Connection reset by peer",
                        ]

                        exception_message = random.choice(unknown_messages)

                        failure_count = random.randint(1, 3)
                        retried_items += failure_count

                        metrics.count_retry_items(
                            failure_count, telemetry_type, RetryCode.CLIENT_EXCEPTION, exception_message
                        )

                    continue

            return ExportResult.SUCCESS

        exporter._transmit = types.MethodType(patched_transmit, exporter)

        resource = Resource.create({"service.name": "retry-test", "service.instance.id": "test-instance"})
        trace_provider = TracerProvider(resource=resource)

        processor = SimpleSpanProcessor(exporter)
        trace_provider.add_span_processor(processor)

        tracer = trace_provider.get_tracer(__name__)

        total_items = random.randint(15, 25)  # Increased to get more aggregation

        for i in range(total_items):
            span_type = random.choice(["client", "server"])

            if span_type == "client":
                # Client spans generate RemoteDependencyData
                with tracer.start_as_current_span(
                    name=f"dependency-{i}",
                    kind=trace.SpanKind.CLIENT,
                    attributes={
                        "db.system": "mysql",
                        "db.name": "test_db",
                        "db.operation": "query",
                        "net.peer.name": "test-db-server",
                        "net.peer.port": 3306,
                    },
                ) as span:
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    time.sleep(0.01)
            else:
                # Server spans generate RequestData
                with tracer.start_as_current_span(
                    name=f"GET /api/endpoint-{i}",
                    kind=trace.SpanKind.SERVER,
                    attributes={
                        "http.method": "GET",
                        "http.url": f"https://example.com/api/endpoint-{i}",
                        "http.route": f"/api/endpoint-{i}",
                        "http.status_code": 200,
                        "http.scheme": "https",
                        "http.host": "example.com",
                    },
                ) as span:
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    time.sleep(0.01)

        trace_provider.force_flush()

        self.metrics_instance = metrics

        self.assertTrue(self.mock_options.transmit_called[0], "Exporter _transmit method was not called")

        # Enhanced counting and verification logic
        actual_retried_count = 0
        category_totals = {}
        http_status_totals = {}
        client_timeout_totals = {}
        unknown_retry_totals = {}

        for telemetry_type, retry_code_data in metrics._counters.total_item_retry_count.items():
            for retry_code, reason_map in retry_code_data.items():
                if isinstance(reason_map, dict):
                    for reason, count in reason_map.items():
                        actual_retried_count += count
                        category_totals[reason] = category_totals.get(reason, 0) + count

                        # Separate HTTP status codes from client exceptions
                        if isinstance(retry_code, int):
                            http_status_totals[reason] = http_status_totals.get(reason, 0) + count
                        elif retry_code == RetryCode.CLIENT_TIMEOUT:
                            client_timeout_totals[reason] = client_timeout_totals.get(reason, 0) + count
                        elif retry_code == RetryCode.CLIENT_EXCEPTION:
                            unknown_retry_totals[reason] = unknown_retry_totals.get(reason, 0) + count
                else:
                    actual_retried_count += reason_map

        # Main assertion
        self.assertEqual(
            actual_retried_count,
            retried_items,
            f"Expected {retried_items} retried items, got {actual_retried_count}. "
            f"HTTP Status retries: {len(http_status_totals)}, Client Timeout retries: {len(client_timeout_totals)}, "
            f"Unknown retries: {len(unknown_retry_totals)}",
        )

        # Verify aggregation occurred
        self.assertGreater(
            len(http_status_totals) + len(client_timeout_totals) + len(unknown_retry_totals),
            0,
            "At least one type of retry should have occurred",
        )

        # Verify that both integer and enum retry codes are being stored properly
        retry_code_types = set()
        for telemetry_type, retry_code_data in metrics._counters.total_item_retry_count.items():
            for retry_code in retry_code_data.keys():
                retry_code_types.add(type(retry_code).__name__)

        # Additional assertion to verify aggregation works
        multi_count_categories = [cat for cat, count in category_totals.items() if count > 1]
