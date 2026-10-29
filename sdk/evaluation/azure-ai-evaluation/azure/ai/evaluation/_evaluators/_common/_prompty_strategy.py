import json
import math
import re
from typing import Any, Callable, Dict, Optional, Tuple

from azure.ai.evaluation._common.constants import PROMPT_BASED_REASON_EVALUATORS
from azure.ai.evaluation._common.utils import check_score_is_valid, parse_quality_evaluator_reason_score
from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget
from ._base_model_eval import ModelEvaluatorBase, not_applicable_result


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
        return self.parse(await runner(timeout=self.timeout, **eval_input))

    def skipped(self, reason: str, threshold: Optional[float] = None) -> Dict[str, Any]:
        result = not_applicable_result(self.result_key, reason, self.threshold if threshold is None else threshold)
        if self.top_level_usage:
            metadata = ModelEvaluatorBase._get_token_metadata({})
            result.update({f"{self.result_key}_{key}": value for key, value in metadata.items()})
        return result

    def parse(self, output: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(output, dict) or (not self.strict and not output):
            self._invalid_output()
        answer = output.get("llm_output", output if self.strict else "")
        if not self.strict and isinstance(answer, str):
            try:
                parsed = json.loads(answer)
            except (json.JSONDecodeError, TypeError):
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
            self._invalid_output()
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
                extracted = self._extract_score_from_text(answer, has_score_range=bool(self.score_range))
                if extracted is not None:
                    score = extracted
                    has_score = True
        if self.score_range:
            minimum, maximum = self.score_range
            score_for_error = score
            try:
                valid_score = (
                    has_score and not isinstance(score, bool) and check_score_is_valid(score, minimum, maximum)
                )
            except OverflowError:
                valid_score = False
                # Formatting an oversized integer can also exceed Python's decimal digit limit.
                score_for_error = "<numeric overflow>"
            if not valid_score:
                raise EvaluationException(
                    message=f"Invalid score value: {score_for_error}. Expected a number in range [{minimum}, {maximum}].",
                    internal_message="Invalid score value.",
                    category=ErrorCategory.FAILED_EXECUTION,
                    target=self.score_error_target,
                    blame=ErrorBlame.SYSTEM_ERROR,
                )
        score = float(score) if self.strict or score is not None else math.nan
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

    def _invalid_output(self) -> None:
        raise EvaluationException(
            message="Evaluator returned invalid output.",
            blame=ErrorBlame.SYSTEM_ERROR,
            category=ErrorCategory.FAILED_EXECUTION,
            target=self.error_target,
        )

    @staticmethod
    def _extract_score_from_text(llm_output: str, has_score_range: bool = False) -> Optional[float]:
        """Extract a numeric score from free-text LLM output that is not parseable JSON.

        Preference order: the whole output is a bare number, an explicitly labelled score
        (e.g. "Score: 4"), trailing verdict score after colon, then numeric fallback.
        Taking the first digit risks scoring the judge's reasoning rather than its verdict.
        """
        match = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*", llm_output)
        if match:
            return float(match.group(1))
        match = re.search(r"[Ss]core\s*[:=]\s*(\d+(?:\.\d+)?)", llm_output)
        if match:
            return float(match.group(1))
        match = re.search(r"(\d+(?:\.\d+)?)\s*(?:out of|/)\s*\d+", llm_output, re.IGNORECASE)
        if match:
            return float(match.group(1))
        match = re.search(r"[:=]\s*(\d+(?:\.\d+)?)\s*$", llm_output)
        if match:
            return float(match.group(1))
        if has_score_range:
            matches = re.findall(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?", llm_output)
            if matches:
                return float(matches[-1])
        else:
            match = re.search(r"\d", llm_output)
            if match:
                return float(match.group())
        return None
