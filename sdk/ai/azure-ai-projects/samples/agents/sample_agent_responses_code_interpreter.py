# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use the code interpreter tool
    using the synchronous client.

USAGE:
    python sample_agent_responses_code_interpreter.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity load_dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Azure AI Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

load_dotenv()

project_client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with project_client:

    openai_client = project_client.get_openai_client()

    # See https://platform.openai.com/docs/api-reference/responses/create?lang=python
    response = openai_client.responses.create(
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        input="I need to solve the equation 3x + 11 = 14. Can you help me?",
        tools=[{"type": "code_interpreter", "container": {"type": "auto"}}],
    )
    print(f"Response output: {response.output_text}")
