# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed-------------------------
import csv, os, pytest, re, inspect, sys
import importlib.util
import unittest.mock as mock
from azure.core.exceptions import HttpResponseError
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy, RecordedTransport
from test_base import servicePreparer, patched_open_crlf_to_lf
from pytest import MonkeyPatch
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from azure.identity import DefaultAzureCredential
from functools import wraps
from typing import Callable, Optional


class SampleExecutor:
    """Decorator for executing sample files with proper environment setup and credential mocking."""

    def __init__(self, env_var_mapping_fn: Callable):
        """
        Initialize the SampleExecutor decorator.
        
        Args:
            env_var_mapping_fn: Function that returns the environment variable mapping
        """
        self.env_var_mapping_fn = env_var_mapping_fn
        self.agent = None
        self.project_client = None
        self.credential = None

    def __enter__(self):
        """Context manager entry - creates agent for all tests."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - deletes agent after all tests."""
        if self.agent and self.project_client:
            try:
                self.project_client.agents.delete_version(
                    agent_name=self.agent.name,
                    agent_version=self.agent.version
                )
                print(f"Agent {self.agent.name} deleted")
            except Exception as e:
                print(f"Error deleting agent: {e}")
        
        if self.project_client:
            self.project_client.close()
        
        
        return False

    def setup_agent(self, test_instance: "AzureRecordedTestCase", endpoint: str, is_async: bool):
        """
        Setup agent using context managers.
        
        Args:
            test_instance: The test instance to get credentials from
            endpoint: The Azure AI project endpoint
        """
        # Get credential from test infrastructure
        credential = test_instance.get_credential(AIProjectClient, is_async=is_async)
        self.credential = credential
        
        # Create project client
        self.project_client = AIProjectClient(endpoint=endpoint, credential=credential)
        
        # Create agent
        self.agent = self.project_client.agents.create_version(
            agent_name="TestToolsAgent",
            definition=PromptAgentDefinition(
                model="gpt-4o",
                instructions="You are a helpful assistant for testing purposes.",
            ),
        )
        print(f"Agent {self.agent.name} (version {self.agent.version}) created")

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
                # Setup agent on first call
                if self.agent is None:
                    endpoint = kwargs.get("azure_ai_projects_tests_project_endpoint", "")
                    self.setup_agent(test_instance, endpoint, True)
                
                env_var_mapping = self.env_var_mapping_fn(test_instance)
                executor = _SampleExecutorInstance(
                    test_instance, 
                    env_var_mapping, 
                    self.agent,
                    **kwargs
                )
                await fn(test_instance, sample_path, executor=executor, **kwargs)
            
            return _async_wrapper
        else:
            @wraps(fn)
            def _sync_wrapper(test_instance, sample_path: str, **kwargs):
                # Setup agent on first call
                if self.agent is None:
                    endpoint = kwargs.get("azure_ai_projects_tests_project_endpoint", "")
                    self.setup_agent(test_instance, endpoint, False)
                
                env_var_mapping = self.env_var_mapping_fn(test_instance)
                executor = _SampleExecutorInstance(
                    test_instance, 
                    env_var_mapping,
                    self.agent,
                    **kwargs
                )
                fn(test_instance, sample_path, executor=executor, **kwargs)
            
            return _sync_wrapper


class _SampleExecutorInstance:
    """Internal class for executing sample files with proper environment setup and credential mocking."""

    def __init__(self, test_instance: "AzureRecordedTestCase", env_var_mapping: dict[str, str], agent, **kwargs):
        self.test_instance = test_instance
        self.env_var_mapping = env_var_mapping
        self.agent = agent
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

    def execute(self, sample_path: str):
        """Execute a synchronous sample with proper mocking and environment setup."""
        self._prepare_execution(sample_path)
        
        with (
            MonkeyPatch.context() as mp,
            mock.patch("builtins.print", side_effect=self._capture_print),
            mock.patch("builtins.open", side_effect=patched_open_crlf_to_lf),
            mock.patch("azure.identity.DefaultAzureCredential") as mock_credential,
        ):
            for var_name, var_value in self.env_vars.items():
                mp.setenv(var_name, var_value)
            credential_instance = self.test_instance.get_credential(AIProjectClient, is_async=False)
            credential_mock = mock.MagicMock()
            credential_mock.__enter__.return_value = credential_instance
            credential_mock.__exit__.return_value = False
            mock_credential.return_value = credential_mock
            if self.spec.loader is None:
                raise ImportError(f"Could not load module {self.spec.name} from {self.sample_path}")
            self.spec.loader.exec_module(self.module)

        self._validate_output()

    async def execute_async(self, sample_path: str):
        """Execute an asynchronous sample with proper mocking and environment setup."""
        self._prepare_execution(sample_path)
        
        with (
            MonkeyPatch.context() as mp,
            mock.patch("builtins.print", side_effect=self._capture_print),
            mock.patch("builtins.open", side_effect=patched_open_crlf_to_lf),
            mock.patch("azure.identity.aio.DefaultAzureCredential") as mock_credential,
        ):
            for var_name, var_value in self.env_vars.items():
                mp.setenv(var_name, var_value)

            # Create a mock credential that supports async context manager protocol
            credential_instance = self.test_instance.get_credential(AIProjectClient, is_async=True)
            credential_mock = mock.AsyncMock()
            credential_mock.__aenter__.return_value = credential_instance
            credential_mock.__aexit__.return_value = False
            mock_credential.return_value = credential_mock
            if self.spec.loader is None:
                raise ImportError(f"Could not load module {self.spec.name} from {self.sample_path}")
            self.spec.loader.exec_module(self.module)
            await self.module.main()

        self._validate_output()

    def _validate_output(self):
        """
        Validates:
        * Sample output contains the marker '==> Result: <content>'
        * If the sample includes a comment '# Print result (should contain "<keyword>")',
          the result must include that keyword (case-insensitive)
        * If no keyword is specified, the result must be at least 200 characters long
        """
        # Find content after ==> Result: marker in print_calls array
        result_line = None
        for call in self.print_calls:
            if call.startswith("==> Result:"):
                result_line = call
                break

        if not result_line:
            assert False, "Expected to find '==> Result:' in print calls."

        # Extract content after ==> Result:
        arrow_match = re.search(r"==> Result:(.*)", result_line, re.IGNORECASE | re.DOTALL)
        if not arrow_match:
            assert False, f"Expected to find '==> Result:' in line: {result_line}"

        content_after_arrow = arrow_match.group(1).strip()

        # Read the sample file to check for expected output comment
        with open(self.sample_path) as f:
            sample_code = f.read()

        # Verify pattern: # Print result (should contain '...') if exist
        match = re.search(r"# Print result \(should contain ['\"](.+?)['\"]\)", sample_code)
        if match:
            # Decode Unicode escape sequences like \u00b0F to actual characters
            expected_contain = match.group(1).encode().decode("unicode_escape")
            assert (
                expected_contain.lower() in content_after_arrow.lower()
            ), f"Expected to find '{expected_contain}' after '==> Result:', but got: {content_after_arrow}"
        else:
            result_len = len(content_after_arrow)
            assert result_len > 200, f"Expected 200 characters after '==> Result:', but got {result_len} characters"


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