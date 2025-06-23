# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import math
import os
import logging
import re
from typing import Dict, List, Union, TypeVar, cast
from typing_extensions import overload, override
from azure.ai.evaluation._evaluators._common import PromptyEvaluatorBase
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from ..._common.utils import check_score_is_valid
from azure.ai.evaluation._common._experimental import experimental

logger = logging.getLogger(__name__)

T_EvalValue = TypeVar("T_EvalValue")

@experimental
class ToolCallAccuracyEvaluator(PromptyEvaluatorBase[Union[str, float]]):
    """The Tool Call Accuracy evaluator assesses how accurately an AI uses tools by examining:
        - Relevance to the conversation
        - Parameter correctness according to tool definitions
        - Parameter value extraction from the conversation

    The evaluator uses a scoring rubric of 1 to 5:
        - Score 1: The tool calls are irrelevant
        - Score 2: The tool calls are partially relevant, but not enough tools were called or the parameters were not correctly passed
        - Score 3: The tool calls are relevant, but there were unncessary, excessive tool calls made
        - Score 4: The tool calls are relevant, but some tools returned errors and agent retried calling them again and succeeded
        - Score 5: The tool calls are relevant, and all parameters were correctly passed

    This evaluation focuses on measuring whether tool calls meaningfully contribute to addressing
    user needs while properly following tool definitions and using information present in the
    conversation history.

    :param model_config: Configuration for the Azure OpenAI model.
    :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration]

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_evaluate.py
            :start-after: [START tool_call_accuracy_evaluator]
            :end-before: [END tool_call_accuracy_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call a ToolCallAccuracyEvaluator.

    .. admonition:: Example using Azure AI Project URL:
        
        .. literalinclude:: ../samples/evaluation_samples_evaluate_fdp.py
            :start-after: [START tool_call_accuracy_evaluator]
            :end-before: [END tool_call_accuracy_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call ToolCallAccuracyEvaluator using Azure AI Project URL in the following format 
                https://{resource_name}.services.ai.azure.com/api/projects/{project_name}

    .. note::

        To align with our support of a diverse set of models, an output key without the `gpt_` prefix has been added.
        To maintain backwards compatibility, the old key with the `gpt_` prefix is still be present in the output;
        however, it is recommended to use the new key moving forward as the old key will be deprecated in the future.
    """

    _PROMPTY_FILE = "tool_call_accuracy.prompty"
    _RESULT_KEY = "tool_call_accurate"

    _MAX_TOOL_CALL_ACCURACY_SCORE = 5
    _MIN_TOOL_CALL_ACCURACY_SCORE = 1
    _DEFAULT_TOOL_CALL_ACCURACY_SCORE = 3

    id = "id"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    @override
    def __init__(self, model_config, *,
                 threshold=_DEFAULT_TOOL_CALL_ACCURACY_SCORE,
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
        query: Union[str, List[dict]],
        tool_definitions: Union[dict, List[dict]],
        tool_calls: Union[dict, List[dict]]  = None,
        response: Union[str, List[dict]] = None
    ) -> Dict[str, Union[str, float]]:
        """
        Evaluate tool call accuracy. Accepts a query, tool definitions, and tool calls for evaluation.

        :keyword query: Query or Chat history up to the message that has the tool call being evaluated.
        :paramtype query: Union[str, List[dict]]
        :keyword tool_definitions: List of tool definitions whose calls are being evaluated.
        :paramtype tool_definitions: Union[dict, List[dict]]
        :keyword tool_calls: Optional List of tool calls to evaluate. If not provided response should be provided and should have
            tool call(s) in it.
        :paramtype tool_calls: Union[dict, List[dict]]
        :keyword response: Optional response to be evaluated alongside the tool calls.
            If provided all tool calls in response will be evaluated when tool_calls parameter is not provided.
            If provided and tool_calls parameter is provided, only the tool calls in tool_calls parameter will be evaluated.
                If response has extra tool calls they will not be evaluated, response will be used to extract any tool calls that are needed for evaluating a certain tool call.
            Recommended to provide it when there are tool calls that depend on output of a previous tool call.
        :paramtype response: Union[str, List[dict]]
        :return: The tool selection evaluation results.
        :rtype: Dict[str, Union[str, float]]
        """

    def _convert_kwargs_to_eval_input(self, **kwargs):
        """Convert an arbitrary input into a list of inputs for evaluators.
        It is assumed that evaluators generally make use of their inputs in one of two ways.
        Either they receive a collection of keyname inputs that are all single values
        (like a query and response), or they receive conversation that iss a list of dictionary
        values.

        The self._singleton_inputs list assigned during initialization is used to find and extract
        singleton keywords, and self._allow_conversation_input is used to determine if a conversation
        is a valid input.

        If both conversations and singletons are allowed, the function will raise an exception if both
        are inputted.

        This function must be overridden by child classes IF they need to both a conversation and
        other inputs to be passed in.

        :keyword kwargs: The inputs to convert.
        :type kwargs: Dict
        :return: A list of arbitrary values that are valid inputs for this evaluator's do_eval function.
        :rtype: List
        """
        # TODO add warning that only tool calls of type function are supported
        # Collect inputs
        tool_calls = kwargs.get("tool_calls")
        tool_definitions = kwargs.get("tool_definitions")
        query = kwargs.get("query")
        response = kwargs.get("response")

        # TODO : Support classes that represents tool calls, messages etc once client side definitions are available
        if response:
            parsed_tool_calls = self._parse_tools_from_response(response)
            if parsed_tool_calls:
                tool_calls = parsed_tool_calls

        if not tool_calls:
            return {"error_message": "No tool calls found in response or provided tool_calls."}
        if not tool_definitions or len(tool_definitions) == 0:
            return {"error_message": "Tool definitions must be provided."}

        if not isinstance(tool_calls, list):
            tool_calls = [tool_calls]
        if not isinstance(tool_definitions, list):
            tool_definitions = [tool_definitions]

        try:
            needed_tool_definitions = self._extract_needed_tool_definitions(tool_calls, tool_definitions)
        except EvaluationException as e:
            return {"error_message": "Tool definitions for all tool calls must be provided."}
        if len(needed_tool_definitions) == 0:
            return {"error_message": "Tool definitions for all tool calls must be provided."}

        return {
            "query": query,
            "tool_calls": tool_calls,
            "tool_definitions": needed_tool_definitions
        }
        

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
        # Single LLM call for all tool calls
        llm_output = await self._flow(timeout=self._LLM_CALL_TIMEOUT, **eval_input)

        if isinstance(llm_output, dict):
            score = llm_output.get("tool_calls_success_level", None)
            if not score or not check_score_is_valid(score, ToolCallAccuracyEvaluator._MIN_TOOL_CALL_ACCURACY_SCORE, ToolCallAccuracyEvaluator._MAX_TOOL_CALL_ACCURACY_SCORE):
                raise EvaluationException(
                    message=f"Invalid score value: {score}. Expected a number in range [{ToolCallAccuracyEvaluator._MIN_TOOL_CALL_ACCURACY_SCORE}, {ToolCallAccuracyEvaluator._MAX_TOOL_CALL_ACCURACY_SCORE}].",
                    internal_message="Invalid score value.",
                    category=ErrorCategory.FAILED_EXECUTION,
                    blame=ErrorBlame.SYSTEM_ERROR,
                )
            
            # Format the output
            reason = llm_output.get("chain_of_thought", "")
            score = float(score)
            score_result = 'pass' if score >= self.threshold else 'fail'
            response_dict = {
                self._result_key: score,
                f"{self._result_key}_result": score_result,
                f"{self._result_key}_threshold": self.threshold,
                f"{self._result_key}_reason": reason,
                'applicable': True,
                'per_tool_call_details': llm_output.get('additional_details', {}),
                'excess_tool_calls': llm_output.get('excess_tool_calls', {}),
                'missing_tool_calls': llm_output.get('missing_tool_calls', {}),
            }
            return response_dict
            
        else:
            raise EvaluationException(
            message="Tool call accuracy evaluator returned invalid output.",
            blame=ErrorBlame.SYSTEM_ERROR,
            category=ErrorCategory.FAILED_EXECUTION,
            target=ErrorTarget.TOOL_CALL_ACCURACY_EVALUATOR,
        )
    
    async def _real_call(self, **kwargs):
        """The asynchronous call where real end-to-end evaluation logic is performed.

        :keyword kwargs: The inputs to evaluate.
        :type kwargs: Dict
        :return: The evaluation result.
        :rtype: Union[DoEvalResult[T_EvalValue], AggregateResult[T_EvalValue]]
        """
        # Convert inputs into list of evaluable inputs.
        eval_input = self._convert_kwargs_to_eval_input(**kwargs)
        if isinstance(eval_input, dict) and eval_input.get('error_message'):
            # If there is an error message, return not applicable result
            return self._not_applicable_result(eval_input.get('error_message'))
        # Do the evaluation
        result = await self._do_eval(eval_input)
        # Return the result
        return result
    
    def _not_applicable_result(self, error_message):
        """Return a result indicating that the tool call is not applicable for evaluation.

        :param eval_input: The input to the evaluator.
        :type eval_input: Dict
        :return: A dictionary containing the result of the evaluation.
        :rtype: Dict[str, Union[str, float]]
        """
        # If no tool calls were made or tool call type is not supported, return not applicable result
        return {
            self._result_key: self._NOT_APPLICABLE_RESULT,
            f"{self._result_key}_result": 'pass',
            f"{self._result_key}_threshold": self.threshold,
            f"{self._result_key}_reason": error_message,
            "applicable": False,
            "per_tool_call_details": {},
            "excess_tool_calls": {},
            "missing_tool_calls": {},

        }
    
    def _parse_tools_from_response(self, response):
        """Parse the response to extract tool calls and results.
        :param response: The response to parse.
        :type response: Union[str, List[dict]]
        :return: List of tool calls extracted from the response.
        :rtype: List[dict]
        """
        tool_calls = []
        tool_results = []
        if isinstance(response, list):
            for message in response:
                if message.get("role") == "assistant":
                    tool_calls.extend([content for content in message.get("content")
                                    if content.get("type") == "tool_call"])
                    tool_results.extend([content for content in message.get("content")
                                    if content.get("type") == "tool_result"])
        # Format the tool calls and results
        for i in range(min(len(tool_calls), len(tool_results))):
            if isinstance(tool_calls[i], dict) and tool_calls[i].get("type") == "tool_call":
                if tool_results[i]["tool_call_id"] == tool_calls[i]["tool_call_id"]:
                    tool_calls[i]["tool_result"] = tool_results[i]

        return tool_calls
    
    def _extract_needed_tool_definitions(self, tool_calls, tool_definitions):
        """Extract the tool definitions that are needed for the provided tool calls.
        :param tool_calls: List of tool calls to evaluate.
        :type tool_calls: List[dict]
        :param tool_definitions: List of tool definitions to use for evaluation.
        :type tool_definitions: List[dict]
        :return: List of tool definitions that are needed for the provided tool calls.
        :rtype: List[dict]
        """
        needed_tool_definitions = []
        for tool_call in tool_calls:
            if isinstance(tool_call, dict) and tool_call.get("type") == "tool_call":
                tool_name = tool_call.get("name")
                tool_definition = [tool for tool in tool_definitions if tool.get("name") == tool_name and tool.get("type", "function") == "function"]
                if len(tool_definition) > 0:
                    needed_tool_definitions.extend(tool_definition)
                else:
                    raise EvaluationException(
                        message=f"Tool definition for {tool_name} not found",
                        blame=ErrorBlame.USER_ERROR,
                        category=ErrorCategory.INVALID_VALUE,
                        target=ErrorTarget.TOOL_CALL_ACCURACY_EVALUATOR,
                    )
        return needed_tool_definitions

    @override
    def __call__(  # pylint: disable=docstring-missing-param
        self,
        *args,
        **kwargs,
    ):
        """
        Evaluate tool call accuracy. Accepts a query, tool definitions, and tool calls for evaluation.

        :keyword query: Query or Chat history up to the message that has the tool call being evaluated.
        :paramtype query: Union[str, List[dict]]
        :keyword tool_definitions: List of tool definitions whose calls are being evaluated.
        :paramtype tool_definitions: Union[dict, List[dict]]
        :keyword tool_calls: Optional List of tool calls to evaluate. If not provided response should be provided and should have
            tool call(s) in it.
        :paramtype tool_calls: Union[dict, List[dict]]
        :keyword response: Optional response to be evaluated alongside the tool calls.
            If provided all tool calls in response will be evaluated when tool_calls parameter is not provided.
            If provided and tool_calls parameter is provided, only the tool calls in tool_calls parameter will be evaluated.
                If response has extra tool calls they will not be evaluated, response will be used to extract any tool calls that are needed for evaluating a certain tool call.
            Recommended to provide it when there are tool calls that depend on output of a previous tool call.
        :paramtype response: Union[str, List[dict]]
        :return: The tool selection evaluation results.
        :rtype: Dict[str, Union[str, float]]
        """
        return super().__call__(*args, **kwargs)
