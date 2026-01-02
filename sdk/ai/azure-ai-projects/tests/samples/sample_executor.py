# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Shared base code for sample tests - sync dependencies only."""
import os
import sys
import re
import pytest
import inspect
import importlib.util
import functools
from dataclasses import dataclass, field
from typing import Callable, Optional, Union, overload
from pydantic import BaseModel

import json
import unittest.mock as mock
from typing import cast
from azure.core.credentials import TokenCredential
from azure.core.credentials_async import AsyncTokenCredential
from devtools_testutils.fake_credentials import FakeTokenCredential
from devtools_testutils.fake_credentials_async import AsyncFakeCredential
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

    def __init__(
        self,
        test_instance,
        sample_path: str,
        env_var_mapping: dict[str, str],
        **kwargs,
    ):
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

        # Any remaining ALL_CAPS string kwargs are treated as env vars for the sample.
        # This supports decorators/tests passing env-var overrides via **kwargs.
        env_var_overrides: dict[str, str] = {}
        for key, value in list(kwargs.items()):
            if isinstance(key, str) and key.isupper() and isinstance(value, str):
                env_var_overrides[key] = value
                kwargs.pop(key, None)
        if env_var_overrides:
            # Allow overrides to win over mapped ones if needed.
            self.env_vars.update(env_var_overrides)

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

            @functools.wraps(fn)
            async def _wrapper_async(test_class, sample_path, **kwargs):
                return await fn(test_class, sample_path, **kwargs)

            # Explicitly set the signature to avoid pytest issues when wrapped function (e.g. from recorded_by_proxy)
            # hides the original signature.
            setattr(_wrapper_async, "__signature__", inspect.signature(_wrapper_async, follow_wrapped=False))
            return _wrapper_async
        else:

            @functools.wraps(fn)
            def _wrapper_sync(test_class, sample_path, **kwargs):
                return fn(test_class, sample_path, **kwargs)

            # Explicitly set the signature to avoid pytest issues when wrapped function (e.g. from recorded_by_proxy)
            # hides the original signature.
            setattr(_wrapper_sync, "__signature__", inspect.signature(_wrapper_sync, follow_wrapped=False))
            return _wrapper_sync


