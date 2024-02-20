# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
Examples to show usage of the azure-core-tracing-opentelemetry
with the Communication Phone SDK and exporting to Azure monitor backend.
This example traces calls for creating a phone client getting phone numbers
using Communication Phone SDK. The telemetry will be collected automatically
and sent to Application Insights via the AzureMonitorTraceExporter
"""
# mypy: disable-error-code="attr-defined"
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

# Example with Communication Phone SDKs
from azure.communication.phonenumbers import PhoneNumbersClient

# Create a Phone Client
connection_str = "endpoint=ENDPOINT;accessKey=KEY"
phone_numbers_client = PhoneNumbersClient.from_connection_string(connection_str)

with tracer.start_as_current_span(name="PurchasedPhoneNumbers"):
    purchased_phone_numbers = phone_numbers_client.list_purchased_phone_numbers()
    for acquired_phone_number in purchased_phone_numbers:
        print(acquired_phone_number.phone_number)
