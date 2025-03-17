# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import math
from typing import Dict, Union, List, Optional

from typing_extensions import overload, override

from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget
from azure.ai.evaluation._evaluators._common import PromptyEvaluatorBase
from azure.ai.evaluation._model_configurations import Conversation, Message
from ..._common.utils import check_score_is_valid

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
    _OPTIONAL_PARAMS = ["conversation_history", "tool_definitions"]

    MIN_TASK_ADHERENCE_SCORE = 1
    MAX_TASK_ADHERENCE_SCORE = 5

    id = None
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    @override
    def __init__(self, model_config, threshold=MAX_TASK_ADHERENCE_SCORE):
        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, self._PROMPTY_FILE)
        self.threshold = threshold
        super().__init__(model_config=model_config, prompty_file=prompty_path, result_key=self._RESULT_KEY)

    @overload
    def __call__(
        self,
        *,
        instructions: str,
        query: Union[str, List[Message]],
        response: Union[str, List[Message]],
        conversation_history: Optional[List[Message]] = None,
        tool_definitions: Optional[List[Message]] = None,
    ) -> Dict[str, Union[str, float]]:
        """Evaluate task adherence for a given query, response, and optional context.
        The evaluation considers instructions, query, response, conversation history, and tool definitions.

        :keyword instructions: The task instructions for evaluation.
        :paramtype instructions: str
        :keyword query: The query being evaluated, either a string or a list of messages.
        :paramtype query: Union[str, List[Message]]
        :keyword response: The response being evaluated.
        :paramtype response: Union[str, List[Message]]
        :keyword conversation_history: Previous interactions in the conversation.
        :paramtype conversation_history: Optional[List[Message]]
        :keyword tool_definitions: The tool definitions known to the agent.
        :paramtype tool_definitions: Optional[List[Message]]
        :return: A dictionary with the task adherence evaluation results.
        :rtype: Dict[str, Union[str, float]]
        """

    @override
    def __call__(self, *args, **kwargs):
        """
        Invokes the instance using the overloaded __call__ signature.
        
        For detailed parameter types and return value documentation, see the overloaded __call__ definition.
        """
        return super().__call__(*args, **kwargs)

    @override
    async def _do_eval(self, eval_input: Dict) -> Dict[str, Union[float, str]]:
        """Perform task adherence evaluation.

        :param eval_input: The input to the evaluator.
        :type eval_input: Dict
        :return: The evaluation result.
        :rtype: Dict
        """
        if "query" not in eval_input or "response" not in eval_input or "instructions" not in eval_input:
            raise EvaluationException(
                message="Instructions, query, and response must be provided for task adherence evaluation.",
                internal_message="Missing required evaluation input.",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.MISSING_FIELD,
                target=ErrorTarget.TASK_ADHERENCE_EVALUATOR,
            )
        llm_output = await self._flow(timeout=self._LLM_CALL_TIMEOUT, **eval_input)
        
        if isinstance(llm_output, dict):
            score = llm_output.get("score", math.nan)
            if not check_score_is_valid(score, TaskAdherenceEvaluator.MIN_TASK_ADHERENCE_SCORE, TaskAdherenceEvaluator.MAX_TASK_ADHERENCE_SCORE):
                raise EvaluationException(
                    message=f"Invalid score value: {score}. Expected a number in range [{TaskAdherenceEvaluator.MIN_TASK_ADHERENCE_SCORE}, {TaskAdherenceEvaluator.MAX_TASK_ADHERENCE_SCORE}].",
                    internal_message="Invalid score value.",
                    category=ErrorCategory.FAILED_EXECUTION,
                    blame=ErrorBlame.SYSTEM_ERROR,
                )
            explanation = llm_output.get("explanation", "")
            score = float(score)
            score_result = 'pass' if score >= self.threshold else 'fail'
            response_dict = {
                f"{self._result_key}": score,
                f"{self._result_key}_result": score_result,
                f"{self._result_key}_threshold": self.threshold,
                f"{self._result_key}_reason": explanation,
                f"additional_details": llm_output,
            }
            return response_dict
        
        return {self._result_key: math.nan}
