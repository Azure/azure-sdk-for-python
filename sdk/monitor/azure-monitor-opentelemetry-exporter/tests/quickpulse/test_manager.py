# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

# cSpell:disable

import platform
import unittest
from unittest import mock

from opentelemetry.sdk.metrics import (
    Counter,
    Histogram,
    Meter,
    MeterProvider,
    ObservableGauge,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import SpanKind

from azure.monitor.opentelemetry.exporter._generated.models import ContextTagKeys
from azure.monitor.opentelemetry.exporter._quickpulse._constants import (
    _DEPENDENCY_DURATION_NAME,
    _DEPENDENCY_FAILURE_RATE_NAME,
    _DEPENDENCY_RATE_NAME,
    _EXCEPTION_RATE_NAME,
    _PROCESS_PHYSICAL_BYTES_NAME,
    _PROCESSOR_TIME_NAME,
    _PROCESS_TIME_NORMALIZED_NAME,
    _REQUEST_DURATION_NAME,
    _REQUEST_FAILURE_RATE_NAME,
    _REQUEST_RATE_NAME,
)
from azure.monitor.opentelemetry.exporter._quickpulse._cpu import (
    _get_process_memory,
    _get_process_time_normalized,
    _get_process_time_normalized_old,
)
from azure.monitor.opentelemetry.exporter._quickpulse._exporter import (
    _QuickpulseExporter,
    _QuickpulseMetricReader,
)
from azure.monitor.opentelemetry.exporter._quickpulse._generated.models import (
    TelemetryType,
)
from azure.monitor.opentelemetry.exporter._quickpulse._manager import (
    _QuickpulseManager,
    _apply_document_filters_from_telemetry_data,
    _derive_metrics_from_telemetry_data,
)
from azure.monitor.opentelemetry.exporter._quickpulse._state import (
    _get_global_quickpulse_state,
    _set_global_quickpulse_state,
    _QuickpulseState,
)
from azure.monitor.opentelemetry.exporter._quickpulse._types import (
    _DependencyData,
    _ExceptionData,
    _RequestData,
    _TraceData,
)
from azure.monitor.opentelemetry.exporter._utils import (
    _get_sdk_version,
    _populate_part_a_fields,
)


class TestQuickpulseManager(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        # Reset singleton state - only clear QuickpulseManager instances
        if _QuickpulseManager in _QuickpulseManager._instances:
            del _QuickpulseManager._instances[_QuickpulseManager]

    def tearDown(self):
        # Reset singleton state - only clear QuickpulseManager instances
        if _QuickpulseManager in _QuickpulseManager._instances:
            del _QuickpulseManager._instances[_QuickpulseManager]

    @classmethod
    def setUpClass(cls):
        _set_global_quickpulse_state(_QuickpulseState.PING_SHORT)
        cls.connection_string = "InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ac;LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/"
        cls.resource = Resource.create(
            {
                ResourceAttributes.SERVICE_INSTANCE_ID: "test_instance",
                ResourceAttributes.SERVICE_NAME: "test_service",
            }
        )

    @classmethod
    def tearDownClass(cls):
        _set_global_quickpulse_state(_QuickpulseState.OFFLINE)

    @mock.patch("opentelemetry.sdk.trace.id_generator.RandomIdGenerator.generate_trace_id")
    def test_init(self, generator_mock):
        generator_mock.return_value = "test_trace_id"
        part_a_fields = _populate_part_a_fields(self.resource)
        qpm = _QuickpulseManager()

        # Initialize with kwargs
        qpm.initialize(
            connection_string=self.connection_string,
            resource=self.resource,
        )

        self.assertEqual(_get_global_quickpulse_state(), _QuickpulseState.PING_SHORT)
        self.assertTrue(isinstance(qpm._exporter, _QuickpulseExporter))
        self.assertEqual(
            qpm._exporter._live_endpoint,
            "https://eastus.livediagnostics.monitor.azure.com/",
        )
        self.assertEqual(
            qpm._exporter._instrumentation_key,
            "4321abcd-5678-4efa-8abc-1234567890ac",
        )
        self.assertEqual(qpm._base_monitoring_data_point.version, _get_sdk_version())
        self.assertEqual(qpm._base_monitoring_data_point.invariant_version, 5)
        self.assertEqual(
            qpm._base_monitoring_data_point.instance, part_a_fields.get(ContextTagKeys.AI_CLOUD_ROLE_INSTANCE, "")
        )
        self.assertEqual(qpm._base_monitoring_data_point.role_name, part_a_fields.get(ContextTagKeys.AI_CLOUD_ROLE, ""))
        self.assertEqual(qpm._base_monitoring_data_point.machine_name, platform.node())
        self.assertEqual(qpm._base_monitoring_data_point.stream_id, "test_trace_id")
        self.assertTrue(isinstance(qpm._reader, _QuickpulseMetricReader))
        self.assertEqual(qpm._reader._exporter, qpm._exporter)
        self.assertEqual(qpm._reader._base_monitoring_data_point, qpm._base_monitoring_data_point)
        self.assertTrue(isinstance(qpm._meter_provider, MeterProvider))
        self.assertEqual(qpm._meter_provider._sdk_config.metric_readers, [qpm._reader])
        self.assertEqual(qpm._meter_provider._sdk_config.resource, self.resource)
        self.assertTrue(isinstance(qpm._meter, Meter))
        self.assertEqual(qpm._meter.name, "azure_monitor_live_metrics")
        self.assertTrue(isinstance(qpm._request_duration, Histogram))
        self.assertEqual(qpm._request_duration.name, _REQUEST_DURATION_NAME[0])
        self.assertTrue(isinstance(qpm._dependency_duration, Histogram))
        self.assertEqual(qpm._dependency_duration.name, _DEPENDENCY_DURATION_NAME[0])
        self.assertTrue(isinstance(qpm._request_rate_counter, Counter))
        self.assertEqual(qpm._request_rate_counter.name, _REQUEST_RATE_NAME[0])
        self.assertTrue(isinstance(qpm._request_failed_rate_counter, Counter))
        self.assertEqual(qpm._request_failed_rate_counter.name, _REQUEST_FAILURE_RATE_NAME[0])
        self.assertTrue(isinstance(qpm._dependency_rate_counter, Counter))
        self.assertEqual(qpm._dependency_rate_counter.name, _DEPENDENCY_RATE_NAME[0])
        self.assertTrue(isinstance(qpm._dependency_failure_rate_counter, Counter))
        self.assertEqual(qpm._dependency_failure_rate_counter.name, _DEPENDENCY_FAILURE_RATE_NAME[0])
        self.assertTrue(isinstance(qpm._exception_rate_counter, Counter))
        self.assertEqual(qpm._exception_rate_counter.name, _EXCEPTION_RATE_NAME[0])
        self.assertTrue(isinstance(qpm._process_memory_gauge, ObservableGauge))
        self.assertEqual(qpm._process_memory_gauge.name, _PROCESS_PHYSICAL_BYTES_NAME[0])
        self.assertEqual(qpm._process_memory_gauge._callbacks, [_get_process_memory])
        self.assertTrue(isinstance(qpm._process_time_gauge, ObservableGauge))
        self.assertEqual(qpm._process_time_gauge.name, _PROCESS_TIME_NORMALIZED_NAME[0])
        self.assertEqual(qpm._process_time_gauge._callbacks, [_get_process_time_normalized])
        self.assertTrue(isinstance(qpm._process_time_gauge_old, ObservableGauge))
        self.assertEqual(qpm._process_time_gauge_old.name, _PROCESSOR_TIME_NAME[0])
        self.assertEqual(qpm._process_time_gauge_old._callbacks, [_get_process_time_normalized_old])

    def test_singleton(self):
        part_a_fields = _populate_part_a_fields(self.resource)
        resource2 = Resource.create(
            {
                ResourceAttributes.SERVICE_INSTANCE_ID: "test_instance2",
                ResourceAttributes.SERVICE_NAME: "test_service2",
            }
        )
        qpm = _QuickpulseManager()
        qpm.initialize(
            connection_string=self.connection_string,
            resource=self.resource,
        )
        qpm2 = _QuickpulseManager()
        # Second instance should be the same singleton, so initialize should be ignored
        qpm2.initialize(
            connection_string=self.connection_string,
            resource=resource2,
        )
        self.assertEqual(qpm, qpm2)
        # Configuration should be from first initialization since singleton was already initialized
        self.assertEqual(
            qpm._base_monitoring_data_point.instance, part_a_fields.get(ContextTagKeys.AI_CLOUD_ROLE_INSTANCE, "")
        )
        self.assertEqual(qpm._base_monitoring_data_point.role_name, part_a_fields.get(ContextTagKeys.AI_CLOUD_ROLE, ""))
        self.assertEqual(
            qpm2._base_monitoring_data_point.instance, part_a_fields.get(ContextTagKeys.AI_CLOUD_ROLE_INSTANCE, "")
        )
        self.assertEqual(
            qpm2._base_monitoring_data_point.role_name, part_a_fields.get(ContextTagKeys.AI_CLOUD_ROLE, "")
        )

    def test_initialize_success(self):
        """Test successful initialization."""
        qpm = _QuickpulseManager()

        # Initially not initialized
        self.assertFalse(qpm.is_initialized())

        # Initialize should succeed
        result = qpm.initialize(connection_string=self.connection_string, resource=self.resource)
        self.assertTrue(result)
        self.assertTrue(qpm.is_initialized())

        # Should have created all necessary components
        self.assertIsNotNone(qpm._exporter)
        self.assertIsNotNone(qpm._reader)
        self.assertIsNotNone(qpm._meter_provider)
        self.assertIsNotNone(qpm._meter)
        self.assertIsNotNone(qpm._base_monitoring_data_point)

        # Cleanup
        qpm.shutdown()

    def test_initialize_already_initialized(self):
        """Test initialization when already initialized."""
        qpm = _QuickpulseManager()

        # First initialization
        result1 = qpm.initialize(connection_string=self.connection_string)
        self.assertTrue(result1)
        self.assertTrue(qpm.is_initialized())

        # Second initialization should return True without reinitializing
        result2 = qpm.initialize(connection_string=self.connection_string)
        self.assertTrue(result2)
        self.assertTrue(qpm.is_initialized())

        # Cleanup
        qpm.shutdown()

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._QuickpulseExporter")
    def test_initialize_failure(self, exporter_mock):
        """Test initialization failure handling."""
        exporter_mock.side_effect = Exception("Exporter creation failed")

        qpm = _QuickpulseManager()

        # Initialize should fail
        result = qpm.initialize(connection_string=self.connection_string)
        self.assertFalse(result)
        self.assertFalse(qpm.is_initialized())

        # Components should be cleaned up
        self.assertIsNone(qpm._exporter)
        self.assertIsNone(qpm._reader)
        self.assertIsNone(qpm._meter_provider)
        self.assertIsNone(qpm._meter)

    def test_initialize_with_default_resource(self):
        """Test initialization with default resource when none provided."""
        qpm = _QuickpulseManager()

        result = qpm.initialize(connection_string=self.connection_string)
        self.assertTrue(result)
        self.assertTrue(qpm.is_initialized())
        self.assertIsNotNone(qpm._base_monitoring_data_point)

        # Cleanup
        qpm.shutdown()

    def test_shutdown_success(self):
        """Test successful shutdown."""
        qpm = _QuickpulseManager()

        # Initialize first
        qpm.initialize(connection_string=self.connection_string)
        self.assertTrue(qpm.is_initialized())

        # Shutdown should succeed
        result = qpm.shutdown()
        self.assertTrue(result)
        self.assertFalse(qpm.is_initialized())

        # Components should be cleaned up
        self.assertIsNone(qpm._exporter)
        self.assertIsNone(qpm._reader)
        self.assertIsNone(qpm._meter_provider)
        self.assertIsNone(qpm._meter)

    def test_shutdown_not_initialized(self):
        """Test shutdown when not initialized."""
        qpm = _QuickpulseManager()

        # Shutdown should return False when not initialized
        result = qpm.shutdown()
        self.assertFalse(result)
        self.assertFalse(qpm.is_initialized())

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._logger")
    def test_shutdown_meter_provider_exception(self, logger_mock):
        """Test shutdown handling meter provider exception."""
        qpm = _QuickpulseManager()

        # Initialize first
        qpm.initialize(connection_string=self.connection_string)

        # Mock meter provider to raise exception on shutdown
        qpm._meter_provider.shutdown = mock.Mock(side_effect=Exception("Shutdown failed"))

        # Shutdown should handle exception and return False
        result = qpm.shutdown()
        self.assertFalse(result)
        self.assertFalse(qpm.is_initialized())

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._apply_document_filters_from_telemetry_data")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._derive_metrics_from_telemetry_data")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._TelemetryData")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._is_post_state")
    def test_record_span_server_success(self, post_state_mock, data_mock, metric_derive_mock, doc_mock):
        post_state_mock.return_value = True
        span_mock = mock.Mock()
        span_mock.end_time = 10
        span_mock.start_time = 5
        span_mock.status.is_ok = True
        span_mock.kind = SpanKind.SERVER
        span_mock.events = []
        data = _RequestData(
            custom_dimensions={},
            duration=1000,
            success=True,
            name="test_req",
            response_code=400,
            url="test_url",
        )
        data_mock._from_span.return_value = data
        qpm = _QuickpulseManager()
        qpm.initialize(
            connection_string=self.connection_string,
            resource=self.resource,
        )

        # Mock the metric instruments
        qpm._request_rate_counter = mock.Mock()
        qpm._request_duration = mock.Mock()

        qpm._record_span(span_mock)
        qpm._request_rate_counter.add.assert_called_once_with(1)
        qpm._request_duration.record.assert_called_once_with(5e-09)
        data_mock._from_span.assert_called_once_with(span_mock)
        metric_derive_mock.assert_called_once_with(data)
        doc_mock.assert_called_once_with(data)

        # Cleanup
        qpm.shutdown()

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._apply_document_filters_from_telemetry_data")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._derive_metrics_from_telemetry_data")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._TelemetryData")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._is_post_state")
    def test_record_span_server_failure(self, post_state_mock, data_mock, metric_derive_mock, doc_mock):
        post_state_mock.return_value = True
        span_mock = mock.Mock()
        span_mock.end_time = 10
        span_mock.start_time = 5
        span_mock.status.is_ok = False
        span_mock.kind = SpanKind.SERVER
        span_mock.events = []
        data = _RequestData(
            custom_dimensions={},
            duration=1000,
            success=False,
            name="test_req",
            response_code=400,
            url="test_url",
        )
        data_mock._from_span.return_value = data
        qpm = _QuickpulseManager()
        qpm.initialize(
            connection_string=self.connection_string,
            resource=self.resource,
        )

        # Mock the metric instruments
        qpm._request_failed_rate_counter = mock.Mock()
        qpm._request_duration = mock.Mock()

        qpm._record_span(span_mock)
        qpm._request_failed_rate_counter.add.assert_called_once_with(1)
        qpm._request_duration.record.assert_called_once_with(5e-09)
        data_mock._from_span.assert_called_once_with(span_mock)
        metric_derive_mock.assert_called_once_with(data)
        doc_mock.assert_called_once_with(data)

        # Cleanup
        qpm.shutdown()

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._apply_document_filters_from_telemetry_data")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._derive_metrics_from_telemetry_data")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._TelemetryData")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._is_post_state")
    def test_record_span_dep_success(self, post_state_mock, data_mock, metric_derive_mock, doc_mock):
        post_state_mock.return_value = True
        span_mock = mock.Mock()
        span_mock.end_time = 10
        span_mock.start_time = 5
        span_mock.status.is_ok = True
        span_mock.kind = SpanKind.CLIENT
        span_mock.events = []
        data = _DependencyData(
            custom_dimensions={},
            duration=1000,
            name="test_dep",
            result_code=200,
            target="target",
            type="test_type",
            data="test_data",
            success=True,
        )
        data_mock._from_span.return_value = data
        qpm = _QuickpulseManager()
        qpm.initialize(
            connection_string=self.connection_string,
            resource=self.resource,
        )

        # Mock the metric instruments
        qpm._dependency_rate_counter = mock.Mock()
        qpm._dependency_duration = mock.Mock()

        qpm._record_span(span_mock)
        qpm._dependency_rate_counter.add.assert_called_once_with(1)
        qpm._dependency_duration.record.assert_called_once_with(5e-09)
        data_mock._from_span.assert_called_once_with(span_mock)
        metric_derive_mock.assert_called_once_with(data)
        doc_mock.assert_called_once_with(data)

        # Cleanup
        qpm.shutdown()

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._apply_document_filters_from_telemetry_data")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._derive_metrics_from_telemetry_data")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._TelemetryData")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._is_post_state")
    def test_record_span_dep_failure(self, post_state_mock, data_mock, metric_derive_mock, doc_mock):
        post_state_mock.return_value = True
        span_mock = mock.Mock()
        span_mock.end_time = 10
        span_mock.start_time = 5
        span_mock.status.is_ok = False
        span_mock.kind = SpanKind.CLIENT
        span_mock.events = []
        data = _DependencyData(
            custom_dimensions={},
            duration=1000,
            name="test_dep",
            result_code=200,
            target="target",
            type="test_type",
            data="test_data",
            success=False,
        )
        data_mock._from_span.return_value = data
        qpm = _QuickpulseManager()
        qpm.initialize(
            connection_string=self.connection_string,
            resource=self.resource,
        )

        # Mock the metric instruments
        qpm._dependency_failure_rate_counter = mock.Mock()
        qpm._dependency_duration = mock.Mock()

        qpm._record_span(span_mock)
        qpm._dependency_failure_rate_counter.add.assert_called_once_with(1)
        qpm._dependency_duration.record.assert_called_once_with(5e-09)
        data_mock._from_span.assert_called_once_with(span_mock)
        metric_derive_mock.assert_called_once_with(data)
        doc_mock.assert_called_once_with(data)

        # Cleanup
        qpm.shutdown()

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._apply_document_filters_from_telemetry_data")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._derive_metrics_from_telemetry_data")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._TelemetryData")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._is_post_state")
    def test_record_span_derive_filter_metrics(self, post_state_mock, data_mock, metric_derive_mock, doc_mock):
        post_state_mock.return_value = True
        span_mock = mock.Mock()
        span_mock.end_time = 10
        span_mock.start_time = 5
        span_mock.events = []
        data = _RequestData(
            custom_dimensions={},
            duration=1000,
            success=True,
            name="test_req",
            response_code=400,
            url="test_url",
        )
        data_mock._from_span.return_value = data
        qpm = _QuickpulseManager()
        qpm.initialize(
            connection_string=self.connection_string,
            resource=self.resource,
        )
        qpm._record_span(span_mock)
        data_mock._from_span.assert_called_once_with(span_mock)
        metric_derive_mock.assert_called_once_with(data)
        doc_mock.assert_called_once_with(data)

        # Cleanup
        qpm.shutdown()

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._ExceptionData")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._apply_document_filters_from_telemetry_data")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._derive_metrics_from_telemetry_data")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._TelemetryData")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._is_post_state")
    def test_record_span_span_event_exception(
        self,
        post_state_mock,
        data_mock,
        metric_derive_mock,
        doc_mock,
        exc_data_mock,
    ):
        post_state_mock.return_value = True
        span_mock = mock.Mock()
        event_mock = mock.Mock()
        event_mock.name = "exception"
        span_mock.events = [event_mock]
        span_mock.end_time = 10
        span_mock.start_time = 5
        data = _RequestData(
            custom_dimensions={},
            duration=1000,
            success=True,
            name="test_req",
            response_code=400,
            url="test_url",
        )
        exc_data = _ExceptionData(
            custom_dimensions={},
            message="exception",
            stack_trace="",
        )
        data_mock._from_span.return_value = data
        exc_data_mock._from_span_event.return_value = exc_data
        qpm = _QuickpulseManager()
        qpm.initialize(
            connection_string=self.connection_string,
            resource=self.resource,
        )

        # Mock the metric instruments
        qpm._exception_rate_counter = mock.Mock()

        qpm._record_span(span_mock)
        qpm._exception_rate_counter.add.assert_called_once_with(1)
        data_mock._from_span.assert_called_once_with(span_mock)
        exc_data_mock._from_span_event.assert_called_once_with(event_mock)
        metric_derive_mock.assert_any_call(data)
        doc_mock.assert_any_call(data)
        metric_derive_mock.assert_any_call(exc_data)
        doc_mock.assert_any_call(exc_data)

        # Cleanup
        qpm.shutdown()

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._apply_document_filters_from_telemetry_data")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._derive_metrics_from_telemetry_data")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._TelemetryData")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._is_post_state")
    def test_record_log(self, post_state_mock, data_mock, metric_derive_mock, doc_mock):
        post_state_mock.return_value = True
        log_record_mock = mock.Mock()
        log_record_mock.attributes = {}
        log_data_mock = mock.Mock()
        log_data_mock.log_record = log_record_mock
        data = _TraceData(
            message="body",
            custom_dimensions={},
        )
        data_mock._from_log_record.return_value = data
        qpm = _QuickpulseManager()
        qpm.initialize(
            connection_string=self.connection_string,
            resource=self.resource,
        )

        # Mock the metric instruments
        qpm._exception_rate_counter = mock.Mock()

        qpm._record_log_record(log_data_mock)
        qpm._exception_rate_counter.add.assert_not_called()
        data_mock._from_log_record.assert_called_once_with(log_record_mock)
        metric_derive_mock.assert_called_once_with(data)
        doc_mock.assert_called_once_with(data, None)

        # Cleanup
        qpm.shutdown()

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._apply_document_filters_from_telemetry_data")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._derive_metrics_from_telemetry_data")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._TelemetryData")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._is_post_state")
    def test_record_log_exception(self, post_state_mock, data_mock, metric_derive_mock, doc_mock):
        post_state_mock.return_value = True
        log_record_mock = mock.Mock()
        log_data_mock = mock.Mock()
        log_data_mock.log_record = log_record_mock
        data = _ExceptionData(
            message="exc_message",
            stack_trace="",
            custom_dimensions={},
        )
        data_mock._from_log_record.return_value = data
        attributes = {
            SpanAttributes.EXCEPTION_TYPE: "exc_type",
            SpanAttributes.EXCEPTION_MESSAGE: "exc_msg",
        }
        log_data_mock.log_record.attributes = attributes
        qpm = _QuickpulseManager()
        qpm.initialize(
            connection_string=self.connection_string,
            resource=self.resource,
        )

        # Mock the metric instruments
        qpm._exception_rate_counter = mock.Mock()

        qpm._record_log_record(log_data_mock)
        qpm._exception_rate_counter.add.assert_called_once_with(1)
        data_mock._from_log_record.assert_called_once_with(log_record_mock)
        metric_derive_mock.assert_called_once_with(data)
        doc_mock.assert_called_once_with(data, "exc_type")

        # Cleanup
        qpm.shutdown()

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._apply_document_filters_from_telemetry_data")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._derive_metrics_from_telemetry_data")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._TelemetryData")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._is_post_state")
    def test_record_log_derive_filter_metrics(self, post_state_mock, data_mock, metric_derive_mock, doc_mock):
        post_state_mock.return_value = True
        log_record_mock = mock.Mock()
        log_record_mock.attributes = {}
        log_data_mock = mock.Mock()
        log_data_mock.log_record = log_record_mock
        data = _TraceData(
            message="body",
            custom_dimensions={},
        )
        data_mock._from_log_record.return_value = data
        qpm = _QuickpulseManager()
        qpm.initialize(
            connection_string=self.connection_string,
            resource=self.resource,
        )
        qpm._record_log_record(log_data_mock)
        data_mock._from_log_record.assert_called_once_with(log_record_mock)
        metric_derive_mock.assert_called_once_with(data)
        doc_mock.assert_called_once_with(data, None)

        # Cleanup
        qpm.shutdown()

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._create_projections")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._check_metric_filters")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._get_quickpulse_derived_metric_infos")
    def test_derive_metrics_from_telemetry_data(self, get_derived_mock, filter_mock, projection_mock):
        metric_infos = [mock.Mock()]
        get_derived_mock.return_value = {
            TelemetryType.DEPENDENCY: metric_infos,
        }
        data = _DependencyData(
            duration=0,
            success=True,
            name="test",
            result_code=200,
            target="",
            type="",
            data="",
            custom_dimensions={},
        )
        filter_mock.return_value = True
        _derive_metrics_from_telemetry_data(data)
        get_derived_mock.assert_called_once()
        filter_mock.assert_called_once_with(metric_infos, data)
        projection_mock.assert_called_once_with(metric_infos, data)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._create_projections")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._check_metric_filters")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._get_quickpulse_derived_metric_infos")
    def test_derive_metrics_from_telemetry_data_filter_false(self, get_derived_mock, filter_mock, projection_mock):
        metric_infos = [mock.Mock()]
        get_derived_mock.return_value = {
            TelemetryType.DEPENDENCY: metric_infos,
        }
        data = _DependencyData(
            duration=0,
            success=True,
            name="test",
            result_code=200,
            target="",
            type="",
            data="",
            custom_dimensions={},
        )
        filter_mock.return_value = False
        _derive_metrics_from_telemetry_data(data)
        get_derived_mock.assert_called_once()
        filter_mock.assert_called_once_with(metric_infos, data)
        projection_mock.assert_not_called()

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._append_quickpulse_document")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._get_span_document")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._check_filters")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._get_quickpulse_doc_stream_infos")
    def test_apply_doc_filters_from_telemetry_data(
        self,
        get_doc_stream_mock,
        filter_mock,
        get_span_mock,
        append_mock,
    ):
        filter_group_mock = mock.Mock()
        doc_infos_inner = {"streamId": [filter_group_mock]}
        get_doc_stream_mock.return_value = {
            TelemetryType.DEPENDENCY: doc_infos_inner,
        }
        data = _DependencyData(
            duration=0,
            success=True,
            name="test",
            result_code=200,
            target="",
            type="",
            data="",
            custom_dimensions={},
        )
        filter_mock.return_value = True
        doc_mock = mock.Mock()
        get_span_mock.return_value = doc_mock
        _apply_document_filters_from_telemetry_data(data)
        get_doc_stream_mock.assert_called_once()
        filter_mock.assert_called_once_with(filter_group_mock.filters, data)
        get_span_mock.assert_called_once_with(data)
        self.assertEqual(doc_mock.document_stream_ids, ["streamId"])
        append_mock.assert_called_once_with(doc_mock)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._append_quickpulse_document")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._get_span_document")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._check_filters")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._get_quickpulse_doc_stream_infos")
    def test_apply_doc_filters_from_telemetry_data_all_streams(
        self,
        get_doc_stream_mock,
        filter_mock,
        get_span_mock,
        append_mock,
    ):
        get_doc_stream_mock.return_value = {
            TelemetryType.DEPENDENCY: {},
        }
        data = _DependencyData(
            duration=0,
            success=True,
            name="test",
            result_code=200,
            target="",
            type="",
            data="",
            custom_dimensions={},
        )
        filter_mock.return_value = False
        doc_mock = mock.Mock()
        doc_mock.document_stream_ids = None
        get_span_mock.return_value = doc_mock
        _apply_document_filters_from_telemetry_data(data)
        get_doc_stream_mock.assert_called_once()
        filter_mock.assert_not_called()
        get_span_mock.assert_called_once_with(data)
        self.assertIsNone(doc_mock.document_stream_ids)
        append_mock.assert_called_once_with(doc_mock)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._append_quickpulse_document")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._get_span_document")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._check_filters")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._get_quickpulse_doc_stream_infos")
    def test_apply_doc_filters_from_telemetry_data_false_filter(
        self,
        get_doc_stream_mock,
        filter_mock,
        get_span_mock,
        append_mock,
    ):
        filter_group_mock = mock.Mock()
        doc_infos_inner = {"streamId": [filter_group_mock]}
        get_doc_stream_mock.return_value = {
            TelemetryType.DEPENDENCY: doc_infos_inner,
        }
        data = _DependencyData(
            duration=0,
            success=True,
            name="test",
            result_code=200,
            target="",
            type="",
            data="",
            custom_dimensions={},
        )
        filter_mock.return_value = False
        doc_mock = mock.Mock()
        doc_mock.document_stream_ids = None
        get_span_mock.return_value = doc_mock
        _apply_document_filters_from_telemetry_data(data)
        get_doc_stream_mock.assert_called_once()
        filter_mock.assert_called_once_with(filter_group_mock.filters, data)
        get_span_mock.assert_not_called()
        self.assertIsNone(doc_mock.document_stream_ids)
        append_mock.assert_not_called()

    def test_validate_recording_resources(self):
        """Test _validate_recording_resources method."""
        qpm = _QuickpulseManager()

        # Before initialization - should return False
        self.assertFalse(qpm._validate_recording_resources())

        # After initialization - should return True
        qpm.initialize(connection_string=self.connection_string, resource=self.resource)
        self.assertTrue(qpm._validate_recording_resources())

        # After shutdown - instruments should be preserved
        qpm.shutdown()
        self.assertTrue(qpm._validate_recording_resources())

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._is_post_state")
    def test_record_span_not_post_state(self, post_state_mock):
        """Test _record_span when not in post state."""
        post_state_mock.return_value = False
        qpm = _QuickpulseManager()
        qpm.initialize(connection_string=self.connection_string, resource=self.resource)

        span_mock = mock.Mock()

        # Mock the metric instruments to verify they're not called
        qpm._request_rate_counter = mock.Mock()
        qpm._request_duration = mock.Mock()

        qpm._record_span(span_mock)

        # Verify no metrics were recorded
        qpm._request_rate_counter.add.assert_not_called()
        qpm._request_duration.record.assert_not_called()

        # Cleanup
        qpm.shutdown()

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._is_post_state")
    def test_record_span_not_initialized(self, post_state_mock):
        """Test _record_span when manager is not initialized."""
        post_state_mock.return_value = True
        qpm = _QuickpulseManager()

        span_mock = mock.Mock()

        # Should not crash and should not record anything
        qpm._record_span(span_mock)

        # Verify manager is still not initialized
        self.assertFalse(qpm.is_initialized())

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._logger")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._apply_document_filters_from_telemetry_data")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._derive_metrics_from_telemetry_data")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._TelemetryData")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._is_post_state")
    def test_record_span_exception_handling(
        self, post_state_mock, data_mock, metric_derive_mock, doc_mock, logger_mock
    ):
        """Test _record_span exception handling."""
        post_state_mock.return_value = True
        span_mock = mock.Mock()
        span_mock.end_time = 10
        span_mock.start_time = 5
        span_mock.status.is_ok = True
        span_mock.kind = SpanKind.SERVER
        span_mock.events = []

        # Make _TelemetryData._from_span raise an exception
        data_mock._from_span.side_effect = Exception("Test exception")

        qpm = _QuickpulseManager()
        qpm.initialize(connection_string=self.connection_string, resource=self.resource)

        # Should not crash when exception occurs
        qpm._record_span(span_mock)

        # Verify exception was logged
        logger_mock.exception.assert_called_once()

        # Cleanup
        qpm.shutdown()

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._is_post_state")
    def test_record_log_record_not_post_state(self, post_state_mock):
        """Test _record_log_record when not in post state."""
        post_state_mock.return_value = False
        qpm = _QuickpulseManager()
        qpm.initialize(connection_string=self.connection_string, resource=self.resource)

        log_data_mock = mock.Mock()

        # Mock the metric instruments to verify they're not called
        qpm._exception_rate_counter = mock.Mock()

        qpm._record_log_record(log_data_mock)

        # Verify no metrics were recorded
        qpm._exception_rate_counter.add.assert_not_called()

        # Cleanup
        qpm.shutdown()

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._is_post_state")
    def test_record_log_record_not_initialized(self, post_state_mock):
        """Test _record_log_record when manager is not initialized."""
        post_state_mock.return_value = True
        qpm = _QuickpulseManager()

        log_data_mock = mock.Mock()

        # Should not crash and should not record anything
        qpm._record_log_record(log_data_mock)

        # Verify manager is still not initialized
        self.assertFalse(qpm.is_initialized())

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._logger")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._apply_document_filters_from_telemetry_data")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._derive_metrics_from_telemetry_data")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._TelemetryData")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._is_post_state")
    def test_record_log_record_exception_handling(
        self, post_state_mock, data_mock, metric_derive_mock, doc_mock, logger_mock
    ):
        """Test _record_log_record exception handling."""
        post_state_mock.return_value = True
        log_record_mock = mock.Mock()
        log_data_mock = mock.Mock()
        log_data_mock.log_record = log_record_mock

        # Make _TelemetryData._from_log_record raise an exception
        data_mock._from_log_record.side_effect = Exception("Test exception")

        qpm = _QuickpulseManager()
        qpm.initialize(connection_string=self.connection_string, resource=self.resource)

        # Should not crash when exception occurs
        qpm._record_log_record(log_data_mock)

        # Verify exception was logged
        logger_mock.exception.assert_called_once()

        # Cleanup
        qpm.shutdown()

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._apply_document_filters_from_telemetry_data")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._derive_metrics_from_telemetry_data")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._TelemetryData")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._is_post_state")
    def test_record_log_record_no_log_record(self, post_state_mock, data_mock, metric_derive_mock, doc_mock):
        """Test _record_log_record when readable_log_record.log_record is None."""
        post_state_mock.return_value = True
        log_data_mock = mock.Mock()
        log_data_mock.log_record = None

        qpm = _QuickpulseManager()
        qpm.initialize(connection_string=self.connection_string, resource=self.resource)

        # Should not crash and should not process anything
        qpm._record_log_record(log_data_mock)

        # Verify no telemetry data processing occurred
        data_mock._from_log_record.assert_not_called()
        metric_derive_mock.assert_not_called()
        doc_mock.assert_not_called()

        # Cleanup
        qpm.shutdown()

    def test_create_metric_instruments_no_meter(self):
        """Test _create_metric_instruments when meter is None."""
        qpm = _QuickpulseManager()

        # Should raise ValueError when meter is not set
        with self.assertRaises(ValueError) as context:
            qpm._create_metric_instruments()

        self.assertIn("Meter must be initialized", str(context.exception))

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._get_quickpulse_derived_metric_infos")
    def test_derive_metrics_no_config(self, get_derived_mock):
        """Test _derive_metrics_from_telemetry_data when no filtering is configured."""
        get_derived_mock.return_value = {}

        data = _DependencyData(
            duration=0,
            success=True,
            name="test",
            result_code=200,
            target="",
            type="",
            data="",
            custom_dimensions={},
        )

        # Should return early without processing
        _derive_metrics_from_telemetry_data(data)
        get_derived_mock.assert_called_once()

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._manager._get_quickpulse_derived_metric_infos")
    def test_derive_metrics_unknown_data_type(self, get_derived_mock):
        """Test _derive_metrics_from_telemetry_data with unknown data type."""
        get_derived_mock.return_value = {TelemetryType.DEPENDENCY: [mock.Mock()]}
