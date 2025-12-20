# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Synchronous sample executor - no async/aio imports."""
import os
import json
import unittest.mock as mock
from typing import cast
from azure.core.credentials import TokenCredential
from devtools_testutils.fake_credentials import FakeTokenCredential
from azure.ai.projects import AIProjectClient
from pytest import MonkeyPatch
from test_samples_base import BaseSampleExecutor


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
