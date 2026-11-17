# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to capture both Azure-core HTTP logs and
    OpenAI transport logs into a single file while running a Prompt Agent operation.
    With logging_enable=True, all logs will include request bodies, response body, and token.

USAGE:
    python samples/logs/sample_log_all.py

    Before running the sample:

    pip install "azure-ai-projects>=2.5.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model.
    3) FOUNDRY_AGENT_NAME - Optional. Defaults to "MyAgent".

    This sample writes Azure-core and OpenAI transport logs to a timestamped temp log file.
"""

import logging
import os

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from log_utils import create_timestamped_temp_log_file
from util import create_version_with_endpoint

load_dotenv()

LOG_FILE = create_timestamped_temp_log_file(__file__)

file_handler = logging.FileHandler(filename=LOG_FILE, encoding="utf-8")

# Logger for logs from azure-ai-projects SDK through Azure-core.
logger = logging.getLogger("azure")
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

# Logger for logs from the OpenAI client.
openai_logger = logging.getLogger("azure.ai.projects.openai_transport")
openai_logger.setLevel(logging.DEBUG)
openai_logger.propagate = False
openai_logger.addHandler(file_handler)

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model = os.environ["FOUNDRY_MODEL_NAME"]
agent_name = os.environ.get("FOUNDRY_AGENT_NAME") or "MyAgent"
with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential, logging_enable=True) as project_client,
):
    with (
        create_version_with_endpoint(
            project_client=project_client,
            agent_name=agent_name,
            definition=PromptAgentDefinition(
                model=model,
                instructions="You are a helpful assistant.",
            ),
        ),
        project_client.get_openai_client(agent_name=agent_name) as openai_client,
    ):
        conversation = openai_client.conversations.create(
            items=[{"type": "message", "role": "user", "content": "How many feet are in a mile?"}],
        )
        print(f"Conversation created (id: {conversation.id})")

        response = openai_client.responses.create(conversation=conversation.id)
        print(f"Response output: {response.output_text}")

        openai_client.conversations.delete(conversation_id=conversation.id)
        print("Conversation deleted")
        print(f"Azure-core and OpenAI transport logs written to {LOG_FILE}")
