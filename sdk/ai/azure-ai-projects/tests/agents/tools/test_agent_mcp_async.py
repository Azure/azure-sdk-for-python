# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

import pytest
from test_base import TestBase, servicePreparer
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import RecordedTransport
from azure.ai.projects.models import PromptAgentDefinition, MCPTool, Tool
from openai.types.responses.response_input_param import McpApprovalResponse, ResponseInputParam


class TestAgentMCPAsync(TestBase):

    # To run only this test:
    # pytest tests/agents/tools/test_agent_mcp_async.py::TestAgentMCPAsync::test_agent_mcp_basic_async -s
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_agent_mcp_basic_async(self, **kwargs):

        model = self.test_agents_params["model_deployment_name"]

        async with (
            self.create_async_client(operation_group="agents", **kwargs) as project_client,
            project_client.get_openai_client() as openai_client,
        ):
            # Create MCP tool that connects to a public GitHub repo via MCP server
            mcp_tool = MCPTool(
                server_label="api-specs",
                server_url="https://gitmcp.io/Azure/azure-rest-api-specs",
                require_approval="always",
            )

            tools: list[Tool] = [mcp_tool]
            agent_name = "mcp-basic-agent"

            # Create agent with MCP tool
            agent = await project_client.agents.create_version(
                agent_name=agent_name,
                definition=PromptAgentDefinition(
                    model=model,
                    instructions="You are a helpful agent that can use MCP tools to assist users. Use the available MCP tools to answer questions and perform tasks.",
                    tools=tools,
                ),
                description="Agent for testing basic MCP functionality.",
            )
            self._validate_agent_version(agent, expected_name=agent_name)

            # Create conversation
            conversation = await openai_client.conversations.create()
            print(f"Created conversation (id: {conversation.id})")
            assert conversation.id is not None

            # Send initial request that will trigger the MCP tool
            print("\nAsking agent to summarize Azure REST API specs README...")

            response = await openai_client.responses.create(
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

            response = await openai_client.responses.create(
                conversation=conversation.id,
                input=input_list,
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
            await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("Agent deleted")
