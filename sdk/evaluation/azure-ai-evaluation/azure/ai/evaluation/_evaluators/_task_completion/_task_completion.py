# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import math
import logging
from typing import Dict, Union, List, Optional

from typing_extensions import overload, override

from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget
from azure.ai.evaluation._evaluators._common import PromptyEvaluatorBase
from azure.ai.evaluation._evaluators._common._validators import ToolDefinitionsValidator, ValidatorInterface
from ..._common.utils import reformat_conversation_history, reformat_agent_response, reformat_tool_definitions
from azure.ai.evaluation._model_configurations import Message
from azure.ai.evaluation._common._experimental import experimental

logger = logging.getLogger(__name__)


@experimental
class _TaskCompletionEvaluator(PromptyEvaluatorBase[Union[str, float]]):
    """The Task Completion evaluator determines whether an AI agent successfully completed the requested task based on:

        - Final outcome and deliverable of the task
        - Completeness of task requirements

    This evaluator focuses solely on task completion and success, not on task adherence or intent understanding.

    Scoring is binary:
    - 1 (pass): Task fully completed with usable deliverable that meets all user requirements
    - 0 (fail): Task incomplete, partially completed, or deliverable does not meet requirements

    The evaluation includes task requirement analysis, outcome assessment, and completion gap identification.


    :param model_config: Configuration for the Azure OpenAI model.
    :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration]

    .. admonition:: Example:
        .. literalinclude:: ../samples/evaluation_samples_evaluate.py
            :start-after: [START task_completion_evaluator]
            :end-before: [END task_completion_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call a _TaskCompletionEvaluator with a query and response.

    .. admonition:: Example using Azure AI Project URL:

        .. literalinclude:: ../samples/evaluation_samples_evaluate_fdp.py
            :start-after: [START task_completion_evaluator]
            :end-before: [END task_completion_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call a _TaskCompletionEvaluator using Azure AI Project URL in the following format
                https://{resource_name}.services.ai.azure.com/api/projects/{project_name}

    """

    _PROMPTY_FILE = "task_completion.prompty"
    _RESULT_KEY = "task_completion"
    _OPTIONAL_PARAMS = ["tool_definitions"]

    _validator: ValidatorInterface

    id = "azureai://built-in/evaluators/task_completion"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    @override
    def __init__(self, model_config, *, credential=None, **kwargs):
        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, self._PROMPTY_FILE)

        # Initialize input validator
        self._validator = ToolDefinitionsValidator(error_target=ErrorTarget.TASK_COMPLETION_EVALUATOR)

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
        query: Union[str, List[dict]],
        response: Union[str, List[dict]],
        tool_definitions: Optional[Union[dict, List[dict]]] = None,
    ) -> Dict[str, Union[str, float]]:
        """Evaluate task completion for a given query, response, and optionally tool definitions.
        The query and response can be either a string or a list of messages.


        Example with string inputs and no tools:
            evaluator = _TaskCompletionEvaluator(model_config)
            query = "Plan a 3-day itinerary for Paris with cultural landmarks and local cuisine."
            response = "**Day 1:** Morning: Louvre Museum, Lunch: Le Comptoir du Relais..."

            result = evaluator(query=query, response=response)

        Example with list of messages:
            evaluator = _TaskCompletionEvaluator(model_config)
            query = [{'role': 'system', 'content': 'You are a helpful travel planning assistant.'}, {'createdAt': 1700000060, 'role': 'user', 'content': [{'type': 'text', 'text': 'Plan a 3-day Paris itinerary with cultural landmarks and cuisine'}]}]
            response = [{'createdAt': 1700000070, 'run_id': '0', 'role': 'assistant', 'content': [{'type': 'text', 'text': '**Day 1:** Morning: Visit Louvre Museum (9 AM - 12 PM)...'}]}]
            tool_definitions = [{'name': 'get_attractions', 'description': 'Get tourist attractions for a city.', 'parameters': {'type': 'object', 'properties': {'city': {'type': 'string', 'description': 'The city name.'}}}}]

            result = evaluator(query=query, response=response, tool_definitions=tool_definitions)

        :keyword query: The query being evaluated, either a string or a list of messages.
        :paramtype query: Union[str, List[dict]]
        :keyword response: The response being evaluated, either a string or a list of messages (full agent response potentially including tool calls)
        :paramtype response: Union[str, List[dict]]
        :keyword tool_definitions: An optional list of messages containing the tool definitions the agent is aware of.
        :paramtype tool_definitions: Optional[Union[dict, List[dict]]]
        :return: A dictionary with the task completion evaluation results.
        :rtype: Dict[str, Union[str, float]]
        """

    @override
    def __call__(  # pylint: disable=docstring-missing-param
        self,
        *args,
        **kwargs,
    ):
        """
        Invokes the instance using the overloaded __call__ signature.

        For detailed parameter types and return value documentation, see the overloaded __call__ definition.
        """
        return super().__call__(*args, **kwargs)

    @override
    async def _real_call(self, **kwargs):
        """The asynchronous call where real end-to-end evaluation logic is performed.

        :keyword kwargs: The inputs to evaluate.
        :type kwargs: Dict
        :return: The evaluation result.
        :rtype: Union[DoEvalResult[T_EvalValue], AggregateResult[T_EvalValue]]
        """
        # Validate input before processing
        self._validator.validate_eval_input(kwargs)

        return await super()._real_call(**kwargs)

    @override
    async def _do_eval(self, eval_input: Dict) -> Dict[str, Union[float, str]]:  # type: ignore[override]
        """Do Task Completion evaluation.
        :param eval_input: The input to the evaluator. Expected to contain whatever inputs are needed for the _flow method
        :type eval_input: Dict
        :return: The evaluation result.
        :rtype: Dict
        """
        # we override the _do_eval method as we want the output to be a dictionary,
        # which is a different schema than _base_prompty_eval.py
        if "query" not in eval_input and "response" not in eval_input:
            raise EvaluationException(
                message=f"Both query and response must be provided as input to the Task Completion evaluator.",
                internal_message=f"Both query and response must be provided as input to the Task Completion evaluator.",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.MISSING_FIELD,
                target=ErrorTarget.TASK_COMPLETION_EVALUATOR,
            )
        eval_input["query"] = reformat_conversation_history(eval_input["query"], logger, include_system_messages=True)
        eval_input["response"] = reformat_agent_response(eval_input["response"], logger, include_tool_messages=True)
        if "tool_definitions" in eval_input and eval_input["tool_definitions"] is not None:
            eval_input["tool_definitions"] = reformat_tool_definitions(eval_input["tool_definitions"], logger)

        prompty_output_dict = await self._flow(timeout=self._LLM_CALL_TIMEOUT, **eval_input)
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
        if logger:
            logger.warning("LLM output is not a dictionary, returning 0 for the success.")
        return {self._result_key: 0}
