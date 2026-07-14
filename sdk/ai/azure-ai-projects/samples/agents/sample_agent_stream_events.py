# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to run basic Prompt Agent operations
    using the synchronous AIProjectClient and OpenAI clients. The response
    is streamed by setting `stream=True` in the `.responses.create` call.

    The OpenAI compatible Responses and Conversation calls in this sample are made using
    the OpenAI client from the `openai` package. See https://platform.openai.com/docs/api-reference
    for more information.

USAGE:
    python sample_agent_stream_events.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
    3) FOUNDRY_AGENT_NAME - Optional. The name of the AI agent. If not set, defaults to "MyAgent".
"""

import os
from dotenv import load_dotenv
from util import create_version_with_endpoint
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ.get("FOUNDRY_AGENT_NAME", "MyAgent")

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    create_version_with_endpoint(
        project_client=project_client,
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=os.environ["FOUNDRY_MODEL_NAME"],
            instructions="You are a helpful assistant that answers general questions",
        ),
    ),
    project_client.get_openai_client(agent_name=agent_name) as openai_client,
):
    conversation = openai_client.conversations.create(
        items=[{"type": "message", "role": "user", "content": "Tell me about the capital city of France"}],
    )
    print(f"Created conversation with initial user message (id: {conversation.id})")

    with openai_client.responses.create(
        conversation=conversation.id,
        stream=True,
    ) as response_stream_events:

        for event in response_stream_events:
            if event.type == "response.created":
                print(f"Stream response created with ID: {event.response.id}\n")
            elif event.type == "response.output_text.delta":
                print(event.delta, end="", flush=True)
            elif event.type == "response.text.done":
                print("\n\nResponse text done. Access final text in 'event.text'")
            elif event.type == "response.completed":
                print("\n\nResponse completed. Access final text in 'event.response.output_text'")

    openai_client.conversations.delete(conversation_id=conversation.id)
    print("Conversation deleted")
