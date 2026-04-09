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

from azure.cosmos import ContainerProxy, CosmosClient, DatabaseProxy

# Declare OpenTelemetry as enabled tracing plugin for Azure SDKs
from azure.core.settings import settings
from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan

settings.tracing_implementation = OpenTelemetrySpan

# Regular open telemetry usage from here, see https://github.com/open-telemetry/opentelemetry-python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased, ParentBased


def _get_sample_container() -> tuple[CosmosClient, DatabaseProxy, ContainerProxy]:
    """Create Cosmos client objects from environment variables."""
    account_url = os.environ["COSMOS_ACCOUNT_URL"]
    credential = os.environ["COSMOS_CREDENTIAL"]
    database_name = os.environ["DATABASE_NAME"]
    container_name = os.environ["CONTAINER_NAME"]

    client = CosmosClient(url=account_url, credential=credential)
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name)
    return client, database, container

# ------------------------------------
# Example 1: Basic Setup with Console Exporter
# ------------------------------------
def basic_tracing_example():
    """Basic OpenTelemetry setup with console output."""
    # Simple console exporter
    exporter = ConsoleSpanExporter()

    provider = TracerProvider()
    trace.set_tracer_provider(provider)
    tracer = trace.get_tracer(__name__)
    provider.add_span_processor(SimpleSpanProcessor(exporter))

    with tracer.start_as_current_span(name="MyApplication"):
        _client, _database, container = _get_sample_container()

        # Upsert an item - the emitted span includes Cosmos DB semantic attributes such as:
        #   - db.system.name = "azure.cosmosdb"
        #   - db.operation.name = "upsert_item"
        #   - db.namespace = database name
        #   - db.collection.name = container name
        #   - azure.cosmosdb.connection.mode = "direct" when direct mode is used
        #   - azure.cosmosdb.operation.request_charge = RU cost
        #   - azure.client.id = unique client identifier
        container.upsert_item({"id": "otel-sample-item", "pk": "otel-sample", "value": 100})

        # Query spans include db.query.text only when explicitly opted in via
        # AZURE_COSMOS_ENABLE_DB_QUERY_TEXT=true.
        list(
            container.query_items(
                query="SELECT * FROM c WHERE c.pk = @pk",
                parameters=[{"name": "@pk", "value": "otel-sample"}],
                enable_cross_partition_query=True,
            )
        )

        # Inline literals are sanitized before being added to db.query.text.
        # Example emitted text: SELECT * FROM c WHERE c.pk = @pk AND c.value > ?
        list(
            container.query_items(
                query="SELECT * FROM c WHERE c.pk = @pk AND c.value > 50",
                parameters=[{"name": "@pk", "value": "otel-sample"}],
                enable_cross_partition_query=True,
            )
        )


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
    provider = TracerProvider(sampler=sampler)
    trace.set_tracer_provider(provider)

    # Set up exporter
    exporter = ConsoleSpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exporter))

    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span(name="MyApplication"):
        _client, _database, container = _get_sample_container()

        # Only ~10% of these root traces will be sampled and exported.
        # When a span is not recording, Cosmos-specific enrichment returns early,
        # so query sanitization work is skipped as well.
        for i in range(5):
            list(
                container.query_items(
                    query="SELECT * FROM c WHERE c.id = @id AND c.value = 100",
                    parameters=[{"name": "@id", "value": f"item{i}"}],
                    enable_cross_partition_query=True,
                )
            )


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
    # provider = TracerProvider(sampler=sampler)
    # trace.set_tracer_provider(provider)
    # provider.add_span_processor(SimpleSpanProcessor(exporter))
    #
    # # Your Cosmos DB operations here
    # _client, _database, container = _get_sample_container()
    # list(
    #     container.query_items(
    #         query="SELECT * FROM c WHERE c.pk = @pk AND c.status = 'active'",
    #         parameters=[{"name": "@pk", "value": "otel-sample"}],
    #         enable_cross_partition_query=True,
    #     )
    # )
    # # ... operations will be sent to Azure Monitor
    pass


if __name__ == "__main__":
    # Run basic example
    print("Running basic tracing example...")
    basic_tracing_example()

    # Uncomment to run head sampling example
    # print("\nRunning head sampling example...")
    # head_sampling_example()

