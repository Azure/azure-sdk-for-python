# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

import pytest
from test_base import TestBase, servicePreparer
from devtools_testutils import is_live_and_not_recording
from azure.ai.projects.models import (
    PromptAgentDefinition,
    BingGroundingAgentTool,
    BingGroundingSearchToolParameters,
    BingGroundingSearchConfiguration,
)


class TestAgentBingGrounding(TestBase):

    @servicePreparer()
    @pytest.mark.skipif(
        condition=(not is_live_and_not_recording()),
        reason="Skipped because we cannot record network calls with OpenAI client",
    )
    def test_agent_bing_grounding(self, **kwargs):
        """
        Test agent with Bing grounding capabilities.

        This test verifies that an agent can be created with BingGroundingAgentTool,
        use it to search the web for current information, and provide responses with
        URL citations.

        Routes used in this test:

        Action REST API Route                                Client Method
        ------+---------------------------------------------+-----------------------------------
        # Setup:
        POST   /agents/{agent_name}/versions                 project_client.agents.create_version()

        # Test focus:
        POST   /openai/responses                             openai_client.responses.create() (with Bing grounding)

        # Teardown:
        DELETE /agents/{agent_name}/versions/{agent_version} project_client.agents.delete_version()
        """

        model = self.test_agents_params["model_deployment_name"]

        # Setup
        project_client = self.create_client(operation_group="agents", **kwargs)
        openai_client = project_client.get_openai_client()

        # Note: This test requires BING_PROJECT_CONNECTION_ID environment variable
        # to be set with a valid Bing connection ID from the project
        bing_connection_id = kwargs.get("azure_ai_projects_tests_bing_connection_id")
        
        if not bing_connection_id:
            pytest.skip("BING_PROJECT_CONNECTION_ID environment variable not set")
        
        assert isinstance(bing_connection_id, str), "bing_connection_id must be a string"

        # Create agent with Bing grounding tool
        agent = project_client.agents.create_version(
            agent_name="bing-grounding-agent",
            definition=PromptAgentDefinition(
                model=model,
                instructions="You are a helpful assistant.",
                tools=[
                    BingGroundingAgentTool(
                        bing_grounding=BingGroundingSearchToolParameters(
                            search_configurations=[
                                BingGroundingSearchConfiguration(
                                    project_connection_id=bing_connection_id
                                )
                            ]
                        )
                    )
                ],
            ),
            description="You are a helpful agent.",
        )
        print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")
        assert agent.id is not None
        assert agent.name == "bing-grounding-agent"
        assert agent.version is not None

        # Test agent with a query that requires current web information
        output_text = ""
        url_citations = []
        
        stream_response = openai_client.responses.create(
            stream=True,
            tool_choice="required",
            input="What is the current weather in Seattle?",
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )

        for event in stream_response:
            if event.type == "response.created":
                print(f"Follow-up response created with ID: {event.response.id}")
                assert event.response.id is not None
            elif event.type == "response.output_text.delta":
                print(f"Delta: {event.delta}")
            elif event.type == "response.text.done":
                print(f"Follow-up response done!")
            elif event.type == "response.output_item.done":
                if event.item.type == "message":
                    item = event.item
                    if item.content and len(item.content) > 0:
                        if item.content[-1].type == "output_text":
                            text_content = item.content[-1]
                            for annotation in text_content.annotations:
                                if annotation.type == "url_citation":
                                    print(f"URL Citation: {annotation.url}")
                                    url_citations.append(annotation.url)
            elif event.type == "response.completed":
                print(f"Follow-up completed!")
                print(f"Full response: {event.response.output_text}")
                output_text = event.response.output_text

        # Verify that we got a response
        assert len(output_text) > 0, "Expected non-empty response text"
        
        # Verify that we got URL citations (Bing grounding should provide sources)
        assert len(url_citations) > 0, "Expected URL citations from Bing grounding"
        
        # Verify that citations are valid URLs
        for url in url_citations:
            assert url.startswith("http://") or url.startswith("https://"), f"Invalid URL citation: {url}"
        
        print(f"Test completed successfully with {len(url_citations)} URL citations")

        # Teardown
        project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
        print("Agent deleted")

    @servicePreparer()
    @pytest.mark.skipif(
        condition=(not is_live_and_not_recording()),
        reason="Skipped because we cannot record network calls with OpenAI client",
    )
    def test_agent_bing_grounding_multiple_queries(self, **kwargs):
        """
        Test agent with Bing grounding for multiple queries.

        This test verifies that an agent can handle multiple queries using
        Bing grounding and provide accurate responses with citations.
        """

        model = self.test_agents_params["model_deployment_name"]

        # Setup
        project_client = self.create_client(operation_group="agents", **kwargs)
        openai_client = project_client.get_openai_client()

        bing_connection_id = kwargs.get("azure_ai_projects_tests_bing_connection_id")
        
        if not bing_connection_id:
            pytest.skip("BING_PROJECT_CONNECTION_ID environment variable not set")
        
        assert isinstance(bing_connection_id, str), "bing_connection_id must be a string"

        # Create agent with Bing grounding tool
        agent = project_client.agents.create_version(
            agent_name="bing-grounding-multi-query-agent",
            definition=PromptAgentDefinition(
                model=model,
                instructions="You are a helpful assistant that provides current information.",
                tools=[
                    BingGroundingAgentTool(
                        bing_grounding=BingGroundingSearchToolParameters(
                            search_configurations=[
                                BingGroundingSearchConfiguration(
                                    project_connection_id=bing_connection_id
                                )
                            ]
                        )
                    )
                ],
            ),
            description="Agent for testing multiple Bing grounding queries.",
        )
        print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

        # Test with multiple different queries
        queries = [
            "What is today's date?",
            "What are the latest news about AI?",
        ]

        for query in queries:
            print(f"\nTesting query: {query}")
            output_text = ""
            url_citations = []
            
            stream_response = openai_client.responses.create(
                stream=True,
                tool_choice="required",
                input=query,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            for event in stream_response:
                if event.type == "response.output_item.done":
                    if event.item.type == "message":
                        item = event.item
                        if item.content and len(item.content) > 0:
                            if item.content[-1].type == "output_text":
                                text_content = item.content[-1]
                                for annotation in text_content.annotations:
                                    if annotation.type == "url_citation":
                                        url_citations.append(annotation.url)
                elif event.type == "response.completed":
                    output_text = event.response.output_text

            # Verify that we got a response for each query
            assert len(output_text) > 0, f"Expected non-empty response text for query: {query}"
            print(f"Response length: {len(output_text)} characters")
            print(f"URL citations found: {len(url_citations)}")

        # Teardown
        project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
        print("Agent deleted")
