import json
import math
import re
from typing import Any, Callable, Dict, NoReturn, Optional, Tuple

from azure.ai.evaluation._common.constants import PROMPT_BASED_REASON_EVALUATORS
from azure.ai.evaluation._common.utils import parse_quality_evaluator_reason_score
from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget
from azure.ai.evaluation._legacy.prompty._exceptions import (
    InvalidLLMOutputError,
    RESPONSE_CONTENT_FILTERED,
    RESPONSE_EMPTY,
    RESPONSE_NO_VALID_SCORE,
    RESPONSE_NOT_JSON_OBJECT,
    RESPONSE_TRUNCATED,
    RESPONSE_UNEXPECTED_TYPE,
    raise_invalid_output_for_evaluator,
)
from ._base_model_eval import ModelEvaluatorBase, not_applicable_result


def _to_number(value: Any) -> Tuple[Optional[float], bool]:
    """Convert a score to a float, returning ``(None, False)`` when it is not numeric.

    The conversion error is not kept, because its message can quote judge text.

    :param value: The score.
    :type value: Any
    :return: The number, or None, and whether it was an integer too large for a float.
    :rtype: Tuple[Optional[float], bool]
    """
    try:
        return float(value), False
    except (TypeError, ValueError):
        return None, False
    except OverflowError:
        return None, True


def invalid_output_error(output: Any = None, cause: Optional[str] = None, target: Any = ErrorTarget.EVALUATE):
    """Build the error for an unusable judge output, with only the prompty envelope's metadata.

    :param output: The prompty output, either the envelope that holds ``llm_output`` or the answer itself.
    :type output: Any
    :param cause: A fixed cause. When omitted it is derived from the answer's type.
    :type cause: Optional[str]
    :param target: The error target.
    :type target: Any
    :return: The error.
    :rtype: InvalidLLMOutputError
    """
    # Runtime metadata is only trusted from a prompty envelope; a bare answer dict comes from the judge.
    envelope = output if isinstance(output, dict) and "llm_output" in output else {}
    if envelope.get("finish_reason") == "length":
        cause = RESPONSE_TRUNCATED
    elif envelope.get("finish_reason") == "content_filter":
        cause = RESPONSE_CONTENT_FILTERED
    elif cause is None:
        answer = envelope.get("llm_output") if envelope else output
        if answer is None or answer == "" or answer == {}:
            cause = RESPONSE_EMPTY
        elif isinstance(answer, str):
            cause = RESPONSE_NOT_JSON_OBJECT
        else:
            cause = RESPONSE_UNEXPECTED_TYPE.format(type(answer).__name__)
    usage = envelope.get("reported_usage")
    if not isinstance(usage, dict):
        usage = {
            "prompt_tokens": envelope.get("input_token_count"),
            "completion_tokens": envelope.get("output_token_count"),
            "total_tokens": envelope.get("total_token_count"),
            "model": envelope.get("model_id"),
        }
    return InvalidLLMOutputError(
        cause, finish_reason=envelope.get("finish_reason"), usage=usage, subject="Evaluator", target=target
    )


def _describe_score(score: Any) -> str:
    """Describe a score for an error message without echoing non-numeric judge text."""
    try:
        if score is None or isinstance(score, (bool, int, float)):
            return str(score)
        if isinstance(score, str):
            return str(float(score))
    except ValueError:
        return "<non-numeric str>" if isinstance(score, str) else "<numeric overflow>"
    return f"<{type(score).__name__}>"


