# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any, Optional, TextIO, Union, cast

import io
import logging
import sys

from enum import Enum

from azure.core.tracing import AbstractSpan, SpanKind  # type: ignore
from azure.core.settings import settings  # type: ignore

try:
    from opentelemetry.trace import StatusCode, Span  # noqa: F401 # pylint: disable=unused-import

    _span_impl_type = settings.tracing_implementation()  # pylint: disable=not-callable
except ModuleNotFoundError:
    _span_impl_type = None

logger = logging.getLogger(__name__)


GEN_AI_MESSAGE_ID = "gen_ai.message.id"
GEN_AI_MESSAGE_STATUS = "gen_ai.message.status"
GEN_AI_THREAD_ID = "gen_ai.thread.id"
GEN_AI_THREAD_RUN_ID = "gen_ai.thread.run.id"
GEN_AI_AGENT_ID = "gen_ai.agent.id"
GEN_AI_AGENT_NAME = "gen_ai.agent.name"
GEN_AI_AGENT_DESCRIPTION = "gen_ai.agent.description"
GEN_AI_OPERATION_NAME = "gen_ai.operation.name"
GEN_AI_THREAD_RUN_STATUS = "gen_ai.thread.run.status"
GEN_AI_REQUEST_MODEL = "gen_ai.request.model"
GEN_AI_REQUEST_TEMPERATURE = "gen_ai.request.temperature"
GEN_AI_REQUEST_TOP_P = "gen_ai.request.top_p"
GEN_AI_REQUEST_MAX_INPUT_TOKENS = "gen_ai.request.max_input_tokens"
GEN_AI_REQUEST_MAX_OUTPUT_TOKENS = "gen_ai.request.max_output_tokens"
GEN_AI_RESPONSE_MODEL = "gen_ai.response.model"
GEN_AI_SYSTEM = "gen_ai.system"
SERVER_ADDRESS = "server.address"
AZ_AI_AGENT_SYSTEM = "az.ai.agents"
GEN_AI_TOOL_NAME = "gen_ai.tool.name"
GEN_AI_TOOL_CALL_ID = "gen_ai.tool.call.id"
GEN_AI_REQUEST_RESPONSE_FORMAT = "gen_ai.request.response_format"
GEN_AI_USAGE_INPUT_TOKENS = "gen_ai.usage.input_tokens"
GEN_AI_USAGE_OUTPUT_TOKENS = "gen_ai.usage.output_tokens"
GEN_AI_SYSTEM_MESSAGE = "gen_ai.system.message"
GEN_AI_EVENT_CONTENT = "gen_ai.event.content"
GEN_AI_RUN_STEP_START_TIMESTAMP = "gen_ai.run_step.start.timestamp"
GEN_AI_RUN_STEP_END_TIMESTAMP = "gen_ai.run_step.end.timestamp"
GEN_AI_RUN_STEP_STATUS = "gen_ai.run_step.status"
ERROR_TYPE = "error.type"
ERROR_MESSAGE = "error.message"


class OperationName(Enum):
    CREATE_AGENT = "create_agent"
    CREATE_THREAD = "create_thread"
    CREATE_MESSAGE = "create_message"
    START_THREAD_RUN = "start_thread_run"
    GET_THREAD_RUN = "get_thread_run"
    EXECUTE_TOOL = "execute_tool"
    LIST_MESSAGES = "list_messages"
    LIST_RUN_STEPS = "list_run_steps"
    SUBMIT_TOOL_OUTPUTS = "submit_tool_outputs"
    PROCESS_THREAD_RUN = "process_thread_run"


def trace_tool_execution(
    tool_call_id: str,
    tool_name: str,
    thread_id: Optional[str] = None,  # TODO: would be nice to have this, but need to propagate somehow
    agent_id: Optional[str] = None,  # TODO: would be nice to have this, but need to propagate somehow
    run_id: Optional[str] = None,  # TODO: would be nice to have this, but need to propagate somehow
) -> "Optional[AbstractSpan]":
    span = start_span(
        OperationName.EXECUTE_TOOL,
        server_address=None,
        span_name=f"execute_tool {tool_name}",
        thread_id=thread_id,
        agent_id=agent_id,
        run_id=run_id,
        gen_ai_system=None,
    )  # it's a client code execution, not GenAI span
    if span is not None and span.span_instance.is_recording:
        span.add_attribute(GEN_AI_TOOL_CALL_ID, tool_call_id)
        span.add_attribute(GEN_AI_TOOL_NAME, tool_name)

    return span


