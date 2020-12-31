"""
Examples to show usage of the azure-core-tracing-opentelemetry
with the servicebus SDK.

This example traces calls for sending messages to the servicebus queue.

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
from opentelemetry.sdk.trace.export import SimpleExportSpanProcessor

# Simple console exporter
exporter = ConsoleSpanExporter()

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
trace.get_tracer_provider().add_span_processor(
    SimpleExportSpanProcessor(exporter)
)

# Example with Servicebus SDKs

from azure.servicebus import ServiceBusClient, ServiceBusMessage
import os

connstr = os.environ['SERVICE_BUS_CONN_STR']
queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']


with tracer.start_as_current_span(name="MyApplication"):
    with ServiceBusClient.from_connection_string(connstr) as client:
        with client.get_queue_sender(queue_name) as sender:
            # Sending a single message
            single_message = ServiceBusMessage("Single message")
            sender.send_messages(single_message)

            # Sending a list of messages
            messages = [ServiceBusMessage("First message"), ServiceBusMessage("Second message")]
            sender.send_messages(messages)
