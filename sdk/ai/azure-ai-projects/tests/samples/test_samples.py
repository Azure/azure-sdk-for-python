# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed-------------------------
import csv, os, pytest, re, inspect, sys, json
import importlib.util
import unittest.mock as mock
from azure.core.exceptions import HttpResponseError
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy, RecordedTransport
from test_base import servicePreparer, patched_open_crlf_to_lf
from pytest import MonkeyPatch
from azure.ai.projects import AIProjectClient
from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient
from azure.identity import DefaultAzureCredential
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential
from functools import wraps
from typing import Callable, Optional, Literal
from pydantic import BaseModel


class SampleExecutor:
    """Decorator for executing sample files with proper environment setup and credential mocking."""

    def __init__(self, env_var_mapping_fn: Callable):
        """
        Initialize the SampleExecutor decorator.

        Args:
            env_var_mapping_fn: Function that returns the environment variable mapping
        """
        self.env_var_mapping_fn = env_var_mapping_fn

    def __call__(self, fn):
        """
        Wrap the test function to provide executor instance.

        Args:
            fn: The test function to wrap

        Returns:
            Wrapped function with executor injection
        """
        if inspect.iscoroutinefunction(fn):

            @wraps(fn)
            async def _async_wrapper(test_instance, sample_path: str, **kwargs):
                env_var_mapping = self.env_var_mapping_fn(test_instance)
                executor = _SampleExecutorInstance(test_instance, env_var_mapping, **kwargs)
                await fn(test_instance, sample_path, executor=executor, **kwargs)

            return _async_wrapper
        else:

            @wraps(fn)
            def _sync_wrapper(test_instance, sample_path: str, **kwargs):
                env_var_mapping = self.env_var_mapping_fn(test_instance)
                executor = _SampleExecutorInstance(test_instance, env_var_mapping, **kwargs)
                fn(test_instance, sample_path, executor=executor, **kwargs)

            return _sync_wrapper


