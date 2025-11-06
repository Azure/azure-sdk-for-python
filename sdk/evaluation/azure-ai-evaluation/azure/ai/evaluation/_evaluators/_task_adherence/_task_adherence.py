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
from ..._common.utils import (
    reformat_conversation_history,
    reformat_agent_response,
)
from azure.ai.evaluation._model_configurations import Message
from azure.ai.evaluation._common._experimental import experimental

logger = logging.getLogger(__name__)


@experimental
class TaskAdherenceEvaluator(PromptyEvaluatorBase[Union[str, float]]):
    """The Task Adherence evaluator assesses whether an AI assistant's actions fully align with the user's intent
    and fully achieve the intended goal across three dimensions:

        - Goal adherence: Did the assistant achieve the user's objective within scope and constraints?
        - Rule adherence: Did the assistant respect safety, privacy, authorization, and presentation contracts?
        - Procedural adherence: Did the assistant follow required workflows, tool use, sequencing, and verification?

    The evaluator returns a boolean flag indicating whether there was any material failure in any dimension.
    A material failure is an issue that makes the output unusable, creates verifiable risk, violates an explicit
    constraint, or is a critical issue as defined in the evaluation dimensions.

    The evaluation includes step-by-step reasoning and a flagged boolean result.


    :param model_config: Configuration for the Azure OpenAI model.
    :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration]

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_evaluate.py
            :start-after: [START task_adherence_evaluator]
            :end-before: [END task_adherence_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call an TaskAdherenceEvaluator with a query and response.

    .. admonition:: Example using Azure AI Project URL:

        .. literalinclude:: ../samples/evaluation_samples_evaluate_fdp.py
            :start-after: [START task_adherence_evaluator]
            :end-before: [END task_adherence_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call TaskAdherenceEvaluator using Azure AI Project URL in the following format
                https://{resource_name}.services.ai.azure.com/api/projects/{project_name}

    """

    _PROMPTY_FILE = "task_adherence.prompty"
    _RESULT_KEY = "task_adherence"
    _OPTIONAL_PARAMS = []

    _DEFAULT_TASK_ADHERENCE_SCORE = 0

    id = "azureai://built-in/evaluators/task_adherence"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    @override
    def __init__(self, model_config, *, threshold=_DEFAULT_TASK_ADHERENCE_SCORE, credential=None, **kwargs):
        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, self._PROMPTY_FILE)
        self.threshold = threshold  # to be removed in favor of _threshold
        super().__init__(
            model_config=model_config,
            prompty_file=prompty_path,
            result_key=self._RESULT_KEY,
            credential=credential,
            _higher_is_better=True,
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
        """Evaluate task adherence for a given query and response.
        The query and response must be lists of messages in conversation format.


        Example with list of messages:
            evaluator = TaskAdherenceEvaluator(model_config)
            query = [{'role': 'system', 'content': 'You are a friendly and helpful customer service agent.'}, {'createdAt': 1700000060, 'role': 'user', 'content': [{'type': 'text', 'text': 'Hi, I need help with the last 2 orders on my account #888. Could you please update me on their status?'}]}]
            response = [{'createdAt': 1700000070, 'run_id': '0', 'role': 'assistant', 'content': [{'type': 'text', 'text': 'Hello! Let me quickly look up your account details.'}]}, {'createdAt': 1700000075, 'run_id': '0', 'role': 'assistant', 'content': [{'type': 'tool_call', 'tool_call': {'id': 'tool_call_20250310_001', 'type': 'function', 'function': {'name': 'get_orders', 'arguments': {'account_number': '888'}}}}]}, {'createdAt': 1700000080, 'run_id': '0', 'tool_call_id': 'tool_call_20250310_001', 'role': 'tool', 'content': [{'type': 'tool_result', 'tool_result': '[{ "order_id": "123" }, { "order_id": "124" }]'}]}, {'createdAt': 1700000085, 'run_id': '0', 'role': 'assistant', 'content': [{'type': 'text', 'text': 'Thanks for your patience. I see two orders on your account. Let me fetch the details for both.'}]}, {'createdAt': 1700000090, 'run_id': '0', 'role': 'assistant', 'content': [{'type': 'tool_call', 'tool_call': {'id': 'tool_call_20250310_002', 'type': 'function', 'function': {'name': 'get_order', 'arguments': {'order_id': '123'}}}}, {'type': 'tool_call', 'tool_call': {'id': 'tool_call_20250310_003', 'type': 'function', 'function': {'name': 'get_order', 'arguments': {'order_id': '124'}}}}]}, {'createdAt': 1700000095, 'run_id': '0', 'tool_call_id': 'tool_call_20250310_002', 'role': 'tool', 'content': [{'type': 'tool_result', 'tool_result': '{ "order": { "id": "123", "status": "shipped", "delivery_date": "2025-03-15" } }'}]}, {'createdAt': 1700000100, 'run_id': '0', 'tool_call_id': 'tool_call_20250310_003', 'role': 'tool', 'content': [{'type': 'tool_result', 'tool_result': '{ "order": { "id": "124", "status": "delayed", "expected_delivery": "2025-03-20" } }'}]}, {'createdAt': 1700000105, 'run_id': '0', 'role': 'assistant', 'content': [{'type': 'text', 'text': 'The order with ID 123 has been shipped and is expected to be delivered on March 15, 2025. However, the order with ID 124 is delayed and should now arrive by March 20, 2025. Is there anything else I can help you with?'}]}]

            result = evaluator(query=query, response=response)

        :keyword query: The query being evaluated, must be a list of messages including system and user messages.
        :paramtype query: Union[str, List[dict]]
        :keyword response: The response being evaluated, must be a list of messages (full agent response including tool calls and results)
        :paramtype response: Union[str, List[dict]]
        :return: A dictionary with the task adherence evaluation results including flagged (bool) and reasoning (str).
        :rtype: Dict[str, Union[str, float, bool]]
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
    async def _do_eval(self, eval_input: Dict) -> Dict[str, Union[float, str, bool]]:  # type: ignore[override]
        """Do Task Adherence evaluation.
        :param eval_input: The input to the evaluator. Expected to contain whatever inputs are needed for the _flow method
        :type eval_input: Dict
        :return: The evaluation result.
        :rtype: Dict
        """
        # we override the _do_eval method as we want the output to be a dictionary,
        # which is a different schema than _base_prompty_eval.py
        if "query" not in eval_input or "response" not in eval_input:
            raise EvaluationException(
                message=f"Both query and response must be provided as input to the Task Adherence evaluator.",
                internal_message=f"Both query and response must be provided as input to the Task Adherence evaluator.",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.MISSING_FIELD,
                target=ErrorTarget.TASK_ADHERENCE_EVALUATOR,
            )

        # Reformat conversation history and extract system message
        query_messages = reformat_conversation_history(eval_input["query"], logger, include_system_messages=True)
        system_message = ""
        user_query = ""

        # Parse query messages to extract system message and user query
        if isinstance(query_messages, list):
            for msg in query_messages:
                if isinstance(msg, dict) and msg.get("role") == "system":
                    system_message = msg.get("content", "")
                elif isinstance(msg, dict) and msg.get("role") == "user":
                    user_query = msg.get("content", "")
        elif isinstance(query_messages, str):
            user_query = query_messages

        # Reformat response and separate assistant messages from tool calls
        response_messages = reformat_agent_response(eval_input["response"], logger, include_tool_messages=True)
        assistant_response = ""
        tool_calls = ""

        # Parse response messages to extract assistant response and tool calls
        if isinstance(response_messages, list):
            assistant_parts = []
            tool_parts = []
            for msg in response_messages:
                if isinstance(msg, dict):
                    role = msg.get("role", "")
                    if role == "assistant":
                        content = msg.get("content", "")
                        if isinstance(content, list):
                            for item in content:
                                if isinstance(item, dict):
                                    if item.get("type") == "text":
                                        assistant_parts.append(item.get("text", ""))
                                    elif item.get("type") == "tool_call":
                                        tool_parts.append(str(item.get("tool_call", "")))
                        else:
                            assistant_parts.append(str(content))
                    elif role == "tool":
                        tool_parts.append(str(msg))
            assistant_response = "\n".join(assistant_parts)
            tool_calls = "\n".join(tool_parts)
        elif isinstance(response_messages, str):
            assistant_response = response_messages

        # Prepare inputs for prompty
        prompty_input = {
            "system_message": system_message,
            "query": user_query,
            "response": assistant_response,
            "tool_calls": tool_calls,
        }

        prompty_output_dict = await self._flow(timeout=self._LLM_CALL_TIMEOUT, **prompty_input)
        llm_output = prompty_output_dict["llm_output"]

        if isinstance(llm_output, dict):
            flagged = llm_output.get("flagged", False)
            reasoning = llm_output.get("reasoning", "")
            # Convert flagged to numeric score for backward compatibility (1 = pass, 0 = fail)
            score = 0.0 if flagged else 1.0
            score_result = "fail" if flagged else "pass"

            return {
                f"{self._result_key}": score,
                f"{self._result_key}_result": score_result,
                f"{self._result_key}_reason": reasoning,
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
