# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# mypy: disable-error-code="attr-defined"
import os

from django.http import HttpResponse

from opentelemetry import trace
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

# Enable instrumentation in the django library.
DjangoInstrumentor().instrument()

trace.set_tracer_provider(TracerProvider())
span_processor = BatchSpanProcessor(
    AzureMonitorTraceExporter.from_connection_string(
        os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
    )
)
trace.get_tracer_provider().add_span_processor(span_processor)

def index(request):
    return HttpResponse("Hello, world.")
