# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Shared base code for sample tests - sync dependencies only."""
import os
import sys
import json
import inspect
import importlib.util
import unittest.mock as mock
from typing import Optional
from pydantic import BaseModel
from pytest import MonkeyPatch


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

    def _get_validation_request_params(self) -> dict:
        """Get common parameters for validation request."""
        return {
            "model": "gpt-4o",
            "instructions": """We just run Python code and captured a Python array of print statements.
Validating the printed content to determine if correct or not:
Respond false if any entries show:
- Error messages or exception text
- Empty or null results where data is expected
- Malformed or corrupted data
- Timeout or connection errors
- Warning messages indicating failures
- Failure to retrieve or process data
- Statements saying documents/information didn't provide relevant data
- Statements saying unable to find/retrieve information
- Asking the user to specify, clarify, or provide more details
- Suggesting to use other tools or sources
- Asking follow-up questions to complete the task
- Indicating lack of knowledge or missing information
- Responses that defer answering or redirect the question
Respond with true only if the result provides a complete, substantive answer with actual data/information.
Always respond with `reason` indicating the reason for the response.""",
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

    def _execute_module(self, patched_open_fn):
        """Execute the module with environment setup and mocking."""
        if self.spec.loader is None:
            raise ImportError(f"Could not load module {self.spec.name} from {self.sample_path}")

        with (
            mock.patch("builtins.print", side_effect=self._capture_print),
            mock.patch("builtins.open", side_effect=patched_open_fn),
        ):
            self.spec.loader.exec_module(self.module)


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


def get_sample_paths(
    sub_folder: str,
    *,
    samples_to_skip: Optional[list[str]] = None,
    is_async: Optional[bool] = False,
) -> list:
    """Get list of sample paths for testing."""
    # Get the path to the samples folder
    current_dir = os.path.dirname(os.path.abspath(__file__))
    samples_folder_path = os.path.normpath(os.path.join(current_dir, os.pardir, os.pardir))
    target_folder = os.path.join(samples_folder_path, "samples", *sub_folder.split("/"))

    if not os.path.exists(target_folder):
        raise ValueError(f"Target folder does not exist: {target_folder}")

    print("Target folder for samples:", target_folder)
    print("is_async:", is_async)
    print("samples_to_skip:", samples_to_skip)
    # Discover all sync or async sample files in the folder
    all_files = [
        f
        for f in os.listdir(target_folder)
        if (
            f.startswith("sample_")
            and (f.endswith("_async.py") if is_async else (f.endswith(".py") and not f.endswith("_async.py")))
        )
    ]

    if samples_to_skip:
        files_to_test = [f for f in all_files if f not in samples_to_skip]
    else:
        files_to_test = all_files

    print(f"Running the following samples as test:\n{files_to_test}")

    # Create pytest.param objects
    import pytest

    samples = []
    for filename in sorted(files_to_test):
        sample_path = os.path.join(target_folder, filename)
        test_id = filename.replace(".py", "")
        samples.append(pytest.param(sample_path, id=test_id))

    return samples


def get_sample_environment_variables_map(operation_group: Optional[str] = None) -> dict[str, str]:
    """Get the mapping of sample environment variables to test environment variables.

    Args:
        operation_group: Optional operation group name (e.g., "agents") to scope the endpoint variable.

    Returns:
        Dictionary mapping sample env var names to test env var names.
    """
    return {
        "AZURE_AI_PROJECT_ENDPOINT": (
            "azure_ai_projects_tests_project_endpoint"
            if operation_group is None
            else f"azure_ai_projects_tests_{operation_group}_project_endpoint"
        ),
        "AZURE_AI_MODEL_DEPLOYMENT_NAME": "azure_ai_projects_tests_model_deployment_name",
        "IMAGE_GENERATION_MODEL_DEPLOYMENT_NAME": "azure_ai_projects_tests_image_generation_model_deployment_name",
        "AI_SEARCH_PROJECT_CONNECTION_ID": "azure_ai_projects_tests_ai_search_project_connection_id",
        "AI_SEARCH_INDEX_NAME": "azure_ai_projects_tests_ai_search_index_name",
        "AI_SEARCH_USER_INPUT": "azure_ai_projects_tests_ai_search_user_input",
        "SHAREPOINT_USER_INPUT": "azure_ai_projects_tests_sharepoint_user_input",
        "SHAREPOINT_PROJECT_CONNECTION_ID": "azure_ai_projects_tests_sharepoint_project_connection_id",
        "MEMORY_STORE_CHAT_MODEL_DEPLOYMENT_NAME": "azure_ai_projects_tests_memory_store_chat_model_deployment_name",
        "MEMORY_STORE_EMBEDDING_MODEL_DEPLOYMENT_NAME": "azure_ai_projects_tests_memory_store_embedding_model_deployment_name",
    }
