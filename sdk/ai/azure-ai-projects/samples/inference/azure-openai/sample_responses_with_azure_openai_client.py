# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to get an authenticated
    AzureOpenAI client from the openai package, and perform one `responses` operation.

USAGE:
    python sample_responses_with_azure_openai_client.py

    Before running the sample:

    pip install azure-ai-projects openai

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project. Required.
    2) MODEL_DEPLOYMENT_NAME - The model deployment name, as found in your AI Foundry project. Required.
    3) CONNECTION_NAME - The name of an Azure OpenAI connection, as found in the "Connected resources" tab
       in the Management Center of your AI Foundry project. Required.

    Update the Azure OpenAI api-version as needed (see `api_version=` below). Values can be found here:
    https://learn.microsoft.com/azure/ai-services/openai/reference#api-specs. Note that `responses` operations
    are only supported in the preview API version at the moment.
"""

import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

endpoint = os.environ["PROJECT_ENDPOINT"]
model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]
connection_name = os.environ["CONNECTION_NAME"]

with DefaultAzureCredential(exclude_interactive_browser_credential=False) as credential:

    with AIProjectClient(endpoint=endpoint, credential=credential) as project_client:

        print(
            "Get an authenticated Azure OpenAI client for the parent AI Services resource, and perform a 'responses' operation:"
        )
        with project_client.get_openai_client(api_version="2025-04-01-preview") as client:

            response = client.responses.create(
                model=model_deployment_name,
                input="How many feet are in a mile?",
            )

            print(response.output_text)

        print(
            "Get an authenticated Azure OpenAI client for a connected Azure OpenAI service, and perform a 'responses' operation:"
        )
        with project_client.get_openai_client(
            api_version="2025-04-01-preview", connection_name=connection_name
        ) as client:

            response = client.responses.create(
                model=model_deployment_name,
                input="How many feet are in a mile?",
            )

            print(response.output_text)
