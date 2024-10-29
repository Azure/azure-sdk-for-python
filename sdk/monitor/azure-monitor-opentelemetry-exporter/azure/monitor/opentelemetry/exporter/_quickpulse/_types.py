# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# pylint: disable=protected-access
from dataclasses import dataclass
from typing import Dict, no_type_check

from opentelemetry.sdk._logs import LogRecord
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import SpanKind

from azure.monitor.opentelemetry.exporter.export.trace import _utils as trace_utils


@dataclass
class _TelemetryData:
    custom_dimensions: Dict[str, str]

    @staticmethod
    def _from_span(span: ReadableSpan):
        if span.kind in (SpanKind.SERVER, SpanKind.CONSUMER):
            return _RequestData._from_span(span)
        return _DependencyData._from_span(span)

    @staticmethod
    @no_type_check
    def _from_log_record(log_record: LogRecord):
        exc_type = log_record.attributes.get(SpanAttributes.EXCEPTION_TYPE)
        exc_message = log_record.attributes.get(SpanAttributes.EXCEPTION_MESSAGE)
        if exc_type is not None or exc_message is not None:
            return _ExceptionData._from_log_record(log_record)
        return _TraceData._from_log_record(log_record)


@dataclass
class _RequestData(_TelemetryData):
    duration: float
    success: bool
    name: str
    response_code: int
    url: str

    @staticmethod
    @no_type_check
    def _from_span(span: ReadableSpan):
        # Logic should match that of exporter to Breeze
        url = ""
        duration_ms = 0
        response_code = 0
        success = True
        attributes = {}  # type: ignore
        if span.end_time and span.start_time:
            duration_ms = (span.end_time - span.start_time) / 1e9  # type: ignore
        if span.attributes:
            attributes = span.attributes  # type: ignore
            url = span.attributes.get(SpanAttributes.HTTP_URL, "")  # type: ignore
            # TODO: get url for http requests
            status_code = span.attributes.get(SpanAttributes.HTTP_STATUS_CODE)
            if status_code:
                try:
                    status_code = int(status_code)  # type: ignore
                except ValueError:
                    status_code = 0
            else:
                status_code = 0
            success = span.status.is_ok and status_code and status_code not in range(400, 500)  # type: ignore
            response_code = status_code
        return _RequestData(
            duration=duration_ms,
            success=success,
            name=span.name,
            response_code=response_code,
            url=str(url),
            custom_dimensions=attributes,
        )


@dataclass
class _DependencyData(_TelemetryData):
    duration: float
    success: bool
    name: str
    result_code: int
    target: str
    type: str
    data: str

    @staticmethod
    @no_type_check
    def _from_span(span: ReadableSpan):
        # Logic should match that of exporter to Breeze
        url = ""
        duration_ms = 0
        result_code = 0
        attributes = {}  # type: ignore
        dependency_type = ""
        data = ""
        target = trace_utils._get_target_for_dependency_from_peer(span.attributes)
        if SpanAttributes.HTTP_METHOD in span.attributes:  # type: ignore
            dependency_type = "HTTP"
            url = trace_utils._get_url_for_http_dependency(span.attributes)  # type: ignore
            target, _ = trace_utils._get_target_and_path_for_http_dependency(
                span.attributes,
                target,
                url,
            )
            data = url
        elif SpanAttributes.DB_SYSTEM in span.attributes:  # type: ignore
            db_system = span.attributes[SpanAttributes.DB_SYSTEM]  # type: ignore
            dependency_type = db_system  # type: ignore
            target = trace_utils._get_target_for_db_dependency(
                target,  # type: ignore
                db_system,  # type: ignore
                span.attributes,
            )
            if SpanAttributes.DB_STATEMENT in span.attributes:  # type: ignore
                data = span.attributes[SpanAttributes.DB_STATEMENT]  # type: ignore
            elif SpanAttributes.DB_OPERATION in span.attributes:  # type: ignore
                data = span.attributes[SpanAttributes.DB_OPERATION]  # type: ignore
        elif SpanAttributes.MESSAGING_SYSTEM in span.attributes:  # type: ignore
            dependency_type = span.attributes[SpanAttributes.MESSAGING_SYSTEM]  # type: ignore
            target = trace_utils._get_target_for_messaging_dependency(
                target,  # type: ignore
                span.attributes,
            )
        elif SpanAttributes.RPC_SYSTEM in span.attributes:
            dependency_type = span.attributes[SpanAttributes.RPC_SYSTEM]
            target = trace_utils._get_target_for_rpc_dependency(
                target,  # type: ignore
                span.attributes,
            )
        elif span.kind is SpanKind.PRODUCER:
            dependency_type = "Queue Message"
            msg_system = span.attributes.get(SpanAttributes.MESSAGING_SYSTEM)
            if msg_system:
                dependency_type += " | {}".format(msg_system)
        else:
            dependency_type = "InProc"

        return _DependencyData(
            duration=duration_ms,
            success=span.status.is_ok,
            name=span.name,
            result_code=result_code,
            target=target,
            type=str(dependency_type),
            data=data,
            custom_dimensions=attributes,
        )


@dataclass
class _ExceptionData(_TelemetryData):
    message: str
    stack_trace: str

    @staticmethod
    @no_type_check
    def _from_log_record(log_record: LogRecord):
        return _ExceptionData(
            message=str(log_record.attributes.get(SpanAttributes.EXCEPTION_MESSAGE, "")),
            stack_trace=str(log_record.attributes.get(SpanAttributes.EXCEPTION_STACKTRACE, "")),
            custom_dimensions=log_record.attributes,
        )


@dataclass
class _TraceData(_TelemetryData):
    message: str

    @staticmethod
    @no_type_check
    def _TraceData(log_record: LogRecord):
        return _TraceData(
            message=str(log_record.body),
            custom_dimensions=log_record.attributes,
        )
