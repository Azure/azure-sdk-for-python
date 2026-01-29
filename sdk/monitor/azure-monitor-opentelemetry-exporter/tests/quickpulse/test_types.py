# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

# cSpell:disable

import unittest
from unittest.mock import patch, Mock

from opentelemetry._logs import LogRecord
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.semconv._incubating.attributes import gen_ai_attributes
from opentelemetry.semconv.attributes.http_attributes import (
    HTTP_REQUEST_METHOD,
    HTTP_RESPONSE_STATUS_CODE,
)
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import SpanKind

from azure.monitor.opentelemetry.exporter._quickpulse._types import (
    _DependencyData,
    _ExceptionData,
    _RequestData,
    _TelemetryData,
)


# pylint: disable=protected-access
class TestTelemetryData(unittest.TestCase):
    @patch("azure.monitor.opentelemetry.exporter._quickpulse._types._RequestData")
    def test_from_span_server_kind_server(self, fn_mock):
        span = Mock()
        span.kind = SpanKind.SERVER
        data_mock = Mock()
        fn_mock._from_span.return_value = data_mock
        result = _TelemetryData._from_span(span)
        self.assertEqual(result, data_mock)
        fn_mock._from_span.assert_called_once_with(span)

    @patch("azure.monitor.opentelemetry.exporter._quickpulse._types._RequestData")
    def test_from_span_consumer_kind_(self, fn_mock):
        span = Mock()
        span.kind = SpanKind.CONSUMER
        data_mock = Mock()
        fn_mock._from_span.return_value = data_mock
        result = _TelemetryData._from_span(span)
        self.assertEqual(result, data_mock)
        fn_mock._from_span.assert_called_once_with(span)

    @patch("azure.monitor.opentelemetry.exporter._quickpulse._types._DependencyData")
    def test_from_span_dependency_kind(self, fn_mock):
        span = Mock()
        span.kind = SpanKind.CLIENT
        data_mock = Mock()
        fn_mock._from_span.return_value = data_mock
        result = _TelemetryData._from_span(span)
        self.assertEqual(result, data_mock)
        fn_mock._from_span.assert_called_once_with(span)

    @patch("azure.monitor.opentelemetry.exporter._quickpulse._types._ExceptionData")
    def test_from_log_record_with_exception(self, fn_mock):
        log_record = Mock()
        log_record.attributes = {
            SpanAttributes.EXCEPTION_TYPE: "SomeException",
            SpanAttributes.EXCEPTION_MESSAGE: "An error occurred",
        }
        data_mock = Mock()
        fn_mock._from_log_record.return_value = data_mock
        result = _TelemetryData._from_log_record(log_record)
        self.assertEqual(result, data_mock)
        fn_mock._from_log_record.assert_called_once_with(log_record)

    @patch("azure.monitor.opentelemetry.exporter._quickpulse._types._TraceData")
    def test_from_log_record_without_exception(self, fn_mock):
        log_record = Mock()
        log_record.attributes = {}
        data_mock = Mock()
        fn_mock._from_log_record.return_value = data_mock
        result = _TelemetryData._from_log_record(log_record)
        self.assertEqual(result, data_mock)
        fn_mock._from_log_record.assert_called_once_with(log_record)


class TestRequestData(unittest.TestCase):
    @patch("azure.monitor.opentelemetry.exporter.export.trace._utils._get_url_for_http_request")
    def test_from_span_with_valid_data(self, utils_mock):
        span = Mock(spec=ReadableSpan)
        span.end_time = 2000000000
        span.start_time = 1000000000
        span.name = "test_span"
        span.status.is_ok = True
        span.attributes = {SpanAttributes.HTTP_STATUS_CODE: 200, "custom_attribute": "value"}
        utils_mock.return_value = "http://example.com"

        result = _RequestData._from_span(span)

        self.assertEqual(result.duration, 1.0)
        self.assertTrue(result.success)
        self.assertEqual(result.name, "test_span")
        self.assertEqual(result.response_code, 200)
        self.assertEqual(result.url, "http://example.com")
        self.assertEqual(result.custom_dimensions, span.attributes)

    @patch("azure.monitor.opentelemetry.exporter.export.trace._utils._get_url_for_http_request")
    def test_from_span_with_error_status_code(self, utils_mock):
        span = Mock(spec=ReadableSpan)
        span.end_time = 2000000000
        span.start_time = 1000000000
        span.name = "test_span"
        span.status.is_ok = True
        span.attributes = {SpanAttributes.HTTP_STATUS_CODE: 404, "custom_attribute": "value"}
        utils_mock.return_value = "http://example.com"

        result = _RequestData._from_span(span)

        self.assertEqual(result.duration, 1.0)
        self.assertFalse(result.success)
        self.assertEqual(result.name, "test_span")
        self.assertEqual(result.response_code, 404)
        self.assertEqual(result.url, "http://example.com")
        self.assertEqual(result.custom_dimensions, span.attributes)

    @patch("azure.monitor.opentelemetry.exporter.export.trace._utils._get_url_for_http_request")
    def test_from_span_http_stable_semconv(self, utils_mock):
        span = Mock(spec=ReadableSpan)
        span.end_time = 2000000000
        span.start_time = 1000000000
        span.name = "test_span"
        span.status.is_ok = True
        span.attributes = {HTTP_RESPONSE_STATUS_CODE: 200, "custom_attribute": "value"}
        utils_mock.return_value = "http://example.com"

        result = _RequestData._from_span(span)

        self.assertEqual(result.duration, 1.0)
        self.assertTrue(result.success)
        self.assertEqual(result.name, "test_span")
        self.assertEqual(result.response_code, 200)
        self.assertEqual(result.url, "http://example.com")
        self.assertEqual(result.custom_dimensions, span.attributes)


