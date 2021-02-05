"""
Examples to show usage of the azure-core-tracing-opentelemetry
with the storage SDK.

This example traces calls for publishing cloud data and exports it
using the ConsoleSpanExporter.

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

# Example with Eventgrid SDKs
import os
from azure.eventgrid import EventGridPublisherClient, CloudEvent
from azure.core.credentials import AzureKeyCredential

hostname = os.environ['CLOUD_TOPIC_HOSTNAME']
key = AzureKeyCredential(os.environ['CLOUD_ACCESS_KEY'])
cloud_event = CloudEvent(
    source = 'demo',
    type = 'sdk.demo',
    data = {'test': 'hello'},
    extensions = {'test': 'maybe'}
)
with tracer.start_as_current_span(name="MyApplication"):
    client = EventGridPublisherClient(hostname, key)
    client.send(cloud_event)
