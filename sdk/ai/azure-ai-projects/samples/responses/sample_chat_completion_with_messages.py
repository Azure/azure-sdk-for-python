# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use chat completions with explicit
    message history, including user and assistant messages.

USAGE:
    python sample_chat_completion_with_messages.py

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

    # Using message array for conversation history
    print("=== Chat with Message History ===")
    response = openai_client.responses.create(
        model=model,
        instructions="You are a helpful coding assistant.",
        input=[
            {"role": "user", "content": "How do I read a file in Python?"},
            {
                "role": "assistant",
                "content": "You can use the `open()` function with a context manager: `with open('file.txt', 'r') as f: content = f.read()`",
            },
            {"role": "user", "content": "Can you show me how to write to a file instead?"},
        ],
    )
    print("Conversation context:")
    print("User: How do I read a file in Python?")
    print("Assistant: You can use the `open()` function with a context manager...")
    print("\nUser: Can you show me how to write to a file instead?")
    print(f"Assistant: {response.output_text}\n")

    # Role-based conversation
    print("=== Role-based Conversation ===")
    response = openai_client.responses.create(
        model=model,
        instructions="You are a Shakespearean poet.",
        input=[
            {"role": "user", "content": "Write a greeting."},
        ],
    )
    print("User: Write a greeting.")
    print(f"Assistant (as Shakespeare): {response.output_text}\n")

    # Complex multi-turn with explicit messages
    print("=== Complex Multi-turn Conversation ===")
    messages = [
        {"role": "user", "content": "I need help debugging my code."},
    ]

    response = openai_client.responses.create(
        model=model,
        instructions="You are an expert software engineer who helps debug code.",
        input=messages,
    )
    print(f"User: {messages[0]['content']}")
    print(f"Assistant: {response.output_text}\n")

    # Add to message history and continue
    messages.append({"role": "assistant", "content": response.output_text})
    messages.append({"role": "user", "content": "The error says 'list index out of range'"})

    response = openai_client.responses.create(
        model=model,
        instructions="You are an expert software engineer who helps debug code.",
        input=messages,
    )
    print(f"User: The error says 'list index out of range'")
    print(f"Assistant: {response.output_text}")
