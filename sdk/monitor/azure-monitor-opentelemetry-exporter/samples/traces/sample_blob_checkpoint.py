"""
Examples to show usage of the azure-core-tracing-opentelemetry
with the eventhub checkpoint storage blob SDK and exporting to
Azure monitor backend. This example traces calls for sending
checkpoints via the checkpoint storage blob sdk. The telemetry
will be collected automatically and sent to Application Insights
via the AzureMonitorTraceExporter
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

# Example with EventHub SDKs
from azure.eventhub import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblob import BlobCheckpointStore

CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']
STORAGE_CONNECTION_STR = os.environ["AZURE_STORAGE_CONN_STR"]
BLOB_CONTAINER_NAME = "your-blob-container-name"  # Please make sure the blob container resource exists.

def on_event(partition_context, event):
    # Put your code here.
    # Avoid time-consuming operations.
    print(event)
    partition_context.update_checkpoint(event)

checkpoint_store = BlobCheckpointStore.from_connection_string(
    STORAGE_CONNECTION_STR,
    container_name=BLOB_CONTAINER_NAME,
)
client = EventHubConsumerClient.from_connection_string(
    CONNECTION_STR,
    consumer_group='$Default',
    eventhub_name=EVENTHUB_NAME,
    checkpoint_store=checkpoint_store
)

with tracer.start_as_current_span(name="MyEventHub"):
    try:
        client.receive(on_event)
    except KeyboardInterrupt:
        client.close()
