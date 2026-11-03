# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import math
from typing import Any, Dict, TypeVar, Union

from typing_extensions import override

from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget

# The message-preprocessing helpers now live in ``azure.ai.evaluation._common.utils`` (single source of
# truth). They are imported here so this module can use them and so callers that historically imported
# them from this module keep working. ``_drop_mcp_approval_messages`` / ``_normalize_function_call_types``
# are re-exported only (used indirectly via ``_preprocess_messages``).
from ..._common.utils import (  # noqa: F401  # pylint: disable=unused-import
    _is_intermediate_response,
    _drop_mcp_approval_messages,
    _normalize_function_call_types,
    _preprocess_messages,
)
from ._base_model_eval import ModelEvaluatorBase
from ._prompty_strategy import PromptyEvaluationStrategy
from ._model_runners import AsyncPrompty, UserAgentSingleton  # noqa: F401  # pylint: disable=unused-import

T = TypeVar("T")


class PromptyEvaluatorBase(ModelEvaluatorBase[T]):
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
    :keyword is_reasoning_model: This parameter is in preview. If True, updates the config parameters in
        prompty file based on reasoning models. Defaults to False.
    :type is_reasoning_model: bool
    """

    # __init__ and __call__ are inherited: the constructor from ModelEvaluatorBase, and __call__ is not defined
    # because child classes have such varied signatures that there's no point defining a default here.

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

        # Check for intermediate response
        if _is_intermediate_response(eval_input.get("response")):
            return self._return_not_applicable_result(
                "Intermediate response. Please provide the agent's final response for evaluation.",
                self._threshold,
            )

        # Preprocess messages if they are lists
        if isinstance(eval_input.get("response"), list):
            eval_input["response"] = _preprocess_messages(eval_input["response"])
        if isinstance(eval_input.get("query"), list):
            eval_input["query"] = _preprocess_messages(eval_input["query"])

        if self._uses_decision_model:
            return await self._do_decision_eval(eval_input)

        return await PromptyEvaluationStrategy(
            self._prompty_model_runner,
            result_key=self._result_key,
            threshold=self._threshold,
            timeout=self._LLM_CALL_TIMEOUT,
            strict=False,
            missing_score=math.nan,
            higher_is_better=self._higher_is_better,
        ).evaluate(eval_input)

    async def _do_decision_eval(self, eval_input: Dict) -> Dict[str, Any]:
        """Evaluate the prepared input with the evaluator's decision model.

        Decision-capable evaluators that use this class's ``_do_eval`` override this to send the inputs their
        prompt renders.

        :param eval_input: The validated and preprocessed input.
        :type eval_input: Dict
        :return: The evaluation result.
        :rtype: Dict
        """
        raise NotImplementedError(f"{type(self).__name__} does not define its decision model inputs.")
