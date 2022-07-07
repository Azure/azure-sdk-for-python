"""
Examples to show usage of the azure-core-tracing-opentelemetry
with the Communication SMS SDK and exporting to Azure monitor backend.
This example traces calls for sending an SMS message using Communication 
SMS SDK. The telemetry will be collected automatically and sent to
Application Insights via the AzureMonitorTraceExporter
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

# Example with Communication SMS SDKs
from azure.communication.sms import SmsClient

# Create a SMS Client
connection_str = "endpoint=ENDPOINT;accessKey=KEY"
sms_client = SmsClient.from_connection_string(connection_str)

with tracer.start_as_current_span(name="SendSMS"):
    sms_responses = sms_client.send(
    from_="<from-phone-number>",
    to="<to-phone-number-1>",
    message="Hello World via SMS",
    enable_delivery_report=True, # optional property
    tag="custom-tag") # optional property
