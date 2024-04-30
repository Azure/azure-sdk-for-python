# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
Examples to show usage of the azure-core-tracing-opentelemetry
with the Communication Chat SDK and exporting to Azure monitor backend.
This example traces calls for creating a chat client and thread using
Communication Chat SDK. The telemetry will be collected automatically
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

# Example with Communication Chat SDKs
# Authenticate with Communication Identity SDK
from azure.communication.identity import CommunicationIdentityClient
comm_connection_string = "<connection string of your Communication service>"
identity_client = CommunicationIdentityClient.from_connection_string(comm_connection_string)

# Telemetry will be sent for creating the user and getting the token as well
user = identity_client.create_user()
tokenresponse = identity_client.get_token(user, scopes=["chat"])
token = tokenresponse.token

# Create a Chat Client
from azure.communication.chat import ChatClient, CommunicationTokenCredential

# Your unique Azure Communication service endpoint
endpoint = "https://<RESOURCE_NAME>.communcationservices.azure.com"
with tracer.start_as_current_span(name="CreateChatClient"):
    chat_client = ChatClient(endpoint, CommunicationTokenCredential(token))
    # Create a Chat Thread
    with tracer.start_as_current_span(name="CreateChatThread"):
        create_chat_thread_result = chat_client.create_chat_thread("test topic")
        chat_thread_client = chat_client.get_chat_thread_client(create_chat_thread_result.chat_thread.id)