class _SampleExecutorInstance:
    """Internal class for executing sample files with proper environment setup and credential mocking."""

    class TestReport(BaseModel):
        """Schema for validation test report."""

        model_config = {"extra": "forbid"}
        correct: bool
        reason: str

    def __init__(self, test_instance: "AzureRecordedTestCase", env_var_mapping: dict[str, str], **kwargs):
        self.test_instance = test_instance
        self.env_var_mapping = env_var_mapping
        self.kwargs = kwargs
        self.print_calls: list[str] = []
        self._original_print = print

    def _prepare_execution(self, sample_path: str):
        """Prepare for sample execution by setting up environment and module."""
        self.sample_path = sample_path

        # Prepare environment variables
        self.env_vars = {}
        for sample_var, test_var in self.env_var_mapping.items():
            value = self.kwargs.get(test_var, None)
            if value is not None:
                self.env_vars[sample_var] = value
        self.env_vars["AZURE_AI_MODEL_DEPLOYMENT_NAME"] = "gpt-4o"

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

    def execute(self, sample_path: str):
        """Execute a synchronous sample with proper mocking and environment setup."""
        self._prepare_execution(sample_path)

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

            self._validate_output()

    async def execute_async(self, sample_path: str):
        """Execute an asynchronous sample with proper mocking and environment setup."""
        self._prepare_execution(sample_path)

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
- HTTP error codes (4xx, 5xx)
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
        with (
            DefaultAzureCredential() as credential,
            AIProjectClient(endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"], credential=credential) as project_client,
            project_client.get_openai_client() as openai_client,
        ):
            response = openai_client.responses.create(**self._get_validation_request_params())
            test_report = json.loads(response.output_text)
            self._assert_validation_result(test_report)

    async def _validate_output_async(self):
        """Validate sample output using asynchronous OpenAI client."""
        async with (
            AsyncDefaultAzureCredential() as credential,
            AsyncAIProjectClient(
                endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"], credential=credential
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


def _get_tools_sample_paths():
    # Get the path to the samples folder
    current_dir = os.path.dirname(os.path.abspath(__file__))
    samples_folder_path = os.path.normpath(os.path.join(current_dir, os.pardir, os.pardir))
    tools_folder = os.path.join(samples_folder_path, "samples", "agents", "tools")

    tools_samples_to_skip = [
        "sample_agent_bing_custom_search.py",
        "sample_agent_bing_grounding.py",
        "sample_agent_browser_automation.py",
        "sample_agent_fabric.py",
        "sample_agent_mcp_with_project_connection.py",
        "sample_agent_memory_search.py",
        "sample_agent_openapi_with_project_connection.py",
        "sample_agent_to_agent.py",
    ]
    samples = []

    for filename in sorted(os.listdir(tools_folder)):
        # Only include .py files, exclude __pycache__ and utility files
        if "sample_" in filename and "_async" not in filename and filename not in tools_samples_to_skip:
            sample_path = os.path.join(tools_folder, filename)
            samples.append(pytest.param(sample_path, id=filename.replace(".py", "")))

    return samples


def _get_tools_sample_paths_async():
    # Get the path to the samples folder
    current_dir = os.path.dirname(os.path.abspath(__file__))
    samples_folder_path = os.path.normpath(os.path.join(current_dir, os.pardir, os.pardir))
    tools_folder = os.path.join(samples_folder_path, "samples", "agents", "tools")

    # Skip async samples that are not yet ready for testing
    tools_samples_to_skip = [
        "sample_agent_mcp_with_project_connection_async.py",
        "sample_agent_memory_search_async.py",
    ]
    samples = []

    for filename in sorted(os.listdir(tools_folder)):
        # Only include async .py files, exclude __pycache__ and utility files
        if "sample_" in filename and "_async" in filename and filename not in tools_samples_to_skip:
            sample_path = os.path.join(tools_folder, filename)
            samples.append(pytest.param(sample_path, id=filename.replace(".py", "")))

    return samples


def _get_tools_sample_environment_variables_map(self) -> dict[str, str]:
    return {
        "AZURE_AI_PROJECT_ENDPOINT": "azure_ai_projects_tests_project_endpoint",
        "AI_SEARCH_PROJECT_CONNECTION_ID": "azure_ai_projects_tests_ai_search_project_connection_id",
        "AI_SEARCH_INDEX_NAME": "azure_ai_projects_tests_ai_search_index_name",
        "AI_SEARCH_USER_INPUT": "azure_ai_projects_tests_ai_search_user_input",
        "SHAREPOINT_USER_INPUT": "azure_ai_projects_tests_sharepoint_user_input",
        "SHAREPOINT_PROJECT_CONNECTION_ID": "azure_ai_projects_tests_sharepoint_project_connection_id",
    }


class TestSamples(AzureRecordedTestCase):
    _samples_folder_path: str
    _results: dict[str, tuple[bool, str]]

    """
    Test class for running all samples in the `/sdk/ai/azure-ai-projects/samples` folder.

    To run this test:
    * 'cd' to the folder '/sdk/ai/azure-ai-projects' in your azure-sdk-for-python repo.
    * set AZURE_AI_PROJECT_ENDPOINT=<your-project-endpoint> - Define your Microsoft Foundry project endpoint used by the test.
    * set AZURE_AI_PROJECTS_CONSOLE_LOGGING=false - to make sure logging is not enabled in the test, to reduce console spew.
    * Uncomment the two lines that start with "@pytest.mark.skip" below.
    * Run:  pytest tests\\samples\\test_samples.py::TestSamples
    * Load the resulting report in Excel: tests\\samples\\samples_report.csv
    """

    @classmethod
    def setup_class(cls):
        current_path = os.path.abspath(__file__)
        cls._samples_folder_path = os.path.join(current_path, os.pardir, os.pardir, os.pardir)
        cls._results: dict[str, tuple[bool, str]] = {}

    @classmethod
    def teardown_class(cls):
        """
        Class-level teardown method that generates a report file named "samples_report.csv" after all tests have run.

        The report contains one line per sample run, with three columns:
            1. PASS or FAIL indicating the sample result.
            2. The name of the sample.
            3. The exception string summary if the sample failed, otherwise empty.

        The report is written to the same directory as this test file.
        """
        report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples_report.csv")
        with open(report_path, mode="w", newline="") as file:
            writer = csv.writer(file, quotechar='"', quoting=csv.QUOTE_ALL)  # Ensures proper quoting
            for test_name, (passed, exception_string) in cls._results.items():
                exception_message = f'"{exception_string.splitlines()[0]}"' if exception_string else ""
                writer.writerow([f"{'PASS' if passed else 'FAIL'}", test_name, exception_message])

    @classmethod
    def _set_env_vars(cls, sample_name: str, **kwargs):
        """
        Sets environment variables for a given sample run and prints them.

        Args:
            sample_name (str): The name of the sample being executed.
            **kwargs: Arbitrary keyword arguments representing environment variable names and their values.
        """

        print(f"\nRunning {sample_name} with environment variables: ", end="")
        for key, value in kwargs.items():
            if value:
                env_key = key.upper()
                os.environ[env_key] = value
                print(f"{env_key}={value} ", end="")
        print("\n")

    @classmethod
    def _run_sample(cls, sample_name: str) -> None:
        """
        Executes a synchronous sample file and records the result.

        Args:
            sample_name (str): The name of the sample file to execute.

        Raises:
            Exception: Re-raises any exception encountered during execution of the sample file.

        Side Effects:
            Updates the class-level _results dictionary with the execution status and error message (if any)
            for the given sample.
            Prints an error message to stdout if execution fails.
        """

        sample_path = os.path.normpath(os.path.join(TestSamples._samples_folder_path, sample_name))
        with open(sample_path) as f:
            code = f.read()
            try:
                exec(code)
            except HttpResponseError as exc:
                exception_message = f"{exc.status_code}, {exc.reason}, {str(exc)}"
                TestSamples._results[sample_name] = (False, exception_message)
                print(f"=================> Error running sample {sample_path}: {exception_message}")
                raise Exception from exc
            except Exception as exc:
                TestSamples._results[sample_name] = (False, str(exc))
                print(f"=================> Error running sample {sample_path}: {exc}")
                raise Exception from exc
            TestSamples._results[sample_name] = (True, "")

    @classmethod
    async def _run_sample_async(cls, sample_name: str) -> None:
        """
        Asynchronously runs a sample Python script specified by its file name.

        This method dynamically imports the sample module from the given file path,
        executes its `main()` coroutine, and records the result. If an exception occurs
        during execution, the error is logged and re-raised.

        Args:
            sample_name (str): The name of the sample Python file to run (relative to the samples folder).

        Raises:
            ImportError: If the sample module cannot be loaded.
            Exception: If an error occurs during the execution of the sample's `main()` coroutine.

        Side Effects:
            Updates the `_results` dictionary with the execution status and error message (if any).
            Prints error messages to the console if execution fails.
        """

        sample_path = os.path.normpath(os.path.join(TestSamples._samples_folder_path, sample_name))
        # Dynamically import the module from the given path
        module_name = os.path.splitext(os.path.basename(sample_path))[0]
        spec = importlib.util.spec_from_file_location(module_name, sample_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load module {module_name} from {sample_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # Await the main() coroutine defined in the sample
        try:
            await module.main()
        except HttpResponseError as exc:
            exception_message = f"{exc.status_code}, {exc.reason}, {str(exc)}"
            TestSamples._results[sample_name] = (False, exception_message)
            print(f"=================> Error running sample {sample_path}: {exception_message}")
            raise Exception from exc
        except Exception as exc:
            TestSamples._results[sample_name] = (False, str(exc))
            print(f"=================> Error running sample {sample_path}: {exc}")
            raise Exception from exc
        TestSamples._results[sample_name] = (True, "")

    @pytest.mark.parametrize(
        "sample_name, model_deployment_name, connection_name, data_folder",
        [
            ("samples\\agents\\sample_agents.py", "gpt-4o", "", ""),
            ("samples\\connections\\sample_connections.py", "", "connection1", ""),
            ("samples\\deployments\\sample_deployments.py", "DeepSeek-V3", "", ""),
            ("samples\\datasets\\sample_datasets.py", "", "balapvbyostoragecanary", "samples\\datasets\\data_folder"),
            (
                "samples\\datasets\\sample_datasets_download.py",
                "",
                "balapvbyostoragecanary",
                "samples\\datasets\\data_folder",
            ),
            ("samples\\indexes\\sample_indexes.py", "", "", ""),
            (
                "samples\\inference\\azure-ai-inference\\sample_chat_completions_with_azure_ai_inference_client.py",
                "Phi-4",
                "",
                "",
            ),
            (
                "samples\\inference\\azure-ai-inference\\sample_chat_completions_with_azure_ai_inference_client_and_azure_monitor_tracing.py",
                "Phi-4",
                "",
                "",
            ),
            (
                "samples\\inference\\azure-ai-inference\\sample_chat_completions_with_azure_ai_inference_client_and_console_tracing.py",
                "Phi-4",
                "",
                "",
            ),
            (
                "samples\\inference\\azure-openai\\sample_chat_completions_with_azure_openai_client.py",
                "gpt-4o",
                "connection1",
                "",
            ),
            (
                "samples\\inference\\azure-openai\\sample_responses_with_azure_openai_client.py",
                "gpt-4o",
                "connection1",
                "",
            ),
            (
                "samples\\inference\\azure-openai\\sample_chat_completions_with_azure_openai_client_and_azure_monitor_tracing.py",
                "gpt-4o",
                "",
                "",
            ),
            (
                "samples\\inference\\azure-openai\\sample_chat_completions_with_azure_openai_client_and_console_tracing.py",
                "gpt-4o",
                "",
                "",
            ),
            (
                "samples\\inference\\azure-ai-inference\\sample_image_embeddings_with_azure_ai_inference_client.py",
                "Cohere-embed-v3-english",
                "",
                "samples\\inference\\azure-ai-inference",
            ),
            (
                "samples\\inference\\azure-ai-inference\\sample_text_embeddings_with_azure_ai_inference_client.py",
                "text-embedding-3-large",
                "",
                "",
            ),
            ("samples\\telemetry\\sample_telemetry.py", "", "", ""),
        ],
    )
    @pytest.mark.skip(reason="This test should only run manually on your local machine, with live service calls.")
    def test_samples(
        self, sample_name: str, model_deployment_name: str, connection_name: str, data_folder: str
    ) -> None:
        """
        Run all the synchronous sample code in the samples folder. If a sample throws an exception, which for example
        happens when the service responds with an error, the test will fail.

        Before running this test, you need to define the following environment variables:
        1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the overview page of your
           Microsoft Foundry project.
        """

        self._set_env_vars(
            sample_name,
            **{
                "model_deployment_name": model_deployment_name,
                "connection_name": connection_name,
                "data_folder": data_folder,
            },
        )
        TestSamples._run_sample(sample_name)

    @pytest.mark.parametrize(
        "sample_name, model_deployment_name, connection_name, data_folder",
        [
            ("samples\\agents\\sample_agents_async.py", "gpt-4o", "", ""),
            ("samples\\connections\\sample_connections_async.py", "", "connection1", ""),
            (
                "samples\\datasets\\sample_datasets_async.py",
                "",
                "balapvbyostoragecanary",
                "samples\\datasets\\data_folder",
            ),
            ("samples\\deployments\\sample_deployments_async.py", "DeepSeek-V3", "", ""),
            ("samples\\indexes\\sample_indexes_async.py", "", "", ""),
            (
                "samples\\inference\\azure-ai-inference\\sample_chat_completions_with_azure_ai_inference_client_async.py",
                "Phi-4",
                "",
                "",
            ),
            (
                "samples\\inference\\azure-openai\\sample_chat_completions_with_azure_openai_client_async.py",
                "gpt-4o",
                "connection1",
                "",
            ),
            (
                "samples\\inference\\azure-openai\\sample_responses_with_azure_openai_client_async.py",
                "gpt-4o",
                "connection1",
                "",
            ),
            (
                "samples\\inference\\azure-ai-inference\\sample_image_embeddings_with_azure_ai_inference_client_async.py",
                "Cohere-embed-v3-english",
                "",
                "samples\\inference\\azure-ai-inference",
            ),
            (
                "samples\\inference\\azure-ai-inference\\sample_text_embeddings_with_azure_ai_inference_client_async.py",
                "text-embedding-3-large",
                "",
                "",
            ),
            ("samples\\telemetry\\sample_telemetry_async.py", "", "", ""),
        ],
    )
    @pytest.mark.skip(reason="This test should only run manually on your local machine, with live service calls.")
    async def test_samples_async(
        self, sample_name: str, model_deployment_name: str, connection_name: str, data_folder: str
    ) -> None:
        """
        Run all the asynchronous sample code in the samples folder. If a sample throws an exception, which for example
        happens when the service responds with an error, the test will fail.

        Before running this test, you need to define the following environment variables:
        1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the overview page of your
           Microsoft Foundry project.
        """

        self._set_env_vars(
            sample_name,
            **{
                "model_deployment_name": model_deployment_name,
                "connection_name": connection_name,
                "data_folder": data_folder,
            },
        )
        await TestSamples._run_sample_async(sample_name)

    @servicePreparer()
    @pytest.mark.parametrize("sample_path", _get_tools_sample_paths())
    @SamplePathPasser()
    @SampleExecutor(_get_tools_sample_environment_variables_map)
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_tools_samples(self, sample_path: str, executor: _SampleExecutorInstance, **kwargs) -> None:
        executor.execute(sample_path)

    @servicePreparer()
    @pytest.mark.parametrize("sample_path", _get_tools_sample_paths_async())
    @SamplePathPasser()
    @SampleExecutor(_get_tools_sample_environment_variables_map)
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_tools_samples_async(self, sample_path: str, executor: _SampleExecutorInstance, **kwargs) -> None:
        await executor.execute_async(sample_path)
