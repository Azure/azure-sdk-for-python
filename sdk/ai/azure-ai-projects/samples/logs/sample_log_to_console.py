# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to capture both Azure-core HTTP logs and
    OpenAI transport logs into a single file while running a Prompt Agent operation.
    With logging_enable=False, the transport still logs request and response metadata,
    but excludes request bodies and response bodies while keeping sensitive headers redacted.

USAGE:
    python samples/logs/sample_log_to_console.py

    Before running the sample:

    pip install "azure-ai-projects>=2.5.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model.
    3) FOUNDRY_AGENT_NAME - Optional. Defaults to "MyAgent".

    This sample writes Azure-core and OpenAI transport logs to the console.
"""

import os

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

from util import create_version_with_endpoint

load_dotenv()

os.environ["AZURE_AI_PROJECTS_CONSOLE_LOGGING"] = "true"

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model = os.environ["FOUNDRY_MODEL_NAME"]
agent_name = os.environ.get("FOUNDRY_AGENT_NAME") or "MyAgent"
with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential, logging_enable=False) as project_client,
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
