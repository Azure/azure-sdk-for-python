"""
Examples to show usage of the azure-core-tracing-opentelemetry
with the servicebus SDK.

This example traces calls for sending messages to the servicebus queue.

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
trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(exporter))

# Example with Servicebus SDKs

from azure.servicebus import ServiceBusClient, ServiceBusMessage
import os

connstr = os.environ["SERVICE_BUS_CONN_STR"]
queue_name = os.environ["SERVICE_BUS_QUEUE_NAME"]


with tracer.start_as_current_span(name="MyApplication"):
    with ServiceBusClient.from_connection_string(connstr) as client:
        with client.get_queue_sender(queue_name) as sender:
            # Sending a single message
            single_message = ServiceBusMessage("Single message")
            sender.send_messages(single_message)

            # Sending a list of messages
            messages = [ServiceBusMessage("First message"), ServiceBusMessage("Second message")]
            sender.send_messages(messages)
