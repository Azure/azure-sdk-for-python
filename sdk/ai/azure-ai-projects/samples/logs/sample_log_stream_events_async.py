# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to capture Azure-core HTTP logs and OpenAI
    transport logs into a file while running an asynchronous streaming responses
    operation. With logging_enable=True, request bodies, response metadata, and
    token are included in the log file. Streamed response events are printed to
    the console and are not automatically written to SDK logs as parsed events.

    See also https://platform.openai.com/docs/guides/streaming-responses?api-mode=responses&lang=python

USAGE:
    python samples/logs/sample_log_stream_events_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.5.0" python-dotenv aiohttp

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model.

    This sample writes Azure-core and OpenAI transport logs to a timestamped temp log file.
"""

import asyncio
import logging
import os

from dotenv import load_dotenv

from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential

from log_utils import create_timestamped_temp_log_file

load_dotenv()

LOG_FILE = create_timestamped_temp_log_file(__file__)

logger = logging.getLogger("azure")
logger.setLevel(logging.DEBUG)
logger.handlers.clear()

# Keep stdout available for streamed sample output while also writing SDK logs to a file.
file_handler = logging.FileHandler(filename=LOG_FILE, encoding="utf-8")
logger.addHandler(file_handler)

transport_logger = logging.getLogger("azure.ai.projects.openai_transport")
transport_logger.setLevel(logging.DEBUG)
transport_logger.propagate = False
transport_logger.addHandler(file_handler)

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model = os.environ["FOUNDRY_MODEL_NAME"]


async def main() -> None:
    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential, logging_enable=True) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        stream_response = await openai_client.responses.create(
            model=model,
            input=[
                {"role": "user", "content": "Tell me about the capital city of France"},
            ],
            stream=True,
        )

        async for event in stream_response:
            if event.type == "response.created":
                print(f"Stream response created with ID: {event.response.id}\n")
            elif event.type == "response.output_text.delta":
                print(event.delta, end="", flush=True)
            elif event.type == "response.text.done":
                print("\n\nResponse text done. Access final text in 'event.text'")
            elif event.type == "response.completed":
                print("\n\nResponse completed. Access final text in 'event.response.output_text'")

    print(f"Azure-core and OpenAI transport logs written to {LOG_FILE}")


if __name__ == "__main__":
    asyncio.run(main())
