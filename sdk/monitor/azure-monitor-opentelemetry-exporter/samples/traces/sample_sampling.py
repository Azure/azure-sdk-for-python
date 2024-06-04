# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
An example to show an application using the ApplicationInsightsSampler to enable sampling for your telemetry.
Specify a sampling rate for the sampler to limit the amount of telemetry records you receive. Custom dependencies
 are tracked via spans and telemetry is exported to application insights with the AzureMonitorTraceExporter.
"""
# mypy: disable-error-code="attr-defined"
import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from azure.monitor.opentelemetry.exporter import (
    ApplicationInsightsSampler,
    AzureMonitorTraceExporter,
)

# Sampler expects a sample rate of between 0 and 1 inclusive
# A rate of 0.75 means approximately 75% of your telemetry will be sent
sampler = ApplicationInsightsSampler(0.75)
trace.set_tracer_provider(TracerProvider(sampler=sampler))
tracer = trace.get_tracer(__name__)
exporter = AzureMonitorTraceExporter(
    connection_string=os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)
span_processor = BatchSpanProcessor(exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

for i in range(100):
    # Approximately 25% of these spans should be sampled out
    with tracer.start_as_current_span("hello"):
        print("Hello, World!")

input()
