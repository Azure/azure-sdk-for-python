"""
Examples to show usage of the azure-core-tracing-opentelemetry
with the Eventhub SDK.

This example traces calls for sending a batch to eventhub.

An alternative path to export using AzureMonitor is also mentioned in the sample. Please take
a look at the commented code.
"""

# Declare OpenTelemetry as enabled tracing plugin for Azure SDKs
from azure.core.settings import settings
from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan

settings.tracing_implementation = OpenTelemetrySpan

# In the below example, we use a simple console exporter, uncomment these lines to use
# the Azure Monitor Exporter. It can be installed from https://pypi.org/project/opentelemetry-azure-monitor/
# Example of Azure Monitor exporter, but you can use anything OpenTelemetry supports
# from azure_monitor import AzureMonitorSpanExporter
# exporter = AzureMonitorSpanExporter(
#     instrumentation_key="uuid of the instrumentation key (see your Azure Monitor account)"
# )

# Regular open telemetry usage from here, see https://github.com/open-telemetry/opentelemetry-python
# for details
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

# Simple console exporter
exporter = ConsoleSpanExporter()

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
trace.get_tracer_provider().add_span_processor(
    SimpleSpanProcessor(exporter)
)

from azure.eventhub import EventHubProducerClient, EventData
import os

FULLY_QUALIFIED_NAMESPACE = os.environ['EVENT_HUB_HOSTNAME']
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']

credential = os.environ['EVENTHUB_CONN_STR']

def on_event(context, event):
    print(context.partition_id, ":", event)

with tracer.start_as_current_span(name="MyApplication"):
    producer_client = EventHubProducerClient.from_connection_string(
        conn_str=credential,
        fully_qualified_namespace=FULLY_QUALIFIED_NAMESPACE,
        eventhub_name=EVENTHUB_NAME,
        logging_enable=True
    )
    with producer_client:
        event_data_batch = producer_client.create_batch()
        event_data_batch.add(EventData('Single message'))
        producer_client.send_batch(event_data_batch)