class PromptyEvaluationStrategy:
    def __init__(
        self,
        runner: Callable,
        *,
        result_key: str,
        threshold: float,
        timeout: float,
        strict: bool = True,
        missing_score: Optional[float] = 0,
        score_range: Optional[Tuple[int, int]] = None,
        error_target: Any = ErrorTarget.EVALUATE,
        score_error_target: Any = None,
        binary_cutoff: Optional[float] = None,
        higher_is_better: bool = True,
        completed_alias: Optional[str] = None,
        top_level_usage: bool = False,
        flow_resolver: Optional[Callable] = None,
    ):
        self.runner = runner
        self.result_key = result_key
        self.threshold = threshold
        self.timeout = timeout
        self.strict = strict
        self.missing_score = missing_score
        self.score_range = score_range
        self.error_target = error_target
        self.score_error_target = score_error_target or error_target
        self.binary_cutoff = binary_cutoff
        self.higher_is_better = higher_is_better
        self.completed_alias = completed_alias
        self.top_level_usage = top_level_usage
        self.flow_resolver = flow_resolver

    async def evaluate(self, eval_input: Dict[str, Any]) -> Dict[str, Any]:
        runner = self.flow_resolver() if self.flow_resolver else self.runner
        try:
            output = await runner(timeout=self.timeout, **eval_input)
        except InvalidLLMOutputError as error:
            invalid_output = error
        else:
            try:
                return self.parse(output)
            except InvalidLLMOutputError as error:
                invalid_output = error
        raise_invalid_output_for_evaluator(invalid_output)

    def skipped(self, reason: str, threshold: Optional[float] = None) -> Dict[str, Any]:
        result = not_applicable_result(self.result_key, reason, self.threshold if threshold is None else threshold)
        if self.top_level_usage:
            metadata = ModelEvaluatorBase._get_token_metadata({})
            result.update({f"{self.result_key}_{key}": value for key, value in metadata.items()})
        return result

    def parse(self, output: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(output, dict) or (not self.strict and not output):
            self._invalid_output(output)
        answer = output.get("llm_output", output if self.strict else "")
        if not self.strict and isinstance(answer, str):
            try:
                parsed = json.loads(answer)
            except (ValueError, TypeError, RecursionError):
                parsed = None
            if isinstance(parsed, dict) and parsed:
                answer = parsed
        reason = ""
        properties = {}
        score = self.missing_score
        has_score = False
        if isinstance(answer, dict) and (self.strict or answer):
            if answer.get("status", "completed") == "skipped":
                return self.format_result(
                    None,
                    "not_applicable",
                    f"Not applicable: {answer.get('reason', '')}",
                    "skipped",
                    answer.get("properties", {}) or {},
                    output,
                )
            score = answer.get("score", self.missing_score)
            has_score = "score" in answer
            reason = answer.get("reason", "")
            properties = answer.get("properties", {}) or {}
        elif self.strict:
            self._invalid_output(output)
        elif isinstance(answer, str):
            if self.result_key in PROMPT_BASED_REASON_EVALUATORS:
                if self.score_range:
                    score, reason = parse_quality_evaluator_reason_score(
                        answer, valid_score_range=r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
                    )
                else:
                    score, reason = parse_quality_evaluator_reason_score(answer)
                has_score = not math.isnan(score)
            else:
                match = re.search(
                    r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?" if self.score_range else r"\d", answer
                )
                if match:
                    score = float(match.group())
                    has_score = True
        if self.score_range:
            minimum, maximum = self.score_range
            numeric, overflow = _to_number(score) if has_score and not isinstance(score, bool) else (None, False)
            if not overflow and (numeric is None or math.isnan(numeric)):
                self._invalid_output(output, RESPONSE_NO_VALID_SCORE, self.score_error_target)
            if overflow or not minimum <= numeric <= maximum:
                raise EvaluationException(
                    message=(
                        f"Invalid score value: {'<numeric overflow>' if overflow else _describe_score(score)}. "
                        f"Expected a number in range [{minimum}, {maximum}]."
                    ),
                    internal_message="Invalid score value.",
                    category=ErrorCategory.FAILED_EXECUTION,
                    target=self.score_error_target,
                    blame=ErrorBlame.SYSTEM_ERROR,
                )
            score = numeric
        elif self.strict or score is not None:
            numeric, _ = _to_number(score) if has_score or not self.strict else (None, False)
            if numeric is None or (self.strict and (isinstance(score, bool) or not math.isfinite(numeric))):
                self._invalid_output(output, RESPONSE_NO_VALID_SCORE)
            score = numeric
        else:
            score = math.nan
        cutoff = self.threshold if self.binary_cutoff is None else self.binary_cutoff
        if math.isnan(score) and self.binary_cutoff is None:
            verdict = "unknown"
        else:
            passed = score >= cutoff if self.higher_is_better else score <= cutoff
            verdict = "pass" if passed else "fail"
        return self.format_result(score, verdict, reason, "completed", properties, output)

    def format_result(
        self,
        score: Optional[float],
        verdict: str,
        reason: str,
        status: str,
        properties: Dict[str, Any],
        output: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        metadata = ModelEvaluatorBase._get_token_metadata(output or {})
        properties.update(metadata)
        result = {
            self.result_key: score,
            f"{self.result_key}_score": score,
            f"{self.result_key}_passed": verdict == "pass" if verdict in ("pass", "fail", "unknown") else None,
            f"{self.result_key}_result": verdict,
            f"{self.result_key}_reason": reason,
            f"{self.result_key}_status": status,
            f"{self.result_key}_threshold": self.threshold,
            f"{self.result_key}_properties": properties,
        }
        if self.completed_alias and status == "completed":
            result[self.completed_alias] = score
        if self.top_level_usage:
            result.update({f"{self.result_key}_{key}": value for key, value in metadata.items()})
        return result

    def _invalid_output(self, output: Any = None, cause: Optional[str] = None, target: Any = None) -> NoReturn:
        raise invalid_output_error(output, cause, target or self.error_target)
