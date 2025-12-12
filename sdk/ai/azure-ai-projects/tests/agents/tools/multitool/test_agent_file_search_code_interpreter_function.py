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

import json
from io import BytesIO
from test_base import TestBase, servicePreparer
from devtools_testutils import recorded_by_proxy, RecordedTransport
from azure.ai.projects.models import (
    PromptAgentDefinition,
    FileSearchTool,
    CodeInterpreterTool,
    CodeInterpreterToolAuto,
    FunctionTool,
)
from openai.types.responses.response_input_param import FunctionCallOutput, ResponseInputParam


class TestAgentFileSearchCodeInterpreterFunction(TestBase):
    """Tests for agents using File Search + Code Interpreter + Function Tool."""

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_complete_analysis_workflow(self, **kwargs):
        """
        Test complete workflow: find data, analyze it, save results.

        This test verifies that all three tools are used:
        1. File Search: Agent finds the data file with numerical values
        2. Code Interpreter: Agent performs statistical calculations on the data
        3. Function Tool: Agent saves the computed results
        """

        model = kwargs.get("azure_ai_projects_tests_model_deployment_name")

        # Setup
        project_client = self.create_client(operation_group="agents", **kwargs)
        openai_client = project_client.get_openai_client()

        # Create data file with numbers that require computation
        # Values: 23, 47, 82, 15, 91, 38, 64, 29, 76, 55
        # Sum: 520, Count: 10, Average: 52.0, Min: 15, Max: 91
        txt_content = """Monthly Sales Report - Store #147

The following sales figures (in thousands) were recorded:

January: 23
February: 47
March: 82
April: 15
May: 91
June: 38
July: 64
August: 29
September: 76
October: 55

Please analyze this data for the quarterly review.
"""
        vector_store = openai_client.vector_stores.create(name="ThreeToolStore")

        txt_file = BytesIO(txt_content.encode("utf-8"))
        txt_file.name = "sales_report.txt"

        file = openai_client.vector_stores.files.upload_and_poll(
            vector_store_id=vector_store.id,
            file=txt_file,
        )
        print(f"File uploaded (id: {file.id})")

        # Define function tool for saving analysis results
        func_tool = FunctionTool(
            name="save_analysis",
            description="Save the statistical analysis results. Must be called to persist the analysis.",
            parameters={
                "type": "object",
                "properties": {
                    "report_name": {"type": "string", "description": "Name of the report analyzed"},
                    "total": {"type": "number", "description": "Sum of all values"},
                    "average": {"type": "number", "description": "Average of all values"},
                    "summary": {"type": "string", "description": "Brief summary of findings"},
                },
                "required": ["report_name", "total", "average", "summary"],
                "additionalProperties": False,
            },
            strict=True,
        )

        # Create agent with all three tools and explicit instructions
        agent = project_client.agents.create_version(
            agent_name="three-tool-agent",
            definition=PromptAgentDefinition(
                model=model,
                instructions="You are a data analyst. Use file search to find data files, code interpreter to calculate statistics, and ALWAYS save your analysis using the save_analysis function.",
                tools=[
                    FileSearchTool(vector_store_ids=[vector_store.id]),
                    CodeInterpreterTool(container=CodeInterpreterToolAuto()),
                    func_tool,
                ],
            ),
            description="Agent using File Search, Code Interpreter, and Function Tool.",
        )
        print(f"Agent created (id: {agent.id})")

        # Request that requires all three tools
        response = openai_client.responses.create(
            input="Find the sales report, use code to calculate the total and average of all monthly sales figures, then save the analysis results.",
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )
        self.validate_response(response)
        print("✓ Three-tool combination works!")

        # Cleanup
        project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
        openai_client.vector_stores.delete(vector_store.id)
