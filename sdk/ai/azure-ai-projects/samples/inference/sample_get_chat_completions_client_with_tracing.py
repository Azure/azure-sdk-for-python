# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_get_chat_completions_client_with_tracing.py

DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to get an authenticated 
    async ChatCompletionsClient from the azure.ai.inference package.

USAGE:
    python sample_get_chat_completions_client_with_tracing.py

    Before running the sample:

    pip install azure.ai.projects azure-identity

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""
import os
from azure.ai.projects import AIProjectClient
from azure.ai.inference.models import UserMessage
from azure.identity import DefaultAzureCredential

with AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
) as project_client:

    if not project_client.diagnostics.enable():
        print("Application Insights was not enabled for this project.")
        print("Enable it via the 'Tracing' tab under 'Tools', in your AI Studio project page.")
        exit()

    print(f"Applications Insights connection string = {project_client.diagnostics.connection_string}")

    # Get an authenticated azure.ai.inference chat completions client for your default Serverless connection:
    with project_client.inference.get_chat_completions_client() as client:

        response = client.complete(messages=[UserMessage(content="How many feet are in a mile?")])

        print(response.choices[0].message.content)
