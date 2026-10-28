# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import datetime
import json
import os
import platform
import shutil
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock
from functools import partial

# pylint: disable=import-error
from opentelemetry.context import _SUPPRESS_INSTRUMENTATION_KEY, get_value
from opentelemetry.semconv.attributes.exception_attributes import (
    EXCEPTION_MESSAGE,
    EXCEPTION_STACKTRACE,
    EXCEPTION_TYPE,
)
from opentelemetry.semconv._incubating.attributes import session_attributes
from opentelemetry.sdk import _logs
from opentelemetry.sdk._logs import ReadWriteLogRecord
from opentelemetry._logs import LogRecord
from opentelemetry.sdk.util.instrumentation import InstrumentationScope
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk._logs.export import LogRecordExportResult
from opentelemetry._logs.severity import SeverityNumber
from opentelemetry.trace import set_span_in_context, SpanContext, NonRecordingSpan

from azure.monitor.opentelemetry.exporter.export._base import ExportResult
from azure.core.credentials import AccessToken
from azure.core.exceptions import ServiceRequestError
from azure.core.pipeline.transport import HttpResponse, HttpTransport
from azure.monitor.opentelemetry.exporter.export.logs._exporter import (
    AzureMonitorLogExporter,
    _get_log_export_result,
    _get_severity_level,
)
from azure.monitor.opentelemetry.exporter._constants import (
    _APPLICATION_INSIGHTS_EVENT_MARKER_ATTRIBUTE,
    _MICROSOFT_AVAILABILITY_DURATION,
    _MICROSOFT_AVAILABILITY_ID,
    _MICROSOFT_AVAILABILITY_MESSAGE,
    _MICROSOFT_AVAILABILITY_NAME,
    _MICROSOFT_AVAILABILITY_RUN_LOCATION,
    _MICROSOFT_AVAILABILITY_SUCCESS,
    _MICROSOFT_CUSTOM_EVENT_NAME,
    _MICROSOFT_CUSTOM_MEASUREMENTS,
    _DEFAULT_LOG_MESSAGE,
    _APPLICATION_ID_RESOURCE_KEY,
    _ONE_SETTINGS_FEATURE_LOCAL_STORAGE,
)
from azure.monitor.opentelemetry.exporter._generated.exporter.models import ContextTagKeys
from azure.monitor.opentelemetry.exporter._utils import azure_monitor_context


