# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from datetime import datetime
import unittest
from unittest import mock

from opentelemetry.sdk.metrics.export import HistogramDataPoint, NumberDataPoint
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import SpanKind

from azure.monitor.opentelemetry.exporter._quickpulse._constants import (
    _COMMITTED_BYTES_NAME,
    _DocumentIngressDocumentType,
)
from azure.monitor.opentelemetry.exporter._quickpulse._generated.models._models import (
    Exception,
    MetricPoint,
    MonitoringDataPoint,
    RemoteDependency,
    Request,
    Trace,
)
from azure.monitor.opentelemetry.exporter._quickpulse._utils import (
    _get_span_document,
    _get_log_record_document,
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
            [1,1,0],
            [0,10,20],
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
        metric_point = MetricPoint(
            name=_COMMITTED_BYTES_NAME[1],
            weight=1,
            value=5
        )
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
        metric_point = MetricPoint(
            name=_COMMITTED_BYTES_NAME[1],
            weight=1,
            value=7
        )
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

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._ns_to_iso8601_string")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._get_url")
    def test_get_span_document_client(self, url_mock, iso_mock):
        span_mock = mock.Mock()
        span_mock.name = "test_span"
        span_mock.end_time = 10
        span_mock.start_time = 4
        span_mock.attributes = {
            SpanAttributes.HTTP_STATUS_CODE: "200",
            SpanAttributes.RPC_GRPC_STATUS_CODE: "400",
        }
        span_mock.kind = SpanKind.CLIENT
        url_mock.return_value = "test_url"
        iso_mock.return_value = "1000"
        doc = _get_span_document(span_mock)
        self.assertTrue(isinstance(doc, RemoteDependency))
        self.assertEqual(doc.document_type, _DocumentIngressDocumentType.RemoteDependency.value)
        self.assertEqual(doc.name, "test_span")
        self.assertEqual(doc.command_name, "test_url")
        self.assertEqual(doc.result_code, "200")
        self.assertEqual(doc.duration, "1000")

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._ns_to_iso8601_string")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._get_url")
    def test_get_span_document_server(self, url_mock, iso_mock):
        span_mock = mock.Mock()
        span_mock.name = "test_span"
        span_mock.end_time = 10
        span_mock.start_time = 4
        span_mock.attributes = {
            SpanAttributes.HTTP_STATUS_CODE: "200",
            SpanAttributes.RPC_GRPC_STATUS_CODE: "400",
        }
        span_mock.kind = SpanKind.SERVER
        url_mock.return_value = "test_url"
        iso_mock.return_value = "1000"
        doc = _get_span_document(span_mock)
        self.assertTrue(isinstance(doc, Request))
        self.assertEqual(doc.document_type, _DocumentIngressDocumentType.Request.value)
        self.assertEqual(doc.name, "test_span")
        self.assertEqual(doc.url, "test_url")
        self.assertEqual(doc.response_code, "200")
        self.assertEqual(doc.duration, "1000")

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._ns_to_iso8601_string")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._utils._get_url")
    def test_get_span_document_server_grpc_status(self, url_mock, iso_mock):
        span_mock = mock.Mock()
        span_mock.name = "test_span"
        span_mock.end_time = 10
        span_mock.start_time = 4
        span_mock.attributes = {
            SpanAttributes.RPC_GRPC_STATUS_CODE: "400",
        }
        span_mock.kind = SpanKind.SERVER
        url_mock.return_value = "test_url"
        iso_mock.return_value = "1000"
        doc = _get_span_document(span_mock)
        self.assertTrue(isinstance(doc, Request))
        self.assertEqual(doc.document_type, _DocumentIngressDocumentType.Request.value)
        self.assertEqual(doc.name, "test_span")
        self.assertEqual(doc.url, "test_url")
        self.assertEqual(doc.response_code, "400")
        self.assertEqual(doc.duration, "1000")

    def test_get_log_record_document_server_exc(self):
        log_record = mock.Mock()
        log_record.attributes = {
            SpanAttributes.EXCEPTION_TYPE: "exc_type",
            SpanAttributes.EXCEPTION_MESSAGE: "exc_message",
        }
        log_data = mock.Mock()
        log_data.log_record = log_record
        doc = _get_log_record_document(log_data)
        self.assertTrue(isinstance(doc, Exception))
        self.assertEqual(doc.document_type, _DocumentIngressDocumentType.Exception.value)
        self.assertEqual(doc.exception_type, "exc_type")
        self.assertEqual(doc.exception_message, "exc_message")

    def test_get_log_record_document_server_exc(self):
        log_record = mock.Mock()
        log_record.attributes = {}
        log_record.body = "body"
        log_data = mock.Mock()
        log_data.log_record = log_record
        doc = _get_log_record_document(log_data)
        self.assertTrue(isinstance(doc, Trace))
        self.assertEqual(doc.document_type, _DocumentIngressDocumentType.Trace.value)
        self.assertEqual(doc.message, "body")
