# ----------------------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# ----------------------------------------------------------------------------------------------------------
# Prerequisites -
#
# 1. An Azure Cosmos account -
#    https://learn.microsoft.com/azure/cosmos-db/nosql/quickstart-python#create-an-azure-cosmos-db-account
#
# 2. Microsoft Azure Cosmos PyPI package -
#    https://pypi.python.org/pypi/azure-cosmos/
#
# 3. Azure Core Tracing OpenTelemetry plugin and OpenTelemetry Python SDK
#    pip install azure-core-tracing-opentelemetry opentelemetry-sdk
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates tracing using OpenTelemetry with Cosmos DB
# Shows both basic setup and head sampling configuration
# ----------------------------------------------------------------------------------------------------------

import os
from azure.cosmos.cosmos_client import CosmosClient

# Declare OpenTelemetry as enabled tracing plugin for Azure SDKs
from azure.core.settings import settings
from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan

settings.tracing_implementation = OpenTelemetrySpan

# Regular open telemetry usage from here, see https://github.com/open-telemetry/opentelemetry-python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased, ParentBased

# ------------------------------------
# Example 1: Basic Setup with Console Exporter
# ------------------------------------
def basic_tracing_example():
    """Basic OpenTelemetry setup with console output."""
    # Simple console exporter
    exporter = ConsoleSpanExporter()

    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)
    trace.get_tracer_provider().add_span_processor(
        SimpleSpanProcessor(exporter)
    )

    # Example with Cosmos SDK
    account_url = os.environ["COSMOS_ACCOUNT_URL"]
    credential = os.environ["COSMOS_CREDENTIAL"]
    database_name = os.environ["DATABASE_NAME"]
    container_name = os.environ["CONTAINER_NAME"]

    with tracer.start_as_current_span(name="MyApplication"):
        client = CosmosClient(url=account_url, credential=credential)
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)

        # Create an item - will be traced with Cosmos DB semantic convention attributes
        # Captured attributes include:
        #   - db.system = "cosmosdb"
        #   - db.operation.name = "create_item" (actual SDK method name)
        #   - db.cosmosdb.operation_type = "create" (standardized operation type)
        #   - db.namespace = database name
        #   - db.collection.name = container name
        #   - db.cosmosdb.connection_mode = "gateway" or "direct"
        #   - db.cosmosdb.request_charge = RU cost
        #   - db.cosmosdb.client_id = unique client identifier
        container.create_item({"id": "item1", "value": "test"})


# ------------------------------------
# Example 2: Head Sampling Configuration
# ------------------------------------
def head_sampling_example():
    """
    OpenTelemetry setup with head sampling (probabilistic sampling).

    Head sampling decides at the start of a trace whether to sample it.
    This reduces overhead by only tracing a percentage of requests.
    """

    # Configure head sampling to sample 10% of traces
    # TraceIdRatioBased(0.1) means 10% sampling rate
    sampler = ParentBased(
        root=TraceIdRatioBased(0.1)  # Sample 10% of root spans
    )

    # Create tracer provider with the sampler
    trace.set_tracer_provider(TracerProvider(sampler=sampler))

    # Set up exporter
    exporter = ConsoleSpanExporter()
    trace.get_tracer_provider().add_span_processor(
        SimpleSpanProcessor(exporter)
    )

    tracer = trace.get_tracer(__name__)

    # Example with Cosmos SDK
    account_url = os.environ["COSMOS_ACCOUNT_URL"]
    credential = os.environ["COSMOS_CREDENTIAL"]
    database_name = os.environ["DATABASE_NAME"]
    container_name = os.environ["CONTAINER_NAME"]

    with tracer.start_as_current_span(name="MyApplication"):
        client = CosmosClient(url=account_url, credential=credential)
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)

        # Only ~10% of these operations will be sampled and traced
        for i in range(100):
            container.read_item(item=f"item{i}", partition_key=f"pk{i}")


# ------------------------------------
# Example 3: Azure Monitor Exporter
# ------------------------------------
def azure_monitor_example():
    """
    Example using Azure Monitor as the exporter.
    Uncomment and configure with your Application Insights connection string.
    """
    # from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
    #
    # exporter = AzureMonitorTraceExporter(
    #     connection_string="InstrumentationKey=00000000-0000-0000-0000-000000000000;..."
    # )
    #
    # # Optional: Configure sampling for Azure Monitor
    # sampler = ParentBased(root=TraceIdRatioBased(0.5))  # 50% sampling
    #
    # trace.set_tracer_provider(TracerProvider(sampler=sampler))
    # trace.get_tracer_provider().add_span_processor(
    #     SimpleSpanProcessor(exporter)
    # )
    #
    # # Your Cosmos DB operations here
    # client = CosmosClient(url=account_url, credential=credential)
    # # ... operations will be sent to Azure Monitor
    pass


if __name__ == "__main__":
    # Run basic example
    print("Running basic tracing example...")
    basic_tracing_example()

    # Uncomment to run head sampling example
    # print("\nRunning head sampling example...")
    # head_sampling_example()

