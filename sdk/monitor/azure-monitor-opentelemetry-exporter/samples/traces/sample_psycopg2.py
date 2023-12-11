# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# cSpell:disable
"""
An example to show an application instrumented with the OpenTelemetry psycopg2 instrumentation.
Calls made with the flask library will be automatically tracked and telemetry is exported to 
application insights with the AzureMonitorTraceExporter.
See more info on the psycopg2 instrumentation here:
https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation/opentelemetry-instrumentation-psycopg2
"""
# mypy: disable-error-code="attr-defined"
import os
import psycopg2

from opentelemetry import trace
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

# Enable instrumentation in the psycopg2 library.
Psycopg2Instrumentor().instrument()

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
span_processor = BatchSpanProcessor(
    AzureMonitorTraceExporter.from_connection_string(
        os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
    )
)
trace.get_tracer_provider().add_span_processor(span_processor)

cnx = psycopg2.connect(database='test', user="<user>", password="<password>")
cursor = cnx.cursor()
cursor.execute("INSERT INTO test_tables (test_field) VALUES (123)")
cursor.close()
cnx.close()

# cSpell:enable
