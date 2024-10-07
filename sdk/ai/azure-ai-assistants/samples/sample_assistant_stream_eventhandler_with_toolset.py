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
    AssistantEventHandler,
    MessageDeltaTextContent,
    MessageDeltaChunk,
    RunStep,
    SubmitToolOutputsAction,
    ThreadMessage,
    ThreadRun,
)

from azure.ai.assistants.models import FunctionTool, ToolSet
from user_functions import user_functions

from azure.core.credentials import AzureKeyCredential

import os, logging
from typing import Any


def setup_console_trace_exporter():
    exporter = ConsoleSpanExporter()
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)
    trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(exporter))

    # Instrument requests to capture HTTP-related telemetry
    RequestsInstrumentor().instrument()


class MyEventHandler(AssistantEventHandler):

    def __init__(self, client: AssistantsClient):
        self._client = client

    def on_message_delta(self, delta: "MessageDeltaChunk") -> None:
        for content_part in delta.delta.content:
            if isinstance(content_part, MessageDeltaTextContent):
                text_value = content_part.text.value if content_part.text else "No text"
                logging.info(f"Text delta received: {text_value}")

    def on_thread_message(self, message: "ThreadMessage") -> None:
        logging.info(f"ThreadMessage created. ID: {message.id}, Status: {message.status}")

    def on_thread_run(self, run: "ThreadRun") -> None:
        logging.info(f"ThreadRun status: {run.status}")

        if run.status == "failed":
            logging.error(f"Run failed. Error: {run.last_error}")

        if run.status == "requires_action" and isinstance(run.required_action, SubmitToolOutputsAction):
            self._handle_submit_tool_outputs(run)

    def on_run_step(self, step: "RunStep") -> None:
        logging.info(f"RunStep type: {step.type}, Status: {step.status}")

    def on_run_step(self, step: "RunStep") -> None:
        logging.info(f"RunStep type: {step.type}, Status: {step.status}")

    def on_error(self, data: str) -> None:
        logging.error(f"An error occurred. Data: {data}")

    def on_done(self) -> None:
        logging.info("Stream completed.")

    def on_unhandled_event(self, event_type: str, event_data: Any) -> None:
        logging.warning(f"Unhandled Event Type: {event_type}, Data: {event_data}")

    def _handle_submit_tool_outputs(self, run: "ThreadRun") -> None:
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        if not tool_calls:
            logging.warning("No tool calls to execute.")
            return
        if not self._client:
            logging.warning("AssistantClient not set. Cannot execute tool calls using toolset.")
            return

        toolset = self._client.get_toolset()
        if toolset:
            tool_outputs = toolset.execute_tool_calls(tool_calls)
        else:
            raise ValueError("Toolset is not available in the client.")
        
        logging.info(f"Tool outputs: {tool_outputs}")
        if tool_outputs:
            with self._client.submit_tool_outputs_to_run(
                thread_id=run.thread_id, 
                run_id=run.id, 
                tool_outputs=tool_outputs, 
                stream=True,
                event_handler=self
        ) as stream:
                stream.until_done()


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

    message = assistant_client.create_message(thread_id=thread.id, role="user", content="Hello, send an email with the datetime and weather information in New York? Also let me know the details")
    logging.info(f"Created message, message ID {message.id}")

    with assistant_client.create_and_process_run(
        thread_id=thread.id, 
        assistant_id=assistant.id,
        stream=True,
        event_handler=MyEventHandler(assistant_client)
    ) as stream:
        stream.until_done()

    assistant_client.delete_assistant(assistant.id)
    logging.info("Deleted assistant")

    messages = assistant_client.list_messages(thread_id=thread.id)
    logging.info(f"Messages: {messages}")


if __name__ == "__main__":
    # Set logging level
    logging.basicConfig(level=logging.INFO)
    sample_assistant_stream_iteration()
