# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_openai_assistants_streaming_tools.py

DESCRIPTION:
    This sample demonstrates how to create an assistant with streaming using the AzureOpenAI client.

USAGE:
    python sample_openai_assistants_streaming_tools.py

    Before running the sample:

    pip install openai azure-identity

"""

import os, time
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI
from openai import AssistantEventHandler
from openai.types.beta.threads import TextDeltaBlock
from azure.ai.projects.models import FunctionTool
from openai.types.beta.threads.required_action_function_tool_call import RequiredActionFunctionToolCall
from user_functions import user_functions


class MyEventHandler(AssistantEventHandler):

    def __init__(self,
                 client : AzureOpenAI,
                 functions: FunctionTool):
        super().__init__()
        self.client = client
        self.functions = functions

    def on_message_delta(self, delta, snapshot) -> None:
        if delta.content:
            for content_block in delta.content:
                if isinstance(content_block, TextDeltaBlock) and content_block.text:
                    print(f"Received text: {content_block.text.value}")

    def on_tool_call_done(self, tool_call) -> None:
        if self.current_run is not None and self.current_run.required_action:
            if self.current_run.required_action.type == "submit_tool_outputs":
                tool_calls = self.current_run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []
                for tool_call in tool_calls:
                    if isinstance(tool_call, RequiredActionFunctionToolCall):
                        try:
                            output = functions.execute(tool_call)
                            tool_outputs.append(
                                {
                                    "tool_call_id": tool_call.id,
                                    "output": output,
                                }
                            )
                        except Exception as e:
                            print(f"Error executing tool_call {tool_call.id}: {e}")

                print(f"Tool outputs: {tool_outputs}")
                if tool_outputs:
                    event_handler = MyEventHandler(client, functions)
                    with client.beta.threads.runs.submit_tool_outputs_stream(
                        thread_id=self.current_run.thread_id, run_id=self.current_run.id, tool_outputs=tool_outputs, event_handler=event_handler
                    ) as stream:
                        stream.until_done()

    def on_exception(self, exception: Exception) -> None:
        print(f"on_exception called, exception: {exception}")


with AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
) as project_client:

    # Explicit type hinting for IntelliSense
    client: AzureOpenAI = project_client.inference.get_azure_openai_client()

    functions = FunctionTool(functions=user_functions)

    with client:
        agent = client.beta.assistants.create(
            model="gpt-4-1106-preview", name="my-assistant", instructions="You are a helpful assistant", tools=functions.definitions
        )
        print(f"Created agent, agent ID: {agent.id}")

        thread = client.beta.threads.create()
        print(f"Created thread, thread ID: {thread.id}")

        message = client.beta.threads.messages.create(thread_id=thread.id, role="user", content="Hello, send an email with the datetime and weather information in New York? Also let me know the details.")
        print(f"Created message, message ID: {message.id}")

        event_handler = MyEventHandler(client, functions)
        with client.beta.threads.runs.stream(
            thread_id=thread.id,
            assistant_id=agent.id,
            event_handler=event_handler,
        ) as stream:
            stream.until_done()
        
        client.beta.assistants.delete(agent.id)
        print("Deleted agent")

        messages = client.beta.threads.messages.list(thread_id=thread.id)
        print(f"Messages: {messages}")