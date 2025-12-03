# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable
import json
import io
from test_base import TestBase, servicePreparer
from devtools_testutils import recorded_by_proxy
from azure.ai.projects.models import PromptAgentDefinition, AgentDetails, AgentVersionDetails


class TestAgentCrud(TestBase):

    @servicePreparer()
    @recorded_by_proxy()
    def test_agents_crud(self, **kwargs):
        """
        Test CRUD operations for Agents.

        This test creates two agents, the first one with two versions, the second one with one version.
        It then gets, lists, and deletes them, validating at each step.
        It uses different ways of creating agents: strongly typed, dictionary, and IO[bytes].

        Routes used in this test:

        Action REST API Route                                Client Method
        ------+---------------------------------------------+-----------------------------------
        GET    /agents/{agent_name}                          project_client.agents.get()
        POST   /agents/{agent_name}/versions                 project_client.agents.create_version()
        GET    /agents/{agent_name}/versions                 project_client.agents.list_versions()
        GET    /agents                                       project_client.agents.list()
        DELETE /agents/{agent_name}                          project_client.agents.delete()
        DELETE /agents/{agent_name}/versions/{agent_version} project_client.agents.delete_version()
        GET    /agents/{agent_name}/versions/{agent_version} project_client.agents.get_version()
        """
        print("\n")
        model = self.test_agents_params["model_deployment_name"]
        project_client = self.create_client(operation_group="agents", **kwargs)
        first_agent_name = "MyAgent1"
        second_agent_name = "MyAgent2"

        # Create an Agent using strongly typed definitions
        agent1_version1: AgentVersionDetails = project_client.agents.create_version(
            agent_name=first_agent_name,
            definition=PromptAgentDefinition(
                model=model,
                instructions="First set of instructions here",
            ),
        )
        self._validate_agent_version(agent1_version1)

        # Create another version of the same Agent, using dictionary definition, with different instructions
        body = {"definition": {"model": "gpt-4o", "kind": "prompt", "instructions": "Second set of instructions here"}}
        agent1_version2: AgentVersionDetails = project_client.agents.create_version(
            agent_name=first_agent_name, body=body
        )
        self._validate_agent_version(agent1_version2)

        # Create a different Agent using IO[bytes]
        binary_body = json.dumps(body).encode("utf-8")
        agent2_version1: AgentVersionDetails = project_client.agents.create_version(
            agent_name=second_agent_name, body=io.BytesIO(binary_body)
        )
        self._validate_agent_version(agent2_version1)

        # Create another version of the same Agent, by updating the existing one
        # TODO: Uncomment the lines below, and the delete lines at the end, once the service is fixed (at the moment returns 500 InternalServiceError)
        # agent2_version2: AgentVersionDetails = project_client.agents.update(
        #     agent_name=second_agent_name,
        #     definition=PromptAgentDefinition(
        #         model=model,
        #         instructions="Third set of instructions here",
        #     ),
        # )
        # self._validate_agent_version(agent2_version2)

        # Get the first Agent
        retrieved_agent: AgentDetails = project_client.agents.get(agent_name=first_agent_name)
        self._validate_agent(
            retrieved_agent, expected_name=first_agent_name, expected_latest_version=agent1_version2.version
        )

        # Retrieve specific versions of the first Agent
        retrieved_agent_version: AgentVersionDetails = project_client.agents.get_version(
            agent_name=first_agent_name, agent_version=agent1_version1.version
        )
        self._validate_agent_version(
            retrieved_agent_version, expected_name=first_agent_name, expected_version=agent1_version1.version
        )
        retrieved_agent_version: AgentVersionDetails = project_client.agents.get_version(
            agent_name=first_agent_name, agent_version=agent1_version2.version
        )
        self._validate_agent_version(
            retrieved_agent_version, expected_name=first_agent_name, expected_version=agent1_version2.version
        )

        # List all versions of the first Agent (three should be at least two, per the above..)
        item_count: int = 0
        for listed_agent_version in project_client.agents.list_versions(agent_name=first_agent_name):
            item_count += 1
            self._validate_agent_version(listed_agent_version)
        assert item_count >= 2

        # List all Agents
        # TODO: Enable this once https://msdata.visualstudio.com/Vienna/_workitems/edit/4763062 is fixed
        # item_count = 0
        # for listed_agent in project_client.agents.list(limit=100):
        #     item_count += 1
        #     self._validate_agent(listed_agent)
        # assert item_count >= 2

        # Delete Agents
        result = project_client.agents.delete(agent_name=first_agent_name)
        assert result.deleted
        # result = project_client.agents.delete_version(agent_name=second_agent_name, agent_version=agent2_version2.version)
        # assert result.deleted
        result = project_client.agents.delete_version(
            agent_name=second_agent_name, agent_version=agent2_version1.version
        )
        assert result.deleted
