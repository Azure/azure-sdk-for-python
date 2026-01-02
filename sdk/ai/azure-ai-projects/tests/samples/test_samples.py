# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
from devtools_testutils import recorded_by_proxy, AzureRecordedTestCase, RecordedTransport
from test_base import servicePreparer
from sample_executor import (
    AdditionalSampleTestDetail,
    SyncSampleExecutor,
    additionalSampleTests,
    get_sample_paths,
    SamplePathPasser,
)
from test_samples_helpers import agent_tools_instructions, get_sample_environment_variables_map


class TestSamples(AzureRecordedTestCase):

    # To run this test with a specific sample, use:
    # pytest tests/samples/test_samples.py::TestSamples::test_agent_tools_samples[sample_agent_memory_search]
    @servicePreparer()
    @pytest.mark.parametrize(
        "sample_path",
        get_sample_paths(
            "agents/tools",
            samples_to_skip=[
                "sample_agent_bing_custom_search.py",
                "sample_agent_bing_grounding.py",
                "sample_agent_browser_automation.py",
                "sample_agent_fabric.py",
                "sample_agent_mcp_with_project_connection.py",
                "sample_agent_openapi_with_project_connection.py",
                "sample_agent_to_agent.py",
            ],
        ),
    )
    @SamplePathPasser()
    @additionalSampleTests(
        [
            AdditionalSampleTestDetail(
                sample_filename="sample_agent_computer_use.py",
                env_vars={"COMPUTER_USE_MODEL_DEPLOYMENT_NAME": "sanitized_model"},
            ),
        ]
    )
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_agent_tools_samples(self, sample_path: str, **kwargs) -> None:
        env_var_mapping = get_sample_environment_variables_map(operation_group="agents")
        executor = SyncSampleExecutor(self, sample_path, env_var_mapping, **kwargs)
        executor.execute()
        executor.validate_print_calls_by_llm(
            instructions=agent_tools_instructions,
            project_endpoint=kwargs["azure_ai_projects_tests_agents_project_endpoint"],
        )
