# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: disable=line-too-long,R,no-member
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import io
import logging
import sys
from typing import Union, Any, TextIO, cast

logger = logging.getLogger(__name__)


# TODO: what about `set AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED=true`?
def enable_telemetry(
    *, destination: Union[TextIO, str, None] = None, **kwargs  # pylint: disable=unused-argument
) -> None:
    """Enables telemetry collection with OpenTelemetry for Azure AI clients and popular GenAI libraries.

    Following instrumentations are enabled (when corresponding packages are installed):

    - Azure AI Agents (`azure-ai-agents`)
    - Azure AI Inference (`azure-ai-inference`)
    - OpenAI (`opentelemetry-instrumentation-openai-v2`)
    - Langchain (`opentelemetry-instrumentation-langchain`)

    The recording of prompt and completion messages is disabled by default. To enable it, set the
    `AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED` environment variable to `true`.

    When destination is provided, the method configures OpenTelemetry SDK to export traces to
    stdout or OTLP (OpenTelemetry protocol) gRPC endpoint. It's recommended for local
    development only. For production use, make sure to configure OpenTelemetry SDK directly.

    :keyword destination: Recommended for local testing only. Set it to `sys.stdout` for
        tracing to console output, or a string holding the OpenTelemetry protocol (OTLP)
        endpoint such as "http://localhost:4317.
        If not provided, the method enables instrumentations, but does not configure OpenTelemetry
        SDK to export traces.
    :paramtype destination: Union[TextIO, str, None]
    """
    span_exporter = _get_trace_exporter(destination)
    _configure_tracing(span_exporter)

    log_exporter = _get_log_exporter(destination)
    _configure_logging(log_exporter)

    # Silently try to load a set of relevant Instrumentors
    try:
        from azure.core.settings import settings

        settings.tracing_implementation = "opentelemetry"
    except ModuleNotFoundError:
        logger.warning(
            "Azure SDK tracing plugin is not installed. "
            + "Please install it using 'pip install azure-core-tracing-opentelemetry'"
        )

    try:
        from azure.ai.inference.tracing import AIInferenceInstrumentor  # type: ignore

        inference_instrumentor = AIInferenceInstrumentor()
        if not inference_instrumentor.is_instrumented():
            inference_instrumentor.instrument()
    except ModuleNotFoundError:
        logger.warning(
            "Could not call `AIInferenceInstrumentor().instrument()` since `azure-ai-inference` is not installed"
        )

    try:
        from azure.ai.agents.tracing import AIAgentsInstrumentor  # pylint: disable=import-error,no-name-in-module

        agents_instrumentor = AIAgentsInstrumentor()
        if not agents_instrumentor.is_instrumented():
            agents_instrumentor.instrument()
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.warning("Could not call `AIAgentsInstrumentor().instrument()`", exc_info=exc)

    try:
        from opentelemetry.instrumentation.openai_v2 import OpenAIInstrumentor  # type: ignore

        OpenAIInstrumentor().instrument()
    except ModuleNotFoundError:
        logger.warning(
            "Could not call `OpenAIInstrumentor().instrument()` since "
            + "`opentelemetry-instrumentation-openai-v2` is not installed"
        )

    try:
        from opentelemetry.instrumentation.langchain import LangchainInstrumentor  # type: ignore

        print("Calling LangchainInstrumentor().instrument()")
        LangchainInstrumentor().instrument()
    except ModuleNotFoundError:
        logger.warning(
            "Could not call LangchainInstrumentor().instrument()` since "
            + "`opentelemetry-instrumentation-langchain` is not installed"
        )


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
        from opentelemetry import _logs, _events  # pylint: disable=import-error
        from opentelemetry.sdk._logs import LoggerProvider  # pylint: disable=import-error,no-name-in-module
        from opentelemetry.sdk._events import EventLoggerProvider  # pylint: disable=import-error,no-name-in-module
        from opentelemetry.sdk._logs.export import (  # pylint: disable=import-error
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