def start_span(
    operation_name: OperationName,
    server_address: Optional[str],
    span_name: Optional[str] = None,
    thread_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    run_id: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    max_prompt_tokens: Optional[int] = None,
    max_completion_tokens: Optional[int] = None,
    response_format: Optional[str] = None,
    gen_ai_system: Optional[str] = AZ_AI_AGENT_SYSTEM,
    kind: SpanKind = SpanKind.CLIENT,
) -> "Optional[AbstractSpan]":
    global _span_impl_type  # pylint: disable=global-statement
    if _span_impl_type is None:
        # Try to reinitialize the span implementation type.
        # This is a workaround for the case when the tracing implementation is not set up yet when the agent telemetry is imported.
        # This code should not even get called if settings.tracing_implementation() returns None since that is also checked in
        # _trace_sync_function and _trace_async_function functions in the AIAgentsInstrumentor.
        _span_impl_type = settings.tracing_implementation()  # pylint: disable=not-callable
        if _span_impl_type is None:
            return None

    span = _span_impl_type(name=span_name or operation_name.value, kind=kind)

    if span and span.span_instance.is_recording:
        if gen_ai_system:
            span.add_attribute(GEN_AI_SYSTEM, AZ_AI_AGENT_SYSTEM)

        span.add_attribute(GEN_AI_OPERATION_NAME, operation_name.value)

        if server_address:
            span.add_attribute(SERVER_ADDRESS, server_address)

        if thread_id:
            span.add_attribute(GEN_AI_THREAD_ID, thread_id)

        if agent_id:
            span.add_attribute(GEN_AI_AGENT_ID, agent_id)

        if run_id:
            span.add_attribute(GEN_AI_THREAD_RUN_ID, run_id)

        if model:
            span.add_attribute(GEN_AI_REQUEST_MODEL, model)

        if temperature:
            span.add_attribute(GEN_AI_REQUEST_TEMPERATURE, str(temperature))

        if top_p:
            span.add_attribute(GEN_AI_REQUEST_TOP_P, str(top_p))

        if max_prompt_tokens:
            span.add_attribute(GEN_AI_REQUEST_MAX_INPUT_TOKENS, max_prompt_tokens)

        if max_completion_tokens:
            span.add_attribute(GEN_AI_REQUEST_MAX_OUTPUT_TOKENS, max_completion_tokens)

        if response_format:
            span.add_attribute(GEN_AI_REQUEST_RESPONSE_FORMAT, response_format)

    return span


# Internal helper functions to enable OpenTelemetry, used by both sync and async clients
def _get_trace_exporter(destination: Union[TextIO, str, None]) -> Any:
    if isinstance(destination, str):
        # `destination` is the OTLP endpoint
        # See: https://opentelemetry-python.readthedocs.io/en/latest/exporter/otlp/otlp.html#usage
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter  # type: ignore
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                "OpenTelemetry OTLP exporter is not installed. "
                + "Please install it using 'pip install opentelemetry-exporter-otlp-proto-grpc'"
            ) from e
        return OTLPSpanExporter(endpoint=destination)

    if isinstance(destination, io.TextIOWrapper):
        if destination is sys.stdout:
            # See: https://opentelemetry-python.readthedocs.io/en/latest/sdk/trace.export.html#opentelemetry.sdk.trace.export.ConsoleSpanExporter # pylint: disable=line-too-long
            try:
                from opentelemetry.sdk.trace.export import ConsoleSpanExporter
            except ModuleNotFoundError as e:
                raise ModuleNotFoundError(
                    "OpenTelemetry SDK is not installed. Please install it using 'pip install opentelemetry-sdk'"
                ) from e

            return ConsoleSpanExporter()
        raise ValueError("Only `sys.stdout` is supported at the moment for type `TextIO`")

    return None


