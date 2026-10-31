# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Evaluates prepared input with a decision model and returns the final evaluator result.

An evaluator supplies its questions, scoring policy and error target; this strategy owns the shared mechanics:
status gating, score mapping, provenance and result shape.
"""

import asyncio
import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union

from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from ._base_model_eval import not_applicable_result
from ._decision_protocols import REFUSAL
from ._model_runners import (
    CANCELLED_BY_CALLBACK,
    CONTENT_FILTER,
    DecisionModelRunner,
    _diagnostic,
    validate_noul_answer,
    validate_score_answer,
    validated_execution,
)

STATUS_CUTOFF = 0.5
_METRIC_PREFIX = "azure.ai.evaluation.decision."
T = TypeVar("T")


class DecisionRefusalError(EvaluationException):
    """The decision model declined to answer a question that the evaluation reads.

    A refusal is not a low probability, a zero score or a skip: the evaluation fails without a score. The model's
    content policy decided about the evaluated content, so the error is classified like a chat judge's
    content-filter refusal.
    """

    ERROR_KIND = "model_refusal"

    def __init__(self, question_id: str, error_target: ErrorTarget) -> None:
        self.question_id = question_id
        message = f"The decision model refused to answer question '{question_id}'; no score is available."
        super().__init__(
            message=message,
            internal_message="The decision model refused to answer an evaluation question.",
            blame=ErrorBlame.USER_ERROR,
            category=ErrorCategory.FAILED_EXECUTION,
            target=error_target,
        )

    def __reduce__(self):
        # Copies and pickles rebuild from the constructor's arguments, then restore attached metadata.
        return type(self), (self.question_id, self.target), self.__dict__


def _error_kind(error: EvaluationException) -> str:
    """Return the bounded error kind of a failed evaluation: a refusal, a content filter rejection, or none."""
    if isinstance(error, DecisionRefusalError):
        return DecisionRefusalError.ERROR_KIND
    properties = getattr(error, "properties", None)
    native = properties.get("decision_model") if isinstance(properties, dict) else None
    return CONTENT_FILTER if isinstance(native, dict) and native.get("error_kind") == CONTENT_FILTER else "none"


def _cancelled_by_callback(error: EvaluationException) -> bool:
    """Return whether the runner marked the error as a cancellation by the cancellation callback."""
    return getattr(error, CANCELLED_BY_CALLBACK, False) is True


def _record_evaluation(attributes: Dict[str, str], elapsed_ms: float) -> None:
    """Count one Decision evaluation and record its duration when OpenTelemetry is installed.

    Instruments are looked up per call, like the request metrics, so strategies stay picklable. A metric sink
    failure, including a broken OpenTelemetry installation, is logged and never changes the evaluation result or
    exception.
    """
    try:
        from opentelemetry.metrics import get_meter  # pylint: disable=import-outside-toplevel

        meter = get_meter("azure.ai.evaluation.decision")
        meter.create_counter(_METRIC_PREFIX + "evaluations").add(1, attributes=attributes)
        meter.create_histogram(_METRIC_PREFIX + "evaluation.duration", unit="ms").record(
            elapsed_ms, attributes=attributes
        )
    except ImportError:
        return
    except Exception:  # pylint: disable=broad-except
        _diagnostic("Decision evaluation metric sink failed; the evaluation result is unchanged.")


def _checked_value(validate: Callable[..., T], error_target: ErrorTarget, *args: Any) -> T:
    try:
        return validate(*args)
    except (ValueError, OverflowError) as exc:
        message = f"The decision model returned an invalid response: {exc}"
        raise EvaluationException(
            message=message,
            internal_message=message,
            blame=ErrorBlame.SYSTEM_ERROR,
            category=ErrorCategory.FAILED_EXECUTION,
            target=error_target,
        ) from None


def _read_answer(response: Dict[str, Any], question_id: str, error_target: ErrorTarget) -> Dict[str, Any]:
    answer = response["answers"][question_id]
    if isinstance(answer, dict) and answer.get("type") == REFUSAL:
        raise DecisionRefusalError(question_id, error_target)
    return answer


def decision_probability(
    response: Dict[str, Any], question_id: str, error_target: ErrorTarget = ErrorTarget.EVALUATE
) -> float:
    """Read and validate the probability of a binary decision answer."""
    return _checked_value(validate_noul_answer, error_target, _read_answer(response, question_id, error_target))


def decision_distribution(
    response: Dict[str, Any], question_id: str, levels: int, error_target: ErrorTarget = ErrorTarget.EVALUATE
) -> List[float]:
    """Read and validate the distribution of a scored decision answer."""
    answer = _read_answer(response, question_id, error_target)
    return _checked_value(validate_score_answer, error_target, answer, levels)


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


def _native_answer_provenance(answer: Dict[str, Any]) -> Dict[str, Any]:
    try:
        json.dumps(answer, allow_nan=False)
    except (TypeError, ValueError, OverflowError, RecursionError):
        raise ValueError("native answer provenance must contain only JSON-safe values") from None
    return dict(answer)


@dataclass(frozen=True)
class BinaryScoring:
    """Scores 1 when the answer's probability reaches the cutoff, otherwise 0.

    Standalone results pass only at 1, regardless of the evaluator threshold. Composites can reapply their
    configured member thresholds, so a binary member scoring 0 can pass when its composite threshold is 0.
    """

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
    """Interprets Decision answers using the fixed ``STATUS_CUTOFF`` of 0.5 for applicability.

    The evaluator's score threshold does not change the applicability cutoff.
    """

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
        """Request and interpret one Decision evaluation, recording its outcome and duration as metrics.

        Outcomes are ``completed``, ``skipped`` (not applicable), ``error`` with the error's blame, or
        ``cancelled`` by ``asyncio`` or the cancellation callback. A refusal or a content filter rejection is an
        error with ``error_kind`` ``model_refusal`` or ``content_filter``.
        """
        started = time.monotonic()
        outcome, blame, error_kind = "error", "system", "none"
        try:
            response = await self.runner(state=dict(eval_input), questions=self.questions, timeout=self.timeout)
            result = self.parse(response, eval_input)
            tokens = decision_token_counts(response)
            result.update(
                {
                    f"{self.result_key}_prompt_tokens": tokens["input_token_count"],
                    f"{self.result_key}_completion_tokens": tokens["output_token_count"],
                    f"{self.result_key}_total_tokens": tokens["total_token_count"],
                    f"{self.result_key}_model": tokens["model_id"],
                }
            )
            outcome = "skipped" if result.get(f"{self.result_key}_status") == "skipped" else "completed"
            blame = "none"
            return result
        except asyncio.CancelledError:
            outcome, blame = "cancelled", "none"
            raise
        except EvaluationException as exc:
            if _cancelled_by_callback(exc):
                outcome, blame = "cancelled", "none"
            else:
                blame = "user" if exc.blame == ErrorBlame.USER_ERROR else "system"
                error_kind = _error_kind(exc)
            raise
        finally:
            _record_evaluation(
                {
                    "backend": "decision",
                    "protocol": str(getattr(self.runner, "decision_protocol", "microsoft")),
                    "metric": self.result_key,
                    "outcome": outcome,
                    "blame": blame,
                    "error_kind": error_kind,
                },
                (time.monotonic() - started) * 1000,
            )

    def parse(self, response: Dict[str, Any], eval_input: Dict[str, Any]) -> Dict[str, Any]:
        """Interpret a validated response without making a request.

        Known shared-response usage remains in properties. Only the request-owning result emits standard
        usage fields, so composites can parse multiple members without counting the same request repeatedly.
        """
        key = self.result_key
        properties = self.extra_properties(eval_input) if self.extra_properties else {}
        properties["decision_model"] = {
            "deployment": self.runner.deployment,
            "protocol": self.runner.decision_protocol,
            "model": response["model"],
            "rubric_hash": _digest(self.questions[key]),
            "status_rubric_hash": _digest(self.questions["status"]),
            "status_probability_threshold": STATUS_CUTOFF,
            "reason_type": "templated",
        }
        execution = validated_execution(response.get("_decision_execution"))
        if response.get("usage_details"):
            properties["decision_model"]["usage_details"] = response["usage_details"]
        if execution is not None:
            properties["decision_model"]["execution"] = execution
        tokens = decision_token_counts(response)
        properties.update(
            prompt_tokens=tokens["input_token_count"],
            completion_tokens=tokens["output_token_count"],
            total_tokens=tokens["total_token_count"],
            model=tokens["model_id"],
        )
        try:
            skip_reason = decision_skip_reason(response, STATUS_CUTOFF, self.error_target)
            properties["decision_model"]["status_completion_probability"] = decision_probability(
                response, "status", self.error_target
            )
            properties["decision_model"]["native_status_answer"] = _checked_value(
                _native_answer_provenance, self.error_target, response["answers"]["status"]
            )
            if skip_reason:
                result = not_applicable_result(key, skip_reason, self.threshold)
                result[f"{key}_properties"] = properties
                return result
            score, reason, details = self.scoring.interpret(response, key, self.error_target)
            native_answer = _checked_value(
                _native_answer_provenance,
                self.error_target,
                {name: value for name, value in response["answers"][key].items() if name != "legend"},
            )
        except EvaluationException as exc:
            if isinstance(exc, DecisionRefusalError):
                properties["decision_model"]["error_kind"] = DecisionRefusalError.ERROR_KIND
            exc.properties = properties
            raise
        properties["decision_model"].update(details)
        properties["decision_model"]["native_answer"] = native_answer
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
