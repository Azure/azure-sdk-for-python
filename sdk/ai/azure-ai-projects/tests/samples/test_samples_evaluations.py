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
    """
    Tests for evaluation samples.

    Included samples (9):
    - sample_agent_evaluation.py
    - sample_model_evaluation.py
    - sample_agent_response_evaluation.py
    - sample_agent_response_evaluation_with_function_tool.py
    - sample_evaluations_builtin_with_inline_data.py
    - sample_eval_catalog.py
    - sample_eval_catalog_code_based_evaluators.py
    - sample_eval_catalog_prompt_based_evaluators.py
    - sample_evaluation_compare_insight.py

    More samples will be added in the future.

    Excluded samples and reasons:

    Blob Storage / Dataset Upload (incompatible with test proxy playback):
    - sample_evaluations_builtin_with_dataset_id.py: Uploads data to Azure Blob Storage
      before creating the evaluation.
    - sample_evaluations_ai_assisted.py: Creates a Dataset with file upload.
    - sample_evaluations_graders.py: Creates a Dataset with file upload.
    - sample_evaluations_score_model_grader_with_image.py: Uses image data which may
      involve file upload.
    - sample_evaluation_cluster_insight.py: Creates a Dataset with file upload.

    Authentication incompatibility (mock credentials don't work):
    - sample_evaluations_builtin_with_inline_data_oai.py: Uses OpenAI client directly with
      get_bearer_token_provider() which is incompatible with mock credentials.

    External service dependencies (require additional Azure services):
    - sample_evaluations_builtin_with_traces.py: Requires Azure Application Insights and
      uses azure-monitor-query to fetch traces.
    - sample_scheduled_evaluations.py: Requires Azure RBAC assignment via
      azure-mgmt-authorization and azure-mgmt-resource.

    Complex prerequisites (require manual portal setup):
    - sample_continuous_evaluation_rule.py: Requires manual RBAC assignment in Azure
      Portal to enable continuous evaluation.
    - sample_redteam_evaluations.py: Red team evaluations may require special
      permissions or setup.
    """

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
                "sample_evaluations_builtin_with_inline_data.py",
                "sample_eval_catalog.py",
                "sample_eval_catalog_code_based_evaluators.py",
                "sample_eval_catalog_prompt_based_evaluators.py",
                "sample_evaluation_compare_insight.py",
                "sample_agent_response_evaluation_with_function_tool.py",
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
