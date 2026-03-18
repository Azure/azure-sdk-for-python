# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import json
import logging
from typing import Dict, Union, List

from typing_extensions import overload, override

from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget
from azure.ai.evaluation._evaluators._common import PromptyEvaluatorBase
from azure.ai.evaluation._common._experimental import experimental
from azure.ai.evaluation._workflows._utils import format_workflow_trace_for_eval

logger = logging.getLogger(__name__)

@experimental
class _WorkflowPlanningEvaluator(PromptyEvaluatorBase[Union[str, float]]):
    """Evaluates whether a multi-agent workflow was well-planned and orchestrated to achieve the user's goal.

    Unlike single-agent evaluators that examine individual query-response pairs, this evaluator
    is workflow-traces-native. It consumes the parsed trace of a workflow execution and evaluates
    planning quality across four dimensions:

    - Task Decomposition (dynamic patterns only)
    - Agent Selection & Routing (dynamic patterns)/Pre-planned Structure Quality (fixed patterns)
    - Progress Tracking & Adaptation
    - Error & Failure Handling

    Scoring is binary:
    - 1 (pass): Workflow well-planned across all applicable dimensions
    - 0 (fail): Material failure in one or more applicable dimensions

    :param model_config: Configuration for the Azure OpenAI model.
    :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration]
    """

    _PROMPTY_FILE = "workflow_planning.prompty"
    _RESULT_KEY = "workflow_planning"
    _OPTIONAL_PARAMS: List[str] = []

    id = "azureai://built-in/evaluators/workflow_planning"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    @override
    def __init__(self, model_config, *, credential=None, **kwargs):
        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, self._PROMPTY_FILE)

        super().__init__(
            model_config=model_config,
            prompty_file=prompty_path,
            result_key=self._RESULT_KEY,
            credential=credential,
            **kwargs,
        )

    @overload
    def __call__(
        self,
        *,
        workflow_trace: Union[str, Dict],
    ) -> Dict[str, Union[str, float]]:
        """Evaluate workflow planning quality from a parsed workflow trace.

        :keyword workflow_trace: The parsed workflow trace (dict from converter output, or
            JSON string). Must contain at minimum: agents, invocations, topology.
        :paramtype workflow_trace: Union[str, Dict]
        :return: Evaluation results with score, result, reason, and per-dimension details.
        :rtype: Dict[str, Union[str, float]]
        """

    @override
    def __call__(self, *args, **kwargs):  # pylint: disable=docstring-missing-param
        """Invokes the instance using the overloaded __call__ signature."""
        return super().__call__(*args, **kwargs)

    @override
    def _convert_kwargs_to_eval_input(self, **kwargs):
        """Pass workflow_trace through to _do_eval, even if None (so _do_eval can raise the correct error)."""
        return [{"workflow_trace": kwargs.get("workflow_trace")}]

    @override
    async def _do_eval(self, eval_input: Dict) -> Dict[str, Union[float, str]]:  # type: ignore[override]
        """Perform workflow planning evaluation."""
        workflow_trace = eval_input.get("workflow_trace")
        if workflow_trace is None:
            raise EvaluationException(
                message="workflow_trace must be provided as input to the Workflow Planning evaluator.",
                internal_message="workflow_trace must be provided.",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.MISSING_FIELD,
                target=ErrorTarget.EVALUATE,
            )

        # Normalize workflow_trace to dict
        if isinstance(workflow_trace, str):
            try:
                workflow_trace = json.loads(workflow_trace)
            except (json.JSONDecodeError, ValueError) as exc:
                raise EvaluationException(
                    message="workflow_trace must be a valid JSON string or dict.",
                    internal_message=f"JSON parse failed: {exc}",
                    blame=ErrorBlame.USER_ERROR,
                    category=ErrorCategory.INVALID_VALUE,
                    target=ErrorTarget.EVALUATE,
                ) from exc

        if not isinstance(workflow_trace, dict):
            raise EvaluationException(
                message="workflow_trace must be a dict or JSON string.",
                internal_message=f"Got type {type(workflow_trace).__name__}",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.INVALID_VALUE,
                target=ErrorTarget.EVALUATE,
            )

        workflow_errors = workflow_trace.get("errors", [])
        if workflow_errors:
            raise EvaluationException(
                message=f"Workflow ended with errors: {workflow_errors}. Workflow Planning evaluation is not applicable.",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.NOT_APPLICABLE,
                target=ErrorTarget.EVALUATE,
            )

        has_invocations = bool(workflow_trace.get("invocations"))
        if not has_invocations:
            raise EvaluationException(
                message="No traces found. Workflow Planning evaluation requires non-empty workflow trace evidence.",
                internal_message="workflow_trace contains no invocations.",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.MISSING_FIELD,
                target=ErrorTarget.EVALUATE,
            )

        # Check parse_failed flag
        if workflow_trace.get("parse_failed"):
            logger.warning("Workflow trace has parse_failed=True; evaluation may be limited.")

        # Format trace into LLM-readable text (warnings logged internally)
        trace_str = format_workflow_trace_for_eval(workflow_trace)

        prompty_input = {
            "workflow_trace": trace_str,
        }

        prompty_output_dict = await self._flow(timeout=self._LLM_CALL_TIMEOUT, **prompty_input)
        llm_output = prompty_output_dict.get("llm_output", {})

        if isinstance(llm_output, dict):
            success_value = llm_output.get("success", False)
            if isinstance(success_value, str):
                success = 1 if success_value.lower() == "true" else 0
            else:
                success = 1 if success_value else 0
            success_result = "pass" if success == 1 else "fail"
            reason = llm_output.get("explanation", "")
            return {
                f"{self._result_key}": success,
                f"{self._result_key}_result": success_result,
                f"{self._result_key}_reason": reason,
                f"{self._result_key}_details": llm_output.get("details", ""),
                f"{self._result_key}_prompt_tokens": prompty_output_dict.get("input_token_count", 0),
                f"{self._result_key}_completion_tokens": prompty_output_dict.get("output_token_count", 0),
                f"{self._result_key}_total_tokens": prompty_output_dict.get("total_token_count", 0),
                f"{self._result_key}_finish_reason": prompty_output_dict.get("finish_reason", ""),
                f"{self._result_key}_model": prompty_output_dict.get("model_id", ""),
                f"{self._result_key}_sample_input": prompty_output_dict.get("sample_input", ""),
                f"{self._result_key}_sample_output": prompty_output_dict.get("sample_output", ""),
            }

        else:
            raise EvaluationException(
                message="Evaluator returned invalid output.",
                blame=ErrorBlame.SYSTEM_ERROR,
                category=ErrorCategory.FAILED_EXECUTION,
                target=ErrorTarget.EVALUATE,
            )
