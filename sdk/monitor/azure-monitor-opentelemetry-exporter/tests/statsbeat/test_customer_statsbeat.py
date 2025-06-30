# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import unittest
import logging
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
    _REQ_RETRY_NAME
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

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TestCustomerStatsbeat(unittest.TestCase):
    """Tests for CustomerStatsbeatMetrics."""
    def setUp(self):
        _REQUESTS_MAP.clear()
        self.env_patcher = mock.patch.dict(os.environ, {
            "APPLICATIONINSIGHTS_STATSBEAT_ENABLED_PREVIEW": "true"
        })
        self.env_patcher.start()
        self.mock_options = mock.Mock()
        self.mock_options.instrumentation_key = "363331ca-f431-4119-bdcd-31a75920f958"
        self.mock_options.endpoint_url = "https://eastus-8.in.applicationinsights.azure.com/"
        self.mock_options.network_collection_interval = 900
    
    def tearDown(self):
        self.env_patcher.stop()
    
    def _create_test_metrics(self):
        patcher = mock.patch('azure.monitor.opentelemetry.exporter._connection_string_parser.ConnectionStringParser._validate_instrumentation_key')
        patcher.start()
        self.addCleanup(patcher.stop)
        return CustomerStatsbeatMetrics(self.mock_options)
    
    def test_initialization_(self):
        with mock.patch('azure.monitor.opentelemetry.exporter.statsbeat._customer_statsbeat.AzureMonitorMetricExporter'):
            with mock.patch('azure.monitor.opentelemetry.exporter.statsbeat._customer_statsbeat.PeriodicExportingMetricReader'):
                with mock.patch('azure.monitor.opentelemetry.exporter.statsbeat._customer_statsbeat.MeterProvider'):
                    metrics = self._create_test_metrics()
                    self.assertEqual(metrics._language, "python")
                    self.assertTrue(metrics._is_enabled)
    
    def test_mocks(self):
        original_trace_provider = trace._TRACER_PROVIDER
        trace._TRACER_PROVIDER = None

        # Track successful dependencies for verification
        successful_dependencies = 0

        connection_string = "InstrumentationKey=363331ca-f431-4119-bdcd-31a75920f958;IngestionEndpoint=https://eastus-8.in.applicationinsights.azure.com/"

        with mock.patch('azure.monitor.opentelemetry.exporter.statsbeat._customer_statsbeat.collect_customer_statsbeat'):
            with mock.patch.dict(os.environ, {"APPLICATIONINSIGHTS_STATSBEAT_ENABLED_PREVIEW": "true"}):
                # Initialize metrics
                class StatsbeatOptions:
                    def __init__(self):
                        self.instrumentation_key = "363331ca-f431-4119-bdcd-31a75920f958"
                        self.endpoint_url = "https://eastus-8.in.applicationinsights.azure.com/"
                        self.network_collection_interval = 900
                metrics = CustomerStatsbeatMetrics(StatsbeatOptions())
                metrics._counters.total_item_success_count.clear()

                # Create and configure exporter
                exporter = AzureMonitorTraceExporter(connection_string=connection_string)
                exporter._customer_statsbeat_metrics = metrics

                # Track transmit calls
                transmit_called = [False]

                def patched_transmit(self_exporter, envelopes):
                    transmit_called[0] = True
                    logger.info(f"\nProcessing {len(envelopes)} envelopes")

                    for envelope in envelopes:
                        if not hasattr(envelope, "data") or not envelope.data:
                            continue

                        if envelope.data.base_type == "RemoteDependencyData":
                            base_data = envelope.data.base_data
                            if base_data and hasattr(base_data, "success"):
                                if base_data.success:
                                    metrics.count_successful_items(1, _DEPENDENCY)
                                    logger.info(f"Counted successful DEPENDENCY")

                    return ExportResult.SUCCESS

                # Apply the transmit patch
                original_transmit = exporter._transmit
                exporter._transmit = types.MethodType(patched_transmit, exporter)

                # Set up trace provider and processor
                resource = Resource.create({"service.name": "dependency-test", "service.instance.id": "test-instance"})
                trace_provider = TracerProvider(resource=resource)
                
                processor = SimpleSpanProcessor(exporter)
                trace_provider.add_span_processor(processor)

                # Create tracer
                tracer = trace_provider.get_tracer(__name__)

                # Generate random number of dependencies (between 5 and 15)
                total_dependencies = random.randint(5, 15)
                logger.info(f"Generating {total_dependencies} dependencies")

                # Generate dependencies with random success/failure
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

                # Force flush and wait for processing
                logger.info("Flushing telemetry...")
                trace_provider.force_flush()
                time.sleep(2)

                # Verify transmit was called
                self.assertTrue(transmit_called[0], "Exporter _transmit method was not called")

                # Log counts
                logger.info(f"Generated dependencies - Total: {total_dependencies}, Expected Successful: {successful_dependencies}")
                actual_count = metrics._counters.total_item_success_count.get(_DEPENDENCY, 0)
                logger.info(f"Actual successful dependencies counted: {actual_count}")

                # Verify dependency count
                self.assertEqual(
                    actual_count,
                    successful_dependencies,
                    f"Expected {successful_dependencies} successful dependencies, got {actual_count}"
                )

        trace._TRACER_PROVIDER = original_trace_provider