def ns_to_datetime(ns: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(ns / 1e9, tz=datetime.timezone.utc)


def throw(exc_type, *args, **kwargs):
    def func(*_args, **_kwargs):
        raise exc_type(*args, **kwargs)

    return func


class NotSerializeableClass:
    def __str__(self) -> str:
        return "This class is not serializeable"


# pylint: disable=import-error
# pylint: disable=protected-access, too-many-public-methods
# pylint: disable=too-many-lines, line-too-long
class TestAzureLogExporter(unittest.TestCase):
    _exporter_class = AzureMonitorLogExporter

    @classmethod
    def setUpClass(cls):
        os.environ.pop("APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL", None)
        os.environ.pop("APPLICATIONINSIGHTS_CONNECTION_STRING", None)
        os.environ.pop("APPINSIGHTS_INSTRUMENTATIONKEY", None)
        os.environ["APPINSIGHTS_INSTRUMENTATIONKEY"] = "1234abcd-5678-4efa-8abc-1234567890ab"
        os.environ["APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL"] = "true"
        cls._exporter = cls._exporter_class()
        span_context = SpanContext(
            trace_id=125960616039069540489478540494783893221,
            span_id=2909973987304607650,
            trace_flags=None,
            is_remote=False,
        )
        span = NonRecordingSpan(span_context)
        ctx = set_span_in_context(span)
        cls._log_data = _logs.ReadWriteLogRecord(
            LogRecord(
                timestamp=1646865018558419456,
                context=ctx,
                severity_text="WARNING",
                severity_number=SeverityNumber.WARN,
                body="Test message",
                attributes={
                    "test": "attribute",
                    "ai.operation.name": "TestOperationName",
                },
            ),
            resource=Resource.create(attributes={"asd": "test_resource"}),
            instrumentation_scope=InstrumentationScope("test_name"),
        )
        cls._log_data_user_fields = _logs.ReadWriteLogRecord(
            LogRecord(
                timestamp=1646865018558419456,
                context=ctx,
                severity_text="WARNING",
                severity_number=SeverityNumber.WARN,
                body="Test message",
                attributes={
                    "test": "attribute",
                    "enduser.id": "test-auth",
                    "enduser.pseudo.id": "test-user",
                    session_attributes.SESSION_ID: "test-session",
                },
            ),
            resource=Resource.create(attributes={"asd": "test_resource"}),
            instrumentation_scope=InstrumentationScope("test_name"),
        )
        cls._log_data_empty = _logs.ReadWriteLogRecord(
            LogRecord(
                timestamp=1646865018558419456,
                context=ctx,
                severity_text="WARNING",
                severity_number=SeverityNumber.WARN,
                body="",
                attributes={
                    "test": "attribute",
                    "ai.operation.name": "TestOperationName",
                },
            ),
            resource=Resource.create(attributes={"asd": "test_resource"}),
            instrumentation_scope=InstrumentationScope("test_name"),
        )
        cls._log_data_none = _logs.ReadWriteLogRecord(
            LogRecord(
                timestamp=1646865018558419456,
                context=ctx,
                severity_text="WARNING",
                severity_number=SeverityNumber.WARN,
                body=None,
                attributes={"test": "attribute"},
            ),
            resource=Resource.create(attributes={"asd": "test_resource", "microsoft.applicationId": "app_id"}),
            instrumentation_scope=InstrumentationScope("test_name"),
        )
        cls._log_data_complex_body = _logs.ReadWriteLogRecord(
            LogRecord(
                timestamp=1646865018558419456,
                context=ctx,
                severity_text="WARNING",
                severity_number=SeverityNumber.WARN,
                body={"foo": {"bar": "baz", "qux": 42}},
                attributes={
                    "test": "attribute",
                    "ai.operation.name": "TestOperationName",
                },
            ),
            resource=Resource.create(attributes={"asd": "test_resource"}),
            instrumentation_scope=InstrumentationScope("test_name"),
        )
        cls._log_data_complex_body_not_serializeable = _logs.ReadWriteLogRecord(
            LogRecord(
                timestamp=1646865018558419456,
                context=ctx,
                severity_text="WARNING",
                severity_number=SeverityNumber.WARN,
                body=NotSerializeableClass(),
                attributes={"test": "attribute"},
            ),
            resource=Resource.create(attributes={"asd": "test_resource"}),
            instrumentation_scope=InstrumentationScope("test_name"),
        )
        cls._log_data_empty_with_whitespaces = _logs.ReadWriteLogRecord(
            LogRecord(
                timestamp=1646865018558419456,
                context=ctx,
                severity_text="WARNING",
                severity_number=SeverityNumber.WARN,
                body="  ",
                attributes={"test": "attribute"},
            ),
            resource=Resource.create(attributes={"asd": "test_resource"}),
            instrumentation_scope=InstrumentationScope("test_name"),
        )
        cls._log_data_event = _logs.ReadWriteLogRecord(
            LogRecord(
                timestamp=1646865018558419456,
                context=ctx,
                severity_text="INFO",
                severity_number=SeverityNumber.INFO,
                body="Test Event",
                attributes={
                    "event_key": "event_attribute",
                    _APPLICATION_INSIGHTS_EVENT_MARKER_ATTRIBUTE: True,
                },
            ),
            resource=Resource.create(attributes={"asd": "test_resource"}),
            instrumentation_scope=InstrumentationScope("test_name"),
        )
        cls._log_data_event_complex_body = _logs.ReadWriteLogRecord(
            LogRecord(
                timestamp=1646865018558419456,
                context=ctx,
                severity_text="INFO",
                severity_number=SeverityNumber.INFO,
                body={"foo": {"bar": "baz", "qux": 42}},
                attributes={
                    "event_key": "event_attribute",
                    _APPLICATION_INSIGHTS_EVENT_MARKER_ATTRIBUTE: True,
                },
            ),
            resource=Resource.create(attributes={"asd": "test_resource"}),
            instrumentation_scope=InstrumentationScope("test_name"),
        )
        cls._log_data_event_complex_body_not_serializeable = _logs.ReadWriteLogRecord(
            LogRecord(
                timestamp=1646865018558419456,
                severity_text="INFO",
                severity_number=SeverityNumber.INFO,
                body=NotSerializeableClass(),
                attributes={
                    "event_key": "event_attribute",
                    _APPLICATION_INSIGHTS_EVENT_MARKER_ATTRIBUTE: True,
                },
            ),
            resource=Resource.create(attributes={"asd": "test_resource"}),
            instrumentation_scope=InstrumentationScope("test_name"),
        )
        cls._log_data_custom_event = _logs.ReadWriteLogRecord(
            LogRecord(
                timestamp=1646865018558419456,
                context=ctx,
                severity_text="INFO",
                severity_number=SeverityNumber.INFO,
                body="Test Event",
                attributes={
                    "event_key": "event_attribute",
                    _MICROSOFT_CUSTOM_EVENT_NAME: "event_name",
                    "client.address": "192.168.1.1",
                },
            ),
            resource=Resource.create(attributes={"asd": "test_resource"}),
            instrumentation_scope=InstrumentationScope("custom-event-logger"),
        )
        cls._exc_data = _logs.ReadWriteLogRecord(
            LogRecord(
                timestamp=1646865018558419456,
                context=ctx,
                severity_text="EXCEPTION",
                severity_number=SeverityNumber.FATAL,
                body="Test message",
                attributes={
                    "test": "attribute",
                    EXCEPTION_TYPE: "ZeroDivisionError",
                    EXCEPTION_MESSAGE: "division by zero",
                    EXCEPTION_STACKTRACE: 'Traceback (most recent call last):\n  File "test.py", line 38, in <module>\n    raise ZeroDivisionError()\nZeroDivisionError\n',
                },
            ),
            resource=Resource.create(attributes={"asd": "test_resource"}),
            instrumentation_scope=InstrumentationScope("test_name"),
        )
        cls._exc_data_with_exc_body = _logs.ReadWriteLogRecord(
            LogRecord(
                timestamp=1646865018558419456,
                context=ctx,
                severity_text="EXCEPTION",
                severity_number=SeverityNumber.FATAL,
                body=Exception("test exception message"),
                attributes={
                    "test": "attribute",
                    EXCEPTION_TYPE: "ZeroDivisionError",
                    EXCEPTION_MESSAGE: "division by zero",
                    EXCEPTION_STACKTRACE: 'Traceback (most recent call last):\n  File "test.py", line 38, in <module>\n    raise ZeroDivisionError()\nZeroDivisionError\n',
                },
            ),
            resource=Resource.create(attributes={"asd": "test_resource"}),
            instrumentation_scope=InstrumentationScope("test_name"),
        )
        cls._exc_data_blank_exception = _logs.ReadWriteLogRecord(
            LogRecord(
                timestamp=1646865018558419456,
                context=ctx,
                severity_text="EXCEPTION",
                severity_number=SeverityNumber.FATAL,
                body="test exception",
                attributes={
                    "test": "attribute",
                    EXCEPTION_TYPE: "",
                    EXCEPTION_MESSAGE: "",
                    EXCEPTION_STACKTRACE: "",
                },
            ),
            resource=Resource.create(attributes={"asd": "test_resource"}),
            instrumentation_scope=InstrumentationScope("blank_exception_logger"),
        )
        cls._exc_data_empty = _logs.ReadWriteLogRecord(
            LogRecord(
                timestamp=1646865018558419456,
                context=ctx,
                severity_text="EXCEPTION",
                severity_number=SeverityNumber.FATAL,
                body="",
                attributes={
                    "test": "attribute",
                    EXCEPTION_TYPE: "",
                    EXCEPTION_MESSAGE: "",
                    EXCEPTION_STACKTRACE: "",
                },
            ),
            resource=Resource.create(attributes={"asd": "test_resource"}),
            instrumentation_scope=InstrumentationScope("test_name"),
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._exporter.storage._path, True)

    def test_constructor(self):
        """Test the constructor."""
        exporter = AzureMonitorLogExporter(
            connection_string="InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab",
        )
        self.assertEqual(
            exporter._instrumentation_key,
            "4321abcd-5678-4efa-8abc-1234567890ab",
        )
        self.assertIsNotNone(exporter.storage)

    def test_from_connection_string(self):
        exporter = AzureMonitorLogExporter.from_connection_string(
            "InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab"
        )
        self.assertTrue(isinstance(exporter, AzureMonitorLogExporter))
        self.assertEqual(
            exporter._instrumentation_key,
            "4321abcd-5678-4efa-8abc-1234567890ab",
        )

    def test_export_empty(self):
        exporter = self._exporter
        result = exporter.export([])
        self.assertEqual(result, LogRecordExportResult.SUCCESS)

    def test_export_failure(self):
        exporter = self._exporter
        with mock.patch(
            "azure.monitor.opentelemetry.exporter.AzureMonitorLogExporter._transmit"
        ) as transmit:  # noqa: E501
            transmit.return_value = ExportResult.FAILED_RETRYABLE
            storage_mock = mock.Mock()
            exporter.storage.put = storage_mock
            result = exporter.export([self._log_data])
        self.assertEqual(result, LogRecordExportResult.FAILURE)
        self.assertEqual(storage_mock.call_count, 1)

    def test_export_success(self):
        exporter = self._exporter
        with mock.patch(
            "azure.monitor.opentelemetry.exporter.AzureMonitorLogExporter._transmit"
        ) as transmit:  # noqa: E501
            transmit.return_value = ExportResult.SUCCESS
            storage_mock = mock.Mock()
            exporter._transmit_from_storage = storage_mock
            result = exporter.export([self._log_data])
            self.assertEqual(result, LogRecordExportResult.SUCCESS)
            self.assertEqual(storage_mock.call_count, 1)

    def test_export_routing_attributes(self):
        attributes = {
            "microsoft.instrumentation_key": "customer-key",
            "microsoft.ingestion_endpoint": "https://example.com/",
            "microsoft.multi_endpoint_cloud_role": "customer-service",
            "microsoft.ingestion_auth": "ikey",
            "custom": "value",
            "microsoft.custom": "preserved",
        }
        record = _logs.ReadWriteLogRecord(
            LogRecord(body="message", attributes=attributes.copy()), resource=Resource({})
        )
        for routing in (False, True):
            with self.subTest(routing=routing):
                with mock.patch.dict(
                    os.environ,
                    {"APPLICATIONINSIGHTS_EXPERIMENTAL_FEATURES": "multi_endpoint_routing" if routing else ""},
                ), mock.patch("azure.monitor.opentelemetry.exporter.export._base._enabled_experimental_features", None):
                    exporter = type(self)._exporter_class(disable_offline_storage=True)
                self.addCleanup(exporter.client.close)
                self.addCleanup(exporter.shutdown)
                with mock.patch(
                    "azure.monitor.opentelemetry.exporter.export._base.BaseExporter._transmit",
                    return_value=ExportResult.SUCCESS,
                ) as transmit:
                    self.assertEqual(exporter.export([record]), LogRecordExportResult.SUCCESS)
                transmit.assert_called_once()
                envelopes = transmit.call_args.args[0]
                self.assertEqual(len(envelopes), 1)
                self.assertEqual(envelopes[0].data.base_type, "MessageData")
                properties = envelopes[0].data.base_data.properties
                self.assertEqual(properties["custom"], "value")
                self.assertEqual(properties["microsoft.custom"], "preserved")
                if routing:
                    self.assertNotIn("microsoft.instrumentation_key", properties)
                    self.assertNotIn("microsoft.ingestion_endpoint", properties)
                    self.assertNotIn("microsoft.multi_endpoint_cloud_role", properties)
                    self.assertNotIn("microsoft.ingestion_auth", properties)
                else:
                    self.assertEqual(properties, attributes)
                self.assertEqual(record.log_record.attributes, attributes)

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
            {**valid, "microsoft.ingestion_endpoint": ["https://example.com/"]},
        )
        for routing in (False, True):
            with mock.patch.dict(
                os.environ, {"APPLICATIONINSIGHTS_EXPERIMENTAL_FEATURES": "multi_endpoint_routing" if routing else ""}
            ), mock.patch("azure.monitor.opentelemetry.exporter.export._base._enabled_experimental_features", None):
                exporter = type(self)._exporter_class(disable_offline_storage=True)
            self.addCleanup(exporter.client.close)
            self.addCleanup(exporter.shutdown)
            for attributes in ([valid, *invalid, valid], invalid):
                with self.subTest(routing=routing, attributes=attributes):
                    records = [
                        _logs.ReadWriteLogRecord(LogRecord(body=str(index), attributes=item), resource=Resource({}))
                        for index, item in enumerate(attributes)
                    ]
                    with mock.patch(
                        "azure.monitor.opentelemetry.exporter.export._base.BaseExporter._transmit",
                        return_value=ExportResult.SUCCESS,
                    ) as transmit:
                        self.assertEqual(exporter.export(records), LogRecordExportResult.SUCCESS)
                    expected = sum(item == valid for item in attributes) if routing else len(attributes)
                    if expected or not routing:
                        transmit.assert_called_once()
                        envelopes = transmit.call_args.args[0]
                    else:
                        transmit.assert_not_called()
                        envelopes = []
                    self.assertEqual(len(envelopes), expected)
                    self.assertEqual(
                        [envelope.data.base_data.message for envelope in envelopes],
                        [str(index) for index, item in enumerate(attributes) if not routing or item == valid],
                    )

    @mock.patch("azure.monitor.opentelemetry.exporter.export.logs._exporter._logger")
    def test_export_exception(self, logger_mock):
        exporter = self._exporter
        with mock.patch(
            "azure.monitor.opentelemetry.exporter.AzureMonitorLogExporter._transmit",
            throw(Exception),
        ):  # noqa: E501
            result = exporter.export([self._log_data])
            self.assertEqual(result, LogRecordExportResult.FAILURE)
            self.assertEqual(logger_mock.exception.called, True)

    def test_export_not_retryable(self):
        exporter = self._exporter
        with mock.patch(
            "azure.monitor.opentelemetry.exporter.AzureMonitorLogExporter._transmit"
        ) as transmit:  # noqa: E501
            transmit.return_value = ExportResult.FAILED_NOT_RETRYABLE
            result = exporter.export([self._log_data])
            self.assertEqual(result, LogRecordExportResult.FAILURE)

    def test_log_to_envelope_partA(self):
        exporter = self._exporter
        old_resource = self._log_data.resource
        resource = Resource(
            {
                "service.name": "testServiceName",
                "service.namespace": "testServiceNamespace",
                "service.instance.id": "testServiceInstanceId",
            }
        )
        self._log_data.resource = resource
        envelope = exporter._log_to_envelope(self._log_data)

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
        trace_id = self._log_data.log_record.trace_id
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_OPERATION_ID),
            "{:032x}".format(trace_id),
        )
        span_id = self._log_data.log_record.span_id
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_OPERATION_PARENT_ID),
            "{:016x}".format(span_id),
        )
        self._log_data.resource = old_resource
        self.assertEqual(envelope.tags.get(ContextTagKeys.AI_OPERATION_NAME), "TestOperationName")

    def test_log_to_envelope_gen_ai_messages_attributes_length(self):
        exporter = self._exporter
        messages_length = 1024 * 1024
        messages_value = "m" * messages_length
        oversized_messages_value = "o" * (4 * 1024 * 1024 + 1000)
        other_value = "t" * (1024 * 1024)
        log_data = _logs.ReadWriteLogRecord(
            LogRecord(
                timestamp=1646865018558419456,
                severity_text="INFO",
                severity_number=SeverityNumber.INFO,
                body="gen_ai event",
                attributes={
                    "gen_ai.input.messages": messages_value,
                    "gen_ai.output.messages": oversized_messages_value,
                    "gen_ai.system_instructions": other_value,
                    "custom.attribute": other_value,
                },
            ),
            resource=Resource.create(attributes={"asd": "test_resource"}),
            instrumentation_scope=InstrumentationScope("test_name"),
        )
        # Without the experimental feature, existing truncation limits apply
        envelope = exporter._log_to_envelope(log_data)

        properties = envelope.data.base_data.properties
        self.assertEqual(len(properties["gen_ai.input.messages"]), 256 * 1024)
        self.assertEqual(len(properties["gen_ai.output.messages"]), 256 * 1024)
        self.assertEqual(len(properties["gen_ai.system_instructions"]), 256 * 1024)
        self.assertEqual(len(properties["custom.attribute"]), 8 * 1024)

        with mock.patch(
            "azure.monitor.opentelemetry.exporter.export._base._enabled_experimental_features",
            frozenset({"gen_ai_input_output_limit_increase"}),
        ):
            envelope = exporter._log_to_envelope(log_data)

        properties = envelope.data.base_data.properties
        self.assertEqual(properties["gen_ai.input.messages"], messages_value)
        self.assertEqual(len(properties["gen_ai.output.messages"]), 4 * 1024 * 1024)
        self.assertEqual(len(properties["gen_ai.system_instructions"]), 256 * 1024)
        self.assertEqual(len(properties["custom.attribute"]), 8 * 1024)

    def test_log_to_envelope_partA_default(self):
        exporter = self._exporter
        old_resource = self._log_data.resource
        resource = Resource({"service.name": "testServiceName"})
        self._log_data.resource = resource
        envelope = exporter._log_to_envelope(self._log_data)
        self.assertEqual(envelope.tags.get(ContextTagKeys.AI_CLOUD_ROLE), "testServiceName")
        self.assertEqual(envelope.tags.get(ContextTagKeys.AI_CLOUD_ROLE_INSTANCE), platform.node())
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_INTERNAL_NODE_NAME),
            envelope.tags.get(ContextTagKeys.AI_CLOUD_ROLE_INSTANCE),
        )
        self._log_data.resource = old_resource

    def test_log_to_envelope_log(self):
        exporter = self._exporter
        envelope = exporter._log_to_envelope(self._log_data)
        record = self._log_data.log_record
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Message")
        self.assertEqual(envelope.time, ns_to_datetime(record.timestamp))
        self.assertEqual(envelope.data.base_type, "MessageData")
        self.assertEqual(envelope.data.base_data.message, record.body)
        self.assertEqual(envelope.data.base_data.severity_level, 2)
        self.assertEqual(envelope.data.base_data.properties["test"], "attribute")

    def test_log_to_envelope_user_fields(self):
        exporter = self._exporter
        envelope = exporter._log_to_envelope(self._log_data_user_fields)

        self.assertEqual(envelope.tags.get(ContextTagKeys.AI_USER_AUTH_USER_ID), "test-auth")
        self.assertEqual(envelope.tags.get(ContextTagKeys.AI_USER_ID), "test-user")
        self.assertEqual(envelope.tags.get(ContextTagKeys.AI_SESSION_ID), "test-session")
        self.assertNotIn("enduser.id", envelope.data.base_data.properties)
        self.assertNotIn("enduser.pseudo.id", envelope.data.base_data.properties)
        self.assertNotIn(session_attributes.SESSION_ID, envelope.data.base_data.properties)
        self.assertEqual(envelope.data.base_data.properties.get("logger_name"), "test_name")

    def test_log_to_envelope_log_none(self):
        exporter = self._exporter
        envelope = exporter._log_to_envelope(self._log_data_none)
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Message")
        self.assertEqual(envelope.data.base_type, "MessageData")
        self.assertEqual(envelope.data.base_data.message, _DEFAULT_LOG_MESSAGE)
        self.assertEqual(envelope.data.base_data.properties.get(_APPLICATION_ID_RESOURCE_KEY), None)

    def test_log_to_envelope_log_empty(self):
        exporter = self._exporter
        envelope = exporter._log_to_envelope(self._log_data_empty)
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Message")
        self.assertEqual(envelope.data.base_type, "MessageData")
        self.assertEqual(envelope.data.base_data.message, _DEFAULT_LOG_MESSAGE)
        self.assertEqual(envelope.tags.get(ContextTagKeys.AI_OPERATION_NAME), "TestOperationName")

    def test_log_to_envelope_log_empty_with_whitespaces(self):
        exporter = self._exporter
        envelope = exporter._log_to_envelope(self._log_data_empty_with_whitespaces)
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Message")
        self.assertEqual(envelope.data.base_type, "MessageData")
        self.assertEqual(envelope.data.base_data.message, _DEFAULT_LOG_MESSAGE)

    def test_log_to_envelope_log_complex_body(self):
        exporter = self._exporter
        envelope = exporter._log_to_envelope(self._log_data_complex_body)
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Message")
        self.assertEqual(envelope.data.base_type, "MessageData")
        self.assertEqual(
            envelope.data.base_data.message,
            json.dumps(self._log_data_complex_body.log_record.body),
        )
        self.assertEqual(envelope.tags.get(ContextTagKeys.AI_OPERATION_NAME), "TestOperationName")

    def test_log_to_envelope_log_complex_body_not_serializeable(self):
        exporter = self._exporter
        envelope = exporter._log_to_envelope(self._log_data_complex_body_not_serializeable)
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Message")
        self.assertEqual(envelope.data.base_type, "MessageData")
        self.assertEqual(
            envelope.data.base_data.message,
            str(self._log_data_complex_body_not_serializeable.log_record.body),
        )

    def test_log_to_envelope_exception_with_string_message(self):
        exporter = self._exporter
        envelope = exporter._log_to_envelope(self._exc_data)
        record = self._log_data.log_record
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Exception")
        self.assertEqual(envelope.time, ns_to_datetime(record.timestamp))
        self.assertEqual(envelope.data.base_type, "ExceptionData")
        self.assertEqual(envelope.data.base_data.severity_level, 4)
        self.assertEqual(envelope.data.base_data.properties["test"], "attribute")
        self.assertEqual(len(envelope.data.base_data.exceptions), 1)
        self.assertEqual(envelope.data.base_data.exceptions[0].type_name, "ZeroDivisionError")
        self.assertEqual(envelope.data.base_data.exceptions[0].message, "Test message")
        self.assertTrue(envelope.data.base_data.exceptions[0].has_full_stack)
        self.assertEqual(
            envelope.data.base_data.exceptions[0].stack,
            'Traceback (most recent call last):\n  File "test.py", line 38, in <module>\n    raise ZeroDivisionError()\nZeroDivisionError\n',
        )

    def test_log_to_envelope_exception_with_exc_message(self):
        exporter = self._exporter
        envelope = exporter._log_to_envelope(self._exc_data_with_exc_body)
        record = self._log_data.log_record
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Exception")
        self.assertEqual(envelope.time, ns_to_datetime(record.timestamp))
        self.assertEqual(envelope.data.base_type, "ExceptionData")
        self.assertEqual(envelope.data.base_data.severity_level, 4)
        self.assertEqual(envelope.data.base_data.properties["test"], "attribute")
        self.assertEqual(len(envelope.data.base_data.exceptions), 1)
        self.assertEqual(envelope.data.base_data.exceptions[0].type_name, "ZeroDivisionError")
        self.assertEqual(envelope.data.base_data.exceptions[0].message, "test exception message")
        self.assertTrue(envelope.data.base_data.exceptions[0].has_full_stack)
        self.assertEqual(
            envelope.data.base_data.exceptions[0].stack,
            'Traceback (most recent call last):\n  File "test.py", line 38, in <module>\n    raise ZeroDivisionError()\nZeroDivisionError\n',
        )

    def test_log_to_envelope_exception_empty(self):
        exporter = self._exporter
        envelope = exporter._log_to_envelope(self._exc_data_empty)
        record = self._log_data.log_record
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Exception")
        self.assertEqual(envelope.time, ns_to_datetime(record.timestamp))
        self.assertEqual(envelope.data.base_type, "ExceptionData")
        self.assertEqual(envelope.data.base_data.severity_level, 4)
        self.assertEqual(envelope.data.base_data.properties["test"], "attribute")
        self.assertEqual(len(envelope.data.base_data.exceptions), 1)
        self.assertEqual(envelope.data.base_data.exceptions[0].type_name, "Exception")
        self.assertEqual(envelope.data.base_data.exceptions[0].message, "Exception")
        self.assertTrue(envelope.data.base_data.exceptions[0].has_full_stack)
        self.assertEqual(envelope.data.base_data.exceptions[0].stack, "")

    def test_log_to_envelope_exception_with_blank_exception(self):
        exporter = self._exporter
        envelope = exporter._log_to_envelope(self._exc_data_blank_exception)
        record = self._log_data.log_record
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Exception")
        self.assertEqual(envelope.time, ns_to_datetime(record.timestamp))
        self.assertEqual(envelope.data.base_type, "ExceptionData")
        self.assertEqual(envelope.data.base_data.severity_level, 4)
        self.assertEqual(envelope.data.base_data.properties["test"], "attribute")
        self.assertEqual(len(envelope.data.base_data.exceptions), 1)
        self.assertEqual(envelope.data.base_data.exceptions[0].type_name, "Exception")
        self.assertEqual(envelope.data.base_data.exceptions[0].message, "test exception")
        self.assertTrue(envelope.data.base_data.exceptions[0].has_full_stack)
        self.assertEqual(envelope.data.base_data.exceptions[0].stack, "")
        self.assertEqual(envelope.data.base_data.properties.get("logger_name"), "blank_exception_logger")

    def test_log_to_envelope_event(self):
        exporter = self._exporter
        envelope = exporter._log_to_envelope(self._log_data_event)
        record = self._log_data_event.log_record
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Event")
        self.assertEqual(envelope.time, ns_to_datetime(record.timestamp))
        self.assertEqual(envelope.data.base_type, "EventData")
        self.assertEqual(envelope.data.base_data.name, record.body)
        self.assertEqual(envelope.data.base_data.properties["event_key"], "event_attribute")

    def test_log_to_envelope_event_complex_body(self):
        exporter = self._exporter
        envelope = exporter._log_to_envelope(self._log_data_event_complex_body)
        record = self._log_data_event_complex_body.log_record
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Event")
        self.assertEqual(envelope.time, ns_to_datetime(record.timestamp))
        self.assertEqual(envelope.data.base_type, "EventData")
        self.assertEqual(envelope.data.base_data.name, json.dumps(record.body))
        self.assertEqual(envelope.data.base_data.properties["event_key"], "event_attribute")

    def test_log_to_envelope_event_complex_body_not_serializeable(self):
        exporter = self._exporter
        envelope = exporter._log_to_envelope(self._log_data_event_complex_body_not_serializeable)
        record = self._log_data_event_complex_body_not_serializeable.log_record
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Event")
        self.assertEqual(envelope.time, ns_to_datetime(record.timestamp))
        self.assertEqual(envelope.data.base_type, "EventData")
        self.assertEqual(envelope.data.base_data.name, str(record.body))
        self.assertEqual(envelope.data.base_data.properties["event_key"], "event_attribute")

    def test_log_to_envelope_custom_event(self):
        exporter = self._exporter
        envelope = exporter._log_to_envelope(self._log_data_custom_event)
        record = self._log_data_custom_event.log_record
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Event")
        self.assertEqual(envelope.tags["ai.location.ip"], "192.168.1.1")
        self.assertEqual(envelope.time, ns_to_datetime(record.timestamp))
        self.assertEqual(envelope.data.base_type, "EventData")
        self.assertEqual(envelope.data.base_data.name, "event_name")
        self.assertEqual(envelope.data.base_data.properties["event_key"], "event_attribute")
        self.assertEqual(envelope.data.base_data.properties.get("logger_name"), "custom-event-logger")

    def test_log_to_envelope_custom_measurements(self):
        exporter = self._exporter
        attributes = {
            "test": "attribute",
            _MICROSOFT_CUSTOM_MEASUREMENTS: '{"itemsProcessed": 42.0, "queueDepth": 7}',
        }
        expected = {"itemsProcessed": 42.0, "queueDepth": 7.0}
        cases = {
            "MessageData": {},
            "EventData": {_MICROSOFT_CUSTOM_EVENT_NAME: "event_name"},
            "ExceptionData": {EXCEPTION_TYPE: "ZeroDivisionError", EXCEPTION_MESSAGE: "division by zero"},
        }
        for base_type, extra_attributes in cases.items():
            with self.subTest(base_type=base_type):
                log_data = _logs.ReadWriteLogRecord(
                    LogRecord(
                        timestamp=1646865018558419456,
                        severity_text="INFO",
                        severity_number=SeverityNumber.INFO,
                        body="Test message",
                        attributes={**attributes, **extra_attributes},
                    ),
                    resource=Resource.create(attributes={"asd": "test_resource"}),
                    instrumentation_scope=InstrumentationScope("test_name"),
                )
                envelope = exporter._log_to_envelope(log_data)
                self.assertEqual(envelope.data.base_type, base_type)
                self.assertEqual(envelope.data.base_data.measurements, expected)
                self.assertIsNone(envelope.data.base_data.properties.get(_MICROSOFT_CUSTOM_MEASUREMENTS))

    def test_log_to_envelope_availability(self):
        exporter = self._exporter
        timestamp = 1646865018558419456
        log_data = _logs.ReadWriteLogRecord(
            LogRecord(
                timestamp=timestamp,
                severity_text="INFO",
                severity_number=SeverityNumber.INFO,
                body="availability log",
                attributes={
                    "test": "attribute",
                    _MICROSOFT_AVAILABILITY_ID: "test-id",
                    _MICROSOFT_AVAILABILITY_NAME: "test-name",
                    _MICROSOFT_AVAILABILITY_DURATION: "00:00:05",
                    _MICROSOFT_AVAILABILITY_SUCCESS: "true",
                    _MICROSOFT_AVAILABILITY_RUN_LOCATION: "test-location",
                    _MICROSOFT_AVAILABILITY_MESSAGE: "test-message",
                    _MICROSOFT_CUSTOM_MEASUREMENTS: '{"itemsProcessed": 42.0}',
                },
            ),
            resource=Resource.create(attributes={"asd": "test_resource"}),
            instrumentation_scope=InstrumentationScope("test_name"),
        )

        envelope = exporter._log_to_envelope(log_data)

        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Availability")
        self.assertEqual(envelope.time, ns_to_datetime(timestamp))
        self.assertEqual(envelope.data.base_type, "AvailabilityData")
        self.assertEqual(envelope.data.base_data.id, "test-id")
        self.assertEqual(envelope.data.base_data.name, "test-name")
        self.assertEqual(envelope.data.base_data.duration, "00:00:05")
        self.assertTrue(envelope.data.base_data.success)
        self.assertEqual(envelope.data.base_data.run_location, "test-location")
        self.assertEqual(envelope.data.base_data.message, "test-message")
        self.assertEqual(envelope.data.base_data.measurements, {"itemsProcessed": 42.0})
        self.assertEqual(envelope.data.base_data.properties, {"test": "attribute", "logger_name": "test_name"})

    def test_log_to_envelope_availability_preserves_empty_message(self):
        exporter = self._exporter
        log_data = _logs.ReadWriteLogRecord(
            LogRecord(
                timestamp=1646865018558419456,
                severity_text="INFO",
                severity_number=SeverityNumber.INFO,
                body="availability log",
                attributes={
                    _MICROSOFT_AVAILABILITY_ID: "test-id",
                    _MICROSOFT_AVAILABILITY_NAME: "test-name",
                    _MICROSOFT_AVAILABILITY_DURATION: "00:00:05",
                    _MICROSOFT_AVAILABILITY_SUCCESS: "true",
                    _MICROSOFT_AVAILABILITY_MESSAGE: "",
                },
            ),
            resource=Resource.create(attributes={"asd": "test_resource"}),
            instrumentation_scope=InstrumentationScope("test_name"),
        )

        envelope = exporter._log_to_envelope(log_data)

        self.assertEqual(envelope.data.base_type, "AvailabilityData")
        self.assertEqual(envelope.data.base_data.message, "")

    def test_log_to_envelope_availability_missing_required_attribute(self):
        exporter = self._exporter
        for availability_id in (None, ""):
            with self.subTest(availability_id=availability_id):
                log_data = _logs.ReadWriteLogRecord(
                    LogRecord(
                        timestamp=1646865018558419456,
                        severity_text="INFO",
                        severity_number=SeverityNumber.INFO,
                        body="availability log",
                        attributes={
                            _MICROSOFT_AVAILABILITY_ID: availability_id,
                            _MICROSOFT_AVAILABILITY_NAME: "test-name",
                            _MICROSOFT_AVAILABILITY_DURATION: "00:00:05",
                            _MICROSOFT_AVAILABILITY_SUCCESS: "true",
                        },
                    ),
                    resource=Resource.create(attributes={"asd": "test_resource"}),
                    instrumentation_scope=InstrumentationScope("test_name"),
                )

                envelope = exporter._log_to_envelope(log_data)

                self.assertEqual(envelope.data.base_type, "MessageData")
                self.assertEqual(envelope.data.base_data.message, "availability log")

    def test_log_to_envelope_custom_event_precedes_availability(self):
        exporter = self._exporter
        log_data = _logs.ReadWriteLogRecord(
            LogRecord(
                timestamp=1646865018558419456,
                severity_text="INFO",
                severity_number=SeverityNumber.INFO,
                body="availability log",
                attributes={
                    _MICROSOFT_AVAILABILITY_ID: "test-id",
                    _MICROSOFT_AVAILABILITY_NAME: "test-name",
                    _MICROSOFT_AVAILABILITY_DURATION: "00:00:05",
                    _MICROSOFT_AVAILABILITY_SUCCESS: "true",
                    _MICROSOFT_CUSTOM_EVENT_NAME: "test-event",
                },
            ),
            resource=Resource.create(attributes={"asd": "test_resource"}),
            instrumentation_scope=InstrumentationScope("test_name"),
        )

        envelope = exporter._log_to_envelope(log_data)

        self.assertEqual(envelope.data.base_type, "EventData")
        self.assertEqual(envelope.data.base_data.name, "test-event")

    def test_log_to_envelope_exception_precedes_availability(self):
        exporter = self._exporter
        log_data = _logs.ReadWriteLogRecord(
            LogRecord(
                timestamp=1646865018558419456,
                severity_text="INFO",
                severity_number=SeverityNumber.INFO,
                body="availability log",
                attributes={
                    _MICROSOFT_AVAILABILITY_ID: "test-id",
                    _MICROSOFT_AVAILABILITY_NAME: "test-name",
                    _MICROSOFT_AVAILABILITY_DURATION: "00:00:05",
                    _MICROSOFT_AVAILABILITY_SUCCESS: "true",
                    EXCEPTION_TYPE: "ValueError",
                },
            ),
            resource=Resource.create(attributes={"asd": "test_resource"}),
            instrumentation_scope=InstrumentationScope("test_name"),
        )

        envelope = exporter._log_to_envelope(log_data)

        self.assertEqual(envelope.data.base_type, "ExceptionData")
        self.assertEqual(envelope.data.base_data.exceptions[0].type_name, "ValueError")

    def test_log_to_envelope_timestamp(self):
        exporter = self._exporter
        old_record = self._log_data.log_record
        self._log_data.log_record.timestamp = None
        self._log_data.log_record.observed_timestamp = 1646865018558419457
        envelope = exporter._log_to_envelope(self._log_data)
        record = self._log_data.log_record
        self.assertEqual(envelope.time, ns_to_datetime(record.observed_timestamp))
        self._log_data.log_record = old_record

    def test_log_to_envelope_synthetic_source(self):
        exporter = self._exporter
        resource = Resource.create(
            {
                "service.name": "testServiceName",
                "service.namespace": "testServiceNamespace",
                "service.instance.id": "testServiceInstanceId",
            }
        )
        span_context = SpanContext(
            trace_id=125960616039069540489478540494783893221,
            span_id=2909973987304607650,
            trace_flags=None,
            is_remote=False,
        )
        span = NonRecordingSpan(span_context)
        ctx = set_span_in_context(span)
        log_data = _logs.ReadWriteLogRecord(
            LogRecord(
                timestamp=1646865018558419456,
                context=ctx,
                severity_text="WARNING",
                severity_number=SeverityNumber.WARN,
                body="Test message",
                attributes={
                    "test": "attribute",
                    "user_agent.synthetic.type": "bot",
                },
            ),
            resource=resource,
            instrumentation_scope=InstrumentationScope("test_name"),
        )
        envelope = exporter._log_to_envelope(log_data)

        self.assertEqual(envelope.tags.get(ContextTagKeys.AI_OPERATION_SYNTHETIC_SOURCE), "True")
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_CLOUD_ROLE),
            "testServiceNamespace.testServiceName",
        )
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_CLOUD_ROLE_INSTANCE),
            "testServiceInstanceId",
        )

    def test_log_to_envelope_synthetic_load_always_on(self):
        exporter = self._exporter
        resource = Resource.create(
            {
                "service.name": "testServiceName",
                "service.namespace": "testServiceNamespace",
                "service.instance.id": "testServiceInstanceId",
            }
        )
        span_context = SpanContext(
            trace_id=125960616039069540489478540494783893221,
            span_id=2909973987304607650,
            trace_flags=None,
            is_remote=False,
        )
        span = NonRecordingSpan(span_context)
        ctx = set_span_in_context(span)
        log_data = _logs.ReadWriteLogRecord(
            LogRecord(
                timestamp=1646865018558419456,
                context=ctx,
                severity_text="WARNING",
                severity_number=SeverityNumber.WARN,
                body="Test message",
                attributes={
                    "test": "attribute",
                    "http.user_agent": "Azure-Load-Testing/1.0 AlwaysOn",
                },
            ),
            resource=resource,
            instrumentation_scope=InstrumentationScope("test_name"),
        )
        envelope = exporter._log_to_envelope(log_data)

        self.assertEqual(envelope.tags.get(ContextTagKeys.AI_OPERATION_SYNTHETIC_SOURCE), "True")
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_CLOUD_ROLE),
            "testServiceNamespace.testServiceName",
        )
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_CLOUD_ROLE_INSTANCE),
            "testServiceInstanceId",
        )


