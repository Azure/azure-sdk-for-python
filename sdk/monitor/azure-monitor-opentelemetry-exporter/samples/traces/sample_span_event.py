# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
An example to show an application using custom events. Events are added
to the span and exported via the AzureMonitorTraceExporter.
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

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
span_processor = BatchSpanProcessor(exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Message events
with tracer.start_as_current_span("hello") as span:
    span.add_event("Custom event", {"test": "attributes"})
    print("Hello, World!")

# Exception events
try:
    with tracer.start_as_current_span("hello") as span:
        raise Exception("Custom exception message.")
except Exception:
    print("Exception raised")
