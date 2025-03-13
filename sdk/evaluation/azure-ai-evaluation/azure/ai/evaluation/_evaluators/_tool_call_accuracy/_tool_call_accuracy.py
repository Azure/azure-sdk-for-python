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
from azure.ai.evaluation._common.utils import remove_optional_singletons, parse_quality_evaluator_reason_score
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from azure.ai.evaluation._common.constants import PROMPT_BASED_REASON_EVALUATORS

logger = logging.getLogger(__name__)

T_EvalValue = TypeVar("T_EvalValue")

try:
    from azure.ai.projects.models import ToolDefinition, ThreadMessage, RunStepToolCall
except Exception as ex:
    logger.warning("Please install azure-ai-projects sdk to use this evaluator. ")




class ToolCallAccuracyEvaluator(PromptyEvaluatorBase[Union[str, float]]):
    """The Tool Call Accuracy evaluator assesses how accurately an AI uses tools by examining:
        - Relevance to the conversation
        - Parameter correctness according to tool definitions
        - Parameter value extraction from the conversation
        - Potential usefulness of the tool call

    The evaluator uses a binary scoring system (0 or 1):
        - Score 0: The tool call is irrelevant or contains information not in the conversation/definition
        - Score 1: The tool call is relevant with properly extracted parameters from the conversation

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

    .. note::

        To align with our support of a diverse set of models, an output key without the `gpt_` prefix has been added.
        To maintain backwards compatibility, the old key with the `gpt_` prefix is still be present in the output;
        however, it is recommended to use the new key moving forward as the old key will be deprecated in the future.
    """

    _PROMPTY_FILE = "tool_call_accuracy.prompty"
    _RESULT_KEY = "tool_call_accuracy"

    id = "id"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    @override
    def __init__(self, model_config):
        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, self._PROMPTY_FILE)
        super().__init__(model_config=model_config, prompty_file=prompty_path, result_key=self._RESULT_KEY)

    # Types are the closet from Agent 1.0 I could find since Agent 2.0 python classes does not exist
    @overload
    def __call__(
        self,
        *,
        query: Union[str, List["ThreadMessage"]], # Chat history upto the message that has the tool call being evaluated. Not including the message that has tool call. -- chat history
        tool_definitions: Union["ToolDefinition", List["ToolDefinition"]], # Definition of tool whose call is being evaluated
        tool_calls: Union["ToolCall", List["ToolCall"]]  = None,
        response: Union[str, List["ThreadMessage"]] = None
    ) -> Dict[str, Union[str, float]]:
        """
        Evaluate tool call accuracy. Accepts a query, tool definitions, and tool calls for evaluation.

        :keyword query: Query or Chat history up to the message that has the tool call being evaluated.
        :paramtype query: Union[str, List[ThreadMessage]]
        :keyword tool_definitions: List of tool definitions whose calls are being evaluated.
        :paramtype tool_definitions: List[ToolDefinition]
        :keyword tool_calls: Optional List of tool calls to evaluate. If not provided response should be provided and should have
            tool call(s) in it.
        :paramtype tool_calls: List[ToolCall]
        :keyword response: Optional response to be evaluated alongside the tool calls.
            If provided all tool calls in response will be evaluated when tool_calls parameter is not provided.
            If provided and tool_calls parameter is provided, only the tool calls in tool_calls parameter will be evaluated.
                If response has extra tool calls they will not be evaluated, response will be used to extract any tool calls that are needed for evaluating a certain tool call.
            Recommended to provide it when there are tool calls that depend on output of a previous tool call.
        :paramtype response: Union[str, List[ThreadMessage]]
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
        tool_calls = kwargs.get("tool_calls", None)
        tool_definitions = kwargs.get("tool_definitions")
        query = kwargs.get("query", None)
        response = kwargs.get("response", None)

        if response is None and tool_calls is None:
            raise EvaluationException(
                message="Either response or tool_calls must be provided.",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.MISSING_FIELD,
                target=ErrorTarget.TOOL_CALL_ACCURACY_EVALUATOR,
            )

        if tool_definitions is None:
            raise EvaluationException(
                message="Tool definitions must be provided.",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.MISSING_FIELD,
                target=ErrorTarget.TOOL_CALL_ACCURACY_EVALUATOR,
            )

        # TODO : Support classes that represents tool calls, messages etc once client side definitions are available
        if tool_calls is None:
            # Extract tool calls from response if not provided
            tool_calls = []
            if isinstance(response, list):
                for message in response:
                    if message.get("role") == "assistant":
                        tool_calls.extend([content for content in message.get("content")
                                        if content.get("type") == "tool_call" and content.get("tool_call").get("type") == "function"])
            else:
                raise EvaluationException(
                    message="response does not have tool calls. Either provide tool_calls or response with tool calls.",
                    blame=ErrorBlame.USER_ERROR,
                    category=ErrorCategory.MISSING_FIELD,
                    target=ErrorTarget.TOOL_CALL_ACCURACY_EVALUATOR,
                )

        if not isinstance(tool_calls, list):
            tool_calls = [tool_calls]

        if not isinstance(tool_definitions, list):
            tool_definitions = [tool_definitions]

        eval_inputs = []
        # TODO : When evaluating an agent tool that depends on the output of a previous tool call,
        # we need to provide the output of the previous tool call as part of messages.
        for tool_call in tool_calls:
            if isinstance(tool_call, dict) and tool_call.get("type") == "tool_call" and tool_call.get("tool_call").get("type") == "function":  # TODO assuming dict here but it can be a class
                function_name = tool_call.get("tool_call").get("function").get("name")
                tool_definition = [tool for tool in tool_definitions if tool.get("name") == function_name]
                if len(tool_definition) > 0:
                    tool_definition = tool_definition
                else:
                    raise EvaluationException(
                        message="Tool definition not found",
                        blame=ErrorBlame.USER_ERROR,
                        category=ErrorCategory.INVALID_VALUE,
                        target=ErrorTarget.TOOL_CALL_ACCURACY_EVALUATOR,
                    )
                eval_inputs.append({"messages": query, "tool_call": tool_call, "tool_definition": tool_definition})

        return eval_inputs

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
        llm_output = await self._flow(timeout=self._LLM_CALL_TIMEOUT, **eval_input)

        score = math.nan
        if llm_output:
            # Parse out score and reason from evaluators known to possess them.
            if self._result_key in PROMPT_BASED_REASON_EVALUATORS:
                score, reason = parse_quality_evaluator_reason_score(llm_output, score_range="[0-1]")
                return {
                    self._result_key: float(score),
                    f"{self._result_key}_reason": reason,
                }
            match = re.search(r"\d", llm_output)
            if match:
                score = float(match.group())
            return {self._result_key: float(score)}
        return {self._result_key: float(score)}

    def _aggregate_results(self, per_turn_results):
        """Aggregate the evaluation results of each conversation turn into a single result.

        Exact implementation might need to vary slightly depending on the results produced.
        Default behavior is to average the all number-based outputs.

        :param per_turn_results: List of evaluation results for each turn in the conversation.
        :type per_turn_results: List[Dict]
        :return: A dictionary containing aggregated results, with numeric metrics having their
        means as top-level values in the dictionary, and all original
        values (including non-numerics) located in under the "evaluation_per_turn" key,
        which each sub-key being a metric and each sub-value being a the list of that metric's
        per-turn values.
        :rtype: AggregateResult[T_EvalValue]
        """

        aggregated: Dict[str, Union[float, Dict[str, List[T_EvalValue]]]] = {}
        evaluation_per_turn: Dict[str, List[T_EvalValue]] = {}

        # Go over each turn, and rotate the results into a
        # metric: List[values] format for the evals_per_turn dictionary.
        for turn in per_turn_results:
            for metric, value in turn.items():
                if metric not in evaluation_per_turn:
                    evaluation_per_turn[metric] = []
                evaluation_per_turn[metric].append(value)

        # Find and average all numeric values
        for metric, values in evaluation_per_turn.items():
            if all(isinstance(value, (int, float)) for value in values):
                aggregated[metric] = self._conversation_aggregation_function(cast(List[Union[int, float]], values))
        # Slap the per-turn results back in.
        aggregated["evaluation_per_tool_call"] = evaluation_per_turn
        return aggregated

    @override
    def __call__(  # pylint: disable=docstring-missing-param
        self,
        *args,
        **kwargs,
    ):
        """
        Evaluate tool call accuracy. Accepts a query, tool definitions, and tool calls for evaluation.

        :keyword query: Query or Chat history up to the message that has the tool call being evaluated.
        :paramtype query: Union[str, List[ThreadMessage]]
        :keyword tool_definitions: List of tool definitions whose calls are being evaluated.
        :paramtype tool_definitions: List[ToolDefinition]
        :keyword tool_calls: Optional List of tool calls to evaluate. If not provided response should be provided and should have
            tool call(s) in it.
        :paramtype tool_calls: List[ToolCall]
        :keyword response: Optional response to be evaluated alongside the tool calls.
            If provided all tool calls in response will be evaluated when tool_calls parameter is not provided.
            If provided and tool_calls parameter is provided, only the tool calls in tool_calls parameter will be evaluated.
                If response has extra tool calls they will not be evaluated, response will be used to extract any tool calls that are needed for evaluating a certain tool call.
            Recommended to provide it when there are tool calls that depend on output of a previous tool call.
        :paramtype response: Union[str, List[ThreadMessage]]
        :return: The tool selection evaluation results.
        :rtype: Dict[str, Union[str, float]]
        """
        return super().__call__(*args, **kwargs)
