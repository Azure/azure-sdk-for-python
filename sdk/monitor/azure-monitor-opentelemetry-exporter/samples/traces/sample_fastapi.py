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
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from fastapi import Depends, FastAPI
from httpx import AsyncClient
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

app = FastAPI()

tracer = trace.get_tracer(__name__)

async def get_client():
    async with AsyncClient() as client:
        yield client

@app.get("/")
async def read_root(client=Depends(get_client)):
    with tracer.start_as_current_span("read_root"):
        response = await client.get("https://httpbin.org/get")
        return response.json()

if __name__ == "__main__":
    # cSpell:disable
    import uvicorn
    trace.set_tracer_provider(TracerProvider())
    exporter = AzureMonitorTraceExporter()
    span_processor = BatchSpanProcessor(exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    uvicorn.run("sample_fastapi:app", port=8008, reload=True)
    # cSpell:disable

