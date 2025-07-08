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
from azure.monitor.opentelemetry.exporter.statsbeat._customer_statsbeat import CustomerStatsbeatMetrics

from azure.monitor.opentelemetry.exporter._constants import (
    _APPLICATIONINSIGHTS_STATSBEAT_ENABLED_PREVIEW,
    _REQUEST,
    _DEPENDENCY,
    _REQ_RETRY_NAME,
    _CUSTOMER_STATSBEAT_LANGUAGE,
    _DEFAULT_STATS_SHORT_EXPORT_INTERVAL,
    _UNKNOWN,
    _TYPE_MAP,
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

class TestCustomerStatsbeat(unittest.TestCase):
    """Tests for CustomerStatsbeatMetrics."""
    def setUp(self):
        _REQUESTS_MAP.clear()
        # Clear singleton instance for test isolation
        CustomerStatsbeatMetrics._instance = None
        
        self.env_patcher = mock.patch.dict(os.environ, {
            "APPLICATIONINSIGHTS_STATSBEAT_ENABLED_PREVIEW": "true"
        })
        self.env_patcher.start()
        self.mock_options = mock.Mock()
        self.mock_options.instrumentation_key = "363331ca-f431-4119-bdcd-31a75920f958"
        self.mock_options.network_collection_interval = _DEFAULT_STATS_SHORT_EXPORT_INTERVAL
        self.mock_options.connection_string = "InstrumentationKey=363331ca-f431-4119-bdcd-31a75920f958;IngestionEndpoint=https://eastus-8.in.applicationinsights.azure.com/"
        self.mock_options.language = _CUSTOMER_STATSBEAT_LANGUAGE
        self.original_trace_provider = trace._TRACER_PROVIDER
        trace._TRACER_PROVIDER = None
        self.mock_options.metrics = CustomerStatsbeatMetrics(self.mock_options)
        self.mock_options.transmit_called = [False]

    def tearDown(self):
        self.env_patcher.stop()
        # Restore trace provider
        trace._TRACER_PROVIDER = self.original_trace_provider
        # Clean up singleton instances to prevent cross-test contamination
        if hasattr(self.mock_options, 'metrics') and self.mock_options.metrics:
            metrics = self.mock_options.metrics
            if hasattr(metrics, '_customer_statsbeat_metric_reader'):
                try:
                    # Shutdown to prevent additional periodic exports
                    metrics._customer_statsbeat_metric_reader.shutdown()
                except Exception:
                    pass  # Ignore shutdown errors
        CustomerStatsbeatMetrics._instance = None
    
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

        # Generate random number of dependencies (between 5 and 15)
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
                    "http.status_code": 200 if success else random.choice([401, 402, 403, 405, 500, 503])
                }
            ) as span:
                span.set_status(trace.Status(
                    trace.StatusCode.OK if success else trace.StatusCode.ERROR
                ))
                time.sleep(0.1)

        trace_provider.force_flush()
        
        self.metrics_instance = metrics
        
        self.assertTrue(self.mock_options.transmit_called[0], "Exporter _transmit method was not called")

        actual_count = metrics._counters.total_item_success_count.get(_DEPENDENCY, 0)

        self.assertEqual(
            actual_count,
            successful_dependencies,
            f"Expected {successful_dependencies} successful dependencies, got {actual_count}"
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
                    dropped_items += 1
                    
                    from azure.monitor.opentelemetry.exporter._constants import DropCode
                    from azure.monitor.opentelemetry.exporter._utils import categorize_exception_message, categorize_status_code
                    
                    # Randomly choose between HTTP status code failures and client exceptions
                    failure_type = random.choice(["http_status", "client_exception"])
                    
                    if failure_type == "http_status":
                        # HTTP status code failures from Application Insights
                        status_codes = [400, 401, 402, 403, 404, 408, 429, 500, 502, 503, 504]
                        status_code = random.choice(status_codes)
                        
                        categorized_reason = categorize_status_code(status_code)
                        
                        # Use the status code directly as the drop code (integer)
                        metrics.count_dropped_items(1, telemetry_type, status_code, None)
                    else:
                        # Client exception scenarios
                        exception_scenarios = [
                            "Connection timed out after 30 seconds",
                            "Request timed out after 60 seconds",          # Another timeout - should aggregate
                            "Operation timed out",                         # Another timeout - should aggregate
                            "Network connection failed: Connection refused",
                            "Network error: Host unreachable",             # Another network error - should aggregate
                            "Authentication failed: Invalid credentials", 
                            "Auth error: Token expired",                   # Another auth error - should aggregate
                            "Failed to parse response: Invalid JSON format",
                            "Parse error: Malformed XML",                  # Another parse error - should aggregate
                            "Disk storage full: Cannot write to file",
                            "Out of memory: Cannot allocate buffer",
                            "Memory allocation failed",                    # Another memory error - should aggregate
                            "HTTP 401 Unauthorized",
                            "HTTP 401 Invalid token",                     # Another 401 - should aggregate
                            "HTTP 403 Forbidden", 
                            "HTTP 500 Internal Server Error",
                            "HTTP 500 Database error",                    # Another 500 - should aggregate
                            "HTTP 503 Service Unavailable",
                            "Unknown transmission error",
                            "Unexpected error occurred"                   # Another unknown error - should aggregate
                        ]
                        
                        exception_message = random.choice(exception_scenarios)
                        
                        if "HTTP" in exception_message and any(char.isdigit() for char in exception_message):
                            try:
                                status_code = int(''.join(filter(str.isdigit, exception_message)))
                                categorized_reason = categorize_status_code(status_code)
                            except ValueError:
                                categorized_reason = categorize_exception_message(exception_message)
                        else:
                            categorized_reason = categorize_exception_message(exception_message)
                        
                        
                        metrics.count_dropped_items(1, telemetry_type, DropCode.CLIENT_EXCEPTION, exception_message)
                    
                    continue

            return ExportResult.SUCCESS

        exporter._transmit = types.MethodType(patched_transmit, exporter)

        resource = Resource.create({"service.name": "exception-test", "service.instance.id": "test-instance"})
        trace_provider = TracerProvider(resource=resource)
        
        processor = SimpleSpanProcessor(exporter)
        trace_provider.add_span_processor(processor)

        tracer = trace_provider.get_tracer(__name__)

        total_items = random.randint(10, 20)

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
                    }
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
                    }
                ) as span:
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    time.sleep(0.01)

        trace_provider.force_flush()
        
        self.metrics_instance = metrics
        
        self.assertTrue(self.mock_options.transmit_called[0], "Exporter _transmit method was not called")

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
                        else:
                            client_exception_totals[reason] = client_exception_totals.get(reason, 0) + count
                else:
                    actual_dropped_count += reason_map

        self.assertEqual(
            actual_dropped_count,
            dropped_items,
            f"Expected {dropped_items} dropped items, got {actual_dropped_count}"
        )