# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to maintain a multi-turn conversation
    using the synchronous AIProjectClient and OpenAI client, with
    message history management.

USAGE:
    python sample_chat_completion_conversation.py

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


def chat_turn(openai_client, model: str, user_input: str, previous_response_id: str = None) -> str:
    """Helper function to handle a single chat turn."""
    print(f"\nUser: {user_input}")

    response = openai_client.responses.create(
        model=model,
        input=user_input,
        previous_response_id=previous_response_id,
    )

    print(f"Assistant: {response.output_text}")
    return response.id


with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):
    model = os.environ["FOUNDRY_MODEL_NAME"]

    print("=== Multi-turn Conversation with Context ===")

    # Turn 1: Initial question
    response_id = chat_turn(
        openai_client,
        model,
        "I'm planning a trip to Tokyo. What are the must-see attractions?",
    )

    # Turn 2: Follow-up question (references previous context)
    response_id = chat_turn(
        openai_client,
        model,
        "How many days would you recommend for visiting all of those?",
        previous_response_id=response_id,
    )

    # Turn 3: Another follow-up
    response_id = chat_turn(
        openai_client,
        model,
        "What's the best time of year to visit?",
        previous_response_id=response_id,
    )

    # Turn 4: Final question
    response_id = chat_turn(
        openai_client,
        model,
        "Can you recommend some traditional restaurants?",
        previous_response_id=response_id,
    )

    print("\n=== Conversation with System Instructions ===")

    # Start new conversation with system instructions
    response = openai_client.responses.create(
        model=model,
        instructions="You are a professional translator. Translate user input to French.",
        input="Hello, how are you?",
    )
    print(f"\nUser: Hello, how are you?")
    print(f"Assistant: {response.output_text}")

    # Continue with same instructions
    response = openai_client.responses.create(
        model=model,
        instructions="You are a professional translator. Translate user input to French.",
        input="I love programming.",
        previous_response_id=response.id,
    )
    print(f"\nUser: I love programming.")
    print(f"Assistant: {response.output_text}")
