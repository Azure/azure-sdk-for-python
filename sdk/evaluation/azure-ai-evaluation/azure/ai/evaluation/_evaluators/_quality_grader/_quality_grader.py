# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import logging
import os
from typing import Dict, List, Optional, Union

from typing_extensions import overload, override

if os.getenv("AI_EVALS_USE_PF_PROMPTY", "false").lower() == "true":
    from promptflow.core._flow import AsyncPrompty
else:
    from azure.ai.evaluation._legacy.prompty import AsyncPrompty

from azure.ai.evaluation._evaluators._common import PromptyEvaluatorBase
from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget
from azure.ai.evaluation._model_configurations import Conversation

try:
    from ..._user_agent import UserAgentSingleton
except ImportError:

    class UserAgentSingleton:
        @property
        def value(self) -> str:
            return "None"


from ..._common.utils import construct_prompty_model_config, validate_model_config

logger = logging.getLogger(__name__)

# Thresholds for response quality checks (first prompt)
_RESPONSE_QUALITY_ABSTENTION_EXPECTED = False
_RESPONSE_QUALITY_RELEVANCE_EXPECTED = True
_RESPONSE_QUALITY_ANSWER_COMPLETENESS_THRESHOLD = 1.5

# Thresholds for groundedness checks (second prompt)
_GROUNDEDNESS_THRESHOLD = 3.5
_CONTEXT_COVERAGE_THRESHOLD = 1.5


