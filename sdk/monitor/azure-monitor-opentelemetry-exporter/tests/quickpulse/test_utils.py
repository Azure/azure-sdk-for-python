# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from datetime import datetime
import unittest
from unittest import mock

from opentelemetry.sdk.metrics.export import HistogramDataPoint, NumberDataPoint

from azure.monitor.opentelemetry.exporter._quickpulse._constants import (
    _COMMITTED_BYTES_NAME,
)
from azure.monitor.opentelemetry.exporter._quickpulse._generated.models import (
    AggregationType,
    DocumentType,
    Exception,
    MetricPoint,
    MonitoringDataPoint,
    RemoteDependency,
    Request,
    Trace,
)
from azure.monitor.opentelemetry.exporter._quickpulse._types import (
    _DependencyData,
    _ExceptionData,
    _RequestData,
    _TraceData,
)
from azure.monitor.opentelemetry.exporter._quickpulse._utils import (
    _get_metrics_from_projections,
    _get_span_document,
    _get_log_record_document,
    _filter_time_stamp_to_ms,
    _metric_to_quick_pulse_data_points,
)


class TestUtils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_mdp = MonitoringDataPoint(
            version=1.0,
            invariant_version=1,
            instance="test_instance",
            role_name="test_role_name",
            machine_name="test_machine_name",
            stream_id="test_stream_id",
            is_web_app=False,
            performance_collection_supported=True,
        )

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils.datetime")
    def test_metric_to_qp_data_point_hist(self, datetime_mock):
        point = HistogramDataPoint(
            {},
            0,
            0,
            2,
            10,
            [1, 1, 0],
            [0, 10, 20],
            0,
            5,
        )
        metric = mock.Mock()
        metric.name = _COMMITTED_BYTES_NAME[0]
        metric.data.data_points = [point]
        scope_metric = mock.Mock()
        scope_metric.metrics = [metric]
        resource_metric = mock.Mock()
        resource_metric.scope_metrics = [scope_metric]
        metric_data = mock.Mock()
        metric_data.resource_metrics = [resource_metric]
        metric_point = MetricPoint(name=_COMMITTED_BYTES_NAME[1], weight=1, value=5)
        documents = [mock.Mock()]
        date_now = datetime.now()
        datetime_mock.now.return_value = date_now
        mdp = _metric_to_quick_pulse_data_points(metric_data, self.base_mdp, documents)[0]
        self.assertEqual(mdp.version, self.base_mdp.version)
        self.assertEqual(mdp.instance, self.base_mdp.instance)
        self.assertEqual(mdp.role_name, self.base_mdp.role_name)
        self.assertEqual(mdp.machine_name, self.base_mdp.machine_name)
        self.assertEqual(mdp.stream_id, self.base_mdp.stream_id)
        self.assertEqual(mdp.timestamp, date_now)
        self.assertEqual(mdp.metrics, [metric_point])
        self.assertEqual(mdp.documents, documents)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils.datetime")
    def test_metric_to_qp_data_point_num(self, datetime_mock):
        point = NumberDataPoint(
            {},
            0,
            0,
            7,
        )
        metric = mock.Mock()
        metric.name = _COMMITTED_BYTES_NAME[0]
        metric.data.data_points = [point]
        scope_metric = mock.Mock()
        scope_metric.metrics = [metric]
        resource_metric = mock.Mock()
        resource_metric.scope_metrics = [scope_metric]
        metric_data = mock.Mock()
        metric_data.resource_metrics = [resource_metric]
        metric_point = MetricPoint(name=_COMMITTED_BYTES_NAME[1], weight=1, value=7)
        documents = [mock.Mock()]
        date_now = datetime.now()
        datetime_mock.now.return_value = date_now
        mdp = _metric_to_quick_pulse_data_points(metric_data, self.base_mdp, documents)[0]
        self.assertEqual(mdp.version, self.base_mdp.version)
        self.assertEqual(mdp.instance, self.base_mdp.instance)
        self.assertEqual(mdp.role_name, self.base_mdp.role_name)
        self.assertEqual(mdp.machine_name, self.base_mdp.machine_name)
        self.assertEqual(mdp.stream_id, self.base_mdp.stream_id)
        self.assertEqual(mdp.timestamp, date_now)
        self.assertEqual(mdp.metrics, [metric_point])
        self.assertEqual(mdp.documents, documents)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._get_metrics_from_projections")
    def test_metric_to_qp_data_point_process_filtered_metrics(self, projection_mock):
        metric_data = mock.Mock()
        metric_data.resource_metrics = []
        projections = [("ID:1234", 5.0)]
        projection_mock.return_value = projections
        mdp = _metric_to_quick_pulse_data_points(metric_data, self.base_mdp, [])[0]
        self.assertEqual(mdp.metrics[0].name, "ID:1234")
        self.assertEqual(mdp.metrics[0].value, 5.0)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._ms_to_iso8601_string")
    def test_get_span_document_client(self, iso_mock):
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
        iso_mock.return_value = "1000"
        doc = _get_span_document(data)
        self.assertTrue(isinstance(doc, RemoteDependency))
        self.assertEqual(doc.document_type, DocumentType.REMOTE_DEPENDENCY)
        self.assertEqual(doc.name, "test_dep")
        self.assertEqual(doc.command_name, "test_data")
        self.assertEqual(doc.result_code, "200")
        self.assertEqual(doc.duration, "1000")

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._ms_to_iso8601_string")
    def test_get_span_document_server(self, iso_mock):
        data = _RequestData(
            custom_dimensions={},
            duration=1000,
            success=True,
            name="test_req",
            response_code=400,
            url="test_url",
        )
        iso_mock.return_value = "1000"
        doc = _get_span_document(data)
        self.assertTrue(isinstance(doc, Request))
        self.assertEqual(doc.document_type, DocumentType.REQUEST)
        self.assertEqual(doc.name, "test_req")
        self.assertEqual(doc.url, "test_url")
        self.assertEqual(doc.response_code, "400")
        self.assertEqual(doc.duration, "1000")

    def test_get_log_record_document_exc(self):
        data = _ExceptionData(
            message="exc_message",
            stack_trace="",
            custom_dimensions={},
        )
        doc = _get_log_record_document(data, exc_type="exc_type")
        self.assertTrue(isinstance(doc, Exception))
        self.assertEqual(doc.document_type, DocumentType.EXCEPTION)
        self.assertEqual(doc.exception_type, "exc_type")
        self.assertEqual(doc.exception_message, "exc_message")

    def test_get_log_record_document_trace(self):
        data = _TraceData(
            message="body",
            custom_dimensions={},
        )
        doc = _get_log_record_document(data)
        self.assertTrue(isinstance(doc, Trace))
        self.assertEqual(doc.document_type, DocumentType.TRACE)
        self.assertEqual(doc.message, "body")

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._get_quickpulse_projection_map")
    def test_get_metrics_from_projections(self, projection_map_mock):
        projection_map_mock.return_value = {
            "test-id": (AggregationType.MIN, 3.0, 3),
            "test-id2": (AggregationType.MAX, 5.0, 4),
            "test-id3": (AggregationType.SUM, 2.0, 2),
            "test-id4": (AggregationType.AVG, 12.0, 3),
        }
        metric_tuples = _get_metrics_from_projections()
        self.assertEqual(
            metric_tuples,
            [
                ("test-id", 3.0),
                ("test-id2", 5.0),
                ("test-id3", 2.0),
                ("test-id4", 4.0),
            ],
        )

    def test_valid_time_stamp_with_decimal_seconds(self):
        time_stamp = "14.6:56:7.89"
        expected_ms = 1234567890  # Expected milliseconds
        self.assertEqual(_filter_time_stamp_to_ms(time_stamp), expected_ms)

    def test_valid_time_stamp_with_whole_seconds(self):
        time_stamp = "0.0:0:0.2"
        expected_ms = 200  # Expected milliseconds
        self.assertEqual(_filter_time_stamp_to_ms(time_stamp), expected_ms)

    def test_valid_time_stamp_with_no_days(self):
        time_stamp = "0.5:30:15.5"
        expected_ms = 19815500  # 0 days, 5 hours, 30 minutes, 15.5 seconds
        self.assertEqual(_filter_time_stamp_to_ms(time_stamp), expected_ms)

    def test_valid_time_stamp_with_large_days(self):
        time_stamp = "100.0:0:0"
        expected_ms = 8640000000  # 100 days
        self.assertEqual(_filter_time_stamp_to_ms(time_stamp), expected_ms)

    def test_invalid_time_stamp(self):
        time_stamp = "invalid_format"
        self.assertIsNone(_filter_time_stamp_to_ms(time_stamp))

    def test_time_stamp_missing_seconds(self):
        time_stamp = "1.0:0:"
        self.assertIsNone(_filter_time_stamp_to_ms(time_stamp))

    def test_time_stamp_empty_string(self):
        time_stamp = ""
        self.assertIsNone(_filter_time_stamp_to_ms(time_stamp))
