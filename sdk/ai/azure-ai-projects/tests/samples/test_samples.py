# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
from devtools_testutils import recorded_by_proxy, AzureRecordedTestCase, RecordedTransport
from test_base import servicePreparer
from sample_executor import (
    AdditionalSampleTestDetail,
    SyncSampleExecutor,
    additionalSampleTests,
    get_sample_paths,
    SamplePathPasser,
)
from test_samples_helpers import (
    agent_tools_instructions,
    agents_instructions,
    memories_instructions,
    get_sample_environment_variables_map,
)


class TestSamples(AzureRecordedTestCase):

    # To run this test with a specific sample, use:
    # pytest tests/samples/test_samples.py::TestSamples::test_agent_tools_samples[sample_agent_memory_search]
    @servicePreparer()
    @additionalSampleTests(
        [
            # TODO: Re-enable and record the following sample on Foundry endpoint that supports the new versioning schema before including it in the test run:
            # AdditionalSampleTestDetail(
            #     test_id="sample_agent_azure_function",
            #     sample_filename="sample_agent_azure_function.py",
            #     env_vars={
            #         "STORAGE_INPUT_QUEUE_NAME": "sanitized_input_queue_name",
            #         "STORAGE_OUTPUT_QUEUE_NAME": "sanitized_output_queue_name",
            #         "STORAGE_QUEUE_SERVICE_ENDPOINT": "sanitized_queue_service_endpoint",
            #     },
            # ),
        ]
    )
    @pytest.mark.parametrize(
        "sample_path",
        get_sample_paths(
            "agents/tools",
            samples_to_skip=[
                "sample_agent_azure_function.py",
                "sample_agent_computer_use.py",
                "sample_agent_browser_automation.py",
                "sample_agent_openapi.py",
            ],
        ),
    )
    @SamplePathPasser()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_agent_tools_samples(self, sample_path: str, **kwargs) -> None:
        env_var_mapping = get_sample_environment_variables_map(kwargs)
        executor = SyncSampleExecutor(self, sample_path, env_var_mapping=env_var_mapping, **kwargs)
        executor.execute()
        executor.validate_print_calls_by_llm(
            instructions=agent_tools_instructions,
            project_endpoint=kwargs["azure_ai_project_endpoint"],
            model=kwargs["azure_ai_model_deployment_name"],
        )

    @pytest.mark.parametrize(
        "sample_path",
        get_sample_paths(
            "memories",
            samples_to_skip=[],
        ),
    )
    @servicePreparer()
    @SamplePathPasser()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_memory_samples(self, sample_path: str, **kwargs) -> None:
        env_var_mapping = get_sample_environment_variables_map(kwargs)
        executor = SyncSampleExecutor(self, sample_path, env_var_mapping=env_var_mapping, **kwargs)
        executor.execute()
        executor.validate_print_calls_by_llm(
            instructions=memories_instructions,
            project_endpoint=kwargs["azure_ai_project_endpoint"],
            model=kwargs["azure_ai_model_deployment_name"],
        )

    @pytest.mark.parametrize(
        "sample_path",
        get_sample_paths(
            "agents",
            samples_to_skip=[],
        ),
    )
    @servicePreparer()
    @SamplePathPasser()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_agents_samples(self, sample_path: str, **kwargs) -> None:
        env_var_mapping = get_sample_environment_variables_map(kwargs)
        executor = SyncSampleExecutor(self, sample_path, env_var_mapping=env_var_mapping, **kwargs)
        executor.execute()
        executor.validate_print_calls_by_llm(
            instructions=agents_instructions,
            project_endpoint=kwargs["azure_ai_project_endpoint"],
            model=kwargs["azure_ai_model_deployment_name"],
        )
