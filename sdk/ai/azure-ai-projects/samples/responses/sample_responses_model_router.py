# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to invoke a Microsoft Foundry Model Router deployment
    using the Responses API and inspect the model selected by the router.

USAGE:
    python sample_responses_model_router.py

    Before running the sample:

    pip install "azure-ai-projects>=2.6.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
"""

import os

from dotenv import load_dotenv

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_router_deployment = "model-router"

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):
    print(f"Sending request to Model Router deployment: {model_router_deployment}")

    response = openai_client.responses.create(
        model=model_router_deployment,
        input="Explain why the sky appears blue in three concise sentences.",
        extra_headers={"Foundry-Features": "ModelRouterControls=V1Preview"},
    )

    print(f"\nResponse output:\n{response.output_text}")
    print("\nModel Router result:")
    print(f"  Response ID: {response.id}")
    print(f"  Status: {response.status}")
    print(f"  Selected model: {response.model}")
    if response.usage:
        print(f"  Input tokens: {response.usage.input_tokens}")
        print(f"  Output tokens: {response.usage.output_tokens}")
        print(f"  Total tokens: {response.usage.total_tokens}")
