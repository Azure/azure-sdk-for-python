# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_get_azure_openai_client.py

DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to get an authenticated 
    AsyncAzureOpenAI client from the azure.ai.inference package.

USAGE:
    python sample_get_azure_openai_client.py

    Before running the sample:

    pip install azure.ai.project openai

    Set this environment variable with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""
import os
from azure.ai.project import AIProjectClient
from azure.identity import DefaultAzureCredential

with AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
) as project_client:

    # Get an authenticated OpenAI client for your default Azure OpenAI connection:
    with project_client.inference.get_azure_openai_client() as client:

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
