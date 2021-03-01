# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
An example to show an application instrumented with the Opentelemetry requests instrumentations.
Calls made with the requests library will be automatically tracked and telemetry is exported to 
application insights with the AzureMonitorTraceExporter.
"""
import os
import requests
from opentelemetry import trace
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor

from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
RequestsInstrumentor().instrument()
span_processor = BatchExportSpanProcessor(
    AzureMonitorTraceExporter.from_connection_string(
        os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
    )
)
trace.get_tracer_provider().add_span_processor(span_processor)

with tracer.start_as_current_span("parent"):
    response = requests.get("https://azure.microsoft.com/", timeout=5)
