# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Shared base code for sample tests - sync dependencies only."""
import os
import sys
import pytest
import inspect
import importlib.util
from typing import overload, Union
from pydantic import BaseModel

import json
import unittest.mock as mock
from typing import cast
import pytest
from azure.core.credentials import TokenCredential
from azure.core.credentials_async import AsyncTokenCredential
from devtools_testutils.fake_credentials import FakeTokenCredential
from devtools_testutils.fake_credentials_async import AsyncFakeCredential
from devtools_testutils import recorded_by_proxy, AzureRecordedTestCase, RecordedTransport
from azure.ai.projects import AIProjectClient
from pytest import MonkeyPatch
from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient


@overload
def get_sample_paths(sub_folder: str, *, samples_to_test: list[str]) -> list:
    """Get sample paths for testing (whitelist mode).

    Args:
        sub_folder: Relative path to the samples subfolder (e.g., "agents/tools")
        samples_to_test: Whitelist of sample filenames to include

    Returns:
        List of pytest.param objects with sample paths and test IDs
    """
    ...


@overload
def get_sample_paths(sub_folder: str, *, samples_to_skip: list[str]) -> list:
    """Get sample paths for testing (blacklist mode).

    Args:
        sub_folder: Relative path to the samples subfolder (e.g., "agents/tools")
        samples_to_skip: Blacklist of sample filenames to exclude (auto-discovers all samples)

    Returns:
        List of pytest.param objects with sample paths and test IDs
    """
    ...


def get_sample_paths(
    sub_folder: str,
    *,
    samples_to_skip: Union[list[str], None] = None,
    samples_to_test: Union[list[str], None] = None,
) -> list:
    return _get_sample_paths(
        sub_folder, samples_to_skip=samples_to_skip, samples_to_test=samples_to_test, is_async=False
    )


@overload
def get_async_sample_paths(sub_folder: str, *, samples_to_test: list[str]) -> list:
    """Get async sample paths for testing (whitelist mode).

    Args:
        sub_folder: Relative path to the samples subfolder (e.g., "agents/tools")
        samples_to_test: Whitelist of sample filenames to include

    Returns:
        List of pytest.param objects with sample paths and test IDs
    """
    ...


@overload
def get_async_sample_paths(sub_folder: str, *, samples_to_skip: list[str]) -> list:
    """Get async sample paths for testing (blacklist mode).

    Args:
        sub_folder: Relative path to the samples subfolder (e.g., "agents/tools")
        samples_to_skip: Blacklist of sample filenames to exclude (auto-discovers all samples)
        is_async: Whether to filter for async samples (_async.py suffix)

    Returns:
        List of pytest.param objects with sample paths and test IDs
    """
    ...


def get_async_sample_paths(
    sub_folder: str,
    *,
    samples_to_skip: Union[list[str], None] = None,
    samples_to_test: Union[list[str], None] = None,
) -> list:
    return _get_sample_paths(
        sub_folder, samples_to_skip=samples_to_skip, samples_to_test=samples_to_test, is_async=True
    )


def _get_sample_paths(
    sub_folder: str,
    *,
    samples_to_skip: Union[list[str], None] = None,
    is_async: Union[bool, None] = None,
    samples_to_test: Union[list[str], None] = None,
) -> list:
    # Get the path to the samples folder
    current_dir = os.path.dirname(os.path.abspath(__file__))
    samples_folder_path = os.path.normpath(os.path.join(current_dir, os.pardir, os.pardir))
    target_folder = os.path.join(samples_folder_path, "samples", *sub_folder.split("/"))

    if not os.path.exists(target_folder):
        raise ValueError(f"Target folder does not exist: {target_folder}")

    # Discover all sample files in the folder
    all_files = [f for f in os.listdir(target_folder) if f.startswith("sample_") and f.endswith(".py")]

    # Filter by async suffix only when using samples_to_skip
    if samples_to_skip is not None and is_async is not None:
        if is_async:
            all_files = [f for f in all_files if f.endswith("_async.py")]
        else:
            all_files = [f for f in all_files if not f.endswith("_async.py")]

    # Apply whitelist or blacklist
    if samples_to_test is not None:
        files_to_test = [f for f in all_files if f in samples_to_test]
    else:  # samples_to_skip is not None
        assert samples_to_skip is not None
        files_to_test = [f for f in all_files if f not in samples_to_skip]

    # Create pytest.param objects
    samples = []
    for filename in sorted(files_to_test):
        sample_path = os.path.join(target_folder, filename)
        test_id = filename.replace(".py", "")
        samples.append(pytest.param(sample_path, id=test_id))

    return samples


