import asyncio
import os

from dotenv import load_dotenv

load_dotenv()

from agent_framework import Agent, BaseChatClient, Workflow, WorkflowBuilder
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential

from azure.ai.agentserver.agentframework import from_agent_framework


def create_writer_agent(client: BaseChatClient) -> Agent:
    return Agent(
        client=client,
        name="Writer",
        instructions=(
            "You are an excellent content writer. You create new content and edit contents based on the feedback."
        ),
    )


def create_reviewer_agent(client: BaseChatClient) -> Agent:
    return Agent(
        client=client,
        name="Reviewer",
        instructions=(
            "You are an excellent content reviewer. "
            "Provide actionable feedback to the writer about the provided content. "
            "Provide the feedback in the most concise manner possible."
        ),
    )


def create_workflow(client: BaseChatClient) -> Workflow:
    writer = create_writer_agent(client)
    reviewer = create_reviewer_agent(client)
    return WorkflowBuilder(start_executor=writer).add_edge(writer, reviewer).build()


async def main() -> None:
    client = AzureOpenAIChatClient(credential=AzureCliCredential())
    await from_agent_framework(lambda: create_workflow(client)).run_async()


if __name__ == "__main__":
    asyncio.run(main())