class TestAzureLogExporterWithDisabledStorage(TestAzureLogExporter):
    _exporter_class = partial(AzureMonitorLogExporter, disable_offline_storage=True)

    @classmethod
    def tearDownClass(cls):
        pass

    def test_constructor(self):
        """Test the constructor."""
        exporter = AzureMonitorLogExporter(
            connection_string="InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab",
            disable_offline_storage=True,
        )
        self.assertEqual(
            exporter._instrumentation_key,
            "4321abcd-5678-4efa-8abc-1234567890ab",
        )
        self.assertEqual(exporter.storage, None)

    def test_shutdown(self):
        exporter = self._exporter
        exporter.shutdown()
        self.assertEqual(exporter.storage, None)

    def test_export_failure(self):
        exporter = self._exporter
        with mock.patch(
            "azure.monitor.opentelemetry.exporter.AzureMonitorLogExporter._transmit"
        ) as transmit:  # noqa: E501
            transmit.return_value = ExportResult.FAILED_NOT_RETRYABLE
            transmit_from_storage_mock = mock.Mock()
            exporter._handle_transmit_from_storage = transmit_from_storage_mock
            result = exporter.export([self._log_data])
            self.assertEqual(result, LogRecordExportResult.FAILURE)
            self.assertEqual(exporter.storage, None)
            self.assertEqual(transmit_from_storage_mock.call_count, 1)

    def test_export_success(self):
        exporter = self._exporter
        with mock.patch(
            "azure.monitor.opentelemetry.exporter.AzureMonitorLogExporter._transmit"
        ) as transmit:  # noqa: E501
            transmit.return_value = ExportResult.SUCCESS
            storage_mock = mock.Mock()
            exporter._transmit_from_storage = storage_mock
            result = exporter.export([self._log_data])
            self.assertEqual(result, LogRecordExportResult.SUCCESS)
            self.assertEqual(storage_mock.call_count, 0)


