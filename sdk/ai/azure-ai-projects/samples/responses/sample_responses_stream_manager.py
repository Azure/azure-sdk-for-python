# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to stream through responses.stream that returns a responses stream manager.

USAGE:
    python sample_responses_stream_method.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.ai.projects import AIProjectClient

load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):
    # [START response_stream_method]
    response = openai_client.responses.create(
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        input=[
            {"role": "user", "content": "What is the size of France in square miles?"},
        ],
        stream=False,  # Create non-streaming response
    )

    print(f"Initial response: {response.output_text}")
    print(f"Response ID: {response.id}")

    # Now create a streaming version using the same input but with stream=True
    # This demonstrates an alternative approach since response.stream() may not be available
    with openai_client.responses.stream(
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        input=[
            {"role": "user", "content": "Now tell me about the capital city of France."},
        ],
        previous_response_id=response.id,  # Continue the conversation
    ) as responses_stream_manager:

        # Process streaming events as they arrive
        for event in responses_stream_manager:
            if event.type == "response.created":
                print(f"Stream response created with ID: {event.response.id}")
            elif event.type == "response.output_text.delta":
                print(f"Delta: {event.delta}")
            elif event.type == "response.text.done":
                print(f"Response done with full message: {event.text}")
            elif event.type == "response.completed":
                print(f"Response completed with full message: {event.response.output_text}")
        # [END response_stream_method]
