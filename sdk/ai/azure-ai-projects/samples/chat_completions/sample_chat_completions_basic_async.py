# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to run a basic chat completions operation
    using the asynchronous AIProjectClient and AsyncOpenAI clients.

    See also https://platform.openai.com/docs/api-reference/chat/create?lang=python

USAGE:
    python sample_chat_completions_basic_async.py

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

from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential
from openai.types.chat import ChatCompletionMessageParam

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model = os.environ["FOUNDRY_MODEL_NAME"]


async def main() -> None:

    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Give me one fun fact about the Eiffel Tower."},
        ]

        completion = await openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,
        )

        assistant_message = completion.choices[0].message.content
        print(f"Assistant: {assistant_message}")

        messages.append({"role": "assistant", "content": assistant_message})
        messages.append({"role": "user", "content": "Now give me one related fun fact."})

        completion = await openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,
        )

        assistant_message = completion.choices[0].message.content
        print(f"Assistant: {assistant_message}")


if __name__ == "__main__":
    asyncio.run(main())