class BaseSampleExecutor:
    """Base helper class for executing sample files with proper environment setup.

    This class contains all shared logic that doesn't require async/aio imports.
    Subclasses implement sync/async specific credential and execution logic.
    """

    class TestReport(BaseModel):
        """Schema for validation test report."""

        model_config = {"extra": "forbid"}
        correct: bool
        reason: str

    def __init__(self, test_instance, sample_path: str, env_var_mapping: dict[str, str], **kwargs):
        self.test_instance = test_instance
        self.sample_path = sample_path
        self.print_calls: list[str] = []
        self._original_print = print

        # Prepare environment variables
        self.env_vars = {}
        for sample_var, test_var in env_var_mapping.items():
            value = kwargs.pop(test_var, None)
            if value is not None:
                self.env_vars[sample_var] = value

        # Add the sample's directory to sys.path so it can import local modules
        self.sample_dir = os.path.dirname(sample_path)
        if self.sample_dir not in sys.path:
            sys.path.insert(0, self.sample_dir)

        # Create module spec for dynamic import
        module_name = os.path.splitext(os.path.basename(self.sample_path))[0]
        spec = importlib.util.spec_from_file_location(module_name, self.sample_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load module {module_name} from {self.sample_path}")

        self.module = importlib.util.module_from_spec(spec)
        self.spec = spec

    def _capture_print(self, *args, **kwargs):
        """Capture print calls while still outputting to console."""
        self.print_calls.append(" ".join(str(arg) for arg in args))
        self._original_print(*args, **kwargs)

    def _get_validation_request_params(self, instructions: str, model: str = "gpt-4o") -> dict:
        """Get common parameters for validation request."""
        return {
            "model": model,
            "instructions": instructions,
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "TestReport",
                    "schema": self.TestReport.model_json_schema(),
                }
            },
            # The input field is sanitized in recordings (see conftest.py) by matching the unique prefix
            # "print contents array = ". This allows sample print statements to change without breaking playback.
            # The instructions field is preserved as-is in recordings. If you modify the instructions,
            # you must re-record the tests.
            "input": f"print contents array = {self.print_calls}",
        }

    def _assert_validation_result(self, test_report: dict) -> None:
        """Assert validation result and print reason."""
        if not test_report["correct"]:
            # Write print statements to log file in temp folder for debugging
            import tempfile
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = os.path.join(tempfile.gettempdir(), f"sample_validation_error_{timestamp}.log")
            with open(log_file, "w") as f:
                f.write(f"Sample: {self.sample_path}\n")
                f.write(f"Validation Error: {test_report['reason']}\n\n")
                f.write("Print Statements:\n")
                f.write("=" * 80 + "\n")
                for i, print_call in enumerate(self.print_calls, 1):
                    f.write(f"{i}. {print_call}\n")
            print(f"\nValidation failed! Print statements logged to: {log_file}")
        assert test_report["correct"], f"Error is identified: {test_report['reason']}"
        print(f"Reason: {test_report['reason']}")


class SamplePathPasser:
    """Decorator for passing sample path to test functions."""

    def __call__(self, fn):
        if inspect.iscoroutinefunction(fn):

            async def _wrapper_async(test_class, sample_path, **kwargs):
                return await fn(test_class, sample_path, **kwargs)

            return _wrapper_async
        else:

            def _wrapper_sync(test_class, sample_path, **kwargs):
                return fn(test_class, sample_path, **kwargs)

            return _wrapper_sync


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

    def execute(self):
        """Execute a synchronous sample with proper mocking and environment setup."""
        from test_base import patched_open_crlf_to_lf

        with (
            MonkeyPatch.context() as mp,
            self._get_mock_credential(),
        ):
            for var_name, var_value in self.env_vars.items():
                mp.setenv(var_name, var_value)
            if self.spec.loader is None:
                raise ImportError(f"Could not load module {self.spec.name} from {self.sample_path}")

            with (
                mock.patch("builtins.print", side_effect=self._capture_print),
                mock.patch("builtins.open", side_effect=patched_open_crlf_to_lf),
            ):
                self.spec.loader.exec_module(self.module)

    def validate_print_calls_by_llm(
        self,
        *,
        instructions: str,
        project_endpoint: str,
        model: str = "gpt-4o",
    ):
        """Validate captured print output using synchronous OpenAI client."""
        if not instructions or not instructions.strip():
            raise ValueError("instructions must be a non-empty string")
        if not project_endpoint:
            raise ValueError("project_endpoint must be provided")
        endpoint = project_endpoint
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
            response = openai_client.responses.create(**self._get_validation_request_params(instructions, model=model))
            test_report = json.loads(response.output_text)
            self._assert_validation_result(test_report)


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

    async def execute_async(self):
        """Execute an asynchronous sample with proper mocking and environment setup."""
        from test_base import patched_open_crlf_to_lf

        with (
            MonkeyPatch.context() as mp,
            self._get_mock_credential(),
            mock.patch("builtins.print", side_effect=self._capture_print),
            mock.patch("builtins.open", side_effect=patched_open_crlf_to_lf),
        ):
            for var_name, var_value in self.env_vars.items():
                mp.setenv(var_name, var_value)
            if self.spec.loader is None:
                raise ImportError(f"Could not load module {self.spec.name} from {self.sample_path}")
            self.spec.loader.exec_module(self.module)
            await self.module.main()

    async def validate_print_calls_by_llm(
        self,
        *,
        instructions: str,
        project_endpoint: str,
        model: str = "gpt-4o",
    ):
        """Validate captured print output using asynchronous OpenAI client."""
        if not instructions or not instructions.strip():
            raise ValueError("instructions must be a non-empty string")
        if not project_endpoint:
            raise ValueError("project_endpoint must be provided")
        endpoint = project_endpoint
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
                response = await openai_client.responses.create(
                    **self._get_validation_request_params(instructions, model=model)
                )
                test_report = json.loads(response.output_text)
                self._assert_validation_result(test_report)
