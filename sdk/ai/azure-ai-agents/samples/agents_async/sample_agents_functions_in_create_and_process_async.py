# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use Agent operations with a mix of automatic and manual
    function calls from the Azure Agents service using an asynchronous client.

    Some functions (like fetch_current_datetime and fetch_weather) will be executed automatically,
    while others (like send_email) will require manual approval through the RunHandler.

USAGE:
    python sample_agents_functions_in_create_and_process_async.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-agents azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""
import os, sys, json, asyncio
from typing import Any
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential
from azure.ai.agents.models import (
    AsyncFunctionTool,
    ListSortOrder,
    RequiredFunctionToolCall,
    AsyncRunHandler,
    ThreadRun,
    AsyncToolSet,
    RequiredFunctionToolCallDetails,
)

from utils.user_async_functions import (
    fetch_current_datetime_async,
    fetch_weather,
    send_email_async,
)
from utils.user_async_functions import user_async_functions


async def main():
    project_client = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )

    # Create a toolset with all functions
    all_functions_tool = AsyncFunctionTool(user_async_functions)
    toolset = AsyncToolSet()
    toolset.add(all_functions_tool)

    # Declare a run handler to execute function tool call manually
    class MyRunHandler(AsyncRunHandler):
        async def submit_function_call_output(
            self,
            *,
            run: ThreadRun,
            tool_call: RequiredFunctionToolCall,
            tool_call_details: RequiredFunctionToolCallDetails,
            **kwargs: Any,
        ) -> Any:
            function_name = tool_call_details.name
            if function_name == send_email_async.__name__:
                # Parse arguments from tool call
                args_dict = json.loads(tool_call_details.arguments) if tool_call_details.arguments else {}
                # Call the function directly with the arguments
                return await send_email_async(**args_dict)

    async with project_client:
        agents_client = project_client.agents

        # Enable auto function calling for the subset of safe functions
        auto_functions = {
            fetch_current_datetime_async,
            fetch_weather,
        }
        agents_client.enable_auto_function_calls(auto_functions)

        # Create an Agent with all function tools available
        agent = await agents_client.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            name="my-agent",
            instructions="You are a helpful Agent",
            toolset=toolset,
        )
        print(f"Created Agent, ID: {agent.id}")

        thread = await agents_client.threads.create()
        print(f"Created thread, ID: {thread.id}")

        message = await agents_client.messages.create(
            thread_id=thread.id,
            role="user",
            content="Hello, send an email with the datetime and weather information in New York?",
        )
        print(f"Created message, ID: {message.id}")

        run = await agents_client.runs.create_and_process(
            thread_id=thread.id, agent_id=agent.id, run_handler=MyRunHandler()
        )

        print(f"Run completed with status: {run.status}")

        # Delete the Agent when done
        await agents_client.delete_agent(agent.id)
        print("Deleted Agent")

        # Fetch and log all messages
        messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
        async for msg in messages:
            if msg.text_messages:
                last_text = msg.text_messages[-1]
                print(f"{msg.role}: {last_text.text.value}")


if __name__ == "__main__":
    asyncio.run(main())
