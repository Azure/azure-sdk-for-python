# Copyright (c) Microsoft. All rights reserved.

import asyncio
from typing import Annotated

from agent_framework import Agent, tool
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

from azure.ai.agentserver.agentframework import from_agent_framework
from azure.ai.agentserver.agentframework.persistence.agent_session_repository import JsonLocalFileAgentSessionRepository

"""
Tool Approvals with Sessions

This sample demonstrates using tool approvals with persisted sessions.
"""

load_dotenv()


@tool(approval_mode="always_require")
def add_to_calendar(
    event_name: Annotated[str, "Name of the event"], date: Annotated[str, "Date of the event"]
) -> str:
    """Add an event to the calendar (requires approval)."""
    print(f">>> EXECUTING: add_to_calendar(event_name='{event_name}', date='{date}')")
    return f"Added '{event_name}' to calendar on {date}"


def build_agent() -> Agent:
    return Agent(
        client=AzureOpenAIChatClient(credential=AzureCliCredential()),
        name="CalendarAgent",
        instructions="You are a helpful calendar assistant.",
        tools=[add_to_calendar],
    )


async def main() -> None:
    agent = build_agent()
    session_repository = JsonLocalFileAgentSessionRepository(storage_path="./session_storage")
    await from_agent_framework(agent, session_repository=session_repository).run_async()


if __name__ == "__main__":
    asyncio.run(main())
