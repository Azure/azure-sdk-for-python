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
    * PROJECT_CONNECTION_STRING - The Azure AI Project connection string, as found in your AI Studio Project.
    * MODEL_DEPLOYMENT_NAME - The model deployment name, as found in your AI Studio Project.
    * AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED - Optional. Set to `true` to trace the content of chat
      messages, which may contain personal data. False by default.
"""
import os
import sys
from azure.ai.projects import AIProjectClient
from azure.ai.inference.models import UserMessage
from azure.identity import DefaultAzureCredential

project_connection_string = os.environ["PROJECT_CONNECTION_STRING"]
model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]

with AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=project_connection_string,
) as project_client:

    # Enable console tracing
    project_client.telemetry.enable(destination=sys.stdout)

    # Get an authenticated azure.ai.inference ChatCompletionsClient for your default Serverless connection:
    with project_client.inference.get_chat_completions_client() as client:

        response = client.complete(
            model=model_deployment_name, messages=[UserMessage(content="How many feet are in a mile?")]
        )

        print(response.choices[0].message.content)
