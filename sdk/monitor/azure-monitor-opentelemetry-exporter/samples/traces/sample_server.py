# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# pylint: disable=import-error
# pylint: disable=no-member
# pylint: disable=no-name-in-module
"""
An example to show an application instrumented with the Opentelemetry flask and requests instrumentations.
Calls to the flask application and with the requests library will be automatically tracked and telemetry
is exported to application insights with the AzureMonitorTraceExporter.
"""
import os
import requests
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor

import flask
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

# The preferred tracer implementation must be set, as the opentelemetry-api
# defines the interface with a no-op implementation.
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

exporter = AzureMonitorTraceExporter.from_connection_string(
    os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)

# SpanExporter receives the spans and send them to the target location.
span_processor = BatchExportSpanProcessor(exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Integrations are the glue that binds the OpenTelemetry API and the
# frameworks and libraries that are used together, automatically creating
# Spans and propagating context as appropriate.

# Enable instrumentation in the requests library.
RequestsInstrumentor().instrument()

app = flask.Flask(__name__)
# Enable instrumentation in the flask library.
FlaskInstrumentor().instrument_app(app)


@app.route("/")
def hello():
    with tracer.start_as_current_span("parent"):
        requests.get("https://www.wikipedia.org/wiki/Rabbit")
    return "hello"


if __name__ == "__main__":
    app.run(host="localhost", port=8080, threaded=True)
