# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import datetime as datetime_module
import json
import os
import platform
import shutil
import tempfile
import time as time_module
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock

# pylint: disable=import-error
from opentelemetry.trace import set_tracer_provider
from opentelemetry.sdk import trace, resources
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import Event, ReadableSpan

from opentelemetry.sdk.trace.export import SpanExportResult
from opentelemetry.sdk.util.instrumentation import InstrumentationScope
from opentelemetry.semconv.attributes.exception_attributes import (
    EXCEPTION_ESCAPED,
    EXCEPTION_MESSAGE,
    EXCEPTION_STACKTRACE,
    EXCEPTION_TYPE,
)
from opentelemetry.semconv._incubating.attributes import session_attributes
from opentelemetry.trace import Link, SpanContext, SpanKind
from opentelemetry.trace.status import Status, StatusCode

from azure.core.settings import settings
from azure.core.credentials import AccessToken
from azure.core.pipeline.transport import HttpResponse, HttpTransport
from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan

try:
    from azure.core.instrumentation import get_tracer as get_azure_sdk_tracer
except ImportError:
    # azure.core.instrumentation is not available in older versions of azure-core
    get_azure_sdk_tracer = None
from azure.monitor.opentelemetry.exporter.export._base import BaseExporter, ExportResult
from azure.monitor.opentelemetry.exporter.export.trace._exporter import (
    AzureMonitorTraceExporter,
    _check_instrumentation_span,
    _get_trace_export_result,
)
from azure.monitor.opentelemetry.exporter._constants import (
    _AZURE_SDK_NAMESPACE_NAME,
    _AZURE_SDK_OPENTELEMETRY_NAME,
    _AZURE_AI_SDK_NAME,
    _MULTI_ENDPOINT_ROUTING_ATTRIBUTES,
)
from azure.monitor.opentelemetry.exporter._generated.exporter.models import ContextTagKeys
from azure.monitor.opentelemetry.exporter._generated.exporter._utils.model_base import SdkJSONEncoder
from azure.monitor.opentelemetry.exporter._utils import azure_monitor_context


def throw(exc_type, *args, **kwargs):
    def func(*_args, **_kwargs):
        raise exc_type(*args, **kwargs)

    return func


