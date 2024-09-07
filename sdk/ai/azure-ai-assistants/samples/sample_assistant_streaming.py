# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to use assistants with streaming from
    the Azure Assistants service using a synchronous client.

    See package documentation:
    https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-assistants/README.md#key-concepts

USAGE:
    python sample_assistant_streaming.py

    Set these two environment variables before running the sample:
    1) AZUREAI_ENDPOINT_URL - Your endpoint URL, in the form 
        https://<your-deployment-name>.<your-azure-region>.models.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) AZUREAI_ENDPOINT_KEY - Your model key (a 32-character string). Keep it secret.
"""
from opentelemetry import trace
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

from azure.ai.assistants import AssistantsClient
from azure.ai.assistants.models._models import SubmitToolOutputsDetails
from azure.core.credentials import AzureKeyCredential

import os, time, json


def setup_console_trace_exporter():
    exporter = ConsoleSpanExporter()
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)
    trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(exporter))

    # Instrument requests to capture HTTP-related telemetry
    RequestsInstrumentor().instrument()


def print_streamed_events(response_iterator):
    """Print the events from the streamed response."""
    buffer = ''
    for chunk in response_iterator:
        buffer += chunk.decode('utf-8')
        while '\n\n' in buffer:
            event_data_str, buffer = buffer.split('\n\n', 1)
            print_event_details(event_data_str)


def print_event_details(event_data_str: str):
    """Parse and print the event details."""
    event_lines = event_data_str.strip().split('\n')
    event_type = None
    event_data = ''
    for line in event_lines:
        if line.startswith('event:'):
            event_type = line.split(':', 1)[1].strip()
        elif line.startswith('data:'):
            event_data = line.split(':', 1)[1].strip()

    if event_type:
        print(f"Event: {event_type}")
        try:
            # Attempt to parse the event data as JSON
            parsed_data = json.loads(event_data)
            print("Data:", json.dumps(parsed_data, indent=2))
        except json.JSONDecodeError:
            # If data is not in JSON format, print raw data
            print("Data:", event_data)
    else:
        print("Received a message without event type", event_data_str)


def sample_assistant_streaming():

    setup_console_trace_exporter()

    try:
        endpoint = os.environ["AZUREAI_ENDPOINT_URL"]
        key = os.environ["AZUREAI_ENDPOINT_KEY"]
        api_version = os.environ.get("AZUREAI_API_VERSION", "2024-07-01-preview")
    except KeyError:
        print("Missing environment variable 'AZUREAI_ENDPOINT_URL' or 'AZUREAI_ENDPOINT_KEY'")
        print("Set them before running this sample.")
        exit()

    assistant_client = AssistantsClient(endpoint=endpoint, credential=AzureKeyCredential(key), api_version=api_version)
    print("Created assistant client")

    assistant = assistant_client.create_assistant(
        model="gpt", name="my-assistant", instructions="You are helpful assistant"
    )
    print("Created assistant, assistant ID", assistant.id)

    thread = assistant_client.create_thread()
    print("Created thread, thread ID", thread.id)

    message = assistant_client.create_message(thread_id=thread.id, role="user", content="Hello, tell me a joke")
    print("Created message, message ID", message.id)

    run = assistant_client.create_run(thread_id=thread.id, assistant_id=assistant.id, stream=True)

    if hasattr(run, '__iter__'):
        print_streamed_events(run)

    messages = assistant_client.list_messages(thread_id=thread.id)
    print("messages:", messages)

    assistant_client.delete_assistant(assistant.id)
    print("Deleted assistant")


if __name__ == "__main__":
    sample_assistant_streaming()
