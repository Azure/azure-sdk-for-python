# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# These examples are ingested by the documentation system, and are
# displayed in the SDK reference documentation. When editing these
# example snippets, take into consideration how this might affect
# the readability and usability of the reference documentation.

import asyncio
from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey, exceptions

from azure.core.settings import settings
from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan
from azure.identity.aio import DefaultAzureCredential
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
COSMOS_ENDPOINT = "host"
COSMOS_KEY = "key"

# --- Default behavior example ---
async def run_default_behavior():
    async with CosmosClient(COSMOS_ENDPOINT, credential=COSMOS_KEY) as client:
        db = await client.create_database_if_not_exists(id="sampledb")
        container = await db.create_container_if_not_exists(id="items", partition_key=PartitionKey(path="/pk"))

        item = {"id": "1", "pk": "p1", "name": "widget"}
        await container.create_item(body=item)

        query = "SELECT * FROM c WHERE c.pk = @pk"
        parameters = [{"name": "@pk", "value": "p1"}]
        async for _ in container.query_items(query=query, parameters=parameters):
            pass
        # Delete the database to clean up
        await client.delete_database(db)

# --- Custom behavior with opt-in attributes ---
async def run_custom_behavior_with_opt_in():
    tracing_attributes = {"db.query.parameter": True}

    async with CosmosClient(COSMOS_ENDPOINT, credential=COSMOS_KEY, tracing_attributes=tracing_attributes) as client:
        db = await client.create_database_if_not_exists(id="sampledb_opt_in")
        container = await db.create_container_if_not_exists(id="items", partition_key=PartitionKey(path="/pk"))

        item = {"id": "1", "pk": "p1", "name": "widget"}
        await container.create_item(body=item)

        query = "SELECT * FROM c WHERE c.pk = @pk"
        parameters = [{"name": "@pk", "value": "p1"}, {"name": "@jk", "value": "p2"}]
        async for _ in container.query_items(query=query, parameters=parameters):
            pass
        # Delete the database to clean up
        await client.delete_database(db)

# --- Azure Monitor OpenTelemetry setup ---
async def setup_azure_monitor_tracing():
    credential = DefaultAzureCredential()
    exporter = AzureMonitorTraceExporter(credential=credential)
    provider = TracerProvider()
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    settings.tracing_implementation = OpenTelemetrySpan

# --- Azure Monitor behavior example ---
async def run_with_azure_monitor():
    await setup_azure_monitor_tracing()
    async with CosmosClient(COSMOS_ENDPOINT, credential=DefaultAzureCredential()) as client:
        db = await client.create_database_if_not_exists(id="sampledb_azure_monitor")
        container = await db.create_container_if_not_exists(id="items", partition_key=PartitionKey(path="/pk"))

        item = {"id": "1", "pk": "p1", "name": "widget"}
        await container.create_item(body=item)

        query = "SELECT * FROM c WHERE c.pk = @pk"
        parameters = [{"name": "@pk", "value": "p1"}]
        async for _ in container.query_items(query=query, parameters=parameters):
            pass
        # Delete the database to clean up
        await client.delete_database(db)


# --- Main entry point ---
async def main():
    await run_default_behavior()
    await run_custom_behavior_with_opt_in()
    provider.shutdown()

if __name__ == "__main__":
    asyncio.run(main())