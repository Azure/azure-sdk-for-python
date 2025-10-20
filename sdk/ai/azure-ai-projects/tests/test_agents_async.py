# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import asyncio
from azure.ai.projects.aio import AIProjectClient
from azure.ai.agents.models import ListSortOrder
from test_base import TestBase, servicePreparer
from devtools_testutils.aio import recorded_by_proxy_async

# NOTE: This is just a simple test to verify that the agent can be created and deleted using AIProjectClient.
# You can find comprehensive Agent functionally tests here:
# https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-agents/tests

class TestAgentsAsync(TestBase):

    # To run this test, use the following command in the \sdk\ai\azure-ai-projects folder:
    # cls & pytest tests\test_agents_async.py::TestAgentsAsync::test_agents_async -s
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_agents_async(self, **kwargs):

        endpoint = kwargs.pop("azure_ai_projects_tests_project_endpoint")
        print("\n=====> Endpoint:", endpoint)

        model_deployment_name = self.test_agents_params["model_deployment_name"]
        agent_name = self.test_agents_params["agent_name"]

        async with AIProjectClient(
            endpoint=endpoint,
            credential=self.get_credential(AIProjectClient, is_async=True),
        ) as project_client:

            agent = await project_client.agents.create_agent(
                model=model_deployment_name,
                name=agent_name,
                instructions="You are helpful agent",
            )
            print(f"[test_agents_async] Created agent, agent ID: {agent.id}")
            assert agent.id
            assert agent.model == model_deployment_name
            assert agent.name == agent_name

            thread = await project_client.agents.threads.create()
            print(f"[test_agents_async] Created thread, thread ID: {thread.id}")

            message = await project_client.agents.messages.create(
                thread_id=thread.id, role="user", content="how many feet are in a mile?"
            )
            print(f"[test_agents_async] Created message, message ID: {message.id}")

            run = await project_client.agents.runs.create(thread_id=thread.id, agent_id=agent.id)

            # Poll the run as long as run status is queued or in progress
            while run.status in ["queued", "in_progress", "requires_action"]:
                # Wait for a second
                await asyncio.sleep(1)
                run = await project_client.agents.runs.get(thread_id=thread.id, run_id=run.id)
                print(f"[test_agents_async] Run status: {run.status}")

            if run.status == "failed":
                print(f"[test_agents_async] Run error: {run.last_error}")
                assert False

            await project_client.agents.delete_agent(agent.id)
            print("[test_agents_async] Deleted agent")

            messages = project_client.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
            last_text: str = ""
            async for msg in messages:
                if msg.text_messages:
                    last_text = msg.text_messages[-1].text.value
                    print(f"[test_agents_async] {msg.role}: {last_text}")

            assert "5280" in last_text or "5,280" in last_text
