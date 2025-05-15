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

    pip install azure-ai-projects azure-ai-inference azure-identity opentelemetry-sdk azure-core-tracing-opentelemetry

    If you want to export telemetry to OTLP endpoint (such as Aspire dashboard
    https://learn.microsoft.com/dotnet/aspire/fundamentals/dashboard/standalone?tabs=bash)
    install:

    pip install opentelemetry-exporter-otlp-proto-grpc

    Set these environment variables with your own values:
    * PROJECT_CONNECTION_STRING - The Azure AI Project connection string, as found in your AI Foundry project.
    * MODEL_DEPLOYMENT_NAME - The model deployment name, as found in your AI Foundry project.
    * AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED - Optional. Set to `true` to trace the content of chat
      messages, which may contain personal data. False by default.
"""
import os
import sys
from azure.ai.inference.models import UserMessage
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

project_connection_string = os.environ["PROJECT_CONNECTION_STRING"]
model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]

with AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=project_connection_string,
) as project_client:

    # Enable console tracing
    # or, if you have local OTLP endpoint running, change it to
    # project_client.telemetry.enable(destination="http://localhost:4317")
    project_client.telemetry.enable(destination=sys.stdout)

    # Get an authenticated azure.ai.inference ChatCompletionsClient for your default Serverless connection:
    with project_client.inference.get_chat_completions_client() as client:

        response = client.complete(
            model=model_deployment_name, messages=[UserMessage(content="How many feet are in a mile?")]
        )

        print(response.choices[0].message.content)
