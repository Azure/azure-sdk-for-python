# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
An example to show an application instrumented with the OpenTelemetry flask instrumentation.
Calls made with the flask library will be automatically tracked and telemetry is exported to 
application insights with the AzureMonitorTraceExporter.
See more info on the flask instrumentation here:
https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation/opentelemetry-instrumentation-flask
"""
# mypy: disable-error-code="attr-defined"
import os
import fastapi
import uvicorn

from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# This method instruments all of the FastAPI module.
# You can also use FastAPIInstrumentor().instrument_app(app) to instrument a specific app after it is created.
FastAPIInstrumentor().instrument()
app = fastapi.FastAPI()

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
span_processor = BatchSpanProcessor(
    AzureMonitorTraceExporter.from_connection_string(
        os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
    )
)
trace.get_tracer_provider().add_span_processor(span_processor)

# Requests made to fastapi endpoints will be automatically captured
@app.get("/")
async def test():
    return {"message": "Hello World"}


# Exceptions that are raised within the request are automatically captured
@app.get("/exception")
async def exception():
    raise Exception("Hit an exception")


# Set the OTEL_PYTHON_EXCLUDE_URLS environment variable to "http://127.0.0.1:8000/exclude"
# Telemetry from this endpoint will not be captured due to excluded_urls config above
@app.get("/exclude")
async def exclude():
    return {"message": "Telemetry was not captured"}

if __name__ == "__main__":
    # cSpell:disable
    uvicorn.run("sample_fastapi:app", port=8008, reload=True)
    # cSpell:disable
