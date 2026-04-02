# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import math
import os
import re
import logging
from typing import Dict, Union

from typing_extensions import override

from azure.ai.evaluation._evaluators._common import PromptyEvaluatorBase
from azure.ai.evaluation._evaluators._common._validators import ConversationValidator

try:
    from azure.ai.evaluation._exceptions import ErrorTarget
except ImportError:
    from azure.ai.evaluation._common.utils import ErrorTarget


logger = logging.getLogger(__name__)


class MCSGroundednessEvaluator(PromptyEvaluatorBase[Union[str, float]]):
    """Evaluates groundedness, document utility, and context coverage for a RAG scenario.

    Returns a groundedness score (1-5), contextCoverage (0-3), documentUtility (A/B/C),
    and additional details (unsupportedClaims, missingContextParts, explanation, judgeConfidence).

    Threshold default is 4 for groundedness pass/fail.

    :param model_config: Configuration for the Azure OpenAI model.
    :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration]
    :param threshold: The threshold for groundedness pass/fail. Default is 4.
    :type threshold: int
    :param credential: The credential for authenticating to Azure AI service.
    :type credential: ~azure.core.credentials.TokenCredential
    """

    _PROMPTY_FILE = "mcs_groundedness.prompty"
    _RESULT_KEY = "mcs_groundedness"

    @override
    def __init__(self, model_config, *, threshold=4, credential=None, **kwargs):
        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, self._PROMPTY_FILE)
        self._higher_is_better = True

        self._validator = ConversationValidator(
            error_target=ErrorTarget.GROUNDEDNESS_EVALUATOR,
            requires_query=True,
        )

        super().__init__(
            model_config=model_config,
            prompty_file=prompty_path,
            result_key=self._RESULT_KEY,
            threshold=threshold,
            credential=credential,
            _higher_is_better=self._higher_is_better,
            **kwargs,
        )

    def __call__(
        self,
        *,
        query: str,
        response: str,
        context: str,
    ) -> Dict[str, Union[str, float]]:
        """Evaluate MCS groundedness for given query, response, and context.

        :keyword query: The query to be evaluated.
        :paramtype query: str
        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword context: The context (retrieved documents) to be evaluated against.
        :paramtype context: str
        :return: The evaluation result dict.
        :rtype: Dict[str, Union[str, float]]
        """
        return super().__call__(query=query, response=response, context=context)

    @override
    async def _do_eval(self, eval_input: Dict) -> Dict[str, Union[float, str]]:
        """Parse the JSON output from the prompt and return structured results."""
        prompty_output_dict = await self._flow(timeout=self._LLM_CALL_TIMEOUT, **eval_input)

        score = math.nan
        result = {}

        if prompty_output_dict:
            llm_output = prompty_output_dict.get("llm_output", "")
            input_token_count = prompty_output_dict.get("input_token_count", 0)
            output_token_count = prompty_output_dict.get("output_token_count", 0)
            total_token_count = prompty_output_dict.get("total_token_count", 0)
            finish_reason = prompty_output_dict.get("finish_reason", "")
            model_id = prompty_output_dict.get("model_id", "")
            sample_input = prompty_output_dict.get("sample_input", "")
            sample_output = prompty_output_dict.get("sample_output", "")

            parsed = self._parse_json_output(llm_output)

            groundedness_val = parsed.get("groundedness", None)
            if groundedness_val is not None and groundedness_val != "null":
                try:
                    score = float(groundedness_val)
                except (ValueError, TypeError):
                    score = math.nan

            binary_result = self._get_binary_result(score)

            # Build details dict with all the extra fields from the prompt output
            details = {}
            for key in ("explanation", "contextCoverage", "documentUtility",
                        "missingContextParts", "unsupportedClaims", "judgeConfidence", "index"):
                if key in parsed:
                    details[key] = parsed[key]

            result = {
                self._result_key: float(score) if not math.isnan(score) else score,
                f"{self._result_key}_result": binary_result,
                f"{self._result_key}_threshold": self._threshold,
                f"{self._result_key}_reason": parsed.get("explanation", {}).get("groundedness", ""),
                f"{self._result_key}_details": details,
                f"{self._result_key}_prompt_tokens": input_token_count,
                f"{self._result_key}_completion_tokens": output_token_count,
                f"{self._result_key}_total_tokens": total_token_count,
                f"{self._result_key}_finish_reason": finish_reason,
                f"{self._result_key}_model": model_id,
                f"{self._result_key}_sample_input": sample_input,
                f"{self._result_key}_sample_output": sample_output,
            }

        if result:
            return result

        from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory
        raise EvaluationException(
            message="Evaluator returned invalid output.",
            blame=ErrorBlame.SYSTEM_ERROR,
            category=ErrorCategory.FAILED_EXECUTION,
            target=ErrorTarget.EVALUATE,
        )

    @staticmethod
    def _parse_json_output(llm_output: str) -> dict:
        """Extract JSON from the LLM output string."""
        if not llm_output:
            return {}
        # Try to find a JSON block in the output (may be wrapped in ```json ... ```)
        json_match = re.search(r"```json\s*(.*?)\s*```", llm_output, re.DOTALL)
        if json_match:
            text = json_match.group(1)
        else:
            # Try to find raw JSON object
            json_match = re.search(r"\{.*\}", llm_output, re.DOTALL)
            if json_match:
                text = json_match.group(0)
            else:
                return {}
        try:
            # Handle null values in JSON (Python's json module supports this natively)
            return json.loads(text)
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from LLM output: %s", text[:200])
            return {}

    async def _real_call(self, **kwargs):
        self._validator.validate_eval_input(kwargs)
        return await super()._real_call(**kwargs)
