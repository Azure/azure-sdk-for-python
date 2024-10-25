# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_openai_assistants_streaming.py

DESCRIPTION:
    This sample demonstrates how to create an assistant with streaming using the AzureOpenAI client.

USAGE:
    python sample_openai_assistants_streaming.py

    Before running the sample:

    pip install openai azure-identity

"""

import os, time
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI
from openai import AssistantEventHandler
from openai.types.beta.threads import TextDeltaBlock


class MyEventHandler(AssistantEventHandler):

    def on_message_delta(self, delta, snapshot) -> None:
        if delta.content:
            for content_block in delta.content:
                if isinstance(content_block, TextDeltaBlock) and content_block.text:
                    print(f"Received text: {content_block.text.value}")

    def on_exception(self, exception: Exception) -> None:
        print(f"on_exception called, exception: {exception}")


with AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
) as project_client:

    # Explicit type hinting for IntelliSense
    client: AzureOpenAI = project_client.inference.get_azure_openai_client()

    with client:
        agent = client.beta.assistants.create(
            model="gpt-4-1106-preview", name="my-assistant", instructions="You are a helpful assistant"
        )
        print(f"Created agent, agent ID: {agent.id}")

        thread = client.beta.threads.create()
        print(f"Created thread, thread ID: {thread.id}")

        message = client.beta.threads.messages.create(thread_id=thread.id, role="user", content="Hello, tell me a joke")
        print(f"Created message, message ID: {message.id}")

        with client.beta.threads.runs.stream(
            thread_id=thread.id,
            assistant_id=agent.id,
            event_handler=MyEventHandler(),
        ) as stream:
            stream.until_done()
        
        client.beta.assistants.delete(agent.id)
        print("Deleted agent")

        messages = client.beta.threads.messages.list(thread_id=thread.id)
        print(f"Messages: {messages}")