class TestAzureLogExporterUtils(unittest.TestCase):
    def test_get_log_export_result(self):
        self.assertEqual(
            _get_log_export_result(ExportResult.SUCCESS),
            LogRecordExportResult.SUCCESS,
        )
        self.assertEqual(
            _get_log_export_result(ExportResult.FAILED_NOT_RETRYABLE),
            LogRecordExportResult.FAILURE,
        )
        self.assertEqual(
            _get_log_export_result(ExportResult.FAILED_RETRYABLE),
            LogRecordExportResult.FAILURE,
        )
        self.assertEqual(_get_log_export_result(None), LogRecordExportResult.FAILURE)

    def test_get_severity_level(self):
        for sev_num in SeverityNumber:
            num = sev_num.value
            level = _get_severity_level(sev_num)
            if num in range(0, 9):
                self.assertEqual(level, 0)
            elif num in range(9, 13):
                self.assertEqual(level, 1)
            elif num in range(13, 17):
                self.assertEqual(level, 2)
            elif num in range(17, 21):
                self.assertEqual(level, 3)
            else:
                self.assertEqual(level, 4)


class _Response(HttpResponse):
    def __init__(self, request, status_code=200, headers=None, errors=None):
        super().__init__(request, None)
        self.status_code = status_code
        self.headers = {"Content-Type": "application/json", **(headers or {})}
        self.content_type = "application/json"
        count = len(json.loads(request.body))
        self._body = json.dumps(
            {"itemsReceived": count, "itemsAccepted": count - len(errors or []), "errors": errors or []}
        ).encode()

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
            exporter = AzureMonitorLogExporter(**options)
        self.addCleanup(exporter.shutdown)
        return exporter

    def _record(self, endpoint="https://one.example/proxy/", key="customer-key", auth="ikey", body="message"):
        return ReadWriteLogRecord(
            LogRecord(
                timestamp=1,
                body=body,
                attributes={
                    "microsoft.instrumentation_key": key,
                    "microsoft.ingestion_endpoint": endpoint,
                    "microsoft.ingestion_auth": auth,
                    "microsoft.multi_endpoint_cloud_role": "not-the-resource-role",
                },
            ),
            resource=Resource({"service.name": "resource-role", "service.instance.id": "resource-instance"}),
        )

    def test_grouping_and_per_item_keys(self):
        exporter = self._exporter()
        records = [
            self._record(key=" key-one "),
            self._record(endpoint="https://two.example/", key="key-two"),
            self._record(endpoint="HTTPS://ONE.EXAMPLE:443/proxy", key="key-three"),
        ]
        self.assertEqual(exporter.export(records), LogRecordExportResult.SUCCESS)
        requests = [call.args[0] for call in self.transport.send.call_args_list]
        self.assertEqual(len(requests), 2)
        self.assertTrue(requests[0].url.startswith("https://one.example/proxy/"))
        self.assertTrue(requests[1].url.startswith("https://two.example/"))
        self.assertEqual([item["iKey"] for item in json.loads(requests[0].body)], ["key-one", "key-three"])
        self.assertEqual([item["iKey"] for item in json.loads(requests[1].body)], ["key-two"])
        for request in requests:
            for item in json.loads(request.body):
                self.assertEqual(item["tags"]["ai.cloud.role"], "resource-role")
                self.assertEqual(item["tags"]["ai.cloud.roleInstance"], "resource-instance")
        self.assertEqual(records[0].log_record.attributes["microsoft.instrumentation_key"], " key-one ")

    def test_single_connection_string_is_unchanged(self):
        exporter = self._exporter(routing=False)
        records = [self._record(), self._record(endpoint="https://two.example/")]
        self.assertEqual(exporter.export(records), LogRecordExportResult.SUCCESS)
        self.transport.send.assert_called_once()
        request = self.transport.send.call_args.args[0]
        self.assertTrue(request.url.startswith("https://host.example/"))
        self.assertEqual(
            [item["iKey"] for item in json.loads(request.body)],
            ["1234abcd-5678-4efa-8abc-1234567890ab"] * 2,
        )

    @mock.patch.dict(os.environ)
    def test_routing_without_host_connection_string(self):
        os.environ.pop("APPLICATIONINSIGHTS_CONNECTION_STRING", None)
        os.environ.pop("APPINSIGHTS_INSTRUMENTATIONKEY", None)
        credential = mock.Mock(spec=["get_token"])
        credential.get_token.return_value = AccessToken("test-token", int(time.time()) + 3600)
        exporter = self._exporter(connection_string=None, credential=credential)
        self.assertIsNone(exporter._instrumentation_key)
        os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"] = "invalid"
        self.assertEqual(exporter.export([self._record(), self._record(auth="aad")]), LogRecordExportResult.SUCCESS)
        requests = [call.args[0] for call in self.transport.send.call_args_list]
        self.assertEqual(len(requests), 2)
        self.assertTrue(all(request.url.startswith("https://one.example/proxy/") for request in requests))
        self.assertEqual([json.loads(request.body)[0]["iKey"] for request in requests], ["customer-key"] * 2)
        self.assertNotIn("Authorization", requests[0].headers)
        self.assertEqual(requests[1].headers["Authorization"], f"Bearer {credential.get_token.return_value.token}")

    @mock.patch.dict(os.environ)
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base._get_storage_directory")
    def test_routing_without_host_uses_default_for_none_storage_directory(self, default_storage):
        os.environ.pop("APPLICATIONINSIGHTS_CONNECTION_STRING", None)
        os.environ.pop("APPINSIGHTS_INSTRUMENTATIONKEY", None)
        default_path = str(Path(self.directory.name) / "default")
        default_storage.return_value = default_path
        exporter = self._exporter(
            connection_string=None,
            storage_directory=None,
            disable_offline_storage=False,
        )
        self.assertEqual(exporter.export([self._record()]), LogRecordExportResult.SUCCESS)
        route = exporter._route_exporters[("https://one.example/proxy/", False)]
        self.assertIsNotNone(route.storage)
        self.assertEqual(os.path.dirname(route.storage._path), os.path.abspath(default_path + "-routes"))
        default_storage.assert_called_once_with("")

    def test_route_creation_preserves_resolved_host_configuration(self):
        with mock.patch.dict(
            os.environ,
            {
                "APPINSIGHTS_INSTRUMENTATIONKEY": "1234abcd-5678-4efa-8abc-1234567890ab",
            },
        ):
            os.environ.pop("APPLICATIONINSIGHTS_CONNECTION_STRING", None)
            exporter = self._exporter(connection_string=None, credential=None)
            os.environ.pop("APPINSIGHTS_INSTRUMENTATIONKEY")
            os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"] = "invalid"
            self.assertEqual(exporter.export([self._record()]), LogRecordExportResult.SUCCESS)
        self.assertTrue(self.transport.send.call_args.args[0].url.startswith("https://one.example/proxy/"))

    @mock.patch.dict(os.environ)
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.time.monotonic", return_value=100)
    def test_routing_without_host_preserves_retry_storage(self, clock):
        os.environ.pop("APPLICATIONINSIGHTS_CONNECTION_STRING", None)
        os.environ.pop("APPINSIGHTS_INSTRUMENTATIONKEY", None)
        with mock.patch(
            "azure.monitor.opentelemetry.exporter.export._base.tempfile.gettempdir", return_value=self.directory.name
        ):
            exporter = AzureMonitorLogExporter(transport=self.transport, retry_total=0)
        self.addCleanup(exporter.shutdown)
        self.assertIsNone(exporter.storage)
        self.assertFalse(Path(exporter._storage_directory).exists())
        now = datetime.datetime(2026, 10, 20, tzinfo=datetime.timezone.utc)
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request, 429, {"Retry-After": "60"})
        with mock.patch("azure.monitor.opentelemetry.exporter._storage._now", return_value=now):
            self.assertEqual(exporter.export([self._record(key="old-key")]), LogRecordExportResult.FAILURE)
        self.transport.send.reset_mock()
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request)
        clock.return_value = 161
        with mock.patch(
            "azure.monitor.opentelemetry.exporter._storage._now", return_value=now + datetime.timedelta(seconds=61)
        ):
            self.assertEqual(exporter.export([self._record(key="new-key")]), LogRecordExportResult.SUCCESS)
        requests = [call.args[0] for call in self.transport.send.call_args_list]
        self.assertEqual(len(requests), 2)
        self.assertEqual([json.loads(request.body)[0]["iKey"] for request in requests], ["new-key", "old-key"])
        self.assertTrue(all(request.url.startswith("https://one.example/proxy/") for request in requests))
        self.assertFalse(Path(exporter._storage_directory).exists())

    def test_authentication_groups_and_client_reuse(self):
        credential = mock.Mock(spec=["get_token"])
        credential.get_token.return_value = AccessToken("test-token", int(time.time()) + 3600)
        exporter = self._exporter(credential=credential)
        records = [self._record(), self._record(auth=" AAD ")]
        for _ in range(2):
            self.assertEqual(exporter.export(records), LogRecordExportResult.SUCCESS)
        requests = [call.args[0] for call in self.transport.send.call_args_list]
        self.assertEqual(len(requests), 4)
        for request in requests[::2]:
            self.assertNotIn("Authorization", request.headers)
        for request in requests[1::2]:
            self.assertEqual(request.headers["Authorization"], "Bearer test-token")
        credential.get_token.assert_called_once()

    def test_missing_aad_credential_does_not_block_other_routes(self):
        exporter = self._exporter(credential=None)
        with self.assertLogs("azure.monitor.opentelemetry.exporter.export._base", level="ERROR"):
            result = exporter.export([self._record(auth="aad"), self._record(endpoint="https://two.example/")])
        self.assertEqual(result, LogRecordExportResult.FAILURE)
        self.transport.send.assert_called_once()
        self.assertTrue(self.transport.send.call_args.args[0].url.startswith("https://two.example/"))

    def test_routed_export_exception_is_reported(self):
        exporter = self._exporter()
        with mock.patch.object(exporter, "_transmit_routed", side_effect=RuntimeError("test failure")):
            with self.assertLogs("azure.monitor.opentelemetry.exporter.export.logs._exporter", level="ERROR") as logs:
                self.assertEqual(exporter.export([self._record()]), LogRecordExportResult.FAILURE)
        self.assertIn("test failure", logs.output[0])

    def test_invalid_destination_response_does_not_shutdown_host_stats(self):
        exporter = self._exporter()
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request, 400)
        with mock.patch(
            "azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.shutdown_statsbeat_metrics"
        ) as shutdown_statsbeat, mock.patch(
            "azure.monitor.opentelemetry.exporter.statsbeat.customer.shutdown_customer_sdkstats_metrics"
        ) as shutdown_customer_stats:
            self.assertEqual(exporter.export([self._record()]), LogRecordExportResult.FAILURE)
        shutdown_statsbeat.assert_not_called()
        shutdown_customer_stats.assert_not_called()

    def test_retry_storage_survives_restart_and_preserves_keys(self):
        now = datetime.datetime(2026, 10, 20, tzinfo=datetime.timezone.utc)
        exporter = self._exporter(disable_offline_storage=False)
        self.transport.send.side_effect = lambda request, **kwargs: _Response(
            request, 429, headers={"Retry-After": "60"}
        )
        with mock.patch("azure.monitor.opentelemetry.exporter._storage._now", return_value=now):
            self.assertEqual(exporter.export([self._record(key="old-key")]), LogRecordExportResult.FAILURE)
        exporter.shutdown()
        restarted = self._exporter(disable_offline_storage=False)
        self.transport.send.reset_mock()
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request)
        with mock.patch(
            "azure.monitor.opentelemetry.exporter._storage._now", return_value=now + datetime.timedelta(seconds=61)
        ):
            self.assertEqual(restarted.export([self._record(key="new-key")]), LogRecordExportResult.SUCCESS)
        requests = [call.args[0] for call in self.transport.send.call_args_list]
        self.assertEqual(len(requests), 2)
        self.assertEqual([json.loads(request.body)[0]["iKey"] for request in requests], ["new-key", "old-key"])
        self.assertTrue(all(request.url.startswith("https://one.example/proxy/") for request in requests))
        self.assertFalse(list((Path(self.directory.name) / "host").iterdir()))

    def test_retry_failure_is_isolated_from_other_destinations(self):
        exporter = self._exporter(disable_offline_storage=False)
        self.transport.send.side_effect = lambda request, **kwargs: _Response(
            request, 429 if request.url.startswith("https://one.example/") else 200, headers={"Retry-After": "60"}
        )
        result = exporter.export([self._record(), self._record(endpoint="https://two.example/")])
        self.assertEqual(result, LogRecordExportResult.FAILURE)
        requests = [call.args[0] for call in self.transport.send.call_args_list]
        self.assertEqual(len(requests), 2)
        self.assertTrue(requests[1].url.startswith("https://two.example/"))
        self.assertFalse(list((Path(self.directory.name) / "host").iterdir()))

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.time.monotonic", return_value=100)
    def test_route_backoff_defers_until_retry_after_without_blocking_other_routes(self, clock):
        now = datetime.datetime(2026, 10, 20, tzinfo=datetime.timezone.utc)
        exporter = self._exporter(disable_offline_storage=False)
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request, 429, {"Retry-After": "60"})
        with mock.patch("azure.monitor.opentelemetry.exporter._storage._now", return_value=now):
            self.assertEqual(exporter.export([self._record(key="original")]), LogRecordExportResult.FAILURE)
        self.transport.send.reset_mock()
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request)
        clock.return_value = 120
        with mock.patch(
            "azure.monitor.opentelemetry.exporter._storage._now", return_value=now + datetime.timedelta(seconds=20)
        ):
            result = exporter.export(
                [self._record(key="deferred"), self._record(endpoint="https://two.example/", key="healthy")]
            )
        self.assertEqual(result, LogRecordExportResult.FAILURE)
        self.transport.send.assert_called_once()
        self.assertTrue(self.transport.send.call_args.args[0].url.startswith("https://two.example/"))
        self.assertEqual(len(list(Path(self.directory.name).rglob("*.lock"))), 2)
        self.transport.send.reset_mock()
        clock.return_value = 160
        with mock.patch(
            "azure.monitor.opentelemetry.exporter._storage._now", return_value=now + datetime.timedelta(seconds=60)
        ):
            self.assertEqual(exporter.export([self._record(key="new")]), LogRecordExportResult.SUCCESS)
        requests = [call.args[0] for call in self.transport.send.call_args_list]
        self.assertEqual([json.loads(request.body)[0]["iKey"] for request in requests], ["new", "original", "deferred"])
        self.assertTrue(all(request.url.startswith("https://one.example/proxy/") for request in requests))

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.time.monotonic", return_value=100)
    def test_route_backoff_uses_existing_retry_interval_without_header(self, clock):
        for failure in (503, ServiceRequestError("test connection failure")):
            with self.subTest(failure=failure):
                clock.return_value = 100
                exporter = self._exporter(disable_offline_storage=False, storage_min_retry_interval=9)
                if isinstance(failure, int):
                    self.transport.send.side_effect = lambda request, **kwargs: _Response(request, failure)
                else:
                    self.transport.send.side_effect = failure
                self.assertEqual(exporter.export([self._record()]), LogRecordExportResult.FAILURE)
                self.transport.send.reset_mock()
                self.transport.send.side_effect = lambda request, **kwargs: _Response(request)
                clock.return_value = 108.5
                self.assertEqual(exporter.export([self._record()]), LogRecordExportResult.FAILURE)
                self.transport.send.assert_not_called()
                clock.return_value = 109
                self.assertEqual(exporter.export([self._record()]), LogRecordExportResult.SUCCESS)
                self.transport.send.assert_called_once()

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.time.monotonic", return_value=100)
    def test_route_backoff_is_separate_for_authentication_modes(self, _clock):
        credential = mock.Mock(spec=["get_token"])
        credential.get_token.return_value = AccessToken("test-token", int(time.time()) + 3600)
        exporter = self._exporter(credential=credential, disable_offline_storage=False)
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request, 429, {"Retry-After": "60"})
        self.assertEqual(exporter.export([self._record()]), LogRecordExportResult.FAILURE)
        self.transport.send.reset_mock()
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request)
        self.assertEqual(exporter.export([self._record(), self._record(auth="aad")]), LogRecordExportResult.FAILURE)
        self.transport.send.assert_called_once()
        self.assertIn("Authorization", self.transport.send.call_args.args[0].headers)

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.time.monotonic", return_value=100)
    def test_unavailable_storage_does_not_suppress_transmission(self, _clock):
        for unavailable in ("disabled", "remote", "permissions"):
            with self.subTest(unavailable=unavailable):
                exporter = self._exporter(disable_offline_storage=unavailable == "disabled")
                self.transport.send.side_effect = lambda request, **kwargs: _Response(request, 429)
                self.assertEqual(exporter.export([self._record()]), LogRecordExportResult.FAILURE)
                if unavailable == "remote":
                    exporter._local_storage_configuration_callback(
                        {_ONE_SETTINGS_FEATURE_LOCAL_STORAGE: {"default": "disabled"}}
                    )
                elif unavailable == "permissions":
                    route = exporter._route_exporters[("https://one.example/proxy/", False)]
                    self.addCleanup(route.storage.close)
                    with mock.patch.object(route.storage, "_enabled", False):
                        self.transport.send.reset_mock()
                        self.transport.send.side_effect = lambda request, **kwargs: _Response(request)
                        self.assertEqual(exporter.export([self._record()]), LogRecordExportResult.SUCCESS)
                    self.transport.send.assert_called_once()
                    continue
                self.transport.send.reset_mock()
                self.transport.send.side_effect = lambda request, **kwargs: _Response(request)
                self.assertEqual(exporter.export([self._record()]), LogRecordExportResult.SUCCESS)
                self.transport.send.assert_called_once()

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.time.monotonic", return_value=100)
    def test_single_connection_string_does_not_backoff_new_batches(self, _clock):
        exporter = self._exporter(routing=False, disable_offline_storage=False)
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request, 429, {"Retry-After": "60"})
        self.assertEqual(exporter.export([self._record()]), LogRecordExportResult.FAILURE)
        self.transport.send.reset_mock()
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request)
        self.assertEqual(exporter.export([self._record()]), LogRecordExportResult.SUCCESS)
        self.transport.send.assert_called_once()

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.time.monotonic", return_value=100)
    def test_partial_failure_retries_only_rejected_items(self, clock):
        now = datetime.datetime(2026, 10, 20, tzinfo=datetime.timezone.utc)
        exporter = self._exporter(disable_offline_storage=False)
        self.transport.send.side_effect = lambda request, **kwargs: _Response(
            request,
            206,
            headers={"Retry-After": "60"},
            errors=[{"index": 1, "statusCode": 429, "message": "retry"}],
        )
        with mock.patch("azure.monitor.opentelemetry.exporter._storage._now", return_value=now):
            result = exporter.export([self._record(key="accepted"), self._record(key="rejected")])
        self.assertEqual(result, LogRecordExportResult.FAILURE)
        self.transport.send.reset_mock()
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request)
        clock.return_value = 130
        with mock.patch(
            "azure.monitor.opentelemetry.exporter._storage._now", return_value=now + datetime.timedelta(seconds=30)
        ):
            self.assertEqual(exporter.export([self._record(key="deferred")]), LogRecordExportResult.FAILURE)
        self.transport.send.assert_not_called()
        clock.return_value = 161
        with mock.patch(
            "azure.monitor.opentelemetry.exporter._storage._now", return_value=now + datetime.timedelta(seconds=61)
        ):
            self.assertEqual(exporter.export([self._record(key="new")]), LogRecordExportResult.SUCCESS)
        requests = [call.args[0] for call in self.transport.send.call_args_list]
        self.assertEqual([json.loads(request.body)[0]["iKey"] for request in requests], ["new", "rejected", "deferred"])

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.time.monotonic", return_value=100)
    def test_stored_retry_failure_starts_another_backoff_window(self, clock):
        now = datetime.datetime(2026, 10, 20, tzinfo=datetime.timezone.utc)
        exporter = self._exporter(disable_offline_storage=False)
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request, 429, {"Retry-After": "60"})
        with mock.patch("azure.monitor.opentelemetry.exporter._storage._now", return_value=now):
            self.assertEqual(exporter.export([self._record(key="stored")]), LogRecordExportResult.FAILURE)
        clock.return_value = 160
        self.transport.send.reset_mock()
        self.transport.send.side_effect = lambda request, **kwargs: _Response(
            request, 429 if json.loads(request.body)[0]["iKey"] == "stored" else 200, {"Retry-After": "120"}
        )
        with mock.patch(
            "azure.monitor.opentelemetry.exporter._storage._now", return_value=now + datetime.timedelta(seconds=60)
        ):
            self.assertEqual(exporter.export([self._record(key="new")]), LogRecordExportResult.SUCCESS)
        self.assertEqual(self.transport.send.call_count, 2)
        self.transport.send.reset_mock()
        clock.return_value = 170
        with mock.patch(
            "azure.monitor.opentelemetry.exporter._storage._now", return_value=now + datetime.timedelta(seconds=70)
        ):
            self.assertEqual(exporter.export([self._record(key="deferred")]), LogRecordExportResult.FAILURE)
        self.transport.send.assert_not_called()

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.time.monotonic", return_value=100)
    def test_non_retryable_failure_does_not_defer_new_batches(self, _clock):
        exporter = self._exporter(disable_offline_storage=False)
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request, 400)
        self.assertEqual(exporter.export([self._record()]), LogRecordExportResult.FAILURE)
        self.transport.send.reset_mock()
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request)
        self.assertEqual(exporter.export([self._record()]), LogRecordExportResult.SUCCESS)
        self.transport.send.assert_called_once()

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.time.monotonic", return_value=100)
    def test_backoff_preserves_retry_after_from_redirected_request(self, clock):
        exporter = self._exporter(disable_offline_storage=False)
        record = self._record(endpoint="https://eastus.in.applicationinsights.azure.com/")
        self.transport.send.side_effect = lambda request, **kwargs: (
            _Response(request, 307, {"location": "https://westus.in.applicationinsights.azure.com/"})
            if request.url.startswith("https://eastus.")
            else _Response(request, 429, {"Retry-After": "10"})
        )
        self.assertEqual(exporter.export([record]), LogRecordExportResult.FAILURE)
        self.assertEqual(self.transport.send.call_count, 2)
        self.transport.send.reset_mock()
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request)
        clock.return_value = 109
        self.assertEqual(exporter.export([record]), LogRecordExportResult.FAILURE)
        self.transport.send.assert_not_called()
        clock.return_value = 110
        self.assertEqual(exporter.export([record]), LogRecordExportResult.SUCCESS)
        self.transport.send.assert_called_once()

    def test_retry_storage_is_separate_for_authentication_modes(self):
        credential = mock.Mock(spec=["get_token"])
        credential.get_token.return_value = AccessToken("test-token", int(time.time()) + 3600)
        exporter = self._exporter(credential=credential, disable_offline_storage=False)
        self.transport.send.side_effect = lambda request, **kwargs: _Response(
            request, 200 if "Authorization" in request.headers else 429, headers={"Retry-After": "60"}
        )
        self.assertEqual(exporter.export([self._record(), self._record(auth="aad")]), LogRecordExportResult.FAILURE)
        partitions = list((Path(self.directory.name) / "host-routes").iterdir())
        self.assertEqual(len(partitions), 2)
        self.assertEqual(sorted(bool(list(partition.iterdir())) for partition in partitions), [False, True])
        self.transport.send.reset_mock()
        self.assertEqual(exporter.export([self._record(auth="aad")]), LogRecordExportResult.SUCCESS)
        self.transport.send.assert_called_once()

    def test_storage_capacity_is_shared_by_routes_not_host(self):
        exporter = self._exporter(
            disable_offline_storage=False,
            storage_max_size=1,
            storage_directory=str(Path(self.directory.name) / "host") + os.sep,
        )
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request, 429)
        result = exporter.export([self._record(), self._record(endpoint="https://two.example/")])
        self.assertEqual(result, LogRecordExportResult.FAILURE)
        partitions = list((Path(self.directory.name) / "host-routes").iterdir())
        self.assertEqual(len(partitions), 2)
        self.assertEqual(sorted(bool(list(partition.iterdir())) for partition in partitions), [False, True])
        self.assertTrue(exporter.storage._check_storage_size())

    def test_offline_storage_is_limited_to_64_endpoint_auth_partitions(self):
        credential = mock.Mock(spec=["get_token"])
        credential.get_token.return_value = AccessToken("test-token", int(time.time()) + 3600)
        exporter = self._exporter(disable_offline_storage=False, credential=credential)
        records = [self._record(endpoint=f"https://route-{index}.example/") for index in range(63)]
        records.extend(
            [
                self._record(endpoint="https://route-0.example/", auth="aad"),
                self._record(endpoint="https://overflow.example/"),
                self._record(endpoint="HTTPS://ROUTE-0.EXAMPLE:443", key="another-key"),
            ]
        )
        with self.assertLogs("azure.monitor.opentelemetry.exporter.export._base", level="WARNING") as logs:
            self.assertEqual(exporter.export(records), LogRecordExportResult.SUCCESS)
        self.assertIn("64", logs.output[0])
        self.assertIn("cached route", logs.output[0])
        self.assertIn("offline storage", logs.output[0])
        self.assertEqual(self.transport.send.call_count, 65)
        self.assertEqual(len(exporter._route_exporters), 64)
        partitions = list((Path(self.directory.name) / "host-routes").iterdir())
        self.assertEqual(len(partitions), 64)
        requests = [call.args[0] for call in self.transport.send.call_args_list]
        self.assertEqual([item["iKey"] for item in json.loads(requests[0].body)], ["customer-key", "another-key"])
        self.assertNotIn("Authorization", requests[0].headers)
        self.assertIn("Authorization", requests[63].headers)
        self.assertTrue(requests[64].url.startswith("https://overflow.example/"))
        self.transport.send.reset_mock()
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request, 429)
        retries = [records[0], records[63], records[64]]
        self.assertEqual(exporter.export(retries), LogRecordExportResult.FAILURE)
        self.assertEqual(self.transport.send.call_count, 3)
        self.assertEqual(len(list(Path(self.directory.name).rglob("*.lock"))), 2)
        exporter._local_storage_configuration_callback({_ONE_SETTINGS_FEATURE_LOCAL_STORAGE: {"default": "disabled"}})
        exporter._local_storage_configuration_callback({_ONE_SETTINGS_FEATURE_LOCAL_STORAGE: {"default": "enabled"}})
        self.assertEqual(len(list((Path(self.directory.name) / "host-routes").iterdir())), 64)
        self.assertNotIn(("https://overflow.example/", False), exporter._route_exporters)

    def test_disabled_offline_storage_does_not_create_partitions_past_limit(self):
        exporter = self._exporter()
        records = [self._record(endpoint=f"https://route-{index}.example/") for index in range(65)]
        self.assertEqual(exporter.export(records), LogRecordExportResult.SUCCESS)
        self.assertEqual(self.transport.send.call_count, 65)
        self.assertEqual(len(exporter._route_exporters), 64)
        self.assertNotIn(("https://route-64.example/", False), exporter._route_exporters)
        self.transport.close.assert_not_called()
        self.assertFalse((Path(self.directory.name) / "host-routes").exists())
        self.transport.send.reset_mock()
        self.assertEqual(exporter.export([records[-1]]), LogRecordExportResult.SUCCESS)
        self.transport.send.assert_called_once()
        self.assertEqual(len(exporter._route_exporters), 64)
        self.transport.close.assert_not_called()

    def test_shutdown_waits_for_short_lived_route_using_shared_transport(self):
        exporter = self._exporter()
        records = [self._record(endpoint=f"https://route-{index}.example/") for index in range(64)]
        self.assertEqual(exporter.export(records), LogRecordExportResult.SUCCESS)
        send_started = threading.Event()
        release_send = threading.Event()
        shutdown_done = threading.Event()

        def block_send(request, **kwargs):
            send_started.set()
            release_send.wait(2)
            return _Response(request)

        def shutdown():
            exporter.shutdown()
            shutdown_done.set()

        self.transport.send.side_effect = block_send
        export_thread = threading.Thread(
            target=exporter.export,
            args=([self._record(endpoint="https://overflow.example/")],),
            daemon=True,
        )
        shutdown_thread = threading.Thread(target=shutdown, daemon=True)
        try:
            export_thread.start()
            self.assertTrue(send_started.wait(2))
            shutdown_thread.start()
            self.assertFalse(shutdown_done.wait(0.1), "Shutdown closed a shared transport during an overflow send.")
        finally:
            release_send.set()
            export_thread.join(timeout=2)
            shutdown_thread.join(timeout=2)
        self.assertTrue(shutdown_done.is_set())

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.BaseExporter._transmit")
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.AzureMonitorClient.close")
    def test_short_lived_route_closes_owned_transport(self, close, transmit):
        transmit.return_value = ExportResult.SUCCESS
        options = {
            "connection_string": "InstrumentationKey=1234abcd-5678-4efa-8abc-1234567890ab;"
            "IngestionEndpoint=https://host.example/",
            "disable_offline_storage": True,
            "retry_total": 0,
        }
        exporter = AzureMonitorLogExporter(**options)
        self.addCleanup(exporter.shutdown)
        records = [self._record(endpoint=f"https://route-{index}.example/") for index in range(65)]
        self.assertEqual(exporter.export(records), LogRecordExportResult.SUCCESS)
        self.assertEqual(len(exporter._route_exporters), 64)
        close.assert_called_once()

    @mock.patch("azure.monitor.opentelemetry.exporter.export._rate_limiter.time.monotonic", return_value=0)
    def test_rate_limit_is_shared_by_routes(self, _monotonic):
        exporter = self._exporter(max_envelopes_per_second=1)
        result = exporter.export([self._record(), self._record(endpoint="https://two.example/")])
        self.assertEqual(result, LogRecordExportResult.FAILURE)
        self.transport.send.assert_called_once()

    def test_shutdown_closes_routed_clients(self):
        exporter = self._exporter()
        self.assertEqual(
            exporter.export([self._record(), self._record(endpoint="https://two.example/")]),
            LogRecordExportResult.SUCCESS,
        )
        exporter.shutdown()
        self.assertEqual(self.transport.close.call_count, 3)
        self.assertEqual(exporter.export([self._record()]), LogRecordExportResult.FAILURE)

    def test_storage_kill_switch_applies_to_routes(self):
        exporter = self._exporter(disable_offline_storage=False)
        exporter._local_storage_configuration_callback({_ONE_SETTINGS_FEATURE_LOCAL_STORAGE: {"default": "disabled"}})
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request, 429)
        self.assertEqual(exporter.export([self._record()]), LogRecordExportResult.FAILURE)
        self.assertFalse(list(Path(self.directory.name).rglob("*.lock")))
        exporter._local_storage_configuration_callback({_ONE_SETTINGS_FEATURE_LOCAL_STORAGE: {"default": "enabled"}})
        self.assertEqual(exporter.export([self._record()]), LogRecordExportResult.FAILURE)
        self.assertEqual(len(list(Path(self.directory.name).rglob("*.lock"))), 1)

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.PeriodicTask")
    def test_retry_worker_is_lazy_and_shared_by_storage_backed_routes(self, worker):
        disabled = self._exporter()
        self.assertEqual(disabled.export([self._record()]), LogRecordExportResult.SUCCESS)
        legacy = self._exporter(routing=False, disable_offline_storage=False)
        self.assertEqual(legacy.export([self._record()]), LogRecordExportResult.SUCCESS)
        exporter = self._exporter(disable_offline_storage=False, storage_maintenance_period=17)
        worker.assert_not_called()
        self.assertEqual(exporter.export([self._record()]), LogRecordExportResult.SUCCESS)
        self.assertEqual(
            exporter.export([self._record(), self._record(endpoint="https://two.example/")]),
            LogRecordExportResult.SUCCESS,
        )
        worker.assert_called_once()
        self.assertEqual(worker.call_args.kwargs["interval"], 17)
        self.assertIs(worker.return_value.daemon, True)
        worker.return_value.start.assert_called_once()
        exporter.shutdown()
        worker.return_value.cancel.assert_called_once()
        worker.return_value.join.assert_called_once()
        exporter.shutdown()
        worker.return_value.join.assert_called_once()

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.PeriodicTask")
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.time.monotonic", return_value=100)
    def test_background_retry_preserves_keys_and_auth_without_new_exports(self, clock, worker):
        now = datetime.datetime(2026, 10, 20, tzinfo=datetime.timezone.utc)
        credential = mock.Mock(spec=["get_token"])
        credential.get_token.return_value = AccessToken("test-token", int(time.time()) + 3600)
        exporter = self._exporter(disable_offline_storage=False, credential=credential)
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request, 429, {"Retry-After": "60"})
        with mock.patch("azure.monitor.opentelemetry.exporter._storage._now", return_value=now):
            result = exporter.export([self._record(key="key-only"), self._record(key="aad-key", auth="aad")])
        self.assertEqual(result, LogRecordExportResult.FAILURE)
        retry = worker.call_args.kwargs["function"]
        self.transport.send.reset_mock()
        suppression = []

        def send(request, **kwargs):
            suppression.append(bool(get_value(_SUPPRESS_INSTRUMENTATION_KEY)))
            return _Response(request)

        self.transport.send.side_effect = send
        clock.return_value = 150
        with mock.patch(
            "azure.monitor.opentelemetry.exporter._storage._now", return_value=now + datetime.timedelta(seconds=61)
        ):
            retry()
            self.transport.send.assert_not_called()
            clock.return_value = 161
            retry()
        self.assertEqual(suppression, [True, True])
        self.assertFalse(get_value(_SUPPRESS_INSTRUMENTATION_KEY))
        requests = [call.args[0] for call in self.transport.send.call_args_list]
        self.assertEqual([json.loads(request.body)[0]["iKey"] for request in requests], ["key-only", "aad-key"])
        self.assertTrue(all(request.url.startswith("https://one.example/proxy/") for request in requests))
        self.assertNotIn("Authorization", requests[0].headers)
        self.assertEqual(requests[1].headers["Authorization"], f"Bearer {credential.get_token.return_value.token}")
        self.assertFalse(list(Path(self.directory.name).rglob("*.lock")))
        self.assertFalse(list(Path(self.directory.name).rglob("*.blob")))

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.PeriodicTask")
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.time.monotonic", return_value=100)
    def test_background_retry_honors_storage_kill_switch(self, clock, worker):
        now = datetime.datetime(2026, 10, 20, tzinfo=datetime.timezone.utc)
        exporter = self._exporter(disable_offline_storage=False)
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request, 429, {"Retry-After": "60"})
        with mock.patch("azure.monitor.opentelemetry.exporter._storage._now", return_value=now):
            self.assertEqual(exporter.export([self._record()]), LogRecordExportResult.FAILURE)
        retry = worker.call_args.kwargs["function"]
        self.transport.send.reset_mock()
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request)
        clock.return_value = 161
        with mock.patch(
            "azure.monitor.opentelemetry.exporter._storage._now", return_value=now + datetime.timedelta(seconds=61)
        ):
            exporter._local_storage_configuration_callback(
                {_ONE_SETTINGS_FEATURE_LOCAL_STORAGE: {"default": "disabled"}}
            )
            retry()
            self.transport.send.assert_not_called()
            exporter._local_storage_configuration_callback(
                {_ONE_SETTINGS_FEATURE_LOCAL_STORAGE: {"default": "enabled"}}
            )
            retry()
        self.transport.send.assert_called_once()

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.PeriodicTask")
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.time.monotonic", return_value=100)
    def test_background_retry_failure_waits_for_next_backoff_window(self, clock, worker):
        now = datetime.datetime(2026, 10, 20, tzinfo=datetime.timezone.utc)
        exporter = self._exporter(disable_offline_storage=False)
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request, 429, {"Retry-After": "60"})
        with mock.patch("azure.monitor.opentelemetry.exporter._storage._now", return_value=now):
            self.assertEqual(exporter.export([self._record(key="stored-key")]), LogRecordExportResult.FAILURE)
        retry = worker.call_args.kwargs["function"]
        clock.return_value = 161
        self.transport.send.reset_mock()
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request, 429, {"Retry-After": "120"})
        with mock.patch(
            "azure.monitor.opentelemetry.exporter._storage._now", return_value=now + datetime.timedelta(seconds=61)
        ):
            retry()
        self.transport.send.assert_called_once()
        self.transport.send.reset_mock()
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request)
        clock.return_value = 200
        retry()
        self.transport.send.assert_not_called()
        clock.return_value = 281
        with mock.patch(
            "azure.monitor.opentelemetry.exporter._storage._now", return_value=now + datetime.timedelta(seconds=181)
        ):
            retry()
        self.transport.send.assert_called_once()
        self.assertEqual(json.loads(self.transport.send.call_args.args[0].body)[0]["iKey"], "stored-key")

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.PeriodicTask")
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.time.monotonic", return_value=100)
    def test_background_retry_shares_foreground_rate_limit(self, clock, worker):
        now = datetime.datetime(2026, 10, 20, tzinfo=datetime.timezone.utc)
        exporter = self._exporter(
            disable_offline_storage=False, storage_min_retry_interval=0, max_envelopes_per_second=1
        )
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request, 429)
        with mock.patch("azure.monitor.opentelemetry.exporter._storage._now", return_value=now):
            self.assertEqual(exporter.export([self._record()]), LogRecordExportResult.FAILURE)
        retry = worker.call_args.kwargs["function"]
        self.transport.send.reset_mock()
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request)
        with mock.patch("azure.monitor.opentelemetry.exporter._storage._now", return_value=now):
            retry()
        self.transport.send.assert_not_called()
        clock.return_value = 101
        with mock.patch(
            "azure.monitor.opentelemetry.exporter._storage._now", return_value=now + datetime.timedelta(seconds=1)
        ):
            retry()
        self.transport.send.assert_called_once()

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.PeriodicTask")
    def test_background_retry_error_does_not_block_other_routes(self, worker):
        exporter = self._exporter(disable_offline_storage=False)
        self.assertEqual(
            exporter.export([self._record(), self._record(endpoint="https://two.example/")]),
            LogRecordExportResult.SUCCESS,
        )
        first, second = exporter._route_exporters.values()
        retry = worker.call_args.kwargs["function"]
        suppression = []

        def fail():
            suppression.append(bool(get_value(_SUPPRESS_INSTRUMENTATION_KEY)))
            raise RuntimeError("test failure")

        with mock.patch.object(first, "_transmit_from_storage", side_effect=fail):
            with mock.patch.object(second, "_transmit_from_storage") as drain:
                with self.assertLogs("azure.monitor.opentelemetry.exporter.export._base", level="ERROR") as logs:
                    retry()
        self.assertIn("test failure", logs.output[0])
        drain.assert_called_once()
        self.assertEqual(suppression, [True])
        self.assertFalse(get_value(_SUPPRESS_INSTRUMENTATION_KEY))

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.PeriodicTask")
    def test_background_retry_does_not_wait_for_export_lock_or_run_after_shutdown(self, worker):
        exporter = self._exporter(disable_offline_storage=False)
        self.assertEqual(exporter.export([self._record()]), LogRecordExportResult.SUCCESS)
        retry = worker.call_args.kwargs["function"]
        completed = threading.Event()

        def tick():
            try:
                retry()
            finally:
                completed.set()

        thread = threading.Thread(target=tick, daemon=True)
        try:
            with exporter._route_lock:
                thread.start()
                self.assertTrue(completed.wait(2), "Retry worker blocked on the export lock.")
        finally:
            thread.join(timeout=2)
        self.assertFalse(thread.is_alive())
        exporter.shutdown()
        self.transport.send.reset_mock()
        retry()
        self.transport.send.assert_not_called()

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.PeriodicTask")
    def test_background_retry_does_not_block_other_routes_and_shutdown_waits(self, worker):
        exporter = self._exporter(disable_offline_storage=False)
        first_record = self._record()
        second_record = self._record(endpoint="https://two.example/")
        self.assertEqual(exporter.export([first_record, second_record]), LogRecordExportResult.SUCCESS)
        first = next(iter(exporter._route_exporters.values()))
        retry = worker.call_args.kwargs["function"]
        retry_started = threading.Event()
        release_retry = threading.Event()
        foreground_done = threading.Event()
        shutdown_started = threading.Event()
        shutdown_done = threading.Event()
        foreground_result = []

        def block_retry():
            retry_started.set()
            release_retry.wait(2)

        def export_healthy_route():
            foreground_result.append(exporter.export([second_record]))
            foreground_done.set()

        def shutdown():
            shutdown_started.set()
            exporter.shutdown()
            shutdown_done.set()

        with mock.patch.object(first, "_transmit_from_storage", side_effect=block_retry):
            retry_thread = threading.Thread(target=retry, daemon=True)
            foreground_thread = threading.Thread(target=export_healthy_route, daemon=True)
            shutdown_thread = threading.Thread(target=shutdown, daemon=True)
            try:
                retry_thread.start()
                self.assertTrue(retry_started.wait(2))
                foreground_thread.start()
                self.assertTrue(foreground_done.wait(2), "An unrelated route was blocked by retry I/O.")
                self.assertEqual(foreground_result, [LogRecordExportResult.SUCCESS])
                shutdown_thread.start()
                self.assertTrue(shutdown_started.wait(2))
                self.assertFalse(shutdown_done.wait(0.1), "Shutdown closed a client during retry I/O.")
            finally:
                release_retry.set()
                retry_thread.join(timeout=2)
                foreground_thread.join(timeout=2)
                shutdown_thread.join(timeout=2)
        self.assertTrue(shutdown_done.is_set())

    def test_real_background_worker_retries_without_new_telemetry(self):
        exporter = self._exporter(
            disable_offline_storage=False, storage_min_retry_interval=0, storage_maintenance_period=1
        )
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request, 429)
        self.assertEqual(exporter.export([self._record()]), LogRecordExportResult.FAILURE)
        worker = exporter._route_retry_task
        route = next(iter(exporter._route_exporters.values()))
        self.assertTrue(worker.is_alive())
        delivered = threading.Event()

        def respond(request, **kwargs):
            delivered.set()
            return _Response(request)

        self.transport.send.side_effect = respond
        self.assertTrue(delivered.wait(5), "Background retry did not transmit stored telemetry.")
        with route._transmit_lock:
            self.assertFalse(list(Path(self.directory.name).rglob("*.blob")))
            self.assertFalse(list(Path(self.directory.name).rglob("*.lock")))
        exporter.shutdown()
        self.assertFalse(worker.is_alive())
