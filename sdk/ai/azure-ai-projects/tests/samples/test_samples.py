# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import pytest
import importlib.util


class TestSamples:

    @classmethod
    def setup_class(cls):
        current_path = os.path.abspath(__file__)
        cls._samples_folder_path = os.path.join(current_path, "..", "..", "..", "samples")
        cls._results: dict[str, bool] = {}
        cls._results_async: dict[str, bool] = {}

    @classmethod
    def teardown_class(cls):
        print("\n***********************************************************************")
        if len(cls._results) > 0:
            print("\n Samples results:")
            for result in cls._results.items():
                test_name, passed = result
                print(f" {'PASS' if passed else 'FAIL'}: {test_name}")
            print(
                f" {len(cls._results)} samples run. {sum(cls._results.values())} passed, {len(cls._results) - sum(cls._results.values())} failed."
            )
        if len(cls._results_async) > 0:
            print("\n Asynchronous samples results:")
            for result in cls._results_async.items():
                test_name, passed = result
                print(f" {'PASS' if passed else 'FAIL'}: {test_name}")
            print(
                f" {len(cls._results_async)} samples run. {sum(cls._results_async.values())} passed, {len(cls._results_async) - sum(cls._results_async.values())} failed."
            )
        print("\n***********************************************************************")

    @classmethod
    def _set_env_vars(cls, sample_name: str, **kwargs):
        print(f"\nRunning {sample_name} with environment variables: ", end="")
        for key, value in kwargs.items():
            if value:
                env_key = key.upper()
                os.environ[env_key] = value
                print(f"{env_key}={value} ", end="")
        print("\n")

    @classmethod
    def _run_sample(cls, sample_path: str) -> None:
        with open(sample_path) as f:
            code = f.read()
            exec(code)

    @classmethod
    async def _run_sample_async(cls, sample_path: str) -> None:
        # Dynamically import the module from the given path
        module_name = os.path.splitext(os.path.basename(sample_path))[0]
        spec = importlib.util.spec_from_file_location(module_name, sample_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load module {module_name} from {sample_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # Await the main() coroutine defined in the sample
        await module.main()

    @pytest.mark.skip(reason="This test should only run manually on your local machine, with live service calls.")
    @pytest.mark.parametrize(
        "sample_name, model_deployment_name, connection_name",
        [
            ("agents\\sample_agents.py", "gpt-4o", ""),
            ("connections\\sample_connections.py", "", "connection1"),
            ("deployments\\sample_deployments.py", "DeepSeek-V3", ""),
            ("datasets\\sample_datasets.py", "", ""),
            # ("evaluation\\sample_evaluations.py", "", ""),
            ("indexes\\sample_indexes.py", "", ""),
            ("inference\\sample_chat_completions_with_azure_ai_inference_client.py", "Phi-4", ""),
            (
                "inference\\sample_chat_completions_with_azure_ai_inference_client_and_azure_monitor_tracing.py",
                "Phi-4",
                "",
            ),
            ("inference\\sample_chat_completions_with_azure_ai_inference_client_and_console_tracing.py", "Phi-4", ""),
            ("inference\\sample_chat_completions_with_azure_ai_inference_client_and_prompty_file.py", "Phi-4", ""),
            ("inference\\sample_chat_completions_with_azure_ai_inference_client_and_prompt_string.py", "Phi-4", ""),
            ("inference\\sample_chat_completions_with_azure_openai_client.py", "gpt-4o", ""),
            ("inference\\sample_chat_completions_with_azure_openai_client_and_azure_monitor_tracing.py", "gpt-4o", ""),
            ("inference\\sample_chat_completions_with_azure_openai_client_and_console_tracing.py", "gpt-4o", ""),
            ("inference\\sample_image_embeddings_with_azure_ai_inference_client.py", "to-do-add-model", ""),
            ("inference\\sample_text_embeddings_with_azure_ai_inference_client.py", "text-embedding-3-large", ""),
            ("telemetry\\sample_telemetry.py", "", ""),
        ],
    )
    def test_samples(self, sample_name: str, model_deployment_name: str, connection_name: str) -> None:
        """
        Run all the synchronous sample code in the samples folder. If a sample throws an exception, which for example
        happens when the service responds with an error, the test will fail.

        Before running this test, you need to define the following environment variables:
        1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the overview page of your
           Azure AI Foundry project.
        """

        TestSamples._results[sample_name] = False
        self._set_env_vars(
            sample_name, **{"model_deployment_name": model_deployment_name, "connection_name": connection_name}
        )
        sample_path = os.path.normpath(os.path.join(TestSamples._samples_folder_path, sample_name))
        TestSamples._run_sample(sample_path)
        TestSamples._results[sample_name] = True

    @pytest.mark.skip(reason="This test should only run manually on your local machine, with live service calls.")
    @pytest.mark.parametrize(
        "sample_name, model_deployment_name, connection_name",
        [
            ("agents\\sample_agents_async.py", "", ""),
            ("connections\\sample_connections_async.py", "", "connection1"),
            ("datasets\\sample_datasets_async.py", "", ""),
            ("deployments\\sample_deployments_async.py", "DeepSeek-V3", ""),
            # ("evaluation\\sample_evaluations_async.py", "", ""),
            ("indexes\\sample_indexes_async.py", "", ""),
            ("inference\\async_samples\\sample_chat_completions_with_azure_ai_inference_client_async.py", "Phi-4", ""),
            ("inference\\async_samples\\sample_chat_completions_with_azure_openai_client_async.py", "gpt-4o", ""),
            (
                "inference\\async_samples\\sample_image_embeddings_with_azure_ai_inference_client_async.py",
                "to-do-add-model",
                "",
            ),
            (
                "inference\\async_samples\\sample_text_embeddings_with_azure_ai_inference_client_async.py",
                "text-embedding-3-large",
                "",
            ),
            ("telemetry\\sample_telemetry_async.py", "", ""),
        ],
    )
    async def test_samples_async(self, sample_name: str, model_deployment_name: str, connection_name: str) -> None:
        """
        Run all the asynchronous sample code in the samples folder. If a sample throws an exception, which for example
        happens when the service responds with an error, the test will fail.

        Before running this test, you need to define the following environment variables:
        1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the overview page of your
           Azure AI Foundry project.
        """

        TestSamples._results_async[sample_name] = False
        self._set_env_vars(
            sample_name, **{"model_deployment_name": model_deployment_name, "connection_name": connection_name}
        )
        sample_path = os.path.normpath(os.path.join(TestSamples._samples_folder_path, sample_name))
        await TestSamples._run_sample_async(sample_path)
        TestSamples._results_async[sample_name] = True
