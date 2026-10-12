# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Evaluates prepared input with a decision model and returns the final evaluator result.

An evaluator supplies its questions, scoring policy and error target; this strategy owns the shared mechanics:
status gating, score mapping, provenance and result shape.
"""

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union

from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget
from ._base_model_eval import ModelEvaluatorBase, not_applicable_result
from ._model_runners import DecisionModelRunner, validate_noul_answer, validate_score_answer

STATUS_CUTOFF = 0.5
T = TypeVar("T")


def _checked_value(validate: Callable[..., T], error_target: ErrorTarget, *args: Any) -> T:
    try:
        return validate(*args)
    except ValueError as exc:
        message = f"The decision model returned an invalid response: {exc}"
        raise EvaluationException(
            message=message,
            internal_message=message,
            blame=ErrorBlame.SYSTEM_ERROR,
            category=ErrorCategory.FAILED_EXECUTION,
            target=error_target,
        ) from None


def decision_probability(
    response: Dict[str, Any], question_id: str, error_target: ErrorTarget = ErrorTarget.EVALUATE
) -> float:
    """Read and validate the probability of a binary decision answer."""
    return _checked_value(validate_noul_answer, error_target, response["answers"][question_id])


def decision_distribution(
    response: Dict[str, Any], question_id: str, levels: int, error_target: ErrorTarget = ErrorTarget.EVALUATE
) -> List[float]:
    """Read and validate the distribution of a scored decision answer."""
    return _checked_value(validate_score_answer, error_target, response["answers"][question_id], levels)


def decision_skip_reason(
    response: Dict[str, Any], cutoff: float, error_target: ErrorTarget = ErrorTarget.EVALUATE
) -> Optional[str]:
    """Apply the evaluator's status cutoff before interpreting a score."""
    probability = decision_probability(response, "status", error_target)
    if probability >= cutoff:
        return None
    return (
        f"Status completion probability {probability:.4f} is below {cutoff:.4f}; "
        "evaluation skipped. No model rationale is available."
    )


def decision_token_counts(response: Dict[str, Any]) -> Dict[str, Any]:
    """Convert decision usage to the common model-output metadata shape."""
    usage = response["usage"]
    return {
        "input_token_count": usage["input_tokens"],
        "output_token_count": usage["output_tokens"],
        "total_token_count": usage["input_tokens"] + usage["output_tokens"],
        "model_id": response["model"],
    }


def _label(result_key: str) -> str:
    return result_key.replace("_", " ")


def _digest(question: Dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(question, sort_keys=True).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class BinaryScoring:
    """Scores 1 when the answer's probability reaches the cutoff, otherwise 0."""

    probability_cutoff: float

    def interpret(
        self, response: Dict[str, Any], result_key: str, error_target: ErrorTarget
    ) -> Tuple[float, str, Dict[str, Any]]:
        probability = decision_probability(response, result_key, error_target)
        score = float(probability >= self.probability_cutoff)
        relation = "at or above" if score else "below"
        reason = (
            f"{_label(result_key).capitalize()} probability {probability:.4f} is {relation} "
            f"the {self.probability_cutoff:.4f} cutoff."
        )
        details = {
            "probability_threshold": self.probability_cutoff,
            "probabilities": {"false": 1 - probability, "true": probability},
        }
        return score, reason, details

    def passes(self, score: float, threshold: float) -> bool:
        return score >= 1.0


@dataclass(frozen=True)
class LikertScoring:
    """Scores the highest-probability level of a scale starting at ``minimum``; ties select the lowest level."""

    levels: int
    minimum: int = 1

    def interpret(
        self, response: Dict[str, Any], result_key: str, error_target: ErrorTarget
    ) -> Tuple[float, str, Dict[str, Any]]:
        distribution = decision_distribution(response, result_key, self.levels, error_target)
        score = float(max(range(self.levels), key=distribution.__getitem__) + self.minimum)
        answer = response["answers"][result_key]
        reason = f"Selected {_label(result_key)} level {score:g} from the highest-probability level."
        details = {
            "probabilities": answer["probabilities"],
            "confidence": answer["confidence"],
            "native_mean": answer["score"],
            "expected_score": sum(level * value for level, value in enumerate(distribution)) + self.minimum,
        }
        return score, reason, details

    def passes(self, score: float, threshold: float) -> bool:
        return score >= threshold


class DecisionEvaluationStrategy:
    def __init__(
        self,
        runner: DecisionModelRunner,
        *,
        result_key: str,
        error_target: ErrorTarget,
        questions: Dict[str, Any],
        scoring: Union[BinaryScoring, LikertScoring],
        threshold: float,
        timeout: float,
        extra_properties: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    ):
        self.runner = runner
        self.result_key = result_key
        self.error_target = error_target
        self.questions = questions
        self.scoring = scoring
        self.threshold = threshold
        self.timeout = timeout
        self.extra_properties = extra_properties

    async def evaluate(self, eval_input: Dict[str, Any]) -> Dict[str, Any]:
        key = self.result_key
        response = await self.runner(state=dict(eval_input), questions=self.questions, timeout=self.timeout)
        skip_reason = decision_skip_reason(response, STATUS_CUTOFF, self.error_target)
        if skip_reason:
            return not_applicable_result(key, skip_reason, self.threshold)
        score, reason, details = self.scoring.interpret(response, key, self.error_target)
        properties = self.extra_properties(eval_input) if self.extra_properties else {}
        properties["decision_model"] = {
            "deployment": self.runner.deployment,
            "model": response["model"],
            "rubric_hash": _digest(self.questions[key]),
            "status_rubric_hash": _digest(self.questions["status"]),
            "native_status_answer": response["answers"]["status"],
            "status_completion_probability": decision_probability(response, "status", self.error_target),
            "status_probability_threshold": STATUS_CUTOFF,
            "reason_type": "templated",
            **details,
            "native_answer": response["answers"][key],
        }
        properties.update(ModelEvaluatorBase._get_token_metadata(decision_token_counts(response)))
        passed = self.scoring.passes(score, self.threshold)
        return {
            key: score,
            f"{key}_score": score,
            f"{key}_passed": passed,
            f"{key}_result": "pass" if passed else "fail",
            f"{key}_reason": f"{reason} No model rationale is available.",
            f"{key}_status": "completed",
            f"{key}_threshold": self.threshold,
            f"{key}_properties": properties,
        }
