# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to perform basic chat completions
    using the asynchronous AIProjectClient and AsyncOpenAI client.

USAGE:
    python sample_chat_completion_basic_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv aiohttp

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import asyncio
import os
from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]


async def main() -> None:

    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        # Basic single-turn chat completion
        print("=== Basic Chat Completion ===")
        response = await openai_client.responses.create(
            model=os.environ["FOUNDRY_MODEL_NAME"],
            input="What is the capital of France?",
        )
        print(f"Response: {response.output_text}\n")

        # Chat completion with system instructions
        print("=== Chat with System Instructions ===")
        response = await openai_client.responses.create(
            model=os.environ["FOUNDRY_MODEL_NAME"],
            instructions="You are a helpful assistant that answers questions concisely in one sentence.",
            input="Explain machine learning.",
        )
        print(f"Response: {response.output_text}\n")

        # Multi-turn conversation
        print("=== Multi-turn Conversation ===")
        response = await openai_client.responses.create(
            model=os.environ["FOUNDRY_MODEL_NAME"],
            input="Tell me about Python programming language.",
        )
        print(f"User: Tell me about Python programming language.")
        print(f"Assistant: {response.output_text}\n")

        # Continue the conversation using previous_response_id
        response = await openai_client.responses.create(
            model=os.environ["FOUNDRY_MODEL_NAME"],
            input="What are its main advantages?",
            previous_response_id=response.id,
        )
        print(f"User: What are its main advantages?")
        print(f"Assistant: {response.output_text}\n")


if __name__ == "__main__":
    asyncio.run(main())
