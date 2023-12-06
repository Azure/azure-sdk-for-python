# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
Examples to show usage of the azure-core-tracing-opentelemetry
with the CosmosDb SDK and exporting to Azure monitor backend.
This example traces calls for creating a database and container using
CosmosDb SDK. The telemetry will be collected automatically and sent
to Application Insights via the AzureMonitorTraceExporter
"""
# mypy: disable-error-code="attr-defined"
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

# Example with CosmosDB SDKs
from azure.cosmos import exceptions, CosmosClient, PartitionKey

url = os.environ["ACCOUNT_URI"]
key = os.environ["ACCOUNT_KEY"]
client = CosmosClient(url, key)

database_name = "testDatabase"

with tracer.start_as_current_span(name="CreateDatabase"):
    try:
        database = client.create_database(id=database_name)  # Call will be traced
    except exceptions.CosmosResourceExistsError:
        database = client.get_database_client(database=database_name)

container_name = "products"
with tracer.start_as_current_span(name="CreateContainer"):
    try:
        container = database.create_container(
            id=container_name, partition_key=PartitionKey(path="/productName")  # Call will be traced
        )
    except exceptions.CosmosResourceExistsError:
        container = database.get_container_client(container_name)
