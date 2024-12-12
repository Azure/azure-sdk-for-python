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
from opentelemetry.sdk.resources import Resource, ResourceAttributes
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
from azure.monitor.opentelemetry.exporter._quickpulse._live_metrics import (
    enable_live_metrics,
    _QuickpulseManager,
    _derive_metrics_from_telemetry_data,
)
from azure.monitor.opentelemetry.exporter._quickpulse._state import (
    _get_global_quickpulse_state,
    _set_global_quickpulse_state,
    _QuickpulseState,
)
from azure.monitor.opentelemetry.exporter._quickpulse._types import (
    _DependencyData
)
from azure.monitor.opentelemetry.exporter._utils import (
    _get_sdk_version,
    _populate_part_a_fields,
)


class TestLiveMetrics(unittest.TestCase):

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._QuickpulseManager")
    def test_enable_live_metrics(self, manager_mock):
        mock_resource = mock.Mock()
        enable_live_metrics(
            connection_string="test_cs",
            resource=mock_resource,
        )
        manager_mock.assert_called_with(connection_string="test_cs", resource=mock_resource)


class TestQuickpulseManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _set_global_quickpulse_state(_QuickpulseState.PING_SHORT)

    @classmethod
    def tearDownClass(cls):
        _set_global_quickpulse_state(_QuickpulseState.OFFLINE)

    @mock.patch("opentelemetry.sdk.trace.id_generator.RandomIdGenerator.generate_trace_id")
    def test_init(self, generator_mock):
        generator_mock.return_value = "test_trace_id"
        resource = Resource.create(
            {
                ResourceAttributes.SERVICE_INSTANCE_ID: "test_instance",
                ResourceAttributes.SERVICE_NAME: "test_service",
            }
        )
        part_a_fields = _populate_part_a_fields(resource)
        qpm = _QuickpulseManager(
            connection_string="InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ac;LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/",
            resource=resource,
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
        self.assertEqual(qpm._meter_provider._sdk_config.resource, resource)
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
        resource = Resource.create(
            {
                ResourceAttributes.SERVICE_INSTANCE_ID: "test_instance",
                ResourceAttributes.SERVICE_NAME: "test_service",
            }
        )
        part_a_fields = _populate_part_a_fields(resource)
        resource2 = Resource.create(
            {
                ResourceAttributes.SERVICE_INSTANCE_ID: "test_instance2",
                ResourceAttributes.SERVICE_NAME: "test_service2",
            }
        )
        qpm = _QuickpulseManager(
            connection_string="InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ac;LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/",
            resource=resource,
        )
        qpm2 = _QuickpulseManager(
            connection_string="InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ac;LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/",
            resource=resource2,
        )
        self.assertEqual(qpm, qpm2)
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

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._append_quickpulse_document")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._get_span_document")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._is_post_state")
    def test_record_span_server_success(self, post_state_mock, span_doc_mock, append_doc_mock):
        post_state_mock.return_value = True
        span_doc = mock.Mock()
        span_doc_mock.return_value = span_doc
        span_mock = mock.Mock()
        span_mock.end_time = 10
        span_mock.start_time = 5
        span_mock.status.is_ok = True
        span_mock.kind = SpanKind.SERVER
        qpm = _QuickpulseManager(
            connection_string="InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ac;LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/",
            resource=Resource.create(),
        )
        qpm._request_rate_counter = mock.Mock()
        qpm._request_duration = mock.Mock()
        qpm._record_span(span_mock)
        append_doc_mock.assert_called_once_with(span_doc)
        qpm._request_rate_counter.add.assert_called_once_with(1)
        qpm._request_duration.record.assert_called_once_with(5 / 1e9)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._append_quickpulse_document")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._get_span_document")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._is_post_state")
    def test_record_span_server_failure(self, post_state_mock, span_doc_mock, append_doc_mock):
        post_state_mock.return_value = True
        span_doc = mock.Mock()
        span_doc_mock.return_value = span_doc
        span_mock = mock.Mock()
        span_mock.end_time = 10
        span_mock.start_time = 5
        span_mock.status.is_ok = False
        span_mock.kind = SpanKind.SERVER
        qpm = _QuickpulseManager(
            connection_string="InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ac;LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/",
            resource=Resource.create(),
        )
        qpm._request_failed_rate_counter = mock.Mock()
        qpm._request_duration = mock.Mock()
        qpm._record_span(span_mock)
        append_doc_mock.assert_called_once_with(span_doc)
        qpm._request_failed_rate_counter.add.assert_called_once_with(1)
        qpm._request_duration.record.assert_called_once_with(5 / 1e9)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._append_quickpulse_document")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._get_span_document")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._is_post_state")
    def test_record_span_dep_success(self, post_state_mock, span_doc_mock, append_doc_mock):
        post_state_mock.return_value = True
        span_doc = mock.Mock()
        span_doc_mock.return_value = span_doc
        span_mock = mock.Mock()
        span_mock.end_time = 10
        span_mock.start_time = 5
        span_mock.status.is_ok = True
        span_mock.kind = SpanKind.CLIENT
        qpm = _QuickpulseManager(
            connection_string="InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ac;LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/",
            resource=Resource.create(),
        )
        qpm._dependency_rate_counter = mock.Mock()
        qpm._dependency_duration = mock.Mock()
        qpm._record_span(span_mock)
        append_doc_mock.assert_called_once_with(span_doc)
        qpm._dependency_rate_counter.add.assert_called_once_with(1)
        qpm._dependency_duration.record.assert_called_once_with(5 / 1e9)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._append_quickpulse_document")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._get_span_document")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._is_post_state")
    def test_record_span_dep_failure(self, post_state_mock, span_doc_mock, append_doc_mock):
        post_state_mock.return_value = True
        span_doc = mock.Mock()
        span_doc_mock.return_value = span_doc
        span_mock = mock.Mock()
        span_mock.end_time = 10
        span_mock.start_time = 5
        span_mock.status.is_ok = False
        span_mock.kind = SpanKind.CLIENT
        qpm = _QuickpulseManager(
            connection_string="InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ac;LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/",
            resource=Resource.create(),
        )
        qpm._dependency_failure_rate_counter = mock.Mock()
        qpm._dependency_duration = mock.Mock()
        qpm._record_span(span_mock)
        span_doc_mock.assert_called_once_with(span_mock)
        append_doc_mock.assert_called_once_with(span_doc)
        qpm._dependency_failure_rate_counter.add.assert_called_once_with(1)
        qpm._dependency_duration.record.assert_called_once_with(5 / 1e9)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._derive_metrics_from_telemetry_data")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._TelemetryData")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._get_quickpulse_derived_metric_infos")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._append_quickpulse_document")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._get_span_document")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._is_post_state")
    def test_record_span_derive_filter_metrics(
        self, post_state_mock, span_doc_mock, append_doc_mock, info_mock, data_mock, derive_mock
    ):
        post_state_mock.return_value = True
        span_doc = mock.Mock()
        span_doc_mock.return_value = span_doc
        span_mock = mock.Mock()
        span_mock.end_time = 10
        span_mock.start_time = 5
        qpm = _QuickpulseManager(
            connection_string="InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ac;LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/",
            resource=Resource.create(),
        )
        info_mock.return_value = {"test": "value"}
        data = mock.Mock()
        data_mock._from_span.return_value = data
        qpm._record_span(span_mock)
        info_mock.assert_called_once()
        data_mock._from_span.assert_called_once_with(span_mock)
        derive_mock.assert_called_once_with(data)
        span_doc_mock.assert_called_once_with(span_mock)
        append_doc_mock.assert_called_once_with(span_doc)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._append_quickpulse_document")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._get_log_record_document")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._is_post_state")
    def test_record_log_exception(self, post_state_mock, log_doc_mock, append_doc_mock):
        post_state_mock.return_value = True
        log_record_doc = mock.Mock()
        log_doc_mock.return_value = log_record_doc
        log_data_mock = mock.Mock()
        attributes = {
            SpanAttributes.EXCEPTION_TYPE: "exc_type",
            SpanAttributes.EXCEPTION_MESSAGE: "exc_msg",
        }
        log_data_mock.log_record.attributes = attributes
        qpm = _QuickpulseManager(
            connection_string="InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ac;LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/",
            resource=Resource.create(),
        )
        qpm._exception_rate_counter = mock.Mock()
        qpm._record_log_record(log_data_mock)
        log_doc_mock.assert_called_once_with(log_data_mock)
        append_doc_mock.assert_called_once_with(log_record_doc)
        qpm._exception_rate_counter.add.assert_called_once_with(1)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._derive_metrics_from_telemetry_data")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._TelemetryData")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._get_quickpulse_derived_metric_infos")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._append_quickpulse_document")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._get_log_record_document")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._is_post_state")
    def test_record_log_derive_filter_metrics(
        self, post_state_mock, log_doc_mock, append_doc_mock, info_mock, data_mock, derive_mock
    ):
        post_state_mock.return_value = True
        log_record_doc = mock.Mock()
        log_record_mock = mock.Mock()
        log_doc_mock.return_value = log_record_doc
        log_data_mock = mock.Mock()
        log_data_mock.log_record = log_record_mock
        qpm = _QuickpulseManager(
            connection_string="InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ac;LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/",
            resource=Resource.create(),
        )
        info_mock.return_value = {"test": "value"}
        data = mock.Mock()
        data_mock._from_log_record.return_value = data
        qpm._record_log_record(log_data_mock)
        info_mock.assert_called_once()
        data_mock._from_log_record.assert_called_once_with(log_record_mock)
        derive_mock.assert_called_once_with(data)
        log_doc_mock.assert_called_once_with(log_data_mock)
        append_doc_mock.assert_called_once_with(log_record_doc)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._create_projections")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._check_metric_filters")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._get_quickpulse_derived_metric_infos")
    def test_derive_metrics_from_telemetry_data(self, get_derived_mock, filter_mock, projection_mock):
        metric_infos = [mock.Mock]
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

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._create_projections")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._check_metric_filters")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._get_quickpulse_derived_metric_infos")
    def test_derive_metrics_from_telemetry_data_filter_false(self, get_derived_mock, filter_mock, projection_mock):
        metric_infos = [mock.Mock]
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

# cSpell:enable
