# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# These examples are ingested by the documentation system, and are
# displayed in the SDK reference documentation. When editing these
# example snippets, take into consideration how this might affect
# the readability and usability of the reference documentation.

from azure.cosmos import CosmosClient, PartitionKey, exceptions

from azure.core.settings import settings
from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan
from azure.identity import DefaultAzureCredential
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter


# --- OpenTelemetry setup ---
provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)

# Enable the Azure Core -> OpenTelemetry bridge
settings.tracing_implementation = OpenTelemetrySpan

# --- Cosmos DB setup ---
COSMOS_ENDPOINT = "https://localhost:8081"
COSMOS_KEY = "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="

# --- Default behavior example ---
def run_default_behavior():
    client = CosmosClient(COSMOS_ENDPOINT, credential=COSMOS_KEY)

    db = client.create_database_if_not_exists(id="sampledb")
    container = db.create_container_if_not_exists(id="items", partition_key=PartitionKey(path="/pk"))

    item = {"id": "1", "pk": "p1", "name": "widget"}
    container.create_item(body=item)

    query = "SELECT * FROM c WHERE c.pk = @pk"
    parameters = [{"name": "@pk", "value": "p1"}]
    list(container.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))
    # Delete the database to clean up
    client.delete_database(db)

# --- Custom behavior with opt-in attributes ---
def run_custom_behavior_with_opt_in():
    # Actual value can be anything, here we just use True as a placeholder. The value will be added dynamically.
    # By default, most attributes are shown except for opt-in attributes.
    tracing_attributes = {"db.query.parameter": True}

    # Create the CosmosClient
    # Passing tracing_attributes enables opt-in tracing attributes and custom tracing attributes
    client = CosmosClient(COSMOS_ENDPOINT, credential=COSMOS_KEY, tracing_attributes=tracing_attributes)

    db = client.create_database_if_not_exists(id="sampledb_opt_in")
    container = db.create_container_if_not_exists(id="items", partition_key=PartitionKey(path="/pk"))

    item = {"id": "1", "pk": "p1", "name": "widget"}
    container.create_item(body=item)

    query = "SELECT * FROM c WHERE c.pk = @pk"
    parameters = [{"name": "@pk", "value": "p1"}, {"name": "@jk", "value": "p2"}]
    list(container.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))
    # Delete the database to clean up
    client.delete_database(db)

# --- Azure Monitor OpenTelemetry setup ---
def setup_azure_monitor_tracing():
    # Reconfigure the tracer provider to use the Azure Monitor exporter
    credential = DefaultAzureCredential()
    exporter = AzureMonitorTraceExporter(credential=credential)
    provider = TracerProvider()
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    settings.tracing_implementation = OpenTelemetrySpan

# --- Azure Monitor behavior example ---
def run_with_azure_monitor():
    setup_azure_monitor_tracing()
    # Use DefaultAzureCredential or other credential as appropriate
    client = CosmosClient(COSMOS_ENDPOINT, credential=DefaultAzureCredential())

    db = client.create_database_if_not_exists(id="sampledb_azure_monitor")
    container = db.create_container_if_not_exists(id="items", partition_key=PartitionKey(path="/pk"))

    item = {"id": "1", "pk": "p1", "name": "widget"}
    container.create_item(body=item)

    query = "SELECT * FROM c WHERE c.pk = @pk"
    parameters = [{"name": "@pk", "value": "p1"}]
    list(container.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))
    # Delete the database to clean up
    client.delete_database(db)


# --- Main entry point ---
if __name__ == "__main__":
    run_default_behavior()
    run_custom_behavior_with_opt_in()
    provider.shutdown()