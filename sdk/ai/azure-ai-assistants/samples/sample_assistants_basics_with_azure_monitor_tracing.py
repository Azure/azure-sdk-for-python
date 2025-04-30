# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use basic assistant operations from
    the Azure Assistants service using a synchronous client with Azure Monitor tracing.
    View the results in the "Tracing" tab in your Azure AI Foundry project page.

USAGE:
    python sample_assistants_basics_with_azure_monitor_tracing.py

    Before running the sample:

    pip install azure-ai-assistants azure-identity azure-monitor-opentelemetry

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - the Azure AI Assistants endpoint.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED - Optional. Set to `true` to trace the content of chat
       messages, which may contain personal data. False by default.
"""

import os, time
from azure.ai.assistants import AssistantsClient
from azure.ai.assistants.telemetry import enable_telemetry
from azure.identity import DefaultAzureCredential

assistants_client = AssistantsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

# [START enable_tracing]
from opentelemetry import trace
from azure.monitor.opentelemetry import configure_azure_monitor

# Enable Azure Monitor tracing
application_insights_connection_string = os.environ["AI_APPINSIGHTS_CONNECTION_STRING"]
configure_azure_monitor(connection_string=application_insights_connection_string)

# enable additional instrumentations
enable_telemetry()

scenario = os.path.basename(__file__)
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span(scenario):
    with assistants_client:
        # [END enable_tracing]
        assistant = assistants_client.create_assistant(
            model=os.environ["MODEL_DEPLOYMENT_NAME"], name="my-assistant", instructions="You are helpful assistant"
        )
        print(f"Created assistant, assistant ID: {assistant.id}")

        thread = assistants_client.create_thread()
        print(f"Created thread, thread ID: {thread.id}")

        message = assistants_client.create_message(
            thread_id=thread.id, role="user", content="Hello, tell me a hilarious joke"
        )
        print(f"Created message, message ID: {message.id}")

        run = assistants_client.create_run(thread_id=thread.id, assistant_id=assistant.id)

        # Poll the run as long as run status is queued or in progress
        while run.status in ["queued", "in_progress", "requires_action"]:
            # Wait for a second
            time.sleep(1)
            run = assistants_client.get_run(thread_id=thread.id, run_id=run.id)

            print(f"Run status: {run.status}")

        assistants_client.delete_assistant(assistant.id)
        print("Deleted assistant")

        messages = assistants_client.list_messages(thread_id=thread.id)
        print(f"messages: {messages}")
