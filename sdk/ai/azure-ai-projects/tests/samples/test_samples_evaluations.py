# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import pytest
from devtools_testutils import recorded_by_proxy, AzureRecordedTestCase, RecordedTransport, EnvironmentVariableLoader
from sample_executor import (
    SyncSampleExecutor,
    get_sample_paths,
    SamplePathPasser,
)
from test_samples_helpers import get_sample_environment_variables_map

# Preparer with only the variables needed for evaluation samples
evaluationsPreparer = functools.partial(
    EnvironmentVariableLoader,
    "",
    azure_ai_project_endpoint="https://sanitized-account-name.services.ai.azure.com/api/projects/sanitized-project-name",
    azure_ai_model_deployment_name="gpt-4o",
    azure_ai_agent_name="sanitized-agent-name",
)

evaluations_instructions = """We just run Python code for an evaluation sample and captured a Python array of print statements.
Validating the printed content to determine if the evaluation completed successfully:
Respond false if any entries show:
- Error messages or exception text (not including normal status messages)
- Malformed or corrupted data
- Actual timeout errors or connection failures
- Explicit failure messages like "Evaluation run failed"
- Exceptions being raised

Respond with true if:
- The evaluation was created and ran
- Status messages showing progress (like "Waiting for eval run to complete... current status: in_progress") are NORMAL and expected
- The evaluation completed with results (passed or failed evaluation metrics are both valid outcomes)
- Resources were cleaned up (agent deleted, evaluation deleted)

Always respond with `reason` indicating the reason for the response."""

class TestSamplesEvaluations(AzureRecordedTestCase):

    # To run this test with a specific sample, use:
    # pytest tests/samples/test_samples_evaluations.py::TestSamplesEvaluations::test_evaluation_samples[sample_agent_evaluation]
    @evaluationsPreparer()
    @pytest.mark.parametrize(
        "sample_path",
        get_sample_paths(
            "evaluations",
            samples_to_test=[
                "sample_agent_evaluation.py",
                "sample_model_evaluation.py",
                "sample_agent_response_evaluation.py",
                "sample_evaluations_builtin_with_dataset_id.py",
                "sample_evaluations_builtin_with_inline_data.py",
            ],
        ),
    )
    @SamplePathPasser()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_evaluation_samples(self, sample_path: str, **kwargs) -> None:
        env_var_mapping = get_sample_environment_variables_map(kwargs)
        executor = SyncSampleExecutor(self, sample_path, env_var_mapping=env_var_mapping, **kwargs)
        executor.execute()
        executor.validate_print_calls_by_llm(
            instructions=evaluations_instructions,
            project_endpoint=kwargs["azure_ai_project_endpoint"],
            model=kwargs["azure_ai_model_deployment_name"],
        )
