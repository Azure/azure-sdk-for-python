# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import logging
import math
from typing import Dict, List, Union, TypeVar, Optional
from typing_extensions import overload, override
from azure.ai.evaluation._evaluators._common import PromptyEvaluatorBase
from azure.ai.evaluation._exceptions import (
    ErrorBlame,
    ErrorCategory,
    ErrorTarget,
    EvaluationException,
)
from ..._common.utils import check_score_is_valid, reformat_conversation_history
from azure.ai.evaluation._common._experimental import experimental

logger = logging.getLogger(__name__)


@experimental
class _ToolSelectionEvaluator(PromptyEvaluatorBase[Union[str, float]]):
    """The Tool Selection evaluator assesses the appropriateness and efficiency of tool choices made by an AI agent by examining:
        - Relevance of selected tools to the conversation.
        - Completeness of tool selection according to task requirements.
        - Efficiency in avoiding unnecessary or redundant tools.

    The evaluator uses a binary scoring system:
        - Score 0 (Fail): Tools selected are irrelevant, incorrect, or missing essential tools
        - Score 1 (Pass): All needed tools are selected, even if there are redundant tools

    This evaluation focuses on measuring whether the right tools were chosen for the task,
    regardless of how those tools were executed or their parameter correctness.

    :param model_config: Configuration for the Azure OpenAI model.
    :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration]

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_evaluate.py
            :start-after: [START tool_selection_evaluator]
            :end-before: [END tool_selection_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call a _ToolSelectionEvaluator.

    .. admonition:: Example using Azure AI Project URL:

        .. literalinclude:: ../samples/evaluation_samples_evaluate_fdp.py
            :start-after: [START tool_selection_evaluator]
            :end-before: [END tool_selection_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call _ToolSelectionEvaluator using Azure AI Project URL in the following format
                https://{resource_name}.services.ai.azure.com/api/projects/{project_name}

    .. note::

        To align with our support of a diverse set of models, an output key without the `gpt_` prefix has been added.
        To maintain backwards compatibility, the old key with the `gpt_` prefix is still be present in the output;
        however, it is recommended to use the new key moving forward as the old key will be deprecated in the future.
    """

    _PROMPTY_FILE = "tool_selection.prompty"
    _RESULT_KEY = "tool_selection"

    _NO_TOOL_CALLS_MESSAGE = "No tool calls found in response or provided tool_calls."
    _NO_TOOL_DEFINITIONS_MESSAGE = "Tool definitions must be provided."
    _TOOL_DEFINITIONS_MISSING_MESSAGE = "Tool definitions for all tool calls must be provided."
    _INVALID_SCORE_MESSAGE = "Tool selection score must be 0 or 1."

    id = "azureai://built-in/evaluators/tool_selection"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    @override
    def __init__(self, model_config, *, threshold=1, credential=None, **kwargs):
        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, self._PROMPTY_FILE)
        self.threshold = threshold
        super().__init__(
            model_config=model_config,
            prompty_file=prompty_path,
            result_key=self._RESULT_KEY,
            threshold=1,
            credential=credential,
            **kwargs,
        )

    @override
    def __call__(  # pylint: disable=docstring-missing-param
        self,
        *args,
        **kwargs,
    ):
        """
        Evaluate tool selection quality for a given query, tool definitions, and tool calls.

        For detailed parameter types and return value documentation, see the class documentation.
        """
        return super().__call__(*args, **kwargs)

    def _convert_kwargs_to_eval_input(self, **kwargs):
        """Convert an arbitrary input into a list of inputs for evaluators.
        It is assumed that evaluators generally make use of their inputs in one of two ways.
        Either they receive a collection of keyname inputs that are all single values
        (like a query and response), or they receive conversation that is a list of dictionary
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
            raise EvaluationException(
                message=self._NO_TOOL_CALLS_MESSAGE,
                category=ErrorCategory.NOT_APPLICABLE,
                target=ErrorTarget.TOOL_SELECTION_EVALUATOR,
                blame=ErrorBlame.USER_ERROR,
            )

        if not isinstance(tool_calls, list):
            tool_calls = [tool_calls]
        if not isinstance(tool_definitions, list):
            tool_definitions = [tool_definitions] if tool_definitions else []

        try:
            needed_tool_definitions = self._extract_needed_tool_definitions(
                tool_calls, tool_definitions, ErrorTarget.TOOL_SELECTION_EVALUATOR
            )
        except EvaluationException:
            # Re-raise the exception from _extract_needed_tool_definitions as it already has specific error details
            raise

        # Check if no tool definitions were found at all (including built-in tools)
        if len(needed_tool_definitions) == 0:
            raise EvaluationException(
                message=self._NO_TOOL_DEFINITIONS_MESSAGE,
                category=ErrorCategory.NOT_APPLICABLE,
                target=ErrorTarget.TOOL_SELECTION_EVALUATOR,
                blame=ErrorBlame.USER_ERROR,
            )

        # Extract only tool names from tool calls, removing parameters and results
        tool_names = self._extract_tool_names_from_calls(tool_calls)

        return {
            "query": query,
            "tool_calls": tool_names,  # Only tool names, no parameters
            "tool_definitions": needed_tool_definitions,
        }

    @override
    async def _do_eval(self, eval_input: Dict) -> Dict[str, Union[float, str]]:
        """Do Tool Selection evaluation.

        :param eval_input: The input to the evaluator.
        :type eval_input: Dict
        :return: A dictionary containing the result of the evaluation.
        :rtype: Dict[str, Union[str, float]]
        """
        if eval_input.get("query") is None:
            raise EvaluationException(
                message=("Query is a required input to the Tool Selection evaluator."),
                internal_message=("Query is a required input to the Tool Selection evaluator."),
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.INVALID_VALUE,
                target=ErrorTarget.TOOL_SELECTION_EVALUATOR,
            )

        # Format conversation history for cleaner evaluation
        eval_input["query"] = reformat_conversation_history(
            eval_input["query"], logger, include_system_messages=True, include_tool_messages=True
        )

        # Call the LLM to evaluate
        prompty_output_dict = await self._flow(timeout=self._LLM_CALL_TIMEOUT, **eval_input)
        llm_output = prompty_output_dict.get("llm_output", {})

        if isinstance(llm_output, dict):
            score = llm_output.get("score", None)
            if score not in [0, 1]:
                raise EvaluationException(
                    message=f"Invalid score value: {score}. Expected 0 or 1.",
                    internal_message="Invalid score value.",
                    category=ErrorCategory.FAILED_EXECUTION,
                    blame=ErrorBlame.SYSTEM_ERROR,
                )

            # Format the output
            explanation = llm_output.get("explanation", "")
            score = int(score)  # Keep as int since it's binary (0 or 1)
            score_result = "pass" if score == 1 else "fail"

            # Add tool selection accuracy post-processing
            details = llm_output.get("details", {})
            if details:
                tool_selection_accuracy = self._calculate_tool_selection_accuracy(details)
                details["tool_selection_accuracy"] = tool_selection_accuracy

            response_dict = {
                self._result_key: score,
                f"{self._result_key}_result": score_result,
                f"{self._result_key}_threshold": self._threshold,
                f"{self._result_key}_reason": explanation,
                f"{self._result_key}_details": details,
                f"{self._result_key}_prompt_tokens": prompty_output_dict.get("input_token_count", 0),
                f"{self._result_key}_completion_tokens": prompty_output_dict.get("output_token_count", 0),
                f"{self._result_key}_total_tokens": prompty_output_dict.get("total_token_count", 0),
                f"{self._result_key}_finish_reason": prompty_output_dict.get("finish_reason", ""),
                f"{self._result_key}_model": prompty_output_dict.get("model_id", ""),
                f"{self._result_key}_sample_input": prompty_output_dict.get("sample_input", ""),
                f"{self._result_key}_sample_output": prompty_output_dict.get("sample_output", ""),
            }
            return response_dict

        else:
            raise EvaluationException(
                message="Tool selection evaluator returned invalid output.",
                blame=ErrorBlame.SYSTEM_ERROR,
                category=ErrorCategory.FAILED_EXECUTION,
                target=ErrorTarget.TOOL_SELECTION_EVALUATOR,
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
        result = await self._do_eval(eval_input)

        return result

    def _calculate_tool_selection_accuracy(self, details):
        """Calculate tool selection accuracy from the evaluation details.

        :param details: The details dictionary from the LLM evaluation output
        :type details: Dict
        :return: Tool selection accuracy as a percentage
        :rtype: float
        """
        correct_tool_selections = details.get("correct_tool_selections", 0)
        wrong_tool_selections = details.get("wrong_tool_selections", 0)
        total_tools_called = correct_tool_selections + wrong_tool_selections

        if total_tools_called > 0:
            accuracy = (correct_tool_selections / total_tools_called) * 100
            return round(accuracy, 2)
        else:
            return 100.0
