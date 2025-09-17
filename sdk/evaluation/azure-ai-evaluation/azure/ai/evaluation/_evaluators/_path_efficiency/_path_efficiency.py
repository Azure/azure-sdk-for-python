# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
from collections import Counter
from typing import Dict, List, Union, Any, Tuple
from typing_extensions import overload, override

from azure.ai.evaluation._evaluators._common import EvaluatorBase
from azure.ai.evaluation._constants import EVALUATION_PASS_FAIL_MAPPING


class PathEfficiencyEvaluator(EvaluatorBase):
    """
    Evaluates whether an agent's sequence of actions is efficient and follows optimal decision-making patterns.

    The Path Efficiency Evaluator calculates precision, recall, and F1 scores based on the comparison
    between the agent's tool usage trajectory and the ground truth expected steps. It also provides
    three binary match metrics: exact match, in-order match (allows extra steps), and any-order match (allows extra steps and ignores order).

    :param precision_threshold: The threshold value to determine if the precision evaluation passes or fails. Default is 0.5.
    :type precision_threshold: float
    :param recall_threshold: The threshold value to determine if the recall evaluation passes or fails. Default is 0.5.
    :type recall_threshold: float
    :param f1_score_threshold: The threshold value to determine if the F1 score evaluation passes or fails. Default is 0.5.
    :type f1_score_threshold: float

    .. admonition:: Example:

        .. code-block:: python

            from azure.ai.evaluation import PathEfficiencyEvaluator

            path_efficiency_eval = PathEfficiencyEvaluator(
                precision_threshold=0.7,
                recall_threshold=0.8,
                f1_score_threshold=0.75
            )

            # Example 1: Using simple tool names list
            result = path_efficiency_eval(
                response=[
                    {"role": "assistant", "content": [{"type": "tool_call", "tool_call_id": "call_1", "name": "determine_intent", "arguments": {}}]},
                    {"role": "assistant", "content": [{"type": "tool_call", "tool_call_id": "call_2", "name": "use_tool", "arguments": {}}]},
                    {"role": "assistant", "content": [{"type": "tool_call", "tool_call_id": "call_3", "name": "review_results", "arguments": {}}]},
                    {"role": "assistant", "content": [{"type": "tool_call", "tool_call_id": "call_4", "name": "report_generation", "arguments": {}}]}
                ],
                ground_truth=["determine_intent", "use_tool", "review_results", "report_generation"]
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

    _DEFAULT_PATH_EFFICIENCY_SCORE_THRESHOLD = 0.5

    id = "azureai://built-in/evaluators/path_efficiency"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    @override
    def __init__(
        self,
        *,
        precision_threshold: float = _DEFAULT_PATH_EFFICIENCY_SCORE_THRESHOLD,
        recall_threshold: float = _DEFAULT_PATH_EFFICIENCY_SCORE_THRESHOLD,
        f1_score_threshold: float = _DEFAULT_PATH_EFFICIENCY_SCORE_THRESHOLD,
    ):
        self._higher_is_better = True
        super().__init__()

        # Type checking for threshold parameters
        for name, value in [
            ("precision_threshold", precision_threshold),
            ("recall_threshold", recall_threshold),
            ("f1_score_threshold", f1_score_threshold),
        ]:
            if not isinstance(value, float):
                raise TypeError(f"{name} must be a float, got {type(value)}")

        self._threshold = {
            "path_efficiency_precision": precision_threshold,
            "path_efficiency_recall": recall_threshold,
            "path_efficiency_f1": f1_score_threshold,
        }

    def _calculate_precision_recall_f1_scores(
        self, agent_steps: List[str], ground_truth: List[str]
    ) -> Dict[str, float]:
        """Calculate precision, recall, and F1 scores."""
        if not agent_steps:
            return {"precision_score": 0.0, "recall_score": 0.0, "f1_score": 0.0}

        # Count occurrences of each step in both lists to handle duplicates
        agent_steps_counts = Counter(agent_steps)
        ground_truth_counts = Counter(ground_truth)

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

    def _calculate_exact_match(self, agent_steps: List[str], ground_truth: List[str]) -> bool:
        """Check if agent steps exactly match ground truth (order and content)."""
        return agent_steps == ground_truth

    def _calculate_in_order_match(self, agent_steps: List[str], ground_truth: List[str]) -> bool:
        """Check if all ground truth steps appear in agent steps in correct order (extra steps allowed)."""
        if not ground_truth:
            return True

        gt_index = 0
        for step in agent_steps:
            if gt_index < len(ground_truth) and step == ground_truth[gt_index]:
                gt_index += 1

        return gt_index == len(ground_truth)

    def _calculate_any_order_match(self, agent_steps: List[str], ground_truth: List[str]) -> bool:
        """Check if all ground truth steps appear in agent steps with sufficient frequency (any order, extra steps allowed)."""
        # Count occurrences of each step in both lists to handle duplicates
        agent_counts = Counter(agent_steps)
        ground_truth_counts = Counter(ground_truth)

        # Check if agent has at least as many occurrences of each ground truth step
        return all(agent_counts[step] >= ground_truth_counts[step] for step in ground_truth_counts)

    def _extract_tool_names_and_params_from_response(self, response) -> List[Tuple[str, Dict[str, str]]]:
        """Extract tool names and parameters from the response.
        
        :param response: The response to parse.
        :type response: Union[str, List[dict]]
        :return: List of tuples containing (tool_name, parameters_dict) extracted from the response.
        :rtype: List[Tuple[str, Dict[str, str]]]
        """
        tool_calls = self._parse_tools_from_response(response)
        tool_name_param_pairs = []
        
        for tool_call in tool_calls:
            if not isinstance(tool_call, dict):
                continue
                
            if tool_call.get("type") != "tool_call":
                continue
                
            if "name" not in tool_call:
                continue
                
            tool_name = tool_call["name"]
            
            # Extract parameters/arguments
            parameters = {}
            if "arguments" in tool_call:
                args = tool_call["arguments"]
                if isinstance(args, dict):
                    # Convert all values to strings for consistent comparison
                    parameters = {str(k): str(v) for k, v in args.items()}
                elif isinstance(args, str):
                    # If arguments is a string, try to parse it as JSON
                    try:
                        parsed_args = json.loads(args)
                        if isinstance(parsed_args, dict):
                            parameters = {str(k): str(v) for k, v in parsed_args.items()}
                    except json.JSONDecodeError:
                        # If parsing fails, treat as empty parameters
                        parameters = {}
            
            tool_name_param_pairs.append((tool_name, parameters))
        
        return tool_name_param_pairs

    def _match_tools_with_parameters(
        self, 
        agent_tool_pairs: List[Tuple[str, Dict[str, str]]], 
        ground_truth_names: List[str], 
        ground_truth_params_dict: Dict[str, Dict[str, str]]
    ) -> List[str]:
        """Match agent tools with ground truth considering both name and parameters.
        
        :param agent_tool_pairs: List of (tool_name, parameters) tuples from agent response.
        :type agent_tool_pairs: List[Tuple[str, Dict[str, str]]]
        :param ground_truth_names: List of expected tool names.
        :type ground_truth_names: List[str]
        :param ground_truth_params_dict: Dictionary mapping tool names to their expected parameters.
        :type ground_truth_params_dict: Dict[str, Dict[str, str]]
        :return: List of tool names that matched both name and parameters.
        :rtype: List[str]
        """
        matched_tools = []
        
        for agent_name, agent_params in agent_tool_pairs:
            # Check if the tool name exists in ground truth
            if agent_name in ground_truth_names:
                # Get expected parameters for this tool
                expected_params = ground_truth_params_dict.get(agent_name, {})
                
                # Check if parameters match exactly
                if agent_params == expected_params:
                    matched_tools.append(agent_name)
        
        return matched_tools

    @override
    async def _do_eval(self, eval_input: Dict) -> Dict[str, Union[float, str]]:
        """Produce a path efficiency evaluation result.

        :param eval_input: The input to the evaluation function. Must contain "response" and "ground_truth".
        :type eval_input: Dict
        :return: The evaluation result.
        :rtype: Dict[str, Union[float, str]]
        """
        response = eval_input["response"]
        ground_truth = eval_input["ground_truth"]

        # Value and type checking for ground truth steps
        if not ground_truth:
            raise ValueError("ground_truth cannot be empty")

        # Check if ground_truth is a tuple (tool names + parameters) or list (tool names only)
        use_parameter_matching = False
        ground_truth_names = []
        ground_truth_params_dict = {}
        
        if isinstance(ground_truth, tuple) and len(ground_truth) == 2:
            # Tuple format: (tool_names, parameters_dict)
            tool_names_list, params_dict = ground_truth
            
            if not isinstance(tool_names_list, list) or not all(isinstance(name, str) for name in tool_names_list):
                raise TypeError("ground_truth tuple first element must be a list of strings (tool names)")
            
            if not isinstance(params_dict, dict):
                raise TypeError("ground_truth tuple second element must be a dictionary mapping tool names to parameters")
            
            # Validate that all values in params_dict are dictionaries with string keys and values
            for tool_name, params in params_dict.items():
                if not isinstance(tool_name, str):
                    raise TypeError("ground_truth parameters dictionary keys must be strings (tool names)")
                if not isinstance(params, dict):
                    raise TypeError(f"ground_truth parameters for tool '{tool_name}' must be a dictionary")
                if not all(isinstance(k, str) and isinstance(v, str) for k, v in params.items()):
                    raise TypeError(f"ground_truth parameters for tool '{tool_name}' must have string keys and values")
            
            ground_truth_names = [name.strip() for name in tool_names_list]
            ground_truth_params_dict = params_dict
            use_parameter_matching = True
            
        elif isinstance(ground_truth, list) and all(isinstance(step, str) for step in ground_truth):
            # List format: just tool names
            ground_truth_names = [step.strip() for step in ground_truth]
            use_parameter_matching = False
            
        else:
            raise TypeError("ground_truth must be a list of strings or a tuple of (list[str], dict[str, dict[str, str]])")

        # Extract tool information from the response
        if use_parameter_matching:
            # Extract both names and parameters for matching
            agent_tool_pairs = self._extract_tool_names_and_params_from_response(response)
            agent_steps = self._match_tools_with_parameters(agent_tool_pairs, ground_truth_names, ground_truth_params_dict)
        else:
            # Extract only tool names
            agent_steps = self._extract_tool_names_from_response(response)
            agent_steps = [step.strip() for step in agent_steps]

        # Calculate precision, recall, and F1 scores
        metrics = self._calculate_precision_recall_f1_scores(agent_steps, ground_truth_names)

        # Calculate binary match metrics
        exact_match = self._calculate_exact_match(agent_steps, ground_truth_names)
        in_order_match = self._calculate_in_order_match(agent_steps, ground_truth_names)
        any_order_match = self._calculate_any_order_match(agent_steps, ground_truth_names)

        # Convert metrics to floats, using nan for None or non-convertible values
        path_efficiency_precision = (
            float(metrics["precision_score"]) if metrics["precision_score"] is not None else float("nan")
        )
        path_efficiency_recall = float(metrics["recall_score"]) if metrics["recall_score"] is not None else float("nan")
        path_efficiency_f1_score = float(metrics["f1_score"]) if metrics["f1_score"] is not None else float("nan")

        return {
            "path_efficiency_precision_score": path_efficiency_precision,
            "path_efficiency_recall_score": path_efficiency_recall,
            "path_efficiency_f1_score": path_efficiency_f1_score,
            "path_efficiency_exact_match_result": EVALUATION_PASS_FAIL_MAPPING[exact_match],
            "path_efficiency_in_order_match_result": EVALUATION_PASS_FAIL_MAPPING[in_order_match],
            "path_efficiency_any_order_match_result": EVALUATION_PASS_FAIL_MAPPING[any_order_match],
        }

    @overload
    def __call__(  # type: ignore
        self, *, response: Union[str, List[Dict[str, Any]]], ground_truth: List[str]
    ) -> Dict[str, Union[float, str]]:
        """
        Evaluate the path efficiency of an agent's action sequence.

        :keyword response: The agent's response containing tool calls.
        :paramtype response: Union[str, List[Dict[str, Any]]]
        :keyword ground_truth: List of expected tool/action steps.
        :paramtype ground_truth: List[str]
        :return: The path efficiency scores and results.
        :rtype: Dict[str, Union[float, str]]
        """

    @overload
    def __call__(  # type: ignore
        self, *, response: Union[str, List[Dict[str, Any]]], ground_truth: Tuple[List[str], Dict[str, Dict[str, str]]]
    ) -> Dict[str, Union[float, str]]:
        """
        Evaluate the path efficiency of an agent's action sequence with tool parameters.

        :keyword response: The agent's response containing tool calls.
        :paramtype response: Union[str, List[Dict[str, Any]]]
        :keyword ground_truth: Tuple of (tool names list, parameters dict) where parameters must match exactly.
        :paramtype ground_truth: Tuple[List[str], Dict[str, Dict[str, str]]]
        :return: The path efficiency scores and results.
        :rtype: Dict[str, Union[float, str]]
        """

    @override
    def __call__(
        self,
        *args,
        **kwargs,
    ):
        """
        Evaluate path efficiency.

        :keyword response: The agent's response containing tool calls.
        :paramtype response: Union[str, List[Dict[str, Any]]]
        :keyword ground_truth: List of expected tool/action steps or tuple of (tool names, parameters dict).
        :paramtype ground_truth: Union[List[str], Tuple[List[str], Dict[str, Dict[str, str]]]]
        :return: The path efficiency scores and results.
        :rtype: Dict[str, Union[float, str]]
        """
        return super().__call__(*args, **kwargs)
