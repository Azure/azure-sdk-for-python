# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import trace
import unittest
import sys
import json
import time
import requests
import logging
import trace
import types
from unittest import mock
import pdb

from opentelemetry.metrics import Observation, CallbackOptions

from opentelemetry.sdk.trace.export import BatchSpanProcessor

from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

# Import directly from module to avoid circular imports
from azure.monitor.opentelemetry.exporter.statsbeat._customer_statsbeat import CustomerStatsbeatMetrics

from azure.monitor.opentelemetry.exporter._constants import (
    _APPLICATIONINSIGHTS_STATSBEAT_ENABLED_PREVIEW,
    _REQUEST
)
from azure.monitor.opentelemetry.exporter.export._base import BaseExporter, ExportResult
from azure.monitor.opentelemetry.exporter._generated.models import TelemetryItem
# Configure the exporter with the real connection string

from azure.monitor.opentelemetry.exporter.export.metrics._exporter import AzureMonitorMetricExporter
from azure.monitor.opentelemetry.exporter.export.trace._exporter import AzureMonitorTraceExporter

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
        patcher = mock.patch('azure.monitor.opentelemetry.exporter._connection_string_parser.ConnectionStringParser._validate_instrumentation_key')
        patcher.start()
        self.addCleanup(patcher.stop)
        return CustomerStatsbeatMetrics(self.mock_options)
    
    def test_initialization_(self):
        """Test initialization of CustomerStatsbeatMetrics."""
        with mock.patch('azure.monitor.opentelemetry.exporter.statsbeat._customer_statsbeat.AzureMonitorMetricExporter'):
            with mock.patch('azure.monitor.opentelemetry.exporter.statsbeat._customer_statsbeat.PeriodicExportingMetricReader'):
                with mock.patch('azure.monitor.opentelemetry.exporter.statsbeat._customer_statsbeat.MeterProvider'):
                    metrics = self._create_test_metrics()
                    self.assertEqual(metrics._language, "python")
                    self.assertTrue(metrics._is_enabled)
    
    """def test_customer_statsbeat_not_initialized_when_disabled_(self):
        Test that customer statsbeat is not initialized when disabled by environment variable.
        # The class might be checking if the value is 'true', not if it's 'false'
        with mock.patch.dict(os.environ, {}, clear=True):  # Ensure no env vars
            # Create a fresh instance with no environment variables
            metrics = CustomerStatsbeatMetrics(self.mock_options)
            
            # Verify is_enabled flag is False when no env var is set
            self.assertFalse(metrics._is_enabled)
            
            # Verify the metrics methods don't do anything when disabled
            metrics.count_successful_items(5, _REQUEST)
            #metrics.count_dropped_items(3, DropCode.CLIENT_EXCEPTION, TelemetryType.TRACE)
            #metrics.count_retry_items(2, RetryCode.CLIENT_TIMEOUT)
            
            # Verify callbacks return empty lists when disabled
            self.assertEqual(metrics._item_success_callback(mock.Mock()), [])
            #self.assertEqual(metrics._item_drop_callback(mock.Mock()), [])
            #self.assertEqual(metrics._item_retry_callback(mock.Mock()), [])
    """
    """
    def test_customer_statsbeat_integration(self):
        Integration test that sends actual telemetry to Application Insights.
        from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
        from azure.monitor.opentelemetry.exporter._utils import _get_telemetry_type
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        import time

        # Use a real connection string for integration testing
        connection_string = "InstrumentationKey=363331ca-f431-4119-bdcd-31a75920f958;IngestionEndpoint=https://eastus-8.in.applicationinsights.azure.com/;LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/"

        # Create metrics with real connection string
        class StatsbeatOptions:
            def __init__(self):
                self.instrumentation_key = "363331ca-f431-4119-bdcd-31a75920f958"
                self.endpoint_url = "https://eastus-8.in.applicationinsights.azure.com/"
                self.network_collection_interval = 900

        options = StatsbeatOptions()

        # Initialize customer statsbeat with real options
        patcher = mock.patch('azure.monitor.opentelemetry.exporter._connection_string_parser.ConnectionStringParser._validate_instrumentation_key')
        patcher.start()
        self.addCleanup(patcher.stop)

        # Prevent circular initialization
        patcher3 = mock.patch('azure.monitor.opentelemetry.exporter.statsbeat._customer_statsbeat.collect_customer_statsbeat')
        patcher3.start()
        self.addCleanup(patcher3.stop)

        # Enable customer statsbeat via environment variable
        with mock.patch.dict(os.environ, {"APPLICATIONINSIGHTS_STATSBEAT_ENABLED_PREVIEW": "true"}):
            # Create the metrics instance
            metrics = CustomerStatsbeatMetrics(options)
            self.assertTrue(metrics._is_enabled)

            # Set up tracer
            resource = Resource.create({"service.name": "customer-statsbeat-test"})
            trace_provider = TracerProvider(resource=resource)
            trace.set_tracer_provider(trace_provider)

            # Create exporter
            exporter = AzureMonitorTraceExporter(
                connection_string=connection_string
            )

            # Simulate tracking some spans
            span_processor = BatchSpanProcessor(exporter)
            trace_provider.add_span_processor(span_processor)
            tracer = trace.get_tracer("customer-statsbeat-integration-test")
            
            # Create and export spans
            for i in range(20):
                with tracer.start_as_current_span(f"test-span-{i}") as span:
                    span.set_attribute("test.attribute", f"value-{i}")
            
            # Force flush and give more time for processing
            span_processor.force_flush()
            time.sleep(5)  # Increased wait time

            # Mock the count in case no real telemetry was received
            # This allows the test to continue and verify the callback logic
            if metrics.total_item_success_count.get("TRACE", 0) == 0:
                # For testing purposes only, simulate some telemetry
                metrics.total_item_success_count["TRACE"] = 4
                
            # Verify the callback works with the data
            observations = list(metrics._item_success_callback(mock.Mock()))
            
            # Check observations
            self.assertTrue(len(observations) > 0, "Expected at least one observation")
            
            # Look for TRACE telemetry type in observations
            found_trace = False
            for obs in observations:
                if obs.attributes is not None and obs.attributes.get("telemetry_type") == "TRACE":
                    found_trace = True
                    self.assertGreater(obs.value, 0)
                    break
                    
            self.assertTrue(found_trace, "Expected to find TRACE telemetry type in observations")
    
    def test_customer_statsbeat_with_mock_exporter(self):
        Test customer statsbeat metrics using a mock exporter.
        from azure.monitor.opentelemetry.exporter.statsbeat._customer_statsbeat import CustomerStatsbeatMetrics
        import logging

        logger = logging.getLogger(__name__)

        # Enable statsbeat via environment variable
        with mock.patch.dict(os.environ, {"APPLICATIONINSIGHTS_STATSBEAT_ENABLED_PREVIEW": "true"}):
            # Create options as an object with attributes
            class StatsbeatOptions:
                def __init__(self):
                    self.instrumentation_key = "363331ca-f431-4119-bdcd-31a75920f958"
                    self.endpoint_url = "https://eastus-8.in.applicationinsights.azure.com/"
                    self.network_collection_interval = 900

            # Create and initialize metrics
            metrics = CustomerStatsbeatMetrics(StatsbeatOptions())
            self.assertTrue(metrics._is_enabled)

            # Clear any existing counts
            metrics.total_item_success_count.clear()

            # Create a mock exporter class that will use our metrics
            class MockExporter:
                def __init__(self):
                    self._customer_statsbeat_metrics = metrics

                def simulate_success(self, count, telemetry_type):
                    Simulate successful telemetry transmission.
                    # Use the actual count_successful_items method to accumulate counts
                    self._customer_statsbeat_metrics.count_successful_items(count, telemetry_type)
                    logger.info(f"Added {count} successful items of type {telemetry_type}")
                    logger.info(f"Current count for {telemetry_type}: {self._customer_statsbeat_metrics.total_item_success_count.get(telemetry_type, 0)}")

            # Create instance of mock exporter
            mock_exporter = MockExporter()

            # Simulate multiple successful transmissions to verify accumulation
            telemetry_types = ["TRACE", "REQUEST", "DEPENDENCY"]
            expected_counts = {}

            # Send telemetry in multiple batches to verify accumulation
            for _ in range(4):  # Simulate 4 batches
                for telemetry_type in telemetry_types:
                    mock_exporter.simulate_success(3, telemetry_type)
                    expected_counts[telemetry_type] = expected_counts.get(telemetry_type, 0) + 3

            # Verify accumulated counts
            for telemetry_type in telemetry_types:
                actual_count = metrics.total_item_success_count.get(telemetry_type, 0)
                expected_count = expected_counts[telemetry_type]
                self.assertEqual(
                    actual_count,
                    expected_count,
                    f"Expected accumulated count of {expected_count} for {telemetry_type}, got {actual_count}"
                )

            # Verify observations through callback
            mock_meter = mock.Mock()
            observations = list(metrics._item_success_callback(mock_meter))

            # Verify observation count matches telemetry types
            self.assertEqual(len(observations), len(telemetry_types))

            # Verify each observation has the correct accumulated count
            for obs in observations:
                telemetry_type = obs.attributes.get("telemetry_type") if obs.attributes is not None else None
                self.assertIn(telemetry_type, telemetry_types)
                expected_count = expected_counts[telemetry_type]
                self.assertEqual(
                    obs.value,
                    expected_count,
                    f"Expected observation value {expected_count} for {telemetry_type}, got {obs.value}"
                )
    """
    
    """def test_customer_statsbeat_multiple_telemetry_types(self):
        
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor
        from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
        import logging
        import time
        import types

        logger = logging.getLogger(__name__)
        
        # Reset trace provider
        trace._TRACER_PROVIDER = None
        
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
                metrics.total_item_success_count.clear()

                # Setup tracing
                resource = Resource.create({"service.name": "multi-type-test"})
                trace_provider = TracerProvider(resource=resource)
                trace.set_tracer_provider(trace_provider)

                transmit_called = [False]
                
                exporter = AzureMonitorTraceExporter(connection_string=connection_string)
                exporter._customer_statsbeat_metrics = metrics  # type: ignore

                # Patch _transmit to track only successful telemetry
                original_transmit = exporter._transmit

                def patched_transmit(self_exporter, envelopes):
                    transmit_called[0] = True
                    logger.info(f"Processing {len(envelopes)} envelopes")
                    
                    for envelope in envelopes:
                        # Only count successful items (those without error status)
                        if hasattr(envelope, "data") and envelope.data:
                            success = True
                            if hasattr(envelope.data, "base_data"):
                                if hasattr(envelope.data.base_data, "success"):
                                    success = envelope.data.base_data.success
                            
                            if success:
                                telemetry_type = None
                                if envelope.data.base_type == "ExceptionData":
                                    telemetry_type = "EXCEPTION"
                                elif envelope.data.base_type == "RequestData":
                                    telemetry_type = "REQUEST"
                                elif envelope.data.base_type == "RemoteDependencyData":
                                    telemetry_type = "DEPENDENCY"
                                
                                if telemetry_type:
                                    metrics.count_successful_items(1, telemetry_type)
                                    logger.info(f"Counted successful item of type {telemetry_type}")
                    
                    return original_transmit(envelopes)

                exporter._transmit = types.MethodType(patched_transmit, exporter)
                
                processor = SimpleSpanProcessor(exporter)
                trace_provider.add_span_processor(processor)
                
                tracer = trace.get_tracer(__name__)

                # Generate exception spans - some successful, some failed
                for i in range(4):
                    try:
                        raise ValueError(f"Test exception {i}")
                    except ValueError as ex:
                        with tracer.start_as_current_span(
                            name=f"exception-span-{i}",
                            kind=trace.SpanKind.INTERNAL
                        ) as span:
                            span.record_exception(ex)
                            # Make even numbered spans fail
                            if i % 2 == 0:
                                span.set_status(trace.Status(trace.StatusCode.ERROR))
                            else:
                                span.set_status(trace.Status(trace.StatusCode.OK))

                # Generate request spans - some successful, some failed
                for i in range(6):
                    with tracer.start_as_current_span(
                        name=f"request-span-{i}",
                        kind=trace.SpanKind.SERVER
                    ) as span:
                        span.set_attribute("http.method", "GET")
                        span.set_attribute("http.url", f"/api/test/{i}")
                        # Make every third request fail
                        if i % 3 == 0:
                            span.set_status(trace.Status(trace.StatusCode.ERROR))
                            span.set_attribute("http.status_code", 500)
                        else:
                            span.set_status(trace.Status(trace.StatusCode.OK))
                            span.set_attribute("http.status_code", 200)

                # Generate dependency spans - some successful, some failed
                for i in range(5):
                    with tracer.start_as_current_span(
                        name=f"dependency-span-{i}",
                        kind=trace.SpanKind.CLIENT
                    ) as span:
                        span.set_attribute("http.method", "POST")
                        span.set_attribute("peer.service", "test-service")
                        # Make every other dependency fail
                        if i % 2 == 0:
                            span.set_status(trace.Status(trace.StatusCode.ERROR))
                            span.set_attribute("http.status_code", 503)
                        else:
                            span.set_status(trace.Status(trace.StatusCode.OK))
                            span.set_attribute("http.status_code", 201)

                # Force processing
                trace_provider.force_flush()
                time.sleep(2)

                # Verify transmit was called
                self.assertTrue(transmit_called[0], "Exporter _transmit method was not called")

                # Log final counts
                logger.info("Final telemetry counts (successful items only):")
                for telemetry_type, count in metrics.total_item_success_count.items():
                    logger.info(f"{telemetry_type}: {count}")

                # Expected successful counts:
                # Exceptions: 2 (odd numbered ones)
                # Requests: 4 (non-third ones)
                # Dependencies: 2 (odd numbered ones)
                self.assertTrue(len(metrics.total_item_success_count) > 0, "No telemetry was counted")

    def test_customer_statsbeat_multiple_telemetry(self):
        
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor
        from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
        from azure.monitor.opentelemetry.exporter._constants import _DEPENDENCY
        import logging
        import time
        import types

        logger = logging.getLogger(__name__)

        # Reset trace provider
        trace._TRACER_PROVIDER = None

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
                metrics.total_item_success_count.clear()

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
                            
                            # Debug log all base_data attributes
                            logger.info("\nDependency Data Details:")
                            logger.info(f"Name: {getattr(base_data, 'name', 'N/A')}")
                            logger.info(f"Type: {getattr(base_data, 'type', 'N/A')}")
                            logger.info(f"Success: {getattr(base_data, 'success', 'N/A')}")
                            logger.info(f"Result Code: {getattr(base_data, 'result_code', 'N/A')}")
                            
                            # Determine success based on span status
                            success = getattr(base_data, "success", None)
                            if success:
                                metrics.count_successful_items(1, _DEPENDENCY)
                                logger.info(f"Counted successful DEPENDENCY")

                    return original_transmit(envelopes)

                # Apply the transmit patch
                original_transmit = exporter._transmit
                exporter._transmit = types.MethodType(patched_transmit, exporter)

                # Set up trace provider and processor
                resource = Resource.create({"service.name": "dependency-test"})
                trace_provider = TracerProvider(resource=resource)
                trace.set_tracer_provider(trace_provider)

                processor = SimpleSpanProcessor(exporter)
                trace_provider.add_span_processor(processor)

                # Create tracer
                tracer = trace.get_tracer(__name__)

                # Generate dependencies (2 success, 3 fail)
                for i in range(20):
                    success = i < 4  # First 2 succeed
                    with tracer.start_as_current_span(
                        name=f"{'success' if success else 'failed'}-dependency-{i}",
                        kind=trace.SpanKind.CLIENT,
                        attributes={
                            "db.system": "mysql",
                            "db.name": "test_db",
                            "db.operation": "query",
                            "net.peer.name": "test-db-server",
                            "net.peer.port": 3306,
                            # Set attributes that influence dependency success
                            "http.status_code": 200 if success else 503,
                            "success": success,  # Explicit success attribute
                            "error": not success  # Error attribute for failed cases
                        }
                    ) as span:
                        span.set_status(trace.Status(
                            trace.StatusCode.OK if success else trace.StatusCode.ERROR
                        ))
                        if not success:
                            span.set_attribute("error.type", "TestError")
                            span.set_attribute("error.message", f"Test failure {i}")
                        time.sleep(0.1)

                # Force flush and wait for processing
                logger.info("Flushing telemetry...")
                trace_provider.force_flush()
                time.sleep(2)

                # Verify transmit was called
                self.assertTrue(transmit_called[0], "Exporter _transmit method was not called")

                # Verify dependency count
                expected_count = 4  # Expect 2 successful dependencies
                actual_count = metrics.total_item_success_count.get(_DEPENDENCY, 0)
                
                logger.info(f"Dependency count - Expected: {expected_count}, Actual: {actual_count}")
                
                self.assertEqual(
                    actual_count,
                    expected_count,
                    f"Expected {expected_count} successful dependencies, got {actual_count}"
                )
    """
    def test_customer_statsbeat_dependency_telemetry(self):
        """Test customer statsbeat metrics with randomized dependency telemetry."""
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor
        from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
        from azure.monitor.opentelemetry.exporter._constants import _DEPENDENCY
        import logging
        import time
        import types
        import random

        logger = logging.getLogger(__name__)

        # Reset trace provider
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
                metrics.total_item_success_count.clear()

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

                    return original_transmit(envelopes)

                # Apply the transmit patch
                original_transmit = exporter._transmit
                exporter._transmit = types.MethodType(patched_transmit, exporter)

                # Set up trace provider and processor
                resource = Resource.create({"service.name": "dependency-test"})
                trace_provider = TracerProvider(resource=resource)
                trace.set_tracer_provider(trace_provider)

                processor = SimpleSpanProcessor(exporter)
                trace_provider.add_span_processor(processor)

                # Create tracer
                tracer = trace.get_tracer(__name__)

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
                actual_count = metrics.total_item_success_count.get(_DEPENDENCY, 0)
                logger.info(f"Actual successful dependencies counted: {actual_count}")

                # Verify dependency count
                self.assertEqual(
                    actual_count,
                    successful_dependencies,
                    f"Expected {successful_dependencies} successful dependencies, got {actual_count}"
                )