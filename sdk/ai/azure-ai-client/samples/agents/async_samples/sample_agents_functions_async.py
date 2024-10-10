# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import logging
import time

from azure.ai.client.aio import AzureAIClient
from azure.ai.client.models import AsyncFunctionTool
from azure.identity import DefaultAzureCredential

import os

from user_async_functions import user_async_functions

# Create an Azure AI Client from a connection string, copied from your AI Studio project.
# At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
# Customer needs to login to Azure subscription via Azure CLI and set the environment variables

connection_string = os.environ["AI_CLIENT_CONNECTION_STRING"]

ai_client = AzureAIClient.from_connection_string(
    credential=DefaultAzureCredential(),
    connection=connection_string,
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

async def main():
    async with ai_client:
        # Initialize assistant functions
        functions = AsyncFunctionTool(functions=user_async_functions)

        # Create agent
        agent = await ai_client.agents.create_agent(
            model="gpt-4-1106-preview", name="my-assistant", instructions="You are helpful assistant", tools=functions.definitions
        )
        logging.info(f"Created agent, agent ID: {agent.id}")
        logging.info("Created assistant client")

        # Create thread for communication
        thread = await ai_client.agents.create_thread()
        logging.info(f"Created thread, ID: {thread.id}")

        # Create and send message
        message = await ai_client.agents.create_message(thread_id=thread.id, role="user", content="Hello, what's the time?")
        logging.info(f"Created message, ID: {message.id}")

        # Create and run assistant task
        run = await ai_client.agents.create_run(thread_id=thread.id, assistant_id=agent.id)
        logging.info(f"Created run, ID: {run.id}")

        # Polling loop for run status
        while run.status in ["queued", "in_progress", "requires_action"]:
            time.sleep(4)
            run = await ai_client.agents.get_run(thread_id=thread.id, run_id=run.id)

            if run.status == "requires_action" and run.required_action.submit_tool_outputs:
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                if not tool_calls:
                    logging.warning("No tool calls provided - cancelling run")
                    await ai_client.agents.cancel_run(thread_id=thread.id, run_id=run.id)
                    break

                tool_outputs = []
                for tool_call in tool_calls:
                    output = await functions.execute(tool_call)
                    tool_output = {
                            "tool_call_id": tool_call.id,
                            "output": output,
                        }
                    tool_outputs.append(tool_output)

                logging.info(f"Tool outputs: {tool_outputs}")
                if tool_outputs:
                    await ai_client.agents.submit_tool_outputs_to_run(
                        thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs
                    )

            logging.info(f"Current run status: {run.status}")

        logging.info(f"Run completed with status: {run.status}")

        # Delete the assistant when done
        await ai_client.agents.delete_agent(agent.id)
        logging.info("Deleted assistant")

        # Fetch and log all messages
        messages = await ai_client.agents.list_messages(thread_id=thread.id)
        logging.info(f"Messages: {messages}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main());