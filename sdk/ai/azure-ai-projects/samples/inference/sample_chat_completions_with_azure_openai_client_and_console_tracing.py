# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to get an authenticated 
    AzureOpenAI client from the openai package. The client is already instrumented
    with console OpenTelemetry tracing.

USAGE:
    python sample_chat_completions_with_azure_openai_client_and_console_tracing.py

    Before running the sample:

    pip install azure-ai-projects openai opentelemetry.instrumentation.openai opentelemetry-sdk opentelemetry-exporter-otlp-proto-http

    Set these environment variables with your own values:
    * PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
    * AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED=true - Optional. For detailed traces, including chat request and response messages.
"""
import os
import sys
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

with AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
) as project_client:

    # Enable console tracing. Set environment variable `AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED=true`
    # for detailed logs, including chat request and response messages.
    project_client.diagnostics.enable(destination=sys.stdout)

    # Get an authenticated OpenAI client for your default Azure OpenAI connection:
    with project_client.inference.get_azure_openai_client(api_version="2024-06-01") as client:

        response = client.chat.completions.create(
            model="gpt-4-0613",
            messages=[
                {
                    "role": "user",
                    "content": "How many feet are in a mile?",
                },
            ],
        )

        print(response.choices[0].message.content)
