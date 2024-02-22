# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# cSpell:disable
"""
ASGI config for sample project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from opentelemetry import trace
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sample.settings')

# Azure Monitor OpenTelemetry Exporters and Django Instrumentation should only be set up once in either asgi.py, wsgi.py, or manage.py, depending on startup method.
# If using manage.py, please remove setup from asgi.py and wsgi.py
# Enable instrumentation in the django library.
DjangoInstrumentor().instrument()
# Set up Azure Monitor OpenTelemetry Exporter
trace.set_tracer_provider(TracerProvider())
span_processor = BatchSpanProcessor(
    AzureMonitorTraceExporter.from_connection_string(
        os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
    )
)
trace.get_tracer_provider().add_span_processor(span_processor)

application = get_asgi_application()

# cSpell:enable