class QualityGraderEvaluator(PromptyEvaluatorBase[Union[str, float]]):
    """Evaluates overall response quality using a two-stage grading pipeline.

    Stage 1 (Response Quality): Evaluates the response for relevance, abstention, and answer completeness.
    The response must satisfy:
        - abstention must be false
        - relevance must be true
        - answerCompleteness must be greater than 1.5

    Stage 2 (Groundedness, only if context is provided): Evaluates whether the response is grounded in the
    provided context and covers the key information. The response must satisfy:
        - groundedness must be greater than 3.5
        - contextCoverage must exceed 1.5

    If all checks pass, the evaluator returns "pass". Otherwise, it returns "fail" with failure reasons.

    :param model_config: Configuration for the Azure OpenAI model.
    :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration]
    :param credential: The credential for authenticating to Azure AI service.
    :type credential: ~azure.core.credentials.TokenCredential
    :keyword is_reasoning_model: If True, updates config parameters for reasoning models. Defaults to False.
    :paramtype is_reasoning_model: bool
    """

    _RESPONSE_QUALITY_PROMPTY = "quality_grader_response_quality.prompty"
    _GROUNDEDNESS_PROMPTY = "quality_grader_groundedness.prompty"
    _RESULT_KEY = "quality_grader"
    _OPTIONAL_PARAMS = ["context"]

    id = "azureai://built-in/evaluators/quality_grader"

    @override
    def __init__(self, model_config, *, credential=None, **kwargs):
        current_dir = os.path.dirname(__file__)
        response_quality_prompty_path = os.path.join(current_dir, self._RESPONSE_QUALITY_PROMPTY)

        self._higher_is_better = True
        self._model_config = model_config
        self._credential = credential

        super().__init__(
            model_config=model_config,
            prompty_file=response_quality_prompty_path,
            result_key=self._RESULT_KEY,
            threshold=1,
            credential=credential,
            _higher_is_better=self._higher_is_better,
            **kwargs,
        )

        # Load the second prompty flow for groundedness evaluation
        groundedness_prompty_path = os.path.join(current_dir, self._GROUNDEDNESS_PROMPTY)
        subclass_name = self.__class__.__name__
        user_agent = f"{UserAgentSingleton().value} (type=evaluator subtype={subclass_name})"
        prompty_model_config = construct_prompty_model_config(
            validate_model_config(model_config),
            self._DEFAULT_OPEN_API_VERSION,
            user_agent,
        )
        self._groundedness_flow = AsyncPrompty.load(
            source=groundedness_prompty_path,
            model=prompty_model_config,
            token_credential=credential,
            is_reasoning_model=kwargs.get("is_reasoning_model", False),
        )

    @overload
    def __call__(
        self,
        *,
        query: str,
        response: str,
        context: Optional[str] = None,
    ) -> Dict[str, Union[str, float]]:
        """Evaluate quality for a given query, response, and optional context.

        :keyword query: The query to be evaluated.
        :paramtype query: str
        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword context: The context (retrieved documents) to evaluate groundedness against. Optional.
        :paramtype context: Optional[str]
        :return: The quality grader result.
        :rtype: Dict[str, Union[str, float]]
        """

    @overload
    def __call__(
        self,
        *,
        conversation: Conversation,
    ) -> Dict[str, Union[float, Dict[str, List[Union[str, float]]]]]:
        """Evaluate quality for a conversation.

        :keyword conversation: The conversation to evaluate.
        :paramtype conversation: Optional[~azure.ai.evaluation.Conversation]
        :return: The quality grader result.
        :rtype: Dict[str, Union[float, Dict[str, List[Union[str, float]]]]]
        """

    @override
    def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)

    @override
    async def _do_eval(self, eval_input: Dict) -> Dict[str, Union[float, str, Dict]]:  # type: ignore[override]
        """Run the two-stage quality grading pipeline.

        Stage 1: Call the response quality prompt and check thresholds.
        Stage 2 (if context provided): Call the groundedness prompt and check thresholds.
        """
        query = eval_input.get("query", "")
        response = eval_input.get("response", "")
        context = eval_input.get("context", None)

        total_prompt_tokens = 0
        total_completion_tokens = 0
        total_tokens = 0
        model_id = ""

        # --- Stage 1: Response Quality ---
        stage1_input = {"question": query, "response": response}
        stage1_output = await self._flow(timeout=self._LLM_CALL_TIMEOUT, **stage1_input)

        stage1_parsed = self._parse_prompty_json_output(stage1_output)
        total_prompt_tokens += stage1_output.get("input_token_count", 0) if stage1_output else 0
        total_completion_tokens += stage1_output.get("output_token_count", 0) if stage1_output else 0
        total_tokens += stage1_output.get("total_token_count", 0) if stage1_output else 0
        model_id = stage1_output.get("model_id", "") if stage1_output else ""

        # Check stage 1 conditions
        failure_reasons = []
        abstention = stage1_parsed.get("abstention")
        relevance = stage1_parsed.get("relevance")
        answer_completeness = stage1_parsed.get("answerCompleteness")

        if abstention is True:
            failure_reasons.append("abstention is true (expected false)")
        if relevance is not True:
            failure_reasons.append(f"relevance is {relevance} (expected true)")
        if isinstance(answer_completeness, (int, float)) and answer_completeness <= _RESPONSE_QUALITY_ANSWER_COMPLETENESS_THRESHOLD:
            failure_reasons.append(
                f"answerCompleteness is {answer_completeness} (must be > {_RESPONSE_QUALITY_ANSWER_COMPLETENESS_THRESHOLD})"
            )
        elif answer_completeness is None or answer_completeness == "null":
            failure_reasons.append("answerCompleteness is null (must be > 1.5)")

        if failure_reasons:
            return self._build_result(
                passed=False,
                failure_reasons=failure_reasons,
                stage1_parsed=stage1_parsed,
                stage2_parsed=None,
                prompt_tokens=total_prompt_tokens,
                completion_tokens=total_completion_tokens,
                total_tokens=total_tokens,
                model_id=model_id,
            )

        # --- Stage 2: Groundedness (only if context is provided) ---
        stage2_parsed = None
        if context and isinstance(context, str) and context.strip():
            stage2_input = {"question": query, "response": response, "context": context}
            stage2_output = await self._groundedness_flow(timeout=self._LLM_CALL_TIMEOUT, **stage2_input)

            stage2_parsed = self._parse_prompty_json_output(stage2_output)
            total_prompt_tokens += stage2_output.get("input_token_count", 0) if stage2_output else 0
            total_completion_tokens += stage2_output.get("output_token_count", 0) if stage2_output else 0
            total_tokens += stage2_output.get("total_token_count", 0) if stage2_output else 0

            groundedness = stage2_parsed.get("groundedness")
            context_coverage = stage2_parsed.get("contextCoverage")

            if isinstance(groundedness, (int, float)) and groundedness <= _GROUNDEDNESS_THRESHOLD:
                failure_reasons.append(
                    f"groundedness is {groundedness} (must be > {_GROUNDEDNESS_THRESHOLD})"
                )
            elif groundedness is None or groundedness == "null":
                failure_reasons.append("groundedness is null (must be > 3.5)")

            if isinstance(context_coverage, (int, float)) and context_coverage <= _CONTEXT_COVERAGE_THRESHOLD:
                failure_reasons.append(
                    f"contextCoverage is {context_coverage} (must exceed {_CONTEXT_COVERAGE_THRESHOLD})"
                )
            elif context_coverage is None or context_coverage == "null":
                failure_reasons.append("contextCoverage is null (must exceed 1.5)")

            if failure_reasons:
                return self._build_result(
                    passed=False,
                    failure_reasons=failure_reasons,
                    stage1_parsed=stage1_parsed,
                    stage2_parsed=stage2_parsed,
                    prompt_tokens=total_prompt_tokens,
                    completion_tokens=total_completion_tokens,
                    total_tokens=total_tokens,
                    model_id=model_id,
                )

        # All checks passed
        return self._build_result(
            passed=True,
            failure_reasons=[],
            stage1_parsed=stage1_parsed,
            stage2_parsed=stage2_parsed,
            prompt_tokens=total_prompt_tokens,
            completion_tokens=total_completion_tokens,
            total_tokens=total_tokens,
            model_id=model_id,
        )

    @staticmethod
    def _parse_prompty_json_output(prompty_output: Optional[Dict]) -> Dict:
        """Parse the JSON output from a prompty flow call.

        :param prompty_output: The raw output dict from the prompty flow.
        :return: Parsed JSON dict from the LLM output.
        """
        if not prompty_output:
            return {}
        llm_output = prompty_output.get("llm_output", "")
        if not llm_output:
            return {}
        if isinstance(llm_output, dict):
            return llm_output
        try:
            return json.loads(llm_output)
        except (json.JSONDecodeError, TypeError):
            logger.warning("Failed to parse LLM output as JSON: %s", llm_output)
            return {}

    def _build_result(
        self,
        *,
        passed: bool,
        failure_reasons: List[str],
        stage1_parsed: Optional[Dict],
        stage2_parsed: Optional[Dict],
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        model_id: str,
    ) -> Dict[str, Union[str, float, Dict]]:
        """Build the standardized result dictionary.

        :param passed: Whether the evaluation passed.
        :param failure_reasons: List of reasons for failure (empty if passed).
        :param stage1_parsed: Parsed output from stage 1 (response quality).
        :param stage2_parsed: Parsed output from stage 2 (groundedness), or None if not run.
        :param prompt_tokens: Total prompt tokens used.
        :param completion_tokens: Total completion tokens used.
        :param total_tokens: Total tokens used.
        :param model_id: The model ID used.
        :return: Standardized result dict.
        """
        score = 1.0 if passed else 0.0
        result_label = self._PASS_RESULT if passed else self._FAIL_RESULT
        reason = "All quality checks passed." if passed else "; ".join(failure_reasons)

        details = {}
        if stage1_parsed:
            details["abstention"] = stage1_parsed.get("abstention")
            details["relevance"] = stage1_parsed.get("relevance")
            details["answerCompleteness"] = stage1_parsed.get("answerCompleteness")
            details["queryType"] = stage1_parsed.get("queryType")
            details["conversationIncomplete"] = stage1_parsed.get("conversationIncomplete")
            details["judgeConfidence"] = stage1_parsed.get("judgeConfidence")
            details["stage1_explanation"] = stage1_parsed.get("explanation", {})

        if stage2_parsed:
            details["groundedness"] = stage2_parsed.get("groundedness")
            details["contextCoverage"] = stage2_parsed.get("contextCoverage")
            details["documentUtility"] = stage2_parsed.get("documentUtility")
            details["missingContextParts"] = stage2_parsed.get("missingContextParts", [])
            details["unsupportedClaims"] = stage2_parsed.get("unsupportedClaims", [])
            details["stage2_explanation"] = stage2_parsed.get("explanation", {})

        return {
            self._result_key: score,
            f"{self._result_key}_result": result_label,
            f"{self._result_key}_reason": reason,
            f"{self._result_key}_threshold": self._threshold,
            f"{self._result_key}_details": details,
            f"{self._result_key}_prompt_tokens": prompt_tokens,
            f"{self._result_key}_completion_tokens": completion_tokens,
            f"{self._result_key}_total_tokens": total_tokens,
            f"{self._result_key}_model": model_id,
        }
