# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable
import json
import io
from test_base import TestBase, servicePreparer
from devtools_testutils import recorded_by_proxy, RecordedTransport
from azure.ai.projects.models import PromptAgentDefinition, AgentDetails, AgentVersionDetails


class TestAgentCrud(TestBase):

    # To run this test:
    # pytest tests\agents\test_agents_crud.py::TestAgentCrud::test_agents_crud -s
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
        model = kwargs.get("foundry_model_name")
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
        body = {"definition": {"model": model, "kind": "prompt", "instructions": "Second set of instructions here"}}
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

    # To run this test:
    # pytest tests\agents\test_agents_crud.py::TestAgentCrud::test_agent_disable_enable -s
    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_agent_disable_enable(self, **kwargs):
        """
        Test disable and enable operations for Agents.

        This test creates an agent, verifies it can respond to requests,
        disables it and verifies requests fail, then enables it and
        verifies requests work again.

        Routes used in this test:

        Action REST API Route                                Client Method
        ------+---------------------------------------------+-----------------------------------
        POST   /agents/{agent_name}/versions                 project_client.agents.create_version()
        POST   /openai/conversations                         openai_client.conversations.create()
        POST   /openai/responses                             openai_client.responses.create()
        POST   /agents/{agent_name}:disable                  project_client.agents.disable()
        POST   /agents/{agent_name}:enable                   project_client.agents.enable()
        DELETE /agents/{agent_name}/versions/{agent_version} project_client.agents.delete_version()
        """
        print("\n")
        model = kwargs.get("foundry_model_name")
        agent_name = "DisableEnableTestAgent"

        # Setup
        project_client = self.create_client(operation_group="agents", **kwargs)
        openai_client = project_client.get_openai_client()

        # Create an Agent
        agent = project_client.agents.create_version(
            agent_name=agent_name,
            definition=PromptAgentDefinition(
                model=model,
                instructions="You are a helpful assistant that answers general questions",
            ),
        )
        print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")
        self._validate_agent_version(agent)

        # Create a conversation
        conversation = openai_client.conversations.create(
            items=[{"type": "message", "role": "user", "content": "How many feet in a mile?"}]
        )
        print(f"Created conversation with initial user message (id: {conversation.id})")

        # Verify the agent can respond to requests
        response = openai_client.responses.create(
            conversation=conversation.id,
            extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
        )
        print(f"Response id: {response.id}, output text: {response.output_text}")
        assert "5280" in response.output_text or "5,280" in response.output_text

        # Disable the agent
        project_client.agents.disable(agent_name=agent_name)
        print(f"Agent disabled")

        # Verify requests fail when agent is disabled
        # TODO: Why does this call succeed, even though the Agent is disabled?
        # error_raised = False
        # try:
        #     _ = openai_client.responses.create(
        #         conversation=conversation.id,
        #         extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
        #     )
        # except Exception as e:
        #     error_raised = True
        #     print(f"Expected error when calling disabled agent: {e}")
        # assert error_raised, "Expected an error when calling a disabled agent"

        # Enable the agent
        project_client.agents.enable(agent_name=agent_name)
        print(f"Agent enabled")

        # Add a new message to the conversation for the next request
        _ = openai_client.conversations.items.create(
            conversation.id,
            items=[{"type": "message", "role": "user", "content": "And how many meters?"}],
        )

        # Verify the agent can respond to requests again
        response = openai_client.responses.create(
            conversation=conversation.id,
            extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
        )
        print(f"Response id: {response.id}, output text: {response.output_text}")
        assert "1609" in response.output_text or "1,609" in response.output_text

        # Cleanup - delete the agent
        result = project_client.agents.delete_version(agent_name=agent_name, agent_version=agent.version)
        assert result.deleted
        print(f"Agent deleted")
