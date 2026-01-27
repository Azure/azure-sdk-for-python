# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from enum import Enum
from collections import Counter
import json
from typing import Dict, List, Union, Any, Tuple
from typing_extensions import overload, override

from azure.ai.evaluation._constants import EVALUATION_PASS_FAIL_MAPPING
from azure.ai.evaluation._evaluators._common import EvaluatorBase
from azure.ai.evaluation._evaluators._common._validators import TaskNavigationEfficiencyValidator, ValidatorInterface
from azure.ai.evaluation._exceptions import (
    ErrorCategory,
    ErrorTarget,
    EvaluationException,
)


class _TaskNavigationEfficiencyMatchingMode(str, Enum):
    """
    Enumeration of task navigation efficiency matching mode.

    This enum allows you to specify which single matching technique should be used when evaluating
    the efficiency of an agent's tool calls sequence against a ground truth path.
    """

    EXACT_MATCH = "exact_match"
    """
    Binary metric indicating whether the agent's tool calls exactly match the ground truth.

    Returns True only if the agent's tool calls sequence is identical to the expected sequence
    in both order and content (no extra steps, no missing steps, correct order).
    """

    IN_ORDER_MATCH = "in_order_match"
    """
    Binary metric allowing extra steps but requiring correct order of required tool calls.
    
    Returns True if all ground truth steps appear in the agent's sequence in the correct
    order, even if there are additional steps interspersed.
    """

    ANY_ORDER_MATCH = "any_order_match"
    """
    Binary metric allowing both extra steps and different ordering.
    
    Returns True if all ground truth steps appear in the agent's sequence with sufficient
    frequency, regardless of order. Most lenient matching criterion.
    """


