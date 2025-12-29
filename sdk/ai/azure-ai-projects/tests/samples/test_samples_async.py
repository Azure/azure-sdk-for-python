# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import AzureRecordedTestCase, RecordedTransport
from test_base import servicePreparer
from sample_executor import AsyncSampleExecutor, get_async_sample_paths, SamplePathPasser
from test_samples_helpers import agent_tools_instructions, get_sample_environment_variables_map


class TestSamplesAsync(AzureRecordedTestCase):
    """Async test cases for samples."""

    # To run this test with a specific sample, use:
    # pytest tests/samples/test_samples_async.py::TestSamplesAsync::test_agent_tools_samples_async[sample_agent_memory_search_async]
    @servicePreparer()
    @pytest.mark.parametrize(
        "sample_path",
        get_async_sample_paths(
            "agents/tools",
            samples_to_skip=[
                "sample_agent_mcp_with_project_connection_async.py",
            ],
        ),
    )
    @SamplePathPasser()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_agent_tools_samples_async(self, sample_path: str, **kwargs) -> None:
        env_var_mapping = get_sample_environment_variables_map(operation_group="agents")
        executor = AsyncSampleExecutor(self, sample_path, env_var_mapping, **kwargs)
        await executor.execute_async()
        await executor.validate_print_calls_by_llm_async(
            instructions=agent_tools_instructions,
            project_endpoint=os.environ["azure_ai_projects_agents_project_endpoint"],
        )