def _get_log_exporter(destination: Union[TextIO, str, None]) -> Any:
    if isinstance(destination, str):
        # `destination` is the OTLP endpoint
        # See: https://opentelemetry-python.readthedocs.io/en/latest/exporter/otlp/otlp.html#usage
        try:
            # _logs are considered beta (not internal) in OpenTelemetry Python API/SDK.
            # So it's ok to use it for local development, but we'll swallow
            # any errors in case of any breaking changes on OTel side.
            from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter  # type: ignore  # pylint: disable=import-error,no-name-in-module
        except Exception as ex:  # pylint: disable=broad-exception-caught
            # since OTel logging is still in beta in Python, we're going to swallow any errors
            # and just warn about them.
            logger.warning("Failed to configure OpenTelemetry logging.", exc_info=ex)
            return None

        return OTLPLogExporter(endpoint=destination)

    if isinstance(destination, io.TextIOWrapper):
        if destination is sys.stdout:
            # See: https://opentelemetry-python.readthedocs.io/en/latest/sdk/trace.export.html#opentelemetry.sdk.trace.export.ConsoleSpanExporter # pylint: disable=line-too-long
            try:
                from opentelemetry.sdk._logs.export import ConsoleLogExporter

                return ConsoleLogExporter()
            except ModuleNotFoundError as ex:
                # since OTel logging is still in beta in Python, we're going to swallow any errors
                # and just warn about them.
                logger.warning("Failed to configure OpenTelemetry logging.", exc_info=ex)
            return None
        raise ValueError("Only `sys.stdout` is supported at the moment for type `TextIO`")

    return None


def _configure_tracing(span_exporter: Any) -> None:
    if span_exporter is None:
        return

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(
            "OpenTelemetry SDK is not installed. Please install it using 'pip install opentelemetry-sdk'"
        ) from e

    # if tracing was not setup before, we need to create a new TracerProvider
    if not isinstance(trace.get_tracer_provider(), TracerProvider):
        # If the provider is NoOpTracerProvider, we need to create a new TracerProvider
        provider = TracerProvider()
        trace.set_tracer_provider(provider)

    # get_tracer_provider returns opentelemetry.trace.TracerProvider
    # however, we have opentelemetry.sdk.trace.TracerProvider, which implements
    # add_span_processor method, though we need to cast it to fix type checking.
    provider = cast(TracerProvider, trace.get_tracer_provider())
    provider.add_span_processor(SimpleSpanProcessor(span_exporter))


def _configure_logging(log_exporter: Any) -> None:
    if log_exporter is None:
        return

    try:
        # _events and _logs are considered beta (not internal) in
        # OpenTelemetry Python API/SDK.
        # So it's ok to use them for local development, but we'll swallow
        # any errors in case of any breaking changes on OTel side.
        from opentelemetry import _logs, _events
        from opentelemetry.sdk._logs import LoggerProvider  # pylint: disable=import-error,no-name-in-module
        from opentelemetry.sdk._events import EventLoggerProvider  # pylint: disable=import-error,no-name-in-module
        from opentelemetry.sdk._logs.export import (
            SimpleLogRecordProcessor,
        )  # pylint: disable=import-error,no-name-in-module

        if not isinstance(_logs.get_logger_provider(), LoggerProvider):
            logger_provider = LoggerProvider()
            _logs.set_logger_provider(logger_provider)

        # get_logger_provider returns opentelemetry._logs.LoggerProvider
        # however, we have opentelemetry.sdk._logs.LoggerProvider, which implements
        # add_log_record_processor method, though we need to cast it to fix type checking.
        logger_provider = cast(LoggerProvider, _logs.get_logger_provider())
        logger_provider.add_log_record_processor(SimpleLogRecordProcessor(log_exporter))
        _events.set_event_logger_provider(EventLoggerProvider(logger_provider))
    except Exception as ex:  # pylint: disable=broad-exception-caught
        # since OTel logging is still in beta in Python, we're going to swallow any errors
        # and just warn about them.
        logger.warning("Failed to configure OpenTelemetry logging.", exc_info=ex)


def enable_telemetry(destination: Union[TextIO, str, None] = None, **kwargs) -> None:  # pylint: disable=unused-argument
    """Enable tracing and logging to console (sys.stdout), or to an OpenTelemetry Protocol (OTLP) endpoint.

    :param destination: `sys.stdout` to print telemetry to console or a string holding the
        OpenTelemetry protocol (OTLP) endpoint.
        If not provided, this method enables instrumentation, but does not configure OpenTelemetry
        SDK to export traces and logs.
    :type destination: Union[TextIO, str, None]
    """
    span_exporter = _get_trace_exporter(destination)
    _configure_tracing(span_exporter)

    log_exporter = _get_log_exporter(destination)
    _configure_logging(log_exporter)

    try:
        from azure.ai.agents.telemetry import AIAgentsInstrumentor

        agents_instrumentor = AIAgentsInstrumentor()
        if not agents_instrumentor.is_instrumented():
            agents_instrumentor.instrument()
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.warning("Could not call `AIAgentsInstrumentor().instrument()`", exc_info=exc)
