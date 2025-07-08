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
    
    def test_successful_item_count(self):
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
                            metrics.count_successful_items(1, _TYPE_MAP.get(envelope_name, _UNKNOWN))

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
                    "http.status_code": 200 if success else random.choice([400, 500, 503])
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
