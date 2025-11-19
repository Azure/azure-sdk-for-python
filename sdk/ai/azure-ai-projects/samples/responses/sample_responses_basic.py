# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to run a basic responses operation
    using the synchronous AIProject and OpenAI clients.

    See also https://platform.openai.com/docs/api-reference/responses/create?lang=python

USAGE:
    python sample_responses_basic.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" openai azure-identity python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):
    # [START responses]
    with project_client.get_openai_client() as openai_client:
        response = openai_client.responses.create(
            model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
            input="What is the size of France in square miles?",
        )
        print(f"Response output: {response.output_text}")

        response = openai_client.responses.create(
            model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
            input="And what is the capital city?",
            previous_response_id=response.id,
        )
        print(f"Response output: {response.output_text}")
        # [END responses]
