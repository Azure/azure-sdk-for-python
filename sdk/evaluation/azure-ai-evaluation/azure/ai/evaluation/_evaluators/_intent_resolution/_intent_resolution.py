# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import math
import re
import json
from typing import Dict, Union, List, Optional

from typing_extensions import overload, override

from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget
from azure.ai.evaluation._evaluators._common import PromptyEvaluatorBase
from azure.ai.evaluation._model_configurations import Conversation, Message

class IntentResolutionEvaluator(PromptyEvaluatorBase[Union[str, float]]):
    """
    Evaluates intent resolution for a given query and response or a multi-turn conversation, including reasoning.

    The intent resolution evaluator assesses whether the user intent was correctly identified and resolved.

    :param model_config: Configuration for the Azure OpenAI model.
    :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration]

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_evaluate.py
            :start-after: [START intent_resolution_evaluator]
            :end-before: [END intent_resolution_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call an IntentResolutionEvaluator with a query and response.

    .. note::

        To align with our support of a diverse set of models, an output key without the `gpt_` prefix has been added.
        To maintain backwards compatibility, the old key with the `gpt_` prefix is still present in the output;
        however, it is recommended to use the new key moving forward as the old key will be deprecated in the future.
    """

    _PROMPTY_FILE = "intent_resolution.prompty"
    _RESULT_KEY = "intent_resolution"
    _OPTIONAL_PARAMS = ["tool_definitions"]

    id = "azureml://registries/azureml/models/IntentResolution-Evaluator/versions/4"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    @override
    def __init__(self, model_config):
        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, self._PROMPTY_FILE)
        super().__init__(model_config=model_config, prompty_file=prompty_path, result_key=self._RESULT_KEY)

    @overload
    def __call__(
        self,
        *,
        query: Union[str, List[Message]],
        response: Union[str, List[Message]],
        tool_definitions : Optional[Union[str, List[Message]]] = None,
    ) -> Dict[str, Union[str, float]]:
        """Evaluate intent resolution for given input of query, response

        :keyword query: The query to be evaluated.
        :paramtype query: Union[str, List[Message]]
        :keyword response: The response to be evaluated.
        :paramtype response: Union[str, List[Message]]
        :keyword tool_definitions: An optional list of messages containing the tools the agent is to be aware of.
        :paramtype tool_definitions: Optional[Union[str, List[Message]]]
        :return: The intent resolution score.
        :rtype: Dict[str, float]
        """

    @override
    def __call__(  # pylint: disable=docstring-missing-param
        self,
        *args,
        **kwargs,
    ):
        """Evaluate intent resolution. Accepts either a query and response for a single evaluation,
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
        return super().__call__(*args, **kwargs)

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
        # we override the _do_eval method as we want the output to be a dictionary, which is a different schema than _base_prompty_eval.py
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
            parsed_llm_output = {}
            reason = ""
            try:
                #_chain_of_thought = r"<S0>(.*?)</S0>"
                evaluation_pattern = r"<S1>(.*?)</S1>"
                evaluation_match = re.findall(evaluation_pattern, llm_output, re.DOTALL)
                if evaluation_match:
                    parsed_llm_output = json.loads(evaluation_match[0].strip())
                    if 'resolution_score' in parsed_llm_output:
                        score = parsed_llm_output.get("resolution_score", math.nan)
                    if 'explanation' in parsed_llm_output:
                        reason = parsed_llm_output.get("explanation", "")
            except ValueError as exc:
                raise EvaluationException(
                    message=f"Failed to parse model output: \n{llm_output}",
                    internal_message="Failed to parse model output.",
                    category=ErrorCategory.FAILED_EXECUTION,
                    blame=ErrorBlame.SYSTEM_ERROR,
                ) from exc
            response_dict = {
                            self._result_key: float(score),
                            f"gpt_{self._result_key}": float(score),
                            f"{self._result_key}_reason": reason,
                            f"additional_details" : parsed_llm_output
                        }
            return response_dict
        return {self._result_key: float(score), f"gpt_{self._result_key}": float(score)}

