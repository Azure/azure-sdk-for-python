# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import json
import os
import platform
import shutil
import unittest
from unittest import mock
from functools import partial

# pylint: disable=import-error
from opentelemetry.semconv.attributes.exception_attributes import (
    EXCEPTION_MESSAGE,
    EXCEPTION_STACKTRACE,
    EXCEPTION_TYPE,
)
from opentelemetry.sdk import _logs
from opentelemetry._logs import LogRecord
from opentelemetry.sdk.util.instrumentation import InstrumentationScope
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk._logs.export import LogRecordExportResult
from opentelemetry._logs.severity import SeverityNumber
from opentelemetry.trace import set_span_in_context, SpanContext, NonRecordingSpan

from azure.monitor.opentelemetry.exporter.export._base import ExportResult
from azure.monitor.opentelemetry.exporter.export.logs._exporter import (
    AzureMonitorLogExporter,
    _get_log_export_result,
    _get_severity_level,
)
from azure.monitor.opentelemetry.exporter._constants import (
    _APPLICATION_INSIGHTS_EVENT_MARKER_ATTRIBUTE,
    _MICROSOFT_CUSTOM_EVENT_NAME,
    _DEFAULT_LOG_MESSAGE,
)
from azure.monitor.opentelemetry.exporter._generated.models import ContextTagKeys
from azure.monitor.opentelemetry.exporter._utils import (
    azure_monitor_context,
    ns_to_iso_str,
)


def throw(exc_type, *args, **kwargs):
    def func(*_args, **_kwargs):
        raise exc_type(*args, **kwargs)

    return func


class NotSerializeableClass:
    def __str__(self) -> str:
        return "This class is not serializeable"


# pylint: disable=import-error
# pylint: disable=protected-access
# pylint: disable=too-many-lines
class TestAzureLogExporter(unittest.TestCase):
    _exporter_class = AzureMonitorLogExporter

    @classmethod
    def setUpClass(cls):
        os.environ.pop("APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL", None)
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
            resource=Resource.create(attributes={"asd": "test_resource"}),
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
            instrumentation_scope=InstrumentationScope("test_name"),
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
            instrumentation_scope=InstrumentationScope("test_name"),
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
        self.assertEqual(envelope.time, ns_to_iso_str(record.timestamp))
        self.assertEqual(envelope.data.base_type, "MessageData")
        self.assertEqual(envelope.data.base_data.message, record.body)
        self.assertEqual(envelope.data.base_data.severity_level, 2)
        self.assertEqual(envelope.data.base_data.properties["test"], "attribute")

    def test_log_to_envelope_user_fields(self):
        exporter = self._exporter
        envelope = exporter._log_to_envelope(self._log_data_user_fields)

        self.assertEqual(envelope.tags.get(ContextTagKeys.AI_USER_AUTH_USER_ID), "test-auth")
        self.assertEqual(envelope.tags.get(ContextTagKeys.AI_USER_ID), "test-user")
        self.assertNotIn("enduser.id", envelope.data.base_data.properties)
        self.assertNotIn("enduser.pseudo.id", envelope.data.base_data.properties)

    def test_log_to_envelope_log_none(self):
        exporter = self._exporter
        envelope = exporter._log_to_envelope(self._log_data_none)
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Message")
        self.assertEqual(envelope.data.base_type, "MessageData")
        self.assertEqual(envelope.data.base_data.message, _DEFAULT_LOG_MESSAGE)

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
        self.assertEqual(envelope.time, ns_to_iso_str(record.timestamp))
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
        self.assertEqual(envelope.time, ns_to_iso_str(record.timestamp))
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
        self.assertEqual(envelope.time, ns_to_iso_str(record.timestamp))
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
        self.assertEqual(envelope.time, ns_to_iso_str(record.timestamp))
        self.assertEqual(envelope.data.base_type, "ExceptionData")
        self.assertEqual(envelope.data.base_data.severity_level, 4)
        self.assertEqual(envelope.data.base_data.properties["test"], "attribute")
        self.assertEqual(len(envelope.data.base_data.exceptions), 1)
        self.assertEqual(envelope.data.base_data.exceptions[0].type_name, "Exception")
        self.assertEqual(envelope.data.base_data.exceptions[0].message, "test exception")
        self.assertTrue(envelope.data.base_data.exceptions[0].has_full_stack)
        self.assertEqual(envelope.data.base_data.exceptions[0].stack, "")

    def test_log_to_envelope_event(self):
        exporter = self._exporter
        envelope = exporter._log_to_envelope(self._log_data_event)
        record = self._log_data_event.log_record
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Event")
        self.assertEqual(envelope.time, ns_to_iso_str(record.timestamp))
        self.assertEqual(envelope.data.base_type, "EventData")
        self.assertEqual(envelope.data.base_data.name, record.body)
        self.assertEqual(envelope.data.base_data.properties["event_key"], "event_attribute")

    def test_log_to_envelope_event_complex_body(self):
        exporter = self._exporter
        envelope = exporter._log_to_envelope(self._log_data_event_complex_body)
        record = self._log_data_event_complex_body.log_record
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Event")
        self.assertEqual(envelope.time, ns_to_iso_str(record.timestamp))
        self.assertEqual(envelope.data.base_type, "EventData")
        self.assertEqual(envelope.data.base_data.name, json.dumps(record.body))
        self.assertEqual(envelope.data.base_data.properties["event_key"], "event_attribute")

    def test_log_to_envelope_event_complex_body_not_serializeable(self):
        exporter = self._exporter
        envelope = exporter._log_to_envelope(self._log_data_event_complex_body_not_serializeable)
        record = self._log_data_event_complex_body_not_serializeable.log_record
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Event")
        self.assertEqual(envelope.time, ns_to_iso_str(record.timestamp))
        self.assertEqual(envelope.data.base_type, "EventData")
        self.assertEqual(envelope.data.base_data.name, str(record.body))
        self.assertEqual(envelope.data.base_data.properties["event_key"], "event_attribute")

    def test_log_to_envelope_custom_event(self):
        exporter = self._exporter
        envelope = exporter._log_to_envelope(self._log_data_custom_event)
        record = self._log_data_custom_event.log_record
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Event")
        self.assertEqual(envelope.tags["ai.location.ip"], "192.168.1.1")
        self.assertEqual(envelope.time, ns_to_iso_str(record.timestamp))
        self.assertEqual(envelope.data.base_type, "EventData")
        self.assertEqual(envelope.data.base_data.name, "event_name")
        self.assertEqual(envelope.data.base_data.properties["event_key"], "event_attribute")

    def test_log_to_envelope_timestamp(self):
        exporter = self._exporter
        old_record = self._log_data.log_record
        self._log_data.log_record.timestamp = None
        self._log_data.log_record.observed_timestamp = 1646865018558419457
        envelope = exporter._log_to_envelope(self._log_data)
        record = self._log_data.log_record
        self.assertEqual(envelope.time, ns_to_iso_str(record.observed_timestamp))
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
            print(num)
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
