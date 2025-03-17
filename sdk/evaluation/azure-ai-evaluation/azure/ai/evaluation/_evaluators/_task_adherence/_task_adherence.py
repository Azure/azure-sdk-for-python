# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import math
from typing import Dict, Union, List, Optional

from typing_extensions import overload, override

from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget
from azure.ai.evaluation._evaluators._common import PromptyEvaluatorBase
from azure.ai.evaluation._common.utils import parse_quality_evaluator_reason_score
from azure.ai.evaluation._model_configurations import Message

class TaskAdherenceEvaluator(PromptyEvaluatorBase[Union[str, float]]):
    """The Task Adherence evaluator assesses how well an AI-generated response follows the assigned task based on:

        - Alignment with instructions and definitions
        - Accuracy and clarity of the response
        - Proper use of provided tool definitions

    Scoring is based on five levels:
    1. Fully Inadherent – Response completely ignores instructions.
    2. Barely Adherent – Partial alignment with critical gaps.
    3. Moderately Adherent – Meets core requirements but lacks precision.
    4. Mostly Adherent – Clear and accurate with minor issues.
    5. Fully Adherent – Flawless adherence to instructions.

    The evaluation includes a step-by-step reasoning process, a brief explanation, and a final integer score.


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
    """

    _PROMPTY_FILE = "task_adherence.prompty"
    _RESULT_KEY = "task_adherence"
    _OPTIONAL_PARAMS = ["tool_definitions"]

    DEFAULT_TASK_ADHERENCE_SCORE = 5

    id = None
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    @override
    def __init__(self, model_config, threshold=DEFAULT_TASK_ADHERENCE_SCORE):
        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, self._PROMPTY_FILE)
        self.threshold = threshold
        super().__init__(model_config=model_config, prompty_file=prompty_path, result_key=self._RESULT_KEY)

    @overload
    def __call__(
        self,
        *,
        query: Union[str, List[Message]],
        response: Union[str, List[Message]],
        tool_definitions: Optional[List[Message]] = None,
    ) -> Dict[str, Union[str, float]]:
        """Evaluate task adherence for a given query, response, and optional context.
        The evaluation considers instructions, query, response, conversation history, and tool definitions.

        :keyword query: The query being evaluated, either a string or a list of messages.
        :paramtype query: Union[str, List[Message]]
        :keyword response: The response being evaluated.
        :paramtype response: Union[str, List[Message]]
        :keyword tool_definitions: The tool definitions known to the agent.
        :paramtype tool_definitions: Optional[List[Message]]
        :return: A dictionary with the task adherence evaluation results.
        :rtype: Dict[str, Union[str, bool, float]]
        """

    @override
    def __call__(  # pylint: disable=docstring-missing-param
            self,
            *args,
            **kwargs,
    ):
        """
        Evaluate Task Adherence.
        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword query: The query to be evaluated.
        :paramtype query: str
        :return: The adherence score.
        :rtype: Dict[str, Union[str, bool, float]]
        """
        return super().__call__(*args, **kwargs)

    @override
    async def _do_eval(self, eval_input: Dict) -> Dict[str, Union[float, str]]:  # type: ignore[override]
        """Do Task Adherence evaluation.
        :param eval_input: The input to the evaluator. Expected to contain whatever inputs are needed for the _flow method
        :type eval_input: Dict
        :return: The evaluation result.
        :rtype: Dict
        """
        # we override the _do_eval method as we want the output to be a dictionary,
        # which is a different schema than _base_prompty_eval.py
        if "query" not in eval_input and "response" not in eval_input:
            raise EvaluationException(
                message=f"Both query and response must be provided as input to the Task Adherence evaluator.",
                internal_message=f"Both query and response must be provided as input to the Task Adherence evaluator.",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.MISSING_FIELD,
                target=ErrorTarget.TASK_ADHERENCE_EVALUATOR,
            )

        llm_output = await self._flow(timeout=self._LLM_CALL_TIMEOUT, **eval_input)

        score = math.nan
        if llm_output:
            score, reason = parse_quality_evaluator_reason_score(llm_output, valid_score_range="[1-5]")

            score_result = 'pass' if score >= self.threshold else 'fail'

            return {
                f"{self._result_key}": score,
                f"{self._result_key}_result": score_result,
                f"{self._result_key}_threshold": self.threshold,
                f"{self._result_key}_reason": reason,
            }

        return {self._result_key: math.nan}

