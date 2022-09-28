# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
An example to show an application instrumented with the OpenTelemetry flask instrumentation.
Calls made with the flask library will be automatically tracked and telemetry is exported to 
application insights with the AzureMonitorTraceExporter.
See more info on the flask instrumentation here:
https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation/opentelemetry-instrumentation-flask
"""
import os
import flask

from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

# Enable instrumentation in the flask library.
FlaskInstrumentor().instrument()
app = flask.Flask(__name__)

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
span_processor = BatchSpanProcessor(
    AzureMonitorTraceExporter.from_connection_string(
        os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
    )
)
trace.get_tracer_provider().add_span_processor(span_processor)

@app.route("/")
def test():
    return "Test flask request"

if __name__ == "__main__":
    app.run(host="localhost", port=8080, threaded=True)
