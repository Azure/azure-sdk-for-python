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
    python sample_assistant_stream_iteration.py

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
from azure.ai.assistants.models import (
    AssistantStreamEvent,
    MessageDeltaTextContent,
    MessageDeltaChunk,
    SubmitToolOutputsAction,
    ThreadMessage,
    ThreadRun,
    RunStep,
)

from azure.ai.assistants.models import FunctionTool, ToolSet
from user_functions import user_functions

from azure.core.credentials import AzureKeyCredential

import os, logging


def setup_console_trace_exporter():
    exporter = ConsoleSpanExporter()
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)
    trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(exporter))

    # Instrument requests to capture HTTP-related telemetry
    RequestsInstrumentor().instrument()


# Function to handle tool stream iteration
def handle_submit_tool_outputs(assistant_client : AssistantsClient, thread_id, run_id, tool_outputs):
    try:
        with assistant_client.submit_tool_outputs_to_run(
            thread_id=thread_id,
            run_id=run_id,
            tool_outputs=tool_outputs,
            stream=True
        ) as tool_stream:
            for tool_event_type, tool_event_data in tool_stream:
                if tool_event_type == AssistantStreamEvent.ERROR:
                    logging.error(f"An error occurred in tool stream. Data: {tool_event_data}")
                elif tool_event_type == AssistantStreamEvent.DONE:
                    logging.info("Tool stream completed.")
                    break
                else:
                    if isinstance(tool_event_data, MessageDeltaChunk):
                        handle_message_delta(tool_event_data)

    except Exception as e:
        logging.error(f"Failed to process tool stream: {e}")


# Function to handle message delta chunks
def handle_message_delta(delta: MessageDeltaChunk) -> None:
    for content_part in delta.delta.content:
        if isinstance(content_part, MessageDeltaTextContent):
            text_value = content_part.text.value if content_part.text else "No text"
            logging.info(f"Text delta received: {text_value}")


def sample_assistant_stream_iteration():

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

    functions = FunctionTool(user_functions)
    toolset = ToolSet()
    toolset.add(functions)

    assistant = assistant_client.create_assistant(
        model="gpt-4o-mini", name="my-assistant", instructions="You are a helpful assistant", toolset=toolset
    )
    logging.info(f"Created assistant, assistant ID {assistant.id}")

    thread = assistant_client.create_thread()
    logging.info(f"Created thread, thread ID {thread.id}")

    message = assistant_client.create_message(thread_id=thread.id, role="user", content="Hello, what's the time?")
    logging.info(f"Created message, message ID {message.id}")

    with assistant_client.create_and_process_run(thread_id=thread.id, assistant_id=assistant.id, stream=True) as stream:

        for event_type, event_data in stream:

            if isinstance(event_data, MessageDeltaChunk):
                handle_message_delta(event_data)

            elif isinstance(event_data, ThreadMessage):
                logging.info(f"ThreadMessage created. ID: {event_data.id}, Status: {event_data.status}")

            elif isinstance(event_data, ThreadRun):
                logging.info(f"ThreadRun status: {event_data.status}")
                
                if event_data.status == "failed":
                    logging.error(f"Run failed. Error: {event_data.last_error}")

                if event_data.status == "requires_action" and isinstance(event_data.required_action, SubmitToolOutputsAction):
                    tool_calls = event_data.required_action.submit_tool_outputs.tool_calls
                    if not tool_calls:
                        logging.warning("No tool calls to execute.")
                        return

                    toolset = assistant_client.get_toolset()
                    if toolset:
                        tool_outputs = toolset.execute_tool_calls(tool_calls)
                    else:
                        raise ValueError("Toolset is not available in the client.")

                    if tool_outputs:
                        handle_submit_tool_outputs(assistant_client, event_data.thread_id, event_data.id, tool_outputs)
                           
            elif isinstance(event_data, RunStep):
                logging.info(f"RunStep type: {event_data.type}, Status: {event_data.status}")

            elif event_type == AssistantStreamEvent.ERROR:
                logging.error(f"An error occurred. Data: {event_data}")

            elif event_type == AssistantStreamEvent.DONE:
                logging.info("Stream completed.")
                break

            else:
                logging.warning(f"Unhandled Event Type: {event_type}, Data: {event_data}")

    assistant_client.delete_assistant(assistant.id)
    logging.info("Deleted assistant")

    messages = assistant_client.list_messages(thread_id=thread.id)
    logging.info(f"Messages: {messages}")


if __name__ == "__main__":
    # Set logging level
    logging.basicConfig(level=logging.INFO)
    sample_assistant_stream_iteration()
