# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

from test_base import TestBase, servicePreparer
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import RecordedTransport
from azure.ai.projects.models import (
    PromptAgentDefinition,
    CodeInterpreterTool,
    CodeInterpreterToolAuto,
)


class TestAgentCodeInterpreterAsync(TestBase):

    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_agent_code_interpreter_simple_math_async(self, **kwargs):
        """
        Test agent with Code Interpreter for simple Python code execution (async version).

        This test verifies that an agent can execute simple Python code
        without any file uploads or downloads - just pure code execution.
        """

        model = kwargs.get("AZURE_AI_MODEL_DEPLOYMENT_NAME")
        agent_name = "code-interpreter-simple-agent-async"

        async with (
            self.create_async_client(operation_group="agents", **kwargs) as project_client,
            project_client.get_openai_client() as openai_client,
        ):
            # Create agent with code interpreter tool (no files)
            agent = await project_client.agents.create_version(
                agent_name=agent_name,
                definition=PromptAgentDefinition(
                    model=model,
                    instructions="You are a helpful assistant that can execute Python code.",
                    tools=[CodeInterpreterTool(container=CodeInterpreterToolAuto(file_ids=[]))],
                ),
                description="Simple code interpreter agent for basic Python execution.",
            )
            self._validate_agent_version(agent, expected_name=agent_name)

            # Ask the agent to execute a complex Python calculation
            # Problem: Calculate the sum of cubes from 1 to 50, then add 12!/(8!)
            # Expected answer: 1637505
            print("\nAsking agent to calculate: sum of cubes from 1 to 50, plus 12!/(8!)")

            response = await openai_client.responses.create(
                input="Calculate this using Python: First, find the sum of cubes from 1 to 50 (1³ + 2³ + ... + 50³). Then add 12 factorial divided by 8 factorial (12!/8!). What is the final result?",
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )
            self.validate_response(response)

            # Get the response text
            last_message = response.output[-1]
            response_text = ""

            if last_message.type == "message":
                for content_item in last_message.content:
                    if content_item.type == "output_text":
                        response_text += content_item.text

            print(f"Agent's response: {response_text}")

            # Verify the response contains the correct answer (1637505)
            # Note: sum of cubes 1-50 = 1,625,625; 12!/8! = 11,880; total = 1,637,505
            assert (
                "1637505" in response_text or "1,637,505" in response_text
            ), f"Expected answer 1637505 to be in response, but got: {response_text}"

            print("✓ Code interpreter successfully executed Python code and returned correct answer")

            # Teardown
            await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("Agent deleted")
