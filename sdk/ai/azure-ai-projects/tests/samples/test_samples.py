# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import csv
import os
import pytest
import importlib.util
from azure.core.exceptions import HttpResponseError


class TestSamples:
    """
    Test class for running all samples in the `/sdk/ai/azure-ai-projects/samples` folder.

    To run this test:
    * 'cd' to the folder '/sdk/ai/azure-ai-projects' in your azure-sdk-for-python repo.
    * set PROJECT_ENDPOINT=<your-project-endpoint> - Define your Azure AI Foundry project endpoint used by the test.
    * set ENABLE_AZURE_AI_PROJECTS_CONSOLE_LOGGING=false - to make sure logging is not enabled in the test, to reduce console spew.
    * Uncomment the two lines that start with "@pytest.mark.skip" below.
    * Run:  pytest tests/samples/test_samples.py::TestSamples
    * Load the resulting report in Excel: tests/samples/samples_report.csv
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
            # ("samples\\evaluation\\sample_evaluations.py", "", "", ""),
            ("samples\\indexes\\sample_indexes.py", "", "", ""),
            ("samples\\inference\\sample_chat_completions_with_azure_ai_inference_client.py", "Phi-4", "", ""),
            (
                "samples\\inference\\sample_chat_completions_with_azure_ai_inference_client_and_azure_monitor_tracing.py",
                "Phi-4",
                "",
                "",
            ),
            (
                "samples\\inference\\sample_chat_completions_with_azure_ai_inference_client_and_console_tracing.py",
                "Phi-4",
                "",
                "",
            ),
            (
                "samples\\inference\\sample_chat_completions_with_azure_ai_inference_client_and_prompty_file.py",
                "Phi-4",
                "",
                "samples\\inference",
            ),
            (
                "samples\\inference\\sample_chat_completions_with_azure_ai_inference_client_and_prompt_string.py",
                "Phi-4",
                "",
                "",
            ),
            ("samples\\inference\\sample_chat_completions_with_azure_openai_client.py", "gpt-4o", "connection1", ""),
            (
                "samples\\inference\\sample_chat_completions_with_azure_openai_client_and_azure_monitor_tracing.py",
                "gpt-4o",
                "",
                "",
            ),
            (
                "samples\\inference\\sample_chat_completions_with_azure_openai_client_and_console_tracing.py",
                "gpt-4o",
                "",
                "",
            ),
            (
                "samples\\inference\\sample_image_embeddings_with_azure_ai_inference_client.py",
                "Cohere-embed-v3-english",
                "",
                "samples\\inference",
            ),
            (
                "samples\\inference\\sample_text_embeddings_with_azure_ai_inference_client.py",
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
        1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the overview page of your
           Azure AI Foundry project.
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
            # ("samples\\evaluation\\sample_evaluations_async.py", "", "", ""),
            ("samples\\indexes\\sample_indexes_async.py", "", "", ""),
            (
                "samples\\inference\\async_samples\\sample_chat_completions_with_azure_ai_inference_client_async.py",
                "Phi-4",
                "",
                "",
            ),
            (
                "samples\\inference\\async_samples\\sample_chat_completions_with_azure_openai_client_async.py",
                "gpt-4o",
                "connection1",
                "",
            ),
            (
                "samples\\inference\\async_samples\\sample_image_embeddings_with_azure_ai_inference_client_async.py",
                "Cohere-embed-v3-english",
                "",
                "samples\\inference\\async_samples",
            ),
            (
                "samples\\inference\\async_samples\\sample_text_embeddings_with_azure_ai_inference_client_async.py",
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
        1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the overview page of your
           Azure AI Foundry project.
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
