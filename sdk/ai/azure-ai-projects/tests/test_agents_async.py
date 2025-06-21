# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.ai.projects.aio import AIProjectClient
from test_base import TestBase, servicePreparer
from devtools_testutils.aio import recorded_by_proxy_async

# NOTE: This is just a simple test to verify that the agent can be created and deleted using AIProjectClient.
# You can find comprehensive Agent functionally tests here:
# https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-agents/tests


class TestAgentsAsync(TestBase):

    # To run this test, use the following command in the \sdk\ai\azure-ai-projects folder:
    # cls & pytest tests\test_agents_async.py::TestAgentsAsync::test_agents -s
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_agents(self, **kwargs):

        endpoint = kwargs.pop("azure_ai_projects_tests_project_endpoint")
        print("\n=====> Endpoint:", endpoint)

        model_deployment_name = self.test_agents_params["model_deployment_name"]
        agent_name = self.test_agents_params["agent_name"]

        async with AIProjectClient(
            endpoint=endpoint,
            credential=self.get_credential(AIProjectClient, is_async=True),
        ) as project_client:

            print("[test_agents_async] Create agent")
            agent = await project_client.agents.create_agent(
                model=model_deployment_name,
                name=agent_name,
                instructions="You are helpful agent",
            )
            assert agent.id
            assert agent.model == model_deployment_name
            assert agent.name == agent_name

            print("[test_agents_async] Delete agent")
            await project_client.agents.delete_agent(agent.id)
