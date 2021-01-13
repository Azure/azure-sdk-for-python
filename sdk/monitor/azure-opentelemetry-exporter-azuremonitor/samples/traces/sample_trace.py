# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor

from azure.opentelemetry.exporter.azuremonitor import AzureMonitorTraceExporter


exporter = AzureMonitorTraceExporter(
    connection_string = os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
span_processor = BatchExportSpanProcessor(exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

with tracer.start_as_current_span("hello"):
    print("Hello, World!")

input("Press any key to exit...")