class SyncSampleExecutor(BaseSampleExecutor):
    """Synchronous sample executor that only uses sync credentials."""

    def __init__(self, test_instance, sample_path: str, env_var_mapping: dict[str, str], **kwargs):
        super().__init__(test_instance, sample_path, env_var_mapping, **kwargs)
        self.tokenCredential: Optional[TokenCredential | FakeTokenCredential] = None

    def _get_mock_credential(self):
        """Get a mock credential that supports context manager protocol."""
        self.tokenCredential = self.test_instance.get_credential(AIProjectClient, is_async=False)
        patch_target = "azure.identity.DefaultAzureCredential"

        # Create a mock that returns a context manager wrapping the credential
        mock_credential_class = mock.MagicMock()
        mock_credential_class.return_value.__enter__ = mock.MagicMock(return_value=self.tokenCredential)
        mock_credential_class.return_value.__exit__ = mock.MagicMock(return_value=None)

        return mock.patch(patch_target, new=mock_credential_class)

    def execute(self, patched_open_fn=None):
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
            if self.spec.loader is None:
                raise ImportError(f"Could not load module {self.spec.name} from {self.sample_path}")

            with (
                mock.patch("builtins.print", side_effect=self._capture_print),
                mock.patch("builtins.open", side_effect=patched_open_fn),
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
        self.tokenCredential: Optional[AsyncTokenCredential | AsyncFakeCredential] = None

    def _get_mock_credential(self):
        """Get a mock credential that supports async context manager protocol."""
        self.tokenCredential = self.test_instance.get_credential(AsyncAIProjectClient, is_async=True)
        patch_target = "azure.identity.aio.DefaultAzureCredential"

        # Create a mock that returns an async context manager wrapping the credential
        mock_credential_class = mock.MagicMock()
        mock_credential_class.return_value.__aenter__ = mock.AsyncMock(return_value=self.tokenCredential)
        mock_credential_class.return_value.__aexit__ = mock.AsyncMock(return_value=None)

        return mock.patch(patch_target, new=mock_credential_class)

    async def execute_async(self, patched_open_fn=None):
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
            if self.spec.loader is None:
                raise ImportError(f"Could not load module {self.spec.name} from {self.sample_path}")
            self.spec.loader.exec_module(self.module)
            await self.module.main()

    async def validate_print_calls_by_llm_async(
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
            project_client.get_openai_client() as openai_client,
        ):
            response = await openai_client.responses.create(
                **self._get_validation_request_params(instructions, model=model)
            )
            test_report = json.loads(response.output_text)
            self._assert_validation_result(test_report)


def _is_live_mode() -> bool:
    return os.environ.get("AZURE_TEST_RUN_LIVE") == "true"


def _normalize_sample_filename(sample_file: str) -> str:
    return os.path.basename(sample_file)


def _resolve_additional_env_vars(
    *,
    sample_path: str,
    playback_values: dict[str, str],
) -> dict[str, str]:
    sample_filename = os.path.basename(sample_path)

    resolved: dict[str, str] = {}
    if _is_live_mode():
        for env_key, _ in playback_values.items():
            live_value = os.environ.get(env_key)
            if not live_value:
                raise ValueError(
                    f"Missing required environment variable '{env_key}' for live recording of sample '{sample_filename}'. "
                    "Either set it in your environment/.env file or run in playback mode."
                )
            resolved[env_key] = live_value
    else:
        resolved.update(playback_values)

    return resolved


def _register_env_var_sanitizers(
    *,
    resolved_env_vars: dict[str, str],
    playback_values: dict[str, str],
) -> None:
    """Register function-scoped sanitizers to replace live env-var values with playback values."""
    if not _is_live_mode():
        return

    from devtools_testutils import add_general_string_sanitizer

    for env_key, live_value in resolved_env_vars.items():
        playback_value = playback_values.get(env_key)
        if not playback_value:
            continue
        if live_value == playback_value:
            continue

        add_general_string_sanitizer(function_scoped=True, target=live_value, value=playback_value)


@dataclass(init=False)
class AdditionalSampleTestDetail:
    """Configuration for adding an additional parametrized test case for a specific sample.

    In live mode (AZURE_TEST_RUN_LIVE=true), the values for keys in `env_vars` are read from the
    environment and then sanitized to the provided playback values.

    In playback mode, keys in `env_vars` are set to the provided playback values.
    """

    sample_filename: str
    env_vars: dict[str, str]
    _test_id: Optional[str] = field(default=None, repr=False)

    def __init__(
        self,
        *,
        sample_filename: str,
        env_vars: dict[str, str],
        test_id: Optional[str] = None,
    ) -> None:
        self.sample_filename = sample_filename
        self.env_vars = env_vars
        self._test_id = test_id

    @property
    def test_id(self) -> str:
        if self._test_id is None:
            sample_stem = os.path.splitext(os.path.basename(self.sample_filename))[0]
            keys_suffix = ",".join(sorted(self.env_vars.keys()))
            self._test_id = f"{sample_stem}-[{keys_suffix}]"
        return self._test_id

    @test_id.setter
    def test_id(self, value: str) -> None:
        self._test_id = value


def additionalSampleTests(additional_tests: list[AdditionalSampleTestDetail]):
    """Decorator factory that adds additional test cases per sample for record/playback.

    Args:
        additional_tests: List of `AdditionalSampleTestDetail` items.
            - In live mode (AZURE_TEST_RUN_LIVE=true): reads actual values from the environment for ENV_KEY,
              and registers function-scoped sanitizers to replace them with the provided playback values.
            - In playback mode: sets ENV_KEY to the provided playback value.

    The decorator also appends env-var keys to the pytest id for the matching sample.
    """

    # Allow multiple env-var sets per sample (e.g. same sample file listed multiple times)
    env_var_sets_by_sample: dict[str, list[AdditionalSampleTestDetail]] = {}
    for item in additional_tests:
        key = _normalize_sample_filename(item.sample_filename)
        env_var_sets_by_sample.setdefault(key, []).append(item)

    # Mapping from param-id (request.node.callspec.id) -> playback values dict.
    # Populated when we expand parametrize ids.
    playback_values_by_param_id: dict[str, dict[str, str]] = {}

    def _decorator(fn):
        # Attach configuration and storage to the function for pytest_generate_tests to use
        fn._additional_tests_config = env_var_sets_by_sample
        fn._playback_values = playback_values_by_param_id

        # Also try to run the logic immediately if marks are present (backward compatibility)
        _expand_sample_tests(fn, env_var_sets_by_sample, playback_values_by_param_id)

        # Inject pytest_generate_tests into the module of the decorated function
        # This avoids modifying conftest.py or the test file directly
        module = sys.modules.get(fn.__module__)
        if module:
            if not hasattr(module, "pytest_generate_tests"):
                # Define the hook if it doesn't exist
                def pytest_generate_tests(metafunc):
                    process_additional_sample_tests(metafunc)

                setattr(module, "pytest_generate_tests", pytest_generate_tests)
            else:
                # If it exists, wrap it to include our logic
                original_hook = getattr(module, "pytest_generate_tests")

                # Check if we already wrapped it to avoid infinite recursion or double wrapping
                if not getattr(original_hook, "_is_wrapped_additional_sample_tests", False):

                    @functools.wraps(original_hook)
                    def wrapped_pytest_generate_tests(metafunc):
                        process_additional_sample_tests(metafunc)
                        original_hook(metafunc)

                    setattr(wrapped_pytest_generate_tests, "_is_wrapped_additional_sample_tests", True)
                    setattr(module, "pytest_generate_tests", wrapped_pytest_generate_tests)

        def _inject_env_vars(*, sample_path: str, kwargs: dict) -> None:
            # Determine which env-var set applies for this specific parametrized case.
            # Can't rely on the `request` fixture here because outer decorators may hide it from pytest.
            current_test = os.environ.get("PYTEST_CURRENT_TEST", "")
            nodeid = current_test.split(" ")[0]  # drop " (call)" / " (setup)" / etc.

            # Capture everything between the first '[' and the last ']' in the nodeid.
            # This works even if the callspec id itself contains nested brackets like base_id[ENV1|ENV2].
            match = re.search(r"\[(?P<id>.*)\]", nodeid)
            case_id = match.group("id") if match else None
            playback_values = playback_values_by_param_id.get(case_id) if case_id else None

            if not playback_values:
                return

            resolved = _resolve_additional_env_vars(sample_path=sample_path, playback_values=playback_values)
            if not resolved:
                return

            _register_env_var_sanitizers(resolved_env_vars=resolved, playback_values=playback_values)
            for env_key, env_value in resolved.items():
                kwargs.setdefault(env_key, env_value)

        if inspect.iscoroutinefunction(fn):

            @functools.wraps(fn)
            async def _wrapper_async(test_class, sample_path: str, *args, **kwargs):
                _inject_env_vars(sample_path=sample_path, kwargs=kwargs)
                return await fn(test_class, sample_path, *args, **kwargs)

            return _wrapper_async

        @functools.wraps(fn)
        def _wrapper_sync(test_class, sample_path: str, *args, **kwargs):
            _inject_env_vars(sample_path=sample_path, kwargs=kwargs)
            return fn(test_class, sample_path, *args, **kwargs)

        return _wrapper_sync

    return _decorator


def _expand_sample_tests(
    fn: Callable,
    env_var_sets_by_sample: dict[str, list[AdditionalSampleTestDetail]],
    playback_values_by_param_id: dict[str, dict[str, str]],
) -> None:
    """Helper to expand sample tests, used by decorator and pytest_generate_tests."""
    marks = getattr(fn, "pytestmark", [])
    for mark in marks:
        if getattr(mark, "name", None) != "parametrize":
            continue
        if not getattr(mark, "args", None) or len(mark.args) < 2:
            continue

        def _split_argnames(argnames) -> list[str]:
            if isinstance(argnames, str):
                return [a.strip() for a in argnames.split(",") if a.strip()]
            try:
                return list(argnames)
            except TypeError:
                return [str(argnames)]

        argnames = _split_argnames(mark.args[0])
        if "sample_path" not in argnames:
            continue
        sample_path_index = argnames.index("sample_path")
        argvalues = mark.args[1]
        if not isinstance(argvalues, list):
            continue

        expanded: list = []
        inferred_sample_dir: Optional[str] = None
        # template_values stores the values for the test parameters from the first valid parameter set.
        # Examples:
        # - ("path/to/sample.py",)
        template_values: Optional[tuple[str]] = None
        # template_marks stores pytest marks (e.g., pytest.mark.skip) from the first valid parameter set.
        # Examples:
        # - (pytest.mark.skip(reason="Not ready"),)
        # - (pytest.mark.xfail,)
        # - (pytest.mark.slow, pytest.mark.windows_only)
        template_marks: tuple = ()
        seen_sample_filenames: set[str] = set()

        for parameter_set in list(argvalues):
            values = getattr(parameter_set, "values", None)
            if values is None:
                continue

            if template_values is None:
                if isinstance(values, tuple):
                    template_values = values
                elif isinstance(values, list):
                    template_values = tuple(values)

                if template_values is not None:
                    template_marks = tuple(getattr(parameter_set, "marks", ()))

            expanded.append(parameter_set)  # baseline / original

            if not isinstance(values, (list, tuple)):
                continue
            if sample_path_index >= len(values):
                continue

            sample_path = values[sample_path_index]

            sample_filename = os.path.basename(str(sample_path))
            seen_sample_filenames.add(sample_filename)

            if inferred_sample_dir is None:
                inferred_sample_dir = os.path.dirname(str(sample_path))

            additional_details = env_var_sets_by_sample.get(sample_filename)
            if not additional_details:
                continue

            marks_for_param = getattr(parameter_set, "marks", ())
            for detail in additional_details:
                new_id = detail.test_id

                if new_id in playback_values_by_param_id:
                    # Skip if already added (idempotency for pytest_generate_tests)
                    continue
                expanded.append(pytest.param(*values, marks=marks_for_param, id=new_id))
                playback_values_by_param_id[new_id] = detail.env_vars

        # If a sample was excluded from discovery (e.g., via samples_to_skip), it won't appear in argvalues.
        # In that case, still synthesize *variant-only* cases for any configured env-var sets.
        if inferred_sample_dir and template_values is not None:
            for sample_filename, playback_sets in env_var_sets_by_sample.items():
                if sample_filename in seen_sample_filenames:
                    continue

                synthetic_sample_path = os.path.join(inferred_sample_dir, sample_filename)
                synthetic_values = list(template_values)
                synthetic_values[sample_path_index] = synthetic_sample_path

                for detail in playback_sets:
                    new_id = detail.test_id

                    if new_id in playback_values_by_param_id:
                        continue
                    expanded.append(pytest.param(*synthetic_values, marks=template_marks, id=new_id))
                    playback_values_by_param_id[new_id] = detail.env_vars

        # Keep a stable, deterministic order for test ids.
        expanded.sort(key=lambda p: str(getattr(p, "id", "") or ""))

        # Mutate the existing list in-place so pytest sees the expanded cases.
        argvalues[:] = expanded


def process_additional_sample_tests(metafunc: pytest.Metafunc) -> None:
    """Hook to be called from pytest_generate_tests to process additional sample tests."""
    fn = metafunc.function
    env_var_sets_by_sample = getattr(fn, "_additional_tests_config", None)
    playback_values_by_param_id = getattr(fn, "_playback_values", None)

    if env_var_sets_by_sample and playback_values_by_param_id is not None:
        _expand_sample_tests(fn, env_var_sets_by_sample, playback_values_by_param_id)