class _TaskNavigationEfficiencyEvaluator(EvaluatorBase):
    """
    Evaluates whether an agent's sequence of actions is efficient and follows optimal decision-making patterns.

    The Task Navigation Efficiency Evaluator returns binary matching results between the agent's tool usage trajectory and the ground truth expected steps.
    It has three matching techniques: exact match, in-order match (allows extra steps), and any-order match (allows extra steps and ignores order).
    It also returns precision, recall, and F1 scores in properties bag.

    :param matching_mode: The matching mode to use. Default is "exact_match".
    :type matching_mode: enum[str, _TaskNavigationEfficiencyMatchingMode]

    .. admonition:: Example:

        .. code-block:: python

            from azure.ai.evaluation._evaluators._task_navigation_efficiency import _TaskNavigationEfficiencyEvaluator

            task_navigation_efficiency_eval = _TaskNavigationEfficiencyEvaluator(
                matching_mode=_TaskNavigationEfficiencyMatchingMode.EXACT_MATCH
            )

            # Example 1: Using simple tool names list
            result = path_efficiency_eval(
                response=[
                    {"role": "assistant", "content": [{"type": "tool_call", "tool_call_id": "call_1", "name": "identify_tools_to_call", "arguments": {}}]},
                    {"role": "assistant", "content": [{"type": "tool_call", "tool_call_id": "call_2", "name": "call_tool_A", "arguments": {}}]},
                    {"role": "assistant", "content": [{"type": "tool_call", "tool_call_id": "call_3", "name": "call_tool_B", "arguments": {}}]},
                    {"role": "assistant", "content": [{"type": "tool_call", "tool_call_id": "call_4", "name": "response_synthesis", "arguments": {}}]}
                ],
                ground_truth=["identify_tools_to_call", ""call_tool_A", "call_tool_B", "response_synthesis"]
            )

            # Example 2: Using tool names with parameters (exact parameter matching required)
            result = path_efficiency_eval(
                response=[
                    {"role": "assistant", "content": [{"type": "tool_call", "tool_call_id": "call_1", "name": "search", "arguments": {"query": "weather", "location": "NYC"}}]},
                    {"role": "assistant", "content": [{"type": "tool_call", "tool_call_id": "call_2", "name": "format_result", "arguments": {"format": "json"}}]}
                ],
                ground_truth=(
                    ["search", "format_result"],
                    {
                        "search": {"query": "weather", "location": "NYC"},
                        "format_result": {"format": "json"}
                    }
                )
            )
    """

    id = "azureai://built-in/evaluators/task_navigation_efficiency"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    matching_mode: _TaskNavigationEfficiencyMatchingMode
    """The matching mode to use."""

    _validator: ValidatorInterface

    @override
    def __init__(
        self,
        *,
        matching_mode: Union[
            str, _TaskNavigationEfficiencyMatchingMode
        ] = _TaskNavigationEfficiencyMatchingMode.EXACT_MATCH,
    ):
        # Type checking for metric parameter
        if isinstance(matching_mode, str):
            try:
                self.matching_mode = _TaskNavigationEfficiencyMatchingMode(matching_mode)
            except ValueError:
                raise ValueError(
                    f"matching_mode must be one of {[m.value for m in _TaskNavigationEfficiencyMatchingMode]}, got '{matching_mode}'"
                )
        elif isinstance(matching_mode, _TaskNavigationEfficiencyMatchingMode):
            self.matching_mode = matching_mode
        else:
            raise EvaluationException(
                f"matching_mode must be a string with one of {[m.value for m in _TaskNavigationEfficiencyMatchingMode]} or _TaskNavigationEfficiencyMatchingMode enum, got {type(matching_mode)}",
                internal_message=str(matching_mode),
                target=ErrorTarget.TASK_NAVIGATION_EFFICIENCY_EVALUATOR,
                category=ErrorCategory.INVALID_VALUE,
            )

        # Initialize input validator
        self._validator = TaskNavigationEfficiencyValidator(
            error_target=ErrorTarget.TASK_NAVIGATION_EFFICIENCY_EVALUATOR
        )

        super().__init__()

    @override
    async def _real_call(self, **kwargs):
        """The asynchronous call where real end-to-end evaluation logic is performed.

        :keyword kwargs: The inputs to evaluate.
        :type kwargs: Dict
        :return: The evaluation result.
        :rtype: Dict[str, Union[float, str, Dict[str, float]]]
        """
        self._validator.validate_eval_input(kwargs)
        return await super()._real_call(**kwargs)

    def _prepare_steps_for_comparison(
        self,
        agent_tool_pairs: List[Tuple[str, Dict[str, Any]]],
        ground_truth: List[str],
        ground_truth_params: Dict[str, Dict[str, Any]],
        use_parameter_matching: bool,
    ) -> Tuple[
        List[Union[str, Tuple[str, Tuple]]],
        List[Union[str, Tuple[str, Tuple]]],
    ]:
        """Prepare agent and ground truth steps for comparison based on parameter matching mode."""
        agent_steps: List[Union[str, Tuple[str, Tuple]]] = []
        ground_truth_steps: List[Union[str, Tuple[str, Tuple]]] = []
        if use_parameter_matching:
            # When parameter matching is enabled, we need to match both tool name and parameters
            agent_steps = [(pair[0], tuple(sorted(pair[1].items()))) for pair in agent_tool_pairs]
            ground_truth_steps = [
                (name, tuple(sorted(ground_truth_params.get(name, {}).items()))) for name in ground_truth
            ]
        else:
            # When parameter matching is disabled, only compare tool names
            agent_steps = [name for name, _ in agent_tool_pairs]
            ground_truth_steps = [step for step in ground_truth]

        return agent_steps, ground_truth_steps

    def _calculate_precision_recall_f1_scores(self, agent_steps: List, ground_truth_steps: List) -> Dict[str, float]:
        """Calculate precision, recall, and F1 scores."""
        if not agent_steps:
            return {"precision_score": 0.0, "recall_score": 0.0, "f1_score": 0.0}

        # Count occurrences of each step in both lists to handle duplicates
        agent_steps_counts = Counter(agent_steps)
        ground_truth_counts = Counter(ground_truth_steps)

        # Calculate true positives by taking the minimum count for each common element
        # For each step, count the intersection (min count) of agent and ground truth steps
        true_positives = sum(
            min(agent_steps_counts[step], ground_truth_counts[step])
            for step in agent_steps_counts
            if step in ground_truth_counts
        )

        # Calculate false positives (agent steps not in ground truth or excess occurrences)
        # For each step, count the excess occurrences of agent steps not in (minus) ground truth
        # or zero (agent steps minus agent steps) if agent steps is less than ground truth
        false_positives = sum(
            agent_steps_counts[step] - min(agent_steps_counts[step], ground_truth_counts.get(step, 0))
            for step in agent_steps_counts
        )

        # Calculate false negatives (ground truth steps not in agent or missing occurrences)
        # For each step, count the excess occurrences of ground truth steps not in (minus) agent steps
        # or zero (ground truth steps minus ground truth steps) if ground truth steps is less than agent steps
        false_negatives = sum(
            ground_truth_counts[step] - min(ground_truth_counts[step], agent_steps_counts.get(step, 0))
            for step in ground_truth_counts
        )

        # Calculate precision, recall, F1
        precision = (
            true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
        )
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
        f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        return {
            "precision_score": precision,
            "recall_score": recall,
            "f1_score": f1_score,
        }

    def _calculate_exact_match(self, agent_steps: List, ground_truth_steps: List) -> bool:
        """Check if agent steps exactly match ground truth (order and content)."""
        return agent_steps == ground_truth_steps

    def _calculate_in_order_match(self, agent_steps: List, ground_truth_steps: List) -> bool:
        """Check if all ground truth steps appear in agent steps in correct order (extra steps allowed)."""
        if not ground_truth_steps:
            return True

        gt_index = 0
        for step in agent_steps:
            if gt_index < len(ground_truth_steps) and step == ground_truth_steps[gt_index]:
                gt_index += 1

        return gt_index == len(ground_truth_steps)

    def _calculate_any_order_match(self, agent_steps: List, ground_truth_steps: List) -> bool:
        """Check if all ground truth steps appear in agent steps with sufficient frequency (any order, extra steps allowed)."""
        # Count occurrences of each step in both lists to handle duplicates
        agent_counts = Counter(agent_steps)
        ground_truth_counts = Counter(ground_truth_steps)

        # Check if agent has at least as many occurrences of each ground truth step
        return all(agent_counts[step] >= ground_truth_counts[step] for step in ground_truth_counts)

    _TASK_NAVIGATION_EFFICIENCY_MATCHING_MODE_TO_FUNCTIONS = {
        _TaskNavigationEfficiencyMatchingMode.EXACT_MATCH: _calculate_exact_match,
        _TaskNavigationEfficiencyMatchingMode.IN_ORDER_MATCH: _calculate_in_order_match,
        _TaskNavigationEfficiencyMatchingMode.ANY_ORDER_MATCH: _calculate_any_order_match,
    }

    @override
    async def _do_eval(self, eval_input: Dict) -> Dict[str, Union[float, str, Dict[str, float]]]:
        """Produce a path efficiency evaluation result.

        :param eval_input: The input to the evaluation function. Must contain "response" and "ground_truth".
        :type eval_input: Dict
        :return: The evaluation result.
        :rtype: Dict[str, Union[float, str, Dict[str, float]]]
        """
        response = eval_input["response"]
        ground_truth = eval_input["ground_truth"]

        # Value and type checking for ground truth steps
        if not ground_truth:
            raise ValueError("ground_truth cannot be empty")

        # Check if ground_truth is a tuple (tool names + parameters) or list (tool names only)
        use_parameter_matching = False
        ground_truth_names = []
        ground_truth_params_dict: Dict[str, Dict[str, Any]] = {}

        if isinstance(ground_truth, tuple) and len(ground_truth) == 2:
            # Tuple format: (tool_names, parameters_dict)
            tool_names_list, params_dict = ground_truth

            if not isinstance(tool_names_list, list) or not all(isinstance(name, str) for name in tool_names_list):
                raise TypeError("ground_truth tuple first element must be a list of strings (tool names)")

            if not isinstance(params_dict, dict):
                raise TypeError(
                    "ground_truth tuple second element must be a dictionary mapping tool names to parameters"
                )

            # Validate that all values in params_dict are dictionaries with string keys and values
            for tool_name, params in params_dict.items():
                if not isinstance(tool_name, str):
                    raise TypeError("ground_truth parameters dictionary keys must be strings (tool names)")
                if not isinstance(params, dict):
                    raise TypeError(f"ground_truth parameters for tool '{tool_name}' must be a dictionary")
                for k, v in params.items():
                    if not isinstance(k, str):
                        raise TypeError(f"ground_truth parameters for tool '{tool_name}' must have string keys")
                    try:
                        json.dumps(v)
                    except (TypeError, ValueError):
                        raise TypeError(
                            f"ground_truth parameters for tool '{tool_name}' must have JSON-serializable values (got type {type(v)} for key '{k}')"
                        )

            ground_truth_names = [name.strip() for name in tool_names_list]
            ground_truth_params_dict = params_dict
            use_parameter_matching = True
        elif isinstance(ground_truth, list) and all(isinstance(step, str) for step in ground_truth):
            # List format: just tool names
            ground_truth_names = [step.strip() for step in ground_truth]
            use_parameter_matching = False
        else:
            raise TypeError(
                "ground_truth must be a list of strings or a tuple of (list[str], dict[str, dict[str, str]])"
            )

        # Extract tool information from the response
        agent_tool_pairs = self._extract_tool_names_and_params_from_response(response)

        # Prepare steps for comparison
        agent_steps, ground_truth_steps = self._prepare_steps_for_comparison(
            agent_tool_pairs,
            ground_truth_names,
            ground_truth_params_dict,
            use_parameter_matching,
        )

        # Calculate precision, recall, and F1 scores
        additional_properties_metrics = self._calculate_precision_recall_f1_scores(agent_steps, ground_truth_steps)

        # Convert metrics to floats, using nan for None or non-convertible values
        for metric, score in additional_properties_metrics.items():
            additional_properties_metrics[metric] = float(score) if score is not None else float("nan")

        if self.matching_mode in self._TASK_NAVIGATION_EFFICIENCY_MATCHING_MODE_TO_FUNCTIONS:
            # Calculate binary match metrics
            match_result = self._TASK_NAVIGATION_EFFICIENCY_MATCHING_MODE_TO_FUNCTIONS[self.matching_mode](
                self, agent_steps, ground_truth_steps
            )

            return {
                "task_navigation_efficiency_label": match_result,
                "task_navigation_efficiency_result": EVALUATION_PASS_FAIL_MAPPING[match_result],
                "task_navigation_efficiency_details": additional_properties_metrics,
            }
        else:
            raise EvaluationException(
                f"Unsupported matching_mode '{self.matching_mode}'",
                internal_message=str(self.matching_mode),
                target=ErrorTarget.TASK_NAVIGATION_EFFICIENCY_EVALUATOR,
                category=ErrorCategory.INVALID_VALUE,
            )

    @overload
    def __call__(  # type: ignore
        self, *, response: Union[str, List[Dict[str, Any]]], ground_truth: List[str]
    ) -> Dict[str, Union[float, str, Dict[str, float]]]:
        """
        Evaluate the task navigation efficiency of an agent's action sequence.

        :keyword response: The agent's response containing tool calls.
        :paramtype response: Union[str, List[Dict[str, Any]]]
        :keyword ground_truth: List of expected tool/action steps.
        :paramtype ground_truth: List[str]
        :return: The task navigation efficiency scores and results.
        :rtype: Dict[str, Union[float, str, Dict[str, float]]]
        """

    @overload
    def __call__(  # type: ignore
        self,
        *,
        response: Union[str, List[Dict[str, Any]]],
        ground_truth: Tuple[List[str], Dict[str, Dict[str, str]]],
    ) -> Dict[str, Union[float, str, Dict[str, float]]]:
        """
        Evaluate the task navigation efficiency of an agent's action sequence with tool parameters.

        :keyword response: The agent's response containing tool calls.
        :paramtype response: Union[str, List[Dict[str, Any]]]
        :keyword ground_truth: Tuple of (tool names list, parameters dict) where parameters must match exactly.
        :paramtype ground_truth: Tuple[List[str], Dict[str, Dict[str, str]]]
        :return: The task navigation efficiency scores and results.
        :rtype: Dict[str, Union[float, str, Dict[str, float]]]
        """

    @override
    def __call__(
        self,
        *args,
        **kwargs,
    ):
        """
        Evaluate task navigation efficiency.

        :keyword response: The agent's response containing tool calls.
        :paramtype response: Union[str, List[Dict[str, Any]]]
        :keyword ground_truth: List of expected tool/action steps or tuple of (tool names, parameters dict).
        :paramtype ground_truth: Union[List[str], Tuple[List[str], Dict[str, Dict[str, str]]]]
        :return: The task navigation efficiency scores and results.
        :rtype: Dict[str, Union[float, str, Dict[str, float]]]
        """
        return super().__call__(*args, **kwargs)
