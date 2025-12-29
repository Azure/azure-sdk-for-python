# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with an event handler
    and Model Context Protocol (MCP) Tool from the Azure Agents service using
    an asynchronous client.

    To learn more about Model Context Protocol, visit https://modelcontextprotocol.io/

USAGE:
    python sample_agents_stream_eventhandler_with_mcp_async.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-agents azure-identity aiohttp

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) MCP_SERVER_URL - The URL of your MCP server endpoint.
    4) MCP_SERVER_LABEL - A label for your MCP server.
"""
import asyncio
from typing import Any

import os
from azure.ai.projects.aio import AIProjectClient
from azure.ai.agents.aio import AgentsClient
from azure.ai.agents.models import (
    AsyncAgentEventHandler,
    ListSortOrder,
    MessageTextContent,
    MessageDeltaChunk,
    McpTool,
    RequiredMcpToolCall,
    RunStep,
    SubmitToolApprovalAction,
    ThreadMessage,
    ThreadRun,
    ToolApproval,
)
from azure.identity.aio import DefaultAzureCredential
from utils.user_async_functions import user_async_functions

# Get MCP server configuration from environment variables
mcp_server_url = os.environ.get("MCP_SERVER_URL", "https://gitmcp.io/Azure/azure-rest-api-specs")
mcp_server_label = os.environ.get("MCP_SERVER_LABEL", "github")

# Initialize agent MCP tool
mcp_tool = McpTool(
    server_label=mcp_server_label,
    server_url=mcp_server_url,
    allowed_tools=[],  # Optional: specify allowed tools
)


class MyEventHandler(AsyncAgentEventHandler[str]):

    def __init__(self, agents_client: AgentsClient) -> None:
        super().__init__()
        self.agents_client = agents_client

    async def on_message_delta(self, delta: "MessageDeltaChunk") -> None:
        print(f"Text delta received: {delta.text}")

    async def on_thread_message(self, message: "ThreadMessage") -> None:
        print(f"ThreadMessage created. ID: {message.id}, Status: {message.status}")

    async def on_thread_run(self, run: "ThreadRun") -> None:
        print(f"ThreadRun status: {run.status}")

        if run.status == "failed":
            print(f"Run failed. Error: {run.last_error}")

        if run.status == "requires_action" and isinstance(run.required_action, SubmitToolApprovalAction):
            tool_calls = run.required_action.submit_tool_approval.tool_calls

            tool_approvals = []
            for tool_call in tool_calls:
                if isinstance(tool_call, RequiredMcpToolCall):
                    try:
                        print(f"Approving tool call: {tool_call}")
                        tool_approvals.append(
                            ToolApproval(
                                tool_call_id=tool_call.id,
                                approve=True,
                                headers=mcp_tool.headers,
                            )
                        )
                    except Exception as e:
                        print(f"Error approving tool_call {tool_call.id}: {e}")

            print(f"tool_approvals: {tool_approvals}")
            if tool_approvals:
                # Once we receive 'requires_action' status, the next event will be DONE.
                # Here we associate our existing event handler to the next stream.
                await self.agents_client.runs.submit_tool_outputs_stream(
                    thread_id=run.thread_id, run_id=run.id, tool_approvals=tool_approvals, event_handler=self
                )

    async def on_run_step(self, step: "RunStep") -> None:
        print(f"RunStep type: {step.type}, Status: {step.status}")

    async def on_error(self, data: str) -> None:
        print(f"An error occurred. Data: {data}")

    async def on_done(self) -> None:
        print("Stream completed.")

    async def on_unhandled_event(self, event_type: str, event_data: Any) -> None:
        print(f"Unhandled Event Type: {event_type}, Data: {event_data}")


async def main() -> None:
    project_client = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )

    async with project_client:
        agents_client = project_client.agents

        # add allowed tools dynamically
        search_api_code = "search_azure_rest_api_code"
        mcp_tool.allow_tool(search_api_code)
        print(f"Allowed tools: {mcp_tool.allowed_tools}")

        agent = await agents_client.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            name="my-agent",
            instructions="You are a helpful agent that can use MCP tools to assist users. Use the available MCP tools to answer questions and perform tasks.",
            tools=mcp_tool.definitions,
        )
        print(f"Created agent, ID: {agent.id}")

        thread = await agents_client.threads.create()
        print(f"Created thread, thread ID {thread.id}")

        message = await agents_client.messages.create(
            thread_id=thread.id, role="user", content="Please summarize the Azure REST API specifications Readme"
        )
        print(f"Created message, message ID {message.id}")

        mcp_tool.update_headers("SuperSecret", "123456")
        # mcp_tool.set_approval_mode("never")  # Uncomment to disable approval requirement

        async with await agents_client.runs.stream(
            thread_id=thread.id,
            agent_id=agent.id,
            tool_resources=mcp_tool.resources,
            event_handler=MyEventHandler(agents_client),
        ) as stream:
            await stream.until_done()

        await agents_client.delete_agent(agent.id)
        print("Deleted agent")

        messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
        async for msg in messages:
            last_part = msg.content[-1]
            if isinstance(last_part, MessageTextContent):
                print(f"{msg.role}: {last_part.text.value}")


if __name__ == "__main__":
    asyncio.run(main())
