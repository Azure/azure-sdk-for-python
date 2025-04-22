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
from azure.ai.evaluation._common._experimental import experimental

@experimental
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

    """

    _PROMPTY_FILE = "intent_resolution.prompty"
    _RESULT_KEY = "intent_resolution"
    _OPTIONAL_PARAMS = ["tool_definitions"]

    _MIN_INTENT_RESOLUTION_SCORE = 1
    _MAX_INTENT_RESOLUTION_SCORE = 5
    _DEFAULT_INTENT_RESOLUTION_THRESHOLD = 3

    id = None
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    @override
    def __init__(self, model_config, *,
                 threshold = _DEFAULT_INTENT_RESOLUTION_THRESHOLD,
                 **kwargs):
        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, self._PROMPTY_FILE)
        self.threshold = threshold
        super().__init__(model_config=model_config, prompty_file=prompty_path,
                         result_key=self._RESULT_KEY,
                         **kwargs)

    @overload
    def __call__(
        self,
        *,
        query            : Union[str, List[dict]],
        response         : Union[str, List[dict]],
        tool_definitions : Optional[Union[dict, List[dict]]] = None,
    ) -> Dict[str, Union[str, float]]:
        """Evaluate intent resolution for a given query, response and optional tool definitions.
        The query and response can be either a string or a list of messages.

        Example with string inputs and no tools:
            evaluator = IntentResolutionEvaluator(model_config)
            query = "What is the weather today?"
            response = "The weather is sunny."

            result = evaluator(query=query, response=response)

        Example with list of messages:
            evaluator = IntentResolutionEvaluator(model_config)
            query: [{'role': 'system', 'content': 'You are a friendly and helpful customer service agent.'}, {'createdAt': 1700000060, 'role': 'user', 'content': [{'type': 'text', 'text': 'Hi, I need help with the last 2 orders on my account #888. Could you please update me on their status?'}]}]
            response: [{'createdAt': 1700000070, 'run_id': '0', 'role': 'assistant', 'content': [{'type': 'text', 'text': 'Hello! Let me quickly look up your account details.'}]}, {'createdAt': 1700000075, 'run_id': '0', 'role': 'assistant', 'content': [{'type': 'tool_call', 'tool_call': {'id': 'tool_call_20250310_001', 'type': 'function', 'function': {'name': 'get_orders', 'arguments': {'account_number': '888'}}}}]}, {'createdAt': 1700000080, 'run_id': '0', 'tool_call_id': 'tool_call_20250310_001', 'role': 'tool', 'content': [{'type': 'tool_result', 'tool_result': '[{ "order_id": "123" }, { "order_id": "124" }]'}]}, {'createdAt': 1700000085, 'run_id': '0', 'role': 'assistant', 'content': [{'type': 'text', 'text': 'Thanks for your patience. I see two orders on your account. Let me fetch the details for both.'}]}, {'createdAt': 1700000090, 'run_id': '0', 'role': 'assistant', 'content': [{'type': 'tool_call', 'tool_call': {'id': 'tool_call_20250310_002', 'type': 'function', 'function': {'name': 'get_order', 'arguments': {'order_id': '123'}}}}, {'type': 'tool_call', 'tool_call': {'id': 'tool_call_20250310_003', 'type': 'function', 'function': {'name': 'get_order', 'arguments': {'order_id': '124'}}}}]}, {'createdAt': 1700000095, 'run_id': '0', 'tool_call_id': 'tool_call_20250310_002', 'role': 'tool', 'content': [{'type': 'tool_result', 'tool_result': '{ "order": { "id": "123", "status": "shipped", "delivery_date": "2025-03-15" } }'}]}, {'createdAt': 1700000100, 'run_id': '0', 'tool_call_id': 'tool_call_20250310_003', 'role': 'tool', 'content': [{'type': 'tool_result', 'tool_result': '{ "order": { "id": "124", "status": "delayed", "expected_delivery": "2025-03-20" } }'}]}, {'createdAt': 1700000105, 'run_id': '0', 'role': 'assistant', 'content': [{'type': 'text', 'text': 'The order with ID 123 has been shipped and is expected to be delivered on March 15, 2025. However, the order with ID 124 is delayed and should now arrive by March 20, 2025. Is there anything else I can help you with?'}]}]
            tool_definitions: [{'name': 'get_orders', 'description': 'Get the list of orders for a given account number.', 'parameters': {'type': 'object', 'properties': {'account_number': {'type': 'string', 'description': 'The account number to get the orders for.'}}}}, {'name': 'get_order', 'description': 'Get the details of a specific order.', 'parameters': {'type': 'object', 'properties': {'order_id': {'type': 'string', 'description': 'The order ID to get the details for.'}}}}, {'name': 'initiate_return', 'description': 'Initiate the return process for an order.', 'parameters': {'type': 'object', 'properties': {'order_id': {'type': 'string', 'description': 'The order ID for the return process.'}}}}, {'name': 'update_shipping_address', 'description': 'Update the shipping address for a given account.', 'parameters': {'type': 'object', 'properties': {'account_number': {'type': 'string', 'description': 'The account number to update.'}, 'new_address': {'type': 'string', 'description': 'The new shipping address.'}}}}]

            result = evaluator(query=query, response=response, tool_definitions=tool_definitions)

        :keyword query: The query to be evaluated which is either a string or a list of messages.
            The list of messages is the previous conversation history of the user and agent, including system messages and tool calls.
        :paramtype query: Union[str, List[dict]]
        :keyword response: The response to be evaluated, which is either a string or a list of messages (full agent response potentially including tool calls)
        :paramtype response: Union[str, List[dict]]
        :keyword tool_definitions: An optional list of messages containing the tool definitions the agent is aware of.
        :paramtype tool_definitions: Optional[Union[dict, List[dict]]]
        :return: A dictionary with the intent resolution evaluation
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
    async def _do_eval(self, eval_input: Dict) -> Dict[str, Union[float, str]]:  # type: ignore[override]
        """Do intent resolution evaluation.

        :param eval_input: The input to the evaluator. Expected to contain whatever inputs are needed for the _flow method
        :type eval_input: Dict
        :return: The evaluation result.
        :rtype: Dict
        """
        # we override the _do_eval method as we want the output to be a dictionary, which is a different schema than _base_prompty_eval.py
        if "query" not in eval_input and "response" not in eval_input:
            raise EvaluationException(
                message=f"Both query and response must be provided as input to the intent resolution evaluator.",
                internal_message=f"Both query and response must be provided as input to the intent resolution evaluator.",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.MISSING_FIELD,
                target=ErrorTarget.INTENT_RESOLUTION_EVALUATOR,
            )
        llm_output = await self._flow(timeout=self._LLM_CALL_TIMEOUT, **eval_input)
        # llm_output should always be a dictionary because the response_format of prompty is set to json_object, but checking anyway
        if isinstance(llm_output, dict):
            score  = llm_output.get("resolution_score", math.nan)
            if not check_score_is_valid(score, IntentResolutionEvaluator._MIN_INTENT_RESOLUTION_SCORE, IntentResolutionEvaluator._MAX_INTENT_RESOLUTION_SCORE):
                raise EvaluationException(
                    message=f"Invalid score value: {score}. Expected a number in range [{IntentResolutionEvaluator._MIN_INTENT_RESOLUTION_SCORE}, {IntentResolutionEvaluator._MAX_INTENT_RESOLUTION_SCORE}].",
                    internal_message="Invalid score value.",
                    category=ErrorCategory.FAILED_EXECUTION,
                    blame=ErrorBlame.SYSTEM_ERROR,
                )
            reason = llm_output.get("explanation", "")
            score = float(score)
            score_result = 'pass' if score >= self.threshold else 'fail'

            #remove fields 'explanation' and 'resolution_score' from llm_output as they are already included in the response_dict
            if 'explanation' in llm_output: llm_output.pop("explanation")
            if 'resolution_score' in llm_output: llm_output.pop("resolution_score")

            response_dict = {
                             f"{self._result_key}"           : score,
                             f"{self._result_key}_result"    : score_result,
                             f"{self._result_key}_threshold" : self.threshold,
                             f"{self._result_key}_reason"    : reason,
                             f"additional_details"           : llm_output
                        }
            return response_dict
        # If llm_output is not a dictionary, return NaN for the score. This should never happen
        return {self._result_key: math.nan}
