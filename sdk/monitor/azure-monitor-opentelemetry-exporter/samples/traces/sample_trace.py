# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
An example to show an application using Opentelemetry tracing api and sdk. Custom dependencies are
tracked via spans and telemetry is exported to application insights with the AzureMonitorTraceExporter.
"""
# mypy: disable-error-code="attr-defined"
import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

exporter = AzureMonitorTraceExporter.from_connection_string(
    os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)

tracer_provider = TracerProvider()
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)
span_processor = BatchSpanProcessor(exporter, schedule_delay_millis=60000)
trace.get_tracer_provider().add_span_processor(span_processor)

with tracer.start_as_current_span("hello"):
    print("Hello, World!")

# Telemetry records are flushed automatically upon application exit
# If you would like to flush records manually yourself, you can call force_flush()
tracer_provider.force_flush()
