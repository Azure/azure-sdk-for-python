# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to get an authenticated 
    AsyncAzureOpenAI client from the azure.ai.inference package.

USAGE:
    python sample_get_azure_openai_client.py

    Before running the sample:

    pip install azure-ai-projects openai

    Set this environment variable with your own value:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.

    Update the Azure OpenAI api-version as needed. See `api_version=` below.

    Update the model deployment name as needed. See `model=` below.
"""
import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

with AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
) as project_client:

    # Get an authenticated OpenAI client for your default Azure OpenAI connection:
    with project_client.inference.get_azure_openai_client(api_version="2024-06-01") as client:

        response = client.chat.completions.create(
            model="gpt-35-turbo-16k",
            messages=[
                {
                    "role": "user",
                    "content": "How many feet are in a mile?",
                },
            ],
        )

        print(response.choices[0].message.content)
