import asyncio
from dotenv import load_dotenv

load_dotenv()

from agent_framework import ChatAgent, WorkflowBuilder
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential

from azure.ai.agentserver.agentframework import from_agent_framework

def create_writer_agent(client: AzureAIAgentClient) -> ChatAgent:
    return client.create_agent(
        name="Writer",
        instructions=(
            "You are an excellent content writer. You create new content and edit contents based on the feedback."
        ),
    )


def create_reviewer_agent(client: AzureAIAgentClient) -> ChatAgent:
    return client.create_agent(
        name="Reviewer",
        instructions=(
            "You are an excellent content reviewer. "
            "Provide actionable feedback to the writer about the provided content. "
            "Provide the feedback in the most concise manner possible."
        ),
    )


async def main() -> None:
    async with AzureCliCredential() as cred, AzureAIAgentClient(credential=cred) as client:
        builder = (
            WorkflowBuilder()
            .register_agent(lambda: create_writer_agent(client), name="writer")
            .register_agent(lambda: create_reviewer_agent(client), name="reviewer", output_response=True)
            .set_start_executor("writer")
            .add_edge("writer", "reviewer")
        )
        
        # Pass the WorkflowBuilder to the adapter and run it
        await from_agent_framework(workflow=builder).run_async()

        # Or create a factory function for the workflow pass the workflow factory to the adapter 
        # def workflow_factory() -> Workflow:
        #     return builder.build()
        # await from_agent_framework(workflow=workflow_factory).run_async()


if __name__ == "__main__":
    asyncio.run(main())
