# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

from test_base import TestBase, servicePreparer
from devtools_testutils import recorded_by_proxy, RecordedTransport
from azure.ai.projects.models import PromptAgentDefinition, WebSearchPreviewTool, ApproximateLocation


class TestAgentWebSearch(TestBase):

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_agent_web_search(self, **kwargs):
        """
        Test agent with Web Search tool for real-time information.

        This test verifies that an agent can:
        1. Use WebSearchPreviewTool to search the web
        2. Get current/real-time information
        3. Provide answers based on web search results

        Routes used in this test:

        Action REST API Route                                Client Method
        ------+---------------------------------------------+-----------------------------------
        # Setup:
        POST   /agents/{agent_name}/versions                 project_client.agents.create_version()

        # Test focus:
        POST   /openai/responses                             openai_client.responses.create() (with WebSearchPreviewTool)

        # Teardown:
        DELETE /agents/{agent_name}/versions/{agent_version} project_client.agents.delete_version()
        """

        model = kwargs.get("azure_ai_model_deployment_name")

        with (
            self.create_client(operation_group="agents", **kwargs) as project_client,
            project_client.get_openai_client() as openai_client,
        ):
            agent_name = "web-search-agent"

            # Create agent with web search tool
            agent = project_client.agents.create_version(
                agent_name=agent_name,
                definition=PromptAgentDefinition(
                    model=model,
                    instructions="You are a helpful assistant that can search the web for current information.",
                    tools=[
                        WebSearchPreviewTool(
                            user_location=ApproximateLocation(country="US", city="Seattle", region="Washington")
                        )
                    ],
                ),
                description="Agent for testing web search capabilities.",
            )
            self._validate_agent_version(agent, expected_name=agent_name)

            # Ask a question that requires web search for current information
            print("\nAsking agent about current weather...")

            response = openai_client.responses.create(
                input="What is the current weather in Seattle?",
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            self.validate_response(response)

            # Get the response text
            response_text = response.output_text
            print(f"\nAgent's response: {response_text[:300]}...")

            # Verify we got a meaningful response
            assert len(response_text) > 30, f"Expected a substantial response from the agent. Got '{response_text}'"

            # The response should mention weather-related terms or Seattle
            response_lower = response_text.lower()
            assert any(
                keyword in response_lower for keyword in ["weather", "temperature", "seattle", "forecast"]
            ), f"Expected response to contain weather information, but got: {response_text[:200]}"

            print("\n✓ Agent successfully used web search tool to get current information")

            # Teardown
            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("Agent deleted")
