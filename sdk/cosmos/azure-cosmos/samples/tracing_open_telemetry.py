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
# Sample - demonstrates tracing using OpenTelemetry
# ----------------------------------------------------------------------------------------------------------

# Declare OpenTelemetry as enabled tracing plugin for Azure SDKs
from azure.core.settings import settings
from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan

settings.tracing_implementation = OpenTelemetrySpan

# In the below example, we use a simple console exporter, uncomment these lines to use
# the OpenTelemetry exporter for Azure Monitor.
# Example of a trace exporter for Azure Monitor, but you can use anything OpenTelemetry supports
# from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
# exporter = AzureMonitorTraceExporter(
#     connection_string="the connection string used for your Application Insights resource"
# )

# Regular open telemetry usage from here, see https://github.com/open-telemetry/opentelemetry-python
# for details
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter

# Simple console exporter
exporter = ConsoleSpanExporter()

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
trace.get_tracer_provider().add_span_processor(
    SimpleSpanProcessor(exporter)
)

# Example with Cosmos SDK
import os
from azure.cosmos.cosmos_client import CosmosClient

account_url = os.environ["COSMOS_ACCOUNT_URL"]
credential = os.environ["COSMOS_CREDENTIAL"]
database_name = os.environ["DATABASE_NAME"]

with tracer.start_as_current_span(name="MyApplication"):
    client = CosmosClient(url=account_url, credential=credential)
    client.create_database(database_name)  # Call will be traced