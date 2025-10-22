# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import time
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import ListSortOrder
from test_base import TestBase, servicePreparer
from devtools_testutils import recorded_by_proxy

# NOTE: This is just a simple test to verify that the agent can be created and deleted using AIProjectClient.
# You can find comprehensive Agent functionally tests here:
# https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-agents/tests

class TestAgents(TestBase):

    # To run this test, use the following command in the \sdk\ai\azure-ai-projects folder:
    # cls & pytest tests\test_agents.py::TestAgents::test_agents -s
    @servicePreparer()
    @recorded_by_proxy
    def test_agents(self, **kwargs):

        endpoint = kwargs.pop("azure_ai_projects_tests_project_endpoint")
        print("\n=====> Endpoint:", endpoint)

        model_deployment_name = self.test_agents_params["model_deployment_name"]
        agent_name = self.test_agents_params["agent_name"]

        with AIProjectClient(
            endpoint=endpoint,
            credential=self.get_credential(AIProjectClient, is_async=False),
        ) as project_client:

            agent = project_client.agents.create_agent(
                model=model_deployment_name,
                name=agent_name,
                instructions="You are helpful agent",
            )
            print(f"[test_agents] Created agent, agent ID: {agent.id}")
            assert agent.id
            assert agent.model == model_deployment_name
            assert agent.name == agent_name

            thread = project_client.agents.threads.create()
            print(f"[test_agents] Created thread, thread ID: {thread.id}")

            message = project_client.agents.messages.create(
                thread_id=thread.id, role="user", content="how many feet are in a mile?"
            )
            print(f"[test_agents] Created message, message ID: {message.id}")

            run = project_client.agents.runs.create(thread_id=thread.id, agent_id=agent.id)

            # Poll the run as long as run status is queued or in progress
            while run.status in ["queued", "in_progress", "requires_action"]:
                # Wait for a second
                time.sleep(1)
                run = project_client.agents.runs.get(thread_id=thread.id, run_id=run.id)
                print(f"[test_agents] Run status: {run.status}")

            if run.status == "failed":
                print(f"[test_agents] Run error: {run.last_error}")
                assert False

            project_client.agents.delete_agent(agent.id)
            print("[test_agents] Deleted agent")

            messages = project_client.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
            last_text: str = ""
            for msg in messages:
                if msg.text_messages:
                    last_text = msg.text_messages[-1].text.value
                    print(f"[test_agents] {msg.role}: {last_text}")

            assert "5280" in last_text or "5,280" in last_text
