# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import logging
import math
import json
from typing import Dict, List, Union, TypeVar, Optional
from typing_extensions import overload, override
from azure.ai.evaluation._evaluators._common import PromptyEvaluatorBase
from ..._common.utils import reformat_agent_response
from azure.ai.evaluation._exceptions import (
    ErrorBlame,
    ErrorCategory,
    ErrorTarget,
    EvaluationException,
)
from ..._common.utils import reformat_conversation_history
from azure.ai.evaluation._common._experimental import experimental

logger = logging.getLogger(__name__)

T_EvalValue = TypeVar("T_EvalValue")


@experimental
class ToolInputAccuracyEvaluator(PromptyEvaluatorBase[Union[str, float]]):
    """The Tool Input Accuracy evaluator performs a strict binary evaluation (PASS/FAIL) of parameters
    passed to tool calls. It ensures that ALL parameters meet ALL criteria:

        - Parameter grounding: All parameters must be derived from conversation history/query
        - Type compliance: All parameters must match exact types specified in tool definitions
        - Format compliance: All parameters must follow exact format and structure requirements
        - Completeness: All required parameters must be provided
        - No unexpected parameters: Only defined parameters are allowed
        - Value appropriateness: All parameter values must be contextually appropriate

    The evaluator uses strict binary evaluation:
        - PASS: Only when ALL criteria are satisfied perfectly for ALL parameters
        - FAIL: When ANY criterion fails for ANY parameter

    This evaluation focuses on ensuring tool call parameters are completely correct without any tolerance
    for partial correctness.

    :param model_config: Configuration for the Azure OpenAI model.
    :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration]

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_evaluate.py
            :start-after: [START tool_input_accuracy_evaluator]
            :end-before: [END tool_input_accuracy_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call a ToolInputAccuracyEvaluator.

    .. admonition:: Example using Azure AI Project URL:

        .. literalinclude:: ../samples/evaluation_samples_evaluate_fdp.py
            :start-after: [START tool_input_accuracy_evaluator]
            :end-before: [END tool_input_accuracy_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call ToolInputAccuracyEvaluator using Azure AI Project URL in the following format
                https://{resource_name}.services.ai.azure.com/api/projects/{project_name}

    .. note::

        To align with our support of a diverse set of models, an output key without the `gpt_` prefix has been added.
        To maintain backwards compatibility, the old key with the `gpt_` prefix is still be present in the output;
        however, it is recommended to use the new key moving forward as the old key will be deprecated in the future.
    """

    _PROMPTY_FILE = "tool_input_accuracy.prompty"
    _RESULT_KEY = "tool_input_accuracy"

    _NO_TOOL_CALLS_MESSAGE = "No tool calls found in response or provided tool_calls."
    _NO_TOOL_DEFINITIONS_MESSAGE = "Tool definitions must be provided."
    _TOOL_DEFINITIONS_MISSING_MESSAGE = "Tool definitions for all tool calls must be provided."

    def __init__(
        self,
        model_config,
        *,
        credential=None,
        **kwargs,
    ):
        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, self._PROMPTY_FILE)
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
        tool_definitions: Union[dict, List[dict]],
        tool_calls: Optional[Union[dict, List[dict]]] = None,
        response: Optional[Union[str, List[dict]]] = None,
    ) -> Dict[str, Union[str, float]]:
        """
        Evaluate tool input accuracy of tool calls.

        :keyword query: Query or Chat history up to the message that has the tool call being evaluated.
        :paramtype query: Union[str, List[dict]]
        :keyword tool_definitions: List of tool definitions whose calls are being evaluated.
        :paramtype tool_definitions: Union[dict, List[dict]]
        :keyword tool_calls: Optional List of tool calls to evaluate. If not provided response should be provided and should have
            tool call(s) in it.
        :paramtype tool_calls: Optional[Union[dict, List[dict]]]
        :keyword response: Optional response to be evaluated alongside the tool calls.
            If provided all tool calls in response will be evaluated when tool_calls parameter is not provided.
            If provided and tool_calls parameter is provided, only the tool calls in tool_calls parameter will be evaluated.
                If response has extra tool calls they will not be evaluated, response will be used to extract any tool calls that are needed for evaluating a certain tool call.
            Recommended to provide it when there are tool calls that depend on output of a previous tool call.
        :paramtype response: Optional[Union[str, List[dict]]]
        :return: The tool input accuracy evaluation results.
        :rtype: Dict[str, Union[str, float]]
        """

    def _convert_kwargs_to_eval_input(self, **kwargs):
        """Convert kwargs to evaluation input format.

        :keyword kwargs: The inputs to convert.
        :type kwargs: Dict
        :return: The formatted evaluation input.
        :rtype: Dict
        """
        # Collect inputs
        tool_calls = kwargs.get("tool_calls")
        tool_definitions = kwargs.get("tool_definitions", [])  # Default to empty list
        query = kwargs.get("query")
        response = kwargs.get("response")

        # Extract tool calls from response if not provided directly
        if response:
            parsed_tool_calls = self._parse_tools_from_response(response)
            if parsed_tool_calls:
                tool_calls = parsed_tool_calls

        if not tool_calls:
            return {"error_message": self._NO_TOOL_CALLS_MESSAGE}

        if not isinstance(tool_calls, list):
            tool_calls = [tool_calls]
        if not isinstance(tool_definitions, list):
            tool_definitions = [tool_definitions] if tool_definitions else []

        tool_calls = reformat_agent_response(tool_calls, include_tool_calls=True)

        try:
            needed_tool_definitions = self._extract_needed_tool_definitions(
                tool_calls, tool_definitions, ErrorTarget.TOOL_INPUT_ACCURACY_EVALUATOR
            )
        except EvaluationException as e:
            # Check if this is because no tool definitions were provided at all
            if len(tool_definitions) == 0:
                return {"error_message": self._NO_TOOL_DEFINITIONS_MESSAGE}
            else:
                return {"error_message": self._TOOL_DEFINITIONS_MISSING_MESSAGE}

        if len(needed_tool_definitions) == 0:
            return {"error_message": self._NO_TOOL_DEFINITIONS_MESSAGE}

        # Prettify tool calls for LLM evaluation
        prettified_tool_calls = self._prettify_raw_tool_calls(tool_calls)

        return {
            "query": query,
            "tool_calls": prettified_tool_calls,  # Use prettified tool calls for LLM
            "tool_definitions": needed_tool_definitions,
        }

    @override
    async def _do_eval(self, eval_input: Dict) -> Dict[str, Union[float, str]]:
        """Do Tool Input Accuracy evaluation.

        :param eval_input: The input to the evaluator.
        :type eval_input: Dict
        :return: A dictionary containing the result of the evaluation.
        :rtype: Dict[str, Union[str, float]]
        """
        # Format conversation history for cleaner evaluation
        if "query" in eval_input:
            eval_input["query"] = reformat_conversation_history(
                eval_input["query"], logger, include_system_messages=True, include_tool_calls=True
            )

        # Call the LLM to evaluate
        llm_output = await self._flow(timeout=self._LLM_CALL_TIMEOUT, **eval_input)

        if isinstance(llm_output, dict):
            result = llm_output.get("result", None)
            if result not in [0, 1]:
                raise EvaluationException(
                    message=f"Invalid result value: {result}. Expected 0 or 1.",
                    internal_message="Invalid result value.",
                    category=ErrorCategory.FAILED_EXECUTION,
                    blame=ErrorBlame.SYSTEM_ERROR,
                )

            # Add parameter extraction accuracy post-processing
            details = llm_output.get("details", {})
            if details:
                parameter_extraction_accuracy = self._calculate_parameter_extraction_accuracy(details)
                details["parameter_extraction_accuracy"] = parameter_extraction_accuracy

            # Format the output
            explanation = llm_output.get("chain_of_thought", "")
            score_result = "pass" if result == 1 else "fail"
            response_dict = {
                self._result_key: result,
                f"{self._result_key}_result": score_result,
                f"{self._result_key}_reason": explanation,
                "details": details,
            }
            return response_dict

        else:
            raise EvaluationException(
                message="Tool input accuracy evaluator returned invalid output.",
                blame=ErrorBlame.SYSTEM_ERROR,
                category=ErrorCategory.FAILED_EXECUTION,
                target=ErrorTarget.TOOL_INPUT_ACCURACY_EVALUATOR,
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
        if isinstance(eval_input, dict) and eval_input.get("error_message"):
            # If there is an error message, return not applicable result
            return self._not_applicable_result(eval_input.get("error_message"), 1)
        # Do the evaluation
        result = await self._do_eval(eval_input)
        # Return the result
        return result

    def _prettify_raw_tool_calls(self, tool_calls):
        """Prettify raw tool call objects into readable format for LLM evaluation.
        
        :param tool_calls: List of raw tool call objects
        :type tool_calls: List[Dict]
        :return: List of prettified tool call strings
        :rtype: List[str]
        """
        if not tool_calls:
            return []
        
        if not isinstance(tool_calls, list):
            tool_calls = [tool_calls]
        
        prettified = []
        for call in tool_calls:
            if isinstance(call, dict):
                func_name = call.get("name", "unknown_function")
                args = call.get("arguments", {})
                
                # Format arguments
                if isinstance(args, dict):
                    args_str = ", ".join(f'{k}="{v}"' for k, v in args.items())
                elif isinstance(args, str):
                    try:
                        parsed_args = json.loads(args)
                        args_str = ", ".join(f'{k}="{v}"' for k, v in parsed_args.items())
                    except (json.JSONDecodeError, TypeError):
                        args_str = f'args="{args}"'
                else:
                    args_str = ""
                
                prettified.append(f"[TOOL_CALL] {func_name}({args_str})")
        
        return prettified

    def _calculate_parameter_extraction_accuracy(self, details):
        """Calculate parameter extraction accuracy from the evaluation details.

        :param details: The details dictionary from the LLM evaluation output
        :type details: Dict
        :return: Parameter extraction accuracy as a percentage
        :rtype: float
        """
        total_parameters = details.get("total_parameters_passed", 0)
        correct_parameters = details.get("correct_parameters_passed", 0)

        if total_parameters == 0:
            return 100.0  # If no parameters were passed, accuracy is 100%

        accuracy = (correct_parameters / total_parameters) * 100
        return round(accuracy, 2)

    @override
    def __call__(  # pylint: disable=docstring-missing-param
        self,
        *args,
        **kwargs,
    ):
        """
        Evaluate tool input accuracy of tool calls.

        :keyword query: Query or Chat history up to the message that has the tool call being evaluated.
        :paramtype query: Union[str, List[dict]]
        :keyword tool_definitions: List of tool definitions whose calls are being evaluated.
        :paramtype tool_definitions: Union[dict, List[dict]]
        :keyword tool_calls: Optional List of tool calls to evaluate. If not provided response should be provided and should have
            tool call(s) in it.
        :paramtype tool_calls: Optional[Union[dict, List[dict]]]
        :keyword response: Optional response to be evaluated alongside the tool calls.
            If provided all tool calls in response will be evaluated when tool_calls parameter is not provided.
            If provided and tool_calls parameter is provided, only the tool calls in tool_calls parameter will be evaluated.
                If response has extra tool calls they will not be evaluated, response will be used to extract any tool calls that are needed for evaluating a certain tool call.
            Recommended to provide it when there are tool calls that depend on output of a previous tool call.
        :paramtype response: Optional[Union[str, List[dict]]]
        :return: The tool input accuracy evaluation results.
        :rtype: Dict[str, Union[str, float]]
        """
        return super().__call__(*args, **kwargs)
