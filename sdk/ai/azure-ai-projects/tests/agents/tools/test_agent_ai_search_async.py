# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

import asyncio
import pytest
from test_base import TestBase, servicePreparer
from devtools_testutils import is_live_and_not_recording
from azure.ai.projects.models import (
    PromptAgentDefinition,
    AzureAISearchTool,
    AzureAISearchToolResource,
    AISearchIndexResource,
    AzureAISearchQueryType,
)

# The tests in this file rely on an existing Azure AI Search project connection that has been populated with the following document:
# https://arxiv.org/pdf/2508.03680


class TestAgentAISearchAsync(TestBase):

    # Test questions with expected answers
    TEST_QUESTIONS = [
        {
            "title": "Unified Data Interface",
            "question": "Agent Lightning's unified data interface and MDP formulation are designed to separate task-specific agent design from learning-based policy optimization.",
            "answer": True,
        },
        {
            "title": "LightningRL Optimization",
            "question": "LightningRL optimizes multi-call agent trajectories mainly by masking out non-LLM tokens in long trajectories, without decomposing them into transitions.",
            "answer": False,
        },
        {
            "title": "Training-Agent Disaggregation",
            "question": "The Training–Agent Disaggregation architecture uses an Agent Lightning Server (with an OpenAI-like API) and a Client so that agents can run their own tool/code logic without being co-located with the GPU training framework.",
            "answer": True,
        },
        {
            "title": "Text-to-SQL Experiment",
            "question": "In the text-to-SQL experiment, the authors used LangChain to build a 3-agent workflow on the Spider dataset, but only trained 2 of those agents (the SQL-writing and rewriting agents).",
            "answer": True,
        },
        {
            "title": "Math QA Implementation",
            "question": "The math QA task in the experiments was implemented with LangChain and used a SQL executor as its external tool.",
            "answer": False,
        },
    ]

    async def _ask_question_async(
        self,
        openai_client,
        agent_name: str,
        title: str,
        question: str,
        expected_answer: bool,
        question_num: int,
        total_questions: int,
    ):
        """Helper method to ask a single question asynchronously."""
        print(f"\n{'='*80}")
        print(f"Q{question_num}/{total_questions}: {title}")
        print(f"{question}")
        print(f"Expected: {expected_answer}")

        output_text = ""

        stream_response = await openai_client.responses.create(
            stream=True,
            tool_choice="required",
            input=f"Answer this question with only 'True' or 'False': {question}",
            extra_body={"agent": {"name": agent_name, "type": "agent_reference"}},
        )

        async for event in stream_response:
            if event.type == "response.created":
                print(f"Response ID: {event.response.id}")
            elif event.type == "response.completed":
                output_text = event.response.output_text

        # Parse the answer from the output
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
            true_count = output_lower.count("true")
            false_count = output_lower.count("false")
            if true_count > false_count:
                agent_answer = True
            elif false_count > true_count:
                agent_answer = False

        is_correct = False
        if agent_answer is not None:
            is_correct = agent_answer == expected_answer
            if is_correct:
                print(f"✓ Q{question_num} ({title}): CORRECT")
            else:
                print(f"✗ Q{question_num} ({title}): INCORRECT (Agent: {agent_answer}, Expected: {expected_answer})")
        else:
            print(f"✗ Q{question_num} ({title}): UNABLE TO PARSE ANSWER from: {output_text}")

        return is_correct

    @servicePreparer()
    @pytest.mark.skipif(
        condition=(not is_live_and_not_recording()),
        reason="Skipped because we cannot record network calls with OpenAI client",
    )
    @pytest.mark.asyncio
    async def test_agent_ai_search_question_answering_async_parallel(self, **kwargs):
        """
        Test agent with Azure AI Search capabilities for question answering using async (parallel).

        This test verifies that an agent can be created with AzureAISearchTool,
        and handle multiple concurrent requests to search indexed content and provide
        accurate answers to questions based on the search results.

        The test asks 5 true/false questions IN PARALLEL using asyncio.gather() and
        validates that at least 4 are answered correctly by the agent using the search index.

        This should be significantly faster than the sequential version.

        Routes used in this test:

        Action REST API Route                                Client Method
        ------+---------------------------------------------+-----------------------------------
        # Setup:
        POST   /agents/{agent_name}/versions                 project_client.agents.create_version()

        # Test focus:
        POST   /openai/responses (concurrent)                openai_client.responses.create() (with AI Search, parallel)

        # Teardown:
        DELETE /agents/{agent_name}/versions/{agent_version} project_client.agents.delete_version()
        """

        model = kwargs.get("azure_ai_model_deployment_name")

        # Setup
        project_client = self.create_async_client(operation_group="agents", **kwargs)

        async with project_client:
            openai_client = project_client.get_openai_client()

            # Get AI Search connection and index from environment
            ai_search_connection_id = kwargs.get("ai_search_project_connection_id")
            ai_search_index_name = kwargs.get("ai_search_index_name")

            if not ai_search_connection_id:
                pytest.fail("ai_search_project_connection_id environment variable not set")

            if not ai_search_index_name:
                pytest.fail("ai_search_index_name environment variable not set")

            assert isinstance(ai_search_connection_id, str), "ai_search_connection_id must be a string"
            assert isinstance(ai_search_index_name, str), "ai_search_index_name must be a string"

            agent_name = "ai-search-qa-agent-async-parallel"

            # Create agent with Azure AI Search tool
            agent = await project_client.agents.create_version(
                agent_name=agent_name,
                definition=PromptAgentDefinition(
                    model=model,
                    instructions="""You are a helpful assistant that answers true/false questions based on the provided search results.
                    Always use the Azure AI Search tool to find relevant information before answering.
                    Respond with only 'True' or 'False' based on what you find in the search results.
                    If you cannot find clear evidence in the search results, answer 'False'.""",
                    tools=[
                        AzureAISearchTool(
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
                description="Agent for testing AI Search question answering (async parallel).",
            )
            self._validate_agent_version(agent, expected_name=agent_name)

            # Test all questions IN PARALLEL using asyncio.gather()
            total_questions = len(self.TEST_QUESTIONS)
            print(f"\nRunning {total_questions} questions in parallel...")

            # Create tasks for all questions
            tasks = []
            for i, qa_pair in enumerate(self.TEST_QUESTIONS, 1):
                title = qa_pair["title"]
                question = qa_pair["question"]
                expected_answer = qa_pair["answer"]

                task = self._ask_question_async(
                    openai_client, agent.name, title, question, expected_answer, i, total_questions
                )
                tasks.append(task)

            # Run all tasks in parallel and collect results
            results = await asyncio.gather(*tasks)

            # Count correct answers
            correct_answers = sum(1 for is_correct in results if is_correct)

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
            await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("Agent deleted")
