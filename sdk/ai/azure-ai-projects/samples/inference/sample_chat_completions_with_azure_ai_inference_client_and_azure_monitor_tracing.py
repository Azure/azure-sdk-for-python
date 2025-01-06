# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to get an authenticated
    ChatCompletionsClient from the azure.ai.inference package. The client
    is already instrumented to upload traces to Azure Monitor. View the results
    in the "Tracing" tab in your Azure AI Foundry project page.

USAGE:
    python sample_chat_completions_with_azure_ai_inference_client_and_azure_monitor_tracing.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-inference azure-identity azure-monitor-opentelemetry

    Set these environment variables with your own values:
    * PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Foundry project.
    * MODEL_DEPLOYMENT_NAME - The model deployment name, as found in your AI Foundry project.
    * AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED - Optional. Set to `true` to trace the content of chat
      messages, which may contain personal data. False by default.
"""
import os
from azure.ai.projects import AIProjectClient
from azure.ai.inference.models import UserMessage
from azure.identity import DefaultAzureCredential
from azure.monitor.opentelemetry import configure_azure_monitor

project_connection_string = os.environ["PROJECT_CONNECTION_STRING"]
model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]

with AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=project_connection_string,
) as project_client:

    # Enable Azure Monitor tracing
    application_insights_connection_string = project_client.telemetry.get_connection_string()
    if not application_insights_connection_string:
        print("Application Insights was not enabled for this project.")
        print("Enable it via the 'Tracing' tab in your AI Foundry project page.")
        exit()

    # Enable additional instrumentations for openai and langchain
    # which are not included by Azure Monitor out of the box
    project_client.telemetry.enable()
    configure_azure_monitor(connection_string=application_insights_connection_string)

    # Get an authenticated azure.ai.inference ChatCompletionsClient for your default Serverless connection:
    with project_client.inference.get_chat_completions_client() as client:

        response = client.complete(
            model=model_deployment_name, messages=[UserMessage(content="How many feet are in a mile?")]
        )

        print(response.choices[0].message.content)
