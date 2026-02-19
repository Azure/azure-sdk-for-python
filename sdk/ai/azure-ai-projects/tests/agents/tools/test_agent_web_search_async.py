# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

from test_base import TestBase, servicePreparer
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import RecordedTransport
from azure.ai.projects.models import PromptAgentDefinition, WebSearchPreviewTool, ApproximateLocation


class TestAgentWebSearchAsync(TestBase):

    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_agent_web_search_async(self, **kwargs):

        model = kwargs.get("azure_ai_model_deployment_name")

        async with (
            self.create_async_client(operation_group="agents", **kwargs) as project_client,
            project_client.get_openai_client() as openai_client,
        ):
            agent_name = "web-search-agent-async"

            # Create agent with web search tool
            agent = await project_client.agents.create_version(
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

            response = await openai_client.responses.create(
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
            await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("Agent deleted")
