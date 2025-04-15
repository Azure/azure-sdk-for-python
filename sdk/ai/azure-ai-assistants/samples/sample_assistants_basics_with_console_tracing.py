# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use basic assistant operations from
    the Azure Assistants service using a synchronous client with tracing to console.

USAGE:
    python sample_assistants_basics_with_console_tracing.py

    Before running the sample:

    pip install azure-ai-assistants azure-identity opentelemetry-sdk azure-core-tracing-opentelemetry

    If you want to export telemetry to OTLP endpoint (such as Aspire dashboard
    https://learn.microsoft.com/dotnet/aspire/fundamentals/dashboard/standalone?tabs=bash)
    install:

    pip install opentelemetry-exporter-otlp-proto-grpc

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - the Azure AI Assistants endpoint.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in 
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED - Optional. Set to `true` to trace the content of chat
       messages, which may contain personal data. False by default.
"""

import os, sys, time
from azure.ai.assistants import AssistantsClient
from azure.ai.assistants.telemetry import enable_telemetry
from azure.identity import DefaultAzureCredential
from opentelemetry import trace

assistants_client = AssistantsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

# Enable console tracing
# or, if you have local OTLP endpoint running, change it to
# assistants_client.telemetry.enable(destination="http://localhost:4317")
enable_telemetry(destination=sys.stdout)

scenario = os.path.basename(__file__)
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span(scenario):
    with assistants_client:
        assistant = assistants_client.create_assistant(
            model=os.environ["MODEL_DEPLOYMENT_NAME"], name="my-assistant", instructions="You are helpful assistant"
        )
        print(f"Created assistant, assistant ID: {assistant.id}")

        thread = assistants_client.create_thread()
        print(f"Created thread, thread ID: {thread.id}")

        message = assistants_client.create_message(thread_id=thread.id, role="user", content="Hello, tell me a joke")
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
