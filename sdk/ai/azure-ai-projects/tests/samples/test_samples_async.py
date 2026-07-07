# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest, os
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import AzureRecordedTestCase, RecordedTransport
from test_base import servicePreparer, modelsServicePreparer
from sample_executor import (
    AdditionalSampleTestDetail,
    AsyncSampleExecutor,
    SamplePathPasser,
    additionalSampleTests,
    get_async_sample_paths,
)
from test_samples_helpers import get_sample_env_vars


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
                "sample_agent_computer_use_async.py",
                "sample_agent_memory_search_async.py",  # Skipped until re-enabled and recorded on Foundry endpoint that supports the new versioning schema
            ],
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
        await executor.validate_print_calls_by_llm_async()

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
    # To run this test: pytest tests/samples/test_samples_async.py::TestSamplesAsync::test_memory_samples -s
    async def test_memory_samples(self, sample_path: str, **kwargs) -> None:
        env_vars = get_sample_env_vars(kwargs)
        executor = AsyncSampleExecutor(self, sample_path, env_vars=env_vars, **kwargs)
        await executor.execute_async()
        await executor.validate_print_calls_by_llm_async()

    @pytest.mark.parametrize(
        "sample_path",
        get_async_sample_paths(
            "agents",
            samples_to_skip=[
                "sample_external_agents_crud_async.py",  # Skipped until recordings are available.
                "sample_workflow_multi_agent_async.py",
            ],
        ),
    )
    @servicePreparer()
    @SamplePathPasser()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_agents_samples(self, sample_path: str, **kwargs) -> None:
        env_vars = get_sample_env_vars(kwargs)
        executor = AsyncSampleExecutor(self, sample_path, env_vars=env_vars, **kwargs)
        await executor.execute_async()
        await executor.validate_print_calls_by_llm_async()

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
        await executor.validate_print_calls_by_llm_async()

    @pytest.mark.parametrize(
        "sample_path",
        get_async_sample_paths(
            "files",
            samples_to_skip=[
                "sample_files_async.py",  # Skipped until re-enabled and recorded on Foundry endpoint that supports the new versioning schema
            ],
        ),
    )
    @servicePreparer()
    @SamplePathPasser()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_files_samples(self, sample_path: str, **kwargs) -> None:
        env_vars = get_sample_env_vars(kwargs)
        executor = AsyncSampleExecutor(self, sample_path, env_vars=env_vars, **kwargs)
        await executor.execute_async()
        await executor.validate_print_calls_by_llm_async()

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
        await executor.validate_print_calls_by_llm_async()

    @pytest.mark.parametrize(
        "sample_path",
        get_async_sample_paths(
            "models",
            samples_to_test=[
                "sample_models_basic_async.py",
            ],
        ),
    )
    @modelsServicePreparer()
    @SamplePathPasser()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_models_samples(self, sample_path: str, **kwargs) -> None:
        import secrets  # local import to avoid module-level dep

        env_vars = get_sample_env_vars(kwargs)
        # Foundry permanently reserves a `<name>/<version>` asset namespace even
        # after `models.delete`, so every live re-recording needs a unique name.
        # Sanitize back to a stable value in conftest so playback URLs match.
        suffix = secrets.token_hex(4) if self.is_live else "00000000"
        env_vars["MODEL_NAME"] = f"recsmplmdl{suffix}"
        env_vars["MODEL_VERSION"] = "1"
        executor = AsyncSampleExecutor(self, sample_path, env_vars=env_vars, **kwargs)
        await executor.execute_async()
        # `validate_print_calls_by_llm_async` is intentionally not called: see
        # the comment on the synchronous `test_models_samples` for details.

    @pytest.mark.parametrize(
        "sample_path",
        get_async_sample_paths(
            "datasets",
            samples_to_skip=[
                "sample_datasets_async.py",  # Skipped until re-enabled and recorded on Foundry endpoint that supports the new versioning schema
            ],
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
            await executor.validate_print_calls_by_llm_async()

    @pytest.mark.parametrize(
        "sample_path",
        get_async_sample_paths(
            "chat_completions",
            samples_to_skip=[],
        ),
    )
    @servicePreparer()
    @SamplePathPasser()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_chat_completions_samples(self, sample_path: str, **kwargs) -> None:
        env_vars = get_sample_env_vars(kwargs)
        executor = AsyncSampleExecutor(self, sample_path, env_vars=env_vars, **kwargs)
        await executor.execute_async()
        await executor.validate_print_calls_by_llm_async()

    @servicePreparer()
    @additionalSampleTests(
        [
            AdditionalSampleTestDetail(
                test_id="sample_create_hosted_agent_async",
                sample_filename="sample_create_hosted_agent_from_image_async.py",
                env_vars={},
            ),
            AdditionalSampleTestDetail(
                test_id="sample_create_hosted_agent_from_remote_build_async",
                sample_filename="sample_create_hosted_agent_from_code_async.py",
                env_vars={
                    "FOUNDRY_HOSTED_AGENT_REMOTE_BUILD": "true",
                    "ZIP_FILE_PATH": "tests/samples/assets/basic-agent.zip",
                },
            ),
            AdditionalSampleTestDetail(
                test_id="sample_create_hosted_agent_from_code_async",
                sample_filename="sample_create_hosted_agent_from_code_async.py",
                env_vars={
                    "FOUNDRY_HOSTED_AGENT_REMOTE_BUILD": "false",
                    "ZIP_FILE_PATH": "tests/samples/assets/basic-agent-prebuilt.zip",
                },
            ),
            AdditionalSampleTestDetail(
                test_id="sample_session_log_stream_async",
                sample_filename="sample_session_log_stream_async.py",
                env_vars={
                    "ZIP_FILE_PATH": "tests/samples/assets/basic-agent.zip",
                },
            ),
            AdditionalSampleTestDetail(
                test_id="sample_sessions_crud_async",
                sample_filename="sample_sessions_crud_async.py",
                env_vars={
                    "ZIP_FILE_PATH": "tests/samples/assets/basic-agent.zip",
                },
            ),
            AdditionalSampleTestDetail(
                test_id="sample_sessions_files_upload_download_async",
                sample_filename="sample_sessions_files_upload_download_async.py",
                env_vars={
                    "ZIP_FILE_PATH": "tests/samples/assets/basic-agent.zip",
                },
            ),
        ]
    )
    @pytest.mark.parametrize(
        "sample_path",
        get_async_sample_paths(
            "hosted_agents",
            samples_to_skip=[
                "sample_create_hosted_agent_from_image_async.py",  # Specified through AdditionalSampleTestDetail
                "sample_create_hosted_agent_from_code_async.py",  # Specified through AdditionalSampleTestDetail
                "sample_session_log_stream_async.py",  # Specified through AdditionalSampleTestDetail
                "sample_sessions_crud_async.py",  # Specified through AdditionalSampleTestDetail
                "sample_sessions_files_upload_download_async.py",  # Specified through AdditionalSampleTestDetail
            ],
        ),
    )
    @SamplePathPasser()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_hosted_agents_samples(self, sample_path: str, **kwargs) -> None:
        env_vars = get_sample_env_vars(kwargs)
        executor = AsyncSampleExecutor(self, sample_path, env_vars=env_vars, **kwargs)
        await executor.execute_async()
        await executor.validate_print_calls_by_llm_async()

    @additionalSampleTests(
        [
            AdditionalSampleTestDetail(
                test_id="sample_skills_upload_and_download_async",
                sample_filename="sample_skills_upload_and_download_async.py",
                env_vars={
                    "ZIP_FILE_PATH": "tests/samples/assets/team-status-update.zip",
                },
            ),
        ]
    )
    @pytest.mark.parametrize(
        "sample_path",
        get_async_sample_paths(
            "skills",
            samples_to_skip=[
                "sample_skills_upload_and_download_async.py",  # Specified through AdditionalSampleTestDetail
            ],
        ),
    )
    @servicePreparer()
    @SamplePathPasser()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_skills_samples(self, sample_path: str, **kwargs) -> None:
        env_vars = get_sample_env_vars(kwargs)
        executor = AsyncSampleExecutor(self, sample_path, env_vars=env_vars, **kwargs)
        await executor.execute_async()
        await executor.validate_print_calls_by_llm_async()

    @pytest.mark.parametrize(
        "sample_path",
        get_async_sample_paths(
            "toolboxes",
            samples_to_skip=[],
        ),
    )
    @servicePreparer()
    @SamplePathPasser()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_toolboxes_samples(self, sample_path: str, **kwargs) -> None:
        env_vars = get_sample_env_vars(kwargs)
        executor = AsyncSampleExecutor(self, sample_path, env_vars=env_vars, **kwargs)
        await executor.execute_async()
        await executor.validate_print_calls_by_llm_async()
