# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.


import json
import os
import platform
import shutil
import unittest
from unittest import mock

# pylint: disable=import-error
from opentelemetry.sdk import trace, resources
from opentelemetry.sdk.trace.export import SpanExportResult
from opentelemetry.trace import Link, SpanContext, SpanKind
from opentelemetry.trace.status import Status, StatusCode

from azure.monitor.opentelemetry.exporter.export._base import ExportResult
from azure.monitor.opentelemetry.exporter.export.trace._exporter import (
    AzureMonitorTraceExporter
)
from azure.monitor.opentelemetry.exporter._utils import azure_monitor_context


def throw(exc_type, *args, **kwargs):
    def func(*_args, **_kwargs):
        raise exc_type(*args, **kwargs)

    return func


# pylint: disable=import-error
# pylint: disable=protected-access
# pylint: disable=too-many-lines
class TestAzureTraceExporter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ.clear()
        os.environ[
            "APPINSIGHTS_INSTRUMENTATIONKEY"
        ] = "1234abcd-5678-4efa-8abc-1234567890ab"
        cls._exporter = AzureMonitorTraceExporter()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._exporter.storage._path, True)

    def test_constructor(self):
        """Test the constructor."""
        exporter = AzureMonitorTraceExporter(
            connection_string="InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab",
        )
        self.assertEqual(
            exporter._instrumentation_key,
            "4321abcd-5678-4efa-8abc-1234567890ab",
        )

    def test_from_connection_string(self):
        exporter = AzureMonitorTraceExporter.from_connection_string(
            "InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab"
        )
        self.assertTrue(isinstance(exporter, AzureMonitorTraceExporter))
        self.assertEqual(
            exporter._instrumentation_key,
            "4321abcd-5678-4efa-8abc-1234567890ab",
        )

    def test_export_empty(self):
        exporter = self._exporter
        result = exporter.export([])
        self.assertEqual(result, SpanExportResult.SUCCESS)

    def test_export_failure(self):
        exporter = self._exporter
        with mock.patch(
            "azure.monitor.opentelemetry.exporter.AzureMonitorTraceExporter._transmit"
        ) as transmit:  # noqa: E501
            test_span = trace._Span(
                name="test",
                context=SpanContext(
                    trace_id=36873507687745823477771305566750195431,
                    span_id=12030755672171557338,
                    is_remote=False,
                ),
            )
            test_span.start()
            test_span.end()
            transmit.return_value = ExportResult.FAILED_RETRYABLE
            storage_mock = mock.Mock()
            exporter.storage.put = storage_mock
            result = exporter.export([test_span])
        self.assertEqual(result, SpanExportResult.FAILURE)
        self.assertEqual(storage_mock.call_count, 1)

    def test_export_success(self):
        exporter = self._exporter
        test_span = trace._Span(
            name="test",
            context=SpanContext(
                trace_id=36873507687745823477771305566750195431,
                span_id=12030755672171557338,
                is_remote=False,
            ),
        )
        test_span.start()
        test_span.end()
        with mock.patch(
            "azure.monitor.opentelemetry.exporter.AzureMonitorTraceExporter._transmit"
        ) as transmit:  # noqa: E501
            transmit.return_value = ExportResult.SUCCESS
            storage_mock = mock.Mock()
            exporter._transmit_from_storage = storage_mock
            result = exporter.export([test_span])
            self.assertEqual(result, SpanExportResult.SUCCESS)
            self.assertEqual(storage_mock.call_count, 1)

    @mock.patch("azure.monitor.opentelemetry.exporter.export.trace._exporter.logger")
    def test_export_exception(self, logger_mock):
        test_span = trace._Span(
            name="test",
            context=SpanContext(
                trace_id=36873507687745823477771305566750195431,
                span_id=12030755672171557338,
                is_remote=False,
            ),
        )
        test_span.start()
        test_span.end()
        exporter = self._exporter
        with mock.patch(
            "azure.monitor.opentelemetry.exporter.AzureMonitorTraceExporter._transmit",
            throw(Exception),
        ):  # noqa: E501
            result = exporter.export([test_span])
            self.assertEqual(result, SpanExportResult.FAILURE)
            self.assertEqual(logger_mock.exception.called, True)

    def test_export_not_retryable(self):
        exporter = self._exporter
        test_span = trace._Span(
            name="test",
            context=SpanContext(
                trace_id=36873507687745823477771305566750195431,
                span_id=12030755672171557338,
                is_remote=False,
            ),
        )
        test_span.start()
        test_span.end()
        with mock.patch(
            "azure.monitor.opentelemetry.exporter.AzureMonitorTraceExporter._transmit"
        ) as transmit:  # noqa: E501
            transmit.return_value = ExportResult.FAILED_NOT_RETRYABLE
            result = exporter.export([test_span])
            self.assertEqual(result, SpanExportResult.FAILURE)

    def test_span_to_envelope_partA(self):
        exporter = self._exporter
        resource = resources.Resource(
            {"service.name": "testServiceName",
             "service.namespace": "testServiceNamespace",
             "service.instance.id": "testServiceInstanceId"})
        context = SpanContext(
                trace_id=36873507687745823477771305566750195431,
                span_id=12030755672171557338,
                is_remote=False,
            )
        test_span = trace._Span(
            name="test",
            context=context,
            resource=resource,
            attributes={"enduser.id":"testId"},
            parent=context,
        )
        test_span.start()
        test_span.end()
        envelope = exporter._span_to_envelope(test_span)

        self.assertEqual(envelope.instrumentation_key,
                         "1234abcd-5678-4efa-8abc-1234567890ab")
        self.assertIsNotNone(envelope.tags)
        self.assertEqual(envelope.tags.get("ai.device.id"), azure_monitor_context["ai.device.id"])
        self.assertEqual(envelope.tags.get("ai.device.locale"), azure_monitor_context["ai.device.locale"])
        self.assertEqual(envelope.tags.get("ai.device.osVersion"), azure_monitor_context["ai.device.osVersion"])
        self.assertEqual(envelope.tags.get("ai.device.type"), azure_monitor_context["ai.device.type"])
        self.assertEqual(envelope.tags.get("ai.internal.sdkVersion"), azure_monitor_context["ai.internal.sdkVersion"])

        self.assertEqual(envelope.tags.get("ai.cloud.role"), "testServiceNamespace.testServiceName")
        self.assertEqual(envelope.tags.get("ai.cloud.roleInstance"), "testServiceInstanceId")
        self.assertEqual(envelope.tags.get("ai.internal.nodeName"), "testServiceInstanceId")
        self.assertEqual(envelope.tags.get("ai.operation.id"), "{:032x}".format(context.trace_id))
        self.assertEqual(envelope.tags.get("ai.user.id"), "testId")
        self.assertEqual(envelope.tags.get("ai.operation.parentId"), "{:016x}".format(context.span_id))

    def test_span_to_envelope_partA_default(self):
        exporter = self._exporter
        resource = resources.Resource(
            {"service.name": "testServiceName"})
        context = SpanContext(
                trace_id=36873507687745823477771305566750195431,
                span_id=12030755672171557338,
                is_remote=False,
            )
        test_span = trace._Span(
            name="test",
            context=context,
            resource=resource,
        )
        test_span.start()
        test_span.end()
        envelope = exporter._span_to_envelope(test_span)
        self.assertEqual(envelope.tags.get("ai.cloud.role"), "testServiceName")
        self.assertEqual(envelope.tags.get("ai.cloud.roleInstance"), platform.node())

    def test_span_to_envelope_client_http(self):
        exporter = self._exporter
        start_time = 1575494316027613500
        end_time = start_time + 1001000000

        # SpanKind.CLIENT HTTP
        span = trace._Span(
            name="test",
            context=SpanContext(
                trace_id=36873507687745823477771305566750195431,
                span_id=12030755672171557337,
                is_remote=False,
            ),
            attributes={
                "http.method": "GET",
                "http.url": "https://www.wikipedia.org/wiki/Rabbit",
                "http.status_code": 200,
                "peer.service": "service",
                "http.user_agent": "agent",
            },
            kind=SpanKind.CLIENT,
        )
        span.start(start_time=start_time)
        span.end(end_time=end_time)
        span._status = Status(status_code=StatusCode.OK)
        envelope = exporter._span_to_envelope(span)
  
        self.assertEqual(
            envelope.name, "Microsoft.ApplicationInsights.RemoteDependency"
        )
        self.assertEqual(envelope.time, "2019-12-04T21:18:36.027613Z")
        self.assertEqual(envelope.data.base_data.name, "GET /wiki/Rabbit")
        self.assertEqual(envelope.data.base_data.id, "a6f5d48acb4d31d9")
        self.assertEqual(envelope.data.base_data.duration, "0.00:00:01.001")
        self.assertTrue(envelope.data.base_data.success)

        self.assertEqual(envelope.data.base_type, "RemoteDependencyData")
        self.assertEqual(envelope.data.base_data.type, "HTTP")
        self.assertEqual(envelope.data.base_data.target, "service")
        self.assertEqual(
            envelope.data.base_data.data,
            "https://www.wikipedia.org/wiki/Rabbit",
        )
        self.assertEqual(envelope.data.base_data.result_code, "200")
        self.assertEqual(envelope.tags["ai.user.userAgent"], "agent")

        # Name empty
        span._attributes = {
            "http.method": "GET",
            "http.scheme": "https",
            "http.url": "https://www.example.com",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.name, "GET /")

        # Target
        span._attributes = {
            "http.method": "GET",
            "http.scheme": "https",
            "http.url": "https://www.example.com:1234",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.target, "www.example.com:1234")

        span._attributes = {
            "http.method": "GET",
            "http.scheme": "http",
            "http.url": "http://www.example.com:80",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.target, "www.example.com")

        span._attributes = {
            "http.method": "GET",
            "http.scheme": "http",
            "http.url": "http://www.example.com:80",
            "http.host": "www.wikipedia.org:1234",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.target, "www.wikipedia.org:1234")

        span._attributes = {
            "http.method": "GET",
            "http.scheme": "https",
            "http.url": "http://www.example.com:80",
            "http.host": "www.wikipedia.org:443",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.target, "www.wikipedia.org")

        # url
        span._attributes = {
            "http.method": "GET",
            "http.scheme": "https",
            "http.host": "www.wikipedia.org",
            "http.target": "/path/12314/?q=ddds#123"
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.data, "https://www.wikipedia.org/path/12314/?q=ddds#123")

        span._attributes = {
            "http.method": "GET",
            "http.scheme": "https",
            "net.peer.port": "8080",
            "net.peer.name": "example.com",
            "http.target": "/path/12314/?q=ddds#123"
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.data, "https://example.com:8080/path/12314/?q=ddds#123")

        span._attributes = {
            "http.method": "GET",
            "http.scheme": "https",
            "net.peer.port": "8080",
            "net.peer.ip": "192.168.0.1",
            "http.target": "/path/12314/?q=ddds#123"
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.data, "https://192.168.0.1:8080/path/12314/?q=ddds#123")

    def test_span_to_envelope_client_db(self):
        exporter = self._exporter
        start_time = 1575494316027613500
        end_time = start_time + 1001000000

        # SpanKind.CLIENT Db
        span = trace._Span(
            name="test",
            context=SpanContext(
                trace_id=36873507687745823477771305566750195431,
                span_id=12030755672171557337,
                is_remote=False,
            ),
            attributes={
                "db.system": "postgresql",
                "peer.service": "service",
                "db.statement": "SELECT * from test",
            },
            kind=SpanKind.CLIENT,
        )
        span.start(start_time=start_time)
        span.end(end_time=end_time)
        span._status = Status(status_code=StatusCode.OK)
        envelope = exporter._span_to_envelope(span)
  
        self.assertEqual(
            envelope.name, "Microsoft.ApplicationInsights.RemoteDependency"
        )
        self.assertEqual(envelope.time, "2019-12-04T21:18:36.027613Z")
        self.assertEqual(envelope.data.base_data.name, "test")
        self.assertEqual(envelope.data.base_data.id, "a6f5d48acb4d31d9")
        self.assertEqual(envelope.data.base_data.duration, "0.00:00:01.001")
        self.assertTrue(envelope.data.base_data.success)

        self.assertEqual(envelope.data.base_type, "RemoteDependencyData")
        self.assertEqual(envelope.data.base_data.type, "postgresql")
        self.assertEqual(envelope.data.base_data.target, "service")
        self.assertEqual(envelope.data.base_data.data, "SELECT * from test")
        self.assertEqual(envelope.data.base_data.result_code, "0")

        # data
        span._attributes = {
            "db.system": "postgresql",
            "peer.service": "service",
            "db.operation": "SELECT",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.data, "SELECT")

        # Target
        span._attributes = {
            "db.system": "postgresql",
            "db.statement": "SELECT",
            "db.name": "testDb",
            "peer.service": "service",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.target, "service|testDb")

        span._attributes = {
            "db.system": "postgresql",
            "db.statement": "SELECT",
            "db.name": "testDb",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.target, "testDb")

        span._attributes = {
            "db.system": "postgresql",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.target, "postgresql")

        # Type
        span._attributes = {
            "db.system": "mssql",
            "db.statement": "SELECT",
            "db.name": "testDb",
            "peer.service": "service",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.type, "SQL")

    def test_span_to_envelope_client_rpc(self):
        exporter = self._exporter
        start_time = 1575494316027613500
        end_time = start_time + 1001000000

        # SpanKind.CLIENT rpc
        span = trace._Span(
            name="test",
            context=SpanContext(
                trace_id=36873507687745823477771305566750195431,
                span_id=12030755672171557337,
                is_remote=False,
            ),
            attributes={
                "peer.service": "service",
                "rpc.system": "rpc",
                "rpc.service": "Test service",
            },
            kind=SpanKind.CLIENT,
        )
        span.start(start_time=start_time)
        span.end(end_time=end_time)
        span._status = Status(status_code=StatusCode.OK)
        envelope = exporter._span_to_envelope(span)
  
        self.assertEqual(
            envelope.name, "Microsoft.ApplicationInsights.RemoteDependency"
        )
        self.assertEqual(envelope.time, "2019-12-04T21:18:36.027613Z")
        self.assertEqual(envelope.data.base_data.name, "test")
        self.assertEqual(envelope.data.base_data.id, "a6f5d48acb4d31d9")
        self.assertEqual(envelope.data.base_data.duration, "0.00:00:01.001")
        self.assertTrue(envelope.data.base_data.success)

        self.assertEqual(envelope.data.base_type, "RemoteDependencyData")
        self.assertEqual(envelope.data.base_data.type, "rpc.system")
        self.assertEqual(envelope.data.base_data.target, "service")
        
        # target
        span._attributes = {
            "rpc.system": "rpc",
            "rpc.service": "Test service",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.target, "rpc")

        # TODO: data.data
        # self.assertEqual(envelope.data.base_data.data, "SELECT")
        self.assertEqual(envelope.data.base_data.result_code, "0")

    def test_span_to_envelope_producer_messaging(self):
        exporter = self._exporter
        start_time = 1575494316027613500
        end_time = start_time + 1001000000

        # SpanKind.PRODUCER messaging
        span = trace._Span(
            name="test",
            context=SpanContext(
                trace_id=36873507687745823477771305566750195431,
                span_id=12030755672171557337,
                is_remote=False,
            ),
            attributes={
                "messaging.system": "messaging",
                "net.peer.ip": "127.0.0.1",
                "messaging.destination": "celery",
            },
            kind=SpanKind.PRODUCER,
        )
        span.start(start_time=start_time)
        span.end(end_time=end_time)
        span._status = Status(status_code=StatusCode.OK)
        envelope = exporter._span_to_envelope(span)
  
        self.assertEqual(
            envelope.name, "Microsoft.ApplicationInsights.RemoteDependency"
        )
        self.assertEqual(envelope.time, "2019-12-04T21:18:36.027613Z")
        self.assertEqual(envelope.data.base_data.name, "test")
        self.assertEqual(envelope.data.base_data.id, "a6f5d48acb4d31d9")
        self.assertEqual(envelope.data.base_data.duration, "0.00:00:01.001")
        self.assertTrue(envelope.data.base_data.success)

        self.assertEqual(envelope.data.base_type, "RemoteDependencyData")
        self.assertEqual(envelope.data.base_data.type, "Queue Message")
        # TODO: data.target
        # self.assertEqual(envelope.data.base_data.target, "rpc")
        # TODO: data.data
        # self.assertEqual(envelope.data.base_data.data, "SELECT")
        self.assertEqual(envelope.data.base_data.result_code, "0")

    def test_span_to_envelope_internal(self):
        exporter = self._exporter
        start_time = 1575494316027613500
        end_time = start_time + 1001000000

        # SpanKind.INTERNAL
        context = SpanContext(
                trace_id=36873507687745823477771305566750195431,
                span_id=12030755672171557337,
                is_remote=False,
            )
        span = trace._Span(
            name="test",
            context=context,
            parent=context,
            attributes={},
            kind=SpanKind.INTERNAL,
        )
        span.start(start_time=start_time)
        span.end(end_time=end_time)
        span._status = Status(status_code=StatusCode.OK)
        envelope = exporter._span_to_envelope(span)
  
        self.assertEqual(
            envelope.name, "Microsoft.ApplicationInsights.RemoteDependency"
        )
        self.assertEqual(envelope.time, "2019-12-04T21:18:36.027613Z")
        self.assertEqual(envelope.data.base_data.name, "test")
        self.assertEqual(envelope.data.base_data.id, "a6f5d48acb4d31d9")
        self.assertEqual(envelope.data.base_data.duration, "0.00:00:01.001")
        self.assertTrue(envelope.data.base_data.success)

        self.assertEqual(envelope.data.base_type, "RemoteDependencyData")
        self.assertEqual(envelope.data.base_data.type, "InProc")
        self.assertEqual(envelope.data.base_data.result_code, "0")

        # type
        span._parent = None
        envelope = exporter._span_to_envelope(span)
        self.assertIsNone(envelope.data.base_data.type)

    def test_span_envelope_server_http(self):
        exporter = self._exporter
        start_time = 1575494316027613500
        end_time = start_time + 1001000000

        # SpanKind.SERVER HTTP
        span = trace._Span(
            name="test",
            context=SpanContext(
                trace_id=36873507687745823477771305566750195431,
                span_id=12030755672171557337,
                is_remote=False,
            ),
            attributes={
                "http.method": "GET",
                "http.path": "/wiki/Rabbit",
                "http.route": "/wiki/Rabbit",
                "http.url": "https://www.wikipedia.org/wiki/Rabbit",
                "http.status_code": 200,
                "http.user_agent": "agent",
                "http.client_ip": "client_ip",
            },
            kind=SpanKind.SERVER,
        )
        span._status = Status(status_code=StatusCode.OK)
        span.start(start_time=start_time)
        span.end(end_time=end_time)
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(
            envelope.name, "Microsoft.ApplicationInsights.Request"
        )
        self.assertEqual(envelope.data.base_type, "RequestData")
        self.assertEqual(envelope.data.base_data.name, "GET /wiki/Rabbit")
        self.assertEqual(envelope.data.base_data.id, "a6f5d48acb4d31d9")
        self.assertEqual(envelope.data.base_data.duration, "0.00:00:01.001")
        self.assertEqual(envelope.data.base_data.response_code, "200")
        self.assertTrue(envelope.data.base_data.success)

        self.assertEqual(envelope.tags["ai.operation.name"], "GET /wiki/Rabbit")
        self.assertEqual(envelope.tags["ai.user.userAgent"], "agent")
        self.assertEqual(envelope.tags["ai.location.ip"], "client_ip")
        self.assertEqual(envelope.data.base_data.url, "https://www.wikipedia.org/wiki/Rabbit")
        
        # location
        span._attributes = {
            "http.method": "GET",
            "net.peer.ip": "peer_ip"
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.tags["ai.location.ip"], "peer_ip")

        # url
        span._attributes = {
            "http.method": "GET",
            "http.scheme": "https",
            "http.target": "/path",
            "http.host": "www.example.org",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.url, "https://www.example.org/path")

        span._attributes = {
            "http.method": "GET",
            "http.scheme": "https",
            "http.target": "/path",
            "net.host.port": "35555",
            "http.server_name": "example.com",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.url, "https://example.com:35555/path")

        span._attributes = {
            "http.method": "GET",
            "http.scheme": "https",
            "http.target": "/path",
            "net.host.port": "35555",
            "net.host.name": "localhost",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.url, "https://localhost:35555/path")

        # ai.operation.name
        span._attributes = {
            "http.method": "GET",
            "http.url": "https://www.wikipedia.org/wiki/Rabbit/test",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.tags["ai.operation.name"], "GET /wiki/Rabbit/test")
        self.assertEqual(envelope.data.base_data.name, "GET /wiki/Rabbit/test")

        span._attributes = {
            "http.method": "GET",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.tags["ai.operation.name"], "test")
        self.assertEqual(envelope.data.base_data.name, "test")

    def test_span_envelope_server_messaging(self):
        exporter = self._exporter
        start_time = 1575494316027613500
        end_time = start_time + 1001000000

        # SpanKind.SERVER messaging
        span = trace._Span(
            name="test",
            context=SpanContext(
                trace_id=36873507687745823477771305566750195431,
                span_id=12030755672171557337,
                is_remote=False,
            ),
            attributes={
                "messaging.system": "messaging",
                "net.peer.name": "test name",
                "net.peer.ip": "127.0.0.1",
                "messaging.destination": "celery",
            },
            kind=SpanKind.SERVER,
        )
        span._status = Status(status_code=StatusCode.OK)
        span.start(start_time=start_time)
        span.end(end_time=end_time)
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_type, "RequestData")
        self.assertEqual(envelope.data.base_data.name, "test")
        self.assertEqual(envelope.data.base_data.id, "a6f5d48acb4d31d9")
        self.assertEqual(envelope.data.base_data.duration, "0.00:00:01.001")
        self.assertTrue(envelope.data.base_data.success)
        # TODO: messaging

    def test_span_to_envelope_success_error(self):
        exporter = self._exporter
        start_time = 1575494316027613500
        end_time = start_time + 1001000000

        # Status/success error
        span = trace._Span(
            name="test",
            context=SpanContext(
                trace_id=36873507687745823477771305566750195431,
                span_id=12030755672171557337,
                is_remote=False,
            ),
            attributes={
                "test": "asd",
                "http.method": "GET",
                "http.url": "https://www.wikipedia.org/wiki/Rabbit",
                "http.status_code": 200,
            },
            kind=SpanKind.CLIENT,
        )
        span._status = Status(status_code=StatusCode.ERROR)
        span.start(start_time=start_time)
        span.end(end_time=end_time)
        envelope = exporter._span_to_envelope(span)
        self.assertFalse(envelope.data.base_data.success)

    def test_span_to_envelope_properties(self):
        exporter = self._exporter
        start_time = 1575494316027613500
        end_time = start_time + 1001000000

        # Properties
        span = trace._Span(
            name="test",
            context=SpanContext(
                trace_id=36873507687745823477771305566750195431,
                span_id=12030755672171557337,
                is_remote=False,
            ),
            attributes={
                "test": "asd",
                "http.method": "GET",
                "http.url": "https://www.wikipedia.org/wiki/Rabbit",
                "http.status_code": 200,
            },
            kind=SpanKind.CLIENT,
        )
        span._status = Status(status_code=StatusCode.OK)
        span.start(start_time=start_time)
        span.end(end_time=end_time)
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(len(envelope.data.base_data.properties), 1)
        self.assertEqual(envelope.data.base_data.properties["test"], "asd")

    def test_span_to_envelope_properties(self):
        exporter = self._exporter
        start_time = 1575494316027613500
        end_time = start_time + 1001000000

        # Links
        links = []
        links.append(
            Link(
                context=SpanContext(
                    trace_id=36873507687745823477771305566750195432,
                    span_id=12030755672171557338,
                    is_remote=False,
                )
            )
        )
        span = trace._Span(
            name="test",
            context=SpanContext(
                trace_id=36873507687745823477771305566750195431,
                span_id=12030755672171557337,
                is_remote=False,
            ),
            attributes={
                "http.method": "GET",
                "http.url": "https://www.wikipedia.org/wiki/Rabbit",
                "http.status_code": 200,
            },
            kind=SpanKind.CLIENT,
            links=links,
        )
        span._status = Status(status_code=StatusCode.OK)
        span.start(start_time=start_time)
        span.end(end_time=end_time)
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(len(envelope.data.base_data.properties), 1)
        json_dict = json.loads(
            envelope.data.base_data.properties["_MS.links"]
        )[0]
        self.assertEqual(json_dict["id"], "a6f5d48acb4d31da")
