# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to use assistants client convenience methods for user functions and run creation and processing 
    with a synchronous client.

    See package documentation:
    https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-assistants/README.md#key-concepts

USAGE:
    python sample_assistant_convenience_methods.py

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
from azure.ai.assistants.models import AssistantFunctions
from azure.core.credentials import AzureKeyCredential
from user_functions import user_functions

import os, time, logging


def setup_console_trace_exporter():
    exporter = ConsoleSpanExporter()
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)
    trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(exporter))

    # Instrument requests to capture HTTP-related telemetry
    RequestsInstrumentor().instrument()


def sample_assistant_functions():
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Setup console trace exporter
    setup_console_trace_exporter()
    
    # Check for environment variables
    try:
        endpoint = os.environ["AZUREAI_ENDPOINT_URL"]
        key = os.environ["AZUREAI_ENDPOINT_KEY"]
        api_version = os.environ.get("AZUREAI_API_VERSION", "2024-07-01-preview")
    except KeyError as e:
        logging.error("Missing environment variable: %s", e)
        exit()
    
    # Initialize assistant client
    assistant_client = AssistantsClient(endpoint=endpoint, credential=AzureKeyCredential(key), api_version=api_version)
    logging.info("Created assistant client")
    
    # Initialize assistant functions
    functions = AssistantFunctions(functions=user_functions)
    
    # Create assistant
    assistant = assistant_client.create_assistant(
        model="gpt", name="my-assistant", instructions="You are a helpful assistant", tools=functions.definitions
    )
    logging.info("Created assistant, ID: %s", assistant.id)
    
    # Create thread for communication
    thread = assistant_client.create_thread()
    logging.info("Created thread, ID: %s", thread.id)
    
    # Create and send message
    message = assistant_client.create_message(thread_id=thread.id, role="user", content="Hello, what's the time?")
    logging.info("Created message, ID: %s", message.id)
    
    # Create and run assistant task
    run_status = assistant_client.create_and_process_run(thread_id=thread.id, assistant_id=assistant.id, functions=functions)
    logging.info("Run finished with status: %s", run_status)

    # Fetch and log all messages
    messages = assistant_client.list_messages(thread_id=thread.id)
    logging.info("Messages: %s", messages)

    # Delete the assistant when done
    assistant_client.delete_assistant(assistant.id)
    logging.info("Deleted assistant")


if __name__ == "__main__":
    sample_assistant_functions()