# pylint: disable=import-error
# pylint: disable=protected-access, too-many-statements
# pylint: disable=too-many-lines, too-many-public-methods
class TestAzureTraceExporter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ.pop("APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL", None)
        os.environ.pop("APPINSIGHTS_INSTRUMENTATIONKEY", None)
        os.environ.pop("APPLICATIONINSIGHTS_OPENTELEMETRY_RESOURCE_METRIC_DISABLED", None)
        os.environ["APPINSIGHTS_INSTRUMENTATIONKEY"] = "1234abcd-5678-4efa-8abc-1234567890ab"
        os.environ["APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL"] = "true"
        os.environ["APPLICATIONINSIGHTS_OPENTELEMETRY_RESOURCE_METRIC_DISABLED"] = "true"
        cls._exporter = AzureMonitorTraceExporter(
            tracer_provider=trace.TracerProvider(),
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._exporter.storage._path, True)

    def test_constructor(self):
        """Test the constructor."""
        exporter = AzureMonitorTraceExporter(
            connection_string="InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab",
        )
        self.assertIsNone(exporter._tracer_provider)
        self.assertEqual(
            exporter._instrumentation_key,
            "4321abcd-5678-4efa-8abc-1234567890ab",
        )

    def test_constructor_tracer_provider(self):
        """Test the constructor."""
        tp = trace.TracerProvider()
        exporter = AzureMonitorTraceExporter(
            connection_string="InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab",
            tracer_provider=tp,
        )
        self.assertEqual(
            exporter._tracer_provider,
            tp,
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
            exporter._connection_string = (
                "InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab;"
                "IngestionEndpoint=https://eastus-8.in.applicationinsights.azure.com/;"
                "LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/;"
                "ApplicationId=4321abcd-5678-4efa-8abc-1234567890ab"
            )
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

    @mock.patch.dict(os.environ, {"APPLICATIONINSIGHTS_OPENTELEMETRY_RESOURCE_METRIC_DISABLED": "true"})
    def test_export_routing_attributes(self):
        attributes = {
            "microsoft.instrumentation_key": "customer-key",
            "microsoft.ingestion_endpoint": "https://example.com/",
            "microsoft.multi_endpoint_cloud_role": "customer-service",
            "microsoft.ingestion_auth": "ikey",
            "custom": "value",
            "microsoft.custom": "preserved",
        }
        span = trace.ReadableSpan(
            name="test",
            context=SpanContext(trace_id=1, span_id=2, is_remote=False),
            start_time=1,
            end_time=2,
            attributes=attributes.copy(),
            events=(
                trace.Event("event", attributes=attributes.copy()),
                trace.Event("exception", attributes=attributes.copy()),
            ),
        )
        for routing in (False, True):
            with self.subTest(routing=routing):
                with mock.patch.dict(
                    os.environ,
                    {"APPLICATIONINSIGHTS_EXPERIMENTAL_FEATURES": "multi_endpoint_routing" if routing else ""},
                ), mock.patch("azure.monitor.opentelemetry.exporter.export._base._enabled_experimental_features", None):
                    exporter = AzureMonitorTraceExporter(disable_offline_storage=True)
                self.addCleanup(exporter.client.close)
                self.addCleanup(exporter.shutdown)
                with mock.patch.object(BaseExporter, "_transmit", return_value=ExportResult.SUCCESS) as transmit:
                    self.assertEqual(exporter.export([span]), SpanExportResult.SUCCESS)
                transmit.assert_called_once()
                envelopes = transmit.call_args.args[0]
                self.assertEqual(
                    [envelope.data.base_type for envelope in envelopes],
                    ["RemoteDependencyData", "MessageData", "ExceptionData"],
                )
                for envelope in envelopes:
                    properties = envelope.data.base_data.properties
                    self.assertEqual(properties["custom"], "value")
                    self.assertEqual(properties["microsoft.custom"], "preserved")
                    if routing:
                        self.assertNotIn("microsoft.instrumentation_key", properties)
                        self.assertNotIn("microsoft.ingestion_endpoint", properties)
                        self.assertNotIn("microsoft.multi_endpoint_cloud_role", properties)
                        self.assertNotIn("microsoft.ingestion_auth", properties)
                    else:
                        self.assertEqual(properties, attributes)
                self.assertEqual(span.attributes, attributes)
                for event in span.events:
                    self.assertEqual(event.attributes, attributes)

    @mock.patch.dict(os.environ, {"APPLICATIONINSIGHTS_OPENTELEMETRY_RESOURCE_METRIC_DISABLED": "true"})
    def test_export_invalid_routing_attributes(self):
        valid = {
            "microsoft.instrumentation_key": "customer-key",
            "microsoft.ingestion_endpoint": "https://example.com/",
        }
        invalid = (
            {},
            {"microsoft.instrumentation_key": "customer-key"},
            {"microsoft.ingestion_endpoint": "https://example.com/"},
            {**valid, "microsoft.instrumentation_key": " "},
            {**valid, "microsoft.instrumentation_key": 42},
            {**valid, "microsoft.ingestion_endpoint": "http://example.com/"},
            {**valid, "microsoft.ingestion_endpoint": ("https://example.com/",)},
        )
        for routing in (False, True):
            with mock.patch.dict(
                os.environ, {"APPLICATIONINSIGHTS_EXPERIMENTAL_FEATURES": "multi_endpoint_routing" if routing else ""}
            ), mock.patch("azure.monitor.opentelemetry.exporter.export._base._enabled_experimental_features", None):
                exporter = AzureMonitorTraceExporter(disable_offline_storage=True)
            self.addCleanup(exporter.client.close)
            self.addCleanup(exporter.shutdown)
            for attributes in ([valid, *invalid, valid], invalid):
                with self.subTest(routing=routing, attributes=attributes):
                    spans = [
                        trace.ReadableSpan(
                            name=str(index),
                            context=SpanContext(trace_id=1, span_id=2, is_remote=False),
                            start_time=1,
                            end_time=2,
                            attributes=item,
                            events=(trace.Event("event", attributes=valid), trace.Event("exception", attributes=valid)),
                        )
                        for index, item in enumerate(attributes)
                    ]
                    with mock.patch.object(BaseExporter, "_transmit", return_value=ExportResult.SUCCESS) as transmit:
                        self.assertEqual(exporter.export(spans), SpanExportResult.SUCCESS)
                    if routing and not any(item == valid for item in attributes):
                        transmit.assert_not_called()
                        continue
                    transmit.assert_called_once()
                    envelopes = transmit.call_args.args[0]
                    expected = sum(item == valid for item in attributes) if routing else len(attributes)
                    self.assertEqual(len(envelopes), expected * 3)
                    self.assertEqual(
                        [envelope.data.base_data.name for envelope in envelopes[::3]],
                        [str(index) for index, item in enumerate(attributes) if not routing or item == valid],
                    )

    def test_export_with_tracer_provider(self):
        mock_resource = mock.Mock()
        tp = trace.TracerProvider(
            resource=mock_resource,
        )
        exporter = AzureMonitorTraceExporter(
            connection_string="InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab",
            tracer_provider=tp,
        )
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
            with mock.patch(
                "azure.monitor.opentelemetry.exporter.AzureMonitorTraceExporter._get_otel_resource_envelope"
            ) as resource_patch:  # noqa: E501
                result = exporter.export([test_span])
                resource_patch.assert_called_once_with(mock_resource, None)
                self.assertEqual(result, SpanExportResult.SUCCESS)
                self.assertEqual(storage_mock.call_count, 1)

    def test_export_with_tracer_provider_global(self):
        mock_resource = mock.Mock()
        tp = trace.TracerProvider(
            resource=mock_resource,
        )
        set_tracer_provider(tp)
        exporter = AzureMonitorTraceExporter(
            connection_string="InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab",
        )
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
            with mock.patch(
                "azure.monitor.opentelemetry.exporter.AzureMonitorTraceExporter._get_otel_resource_envelope"
            ) as resource_patch:  # noqa: E501
                result = exporter.export([test_span])
                resource_patch.assert_called_once_with(mock_resource, None)
                self.assertEqual(result, SpanExportResult.SUCCESS)
                self.assertEqual(storage_mock.call_count, 1)

    @mock.patch("azure.monitor.opentelemetry.exporter.export.trace._exporter._logger")
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
            {
                "service.name": "testServiceName",
                "service.namespace": "testServiceNamespace",
                "service.instance.id": "testServiceInstanceId",
            }
        )
        context = SpanContext(
            trace_id=36873507687745823477771305566750195431,
            span_id=12030755672171557338,
            is_remote=False,
        )
        test_span = trace._Span(
            name="test",
            context=context,
            resource=resource,
            attributes={
                "enduser.id": "testAuthId",
                "enduser.pseudo.id": "testUserId",
                session_attributes.SESSION_ID: "testSessionId",
                session_attributes.SESSION_PREVIOUS_ID: "testPreviousSessionId",
                "user_agent.synthetic.type": "bot",
            },
            parent=context,
        )
        test_span.start()
        test_span.end()
        envelope = exporter._span_to_envelope(test_span)

        self.assertEqual(envelope.instrumentation_key, "1234abcd-5678-4efa-8abc-1234567890ab")
        self.assertIsNotNone(envelope.tags)
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_DEVICE_ID),
            azure_monitor_context[ContextTagKeys.AI_DEVICE_ID],
        )
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_DEVICE_LOCALE),
            azure_monitor_context[ContextTagKeys.AI_DEVICE_LOCALE],
        )
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_DEVICE_TYPE),
            azure_monitor_context[ContextTagKeys.AI_DEVICE_TYPE],
        )
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_INTERNAL_SDK_VERSION),
            azure_monitor_context[ContextTagKeys.AI_INTERNAL_SDK_VERSION],
        )

        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_CLOUD_ROLE),
            "testServiceNamespace.testServiceName",
        )
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_CLOUD_ROLE_INSTANCE),
            "testServiceInstanceId",
        )
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_INTERNAL_NODE_NAME),
            "testServiceInstanceId",
        )
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_OPERATION_ID),
            "{:032x}".format(context.trace_id),
        )
        self.assertEqual(envelope.tags.get(ContextTagKeys.AI_USER_AUTH_USER_ID), "testAuthId")
        self.assertEqual(envelope.tags.get(ContextTagKeys.AI_USER_ID), "testUserId")
        self.assertEqual(envelope.tags.get(ContextTagKeys.AI_SESSION_ID), "testSessionId")
        self.assertNotIn(session_attributes.SESSION_ID, envelope.data.base_data.properties)
        self.assertEqual(
            envelope.data.base_data.properties.get(session_attributes.SESSION_PREVIOUS_ID),
            "testPreviousSessionId",
        )
        self.assertEqual(envelope.tags.get(ContextTagKeys.AI_OPERATION_SYNTHETIC_SOURCE), "True")
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_OPERATION_PARENT_ID),
            "{:016x}".format(context.span_id),
        )

    def test_span_to_envelope_partA_default(self):
        exporter = self._exporter
        resource = resources.Resource({"service.name": "testServiceName"})
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
        self.assertEqual(envelope.tags.get(ContextTagKeys.AI_CLOUD_ROLE), "testServiceName")
        self.assertEqual(envelope.tags.get(ContextTagKeys.AI_CLOUD_ROLE_INSTANCE), platform.node())
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_INTERNAL_NODE_NAME),
            envelope.tags.get(ContextTagKeys.AI_CLOUD_ROLE_INSTANCE),
        )

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

        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.RemoteDependency")
        self.assertEqual(envelope.time, datetime.fromisoformat("2019-12-04T21:18:36.027613+00:00"))
        self.assertEqual(envelope.data.base_data.name, "GET /wiki/Rabbit")
        self.assertEqual(envelope.data.base_data.id, "a6f5d48acb4d31d9")
        self.assertEqual(envelope.data.base_data.duration, "0.00:00:01.001")
        self.assertTrue(envelope.data.base_data.success)
        self.assertEqual(envelope.data.base_data.data, "https://www.wikipedia.org/wiki/Rabbit")

        self.assertEqual(envelope.data.base_type, "RemoteDependencyData")
        self.assertEqual(envelope.tags[ContextTagKeys.AI_OPERATION_NAME], "GET /wiki/Rabbit")
        self.assertEqual(envelope.data.base_data.type, "HTTP")
        self.assertEqual(envelope.data.base_data.target, "service")
        self.assertEqual(
            envelope.data.base_data.data,
            "https://www.wikipedia.org/wiki/Rabbit",
        )
        self.assertEqual(envelope.data.base_data.result_code, "200")
        self.assertEqual(envelope.tags["ai.user.userAgent"], "agent")
        self.assertEqual(len(envelope.data.base_data.properties), 0)

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

        # Stable semconv
        span._attributes = {
            "http.request.method": "GET",
            "server.address": "www.example.com",
            "server.port": "1234",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.target, "www.example.com:1234")
        span._attributes = {
            "http.request.method": "GET",
            "server.address": "www.example.com",
            "server.port": 80,
            "url.scheme": "http",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.target, "www.example.com")

        # Stable semconv, server.port absent (e.g. default-port URL)
        span._attributes = {
            "http.request.method": "GET",
            "server.address": "www.example.com",
            "url.scheme": "https",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.target, "www.example.com")

        span._attributes = {
            "http.request.method": "GET",
            "server.address": "www.example.com",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.target, "www.example.com")

        span._attributes = {
            "http.request.method": "GET",
            "gen_ai.system": "az.ai.inference",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.target, "az.ai.inference")
        self.assertEqual(envelope.data.base_data.name, "GET /")

        span._attributes = {
            "http.request.method": "GET",
            "server.address": "www.example.com",
            "server.port": 80,
            "url.scheme": "http",
            "gen_ai.system": "az.ai.inference",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.target, "www.example.com")

        # url
        # spell-checker:ignore ddds
        span._attributes = {
            "http.method": "GET",
            "http.scheme": "https",
            "http.host": "www.wikipedia.org",
            "http.target": "/path/12314/?q=ddds#123",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(
            envelope.data.base_data.data,
            "https://www.wikipedia.org/path/12314/?q=ddds#123",
        )

        span._attributes = {
            "http.method": "GET",
            "http.scheme": "https",
            "net.peer.port": "8080",
            "net.peer.name": "example.com",
            "http.target": "/path/12314/?q=ddds#123",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(
            envelope.data.base_data.data,
            "https://example.com:8080/path/12314/?q=ddds#123",
        )

        span._attributes = {
            "http.method": "GET",
            "http.scheme": "https",
            "net.peer.port": "8080",
            "net.peer.ip": "192.168.0.1",
            "http.target": "/path/12314/?q=ddds#123",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(
            envelope.data.base_data.data,
            "https://192.168.0.1:8080/path/12314/?q=ddds#123",
        )

        # Stable semconv
        span._attributes = {
            "http.request.method": "GET",
            "url.full": "https://www.wikipedia.org/path/12314/?q=ddds#124",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(
            envelope.data.base_data.data,
            "https://www.wikipedia.org/path/12314/?q=ddds#124",
        )

        # result_code
        span._attributes = {
            "http.method": "GET",
            "http.scheme": "https",
            "http.url": "https://www.example.com",
            "http.status_code": None,
        }
        envelope = exporter._span_to_envelope(span)
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.result_code, "0")

        span._attributes = {
            "http.method": "GET",
            "http.scheme": "https",
            "http.url": "https://www.example.com",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.result_code, "0")

        span._attributes = {
            "http.method": "GET",
            "http.scheme": "https",
            "http.url": "https://www.example.com",
            "http.status_code": "",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.result_code, "0")

        # Stable semconv
        span._attributes = {
            "http.request.method": "GET",
            "http.response.status_code": "200",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.result_code, "200")

        span._attributes = {
            "http.request.method": "GET",
            "http.response.status_code": "",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.result_code, "0")

    def test_span_to_envelope_client_db(self):
        exporter = self._exporter
        start_time = 1575494316027613500
        end_time = start_time + 1001000000

        # SpanKind.CLIENT Db, deprecated semconv
        span = trace._Span(
            name="test",
            context=SpanContext(
                trace_id=36873507687745823477771305566750195431,
                span_id=12030755672171557337,
                is_remote=False,
            ),
            attributes={
                "db.system": "db2 system",
                "peer.service": "service",
                "db.statement": "SELECT * from test",
            },
            kind=SpanKind.CLIENT,
        )
        span.start(start_time=start_time)
        span.end(end_time=end_time)
        span._status = Status(status_code=StatusCode.OK)
        envelope = exporter._span_to_envelope(span)

        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.RemoteDependency")
        self.assertEqual(envelope.time, datetime.fromisoformat("2019-12-04T21:18:36.027613+00:00"))
        self.assertEqual(envelope.data.base_data.name, "test")
        self.assertEqual(envelope.data.base_data.id, "a6f5d48acb4d31d9")
        self.assertEqual(envelope.data.base_data.duration, "0.00:00:01.001")
        self.assertTrue(envelope.data.base_data.success)

        self.assertEqual(envelope.data.base_type, "RemoteDependencyData")
        self.assertEqual(envelope.tags[ContextTagKeys.AI_OPERATION_NAME], "test")
        self.assertEqual(envelope.data.base_data.type, "db2 system")
        self.assertEqual(envelope.data.base_data.target, "service")
        self.assertEqual(envelope.data.base_data.data, "SELECT * from test")
        self.assertEqual(envelope.data.base_data.result_code, "0")
        self.assertEqual(len(envelope.data.base_data.properties), 0)

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

        # Stable semconv
        span._attributes = {
            "db.system.name": "postgresql",
            "db.query.text": "SELECT * from stable_test",
            "db.namespace": "stableDb",
            "server.address": "stable-server",
            "server.port": 15432,
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.type, "postgresql")
        self.assertEqual(envelope.data.base_data.data, "SELECT * from stable_test")
        self.assertEqual(envelope.data.base_data.target, "stable-server:15432|stableDb")

        span._attributes = {
            "db.system.name": "postgresql",
            "db.operation.name": "SELECT",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.data, "SELECT")

        # Type
        span._attributes = {
            "db.system": "mssql",
            "db.statement": "SELECT",
            "db.name": "testDb",
            "peer.service": "service",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.type, "SQL")

        span._attributes = {
            "db.system": "mysql",
            "db.statement": "SELECT",
            "db.name": "testDb",
            "peer.service": "service",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.type, "mysql")

        span._attributes = {
            "db.system": "postgresql",
            "db.statement": "SELECT",
            "db.name": "testDb",
            "peer.service": "service",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.type, "postgresql")

        span._attributes = {
            "db.system": "mongodb",
            "db.statement": "SELECT",
            "db.name": "testDb",
            "peer.service": "service",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.type, "mongodb")

        span._attributes = {
            "db.system": "redis",
            "db.statement": "SELECT",
            "db.name": "testDb",
            "peer.service": "service",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.type, "redis")

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

        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.RemoteDependency")
        self.assertEqual(envelope.time, datetime.fromisoformat("2019-12-04T21:18:36.027613+00:00"))
        self.assertEqual(envelope.data.base_data.name, "test")
        self.assertEqual(envelope.data.base_data.id, "a6f5d48acb4d31d9")
        self.assertEqual(envelope.data.base_data.duration, "0.00:00:01.001")
        self.assertTrue(envelope.data.base_data.success)
        self.assertEqual(envelope.data.base_data.result_code, "0")

        self.assertEqual(envelope.data.base_type, "RemoteDependencyData")
        self.assertEqual(envelope.tags[ContextTagKeys.AI_OPERATION_NAME], "test")
        self.assertEqual(envelope.data.base_data.type, "rpc.system")
        self.assertEqual(envelope.data.base_data.target, "service")
        self.assertEqual(len(envelope.data.base_data.properties), 0)

        # target
        span._attributes = {
            "rpc.system": "rpc",
            "rpc.service": "Test service",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.target, "rpc")

    def test_span_to_envelope_client_messaging(self):
        exporter = self._exporter
        start_time = 1575494316027613500
        end_time = start_time + 1001000000

        # SpanKind.CLIENT messaging
        span = trace._Span(
            name="test",
            context=SpanContext(
                trace_id=36873507687745823477771305566750195431,
                span_id=12030755672171557337,
                is_remote=False,
            ),
            attributes={
                "messaging.system": "messaging",
                "messaging.destination": "celery",
            },
            kind=SpanKind.CLIENT,
        )
        span.start(start_time=start_time)
        span.end(end_time=end_time)
        span._status = Status(status_code=StatusCode.OK)
        envelope = exporter._span_to_envelope(span)

        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.RemoteDependency")
        self.assertEqual(envelope.time, datetime.fromisoformat("2019-12-04T21:18:36.027613+00:00"))
        self.assertEqual(envelope.data.base_data.name, "test")
        self.assertEqual(envelope.data.base_data.id, "a6f5d48acb4d31d9")
        self.assertEqual(envelope.data.base_data.duration, "0.00:00:01.001")
        self.assertTrue(envelope.data.base_data.success)
        self.assertEqual(envelope.data.base_data.result_code, "0")

        self.assertEqual(envelope.data.base_type, "RemoteDependencyData")
        self.assertEqual(envelope.tags[ContextTagKeys.AI_OPERATION_NAME], "test")
        self.assertEqual(envelope.data.base_data.type, "messaging")
        self.assertEqual(envelope.data.base_data.target, "celery")
        self.assertEqual(len(envelope.data.base_data.properties), 0)

        # target
        span._attributes = {
            "messaging.system": "messaging",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.target, "messaging")

    def test_span_to_envelope_client_gen_ai(self):
        exporter = self._exporter
        start_time = 1575494316027613500
        end_time = start_time + 1001000000

        # SpanKind.CLIENT messaging
        span = trace._Span(
            name="test",
            context=SpanContext(
                trace_id=36873507687745823477771305566750195431,
                span_id=12030755672171557337,
                is_remote=False,
            ),
            attributes={
                "gen_ai.system": "az.ai.inference",
            },
            kind=SpanKind.CLIENT,
        )
        span.start(start_time=start_time)
        span.end(end_time=end_time)
        span._status = Status(status_code=StatusCode.UNSET)
        envelope = exporter._span_to_envelope(span)

        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.RemoteDependency")
        self.assertEqual(envelope.time, datetime.fromisoformat("2019-12-04T21:18:36.027613+00:00"))
        self.assertEqual(envelope.data.base_data.name, "test")
        self.assertEqual(envelope.data.base_data.id, "a6f5d48acb4d31d9")
        self.assertEqual(envelope.data.base_data.duration, "0.00:00:01.001")
        self.assertTrue(envelope.data.base_data.success)
        self.assertEqual(envelope.data.base_data.result_code, "0")

        self.assertEqual(envelope.data.base_type, "RemoteDependencyData")
        self.assertEqual(envelope.tags[ContextTagKeys.AI_OPERATION_NAME], "test")
        self.assertEqual(envelope.data.base_data.type, "GenAI | az.ai.inference")
        self.assertEqual(envelope.data.base_data.target, "az.ai.inference")
        self.assertEqual(len(envelope.data.base_data.properties), 1)

    def test_span_to_envelope_gen_ai_messages_attributes_length(self):
        exporter = self._exporter
        start_time = 1575494316027613500
        end_time = start_time + 1001000000
        messages_length = 1024 * 1024
        messages_value = "m" * messages_length
        oversized_messages_value = "o" * (4 * 1024 * 1024 + 1000)
        other_value = "t" * (1024 * 1024)

        span = trace._Span(
            name="chat",
            context=SpanContext(
                trace_id=36873507687745823477771305566750195431,
                span_id=12030755672171557337,
                is_remote=False,
            ),
            attributes={
                "gen_ai.system": "az.ai.inference",
                "gen_ai.input.messages": messages_value,
                "gen_ai.output.messages": oversized_messages_value,
                "gen_ai.tool.call.result": other_value,
                "custom.attribute": other_value,
            },
            kind=SpanKind.CLIENT,
        )
        span.start(start_time=start_time)
        span.end(end_time=end_time)
        span._status = Status(status_code=StatusCode.UNSET)
        # Without the experimental feature, existing truncation limits apply
        envelope = exporter._span_to_envelope(span)

        properties = envelope.data.base_data.properties
        self.assertEqual(len(properties["gen_ai.input.messages"]), 256 * 1024)
        self.assertEqual(len(properties["gen_ai.output.messages"]), 256 * 1024)
        self.assertEqual(len(properties["gen_ai.tool.call.result"]), 256 * 1024)
        self.assertEqual(len(properties["custom.attribute"]), 8 * 1024)

        with mock.patch(
            "azure.monitor.opentelemetry.exporter.export._base._enabled_experimental_features",
            frozenset({"gen_ai_input_output_limit_increase"}),
        ):
            envelope = exporter._span_to_envelope(span)

        properties = envelope.data.base_data.properties
        self.assertEqual(properties["gen_ai.input.messages"], messages_value)
        self.assertEqual(len(properties["gen_ai.output.messages"]), 4 * 1024 * 1024)
        self.assertEqual(len(properties["gen_ai.tool.call.result"]), 256 * 1024)
        self.assertEqual(len(properties["custom.attribute"]), 8 * 1024)

    def test_span_to_envelope_client_internal_gen_ai_type(self):
        exporter = self._exporter
        start_time = 1575494316027613500
        end_time = start_time + 1001000000

        span = trace._Span(
            name="test",
            context=SpanContext(
                trace_id=36873507687745823477771305566750195431,
                span_id=12030755672171557337,
                is_remote=False,
            ),
            attributes={
                "gen_ai.system": "az.ai.inference",
            },
            kind=SpanKind.INTERNAL,
        )
        span.start(start_time=start_time)
        span.end(end_time=end_time)
        span._status = Status(status_code=StatusCode.UNSET)
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.type, "GenAI | az.ai.inference")

    def test_span_to_envelope_client_multiple_types_with_gen_ai(self):
        exporter = self._exporter
        start_time = 1575494316027613500
        end_time = start_time + 1001000000

        span = trace._Span(
            name="test",
            context=SpanContext(
                trace_id=36873507687745823477771305566750195431,
                span_id=12030755672171557337,
                is_remote=False,
            ),
            attributes={
                "gen_ai.system": "az.ai.inference",
                "az.namespace": "Microsoft.EventHub",
                "peer.address": "test_address",
                "message_bus.destination": "test_destination",
            },
            kind=SpanKind.CLIENT,
        )
        span.start(start_time=start_time)
        span.end(end_time=end_time)
        span._status = Status(status_code=StatusCode.UNSET)
        envelope = exporter._span_to_envelope(span)

        self.assertEqual(envelope.data.base_data.type, "GenAI | az.ai.inference")
        self.assertEqual(envelope.data.base_data.target, "test_address/test_destination")

    def test_span_to_envelope_client_azure(self):
        exporter = self._exporter
        start_time = 1575494316027613500
        end_time = start_time + 1001000000

        # SpanKind.CLIENT messaging
        span = trace._Span(
            name="test",
            context=SpanContext(
                trace_id=36873507687745823477771305566750195431,
                span_id=12030755672171557337,
                is_remote=False,
            ),
            attributes={
                "az.namespace": "Microsoft.EventHub",
                "peer.address": "test_address",
                "message_bus.destination": "test_destination",
            },
            kind=SpanKind.CLIENT,
        )
        span.start(start_time=start_time)
        span.end(end_time=end_time)
        span._status = Status(status_code=StatusCode.OK)
        envelope = exporter._span_to_envelope(span)

        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.RemoteDependency")
        self.assertEqual(envelope.time, datetime.fromisoformat("2019-12-04T21:18:36.027613+00:00"))
        self.assertEqual(envelope.data.base_data.name, "test")
        self.assertEqual(envelope.data.base_data.id, "a6f5d48acb4d31d9")
        self.assertEqual(envelope.data.base_data.duration, "0.00:00:01.001")
        self.assertTrue(envelope.data.base_data.success)
        self.assertEqual(envelope.data.base_data.result_code, "0")

        self.assertEqual(envelope.data.base_type, "RemoteDependencyData")
        self.assertEqual(envelope.tags[ContextTagKeys.AI_OPERATION_NAME], "test")
        self.assertEqual(envelope.data.base_data.type, "Microsoft.EventHub")
        self.assertEqual(envelope.data.base_data.target, "test_address/test_destination")
        self.assertEqual(len(envelope.data.base_data.properties), 2)

        # target
        span._attributes = {
            "messaging.system": "messaging",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.target, "messaging")

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
                "messaging.destination": "celery",
            },
            kind=SpanKind.PRODUCER,
        )
        span.start(start_time=start_time)
        span.end(end_time=end_time)
        span._status = Status(status_code=StatusCode.OK)
        envelope = exporter._span_to_envelope(span)

        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.RemoteDependency")
        self.assertEqual(envelope.time, datetime.fromisoformat("2019-12-04T21:18:36.027613+00:00"))
        self.assertEqual(envelope.data.base_data.name, "test")
        self.assertEqual(envelope.data.base_data.id, "a6f5d48acb4d31d9")
        self.assertEqual(envelope.data.base_data.duration, "0.00:00:01.001")
        self.assertTrue(envelope.data.base_data.success)
        self.assertEqual(envelope.data.base_data.result_code, "0")

        self.assertEqual(envelope.data.base_type, "RemoteDependencyData")
        self.assertEqual(envelope.tags[ContextTagKeys.AI_OPERATION_NAME], "test")
        self.assertEqual(envelope.data.base_data.type, "Queue Message | messaging")
        self.assertEqual(envelope.data.base_data.target, "celery")
        self.assertEqual(len(envelope.data.base_data.properties), 0)

        # target
        span._attributes = {
            "messaging.system": "messaging",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.target, "messaging")

        # azure specific
        # spell-checker:ignore myeventhub
        span._attributes = {
            "az.namespace": "Microsoft.EventHub",
            "peer.address": "Test_peer",
            "message_bus.destination": "/myeventhub",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.type, "Queue Message | Microsoft.EventHub")
        self.assertEqual(envelope.data.base_data.target, "Test_peer//myeventhub")
        self.assertEqual(len(envelope.data.base_data.properties), 2)

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

        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.RemoteDependency")
        self.assertEqual(envelope.time, datetime.fromisoformat("2019-12-04T21:18:36.027613+00:00"))
        self.assertEqual(envelope.data.base_data.name, "test")
        self.assertEqual(envelope.data.base_data.id, "a6f5d48acb4d31d9")
        self.assertEqual(envelope.data.base_data.duration, "0.00:00:01.001")
        self.assertTrue(envelope.data.base_data.success)

        self.assertEqual(envelope.data.base_type, "RemoteDependencyData")
        self.assertEqual(envelope.tags[ContextTagKeys.AI_OPERATION_NAME], "test")
        self.assertEqual(envelope.data.base_data.type, "InProc")
        self.assertEqual(envelope.data.base_data.result_code, "0")
        self.assertEqual(len(envelope.data.base_data.properties), 0)

        # azure specific
        span._attributes = {
            "az.namespace": "Microsoft.EventHub",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.type, "InProc | Microsoft.EventHub")
        self.assertEqual(len(envelope.data.base_data.properties), 1)

    def test_span_envelope_request_azure(self):
        exporter = self._exporter
        start_time = 4000000000000000000
        end_time = start_time + 1001000000

        # SpanKind.SERVER/CONSUMER Azure specific
        links = []
        links.append(
            Link(
                context=SpanContext(
                    trace_id=36873507687745823477771305566750195432,
                    span_id=12030755672171557338,
                    is_remote=False,
                ),
                attributes={"enqueuedTime": 1000000000000},
            )
        )
        links.append(
            Link(
                context=SpanContext(
                    trace_id=36873507687745823477771305566750195432,
                    span_id=12030755672171557338,
                    is_remote=False,
                ),
                attributes={"enqueuedTime": 3000000000000},
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
                "az.namespace": "Microsoft.EventHub",
                "peer.address": "Test_peer",
                "message_bus.destination": "/myeventhub",
            },
            kind=SpanKind.CONSUMER,
            links=links,
        )
        span._status = Status(status_code=StatusCode.OK)
        span.start(start_time=start_time)
        span.end(end_time=end_time)
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Request")
        self.assertEqual(envelope.tags[ContextTagKeys.AI_OPERATION_NAME], "test")
        self.assertEqual(envelope.data.base_type, "RequestData")
        self.assertEqual(envelope.data.base_data.name, "test")
        self.assertEqual(envelope.data.base_data.id, "a6f5d48acb4d31d9")
        self.assertEqual(envelope.data.base_data.duration, "0.00:00:01.001")
        self.assertEqual(envelope.data.base_data.response_code, "0")
        self.assertTrue(envelope.data.base_data.success)
        self.assertEqual(envelope.data.base_data.source, "Test_peer//myeventhub")
        self.assertEqual(envelope.data.base_data.measurements["timeSinceEnqueued"], 2000000000000)
        self.assertEqual(len(envelope.data.base_data.properties), 3)

        # enqueued time
        links = []
        links.append(
            Link(
                context=SpanContext(
                    trace_id=36873507687745823477771305566750195432,
                    span_id=12030755672171557338,
                    is_remote=False,
                ),
                attributes={"enqueuedTime": 5000000000000},
            )
        )
        links.append(
            Link(
                context=SpanContext(
                    trace_id=36873507687745823477771305566750195432,
                    span_id=12030755672171557338,
                    is_remote=False,
                ),
                attributes={"enqueuedTime": 6000000000000},
            )
        )
        span._links = links
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.measurements["timeSinceEnqueued"], 0)

        # Source new semconv
        span._attributes = {
            "az.namespace": "Microsoft.EventHub",
            "net.peer.name": "Test_name",
            "messaging.destination.name": "/testdest",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.source, "Test_name//testdest")

        span._attributes = {
            "az.namespace": "Microsoft.EventHub",
            "server.address": "Test_name",
            "messaging.destination.name": "/testdest",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.source, "Test_name//testdest")

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
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Request")
        self.assertEqual(envelope.data.base_type, "RequestData")
        self.assertEqual(envelope.data.base_data.name, "GET /wiki/Rabbit")
        self.assertEqual(envelope.data.base_data.id, "a6f5d48acb4d31d9")
        self.assertEqual(envelope.data.base_data.duration, "0.00:00:01.001")
        self.assertEqual(envelope.data.base_data.response_code, "200")
        self.assertTrue(envelope.data.base_data.success)
        self.assertEqual(envelope.data.base_data.url, "https://www.wikipedia.org/wiki/Rabbit")

        self.assertEqual(envelope.tags[ContextTagKeys.AI_OPERATION_NAME], "GET /wiki/Rabbit")
        self.assertEqual(envelope.tags["ai.user.userAgent"], "agent")
        self.assertEqual(envelope.tags[ContextTagKeys.AI_LOCATION_IP], "client_ip")
        self.assertEqual(len(envelope.data.base_data.properties), 0)

        # success
        span._attributes = {
            "http.method": "GET",
            "net.peer.ip": "peer_ip",
            "http.status_code": 400,
        }
        envelope = exporter._span_to_envelope(span)
        self.assertFalse(envelope.data.base_data.success)
        self.assertEqual(envelope.data.base_data.response_code, "400")

        # 5xx - trace treats 5xx as success (only 4xx is failure)
        span._attributes = {
            "http.method": "GET",
            "net.peer.ip": "peer_ip",
            "http.status_code": 500,
        }
        envelope = exporter._span_to_envelope(span)
        self.assertTrue(envelope.data.base_data.success)
        self.assertEqual(envelope.data.base_data.response_code, "500")

        ## Stable http semconv
        span._attributes = {
            "http.request.method": "GET",
            "http.response.status_code": 200,
        }
        envelope = exporter._span_to_envelope(span)
        self.assertTrue(envelope.data.base_data.success)
        self.assertEqual(envelope.data.base_data.response_code, "200")

        span._attributes = {
            "http.request.method": "GET",
            "http.response.status_code": 400,
        }
        envelope = exporter._span_to_envelope(span)
        self.assertFalse(envelope.data.base_data.success)
        self.assertEqual(envelope.data.base_data.response_code, "400")

        span._attributes = {
            "http.method": "GET",
            "net.peer.ip": "peer_ip",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertFalse(envelope.data.base_data.success)
        self.assertEqual(envelope.data.base_data.response_code, "0")

        span._attributes = {
            "http.method": "GET",
            "net.peer.ip": "peer_ip",
            "http.status_code": "",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertFalse(envelope.data.base_data.success)
        self.assertEqual(envelope.data.base_data.response_code, "0")

        # Stable semconv - no status code
        span._attributes = {
            "http.request.method": "GET",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertFalse(envelope.data.base_data.success)
        self.assertEqual(envelope.data.base_data.response_code, "0")

        # Stable semconv - no status code
        span._attributes = {
            "http.request.method": "GET",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertFalse(envelope.data.base_data.success)
        self.assertEqual(envelope.data.base_data.response_code, "0")

        # location
        span._attributes = {"http.method": "GET", "net.peer.ip": "peer_ip"}
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.tags[ContextTagKeys.AI_LOCATION_IP], "peer_ip")

        ## Stable http semconv
        span._attributes = {
            "http.request.method": "GET",
            "client.address": "client_address",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.tags[ContextTagKeys.AI_LOCATION_IP], "client_address")

        # url
        span._attributes = {
            "http.method": "GET",
            "http.scheme": "https",
            "http.target": "/path",
            "http.host": "www.example.org",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.url, "https://www.example.org/path")

        ## Stable http semconv
        span._attributes = {
            "http.request.method": "GET",
            "url.full": "https://www.example.org:80/path?query",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.url, "https://www.example.org:80/path?query")

        span._attributes = {
            "http.request.method": "GET",
            "url.scheme": "https",
            "url.path": "/path",
            "url.query": "query",
            "server.address": "www.example.org",
            "server.port": "80",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.url, "https://www.example.org:80/path?query")

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
            "http.route": "/wiki/Rabbit/test",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.tags[ContextTagKeys.AI_OPERATION_NAME], "GET /wiki/Rabbit/test")
        self.assertEqual(envelope.data.base_data.name, "GET /wiki/Rabbit/test")

        ## Stable http semconv
        span._attributes = {
            "http.request.method": "GET",
            "http.route": "/wiki/Rabbit/test",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.tags[ContextTagKeys.AI_OPERATION_NAME], "GET /wiki/Rabbit/test")
        self.assertEqual(envelope.data.base_data.name, "GET /wiki/Rabbit/test")

        span._attributes = {
            "http.method": "GET",
            "http.url": "https://www.wikipedia.org/wiki/Rabbit/test",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.tags[ContextTagKeys.AI_OPERATION_NAME], "GET /wiki/Rabbit/test")
        self.assertEqual(envelope.data.base_data.name, "GET /wiki/Rabbit/test")

        span._attributes = {
            "http.request.method": "GET",
            "url.full": "https://www.wikipedia.org/wiki/Rabbit/test",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.tags[ContextTagKeys.AI_OPERATION_NAME], "GET /wiki/Rabbit/test")
        self.assertEqual(envelope.data.base_data.name, "GET /wiki/Rabbit/test")

        # Default is span name
        span._attributes = {
            "http.method": "GET",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.tags[ContextTagKeys.AI_OPERATION_NAME], "test")
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
        self.assertEqual(envelope.tags[ContextTagKeys.AI_OPERATION_NAME], "test")
        self.assertEqual(envelope.data.base_type, "RequestData")
        self.assertEqual(envelope.data.base_data.name, "test")
        self.assertEqual(envelope.data.base_data.id, "a6f5d48acb4d31d9")
        self.assertEqual(envelope.data.base_data.duration, "0.00:00:01.001")
        self.assertTrue(envelope.data.base_data.success)

        self.assertEqual(envelope.tags[ContextTagKeys.AI_LOCATION_IP], "127.0.0.1")
        self.assertEqual(envelope.data.base_data.source, "test name/celery")
        self.assertEqual(len(envelope.data.base_data.properties), 0)

        # source
        span._attributes = {
            "messaging.system": "messaging",
            "net.peer.ip": "127.0.0.1",
            "messaging.destination": "celery",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.source, "127.0.0.1/celery")

        span._attributes = {
            "messaging.system": "messaging",
            "messaging.destination": "celery",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.source, "celery")

        ## Stable http semconv
        span._attributes = {
            "messaging.system": "messaging",
            "client.address": "127.0.0.1",
            "messaging.destination": "celery",
        }
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.source, "127.0.0.1/celery")

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

    def test_span_to_envelope_sample_rate(self):
        exporter = self._exporter
        start_time = 1575494316027613500
        end_time = start_time + 1001000000

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
                "_MS.sampleRate": 50,
            },
            kind=SpanKind.CLIENT,
        )
        span._status = Status(status_code=StatusCode.OK)
        span.start(start_time=start_time)
        span.end(end_time=end_time)
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.sample_rate, 50)
        self.assertIsNone(envelope.data.base_data.properties.get("_MS.sampleRate"))

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

    def test_span_to_envelope_custom_measurements(self):
        exporter = self._exporter
        start_time = 1575494316027613500
        end_time = start_time + 1001000000

        span = trace._Span(
            name="test",
            context=SpanContext(
                trace_id=36873507687745823477771305566750195431,
                span_id=12030755672171557337,
                is_remote=False,
            ),
            attributes={
                "test": "asd",
                "microsoft.custom_measurements": '{"itemsProcessed": 42.0, "queueDepth": 7}',
            },
            kind=SpanKind.CLIENT,
        )
        span._status = Status(status_code=StatusCode.OK)
        span.start(start_time=start_time)
        span.end(end_time=end_time)
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_type, "RemoteDependencyData")
        self.assertEqual(
            envelope.data.base_data.measurements,
            {"itemsProcessed": 42.0, "queueDepth": 7.0},
        )
        self.assertIsNone(envelope.data.base_data.properties.get("microsoft.custom_measurements"))

    def test_span_to_envelope_custom_measurements_request(self):
        exporter = self._exporter
        start_time = 1575494316027613500
        end_time = start_time + 1001000000

        links = []
        links.append(
            Link(
                context=SpanContext(
                    trace_id=36873507687745823477771305566750195431,
                    span_id=12030755672171557337,
                    is_remote=False,
                ),
                attributes={"enqueuedTime": 3000000000000},
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
                "az.namespace": "Microsoft.EventHub",
                "microsoft.custom_measurements": '{"itemsProcessed": 42.0}',
            },
            kind=SpanKind.CONSUMER,
            links=links,
        )
        span._status = Status(status_code=StatusCode.OK)
        span.start(start_time=start_time)
        span.end(end_time=end_time)
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_type, "RequestData")
        # Custom measurements are merged with the measurements set by the exporter
        self.assertEqual(envelope.data.base_data.measurements["itemsProcessed"], 42.0)
        self.assertIn("timeSinceEnqueued", envelope.data.base_data.measurements)
        self.assertIsNone(envelope.data.base_data.properties.get("microsoft.custom_measurements"))

    def test_span_to_envelope_custom_measurements_invalid(self):
        exporter = self._exporter
        start_time = 1575494316027613500
        end_time = start_time + 1001000000

        span = trace._Span(
            name="test",
            context=SpanContext(
                trace_id=36873507687745823477771305566750195431,
                span_id=12030755672171557337,
                is_remote=False,
            ),
            attributes={
                "microsoft.custom_measurements": "not json",
            },
            kind=SpanKind.CLIENT,
        )
        span._status = Status(status_code=StatusCode.OK)
        span.start(start_time=start_time)
        span.end(end_time=end_time)
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(envelope.data.base_data.measurements, {})
        self.assertIsNone(envelope.data.base_data.properties.get("microsoft.custom_measurements"))

    def test_span_to_envelope_properties_links(self):
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
        json_dict = json.loads(envelope.data.base_data.properties["_MS.links"])[0]
        self.assertEqual(json_dict["id"], "a6f5d48acb4d31da")

    def test_span_to_envelope_properties_std_metrics(self):
        exporter = self._exporter
        start_time = 1575494316027613500
        end_time = start_time + 1001000000

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
            instrumentation_scope=InstrumentationScope("opentelemetry.instrumentation.requests"),
        )
        span._status = Status(status_code=StatusCode.OK)
        span.start(start_time=start_time)
        span.end(end_time=end_time)
        envelope = exporter._span_to_envelope(span)
        self.assertEqual(len(envelope.data.base_data.properties), 1)
        self.assertEqual(
            envelope.data.base_data.properties["_MS.ProcessedByMetricExtractors"],
            "True",
        )

    def test_span_events_to_envelopes_exception(self):
        exporter = self._exporter
        time = 1575494316027613500

        span = trace._Span(
            name="test",
            context=SpanContext(
                trace_id=36873507687745823477771305566750195431,
                span_id=12030755672171557337,
                is_remote=False,
            ),
            parent=SpanContext(
                trace_id=36873507687745823477771305566750195432,
                span_id=12030755672171557338,
                is_remote=False,
            ),
            kind=SpanKind.CLIENT,
            attributes={session_attributes.SESSION_ID: "testSessionId"},
        )
        attributes = {
            EXCEPTION_TYPE: "ZeroDivisionError",
            EXCEPTION_MESSAGE: "zero division error",
            EXCEPTION_STACKTRACE: "Traceback: ZeroDivisionError, division by zero",
            EXCEPTION_ESCAPED: "True",
        }
        span.add_event("exception", attributes, time)
        span.start()
        span.end()
        span._status = Status(status_code=StatusCode.OK)
        envelopes = exporter._span_events_to_envelopes(span)

        self.assertEqual(len(envelopes), 1)
        envelope = envelopes[0]
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Exception")
        self.assertEqual(envelope.instrumentation_key, "1234abcd-5678-4efa-8abc-1234567890ab")
        self.assertIsNotNone(envelope.tags)
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_DEVICE_ID),
            azure_monitor_context[ContextTagKeys.AI_DEVICE_ID],
        )
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_DEVICE_LOCALE),
            azure_monitor_context[ContextTagKeys.AI_DEVICE_LOCALE],
        )
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_DEVICE_TYPE),
            azure_monitor_context[ContextTagKeys.AI_DEVICE_TYPE],
        )
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_INTERNAL_SDK_VERSION),
            azure_monitor_context[ContextTagKeys.AI_INTERNAL_SDK_VERSION],
        )
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_OPERATION_ID),
            "{:032x}".format(span.context.trace_id),
        )
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_OPERATION_PARENT_ID),
            "{:016x}".format(span.context.span_id),
        )
        self.assertEqual(envelope.tags.get(ContextTagKeys.AI_SESSION_ID), "testSessionId")
        self.assertEqual(envelope.time, datetime.fromisoformat("2019-12-04T21:18:36.027613+00:00"))
        self.assertEqual(len(envelope.data.base_data.properties), 0)
        self.assertEqual(len(envelope.data.base_data.exceptions), 1)
        self.assertEqual(envelope.data.base_data.exceptions[0].type_name, "ZeroDivisionError")
        self.assertEqual(envelope.data.base_data.exceptions[0].message, "zero division error")
        self.assertEqual(envelope.data.base_data.exceptions[0].has_full_stack, True)
        self.assertEqual(
            envelope.data.base_data.exceptions[0].stack,
            "Traceback: ZeroDivisionError, division by zero",
        )
        self.assertEqual(envelope.data.base_type, "ExceptionData")

    def test_span_events_to_envelopes_message(self):
        exporter = self._exporter
        time = 1575494316027613500

        span = trace._Span(
            name="test",
            context=SpanContext(
                trace_id=36873507687745823477771305566750195431,
                span_id=12030755672171557337,
                is_remote=False,
            ),
            parent=SpanContext(
                trace_id=36873507687745823477771305566750195432,
                span_id=12030755672171557338,
                is_remote=False,
            ),
            kind=SpanKind.CLIENT,
        )
        attributes = {
            "test": "asd",
        }
        span.add_event("test event", attributes, time)
        span.start()
        span.end()
        span._status = Status(status_code=StatusCode.OK)
        envelopes = exporter._span_events_to_envelopes(span)

        self.assertEqual(len(envelopes), 1)
        envelope = envelopes[0]
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Message")
        self.assertEqual(envelope.instrumentation_key, "1234abcd-5678-4efa-8abc-1234567890ab")
        self.assertIsNotNone(envelope.tags)
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_DEVICE_ID),
            azure_monitor_context[ContextTagKeys.AI_DEVICE_ID],
        )
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_DEVICE_LOCALE),
            azure_monitor_context[ContextTagKeys.AI_DEVICE_LOCALE],
        )
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_DEVICE_TYPE),
            azure_monitor_context[ContextTagKeys.AI_DEVICE_TYPE],
        )
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_INTERNAL_SDK_VERSION),
            azure_monitor_context[ContextTagKeys.AI_INTERNAL_SDK_VERSION],
        )
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_OPERATION_ID),
            "{:032x}".format(span.context.trace_id),
        )
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_OPERATION_PARENT_ID),
            "{:016x}".format(span.context.span_id),
        )
        self.assertEqual(envelope.time, datetime.fromisoformat("2019-12-04T21:18:36.027613+00:00"))
        self.assertEqual(len(envelope.data.base_data.properties), 1)
        self.assertEqual(envelope.data.base_data.properties["test"], "asd")
        self.assertEqual(envelope.data.base_data.message, "test event")
        self.assertEqual(envelope.data.base_type, "MessageData")

    def test_span_events_to_envelopes_session_id(self):
        exporter = self._exporter
        time = 1575494316027613500

        for span_session_id, event_session_id, expected_session_id in (
            ("spanSessionId", None, "spanSessionId"),
            (None, "eventSessionId", "eventSessionId"),
            ("spanSessionId", "eventSessionId", "eventSessionId"),
        ):
            with self.subTest(span_session_id=span_session_id, event_session_id=event_session_id):
                span_attributes = (
                    {session_attributes.SESSION_ID: span_session_id} if span_session_id is not None else None
                )
                event_attributes = (
                    {session_attributes.SESSION_ID: event_session_id} if event_session_id is not None else None
                )
                span = trace._Span(
                    name="test",
                    context=SpanContext(
                        trace_id=36873507687745823477771305566750195431,
                        span_id=12030755672171557337,
                        is_remote=False,
                    ),
                    kind=SpanKind.CLIENT,
                    attributes=span_attributes,
                )
                span.add_event(
                    "test event",
                    event_attributes,
                    time,
                )
                span.start()
                span.end()
                envelopes = exporter._span_events_to_envelopes(span)

                self.assertEqual(len(envelopes), 1)
                envelope = envelopes[0]
                self.assertEqual(
                    envelope.tags.get(ContextTagKeys.AI_SESSION_ID),
                    expected_session_id,
                )
                self.assertNotIn(
                    session_attributes.SESSION_ID,
                    envelope.data.base_data.properties,
                )

    def test_span_events_to_envelopes_custom_measurements(self):
        exporter = self._exporter
        time = 1575494316027613500

        span = trace._Span(
            name="test",
            context=SpanContext(
                trace_id=36873507687745823477771305566750195431,
                span_id=12030755672171557337,
                is_remote=False,
            ),
            kind=SpanKind.CLIENT,
        )
        span.add_event(
            "test event",
            {"test": "asd", "microsoft.custom_measurements": '{"itemsProcessed": 42.0}'},
            time,
        )
        span.add_event(
            "exception",
            {
                "exception.type": "ZeroDivisionError",
                "exception.message": "zero division error",
                "microsoft.custom_measurements": '{"itemsProcessed": 42.0}',
            },
            time,
        )
        span.start()
        span.end()
        span._status = Status(status_code=StatusCode.OK)
        envelopes = exporter._span_events_to_envelopes(span)

        self.assertEqual(len(envelopes), 2)
        for envelope, base_type in zip(envelopes, ("MessageData", "ExceptionData")):
            with self.subTest(base_type=base_type):
                self.assertEqual(envelope.data.base_type, base_type)
                self.assertEqual(envelope.data.base_data.measurements, {"itemsProcessed": 42.0})
                self.assertIsNone(envelope.data.base_data.properties.get("microsoft.custom_measurements"))

    def test_span_events_to_envelopes_sample_rate(self):
        exporter = self._exporter
        time = 1575494316027613500

        span = trace._Span(
            name="test",
            context=SpanContext(
                trace_id=36873507687745823477771305566750195431,
                span_id=12030755672171557337,
                is_remote=False,
            ),
            parent=SpanContext(
                trace_id=36873507687745823477771305566750195432,
                span_id=12030755672171557338,
                is_remote=False,
            ),
            kind=SpanKind.CLIENT,
            attributes={
                "_MS.sampleRate": 50,
            },
        )
        attributes = {
            "test": "asd",
            "_MS.sampleRate": 75,
        }
        span.add_event("test event", attributes, time)
        span.start()
        span.end()
        span._status = Status(status_code=StatusCode.OK)
        envelopes = exporter._span_events_to_envelopes(span)

        self.assertEqual(len(envelopes), 1)
        envelope = envelopes[0]
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Message")
        self.assertEqual(envelope.sample_rate, 50)
        self.assertEqual(envelope.instrumentation_key, "1234abcd-5678-4efa-8abc-1234567890ab")
        self.assertIsNotNone(envelope.tags)
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_DEVICE_ID),
            azure_monitor_context[ContextTagKeys.AI_DEVICE_ID],
        )
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_DEVICE_LOCALE),
            azure_monitor_context[ContextTagKeys.AI_DEVICE_LOCALE],
        )
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_DEVICE_TYPE),
            azure_monitor_context[ContextTagKeys.AI_DEVICE_TYPE],
        )
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_INTERNAL_SDK_VERSION),
            azure_monitor_context[ContextTagKeys.AI_INTERNAL_SDK_VERSION],
        )
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_OPERATION_ID),
            "{:032x}".format(span.context.trace_id),
        )
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_OPERATION_PARENT_ID),
            "{:016x}".format(span.context.span_id),
        )
        self.assertEqual(envelope.time, datetime.fromisoformat("2019-12-04T21:18:36.027613+00:00"))
        self.assertEqual(len(envelope.data.base_data.properties), 1)
        self.assertEqual(envelope.data.base_data.properties["test"], "asd")
        self.assertEqual(envelope.data.base_data.message, "test event")
        self.assertEqual(envelope.data.base_type, "MessageData")

    def test_export_otel_resource_metric_routing(self):
        span = trace.ReadableSpan(
            name="test",
            context=SpanContext(trace_id=1, span_id=2, is_remote=False),
            start_time=1,
            end_time=2,
            attributes={
                "microsoft.instrumentation_key": "customer-key",
                "microsoft.ingestion_endpoint": "https://example.com/",
            },
        )
        variable = "APPLICATIONINSIGHTS_OPENTELEMETRY_RESOURCE_METRIC_DISABLED"
        for routing in (False, True):
            with mock.patch.dict(
                os.environ, {"APPLICATIONINSIGHTS_EXPERIMENTAL_FEATURES": "multi_endpoint_routing" if routing else ""}
            ), mock.patch("azure.monitor.opentelemetry.exporter.export._base._enabled_experimental_features", None):
                exporter = AzureMonitorTraceExporter(
                    disable_offline_storage=True,
                    tracer_provider=trace.TracerProvider(),
                )
            self.addCleanup(exporter.client.close)
            self.addCleanup(exporter.shutdown)
            for disabled in (None, "false", "true", "TRUE"):
                with self.subTest(routing=routing, disabled=disabled), mock.patch.dict(os.environ):
                    if disabled is None:
                        os.environ.pop(variable, None)
                    else:
                        os.environ[variable] = disabled
                    with mock.patch.object(BaseExporter, "_transmit", return_value=ExportResult.SUCCESS) as transmit:
                        self.assertEqual(exporter.export([span]), SpanExportResult.SUCCESS)
                    transmit.assert_called_once()
                    envelopes = transmit.call_args.args[0]
                    collect_resource = not routing and disabled not in ("true", "TRUE")
                    self.assertEqual(len(envelopes), 2 if collect_resource else 1)
                    self.assertEqual(envelopes[-1].data.base_type, "RemoteDependencyData")
                    if collect_resource:
                        self.assertEqual(envelopes[0].data.base_data.metrics[0].name, "_OTELRESOURCE_")

    @mock.patch("azure.monitor.opentelemetry.exporter.export.trace._exporter.get_tracer_provider")
    def test_export_otel_resource_metric(self, mock_get_tracer_provider):
        del os.environ["APPLICATIONINSIGHTS_OPENTELEMETRY_RESOURCE_METRIC_DISABLED"]
        mock_tracer_provider = mock.Mock()
        mock_get_tracer_provider.return_value = mock_tracer_provider
        test_resource = resources.Resource(
            attributes={
                "string_test_key": "string_value",
                "int_test_key": -1,
                "bool_test_key": False,
                "float_test_key": 0.5,
                "sequence_test_key": ["a", "b"],
            }
        )
        mock_tracer_provider.resource = test_resource
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
        exporter = AzureMonitorTraceExporter(
            _disable_offline_storage=True,
        )
        with mock.patch(
            "azure.monitor.opentelemetry.exporter.AzureMonitorTraceExporter._transmit"
        ) as transmit:  # noqa: E501
            transmit.return_value = ExportResult.SUCCESS
            with mock.patch(
                "azure.monitor.opentelemetry.exporter.AzureMonitorTraceExporter._get_otel_resource_envelope"
            ) as mock_get_otel_resource_envelope:  # noqa: E501
                mock_get_otel_resource_envelope.return_value = "test_envelope"
                result = exporter.export([test_span])
                self.assertEqual(result, SpanExportResult.SUCCESS)
                mock_get_otel_resource_envelope.assert_called_once_with(test_resource, None)
                envelopes = ["test_envelope", exporter._span_to_envelope(test_span)]
                transmit.assert_called_once_with(envelopes)

    def test_get_otel_resource_envelope(self):
        exporter = self._exporter
        test_resource = resources.Resource(
            attributes={
                "string_test_key": "string_value",
                "int_test_key": -1,
                "bool_test_key": False,
                "float_test_key": 0.5,
                "sequence_test_key": ["a", "b"],
                "microsoft.applicationId": "test_app_id",
            }
        )
        envelope = exporter._get_otel_resource_envelope(test_resource, "test_app_id")
        metric_name = envelope.name
        self.assertEqual(metric_name, "Microsoft.ApplicationInsights.Metric")
        instrumentation_key = envelope.instrumentation_key
        self.assertEqual(instrumentation_key, exporter._instrumentation_key)

        monitor_base = envelope.data
        self.assertEqual(monitor_base.base_type, "MetricData")
        metrics_data = monitor_base.base_data
        resource_attributes = metrics_data.properties
        # Properties are converted to strings in the envelope
        expected_attributes = {
            "string_test_key": "string_value",
            "int_test_key": "-1",
            "bool_test_key": "False",
            "float_test_key": "0.5",
            "sequence_test_key": "('a', 'b')",
            "microsoft.applicationId": "test_app_id",
        }
        self.assertEqual(resource_attributes, expected_attributes)
        metrics = metrics_data.metrics
        self.assertEqual(len(metrics), 1)
        self.assertEqual(metrics[0].name, "_OTELRESOURCE_")

    def test_get_otel_resource_envelope_serializes_bounded_attributes(self):
        exporter = self._exporter
        test_resource = resources.Resource(
            attributes={
                "svc": "demo",
                "num": 1,
            }
        )
        envelope = exporter._get_otel_resource_envelope(test_resource, None)

        # Ensure the envelope can be JSON serialized with the generated encoder
        serialized = json.dumps(envelope, cls=SdkJSONEncoder, exclude_readonly=True)
        self.assertIn("_OTELRESOURCE_", serialized)


