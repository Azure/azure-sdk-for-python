# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to use assistants operations with a file attachment to the message from
    the Azure Assistants service using a synchronous client.

    See package documentation:
    https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-assistants/README.md#key-concepts

USAGE:
    python sample_assistant_with_code_interpreter_attachment.py

    Set these two environment variables before running the sample:
    1) AZUREAI_ENDPOINT_URL - Your endpoint URL, in the form 
        https://<your-deployment-name>.<your-azure-region>.models.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) AZUREAI_ENDPOINT_KEY - Your model key (a 32-character string). Keep it secret.
"""
import logging
from opentelemetry import trace
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

from azure.ai.assistants import AssistantsClient
from azure.ai.assistants.models._enums import FilePurpose
from azure.ai.assistants.models._models import CodeInterpreterToolDefinition, MessageAttachment
from azure.core.credentials import AzureKeyCredential

import os, time


def setup_console_trace_exporter():
    exporter = ConsoleSpanExporter()
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)
    trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(exporter))

    # Instrument requests to capture HTTP-related telemetry
    RequestsInstrumentor().instrument()


def sample_assistant_basic_operation():

    setup_console_trace_exporter()

    try:
        endpoint = os.environ["AZUREAI_ENDPOINT_URL"]
        key = os.environ["AZUREAI_ENDPOINT_KEY"]
        api_version = os.environ.get("AZUREAI_API_VERSION", "2024-07-01-preview")
    except KeyError:
        logging.error("Missing environment variable 'AZUREAI_ENDPOINT_URL' or 'AZUREAI_ENDPOINT_KEY'")
        logging.error("Set them before running this sample.")
        exit()

    assistant_client = AssistantsClient(endpoint=endpoint, credential=AzureKeyCredential(key), api_version=api_version)
    logging.info("Created assistant client")
    
    # upload a file and wait for it to be processed
    file = assistant_client.upload_file(file_path="product_info_1.md", purpose=FilePurpose.ASSISTANTS)
    while assistant_client.get_file(file.id).status != "processed":
        time.sleep(4)  
        
    code_interpreter = CodeInterpreterToolDefinition()
    
    # notices that CodeInterpreterToolDefinition as tool must be added or the assistant unable to view the file
    assistant = assistant_client.create_assistant(
        model="gpt-4o-mini", name="my-assistant", instructions="You are helpful assistant",
        tools=[code_interpreter]
    )
    logging.info("Created assistant, assistant ID", assistant.id)

    thread = assistant_client.create_thread()
    logging.info("Created thread, thread ID", thread.id)    

    # create a message with the attachment
    attachment = MessageAttachment(file_id=file.id, tools=[code_interpreter])
    message = assistant_client.create_message(thread_id=thread.id, role="user", content="What does the attachment say?", attachments=[attachment])
    logging.info("Created message, message ID", message.id)

    run = assistant_client.create_run(thread_id=thread.id, assistant_id=assistant.id)
    logging.info("Created run, run ID", run.id)

    # poll the run as long as run status is queued or in progress
    while run.status not in ["completed", "failed"]:
        # wait for 4 second
        time.sleep(4)
        run = assistant_client.get_run(thread_id=thread.id, run_id=run.id)
        logging.info("Run status:", run.status)

    logging.info("Run completed with status:", run.status)
    
    
    assistant_client.delete_file(file.id)
    logging.info("Deleted file")

    assistant_client.delete_assistant(assistant.id)
    logging.info("Deleted assistant")

    messages = assistant_client.list_messages(thread_id=thread.id)
    logging.info("messages:", messages)
    

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)    
    sample_assistant_basic_operation()
