# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_get_chat_completions_client.py

DESCRIPTION:
    Given an AzureAIClient, this sample demonstrates how to get an authenticated 
    async ChatCompletionsClient from the azure.ai.inference package.

USAGE:
    python sample_get_chat_completions_client.py

    Before running the sample:

    pip install azure.ai.client azure-identity

    Set this environment variables with your own values:
    AI_CLIENT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""
import os
from azure.ai.client import AzureAIClient
from azure.ai.inference.models import UserMessage
from azure.identity import DefaultAzureCredential

ai_client = AzureAIClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["AI_CLIENT_CONNECTION_STRING"],
)

# Get an authenticated azure.ai.inference chat completions client for your default Serverless connection:
client = ai_client.inference.get_chat_completions_client()

response = client.complete(messages=[UserMessage(content="How many feet are in a mile?")])

print(response.choices[0].message.content)