class TestAzureTraceExporterUtils(unittest.TestCase):
    def test_get_trace_export_result(self):
        self.assertEqual(
            _get_trace_export_result(ExportResult.SUCCESS),
            SpanExportResult.SUCCESS,
        )
        self.assertEqual(
            _get_trace_export_result(ExportResult.FAILED_NOT_RETRYABLE),
            SpanExportResult.FAILURE,
        )
        self.assertEqual(
            _get_trace_export_result(ExportResult.FAILED_RETRYABLE),
            SpanExportResult.FAILURE,
        )
        self.assertEqual(
            _get_trace_export_result(None),
            SpanExportResult.FAILURE,
        )

    def test_check_instrumentation_span(self):
        span = mock.Mock()
        span.attributes = {}
        span.instrumentation_scope.name = "opentelemetry.instrumentation.test"
        with mock.patch("azure.monitor.opentelemetry.exporter._utils.add_instrumentation") as add:
            _check_instrumentation_span(span)
            add.assert_called_once_with("test")

    def test_check_instrumentation_span_not_instrumentation(self):
        span = mock.Mock()
        span.attributes = {}
        span.instrumentation_scope.name = "__main__"
        with mock.patch("azure.monitor.opentelemetry.exporter._utils.add_instrumentation") as add:
            _check_instrumentation_span(span)
            add.assert_not_called()

    def test_check_instrumentation_span_azure_sdk(self):
        span = mock.Mock()
        span.attributes = {}
        span.instrumentation_scope.name = "azure.foo.bar.__init__"

        with mock.patch("azure.monitor.opentelemetry.exporter._utils.add_instrumentation") as add:
            _check_instrumentation_span(span)
            add.assert_called_once_with(_AZURE_SDK_OPENTELEMETRY_NAME)

    @mock.patch("opentelemetry.trace.get_tracer_provider")
    def test_check_instrumentation_span_azure_sdk_otel_span(self, mock_get_tracer_provider):
        mock_get_tracer_provider.return_value = self.get_tracer_provider()

        with OpenTelemetrySpan() as azure_sdk_span:
            with mock.patch("azure.monitor.opentelemetry.exporter._utils.add_instrumentation") as add:
                _check_instrumentation_span(azure_sdk_span.span_instance)
                add.assert_called_once_with(_AZURE_SDK_OPENTELEMETRY_NAME)

            with mock.patch("azure.monitor.opentelemetry.exporter._utils.add_instrumentation") as add:
                azure_sdk_span.add_attribute(_AZURE_SDK_NAMESPACE_NAME, "Microsoft.ServiceBus")
                _check_instrumentation_span(azure_sdk_span.span_instance)
                add.assert_called_once_with(_AZURE_SDK_OPENTELEMETRY_NAME)

            with mock.patch("azure.monitor.opentelemetry.exporter._utils.add_instrumentation") as add:
                azure_sdk_span.add_attribute(_AZURE_SDK_NAMESPACE_NAME, "Microsoft.CognitiveServices")
                _check_instrumentation_span(azure_sdk_span.span_instance)
                add.assert_called_once_with(_AZURE_AI_SDK_NAME)

    @mock.patch("opentelemetry.trace.get_tracer_provider")
    def test_check_instrumentation_span_azure_sdk_span_impl(self, mock_get_tracer_provider):
        mock_get_tracer_provider.return_value = self.get_tracer_provider()

        settings.tracing_implementation = "opentelemetry"
        try:
            azure_sdk_span = settings.tracing_implementation()(name="test")

            with mock.patch("azure.monitor.opentelemetry.exporter._utils.add_instrumentation") as add:
                _check_instrumentation_span(azure_sdk_span.span_instance)
                add.assert_called_once_with(_AZURE_SDK_OPENTELEMETRY_NAME)

            with mock.patch("azure.monitor.opentelemetry.exporter._utils.add_instrumentation") as add:
                azure_sdk_span.add_attribute(_AZURE_SDK_NAMESPACE_NAME, "Microsoft.ServiceBus")
                _check_instrumentation_span(azure_sdk_span.span_instance)
                add.assert_called_once_with(_AZURE_SDK_OPENTELEMETRY_NAME)

            with mock.patch("azure.monitor.opentelemetry.exporter._utils.add_instrumentation") as add:
                azure_sdk_span.add_attribute(_AZURE_SDK_NAMESPACE_NAME, "Microsoft.CognitiveServices")
                _check_instrumentation_span(azure_sdk_span.span_instance)
                add.assert_called_once_with(_AZURE_AI_SDK_NAME)

        finally:
            settings.tracing_implementation = None

    @mock.patch("opentelemetry.trace.get_tracer_provider")
    def test_check_instrumentation_span_azure_sdk_get_tracer(self, mock_get_tracer_provider):
        mock_get_tracer_provider.return_value = self.get_tracer_provider()

        if not get_azure_sdk_tracer:
            self.skipTest("azure.core.instrumentation is not available")

        azure_sdk_tracer = get_azure_sdk_tracer(library_name="azure-foo-bar")
        azure_sdk_span = azure_sdk_tracer.start_span(name="test")

        with mock.patch("azure.monitor.opentelemetry.exporter._utils.add_instrumentation") as add:
            _check_instrumentation_span(azure_sdk_span)
            add.assert_called_once_with(_AZURE_SDK_OPENTELEMETRY_NAME)

        with mock.patch("azure.monitor.opentelemetry.exporter._utils.add_instrumentation") as add:
            azure_sdk_span.set_attribute(_AZURE_SDK_NAMESPACE_NAME, "Microsoft.ServiceBus")
            _check_instrumentation_span(azure_sdk_span)
            add.assert_called_once_with(_AZURE_SDK_OPENTELEMETRY_NAME)

        with mock.patch("azure.monitor.opentelemetry.exporter._utils.add_instrumentation") as add:
            azure_sdk_span.set_attribute(_AZURE_SDK_NAMESPACE_NAME, "Microsoft.CognitiveServices")
            _check_instrumentation_span(azure_sdk_span)
            add.assert_called_once_with(_AZURE_AI_SDK_NAME)

        other_tracer = self.get_tracer_provider().get_tracer("not-azure-foo-bar")
        other_span = other_tracer.start_span(name="test")
        with mock.patch("azure.monitor.opentelemetry.exporter._utils.add_instrumentation") as add:
            _check_instrumentation_span(other_span)
            add.assert_not_called()

    def get_tracer_provider(self):
        return trace.TracerProvider()


