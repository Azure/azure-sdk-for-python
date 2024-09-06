# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to use assistants operations with user function call from
    the Azure Assistants service using a synchronous client.

    See package documentation:
    https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-assistants/README.md#key-concepts

USAGE:
    python sample_assistant_basics.py

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
from user_functions import user_functions

import os, time, json


def setup_console_trace_exporter():
    exporter = ConsoleSpanExporter()
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)
    trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(exporter))

    # Instrument requests to capture HTTP-related telemetry
    RequestsInstrumentor().instrument()


def process_tool_calls(tool_calls):
    print("Processing tool calls")
    tool_outputs = []
    for tool_call in tool_calls:
        function_response = str(handle_function_call(tool_call.function.name, tool_call.function.arguments))
        print(f"Function response: {function_response}")       
        tool_output = {
            "tool_call_id": tool_call.id,
            "output": function_response,
        }
        tool_outputs.append(tool_output)

    return tool_outputs


def handle_function_call(function_name, arguments):
    print(f"Handling function call: {function_name}, arguments: {arguments}")

    if function_name in user_functions:
        function = user_functions[function_name]
        
        try:
            # Parse arguments from JSON string to dictionary
            parsed_arguments = json.loads(arguments)
        except json.JSONDecodeError:
            print("Error decoding JSON arguments.")
            parsed_arguments = {}

        # Ensure parsed_arguments is a dictionary
        if isinstance(parsed_arguments, dict):
            if not parsed_arguments:
                return function()
            else:
                return function(**parsed_arguments)
        else:
            print("Parsed arguments are not a valid dictionary.")
            return None

    else:
        print(f"Function {function_name} not found in user defined functions")
        return None


user_tools = [{
    "type": "function",
    "function": {
        "name": "fetch_current_datetime",
        "description": "Get the current time as a JSON string.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}]


def sample_assistant_operation_with_functions():

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
        model="gpt", name="my-assistant", instructions="You are helpful assistant", tools=user_tools
    )
    print("Created assistant, assistant ID", assistant.id)

    thread = assistant_client.create_thread()
    print("Created thread, thread ID", thread.id)

    message = assistant_client.create_message(thread_id=thread.id, role="user", content="Hello, what's the time?")
    print("Created message, message ID", message.id)

    run = assistant_client.create_run(thread_id=thread.id, assistant_id=assistant.id)
    print("Created run, run ID", run.id)

    # poll the run as long as run status is queued or in progress
    while run.status in ["queued", "in_progress", "requires_action"]:
        # wait for a second
        time.sleep(1)
        run = assistant_client.get_run(thread_id=thread.id, run_id=run.id)

        if run.status == "requires_action":

            submit_tool_outputs_action : SubmitToolOutputsDetails = run.required_action.submit_tool_outputs
            tool_calls = submit_tool_outputs_action.tool_calls
            if tool_calls is None:
                print("Processing run requires tool call action but no tool calls provided, cancel the run")
                assistant_client.cancel_run(thread_id=thread.id, run_id=run.id)

            tool_outputs = process_tool_calls(tool_calls)
            if tool_outputs:
                print("Submitting tool outputs")
                assistant_client.submit_tool_outputs_to_run(thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs)

        print("Run status:", run.status)

    print("Run completed with status:", run.status)

    messages = assistant_client.list_messages(thread_id=thread.id)
    print("messages:", messages)

    assistant_client.delete_assistant(assistant.id)
    print("Deleted assistant")


if __name__ == "__main__":
    sample_assistant_operation_with_functions()
