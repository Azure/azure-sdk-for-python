# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import AzureRecordedTestCase, RecordedTransport
from test_base import servicePreparer
from sample_executor import (
    AsyncSampleExecutor,
    SamplePathPasser,
    get_async_sample_paths,
)
from test_samples_helpers import (
    agent_tools_instructions,
    get_sample_env_vars,
    memories_instructions,
    agents_instructions,
    resource_management_instructions,
)


class TestSamplesAsync(AzureRecordedTestCase):
    """Async test cases for samples."""

    # To run this test with a specific sample, use:
    # pytest tests/samples/test_samples_async.py::TestSamplesAsync::test_agent_tools_samples_async[sample_agent_memory_search_async]
    @servicePreparer()
    @pytest.mark.parametrize(
        "sample_path",
        get_async_sample_paths(
            "agents/tools",
            samples_to_skip=["sample_agent_computer_use_async.py"],
        ),
    )
    @SamplePathPasser()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_agent_tools_samples_async(self, sample_path: str, **kwargs) -> None:
        env_vars = get_sample_env_vars(kwargs)
        executor = AsyncSampleExecutor(
            self,
            sample_path,
            env_vars=env_vars,
            **kwargs,
        )
        await executor.execute_async()
        await executor.validate_print_calls_by_llm_async(
            instructions=agent_tools_instructions,
            project_endpoint=kwargs["azure_ai_project_endpoint"],
            model=kwargs["azure_ai_model_deployment_name"],
        )

    @pytest.mark.parametrize(
        "sample_path",
        get_async_sample_paths(
            "memories",
            samples_to_skip=[],
        ),
    )
    @servicePreparer()
    @SamplePathPasser()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_memory_samples(self, sample_path: str, **kwargs) -> None:
        env_vars = get_sample_env_vars(kwargs)
        executor = AsyncSampleExecutor(self, sample_path, env_vars=env_vars, **kwargs)
        await executor.execute_async()
        await executor.validate_print_calls_by_llm_async(
            instructions=memories_instructions,
            project_endpoint=kwargs["azure_ai_project_endpoint"],
            model=kwargs["azure_ai_model_deployment_name"],
        )

    @pytest.mark.parametrize(
        "sample_path",
        get_async_sample_paths(
            "agents",
            samples_to_skip=[],
        ),
    )
    @servicePreparer()
    @SamplePathPasser()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_agents_samples(self, sample_path: str, **kwargs) -> None:
        env_vars = get_sample_env_vars(kwargs)
        executor = AsyncSampleExecutor(self, sample_path, env_vars=env_vars, **kwargs)
        await executor.execute_async()
        await executor.validate_print_calls_by_llm_async(
            instructions=agents_instructions,
            project_endpoint=kwargs["azure_ai_project_endpoint"],
            model=kwargs["azure_ai_model_deployment_name"],
        )

    @pytest.mark.parametrize(
        "sample_path",
        get_async_sample_paths(
            "connections",
            samples_to_skip=[],
        ),
    )
    @servicePreparer()
    @SamplePathPasser()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_connections_samples(self, sample_path: str, **kwargs) -> None:
        kwargs = kwargs.copy()
        kwargs["connection_name"] = "mcp"
        env_vars = get_sample_env_vars(kwargs)
        executor = AsyncSampleExecutor(self, sample_path, env_vars=env_vars, **kwargs)
        await executor.execute_async()
        await executor.validate_print_calls_by_llm_async(
            instructions=resource_management_instructions,
            project_endpoint=kwargs["azure_ai_project_endpoint"],
            model=kwargs["azure_ai_model_deployment_name"],
        )

    @pytest.mark.parametrize(
        "sample_path",
        get_async_sample_paths(
            "files",
            samples_to_skip=[],
        ),
    )
    @servicePreparer()
    @SamplePathPasser()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_files_samples(self, sample_path: str, **kwargs) -> None:
        env_vars = get_sample_env_vars(kwargs)
        executor = AsyncSampleExecutor(self, sample_path, env_vars=env_vars, **kwargs)
        await executor.execute_async()
        await executor.validate_print_calls_by_llm_async(
            instructions=resource_management_instructions,
            project_endpoint=kwargs["azure_ai_project_endpoint"],
            model=kwargs["azure_ai_model_deployment_name"],
        )

    @pytest.mark.parametrize(
        "sample_path",
        get_async_sample_paths(
            "deployments",
            samples_to_skip=[],
        ),
    )
    @servicePreparer()
    @SamplePathPasser()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_deployments_samples(self, sample_path: str, **kwargs) -> None:
        env_vars = get_sample_env_vars(kwargs)
        executor = AsyncSampleExecutor(self, sample_path, env_vars=env_vars, **kwargs)
        await executor.execute_async()
        await executor.validate_print_calls_by_llm_async(
            instructions=resource_management_instructions,
            project_endpoint=kwargs["azure_ai_project_endpoint"],
            model=kwargs["azure_ai_model_deployment_name"],
        )

    @pytest.mark.parametrize(
        "sample_path",
        get_async_sample_paths(
            "datasets",
            samples_to_skip=[],
        ),
    )
    @servicePreparer()
    @SamplePathPasser()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_datasets_samples(self, sample_path: str, **kwargs) -> None:
        env_vars = get_sample_env_vars(kwargs)
        executor = AsyncSampleExecutor(self, sample_path, env_vars=env_vars, **kwargs)
        await executor.execute_async()
        if self.is_live:
            # Don't replay LLM validation since there probably a defect in proxy server fail to replay
            # Proxy server probably not able to parse the captured print content
            await executor.validate_print_calls_by_llm_async(
                instructions=resource_management_instructions,
                project_endpoint=kwargs["azure_ai_project_endpoint"],
                model=kwargs["azure_ai_model_deployment_name"],
            )
