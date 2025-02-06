# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import math
import os
from typing import Dict, Union, List, Any, re

from typing_extensions import overload, override

from azure.ai.evaluation._evaluators._common import PromptyEvaluatorBase
from azure.ai.evaluation._model_configurations import Conversation
from azure.ai.evaluation._common.constants import PROMPT_BASED_REASON_EVALUATORS
from ..._common.utils import parse_quality_evaluator_reason_score


class FunctionToolAccuracyEvaluator(PromptyEvaluatorBase[Union[str, float]]):
    """
    Evaluates coherence score for a given query and response or a multi-turn conversation, including reasoning.

    The coherence measure assesses the ability of the language model to generate text that reads naturally,
    flows smoothly, and resembles human-like language in its responses. Use it when assessing the readability
    and user-friendliness of a model's generated responses in real-world applications.

    :param model_config: Configuration for the Azure OpenAI model.
    :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration]

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_evaluate.py
            :start-after: [START coherence_evaluator]
            :end-before: [END coherence_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call a CoherenceEvaluator with a query and response.

    .. note::

        To align with our support of a diverse set of models, an output key without the `gpt_` prefix has been added.
        To maintain backwards compatibility, the old key with the `gpt_` prefix is still be present in the output;
        however, it is recommended to use the new key moving forward as the old key will be deprecated in the future.
    """

    _PROMPTY_FILE = "tool_accuracy.prompty"
    _RESULT_KEY = "function_tool_accuracy"

    id = "azureml://registries/azureml/models/Coherence-Evaluator/versions/4"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    @override
    def __init__(self, model_config, tool_definitions: List[Dict[str, Union[str, float]]]):
        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, self._PROMPTY_FILE)
        super().__init__(model_config=model_config, prompty_file=prompty_path, result_key=self._RESULT_KEY)
        self._tool_definitions = tool_definitions

    @overload
    def __call__(
        self,
        *,
        query: str,
        tool_calls: List[Any],
    ) -> Dict[str, Union[str, float]]:
        """Evaluate coherence for given input of query, response

        :keyword query: The query to be evaluated.
        :paramtype query: str
        :keyword response: The response to be evaluated.
        :paramtype response: str
        :return: The coherence score.
        :rtype: Dict[str, float]
        """

    @overload
    def __call__(
        self,
        *,
        conversation: Conversation,
    ) -> Dict[str, Union[float, Dict[str, List[Union[str, float]]]]]:
        """Evaluate coherence for a conversation

        :keyword conversation: The conversation to evaluate. Expected to contain a list of conversation turns under the
            key "messages", and potentially a global context under the key "context". Conversation turns are expected
            to be dictionaries with keys "content", "role", and possibly "context".
        :paramtype conversation: Optional[~azure.ai.evaluation.Conversation]
        :return: The coherence score.
        :rtype: Dict[str, Union[float, Dict[str, List[float]]]]
        """

    @override
    def __call__(  # pylint: disable=docstring-missing-param
        self,
        *args,
        **kwargs,
    ):
        """Evaluate coherence. Accepts either a query and response for a single evaluation,
        or a conversation for a potentially multi-turn evaluation. If the conversation has more than one pair of
        turns, the evaluator will aggregate the results of each turn.

        :keyword query: The query to be evaluated.
        :paramtype query: str
        :keyword response: The response to be evaluated.
        :paramtype response: Optional[str]
        :keyword conversation: The conversation to evaluate. Expected to contain a list of conversation turns under the
            key "messages". Conversation turns are expected
            to be dictionaries with keys "content" and "role".
        :paramtype conversation: Optional[~azure.ai.evaluation.Conversation]
        :return: The relevance score.
        :rtype: Union[Dict[str, float], Dict[str, Union[float, Dict[str, List[float]]]]]
        """
        if kwargs.get("conversation") is None and kwargs.get("tool_definitions") is None:
            kwargs["tool_definitions"] = self._tool_definitions
        return super().__call__(*args, **kwargs)

    @override
    async def _do_eval(self, eval_input: Dict) -> Dict[str, float]:
        """Produce a glue score evaluation result.

        :param eval_input: The input to the evaluation function.
        :type eval_input: Dict
        :return: The evaluation result.
        :rtype: Dict
        """
        eval_input["tool_definitions"] = self._tool_definitions # type: ignore
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
            if self._result_key in PROMPT_BASED_REASON_EVALUATORS or True:
                score, reason = parse_quality_evaluator_reason_score(llm_output)
                return {
                    self._result_key: float(score),
                    f"gpt_{self._result_key}": float(score),
                    f"{self._result_key}_reason": reason,
                }
            match = re.search(r"\d", llm_output)
            if match:
                score = float(match.group())
            return {self._result_key: float(score), f"gpt_{self._result_key}": float(score)}
        return {self._result_key: float(score)}