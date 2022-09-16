"""
Examples to show usage of the azure-core-tracing-opentelemetry
with the storage SDK and exporting to Azure monitor backend.
This example traces calls for creating a container using storage SDK.
The telemetry will be collected automatically and sent to Application
Insights via the AzureMonitorTraceExporter
"""

import os

# Declare OpenTelemetry as enabled tracing plugin for Azure SDKs
from azure.core.settings import settings
from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan

settings.tracing_implementation = OpenTelemetrySpan

# Regular open telemetry usage from here, see https://github.com/open-telemetry/opentelemetry-python
# for details
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# azure monitor trace exporter to send telemetry to appinsights
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
span_processor = BatchSpanProcessor(
    AzureMonitorTraceExporter.from_connection_string(
        os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
    )
)
trace.get_tracer_provider().add_span_processor(span_processor)

# Example with BlobStorage SDKs
from azure.storage.blob import BlobServiceClient

connection_string = os.environ['AZURE_STORAGE_CONNECTION_STRING']
container_name = os.environ['AZURE_STORAGE_BLOB_CONTAINER_NAME']

with tracer.start_as_current_span(name="MyStorageApplication"):
    client = BlobServiceClient.from_connection_string(connection_string)
    client.create_container(container_name)  # Call will be traced
