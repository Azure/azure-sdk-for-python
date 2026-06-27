# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable
import json
import io
import openai
from test_base import TestBase, servicePreparer
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import RecordedTransport
from azure.ai.projects.models import (
    AgentDetails,
    AgentEndpointConfig,
    AgentVersionDetails,
    FixedRatioVersionSelectionRule,
    PromptAgentDefinition,
    ProtocolConfiguration,
    ResponsesProtocolConfiguration,
    VersionSelector,
)


class TestAgentCrudAsync(TestBase):

    @servicePreparer()
    @recorded_by_proxy_async()
    async def test_agents_crud_async(self, **kwargs):
        """
        Test CRUD operations for Agents.

        This test creates two agents, the first one with two versions, the second one with one version.
        It then gets, lists, and deletes them, validating at each step.
        It uses different ways of creating agents: strongly typed, dictionary, and IO[bytes].
        """
        model = kwargs.get("foundry_model_name")
        assert model is not None
        project_client = self.create_async_client(operation_group="agents", **kwargs)
        first_agent_name = "MyAgent1"
        second_agent_name = "MyAgent2"

        async with project_client:
            # Create an Agent using strongly typed definitions
            agent1_version1: AgentVersionDetails = await project_client.agents.create_version(
                agent_name=first_agent_name,
                definition=PromptAgentDefinition(
                    model=model,
                    instructions="First set of instructions here",
                ),
            )
            self._validate_agent_version(agent1_version1)

            # Create another version of the same Agent, using dictionary definition, with different instructions
            body = {"definition": {"model": model, "kind": "prompt", "instructions": "Second set of instructions here"}}
            agent1_version2: AgentVersionDetails = await project_client.agents.create_version(
                agent_name=first_agent_name, body=body
            )
            self._validate_agent_version(agent1_version2)

            # Create a different Agent using IO[bytes]
            binary_body = json.dumps(body).encode("utf-8")
            agent2_version1: AgentVersionDetails = await project_client.agents.create_version(
                agent_name=second_agent_name, body=io.BytesIO(binary_body)
            )
            self._validate_agent_version(agent2_version1)

            # Retrieve the first Agent
            retrieved_agent: AgentDetails = await project_client.agents.get(agent_name=first_agent_name)
            self._validate_agent(
                retrieved_agent, expected_name=first_agent_name, expected_latest_version=agent1_version2.version
            )

            # Retrieve specific versions of the first Agent
            retrieved_agent_version: AgentVersionDetails = await project_client.agents.get_version(
                agent_name=first_agent_name, agent_version=agent1_version1.version
            )
            self._validate_agent_version(
                retrieved_agent_version, expected_name=first_agent_name, expected_version=agent1_version1.version
            )
            retrieved_agent_version: AgentVersionDetails = await project_client.agents.get_version(
                agent_name=first_agent_name, agent_version=agent1_version2.version
            )
            self._validate_agent_version(
                retrieved_agent_version, expected_name=first_agent_name, expected_version=agent1_version2.version
            )

            # List all versions of the first Agent (three should be at least two, per the above..)
            item_count: int = 0
            async for listed_agent_version in project_client.agents.list_versions(agent_name=first_agent_name):
                item_count += 1
                self._validate_agent_version(listed_agent_version)
            assert item_count >= 2

            # List all Agents
            # TODO: Enable this once https://msdata.visualstudio.com/Vienna/_workitems/edit/4763062 is fixed
            # item_count = 0
            # async for listed_agent in project_client.agents.list():
            #     item_count += 1
            #     self._validate_agent(listed_agent)
            # assert item_count >= 2

            # Update Prompt Agents
            # I don't see a way to do this..

            # Delete Agents
            result = await project_client.agents.delete(agent_name=first_agent_name)
            assert result.deleted
            # result = await project_client.agents.delete_version(agent_name=second_agent_name, agent_version=agent2_version2.version)
            # assert result.deleted
            result = await project_client.agents.delete_version(
                agent_name=second_agent_name, agent_version=agent2_version1.version
            )
            assert result.deleted

    # To run this test:
    # pytest tests\agents\test_agents_crud_async.py::TestAgentCrudAsync::test_agent_disable_enable_async -s
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_agent_disable_enable_async(self, **kwargs):
        """
        Test disable and enable operations for Agents.

        This test creates an agent, verifies it can respond to requests,
        disables it and verifies requests fail, then enables it and
        verifies requests work again.

        Routes used in this test:

        Action REST API Route                                Client Method
        ------+---------------------------------------------+-----------------------------------
        POST   /agents/{agent_name}/versions                 project_client.agents.create_version()
        POST   /openai/responses                             openai_client.responses.create()
        POST   /agents/{agent_name}:disable                  project_client.agents.disable()
        POST   /agents/{agent_name}:enable                   project_client.agents.enable()
        DELETE /agents/{agent_name}/versions/{agent_version} project_client.agents.delete_version()
        """
        print("\n")
        model: str = kwargs["foundry_model_name"]
        agent_name = "DisableEnableTestAgent"

        # Setup
        project_client = self.create_async_client(operation_group="agents", **kwargs)
        # Intentionally use Project Endpoint here for Responses calls (by not giving `agent_name`). Sync tests will use Agent
        # endpoint instead, so we cover both endpoint.
        openai_client = project_client.get_openai_client()

        async with project_client:

            # Delete any existing agent from previous test runs (ignore failures)
            try:
                await project_client.agents.delete(agent_name=agent_name)
            except Exception:
                pass

            # Create an Agent
            agent = await project_client.agents.create_version(
                agent_name=agent_name,
                definition=PromptAgentDefinition(
                    model=model,
                    instructions="You are a helpful assistant that answers general questions",
                ),
            )
            print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")
            self._validate_agent_version(agent)

            # Verify the agent can respond to requests
            response = await openai_client.responses.create(
                input="How many feet in a mile?",
                extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
            )
            print(f"Response id: {response.id}, output text: {response.output_text}")
            assert "5280" in response.output_text or "5,280" in response.output_text

            # Disable the agent
            await project_client.agents.disable(agent_name=agent_name)
            print("Agent disabled")

            # Verify requests fail when agent is disabled
            error_raised = False
            try:
                _ = await openai_client.responses.create(
                    input="How many feet in a mile?",
                    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
                )
            except openai.PermissionDeniedError as e:
                error_raised = True
                print(f"Expected error when calling disabled agent: {e}")
            assert error_raised, "Expected an error when calling a disabled agent"

            # Enable the agent
            await project_client.agents.enable(agent_name=agent_name)
            print("Agent enabled")

            # Verify the agent can respond to requests again
            response = await openai_client.responses.create(
                input="How many meters in a mile?",
                extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
            )
            print(f"Response id: {response.id}, output text: {response.output_text}")
            assert "1609" in response.output_text or "1,609" in response.output_text

            # Cleanup - delete the agent
            result = await project_client.agents.delete_version(agent_name=agent_name, agent_version=agent.version)
            assert result.deleted
            print("Agent deleted")

    # To run this test:
    # pytest tests\agents\test_agents_crud_async.py::TestAgentCrudAsync::test_prompt_agent_endpoint_responses_async -s
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_prompt_agent_endpoint_responses_async(self, **kwargs):
        """
        Test prompt-agent endpoint routing for the Responses protocol.

        This test:
        1. Creates a prompt agent version
        2. Configures the agent endpoint to route 100% of traffic to that version
        3. Invokes the agent endpoint through the OpenAI-compatible responses client
        4. Verifies the response
        5. Cleans up by deleting the agent version

        Routes used in this test:

        Action REST API Route                                Client Method
        ------+---------------------------------------------+-----------------------------------
        POST   /agents/{agent_name}/versions                 project_client.agents.create_version()
        PATCH  /agents/{agent_name}                          project_client.agents.update_details()
        POST   /agents/{agent_name}/endpoint/protocols/openai/conversations  openai_client.conversations.create()
        POST   /agents/{agent_name}/endpoint/protocols/openai/responses  openai_client.responses.create()
        DELETE /agents/{agent_name}/versions/{agent_version} project_client.agents.delete_version()
        """
        print("\n")
        model = kwargs.get("foundry_model_name")
        assert model is not None
        agent_name = "PromptAgentEndpointTestAgent"

        project_client = self.create_async_client(operation_group="agents", allow_preview=True, **kwargs)

        async with project_client:
            agent = await project_client.agents.create_version(
                agent_name=agent_name,
                definition=PromptAgentDefinition(
                    model=model,
                    instructions="You are a helpful assistant that answers general knowledge questions.",
                ),
            )
            self._validate_agent_version(agent)
            print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

            try:
                endpoint_config = AgentEndpointConfig(
                    version_selector=VersionSelector(
                        version_selection_rules=[
                            FixedRatioVersionSelectionRule(agent_version=agent.version, traffic_percentage=100),
                        ]
                    ),
                    protocol_configuration=ProtocolConfiguration(responses=ResponsesProtocolConfiguration()),
                )

                patched_agent = await project_client.agents.update_details(
                    agent_name=agent_name,
                    agent_endpoint=endpoint_config,
                )
                assert patched_agent.agent_endpoint is not None
                print(f"Agent endpoint configured for agent: {patched_agent.name}")

                openai_client = project_client.get_openai_client(agent_name=agent_name)
                conversation = await openai_client.conversations.create(
                    items=[
                        {
                            "type": "message",
                            "role": "user",
                            "content": "What is 2 + 2? Answer with just the number.",
                        }
                    ]
                )
                response = await openai_client.responses.create(
                    conversation=conversation.id,
                    input="and then add 2 again",
                )

                print(f"Response id: {response.id}, output text: {response.output_text}")
                assert response.output_text
                assert "6" in response.output_text.strip()
            finally:
                result = await project_client.agents.delete_version(agent_name=agent_name, agent_version=agent.version)
                assert result.deleted
                print("Agent deleted")
