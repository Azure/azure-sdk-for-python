# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to use assistants client with multiple tools and run creation and processing 
    with a synchronous client.

    See package documentation:
    https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-assistants/README.md#key-concepts

USAGE:
    python sample_assistant_run_with_toolset.py

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
from azure.ai.assistants.models import FunctionTool, CodeInterpreterTool, FileSearchTool, ToolSet
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


def sample_assistant_run():

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

    # Initialize assistant tools
    functions = FunctionTool(user_functions)
    code_interpreter = CodeInterpreterTool()

    toolset = ToolSet()
    toolset.add(functions)
    toolset.add(code_interpreter)

    # Create assistant
    assistant = assistant_client.create_assistant(
        model="gpt-4o-mini", name="my-assistant", instructions="You are a helpful assistant", toolset=toolset
    )
    logging.info("Created assistant, ID: %s", assistant.id)

    # Create thread for communication
    thread = assistant_client.create_thread()
    logging.info("Created thread, ID: %s", thread.id)

    # Create message to thread
    message = assistant_client.create_message(thread_id=thread.id, role="user", content="Hello, send an email with the datetime and weather information in New York?")
    logging.info("Created message, ID: %s", message.id)

    # Create and process assistant run in thread with tools
    run = assistant_client.create_and_process_run(thread_id=thread.id, assistant_id=assistant.id)
    logging.info("Run finished with status: %s", run.status)

    if run.status == "failed":
        logging.error("Run failed: %s", run.last_error)

    # Delete the assistant when done
    assistant_client.delete_assistant(assistant.id)
    logging.info("Deleted assistant")

    # Fetch and log all messages
    messages = assistant_client.list_messages(thread_id=thread.id)
    logging.info("Messages: %s", messages)


if __name__ == "__main__":
    # Set logging level
    logging.basicConfig(level=logging.INFO)
    sample_assistant_run()
