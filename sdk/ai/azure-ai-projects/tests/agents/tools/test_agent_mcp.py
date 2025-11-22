# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

import pytest
from test_base import TestBase, servicePreparer
from devtools_testutils import is_live_and_not_recording
from azure.ai.projects.models import PromptAgentDefinition, MCPTool, Tool
from openai.types.responses.response_input_param import McpApprovalResponse, ResponseInputParam


class TestAgentMCP(TestBase):

    @servicePreparer()
    @pytest.mark.skipif(
        condition=(not is_live_and_not_recording()),
        reason="Skipped because we cannot record network calls with OpenAI client",
    )
    def test_agent_mcp_basic(self, **kwargs):
        """
        Test agent with MCP (Model Context Protocol) tool for external API access.

        This test verifies that an agent can:
        1. Use an MCP tool to access external resources (GitHub repo)
        2. Request approval for MCP operations
        3. Process approval responses
        4. Complete the task using the MCP tool

        The test uses a public GitHub MCP server that provides access to
        Azure REST API specifications.

        Routes used in this test:

        Action REST API Route                                Client Method
        ------+---------------------------------------------+-----------------------------------
        # Setup:
        POST   /agents/{agent_name}/versions                 project_client.agents.create_version()
        POST   /openai/conversations                         openai_client.conversations.create()

        # Test focus:
        POST   /openai/responses                             openai_client.responses.create() (with MCP tool)
        POST   /openai/responses                             openai_client.responses.create() (with approval)

        # Teardown:
        DELETE /agents/{agent_name}/versions/{agent_version} project_client.agents.delete_version()
        """

        model = self.test_agents_params["model_deployment_name"]

        with (
            self.create_client(operation_group="agents", **kwargs) as project_client,
            project_client.get_openai_client() as openai_client,
        ):
            # Create MCP tool that connects to a public GitHub repo via MCP server
            mcp_tool = MCPTool(
                server_label="api-specs",
                server_url="https://gitmcp.io/Azure/azure-rest-api-specs",
                require_approval="always",
            )

            tools: list[Tool] = [mcp_tool]

            # Create agent with MCP tool
            agent = project_client.agents.create_version(
                agent_name="mcp-basic-agent",
                definition=PromptAgentDefinition(
                    model=model,
                    instructions="You are a helpful agent that can use MCP tools to assist users. Use the available MCP tools to answer questions and perform tasks.",
                    tools=tools,
                ),
                description="Agent for testing basic MCP functionality.",
            )
            print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")
            assert agent.id is not None
            assert agent.name == "mcp-basic-agent"
            assert agent.version is not None

            # Create conversation
            conversation = openai_client.conversations.create()
            print(f"Created conversation (id: {conversation.id})")
            assert conversation.id is not None

            # Send initial request that will trigger the MCP tool
            print("\nAsking agent to summarize Azure REST API specs README...")

            response = openai_client.responses.create(
                conversation=conversation.id,
                input="Please summarize the Azure REST API specifications Readme",
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            print(f"Initial response completed (id: {response.id})")
            assert response.id is not None
            assert response.output is not None
            assert len(response.output) > 0

            # Process any MCP approval requests
            approval_requests_found = 0
            input_list: ResponseInputParam = []

            for item in response.output:
                if item.type == "mcp_approval_request":
                    approval_requests_found += 1
                    print(f"Found MCP approval request (id: {item.id}, server: {item.server_label})")

                    if item.server_label == "api-specs" and item.id:
                        # Approve the MCP request
                        input_list.append(
                            McpApprovalResponse(
                                type="mcp_approval_response",
                                approve=True,
                                approval_request_id=item.id,
                            )
                        )
                        print(f"✓ Approved MCP request: {item.id}")

            # Verify that at least one approval request was generated
            assert (
                approval_requests_found > 0
            ), f"Expected at least 1 MCP approval request, but found {approval_requests_found}"

            print(f"\n✓ Processed {approval_requests_found} MCP approval request(s)")

            # Send the approval response to continue the agent's work
            print("\nSending approval response to continue agent execution...")

            response = openai_client.responses.create(
                input=input_list,
                previous_response_id=response.id,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            print(f"Final response completed (id: {response.id})")
            assert response.id is not None

            # Get the final response text
            response_text = response.output_text
            print(f"\nAgent's response preview: {response_text[:200]}...")

            # Verify we got a meaningful response
            assert len(response_text) > 100, "Expected a substantial response from the agent"

            # Check that the response mentions Azure or REST API (indicating it accessed the repo)
            assert any(
                keyword in response_text.lower() for keyword in ["azure", "rest", "api", "specification"]
            ), f"Expected response to mention Azure/REST API, but got: {response_text[:200]}"

            print("\n✓ Agent successfully used MCP tool to access GitHub repo and complete task")

            # Teardown
            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("Agent deleted")

    @servicePreparer()
    @pytest.mark.skipif(
        condition=(not is_live_and_not_recording()),
        reason="Skipped because we cannot record network calls with OpenAI client",
    )
    def test_agent_mcp_with_project_connection(self, **kwargs):
        """
        Test agent with MCP tool using a project connection for authentication.

        This test verifies that an agent can:
        1. Use an MCP tool with a project connection (GitHub PAT)
        2. Access authenticated GitHub API endpoints
        3. Request and process approval for MCP operations
        4. Return personal GitHub profile information

        Routes used in this test:

        Action REST API Route                                Client Method
        ------+---------------------------------------------+-----------------------------------
        # Setup:
        POST   /agents/{agent_name}/versions                 project_client.agents.create_version()
        POST   /openai/conversations                         openai_client.conversations.create()

        # Test focus:
        POST   /openai/responses                             openai_client.responses.create() (with MCP + connection)
        POST   /openai/responses                             openai_client.responses.create() (with approval)

        # Teardown:
        DELETE /agents/{agent_name}/versions/{agent_version} project_client.agents.delete_version()
        """

        model = self.test_agents_params["model_deployment_name"]

        with (
            self.create_client(operation_group="agents", **kwargs) as project_client,
            project_client.get_openai_client() as openai_client,
        ):
            # Get MCP project connection from environment
            mcp_project_connection_id = kwargs.get("azure_ai_projects_tests_mcp_project_connection_id")

            if not mcp_project_connection_id:
                pytest.skip("AZURE_AI_PROJECTS_TESTS_MCP_PROJECT_CONNECTION_ID environment variable not set")

            assert isinstance(mcp_project_connection_id, str), "mcp_project_connection_id must be a string"
            print(f"Using MCP project connection: {mcp_project_connection_id}")

            # Create MCP tool with project connection for GitHub API access
            mcp_tool = MCPTool(
                server_label="github-api",
                server_url="https://api.githubcopilot.com/mcp",
                require_approval="always",
                project_connection_id=mcp_project_connection_id,
            )

            tools: list[Tool] = [mcp_tool]

            # Create agent with MCP tool
            agent = project_client.agents.create_version(
                agent_name="mcp-connection-agent",
                definition=PromptAgentDefinition(
                    model=model,
                    instructions="Use MCP tools as needed to access GitHub information.",
                    tools=tools,
                ),
                description="Agent for testing MCP with project connection.",
            )
            print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")
            assert agent.id is not None
            assert agent.name == "mcp-connection-agent"
            assert agent.version is not None

            # Create conversation
            conversation = openai_client.conversations.create()
            print(f"Created conversation (id: {conversation.id})")
            assert conversation.id is not None

            # Send initial request that will trigger the MCP tool with authentication
            print("\nAsking agent to get GitHub profile username...")

            response = openai_client.responses.create(
                conversation=conversation.id,
                input="What is my username in Github profile?",
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            print(f"Initial response completed (id: {response.id})")
            assert response.id is not None
            assert response.output is not None
            assert len(response.output) > 0

            # Process any MCP approval requests
            approval_requests_found = 0
            input_list: ResponseInputParam = []

            for item in response.output:
                if item.type == "mcp_approval_request":
                    approval_requests_found += 1
                    print(f"Found MCP approval request (id: {item.id}, server: {item.server_label})")

                    if item.server_label == "github-api" and item.id:
                        # Approve the MCP request
                        input_list.append(
                            McpApprovalResponse(
                                type="mcp_approval_response",
                                approve=True,
                                approval_request_id=item.id,
                            )
                        )
                        print(f"✓ Approved MCP request: {item.id}")

            # Verify that at least one approval request was generated
            assert (
                approval_requests_found > 0
            ), f"Expected at least 1 MCP approval request, but found {approval_requests_found}"

            print(f"\n✓ Processed {approval_requests_found} MCP approval request(s)")

            # Send the approval response to continue the agent's work
            print("\nSending approval response to continue agent execution...")

            response = openai_client.responses.create(
                input=input_list,
                previous_response_id=response.id,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            print(f"Final response completed (id: {response.id})")
            assert response.id is not None

            # Get the final response text
            response_text = response.output_text
            print(f"\nAgent's response: {response_text}")

            # Verify we got a meaningful response with a GitHub username
            assert len(response_text) > 5, "Expected a response with a GitHub username"

            # The response should contain some indication of a username or GitHub profile info
            # We can't assert the exact username, but we can verify it's not an error
            assert (
                "error" not in response_text.lower() or "username" in response_text.lower()
            ), f"Expected response to contain GitHub profile info, but got: {response_text}"

            print("\n✓ Agent successfully used MCP tool with project connection to access authenticated GitHub API")

            # Teardown
            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("Agent deleted")
