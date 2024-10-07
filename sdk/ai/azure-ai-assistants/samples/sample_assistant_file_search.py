# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to use assistants client for file search and processing 
    with a synchronous client.

    See package documentation:
    https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-assistants/README.md#key-concepts

USAGE:
    python sample_assistant_file_search.py

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
from azure.ai.assistants.models import FileSearchTool, ToolSet
from azure.ai.assistants.models._enums import FilePurpose
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
        logging.error(f"Missing environment variable: {e}")
        exit()

    # Initialize assistant client
    assistant_client = AssistantsClient(endpoint=endpoint, credential=AzureKeyCredential(key), api_version=api_version)
    logging.info("Created assistant client")

    # Create file search tool
    file_search = FileSearchTool()
    openai_file = assistant_client.upload_file(file_path="product_info_1.md", purpose=FilePurpose.ASSISTANTS)
    openai_vectorstore = assistant_client.create_vector_store(file_ids=[openai_file.id], name="my_vectorstore")
    file_search.add_vector_store(openai_vectorstore.id)

    toolset = ToolSet()
    toolset.add(file_search)

    # Create assistant
    assistant = assistant_client.create_assistant(
        model="gpt-4o-mini", name="my-assistant", instructions="Hello, you are helpful assistant and can search information from uploaded files", toolset=toolset
    )
    logging.info(f"Created assistant, ID: {assistant.id}")

    # Create thread for communication
    thread = assistant_client.create_thread()
    logging.info(f"Created thread, ID: {thread.id}")

    # Create message to thread
    message = assistant_client.create_message(thread_id=thread.id, role="user", content="Hello, what Contoso products do you know?")
    logging.info(f"Created message, ID: {message.id}")

    # Create and process assistant run in thread with tools
    # Note: If vector store has been created just before this, there can be need to poll the status of vector store to be ready for information retrieval
    #       This can be done by calling `assistant_client.get_vector_store(vector_store_id)` and checking the status of vector store
    #       We may want to add conveniency around this
    run = assistant_client.create_and_process_run(thread_id=thread.id, assistant_id=assistant.id)
    logging.info(f"Run finished with status: {run.status}")

    if run.status == "failed":
        # Check if you got "Rate limit is exceeded.", then you want to get more quota
        logging.error(f"Run failed: {run.last_error}")

    # Delete the file when done
    assistant_client.delete_vector_store(openai_vectorstore.id)
    logging.info("Deleted vector store")

    # Delete the assistant when done
    assistant_client.delete_assistant(assistant.id)
    logging.info("Deleted assistant")

    # Fetch and log all messages
    messages = assistant_client.list_messages(thread_id=thread.id)
    logging.info(f"Messages: {messages}")


if __name__ == "__main__":
    # Set logging level
    logging.basicConfig(level=logging.INFO)
    sample_assistant_run()
