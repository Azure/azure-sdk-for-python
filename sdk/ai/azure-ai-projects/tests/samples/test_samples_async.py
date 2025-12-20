# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import AzureRecordedTestCase, RecordedTransport
from test_base import servicePreparer
from test_samples_base import (
    SamplePathPasser,
    get_sample_paths,
    get_sample_environment_variables_map,
)
from async_sample_executor import AsyncSampleExecutor


def _get_async_sample_paths(sub_folder: str, *, samples_to_skip: list[str]) -> list:
    return get_sample_paths(sub_folder, samples_to_skip=samples_to_skip, is_async=True)


class TestSamplesAsync(AzureRecordedTestCase):
    """Async test cases for samples."""

    # To run this test with a specific sample, use:
    # pytest tests/samples/test_samples_async.py::TestSamplesAsync::test_agent_tools_samples_async[sample_agent_memory_search_async]
    @servicePreparer()
    @pytest.mark.parametrize(
        "sample_path",
        _get_async_sample_paths(
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
