# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import math
import logging
from typing import Dict, Union, List, Optional

from typing_extensions import overload, override

from azure.ai.evaluation._exceptions import (
    EvaluationException,
    ErrorBlame,
    ErrorCategory,
    ErrorTarget,
)
from azure.ai.evaluation._evaluators._common import PromptyEvaluatorBase
from ..._common.utils import (
    reformat_conversation_history,
    reformat_agent_response,
    reformat_tool_definitions,
    filter_to_used_tools,
)
from azure.ai.evaluation._model_configurations import Message
from azure.ai.evaluation._common._experimental import experimental

logger = logging.getLogger(__name__)


@experimental
class ToolOutputUtilizationEvaluator(PromptyEvaluatorBase[Union[str, float]]):
    """The Tool Output Utilization Evaluator assesses how effectively an AI agent utilizes the outputs from tools and whether it accurately incorporates this information into its responses.

    Scoring is based on two levels:
    1. Pass - The agent effectively utilizes tool outputs and accurately incorporates the information into its response.
    2. Fail - The agent fails to properly utilize tool outputs or incorrectly incorporates the information into its response.

    The evaluation includes the score, a brief explanation, and a final pass/fail result.


    :param model_config: Configuration for the Azure OpenAI model.
    :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration]

    .. admonition:: Example:
        .. literalinclude:: ../samples/evaluation_samples_evaluate.py
            :start-after: [START tool_output_utilization_evaluator]
            :end-before: [END tool_output_utilization_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call a ToolOutputUtilizationEvaluator with a query and response.

    .. admonition:: Example using Azure AI Project URL:

        .. literalinclude:: ../samples/evaluation_samples_evaluate_fdp.py
            :start-after: [START tool_output_utilization_evaluator]
            :end-before: [END tool_output_utilization_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call ToolOutputUtilizationEvaluator using Azure AI Project URL in the following format
                https://{resource_name}.services.ai.azure.com/api/projects/{project_name}

    """

    _PROMPTY_FILE = "tool_output_utilization.prompty"
    _RESULT_KEY = "tool_output_utilization"
    _OPTIONAL_PARAMS = ["tool_definitions"]

    _DEFAULT_TOOL_OUTPUT_UTILIZATION_SCORE = 3

    id = "azureai://built-in/evaluators/tool_output_utilization"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    @override
    def __init__(
        self,
        model_config,
        *,
        threshold=_DEFAULT_TOOL_OUTPUT_UTILIZATION_SCORE,
        credential=None,
        **kwargs,
    ):
        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, self._PROMPTY_FILE)
        self.threshold = threshold
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
        tool_definitions: Union[dict, List[dict]],
    ) -> Dict[str, Union[str, float]]:
        """Evaluate tool output utilization for a given query, response, and optional tool defintions.
        The query and response can be either a string or a list of messages.


        Example with string inputs and no tools:
            evaluator = ToolOutputUtilizationEvaluator(model_config)
            query = "What is the weather today?"
            response = "The weather is sunny."

            result = evaluator(query=query, response=response)

        Example with list of messages:
            evaluator = ToolOutputUtilizationEvaluator(model_config)
            query = [{'role': 'system', 'content': 'You are a friendly and helpful customer service agent.'}, {'createdAt': 1700000060, 'role': 'user', 'content': [{'type': 'text', 'text': 'Hi, I need help with the last 2 orders on my account #888. Could you please update me on their status?'}]}]
            response = [{'createdAt': 1700000070, 'run_id': '0', 'role': 'assistant', 'content': [{'type': 'text', 'text': 'Hello! Let me quickly look up your account details.'}]}, {'createdAt': 1700000075, 'run_id': '0', 'role': 'assistant', 'content': [{'type': 'tool_call', 'tool_call': {'id': 'tool_call_20250310_001', 'type': 'function', 'function': {'name': 'get_orders', 'arguments': {'account_number': '888'}}}}]}, {'createdAt': 1700000080, 'run_id': '0', 'tool_call_id': 'tool_call_20250310_001', 'role': 'tool', 'content': [{'type': 'tool_result', 'tool_result': '[{ "order_id": "123" }, { "order_id": "124" }]'}]}, {'createdAt': 1700000085, 'run_id': '0', 'role': 'assistant', 'content': [{'type': 'text', 'text': 'Thanks for your patience. I see two orders on your account. Let me fetch the details for both.'}]}, {'createdAt': 1700000090, 'run_id': '0', 'role': 'assistant', 'content': [{'type': 'tool_call', 'tool_call': {'id': 'tool_call_20250310_002', 'type': 'function', 'function': {'name': 'get_order', 'arguments': {'order_id': '123'}}}}, {'type': 'tool_call', 'tool_call': {'id': 'tool_call_20250310_003', 'type': 'function', 'function': {'name': 'get_order', 'arguments': {'order_id': '124'}}}}]}, {'createdAt': 1700000095, 'run_id': '0', 'tool_call_id': 'tool_call_20250310_002', 'role': 'tool', 'content': [{'type': 'tool_result', 'tool_result': '{ "order": { "id": "123", "status": "shipped", "delivery_date": "2025-03-15" } }'}]}, {'createdAt': 1700000100, 'run_id': '0', 'tool_call_id': 'tool_call_20250310_003', 'role': 'tool', 'content': [{'type': 'tool_result', 'tool_result': '{ "order": { "id": "124", "status": "delayed", "expected_delivery": "2025-03-20" } }'}]}, {'createdAt': 1700000105, 'run_id': '0', 'role': 'assistant', 'content': [{'type': 'text', 'text': 'The order with ID 123 has been shipped and is expected to be delivered on March 15, 2025. However, the order with ID 124 is delayed and should now arrive by March 20, 2025. Is there anything else I can help you with?'}]}]
            tool_definitions = [{'name': 'get_orders', 'description': 'Get the list of orders for a given account number.', 'parameters': {'type': 'object', 'properties': {'account_number': {'type': 'string', 'description': 'The account number to get the orders for.'}}}}, {'name': 'get_order', 'description': 'Get the details of a specific order.', 'parameters': {'type': 'object', 'properties': {'order_id': {'type': 'string', 'description': 'The order ID to get the details for.'}}}}, {'name': 'initiate_return', 'description': 'Initiate the return process for an order.', 'parameters': {'type': 'object', 'properties': {'order_id': {'type': 'string', 'description': 'The order ID for the return process.'}}}}, {'name': 'update_shipping_address', 'description': 'Update the shipping address for a given account.', 'parameters': {'type': 'object', 'properties': {'account_number': {'type': 'string', 'description': 'The account number to update.'}, 'new_address': {'type': 'string', 'description': 'The new shipping address.'}}}}]

            result = evaluator(query=query, response=response, tool_definitions=tool_definitions)

        :keyword query: The query being evaluated, either a string or a list of messages.
        :paramtype query: Union[str, List[dict]]
        :keyword response: The response being evaluated, either a string or a list of messages (full agent response potentially including tool calls)
        :paramtype response: Union[str, List[dict]]
        :keyword tool_definitions: An optional list of messages containing the tool definitions the agent is aware of.
        :paramtype tool_definitions: Union[dict, List[dict]]
        :return: A dictionary with the tool output utilization evaluation results.
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
        """Do Tool Output Utilization evaluation.
        :param eval_input: The input to the evaluator. Expected to contain whatever inputs are needed for the _flow method
        :type eval_input: Dict
        :return: The evaluation result.
        :rtype: Dict
        """
        # we override the _do_eval method as we want the output to be a dictionary,
        # which is a different schema than _base_prompty_eval.py
        if (
            ("query" not in eval_input)
            and ("response" not in eval_input)
            and ("tool_definitions" not in eval_input)
        ):
            raise EvaluationException(
                message="Query, response, and tool_definitions are required inputs to the Tool Output Utilization evaluator.",
                internal_message="Query, response, and tool_definitions are required inputs to the Tool Output Utilization evaluator.",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.MISSING_FIELD,
                target=ErrorTarget.TOOL_OUTPUT_UTILIZATION_EVALUATOR,
            )

        tool_definitions = eval_input["tool_definitions"]
        filtered_tool_definitions = filter_to_used_tools(
            tool_definitions=tool_definitions,
            msgs_lists=[eval_input["query"], eval_input["response"]],
            logger=logger,
        )
        eval_input["tool_definitions"] = reformat_tool_definitions(
            filtered_tool_definitions, logger
        )

        eval_input["query"] = reformat_conversation_history(
            eval_input["query"],
            logger,
            include_system_messages=True,
            include_tool_messages=True,
        )
        eval_input["response"] = reformat_agent_response(
            eval_input["response"], logger, include_tool_messages=True
        )

        llm_output = await self._flow(timeout=self._LLM_CALL_TIMEOUT, **eval_input)
        if isinstance(llm_output, dict):
            output_label = llm_output.get("label", None)
            if output_label is None:
                if logger:
                    logger.warning(
                        "LLM output does not contain 'label' key, returning NaN for the score."
                    )
                output_label = "fail"

            output_label = output_label.lower()
            if output_label not in ["pass", "fail"]:
                if logger:
                    logger.warning(
                        f"LLM output label is not 'pass' or 'fail' (got '{output_label}'), returning NaN for the score."
                    )

            score = 1.0 if output_label == "pass" else 0.0
            score_result = output_label
            reason = llm_output.get("reason", "")

            faulty_details = llm_output.get("faulty_details", [])
            if faulty_details:
                reason += " Issues found: " + "; ".join(faulty_details)

            return {
                f"{self._result_key}": score,
                f"{self._result_key}_result": score_result,
                f"{self._result_key}_reason": reason,
            }
        if logger:
            logger.warning(
                "LLM output is not a dictionary, returning NaN for the score."
            )
        return {self._result_key: math.nan}
