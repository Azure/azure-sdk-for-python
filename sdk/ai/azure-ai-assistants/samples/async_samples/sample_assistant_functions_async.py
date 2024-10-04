# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to use assistants operations with user function call from
    the Azure Assistants service using a asynchronous client.

    See package documentation:
    https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-assistants/README.md#key-concepts

USAGE:
    python sample_assistant_functions_async.py

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

from azure.ai.assistants.aio import AssistantsClient
from azure.ai.assistants.models import AsyncFunctionTool
from azure.core.credentials import AzureKeyCredential

import os, time, logging, asyncio
import asyncio.threads

from user_async_functions import user_async_functions


def setup_console_trace_exporter():
    exporter = ConsoleSpanExporter()
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)
    trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(exporter))

    # Instrument requests to capture HTTP-related telemetry
    RequestsInstrumentor().instrument()


async def sample_assistant_functions():
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
    async with AssistantsClient(endpoint=endpoint, credential=AzureKeyCredential(key), api_version=api_version) as assistant_client:
        logging.info("Created assistant client")

        # Initialize assistant functions
        functions = AsyncFunctionTool(functions=user_async_functions)

        # Create assistant
        assistant = await assistant_client.create_assistant(
            model="gpt-4o-mini", name="my-assistant", instructions="You are a helpful assistant", tools=functions.definitions
        )
        logging.info("Created assistant, ID: %s", assistant.id)

        # Create thread for communication
        thread = await assistant_client.create_thread()
        logging.info("Created thread, ID: %s", thread.id)

        # Create and send message
        message = await assistant_client.create_message(thread_id=thread.id, role="user", content="Hello, what's the time?")
        logging.info("Created message, ID: %s", message.id)

        # Create and run assistant task
        run = await assistant_client.create_run(thread_id=thread.id, assistant_id=assistant.id)
        logging.info("Created run, ID: %s", run.id)

        # Polling loop for run status
        while run.status in ["queued", "in_progress", "requires_action"]:
            time.sleep(1)
            run = await assistant_client.get_run(thread_id=thread.id, run_id=run.id)

            if run.status == "requires_action" and run.required_action.submit_tool_outputs:
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                if not tool_calls:
                    logging.warning("No tool calls provided - cancelling run")
                    await assistant_client.cancel_run(thread_id=thread.id, run_id=run.id)
                    break

                tool_outputs = []
                for tool_call in tool_calls:
                    output = await functions.execute(tool_call)
                    tool_output = {
                            "tool_call_id": tool_call.id,
                            "output": output,
                        }
                    tool_outputs.append(tool_output)

                logging.info("Tool outputs: %s", tool_outputs)
                if tool_outputs:
                    await assistant_client.submit_tool_outputs_to_run(
                        thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs
                    )

            logging.info("Current run status: %s", run.status)

        logging.info("Run completed with status: %s", run.status)

        # Delete the assistant when done
        await assistant_client.delete_assistant(assistant.id)
        logging.info("Deleted assistant")

        # Fetch and log all messages
        messages = await assistant_client.list_messages(thread_id=thread.id)
        logging.info("Messages: %s", messages)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(sample_assistant_functions());