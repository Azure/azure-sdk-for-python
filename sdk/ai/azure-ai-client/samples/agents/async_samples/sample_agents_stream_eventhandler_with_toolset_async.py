# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_agents_stream_eventhandler_with_toolset_async.py

DESCRIPTION:
    This sample demonstrates how to use agent operations with an event handler and toolset from
    the Azure Agents service using a asynchronous client.

USAGE:
    python sample_agents_stream_eventhandler_with_toolset_async.py

    Before running the sample:

    pip install azure.ai.client azure-identity

    Set this environment variables with your own values:
    AI_CLIENT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""
import asyncio
from typing import Any

from azure.ai.client.aio import AzureAIClient
from azure.ai.client.models import MessageDeltaChunk, MessageDeltaTextContent, RunStep, SubmitToolOutputsAction, ThreadMessage, ThreadRun
from azure.ai.client.models import AsyncAgentEventHandler, AsyncFunctionTool, AsyncToolSet
from azure.ai.client.aio.operations import AgentsOperations
from azure.identity import DefaultAzureCredential

import os

from user_async_functions import user_async_functions


class MyEventHandler(AsyncAgentEventHandler):

    def __init__(self, agents: AgentsOperations) -> None:
        self._agents = agents

    async def on_message_delta(self, delta: "MessageDeltaChunk") -> None:
        for content_part in delta.delta.content:
            if isinstance(content_part, MessageDeltaTextContent):
                text_value = content_part.text.value if content_part.text else "No text"
                print(f"Text delta received: {text_value}")

    async def on_thread_message(self, message: "ThreadMessage") -> None:
        print(f"ThreadMessage created. ID: {message.id}, Status: {message.status}")

    async def on_thread_run(self, run: "ThreadRun") -> None:
        print(f"ThreadRun status: {run.status}")

        if run.status == "failed":
            print(f"Run failed. Error: {run.last_error}")

        if run.status == "requires_action" and isinstance(run.required_action, SubmitToolOutputsAction):
            await self._handle_submit_tool_outputs(run)

    async def on_run_step(self, step: "RunStep") -> None:
        print(f"RunStep type: {step.type}, Status: {step.status}")

    async def on_error(self, data: str) -> None:
        print(f"An error occurred. Data: {data}")

    async def on_done(self) -> None:
        print("Stream completed.")

    async def on_unhandled_event(self, event_type: str, event_data: Any) -> None:
        print(f"Unhandled Event Type: {event_type}, Data: {event_data}")

    async def _handle_submit_tool_outputs(self, run: "ThreadRun") -> None:
        if isinstance(run.required_action, SubmitToolOutputsAction):
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            if not tool_calls:
                print("No tool calls to execute.")
                return
            if not self._agents:
                print("AssistantClient not set. Cannot execute tool calls using toolset.")
                return

            toolset = self._agents.get_toolset()
            if toolset:
                tool_outputs = await toolset.execute_tool_calls(tool_calls)
            else:
                raise ValueError("Toolset is not available in the client.")
            
            print(f"Tool outputs: {tool_outputs}")
            if tool_outputs:
                async with await self._agents.submit_tool_outputs_to_stream(
                    thread_id=run.thread_id, 
                    run_id=run.id, 
                    tool_outputs=tool_outputs, 
                    event_handler=self
            ) as stream:
                    await stream.until_done()


async def main():
    # Create an Azure AI Client from a connection string, copied from your AI Studio project.
    # At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
    # Customer needs to login to Azure subscription via Azure CLI and set the environment variables

    ai_client = AzureAIClient.from_connection_string(
        credential=DefaultAzureCredential(),
        conn_str=os.environ["AI_CLIENT_CONNECTION_STRING"]
    )

    # Or, you can create the Azure AI Client by giving all required parameters directly
    """
    ai_client = AzureAIClient(
        credential=DefaultAzureCredential(),
        host_name=os.environ["AI_CLIENT_HOST_NAME"],
        subscription_id=os.environ["AI_CLIENT_SUBSCRIPTION_ID"],
        resource_group_name=os.environ["AI_CLIENT_RESOURCE_GROUP_NAME"],
        workspace_name=os.environ["AI_CLIENT_WORKSPACE_NAME"],
        logging_enable=True, # Optional. Remove this line if you don't want to show how to enable logging
    )
    """        

    # Initialize toolset with user functions
    functions = AsyncFunctionTool(user_async_functions)
    toolset = AsyncToolSet()
    toolset.add(functions)
    
    async with ai_client:        
        
        agent = await ai_client.agents.create_agent(
            model="gpt-4-1106-preview", name="my-assistant", instructions="You are helpful assistant", toolset=toolset
        )
        print(f"Created agent, agent ID: {agent.id}")


        thread = await ai_client.agents.create_thread()
        print(f"Created thread, thread ID {thread.id}")

        message = await ai_client.agents.create_message(thread_id=thread.id, role="user", content="Hello, send an email with the datetime and weather information in New York? Also let me know the details")
        print(f"Created message, message ID {message.id}")

        async with await ai_client.agents.create_stream(
            thread_id=thread.id, 
            assistant_id=agent.id,
            event_handler=MyEventHandler(ai_client.agents)
        ) as stream:
            await stream.until_done()

        await ai_client.agents.delete_agent(agent.id)
        print("Deleted assistant")

        messages = await ai_client.agents.list_messages(thread_id=thread.id)
        print(f"Messages: {messages}")


if __name__ == "__main__":
    asyncio.run(main())
