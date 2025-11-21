# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

"""
Multi-Tool Tests: File Search + Code Interpreter + Function Tool

Tests various scenarios using an agent with all three tools together.
All tests use the same 3-tool combination but different inputs and workflows.
"""

import os
import json
import pytest
from test_base import TestBase, servicePreparer
from devtools_testutils import is_live_and_not_recording
from azure.ai.projects.models import PromptAgentDefinition, FileSearchTool, CodeInterpreterTool, CodeInterpreterToolAuto, FunctionTool
from openai.types.responses.response_input_param import FunctionCallOutput, ResponseInputParam


class TestAgentFileSearchCodeInterpreterFunction(TestBase):
    """Tests for agents using File Search + Code Interpreter + Function Tool."""

    @servicePreparer()
    @pytest.mark.skipif(
        condition=(not is_live_and_not_recording()),
        reason="Skipped because we cannot record network calls with OpenAI client",
    )
    def test_complete_analysis_workflow(self, **kwargs):
        """
        Test complete workflow: find data, analyze it, save results.
        """

        model = self.test_agents_params["model_deployment_name"]

        # Setup
        project_client = self.create_client(operation_group="agents", **kwargs)
        openai_client = project_client.get_openai_client()

        # Create data file
        txt_content = "Sample data for analysis"
        vector_store = openai_client.vector_stores.create(name="ThreeToolStore")
        
        from io import BytesIO
        txt_file = BytesIO(txt_content.encode('utf-8'))
        txt_file.name = "data.txt"
        
        file = openai_client.vector_stores.files.upload_and_poll(
            vector_store_id=vector_store.id,
            file=txt_file,
        )
        print(f"File uploaded (id: {file.id})")

        # Define function tool
        func_tool = FunctionTool(
            name="save_result",
            description="Save analysis result",
            parameters={
                "type": "object",
                "properties": {
                    "result": {"type": "string", "description": "The result"},
                },
                "required": ["result"],
                "additionalProperties": False,
            },
            strict=True,
        )

        # Create agent with all three tools
        agent = project_client.agents.create_version(
            agent_name="three-tool-agent",
            definition=PromptAgentDefinition(
                model=model,
                instructions="Use file search to find data, code interpreter to analyze it, and save_result to save findings.",
                tools=[
                    FileSearchTool(vector_store_ids=[vector_store.id]),
                    CodeInterpreterTool(container=CodeInterpreterToolAuto()),
                    func_tool,
                ],
            ),
            description="Agent using File Search, Code Interpreter, and Function Tool.",
        )
        print(f"Agent created (id: {agent.id})")
        
        # Use the agent
        response = openai_client.responses.create(
            input="Find the data file, analyze it, and save the results.",
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )
        print(f"Response received (id: {response.id})")
        
        assert response.id is not None
        print("✓ Three-tool combination works!")
        
        # Cleanup
        project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
        openai_client.vector_stores.delete(vector_store.id)

    @servicePreparer()
    @pytest.mark.skipif(
        condition=(not is_live_and_not_recording()),
        reason="Skipped because we cannot record network calls with OpenAI client",
    )
    def test_four_tools_combination(self, **kwargs):
        """
        Test with 4 tools: File Search + Code Interpreter + 2 Functions.
        """

        model = self.test_agents_params["model_deployment_name"]

        # Setup
        project_client = self.create_client(operation_group="agents", **kwargs)
        openai_client = project_client.get_openai_client()

        # Create vector store
        txt_content = "Test data"
        vector_store = openai_client.vector_stores.create(name="FourToolStore")
        
        from io import BytesIO
        txt_file = BytesIO(txt_content.encode('utf-8'))
        txt_file.name = "data.txt"
        
        file = openai_client.vector_stores.files.upload_and_poll(
            vector_store_id=vector_store.id,
            file=txt_file,
        )

        # Define two function tools
        func_tool_1 = FunctionTool(
            name="save_result",
            description="Save result",
            parameters={
                "type": "object",
                "properties": {
                    "result": {"type": "string", "description": "The result"},
                },
                "required": ["result"],
                "additionalProperties": False,
            },
            strict=True,
        )
        
        func_tool_2 = FunctionTool(
            name="log_action",
            description="Log an action",
            parameters={
                "type": "object",
                "properties": {
                    "action": {"type": "string", "description": "Action taken"},
                },
                "required": ["action"],
                "additionalProperties": False,
            },
            strict=True,
        )

        # Create agent with 4 tools
        agent = project_client.agents.create_version(
            agent_name="four-tool-agent",
            definition=PromptAgentDefinition(
                model=model,
                instructions="Use all available tools.",
                tools=[
                    FileSearchTool(vector_store_ids=[vector_store.id]),
                    CodeInterpreterTool(container=CodeInterpreterToolAuto()),
                    func_tool_1,
                    func_tool_2,
                ],
            ),
            description="Agent with 4 tools.",
        )
        print(f"Agent with 4 tools created (id: {agent.id})")
        
        assert agent.id is not None
        print("✓ 4 tools works!")
        
        # Cleanup
        project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
        openai_client.vector_stores.delete(vector_store.id)
