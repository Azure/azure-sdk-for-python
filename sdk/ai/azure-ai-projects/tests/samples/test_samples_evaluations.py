# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import os
import re
import pytest
from devtools_testutils import recorded_by_proxy, AzureRecordedTestCase, RecordedTransport, EnvironmentVariableLoader
from sample_executor import (
    SyncSampleExecutor,
    get_sample_paths,
    SamplePathPasser,
)
from test_samples_helpers import get_sample_env_vars

# Preparer with only the variables needed for evaluation samples
evaluationsPreparer = functools.partial(
    EnvironmentVariableLoader,
    "",
    foundry_project_endpoint="https://sanitized-account-name.services.ai.azure.com/api/projects/sanitized-project-name",
    foundry_model_name="sanitized-model-deployment-name",
    foundry_agent_name="sanitized-agent-name",
)


def _preprocess_eval_validation(entries: list[str]) -> str:
    """Pre-process evaluation validation entries for LLM analysis.

    Filters out SDK/HTTP debug log entries that flood the validation text with
    words like 'error', 'failed', 'timeout' in innocuous contexts (HTTP headers,
    response bodies, connection parameters), causing LLM false positives.
    Keeps only the meaningful sample output and annotates metric counter fields.
    """
    # --- Step 1: filter out debug/HTTP noise entries ---
    _NOISE = re.compile(
        r"^\[(?:azure\.|openai\.|httpx|httpcore|msrest)"  # debug logger prefix
        r"|^==> Request:|^<== Response:"  # HTTP request/response markers
        r"|^Headers:|^Body:"  # header/body sections
        r"|^\s*x-stainless-|^\s*x-ms-|^\s*x-request-"  # x- prefixed headers
        r"|^\s*apim-request-id:|^\s*azureml-served"  # Azure-specific headers
        r"|^\s*mise-correlation-id:"  # correlation headers
        r"|^\s*(?:accept|accept-encoding|authorization|connection|content-length"
        r"|content-type|content-encoding|host|user-agent|server|date|vary"
        r"|transfer-encoding|strict-transport-security|request-context"
        r"|x-content-type-options|api-supported-versions):"  # standard HTTP headers
        r"|^(?:GET|POST|PUT|DELETE|PATCH) https?://"  # HTTP method lines
        r"|^\d{3} (?:OK|Created|Accepted|No Content)"  # HTTP status lines
        r"|^DEBUG |^INFO ",  # log level prefixes
        re.IGNORECASE,
    )
    kept = [e for e in entries if e.strip() and not _NOISE.match(e.strip())]
    text = "\n".join(kept)

    # --- Step 2: annotate metric counter fields ---
    # JSON-style ("field": value) and pprint-style ('field': value)
    text = re.sub(
        r"""(?P<quote>["'])(?P<field>failed|errored|error|not_applicable)(?P=quote):\s*(?P<value>\d+|null|"null"|None|\{[^}]*\})""",
        r'"\g<field>": \g<value> /* metric counter, not an error */',
        text,
    )
    # Python repr-style (field=value) — e.g. ResultCounts(failed=0, errored=0)
    text = re.sub(
        r"\b(?P<field>failed|errored|error|not_applicable)=(?P<value>\d+|None)",
        r"\g<field>=\g<value>/* metric counter, not an error */",
        text,
    )
    return text


