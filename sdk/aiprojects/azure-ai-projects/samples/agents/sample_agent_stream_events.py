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

    pip install "azure-ai-projects>=2.0.0b1" python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):

    agent = project_client.agents.create_version(
        agent_name="MyAgent",
        definition=PromptAgentDefinition(
            model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
            instructions="You are a helpful assistant that answers general questions",
        ),
    )
    print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

    conversation = openai_client.conversations.create(
        items=[{"type": "message", "role": "user", "content": "Tell me about the capital city of France"}],
    )
    print(f"Created conversation with initial user message (id: {conversation.id})")

    with openai_client.responses.create(
        conversation=conversation.id,
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        input="",
        stream=True,
    ) as response_stream_events:

        for event in response_stream_events:
            if event.type == "response.created":
                print(f"Stream response created with ID: {event.response.id}\n")
            elif event.type == "response.output_text.delta":
                print(event.delta, end="", flush=True)
            elif event.type == "response.text.done":
                print(f"\n\nResponse text done. Access final text in 'event.text'")
            elif event.type == "response.completed":
                print(f"\n\nResponse completed. Access final text in 'event.response.output_text'")

    openai_client.conversations.delete(conversation_id=conversation.id)
    print("Conversation deleted")

    project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
    print("Agent deleted")
