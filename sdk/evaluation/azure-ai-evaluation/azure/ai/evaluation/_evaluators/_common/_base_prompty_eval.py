# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import math
import re
from typing import Dict, TypeVar, Union

from promptflow.core import AsyncPrompty
from typing_extensions import override

from azure.ai.evaluation._common.constants import PROMPT_BASED_REASON_EVALUATORS
from azure.ai.evaluation._constants import EVALUATION_PASS_FAIL_MAPPING
from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget
from ..._common.utils import construct_prompty_model_config, validate_model_config, parse_quality_evaluator_reason_score
from . import EvaluatorBase

try:
    from ..._user_agent import USER_AGENT
except ImportError:
    USER_AGENT = "None"

T = TypeVar("T")


class PromptyEvaluatorBase(EvaluatorBase[T]):
    """Base class for all evaluators that make use of context as an input. It's also assumed that such evaluators
    make use of a prompty file, and return their results as a dictionary, with a single key-value pair
    linking the result name to a float value (unless multi-turn evaluation occurs, in which case the
    per-turn results are stored in a list under the key "evaluation_per_turn").

    :param result_key: The key to use for the result of the evaluation. Single turn evaluations will return
        a dictionary in the format {result_key: float}.
    :type result_key: str
    :param prompty_file: The path to the prompty file to use for evaluation.
    :type prompty_file: str
    :param model_config: The model configuration to use for evaluation.
    :type model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration]
    :param ignore_queries: If True, queries will be ignored in conversation evaluations. Default is False.
        Useful since some evaluators of this format are response-only.
    :type ignore_queries: bool
    """

    _LLM_CALL_TIMEOUT = 600
    _DEFAULT_OPEN_API_VERSION = "2024-02-15-preview"

    def __init__(self, *, result_key: str, prompty_file: str, model_config: dict, eval_last_turn: bool = False, threshold: int = 3, _higher_is_better: bool = False):
        self._result_key = result_key
        self._prompty_file = prompty_file
        self._threshold = threshold
        self._higher_is_better = _higher_is_better
        super().__init__(eval_last_turn=eval_last_turn, threshold=threshold, _higher_is_better=_higher_is_better)

        subclass_name = self.__class__.__name__
        user_agent = f"{USER_AGENT} (type=evaluator subtype={subclass_name})"
        prompty_model_config = construct_prompty_model_config(
            validate_model_config(model_config),
            self._DEFAULT_OPEN_API_VERSION,
            user_agent,
        )

        self._flow = AsyncPrompty.load(source=prompty_file, model=prompty_model_config)

    # __call__ not overridden here because child classes have such varied signatures that there's no point
    # defining a default here.
    def _get_binary_result(self, score: float) -> str:
        """Get the binary result based on the score.

        :param score: The score to evaluate.
        :type score: float
        :return: The binary result.
        :rtype: str
        """
        if math.isnan(score):
            return "unknown"
        if self._higher_is_better:
            if score >= self._threshold:
                return EVALUATION_PASS_FAIL_MAPPING[True]
            else:
                return EVALUATION_PASS_FAIL_MAPPING[False]
        else:
            if score <= self._threshold:
                return EVALUATION_PASS_FAIL_MAPPING[True]
            else:
                return EVALUATION_PASS_FAIL_MAPPING[False]

    @override
    async def _do_eval(self, eval_input: Dict) -> Dict[str, Union[float, str]]:  # type: ignore[override]
        """Do a relevance evaluation.

        :param eval_input: The input to the evaluator. Expected to contain
        whatever inputs are needed for the _flow method, including context
        and other fields depending on the child class.
        :type eval_input: Dict
        :return: The evaluation result.
        :rtype: Dict
        """
        if "query" not in eval_input and "response" not in eval_input:
            raise EvaluationException(
                message="Only text conversation inputs are supported.",
                internal_message="Only text conversation inputs are supported.",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.INVALID_VALUE,
                target=ErrorTarget.CONVERSATION,
            )
        llm_output = await self._flow(timeout=self._LLM_CALL_TIMEOUT, **eval_input)

        score = math.nan
        if llm_output:
            # Parse out score and reason from evaluators known to possess them.
            if self._result_key in PROMPT_BASED_REASON_EVALUATORS:
                score, reason = parse_quality_evaluator_reason_score(llm_output)
                binary_result = self._get_binary_result(score)
                return {
                    self._result_key: float(score),
                    f"gpt_{self._result_key}": float(score),
                    f"{self._result_key}_reason": reason,
                    f"{self._result_key}_result": binary_result,
                    f"{self._result_key}_threshold": self._threshold,
                }
            match = re.search(r"\d", llm_output)
            if match:
                score = float(match.group())
                binary_result = self._get_binary_result(score)
            return {
                self._result_key: float(score), 
                f"gpt_{self._result_key}": float(score),
                f"{self._result_key}_result": binary_result,
                f"{self._result_key}_threshold": self._threshold,
            }

        binary_result = self._get_binary_result(score)
        return {
            self._result_key: float(score), 
            f"gpt_{self._result_key}": float(score),
            f"{self._result_key}_result": binary_result,
            f"{self._result_key}_threshold": self._threshold,
        }