class _Response(HttpResponse):
    def __init__(self, request, status_code=200, headers=None):
        super().__init__(request, None)
        self.status_code = status_code
        self.headers = {"Content-Type": "application/json", **(headers or {})}
        self.content_type = "application/json"
        count = len(json.loads(request.body))
        self._body = json.dumps({"itemsReceived": count, "itemsAccepted": count, "errors": []}).encode()

    def body(self):
        return self._body

    def json(self):
        return json.loads(self._body)


class TestMultiEndpointRouting(unittest.TestCase):
    def setUp(self):
        environment = mock.patch.dict(
            os.environ,
            {
                "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
                "APPLICATIONINSIGHTS_SDKSTATS_DISABLED": "true",
                "APPLICATIONINSIGHTS_CONTROLPLANE_DISABLED": "true",
                "APPLICATIONINSIGHTS_EXPERIMENTAL_FEATURES": "multi_endpoint_routing",
                "APPLICATIONINSIGHTS_OPENTELEMETRY_RESOURCE_METRIC_DISABLED": "true",
            },
        )
        environment.start()
        self.addCleanup(environment.stop)
        features = mock.patch("azure.monitor.opentelemetry.exporter.export._base._enabled_experimental_features", None)
        features.start()
        self.addCleanup(features.stop)
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.transport = mock.MagicMock(spec=HttpTransport)
        self.transport.close.return_value = None
        self.transport.__exit__.side_effect = lambda *args: self.transport.close()
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request)

    def _exporter(self, *, routing=True, **kwargs):
        options = {
            "connection_string": "InstrumentationKey=1234abcd-5678-4efa-8abc-1234567890ab;"
            "IngestionEndpoint=https://host.example/",
            "disable_offline_storage": True,
            "storage_directory": str(Path(self.directory.name) / "host"),
            "transport": self.transport,
            "retry_total": 0,
        }
        options.update(kwargs)
        with mock.patch.dict(
            os.environ, {"APPLICATIONINSIGHTS_EXPERIMENTAL_FEATURES": "multi_endpoint_routing" if routing else ""}
        ), mock.patch("azure.monitor.opentelemetry.exporter.export._base._enabled_experimental_features", None):
            exporter = AzureMonitorTraceExporter(**options)
        self.addCleanup(exporter.client.close)
        self.addCleanup(exporter.shutdown)
        return exporter

    def _span(
        self,
        endpoint="https://one.example/proxy/",
        key="customer-key",
        auth="ikey",
        kind=SpanKind.CLIENT,
        cloud_role="not-the-resource-role",
    ):
        return ReadableSpan(
            name="operation",
            context=SpanContext(trace_id=1, span_id=2, is_remote=False),
            kind=kind,
            start_time=1,
            end_time=2,
            attributes={
                "microsoft.instrumentation_key": key,
                "microsoft.ingestion_endpoint": endpoint,
                "microsoft.ingestion_auth": auth,
                "microsoft.multi_endpoint_cloud_role": cloud_role,
                "custom": "span-value",
            },
            resource=Resource({"service.name": "resource-role", "service.instance.id": "resource-instance"}),
            events=(
                Event("message", attributes={"custom": "event-value"}),
                Event(
                    "exception",
                    attributes={
                        "microsoft.instrumentation_key": "event-key",
                        "microsoft.ingestion_endpoint": "https://event.example/",
                        "microsoft.ingestion_auth": "aad",
                        "microsoft.multi_endpoint_cloud_role": "event-role",
                        "custom": "exception-value",
                    },
                ),
            ),
        )

    def test_grouping_and_events_follow_parent_route(self):
        exporter = self._exporter()
        spans = [
            self._span(key=" key-one ", kind=SpanKind.SERVER),
            self._span(endpoint="https://two.example/", key="key-two"),
            self._span(endpoint="HTTPS://ONE.EXAMPLE:443/proxy", key="key-three"),
        ]
        self.assertEqual(exporter.export(spans), SpanExportResult.SUCCESS)
        requests = [call.args[0] for call in self.transport.send.call_args_list]
        self.assertEqual(len(requests), 2)
        self.assertTrue(requests[0].url.startswith("https://one.example/proxy/"))
        self.assertTrue(requests[1].url.startswith("https://two.example/"))
        first = json.loads(requests[0].body)
        self.assertEqual([item["iKey"] for item in first], ["key-one"] * 3 + ["key-three"] * 3)
        self.assertEqual(
            [item["data"]["baseType"] for item in first],
            ["RequestData", "MessageData", "ExceptionData", "RemoteDependencyData", "MessageData", "ExceptionData"],
        )
        self.assertEqual([item["iKey"] for item in json.loads(requests[1].body)], ["key-two"] * 3)
        for request in requests:
            for item in json.loads(request.body):
                self.assertEqual(item["tags"]["ai.cloud.role"], "not-the-resource-role")
                self.assertEqual(item["tags"]["ai.cloud.roleInstance"], "resource-instance")
                self.assertEqual(item["tags"]["ai.operation.id"], "{:032x}".format(1))
                properties = item["data"]["baseData"]["properties"]
                for attribute in _MULTI_ENDPOINT_ROUTING_ATTRIBUTES:
                    self.assertNotIn(attribute, properties)
                self.assertIn(properties["custom"], ("span-value", "event-value", "exception-value"))
        self.assertEqual(spans[0].attributes["microsoft.instrumentation_key"], " key-one ")
        self.assertEqual(spans[0].events[1].attributes["microsoft.instrumentation_key"], "event-key")

    def test_single_connection_string_is_unchanged(self):
        exporter = self._exporter(routing=False)
        self.assertEqual(
            exporter.export([self._span(), self._span(endpoint="https://two.example/")]), SpanExportResult.SUCCESS
        )
        self.transport.send.assert_called_once()
        request = self.transport.send.call_args.args[0]
        self.assertTrue(request.url.startswith("https://host.example/"))
        items = json.loads(request.body)
        self.assertEqual([item["iKey"] for item in items], ["1234abcd-5678-4efa-8abc-1234567890ab"] * 6)
        self.assertEqual([item["tags"]["ai.cloud.role"] for item in items], ["resource-role"] * 6)
        self.assertEqual(items[0]["data"]["baseData"]["properties"]["microsoft.instrumentation_key"], "customer-key")
        self.assertEqual(items[2]["data"]["baseData"]["properties"]["microsoft.instrumentation_key"], "event-key")

    def test_missing_and_invalid_cloud_roles_use_unknown_service(self):
        exporter = self._exporter()
        spans = [self._span(cloud_role=value) for value in (None, " \t\n", 42)]
        self.assertEqual(exporter.export(spans), SpanExportResult.SUCCESS)
        items = json.loads(self.transport.send.call_args.args[0].body)
        self.assertEqual([item["tags"]["ai.cloud.role"] for item in items], ["unknown_service"] * 9)
        self.assertEqual([item["tags"]["ai.cloud.roleInstance"] for item in items], ["resource-instance"] * 9)

    def test_empty_and_invalid_batches_do_not_transmit(self):
        exporter = self._exporter()
        for spans in ([], [self._span(key=" ")], [self._span(endpoint="http://invalid.example/")]):
            with self.subTest(spans=spans):
                self.assertEqual(exporter.export(spans), SpanExportResult.SUCCESS)
        self.transport.send.assert_not_called()

    @mock.patch.dict(os.environ)
    def test_routing_without_host_connection_string(self):
        os.environ.pop("APPLICATIONINSIGHTS_CONNECTION_STRING", None)
        os.environ.pop("APPINSIGHTS_INSTRUMENTATIONKEY", None)
        exporter = self._exporter(connection_string=None)
        self.assertIsNone(exporter.application_id)
        os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"] = "invalid"
        self.assertEqual(exporter.export([self._span()]), SpanExportResult.SUCCESS)
        request = self.transport.send.call_args.args[0]
        self.assertTrue(request.url.startswith("https://one.example/proxy/"))
        self.assertEqual([item["iKey"] for item in json.loads(request.body)], ["customer-key"] * 3)

    def test_configured_application_id_is_preserved(self):
        exporter = self._exporter(
            connection_string="InstrumentationKey=1234abcd-5678-4efa-8abc-1234567890ab;ApplicationId=host-app"
        )
        self.assertEqual(exporter.application_id, "host-app")

    def test_authentication_groups_include_parent_events(self):
        credential = mock.Mock(spec=["get_token"])
        credential.get_token.return_value = AccessToken("test-token", int(time_module.time()) + 3600)
        exporter = self._exporter(credential=credential)
        spans = [self._span(), self._span(auth=" AAD ")]
        for _ in range(2):
            self.assertEqual(exporter.export(spans), SpanExportResult.SUCCESS)
        requests = [call.args[0] for call in self.transport.send.call_args_list]
        self.assertEqual(len(requests), 4)
        for request in requests[::2]:
            self.assertNotIn("Authorization", request.headers)
        for request in requests[1::2]:
            self.assertEqual(request.headers["Authorization"], f"Bearer {credential.get_token.return_value.token}")
        self.assertTrue(all(len(json.loads(request.body)) == 3 for request in requests))
        credential.get_token.assert_called_once()

    def test_missing_aad_credential_does_not_block_other_routes(self):
        exporter = self._exporter(credential=None)
        with self.assertLogs("azure.monitor.opentelemetry.exporter.export._base", level="ERROR"):
            result = exporter.export([self._span(auth="aad"), self._span(endpoint="https://two.example/")])
        self.assertEqual(result, SpanExportResult.FAILURE)
        self.transport.send.assert_called_once()
        self.assertTrue(self.transport.send.call_args.args[0].url.startswith("https://two.example/"))

    def test_retry_storage_preserves_parent_route_and_event_keys(self):
        now = datetime_module.datetime(2026, 10, 20, tzinfo=datetime_module.timezone.utc)
        exporter = self._exporter(disable_offline_storage=False)
        self.transport.send.side_effect = lambda request, **kwargs: _Response(
            request, 429 if request.url.startswith("https://one.example/") else 200, {"Retry-After": "60"}
        )
        with mock.patch("azure.monitor.opentelemetry.exporter._storage._now", return_value=now):
            result = exporter.export([self._span(key="old-key"), self._span(endpoint="https://two.example/")])
        self.assertEqual(result, SpanExportResult.FAILURE)
        self.assertEqual(self.transport.send.call_count, 2)
        exporter.shutdown()
        restarted = self._exporter(disable_offline_storage=False)
        self.transport.send.reset_mock()
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request)
        with mock.patch(
            "azure.monitor.opentelemetry.exporter._storage._now",
            return_value=now + datetime_module.timedelta(seconds=61),
        ):
            self.assertEqual(restarted.export([self._span(key="new-key")]), SpanExportResult.SUCCESS)
        requests = [call.args[0] for call in self.transport.send.call_args_list]
        self.assertEqual(len(requests), 2)
        self.assertEqual(
            [[item["iKey"] for item in json.loads(request.body)] for request in requests],
            [["new-key"] * 3, ["old-key"] * 3],
        )
        self.assertTrue(all(request.url.startswith("https://one.example/proxy/") for request in requests))
        self.assertFalse(list((Path(self.directory.name) / "host").iterdir()))

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.time.monotonic", return_value=100)
    def test_backoff_defers_spans_and_events(self, clock):
        exporter = self._exporter(disable_offline_storage=False)
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request, 429, {"Retry-After": "60"})
        self.assertEqual(exporter.export([self._span()]), SpanExportResult.FAILURE)
        self.transport.send.reset_mock()
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request)
        self.assertEqual(exporter.export([self._span(key="deferred")]), SpanExportResult.FAILURE)
        self.transport.send.assert_not_called()
        clock.return_value = 160
        self.assertEqual(exporter.export([self._span(key="new")]), SpanExportResult.SUCCESS)
        self.transport.send.assert_called_once()
        self.assertEqual([item["iKey"] for item in json.loads(self.transport.send.call_args.args[0].body)], ["new"] * 3)

    def test_shutdown_closes_routes_and_rejects_later_exports(self):
        exporter = self._exporter(disable_offline_storage=False)
        self.assertEqual(exporter.export([self._span()]), SpanExportResult.SUCCESS)
        exporter.shutdown()
        closes = self.transport.close.call_count
        self.assertEqual(closes, 2)
        exporter.shutdown()
        self.assertEqual(self.transport.close.call_count, closes)
        self.transport.send.reset_mock()
        with self.assertLogs("azure.monitor.opentelemetry.exporter.export._base", level="ERROR"):
            self.assertEqual(exporter.export([self._span()]), SpanExportResult.FAILURE)
        self.transport.send.assert_not_called()

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.time.monotonic", return_value=100)
    def test_background_retry_sends_span_and_events_without_new_exports(self, clock):
        now = datetime_module.datetime(2026, 10, 20, tzinfo=datetime_module.timezone.utc)
        exporter = self._exporter(disable_offline_storage=False)
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request, 429, {"Retry-After": "60"})
        with mock.patch("azure.monitor.opentelemetry.exporter._storage._now", return_value=now):
            self.assertEqual(exporter.export([self._span(key="original")]), SpanExportResult.FAILURE)
        self.transport.send.reset_mock()
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request)
        clock.return_value = 161
        with mock.patch(
            "azure.monitor.opentelemetry.exporter._storage._now",
            return_value=now + datetime_module.timedelta(seconds=61),
        ):
            exporter._route_retry_task.function()
        self.transport.send.assert_called_once()
        items = json.loads(self.transport.send.call_args.args[0].body)
        self.assertEqual([item["iKey"] for item in items], ["original"] * 3)
        self.assertEqual(
            [item["data"]["baseType"] for item in items], ["RemoteDependencyData", "MessageData", "ExceptionData"]
        )

    def test_routed_export_exception_is_reported(self):
        exporter = self._exporter()
        with mock.patch.object(exporter, "_transmit_routed", side_effect=RuntimeError("test failure")):
            with self.assertLogs("azure.monitor.opentelemetry.exporter.export.trace._exporter", level="ERROR") as logs:
                self.assertEqual(exporter.export([self._span()]), SpanExportResult.FAILURE)
        self.assertIn("test failure", logs.output[0])
