# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os, pytest, inspect, sys, json
import importlib.util
import unittest.mock as mock
from typing import Union, cast, overload
from azure.core.credentials import TokenCredential
from azure.core.credentials_async import AsyncTokenCredential
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy, RecordedTransport
from test_base import servicePreparer, patched_open_crlf_to_lf
from pytest import MonkeyPatch
from azure.ai.projects import AIProjectClient
from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient
from pydantic import BaseModel


class SampleExecutor:
    """Helper class for executing sample files with proper environment setup and credential mocking."""

    class TestReport(BaseModel):
        """Schema for validation test report."""

        model_config = {"extra": "forbid"}
        correct: bool
        reason: str

    def __init__(
        self, test_instance: "AzureRecordedTestCase", sample_path: str, env_var_mapping: dict[str, str], **kwargs
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

    def _get_mock_credential(self, is_async: bool):
        """Get a mock credential that supports context manager protocol."""
        credential_instance = self.test_instance.get_credential(AIProjectClient, is_async=is_async)
        if is_async:
            patch_target = "azure.identity.aio.DefaultAzureCredential"
        else:
            patch_target = "azure.identity.DefaultAzureCredential"

        # Create a mock that returns a context manager wrapping the credential
        mock_credential_class = mock.MagicMock()
        mock_credential_class.return_value.__enter__ = mock.MagicMock(return_value=credential_instance)
        mock_credential_class.return_value.__exit__ = mock.MagicMock(return_value=None)
        mock_credential_class.return_value.__aenter__ = mock.AsyncMock(return_value=credential_instance)
        mock_credential_class.return_value.__aexit__ = mock.AsyncMock(return_value=None)

        return mock.patch(patch_target, new=mock_credential_class)

    def execute(self, enable_llm_validation: bool = True):
        """Execute a synchronous sample with proper mocking and environment setup."""

        with (
            MonkeyPatch.context() as mp,
            self._get_mock_credential(is_async=False),
        ):
            for var_name, var_value in self.env_vars.items():
                mp.setenv(var_name, var_value)

            with (
                mock.patch("builtins.print", side_effect=self._capture_print),
                mock.patch("builtins.open", side_effect=patched_open_crlf_to_lf),
            ):
                if self.spec.loader is None:
                    raise ImportError(f"Could not load module {self.spec.name} from {self.sample_path}")
                self.spec.loader.exec_module(self.module)

            if enable_llm_validation:
                self._validate_output()

    async def execute_async(self, enable_llm_validation: bool = True):
        """Execute an asynchronous sample with proper mocking and environment setup."""

        with (
            MonkeyPatch.context() as mp,
            self._get_mock_credential(is_async=True),
        ):
            for var_name, var_value in self.env_vars.items():
                mp.setenv(var_name, var_value)

            with (
                mock.patch("builtins.open", side_effect=patched_open_crlf_to_lf),
                mock.patch("builtins.print", side_effect=self._capture_print),
            ):
                if self.spec.loader is None:
                    raise ImportError(f"Could not load module {self.spec.name} from {self.sample_path}")
                self.spec.loader.exec_module(self.module)
                await self.module.main()

            if enable_llm_validation:
                await self._validate_output_async()

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

    def _validate_output(self):
        """Validate sample output using synchronous OpenAI client."""
        credential = self.test_instance.get_credential(AIProjectClient, is_async=False)
        with (
            AIProjectClient(
                endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"], credential=cast(TokenCredential, credential)
            ) as project_client,
            project_client.get_openai_client() as openai_client,
        ):
            response = openai_client.responses.create(**self._get_validation_request_params())
            test_report = json.loads(response.output_text)
            self._assert_validation_result(test_report)

    async def _validate_output_async(self):
        """Validate sample output using asynchronous OpenAI client."""
        credential = self.test_instance.get_credential(AIProjectClient, is_async=True)
        async with (
            AsyncAIProjectClient(
                endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"], credential=cast(AsyncTokenCredential, credential)
            ) as project_client,
        ):
            async with project_client.get_openai_client() as openai_client:
                response = await openai_client.responses.create(**self._get_validation_request_params())
                test_report = json.loads(response.output_text)
                self._assert_validation_result(test_report)


class SamplePathPasser:
    def __call__(self, fn):
        if inspect.iscoroutinefunction(fn):

            async def _wrapper_async(test_class, sample_path, **kwargs):
                return await fn(test_class, sample_path, **kwargs)

            return _wrapper_async
        else:

            def _wrapper_sync(test_class, sample_path, **kwargs):
                return fn(test_class, sample_path, **kwargs)

            return _wrapper_sync


@overload
def _get_sample_paths(sub_folder: str, *, samples_to_test: list[str]) -> list:
    """Get sample paths for testing (whitelist mode).

    Args:
        sub_folder: Relative path to the samples subfolder (e.g., "agents/tools")
        samples_to_test: Whitelist of sample filenames to include

    Returns:
        List of pytest.param objects with sample paths and test IDs
    """
    ...


@overload
def _get_sample_paths(sub_folder: str, *, samples_to_skip: list[str], is_async: bool) -> list:
    """Get sample paths for testing (blacklist mode).

    Args:
        sub_folder: Relative path to the samples subfolder (e.g., "agents/tools")
        samples_to_skip: Blacklist of sample filenames to exclude (auto-discovers all samples)
        is_async: Whether to filter for async samples (_async.py suffix)

    Returns:
        List of pytest.param objects with sample paths and test IDs
    """
    ...


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


class TestSamples(AzureRecordedTestCase):

    @servicePreparer()
    @pytest.mark.parametrize(
        "sample_path",
        _get_sample_paths(
            "agents/tools",
            samples_to_skip=[
                "sample_agent_bing_custom_search.py",
                "sample_agent_bing_grounding.py",
                "sample_agent_browser_automation.py",
                "sample_agent_fabric.py",
                "sample_agent_mcp_with_project_connection.py",
                "sample_agent_memory_search.py",
                "sample_agent_openapi_with_project_connection.py",
                "sample_agent_to_agent.py",
            ],
            is_async=False,
        ),
    )
    @SamplePathPasser()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_agent_tools_samples(self, sample_path: str, **kwargs) -> None:
        env_var_mapping = self._get_sample_environment_variables_map()
        executor = SampleExecutor(self, sample_path, env_var_mapping, **kwargs)
        executor.execute()

    @servicePreparer()
    @pytest.mark.parametrize(
        "sample_path",
        _get_sample_paths(
            "agents/tools",
            samples_to_skip=[
                "sample_agent_mcp_with_project_connection_async.py",
                "sample_agent_memory_search_async.py",
            ],
            is_async=True,
        ),
    )
    @SamplePathPasser()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_agent_tools_samples_async(self, sample_path: str, **kwargs) -> None:
        env_var_mapping = self._get_sample_environment_variables_map()
        executor = SampleExecutor(self, sample_path, env_var_mapping, **kwargs)
        await executor.execute_async()

    def _get_sample_environment_variables_map(self) -> dict[str, str]:
        return {
            "AZURE_AI_PROJECT_ENDPOINT": "azure_ai_projects_tests_project_endpoint",
            "AZURE_AI_MODEL_DEPLOYMENT_NAME": "azure_ai_projects_tests_model_deployment_name",
            "IMAGE_GENERATION_MODEL_DEPLOYMENT_NAME": "azure_ai_projects_tests_image_generation_model_deployment_name",
            "AI_SEARCH_PROJECT_CONNECTION_ID": "azure_ai_projects_tests_ai_search_project_connection_id",
            "AI_SEARCH_INDEX_NAME": "azure_ai_projects_tests_ai_search_index_name",
            "AI_SEARCH_USER_INPUT": "azure_ai_projects_tests_ai_search_user_input",
            "SHAREPOINT_USER_INPUT": "azure_ai_projects_tests_sharepoint_user_input",
            "SHAREPOINT_PROJECT_CONNECTION_ID": "azure_ai_projects_tests_sharepoint_project_connection_id",
        }
