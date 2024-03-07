"""
Examples to show usage of the azure-core-tracing-opentelemetry
with the Eventhub SDK.

This example traces calls for sending a batch to eventhub.

An alternative path to export using the OpenTelemetry exporter for Azure Monitor
is also mentioned in the sample. Please take a look at the commented code.
"""

# Declare OpenTelemetry as enabled tracing plugin for Azure SDKs
from azure.core.settings import settings

settings.tracing_implementation = "opentelemetry"

# In the below example, we use a simple console exporter, uncomment these lines to use
# the OpenTelemetry exporter for Azure Monitor.
# Example of a trace exporter for Azure Monitor, but you can use anything OpenTelemetry supports.

# from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
# exporter = AzureMonitorTraceExporter(
#     connection_string="the connection string used for your Application Insights resource"
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
# see issue https://github.com/open-telemetry/opentelemetry-python/issues/3713
trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(exporter))  # type: ignore

from azure.eventhub import EventHubProducerClient, EventData
import os

FULLY_QUALIFIED_NAMESPACE = os.environ["EVENT_HUB_HOSTNAME"]
EVENTHUB_NAME = os.environ["EVENT_HUB_NAME"]

credential = os.environ["EVENTHUB_CONN_STR"]


def on_event(context, event):
    print(context.partition_id, ":", event)


with tracer.start_as_current_span(name="MyApplication"):
    producer_client = EventHubProducerClient.from_connection_string(
        conn_str=credential,
        fully_qualified_namespace=FULLY_QUALIFIED_NAMESPACE,
        eventhub_name=EVENTHUB_NAME,
        logging_enable=True,
    )
    with producer_client:
        event_data_batch = producer_client.create_batch()
        event_data_batch.add(EventData("Single message"))
        producer_client.send_batch(event_data_batch)
