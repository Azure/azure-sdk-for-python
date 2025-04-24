# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# --------------------------------------------
from typing import Any, Dict, List, Optional, Union
from azure.ai.evaluation._evaluators._common import PromptyEvaluatorBase
from ._tool_calls_predictor import predict_tools

def _extract_tool_items(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    items = []
    for msg in messages:
        for c in msg.get("content", []):
            if c.get("type") == "tool_call":
                items.append({
                    "type": "tool_call",
                    "name": c.get("name"),
                    "arguments": c.get("arguments"),
                })
            elif c.get("type") == "tool_result":
                items.append({
                    "type": "tool_result",
                    "tool_result": c.get("tool_result"),
                })
    return items


def _compare_values(val1, val2) -> float:
    # Helper: recursively, for dict, list, primitives
    if isinstance(val1, dict) and isinstance(val2, dict):
        keys = set(val1) | set(val2)
        if not keys:
            return 1.0
        scores = []
        for k in keys:
            if k in val1 and k in val2:
                scores.append(_compare_values(val1[k], val2[k]))
            else:
                scores.append(0.0)
        return sum(scores) / len(scores)
    elif isinstance(val1, list) and isinstance(val2, list):
        if not val1 and not val2:
            return 1.0
        matches = []
        min_len = min(len(val1), len(val2))
        for i in range(min_len):
            matches.append(_compare_values(val1[i], val2[i]))
            # Penalty for missing values
        matches += [0.0] * (abs(len(val1) - len(val2)))
        return sum(matches) / max(len(val1), len(val2), 1)
    else:
        # Compare scalars as strings with normalization
        if str(val1).lower() == str(val2).lower():
            return 1.0
            # Otherwise consider similar strings (could add fuzzy matching here if wanted)
        return 0.0


def _match_tool_call(expected: Dict, predicted: Dict) -> float:
    if expected["type"] != predicted["type"]:
        return 0.0
    if expected["type"] == "tool_call":
        name_match = expected.get("name") == predicted.get("name")
        args_expected = expected.get("arguments", {})
        args_pred = predicted.get("arguments", {})
        if name_match:
            if args_expected == args_pred:
                return 1.0
                # Partial credit: overlap in arguments
            arg_score = _compare_values(args_expected, args_pred)
            return 0.5 + 0.5 * arg_score if arg_score > 0 else 0.5
        else:
            return 0.0
    elif expected["type"] == "tool_result":
        res_expected = expected.get("tool_result", {})
        res_pred = predicted.get("tool_result", {})
        score = _compare_values(res_expected, res_pred)
        if score == 1.0:
            return 1.0
        elif score > 0:
            return 0.5 + 0.5 * score
        else:
            return 0.5 if res_pred else 0.0
    return 0.0


def _evaluate_tool_accuracy(expected: List[Dict], predicted: List[Dict]) -> (float, List[str]):
    reasons = []
    matched_pred_indices = set()
    per_item_scores = []

    for idx, exp in enumerate(expected):
        max_score = 0.0
        max_j = None
        for j, pred in enumerate(predicted):
            if j in matched_pred_indices:
                continue
            score = _match_tool_call(exp, pred)
            if score > max_score:
                max_score = score
                max_j = j
        per_item_scores.append(max_score)
        if max_score == 1.0:
            continue
        elif max_score >= 0.75:
            reasons.append(f"Mostly correct for {exp['type']} (minor data mismatch).")
        elif max_score >= 0.5:
            reasons.append(f"Partial match for {exp['type']} (key fields mismatch or missing).")
        else:
            reasons.append(f"Missing or incorrect {exp['type']}.")
        if max_j is not None:
            matched_pred_indices.add(max_j)
    accuracy = sum(per_item_scores) / max(len(expected), 1)
    return accuracy, reasons


class ToolCallAccuracyEvaluator(PromptyEvaluatorBase[Union[str, float]]):
    _PROMPTY_FILE = None
    _RESULT_KEY = "tool_call_accuracy"
    _DEFAULT_THRESHOLD = 0.8

    def __init__(self, model_config, *, threshold: float = _DEFAULT_THRESHOLD):
        self.threshold = threshold
        super().__init__(
            model_config=model_config,
            prompty_file=None,
            result_key=self._RESULT_KEY
        )

    def __call__(
            self,
            query: List[Dict[str, Any]],
            response: List[Dict[str, Any]],
            tool_definitions: List[Dict[str, Any]],
            ground_truth: Optional[List[Dict[str, Any]]] = None,
            **kwargs
    ) -> Dict[str, Any]:
        eval_input = {
            "query": query,
            "response": response,
            "tool_definitions": tool_definitions,
            "ground_truth": ground_truth
        }
        return super().__call__(eval_input, **kwargs)

    async def _do_eval(self, eval_input: Dict) -> Dict[str, Union[float, str]]:
        query = eval_input.get("query")
        response = eval_input.get("response")
        tool_definitions = eval_input.get("tool_definitions")
        ground_truth = eval_input.get("ground_truth")

        if ground_truth is None:
            ground_truth = generate_ground_truth(query, response, tool_definitions)

        gt_items = ground_truth
        pred_items = _extract_tool_items(response)

        accuracy, reasons = _evaluate_tool_accuracy(gt_items, pred_items)
        status = "pass" if accuracy >= self.threshold else "fail"

        if not reasons:
            reason_str = "All tool calls and results matched the ground truth."
        else:
            if accuracy == 0.0:
                reason_str = "No correct tool calls or results detected."
            else:
                reason_str = "; ".join(reasons)

        result = {
            "tool_call_accuracy": status,
            "tool_call_accuracy_score": round(accuracy, 3),
            "tool_call_threshold": self.threshold,
            "tool_call_accuracy_reason": reason_str
        }
        return result  