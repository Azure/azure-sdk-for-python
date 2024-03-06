# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# cSpell:disable
import flask
import os
import logging
import time
import requests

from azure.monitor.opentelemetry.exporter._quickpulse._live_metrics import enable_live_metrics
from azure.monitor.opentelemetry.exporter._quickpulse._log_record_processor import _QuickpulseLogRecordProcessor
from azure.monitor.opentelemetry.exporter._quickpulse._span_processor import _QuickpulseSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

from opentelemetry._logs import (
    get_logger_provider,
    set_logger_provider,
)
from opentelemetry.sdk._logs import (
    LoggerProvider,
    LoggingHandler,
)
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter

FlaskInstrumentor().instrument()

app = flask.Flask(__name__)

manager = enable_live_metrics(
    connection_string=os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"],
    resource=Resource.create()
)

exporter = AzureMonitorTraceExporter.from_connection_string(
    os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)

RequestsInstrumentor().instrument()

tracer_provider = TracerProvider()
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)
qp_span_processor = _QuickpulseSpanProcessor()
trace.get_tracer_provider().add_span_processor(qp_span_processor)

# logger_provider = LoggerProvider()
# set_logger_provider(logger_provider)
# exporter = AzureMonitorLogExporter.from_connection_string(
#     os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
# )
# qp_log_processor = _QuickpulseLogRecordProcessor()
# get_logger_provider().add_log_record_processor(qp_log_processor)

# # Attach LoggingHandler to namespaced logger
# handler = LoggingHandler()
# logger = logging.getLogger(__name__)
# logger.addHandler(handler)
# logger.setLevel(logging.INFO)

# while True:
#     logger.exception("Hello World!")

# @app.route("/")
# def test():
#     return "Test flask request"

while True:
    try:
        with tracer.start_as_current_span("hello") as span:
            time.sleep(0.2)
            requests.get("https://httpstat.us/200")
            raise Exception("Custom exception message.")
    except Exception:
        print("Exception raised")

# if __name__ == "__main__":
#     app.run(host="localhost", port=8080, threaded=True)
