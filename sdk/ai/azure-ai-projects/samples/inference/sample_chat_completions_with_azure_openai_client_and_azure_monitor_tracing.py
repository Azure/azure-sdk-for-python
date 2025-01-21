# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to get an authenticated
    AzureOpenAI client from the openai package. The client is already instrumented
    to upload traces to Azure Monitor. View the results in the "Tracing" tab in your
    Azure AI Foundry project page.

USAGE:
    python sample_chat_completions_with_azure_openai_client_and_azure_monitor_tracing.py

    Before running the sample:

    pip install azure-ai-projects openai azure-monitor-opentelemetry opentelemetry-instrumentation-openai-v2

    Set these environment variables with your own values:
    * PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Foundry project.
    * MODEL_DEPLOYMENT_NAME - The model deployment name, as found in your AI Foundry project.
    * OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT - Optional. Set to `true` to trace the content of chat
      messages, which may contain personal data. False by default.

    Update the Azure OpenAI api-version as needed (see `api_version=` below). Values can be found here:
    https://learn.microsoft.com/azure/ai-services/openai/reference#api-specs
"""
import os
from azure.ai.projects import AIProjectClient
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

    # Get an authenticated OpenAI client for your default Azure OpenAI connection:
    with project_client.inference.get_azure_openai_client(api_version="2024-06-01") as client:

        response = client.chat.completions.create(
            model=model_deployment_name,
            messages=[
                {
                    "role": "user",
                    "content": "How many feet are in a mile?",
                },
            ],
        )

        print(response.choices[0].message.content)
