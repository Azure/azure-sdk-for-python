# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import json
import unittest.mock as mock
from typing import cast
import pytest
from azure.core.credentials_async import AsyncTokenCredential
from devtools_testutils.fake_credentials_async import AsyncFakeCredential
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import AzureRecordedTestCase, RecordedTransport
from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient
from pytest import MonkeyPatch
from test_base import servicePreparer
from sample_executor_helpers import (
    BaseSampleExecutor,
    SamplePathPasser,
    get_sample_paths,
    get_sample_environment_variables_map,
)


class AsyncSampleExecutor(BaseSampleExecutor):
    """Asynchronous sample executor that uses async credentials."""

    def __init__(self, test_instance, sample_path: str, env_var_mapping: dict[str, str], **kwargs):
        super().__init__(test_instance, sample_path, env_var_mapping, **kwargs)
        self.tokenCredential: AsyncTokenCredential | AsyncFakeCredential | None = None

    def _get_mock_credential(self):
        """Get a mock credential that supports async context manager protocol."""
        self.tokenCredential = self.test_instance.get_credential(AsyncAIProjectClient, is_async=True)
        patch_target = "azure.identity.aio.DefaultAzureCredential"

        # Create a mock that returns an async context manager wrapping the credential
        mock_credential_class = mock.MagicMock()
        mock_credential_class.return_value.__aenter__ = mock.AsyncMock(return_value=self.tokenCredential)
        mock_credential_class.return_value.__aexit__ = mock.AsyncMock(return_value=None)

        return mock.patch(patch_target, new=mock_credential_class)

    async def execute_async(self, enable_llm_validation: bool = True, patched_open_fn=None):
        """Execute an asynchronous sample with proper mocking and environment setup."""
        # Import patched_open_crlf_to_lf here to avoid circular import
        if patched_open_fn is None:
            from test_base import patched_open_crlf_to_lf

            patched_open_fn = patched_open_crlf_to_lf

        with (
            MonkeyPatch.context() as mp,
            self._get_mock_credential(),
            mock.patch("builtins.print", side_effect=self._capture_print),
            mock.patch("builtins.open", side_effect=patched_open_fn),
        ):
            for var_name, var_value in self.env_vars.items():
                mp.setenv(var_name, var_value)

            self._execute_module()
            await self.module.main()

            if enable_llm_validation:
                await self._validate_output_async()

    def _execute_module(self):
        """Execute the module without applying patches (patches applied at caller level)."""
        if self.spec.loader is None:
            raise ImportError(f"Could not load module {self.spec.name} from {self.sample_path}")
        self.spec.loader.exec_module(self.module)

    async def _validate_output_async(self):
        """Validate sample output using asynchronous OpenAI client."""
        endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
        print(f"For validating console output, creating AIProjectClient with endpoint: {endpoint}")
        assert isinstance(self.tokenCredential, AsyncTokenCredential) or isinstance(
            self.tokenCredential, AsyncFakeCredential
        )
        async with (
            AsyncAIProjectClient(
                endpoint=endpoint, credential=cast(AsyncTokenCredential, self.tokenCredential)
            ) as project_client,
        ):
            async with project_client.get_openai_client() as openai_client:
                response = await openai_client.responses.create(**self._get_validation_request_params())
                test_report = json.loads(response.output_text)
                self._assert_validation_result(test_report)


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
