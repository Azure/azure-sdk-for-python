# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
An example showing how to add custom measurements to trace telemetry. Entries of the
`microsoft.custom_measurements` attribute populate the `measurements` field of the exported
telemetry. OpenTelemetry attribute values cannot hold maps, so the value is a JSON object
encoded as a string.
"""
# mypy: disable-error-code="attr-defined"
import json
import os

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

exporter = AzureMonitorTraceExporter.from_connection_string(os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"])

tracer_provider = TracerProvider()
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)
tracer_provider.add_span_processor(BatchSpanProcessor(exporter))

custom_measurements = json.dumps({"itemsProcessed": 42.0, "queueDepth": 7})

# Measurements on the span itself
with tracer.start_as_current_span(
    "custom_measurements",
    attributes={"microsoft.custom_measurements": custom_measurements},
) as span:
    # Measurements on a span event
    span.add_event("span event", {"microsoft.custom_measurements": custom_measurements})

tracer_provider.force_flush()
