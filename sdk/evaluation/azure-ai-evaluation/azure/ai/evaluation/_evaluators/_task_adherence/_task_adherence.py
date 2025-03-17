# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import math
from typing import Dict, Union, List, Optional

from typing_extensions import overload, override

from azure.ai.evaluation._evaluators._common import PromptyEvaluatorBase
from azure.ai.evaluation._model_configurations import Message

class TaskAdherenceEvaluator(PromptyEvaluatorBase[Union[str, float]]):
    """
    Evaluates task adherence for a given query and response within a QA scenario.
    
    The task adherence evaluator assesses how well the response follows the assigned task and instructions.

    :param model_config: Configuration for the Azure OpenAI model.
    :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration]
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

        :return: The completeness score.
        :rtype: Dict[str, Union[str, bool, float]]
        """
        completeness_result = super().__call__(*args, **kwargs)
        response_completeness_score = float(completeness_result.get(self._result_key, math.nan))
        explanation = completeness_result.get(f"{self._result_key}_reason")

        is_response_complete = response_completeness_score >= self.threshold

        return {
            "is_response_complete": is_response_complete,
            "response_completeness_score": response_completeness_score,
            "explanation": explanation
        }

