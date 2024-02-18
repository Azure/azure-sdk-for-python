# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

from opentelemetry import trace
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter


def main():
    """Run administrative tasks."""
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

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
