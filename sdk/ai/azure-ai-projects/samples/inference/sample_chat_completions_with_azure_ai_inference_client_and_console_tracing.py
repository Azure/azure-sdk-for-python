# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to get an authenticated 
    ChatCompletionsClient from the azure.ai.inference package. The client
    is already instrumented with console OpenTelemetry tracing.

USAGE:
    python sample_chat_completions_with_azure_ai_inference_client_and_console_tracing.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-inference azure-identity opentelemetry-sdk opentelemetry-exporter-otlp-proto-http

    Set these environment variables with your own values:
    * PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
    * AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED=true - Optional. For detailed traces, including chat request and response messages.
"""
import os
import sys
from azure.ai.projects import AIProjectClient
from azure.ai.inference.models import UserMessage
from azure.identity import DefaultAzureCredential

with AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
) as project_client:

    # Enable console tracing. Set environment variable `AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED=true`
    # for detailed logs, including chat request and response messages.
    project_client.diagnostics.enable(destination=sys.stdout)
    """
    if not project_client.diagnostics.db_enable(destination=sys.stdout):
        print("Application Insights was not enabled for this project.")
        print("Enable it via the 'Tracing' tab under 'Tools', in your AI Studio project page.")
        exit()

    print(f"Applications Insights connection string = {project_client.diagnostics.connection_string}")

    configure_azure_monitor(connection_string=project_client.diagnostics.application_insights.connection_string)
    """

    # Get an authenticated azure.ai.inference ChatCompletionsClient for your default Serverless connection:
    with project_client.inference.get_chat_completions_client() as client:

        response = client.complete(messages=[UserMessage(content="How many feet are in a mile?")])

        print(response.choices[0].message.content)
