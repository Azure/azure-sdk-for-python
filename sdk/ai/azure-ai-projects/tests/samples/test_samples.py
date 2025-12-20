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
from azure.core.credentials import TokenCredential
from devtools_testutils.fake_credentials import FakeTokenCredential
from devtools_testutils import recorded_by_proxy, AzureRecordedTestCase, RecordedTransport
from azure.ai.projects import AIProjectClient
from pytest import MonkeyPatch
from test_base import servicePreparer
from sample_executor_helpers import (
    BaseSampleExecutor,
    SamplePathPasser,
    get_sample_paths,
    get_sample_environment_variables_map,
)


class SyncSampleExecutor(BaseSampleExecutor):
    """Synchronous sample executor that only uses sync credentials."""

    def __init__(self, test_instance, sample_path: str, env_var_mapping: dict[str, str], **kwargs):
        super().__init__(test_instance, sample_path, env_var_mapping, **kwargs)
        self.tokenCredential: TokenCredential | FakeTokenCredential | None = None

    def _get_mock_credential(self):
        """Get a mock credential that supports context manager protocol."""
        self.tokenCredential = self.test_instance.get_credential(AIProjectClient, is_async=False)
        patch_target = "azure.identity.DefaultAzureCredential"

        # Create a mock that returns a context manager wrapping the credential
        mock_credential_class = mock.MagicMock()
        mock_credential_class.return_value.__enter__ = mock.MagicMock(return_value=self.tokenCredential)
        mock_credential_class.return_value.__exit__ = mock.MagicMock(return_value=None)

        return mock.patch(patch_target, new=mock_credential_class)

    def execute(self, enable_llm_validation: bool = True, patched_open_fn=None):
        """Execute a synchronous sample with proper mocking and environment setup."""
        # Import patched_open_crlf_to_lf here to avoid circular import
        if patched_open_fn is None:
            from test_base import patched_open_crlf_to_lf

            patched_open_fn = patched_open_crlf_to_lf

        with (
            MonkeyPatch.context() as mp,
            self._get_mock_credential(),
        ):
            for var_name, var_value in self.env_vars.items():
                mp.setenv(var_name, var_value)

            self._execute_module(patched_open_fn)

            if enable_llm_validation:
                self._validate_output()

    def _validate_output(self):
        """Validate sample output using synchronous OpenAI client."""
        endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
        print(f"For validating console output, creating AIProjectClient with endpoint: {endpoint}")
        assert isinstance(self.tokenCredential, TokenCredential) or isinstance(
            self.tokenCredential, FakeTokenCredential
        )
        with (
            AIProjectClient(
                endpoint=endpoint, credential=cast(TokenCredential, self.tokenCredential)
            ) as project_client,
            project_client.get_openai_client() as openai_client,
        ):
            response = openai_client.responses.create(**self._get_validation_request_params())
            test_report = json.loads(response.output_text)
            self._assert_validation_result(test_report)


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
            is_async=False,
        ),
    )
    @SamplePathPasser()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_agent_tools_samples(self, sample_path: str, **kwargs) -> None:
        env_var_mapping = get_sample_environment_variables_map(operation_group="agents")
        executor = SyncSampleExecutor(self, sample_path, env_var_mapping, **kwargs)
        executor.execute()
