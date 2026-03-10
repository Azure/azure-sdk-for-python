# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use advanced chat completion parameters
    like temperature, max_tokens, and other configuration options using
    the synchronous AIProjectClient and OpenAI client.

USAGE:
    python sample_chat_completion_advanced.py

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
    model = os.environ["FOUNDRY_MODEL_NAME"]

    # Temperature control (lower for more deterministic, higher for more creative)
    print("=== Low Temperature (Deterministic) ===")
    response = openai_client.responses.create(
        model=model,
        input="List three programming languages.",
        temperature=0.1,  # More focused and deterministic
    )
    print(f"Response (temp=0.1): {response.output_text}\n")

    print("=== High Temperature (Creative) ===")
    response = openai_client.responses.create(
        model=model,
        input="Write a creative tagline for a coffee shop.",
        temperature=1.5,  # More creative and varied
    )
    print(f"Response (temp=1.5): {response.output_text}\n")

    # Max tokens control
    print("=== Max Tokens Limit ===")
    response = openai_client.responses.create(
        model=model,
        input="Explain the history of computers.",
        max_output_tokens=50,  # Limit response length
    )
    print(f"Response (max_tokens=50): {response.output_text}\n")

    # Top-p (nucleus sampling)
    print("=== Top-P Sampling ===")
    response = openai_client.responses.create(
        model=model,
        input="Describe a sunset.",
        top_p=0.9,  # Consider tokens with cumulative probability up to 90%
        temperature=0.8,
    )
    print(f"Response (top_p=0.9): {response.output_text}\n")

    # Presence and frequency penalties
    print("=== With Presence Penalty (Encourage New Topics) ===")
    response = openai_client.responses.create(
        model=model,
        input="Write about technology.",
        presence_penalty=0.8,  # Penalize repeated topics
        temperature=0.7,
    )
    print(f"Response: {response.output_text}\n")

    print("=== With Frequency Penalty (Reduce Repetition) ===")
    response = openai_client.responses.create(
        model=model,
        input="List benefits of exercise.",
        frequency_penalty=0.5,  # Reduce repeated words
    )
    print(f"Response: {response.output_text}\n")

    # Combining multiple parameters
    print("=== Combined Advanced Parameters ===")
    response = openai_client.responses.create(
        model=model,
        instructions="You are a creative storyteller.",
        input="Write the opening of a science fiction story.",
        temperature=0.9,
        max_output_tokens=150,
        top_p=0.95,
        presence_penalty=0.3,
        frequency_penalty=0.3,
    )
    print(f"Response: {response.output_text}\n")

    # Using metadata for tracking
    print("=== With Metadata ===")
    response = openai_client.responses.create(
        model=model,
        input="What is machine learning?",
        metadata={
            "user_id": "user123",
            "session_id": "session456",
            "request_type": "educational",
        },
    )
    print(f"Response: {response.output_text}")
    print(f"Response ID: {response.id}")