class TestSamplesEvaluations(AzureRecordedTestCase):
    """
    Tests for evaluation samples.

    Included samples (28):

    Main evaluation samples (13):
    - sample_agent_evaluation.py
    - sample_model_evaluation.py
    - sample_agent_response_evaluation.py
    - sample_agent_response_evaluation_with_function_tool.py
    - sample_evaluations_builtin_with_inline_data.py
    - sample_eval_catalog.py
    - sample_eval_catalog_code_based_evaluators.py
    - sample_eval_catalog_prompt_based_evaluators.py
    - sample_evaluation_compare_insight.py
    - sample_redteam_evaluations.py
    - sample_evaluations_graders.py (OpenAI graders: label_model, text_similarity, string_check, score_model)
    - sample_evaluations_ai_assisted.py (AI-assisted evaluators: Similarity, ROUGE, METEOR, GLEU, F1, BLEU)
    - sample_evaluation_cluster_insight.py (cluster insights generation)

    Agentic evaluator samples (15):
    - sample_coherence.py
    - sample_fluency.py
    - sample_groundedness.py
    - sample_intent_resolution.py
    - sample_quality_grader.py
    - sample_relevance.py
    - sample_response_completeness.py
    - sample_task_adherence.py
    - sample_task_completion.py
    - sample_task_navigation_efficiency.py
    - sample_tool_call_accuracy.py
    - sample_tool_call_success.py
    - sample_tool_input_accuracy.py
    - sample_tool_output_utilization.py
    - sample_tool_selection.py
    - sample_generic_agentic_evaluator.py

    Excluded samples and reasons:

    Blob Storage / Dataset Upload (incompatible with test proxy playback):
    - sample_evaluations_builtin_with_dataset_id.py: Uploads data to Azure Blob Storage
      before creating the evaluation.
    - sample_evaluations_score_model_grader_with_image.py: Uses image data which may
      involve file upload.

    Authentication incompatibility (mock credentials don't work):
    - sample_evaluations_builtin_with_inline_data_oai.py: Uses OpenAI client directly with
      get_bearer_token_provider() which is incompatible with mock credentials.

    External service dependencies (require additional Azure services):
    - sample_evaluations_builtin_with_traces.py: Requires Azure Application Insights and
      uses azure-monitor-query to fetch traces.
    - sample_scheduled_evaluations.py: Requires Azure RBAC assignment via
      azure-mgmt-authorization and azure-mgmt-resource, AND uploads Dataset.

    Complex prerequisites (require manual portal setup):
    - sample_continuous_evaluation_rule.py: Requires manual RBAC assignment in Azure
      Portal to enable continuous evaluation.
    """

    # To run this test with a specific sample, use:
    # pytest tests/samples/test_samples_evaluations.py::TestSamplesEvaluations::test_evaluation_samples[sample_agent_evaluation]
    @evaluationsPreparer()
    @pytest.mark.parametrize(
        "sample_path",
        get_sample_paths(
            "evaluations",
            samples_to_skip=[
                "sample_evaluations_ai_assisted.py",  # Similarity evaluator returns FAILED_EXECUTION ('query' is missing)
                "sample_evaluations_builtin_with_inline_data_oai.py",  # 401 AuthenticationError (invalid subscription key or API endpoint)
                "sample_evaluations_builtin_with_traces.py",  # Missing required env var APPINSIGHTS_RESOURCE_ID (KeyError)
                "sample_evaluations_score_model_grader_with_image.py",  # Eval fails: image inputs not supported for configured grader model
                "sample_evaluations_score_model_grader_with_image_model_target.py",  # Eval fails: image inputs not supported for configured grader model
                "sample_evaluations_score_model_grader_with_audio.py",  # Eval fails: audio inputs not supported for configured grader model
                "sample_evaluations_score_model_grader_with_audio_model_target.py",  # Eval fails: audio inputs not supported for configured grader model
                "sample_scheduled_evaluations.py",  # Missing dependency azure.mgmt.resource (ModuleNotFoundError)
                "sample_evaluations_builtin_with_dataset_id.py",  # Requires dataset upload / Blob Storage prerequisite
                "sample_continuous_evaluation_rule.py",  # Requires manual RBAC assignment in Azure Portal
                "sample_evaluations_builtin_with_csv.py",  # Requires CSV file upload prerequisite
                "sample_synthetic_data_agent_evaluation.py",  # Synthetic data gen is long-running preview feature
                "sample_synthetic_data_model_evaluation.py",  # Synthetic data gen is long-running preview feature
                "sample_eval_catalog_prompt_based_evaluators.py",  # For some reason fails with 500 (Internal server error)
            ],
        ),
    )
    @SamplePathPasser()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_evaluation_samples(self, sample_path: str, **kwargs) -> None:
        env_vars = get_sample_env_vars(kwargs)
        executor = SyncSampleExecutor(
            self,
            sample_path,
            env_vars=env_vars,
            validation_text_preprocessor=_preprocess_eval_validation,
            **kwargs,
        )
        executor.execute()
        executor.validate_print_calls_by_llm()

    # To run this test with a specific sample, use:
    # pytest tests/samples/test_samples_evaluations.py::TestSamplesEvaluations::test_agentic_evaluator_samples[sample_coherence]
    @evaluationsPreparer()
    @pytest.mark.parametrize(
        "sample_path",
        get_sample_paths(
            "evaluations/agentic_evaluators",
            samples_to_skip=[
                "sample_intent_resolution.py",  # Evaluator FAILED_EXECUTION: tool_definitions must be a list of dictionaries
                "sample_quality_grader.py",
                "sample_task_navigation_efficiency.py",  # Evaluator FAILED_EXECUTION: required 'actions' parameter is missing
                "sample_tool_call_success.py",  # Sample data evaluates to failure (tool result has DB_CONNECTION_FAILED)
            ],
        ),
    )
    @SamplePathPasser()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_agentic_evaluator_samples(self, sample_path: str, **kwargs) -> None:
        env_vars = get_sample_env_vars(kwargs)
        executor = SyncSampleExecutor(
            self,
            sample_path,
            env_vars=env_vars,
            validation_text_preprocessor=_preprocess_eval_validation,
            **kwargs,
        )
        executor.execute()
        executor.validate_print_calls_by_llm()

    # To run this test, use:
    # pytest tests/samples/test_samples_evaluations.py::TestSamplesEvaluations::test_generic_agentic_evaluator_sample
    @evaluationsPreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_generic_agentic_evaluator_sample(self, **kwargs) -> None:
        # Manually construct path to nested sample
        current_dir = os.path.dirname(os.path.abspath(__file__))
        samples_folder = os.path.normpath(os.path.join(current_dir, os.pardir, os.pardir))
        sample_path = os.path.join(
            samples_folder,
            "samples",
            "evaluations",
            "agentic_evaluators",
            "sample_generic_agentic_evaluator",
            "sample_generic_agentic_evaluator.py",
        )
        env_vars = get_sample_env_vars(kwargs)
        executor = SyncSampleExecutor(
            self,
            sample_path,
            env_vars=env_vars,
            validation_text_preprocessor=_preprocess_eval_validation,
            **kwargs,
        )
        executor.execute()
        executor.validate_print_calls_by_llm()
