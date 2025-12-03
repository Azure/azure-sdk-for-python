# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to run a basic streaming responses operation
    using OpenAI client `.responses.create()` method with `stream=True`.

    See also https://platform.openai.com/docs/api-reference/responses/create?lang=python

    Note also the alternative streaming approach shown in sample_responses_stream_manager.py.

USAGE:
    python sample_responses_stream_events.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" python-dotenv

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
    project_client.get_openai_client() as openai_client,
):

    response_stream_events = openai_client.responses.create(
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        input=[
            {"role": "user", "content": "Give me 5 good reasons why I should exercise daily."},
        ],
        stream=True,
    )

    for event in response_stream_events:
        if event.type == "response.created":
            print(f"Stream response created with ID: {event.response.id}")
        elif event.type == "response.output_text.delta":
            print(f"Delta: {event.delta}")
        elif event.type == "response.text.done":
            print(f"Response done with full message: {event.text}")
        elif event.type == "response.completed":
            print(f"Response completed with full message: {event.response.output_text}")
