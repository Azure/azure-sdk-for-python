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
    AzureAISearchAgentTool,
    AzureAISearchToolResource,
    AISearchIndexResource,
    AzureAISearchQueryType,
)

# The tests in this file rely on an existing Azure AI Search project connection that has been populated with the following document:
# https://arxiv.org/pdf/2508.03680

class TestAgentAISearch(TestBase):

    # Test questions with expected answers
    TEST_QUESTIONS = [
        {
            "question": "Agent Lightning's unified data interface and MDP formulation are designed to separate task-specific agent design from learning-based policy optimization.",
            "answer": True,
        },
        {
            "question": "LightningRL optimizes multi-call agent trajectories mainly by masking out non-LLM tokens in long trajectories, without decomposing them into transitions.",
            "answer": False,
        },
        {
            "question": "The Training–Agent Disaggregation architecture uses an Agent Lightning Server (with an OpenAI-like API) and a Client so that agents can run their own tool/code logic without being co-located with the GPU training framework.",
            "answer": True,
        },
        {
            "question": "In the text-to-SQL experiment, the authors used LangChain to build a 3-agent workflow on the Spider dataset, but only trained 2 of those agents (the SQL-writing and rewriting agents).",
            "answer": True,
        },
        {
            "question": "The math QA task in the experiments was implemented with LangChain and used a SQL executor as its external tool.",
            "answer": False,
        },
    ]

    @servicePreparer()
    @pytest.mark.skip(reason="Slow sequential sync test - covered by faster parallel async test")
    @pytest.mark.skipif(
        condition=(not is_live_and_not_recording()),
        reason="Skipped because we cannot record network calls with OpenAI client",
    )
    def test_agent_ai_search_question_answering(self, **kwargs):
        """
        Test agent with Azure AI Search capabilities for question answering.

        NOTE: This test is skipped in favor of the parallel async version which is
        significantly faster (~3x) and provides the same coverage.
        See test_agent_ai_search_async.py::test_agent_ai_search_question_answering_async_parallel

        This test verifies that an agent can be created with AzureAISearchAgentTool,
        use it to search indexed content, and provide accurate answers to questions
        based on the search results.

        The test asks 5 true/false questions and validates that at least 4 are
        answered correctly by the agent using the search index.

        Routes used in this test:

        Action REST API Route                                Client Method
        ------+---------------------------------------------+-----------------------------------
        # Setup:
        POST   /agents/{agent_name}/versions                 project_client.agents.create_version()

        # Test focus:
        POST   /openai/responses                             openai_client.responses.create() (with AI Search)

        # Teardown:
        DELETE /agents/{agent_name}/versions/{agent_version} project_client.agents.delete_version()
        """

        model = self.test_agents_params["model_deployment_name"]

        # Get AI Search connection and index from environment
        ai_search_connection_id = kwargs.get("azure_ai_projects_tests_ai_search_project_connection_id")
        ai_search_index_name = kwargs.get("azure_ai_projects_tests_ai_search_index_name")

        if not ai_search_connection_id:
            pytest.fail("AZURE_AI_PROJECTS_TESTS_AI_SEARCH_PROJECT_CONNECTION_ID environment variable not set")

        if not ai_search_index_name:
            pytest.fail("AZURE_AI_PROJECTS_TESTS_AI_SEARCH_INDEX_NAME environment variable not set")

        assert isinstance(ai_search_connection_id, str), "ai_search_connection_id must be a string"
        assert isinstance(ai_search_index_name, str), "ai_search_index_name must be a string"

        with (
            self.create_client(operation_group="agents", **kwargs) as project_client,
            project_client.get_openai_client() as openai_client,
        ):
            agent_name = "ai-search-qa-agent"

            # Create agent with Azure AI Search tool
            agent = project_client.agents.create_version(
                agent_name=agent_name,
                definition=PromptAgentDefinition(
                    model=model,
                    instructions="""You are a helpful assistant that answers true/false questions based on the provided search results.
                Always use the Azure AI Search tool to find relevant information before answering.
                Respond with only 'True' or 'False' based on what you find in the search results.
                If you cannot find clear evidence in the search results, answer 'False'.""",
                    tools=[
                        AzureAISearchAgentTool(
                            azure_ai_search=AzureAISearchToolResource(
                                indexes=[
                                    AISearchIndexResource(
                                        project_connection_id=ai_search_connection_id,
                                        index_name=ai_search_index_name,
                                        query_type=AzureAISearchQueryType.SIMPLE,
                                    ),
                                ]
                            )
                        )
                    ],
                ),
                description="Agent for testing AI Search question answering.",
            )
            self._validate_agent_version(agent, expected_name=agent_name)

            # Test each question
            correct_answers = 0
            total_questions = len(self.TEST_QUESTIONS)

            for i, qa_pair in enumerate(self.TEST_QUESTIONS, 1):
                question = qa_pair["question"]
                expected_answer = qa_pair["answer"]

                print(f"\n{'='*80}")
                print(f"Question {i}/{total_questions}:")
                print(f"Q: {question}")
                print(f"Expected: {expected_answer}")

                output_text = ""

                stream_response = openai_client.responses.create(
                    stream=True,
                    tool_choice="required",
                    input=f"Answer this question with only 'True' or 'False': {question}",
                    extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
                )

                for event in stream_response:
                    if event.type == "response.created":
                        print(f"Response created with ID: {event.response.id}")
                    elif event.type == "response.output_text.delta":
                        pass  # Don't print deltas to reduce output
                    elif event.type == "response.completed":
                        output_text = event.response.output_text
                        print(f"Agent's answer: {output_text}")

                # Parse the answer from the output
                # Look for "True" or "False" in the response
                output_lower = output_text.lower()
                agent_answer = None

                # Try to extract boolean answer
                if "true" in output_lower and "false" not in output_lower:
                    agent_answer = True
                elif "false" in output_lower and "true" not in output_lower:
                    agent_answer = False
                elif output_lower.strip() in ["true", "false"]:
                    agent_answer = output_lower.strip() == "true"
                else:
                    # Try to determine based on more complex responses
                    # Count occurrences
                    true_count = output_lower.count("true")
                    false_count = output_lower.count("false")
                    if true_count > false_count:
                        agent_answer = True
                    elif false_count > true_count:
                        agent_answer = False

                if agent_answer is not None:
                    is_correct = agent_answer == expected_answer
                    if is_correct:
                        correct_answers += 1
                        print(f"✓ CORRECT (Agent: {agent_answer}, Expected: {expected_answer})")
                    else:
                        print(f"✗ INCORRECT (Agent: {agent_answer}, Expected: {expected_answer})")
                else:
                    print(f"✗ UNABLE TO PARSE ANSWER from: {output_text}")

            # Print summary
            print(f"\n{'='*80}")
            print(f"SUMMARY: {correct_answers}/{total_questions} questions answered correctly")
            print(f"{'='*80}")

            # Verify that at least 4 out of 5 questions were answered correctly
            assert correct_answers >= 4, (
                f"Expected at least 4 correct answers out of {total_questions}, "
                f"but got {correct_answers}. The agent needs to answer at least 80% correctly."
            )

            print(
                f"\n✓ Test passed! Agent answered {correct_answers}/{total_questions} questions correctly (>= 4 required)"
            )

            # Teardown
            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("Agent deleted")
