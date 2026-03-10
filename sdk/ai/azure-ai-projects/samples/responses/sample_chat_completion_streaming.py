# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to perform streaming chat completions
    using the synchronous AIProjectClient and OpenAI client.

USAGE:
    python sample_chat_completion_streaming.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):
    # Basic streaming chat completion
    print("=== Streaming Chat Completion ===")
    print("User: Write a short poem about artificial intelligence.\n")
    print("Assistant: ", end="", flush=True)

    with openai_client.responses.stream(
        model=os.environ["FOUNDRY_MODEL_NAME"],
        input="Write a short poem about artificial intelligence.",
    ) as response_stream:
        for event in response_stream:
            if event.type == "response.output_text.delta":
                print(event.delta, end="", flush=True)
            elif event.type == "response.completed":
                print("\n\n[Streaming completed]")

    # Streaming with conversation history
    print("\n=== Streaming with Conversation History ===")

    # First message
    response = openai_client.responses.create(
        model=os.environ["FOUNDRY_MODEL_NAME"],
        input="What is the speed of light?",
    )
    print(f"User: What is the speed of light?")
    print(f"Assistant: {response.output_text}\n")

    # Follow-up with streaming
    print(f"User: Can you explain why that speed is significant?\n")
    print("Assistant: ", end="", flush=True)

    with openai_client.responses.stream(
        model=os.environ["FOUNDRY_MODEL_NAME"],
        input="Can you explain why that speed is significant?",
        previous_response_id=response.id,
    ) as response_stream:
        for event in response_stream:
            if event.type == "response.output_text.delta":
                print(event.delta, end="", flush=True)
            elif event.type == "response.completed":
                print("\n\n[Streaming completed]")
