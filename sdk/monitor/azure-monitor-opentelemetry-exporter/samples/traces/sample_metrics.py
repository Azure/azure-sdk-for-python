# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
An example to show an application instrumented with the OpenTelemetry instrumentations that collect metrics.
Only certain instrumentations support metrics collection, refer to https://github.com/open-telemetry/opentelemetry-python-contrib/blob/main/instrumentation/README.md
for the full list. Calls made with the underlying instrumented libraries will track metrics information in the
metrics explorer view in Application Insights.
"""
# mypy: disable-error-code="attr-defined"
import flask
import os
import requests
from opentelemetry import metrics, trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from azure.monitor.opentelemetry.exporter import (
    AzureMonitorMetricExporter,
    AzureMonitorTraceExporter,
)

# Enable metrics collection with instrumentation
exporter = AzureMonitorMetricExporter.from_connection_string(
    os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"],
    instrumentation_collection=True,
)
# Metrics are reported every 1 minute
reader = PeriodicExportingMetricReader(exporter)
metrics.set_meter_provider(MeterProvider(metric_readers=[reader]))

# Enable instrumentation in the requests library.
RequestsInstrumentor().instrument()

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
    success_response = requests.get("https://httpstat.us/200", timeout=5)
    failure_response = requests.get("https://httpstat.us/404", timeout=5)
    return "Test flask request"

if __name__ == "__main__":
    app.run(host="localhost", port=8080, threaded=True)