class TestDependencyData(unittest.TestCase):
    def setUp(self):
        self.span = Mock(spec=ReadableSpan)
        self.span.end_time = 2000000000
        self.span.start_time = 1000000000
        self.span.attributes = {}
        self.span.status.is_ok = True
        self.span.name = "test_span"
        self.span.kind = SpanKind.INTERNAL

    def test_inproc_dependency(self):
        self.span.kind = SpanKind.INTERNAL
        result = _DependencyData._from_span(self.span)
        self.assertEqual(result.duration, 1.0)
        self.assertEqual(result.success, True)
        self.assertEqual(result.name, "test_span")
        self.assertEqual(result.result_code, 0)
        self.assertEqual(result.target, "")
        self.assertEqual(result.type, "InProc")
        self.assertEqual(result.data, "")
        self.assertEqual(result.custom_dimensions, {})

    def test_http_dependency(self):
        self.span.kind = SpanKind.CLIENT
        self.span.attributes = {SpanAttributes.HTTP_METHOD: "GET", SpanAttributes.HTTP_URL: "http://example.com"}
        result = _DependencyData._from_span(self.span)
        self.assertEqual(result.type, "HTTP")
        self.assertEqual(result.data, "http://example.com")
        self.assertEqual(result.target, "example.com")

    def test_http_dependency_stable_semconv(self):
        self.span.kind = SpanKind.CLIENT
        self.span.attributes = {HTTP_REQUEST_METHOD: "GET", SpanAttributes.HTTP_URL: "http://example.com"}
        result = _DependencyData._from_span(self.span)
        self.assertEqual(result.type, "HTTP")
        self.assertEqual(result.data, "http://example.com")
        self.assertEqual(result.target, "example.com")

    def test_db_dependency(self):
        self.span.kind = SpanKind.CLIENT
        self.span.attributes = {SpanAttributes.DB_SYSTEM: "mysql", SpanAttributes.DB_STATEMENT: "SELECT * FROM table"}
        result = _DependencyData._from_span(self.span)
        self.assertEqual(result.type, "mysql")
        self.assertEqual(result.data, "SELECT * FROM table")
        self.assertEqual(result.target, "mysql")

    def test_messaging_dependency(self):
        self.span.kind = SpanKind.CLIENT
        self.span.attributes = {SpanAttributes.MESSAGING_SYSTEM: "kafka"}
        result = _DependencyData._from_span(self.span)
        self.assertEqual(result.type, "kafka")
        self.assertEqual(result.target, "kafka")

    def test_rpc_dependency(self):
        self.span.kind = SpanKind.CLIENT
        self.span.attributes = {SpanAttributes.RPC_SYSTEM: "grpc"}
        result = _DependencyData._from_span(self.span)
        self.assertEqual(result.type, "grpc")
        self.assertEqual(result.target, "grpc")

    def test_genai_dependency(self):
        self.span.kind = SpanKind.CLIENT
        self.span.attributes = {gen_ai_attributes.GEN_AI_SYSTEM: "genai"}
        result = _DependencyData._from_span(self.span)
        self.assertEqual(result.type, "genai")

    def test_producer_dependency(self):
        self.span.kind = SpanKind.PRODUCER
        self.span.attributes = {SpanAttributes.MESSAGING_SYSTEM: "kafka"}
        result = _DependencyData._from_span(self.span)
        self.assertEqual(result.type, "Queue Message | kafka")


class TestExceptionData(unittest.TestCase):
    def setUp(self):
        self.log_record = Mock(spec=LogRecord)
        self.log_record.attributes = {
            SpanAttributes.EXCEPTION_MESSAGE: "Test exception message",
            SpanAttributes.EXCEPTION_STACKTRACE: "Test stack trace",
        }

        self.span_event = Mock(spec=LogRecord)
        self.span_event.attributes = {
            SpanAttributes.EXCEPTION_MESSAGE: "Test span event message",
            SpanAttributes.EXCEPTION_STACKTRACE: "Test span event stack trace",
        }

    def test_from_log_record(self):
        result = _ExceptionData._from_log_record(self.log_record)
        self.assertEqual(result.message, "Test exception message")
        self.assertEqual(result.stack_trace, "Test stack trace")
        self.assertEqual(result.custom_dimensions, self.log_record.attributes)

    def test_from_log_record_empty_attributes(self):
        self.log_record.attributes = {}
        result = _ExceptionData._from_log_record(self.log_record)
        self.assertEqual(result.message, "")
        self.assertEqual(result.stack_trace, "")
        self.assertEqual(result.custom_dimensions, self.log_record.attributes)

    def test_from_span_event(self):
        result = _ExceptionData._from_span_event(self.span_event)
        self.assertEqual(result.message, "Test span event message")
        self.assertEqual(result.stack_trace, "Test span event stack trace")
        self.assertEqual(result.custom_dimensions, self.span_event.attributes)

    def test_from_span_event_empty_attributes(self):
        self.span_event.attributes = {}
        result = _ExceptionData._from_span_event(self.span_event)
        self.assertEqual(result.message, "")
        self.assertEqual(result.stack_trace, "")
        self.assertEqual(result.custom_dimensions, self.span_event.attributes)


# cSpell:enable
