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
       page of your Azure AI Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.ai.projects import AIProjectClient

load_dotenv()

# Create OpenAI client with Azure AI authentication and logging
project_client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with project_client:
    # [START response_stream_method]
    openai_client = project_client.get_openai_client()

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
