# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import RecordedTransport
from test_samples import TestSamples, SampleExecutor, SamplePathPasser, _get_sample_paths, servicePreparer


class TestSamplesAsync(TestSamples):
    """Async test cases for samples, inheriting common functionality from TestSamples."""

    # To run this test with a specific sample, use:
    # pytest tests/samples/test_samples_async.py::TestSamplesAsync::test_agent_tools_samples_async[sample_agent_memory_search_async]
    @servicePreparer()
    @pytest.mark.parametrize(
        "sample_path",
        _get_sample_paths(
            "agents/tools",
            samples_to_skip=[
                "sample_agent_mcp_with_project_connection_async.py",
            ],
            is_async=True,
        ),
    )
    @SamplePathPasser()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_agent_tools_samples_async(self, sample_path: str, **kwargs) -> None:
        env_var_mapping = self._get_sample_environment_variables_map(operation_group="agents")
        executor = SampleExecutor(self, sample_path, env_var_mapping, **kwargs)
        await executor.execute_async()
