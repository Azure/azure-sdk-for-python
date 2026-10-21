import asyncio
import math
from unittest.mock import AsyncMock

import pytest

from azure.ai.evaluation._evaluators._common._prompty_strategy import PromptyEvaluationStrategy
from azure.ai.evaluation._exceptions import EvaluationException, ErrorTarget


def strategy(**kwargs):
    options = {"result_key": "metric", "threshold": 3, "timeout": 17}
    options.update(kwargs)
    return PromptyEvaluationStrategy(AsyncMock(), **options)


@pytest.mark.parametrize(
    "answer,expected,reason",
    [
        ({"score": 4, "reason": "good"}, 4, "good"),
        ('{"score": 4, "reason": "good"}', 4, "good"),
        ("malformed JSON { score 4", 4, ""),
        ("the score is 2", 2, ""),
        ("[] score 2", 2, ""),
        (None, math.nan, ""),
        ({"score": None}, math.nan, ""),
        ({}, math.nan, ""),
        ("no score", math.nan, ""),
    ],
)
def test_legacy_parser(answer, expected, reason):
    result = strategy(strict=False, missing_score=math.nan).parse({"llm_output": answer})
    if math.isnan(expected):
        assert math.isnan(result["metric"])
        assert result["metric_result"] == "unknown"
        assert result["metric_passed"] is False
    else:
        assert result["metric"] == expected
    assert result["metric_reason"] == reason


def test_legacy_quality_xml():
    result = strategy(result_key="fluency", strict=False, missing_score=math.nan).parse(
        {
            "llm_output": "<S1> Clear prose </S1><S2>4</S2>",
        }
    )
    assert result["fluency"] == 4
    assert result["fluency_reason"] == "Clear prose"


@pytest.mark.parametrize(
    "higher,score,expected",
    [
        (True, 2, "fail"),
        (True, 3, "pass"),
        (True, 4, "pass"),
        (False, 2, "pass"),
        (False, 3, "pass"),
        (False, 4, "fail"),
    ],
)
def test_threshold_direction(higher, score, expected):
    assert strategy(higher_is_better=higher).parse({"score": score})["metric_result"] == expected


@pytest.mark.parametrize(
    "output",
    [
        None,
        [],
        "text",
        {"llm_output": '{"score":4}'},
        {"llm_output": []},
        {"llm_output": None},
    ],
)
def test_strict_rejects_non_dict_answer(output):
    with pytest.raises(EvaluationException, match="Evaluator returned invalid output") as error:
        strategy(error_target=ErrorTarget.TOOL_CALL_ACCURACY_EVALUATOR).parse(output)
    assert error.value.target == ErrorTarget.TOOL_CALL_ACCURACY_EVALUATOR


@pytest.mark.parametrize("score", [None, 0, -1, 6, "bad", math.nan, math.inf])
def test_score_range_errors(score):
    with pytest.raises(EvaluationException, match="Invalid score value") as error:
        strategy(score_range=(1, 5), error_target=ErrorTarget.TOOL_CALL_ACCURACY_EVALUATOR).parse({"score": score})
    assert error.value.target == ErrorTarget.TOOL_CALL_ACCURACY_EVALUATOR


@pytest.mark.parametrize("strict", [True, False])
@pytest.mark.parametrize("score", [0, 0.0, "0"])
def test_zero_inclusive_range_accepts_an_explicit_zero(strict, score):
    """A parsed zero is a valid score, not a missing-score sentinel."""
    result = strategy(strict=strict, score_range=(0, 1)).parse({"llm_output": {"score": score}})
    assert result["metric"] == 0.0
    assert result["metric_status"] == "completed"


@pytest.mark.parametrize("missing_score", [0, 1])
@pytest.mark.parametrize("strict", [True, False])
@pytest.mark.parametrize(
    "answer",
    [
        {},
        {"reason": "no score"},
        {"score": None},
        {"score": ""},
        {"score": "bad"},
        {"score": math.nan},
        {"score": True},
        {"score": False},
    ],
)
def test_zero_inclusive_range_rejects_missing_or_invalid_scores(strict, missing_score, answer):
    """A default fallback must not manufacture a valid ranged grade."""
    with pytest.raises(EvaluationException, match="Invalid score value"):
        strategy(strict=strict, missing_score=missing_score, score_range=(0, 1)).parse({"llm_output": answer})


@pytest.mark.parametrize("answer", ['{"score": 0}', "the score is 0"])
def test_zero_inclusive_range_accepts_a_parsed_text_zero(answer):
    """Legacy textual and JSON parsing retain explicit zero scores."""
    result = strategy(strict=False, score_range=(0, 1)).parse({"llm_output": answer})
    assert result["metric"] == 0.0


@pytest.mark.parametrize("answer,valid", [("<S1>Reason</S1><S2>0</S2>", True), ("No grade", False)])
def test_quality_text_zero_is_distinct_from_a_missing_grade(answer, valid):
    """The quality parser reports presence independently of its numeric fallback."""
    configured = strategy(result_key="fluency", strict=False, score_range=(0, 5))
    if valid:
        assert configured.parse({"llm_output": answer})["fluency"] == 0.0
    else:
        with pytest.raises(EvaluationException, match="Invalid score value"):
            configured.parse({"llm_output": answer})


@pytest.mark.parametrize("score", ["-1", "6", "1e309"])
def test_explicit_quality_text_range_rejects_out_of_range_scores(score):
    """An explicit range validates the full parsed number instead of a leading digit."""
    with pytest.raises(EvaluationException, match="Invalid score value"):
        strategy(result_key="fluency", strict=False, score_range=(0, 5)).parse(
            {"llm_output": f"<S1>Reason</S1><S2>{score}</S2>"}
        )


def test_legacy_quality_text_domain_is_unchanged_without_an_explicit_range():
    """The existing quality parser still accepts only its default one-through-five domain."""
    result = strategy(result_key="fluency", strict=False).parse({"llm_output": "<S1>Reason</S1><S2>0</S2>"})
    assert math.isnan(result["fluency"])
    assert result["fluency_result"] == "unknown"


def test_missing_completion_score_and_binary_rule():
    completion = strategy(binary_cutoff=1, threshold=7)
    assert completion.parse({})["metric"] == 0
    assert completion.parse({"score": 1})["metric_result"] == "pass"
    with pytest.raises(ValueError):
        completion.parse({"score": "bad"})


@pytest.mark.parametrize("strict", [True, False])
def test_skipped_bypasses_score_validation(strict):
    result = strategy(strict=strict, score_range=(1, 5)).parse(
        {
            "llm_output": {"score": "bad", "status": "skipped", "reason": "not relevant"},
        }
    )
    assert result == {
        "metric": None,
        "metric_score": None,
        "metric_passed": None,
        "metric_result": "not_applicable",
        "metric_reason": "Not applicable: not relevant",
        "metric_status": "skipped",
        "metric_threshold": 3,
        "metric_properties": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "finish_reason": "",
            "model": "",
            "sample_input": "",
            "sample_output": "",
        },
    }


@pytest.mark.parametrize(
    "key,alias,usage",
    [
        ("task_completion", None, False),
        ("tool_call_accuracy", "gpt_tool_call_accuracy", False),
        ("task_completion", None, True),
        ("tool_call_accuracy", None, False),
    ],
)
def test_exact_chat_schemas(key, alias, usage):
    configured = strategy(result_key=key, completed_alias=alias, top_level_usage=usage)
    output = {"llm_output": {"score": 4, "properties": {"custom": "kept"}}, "input_token_count": 9}
    completed = configured.parse(output)
    metadata = {
        "prompt_tokens": 9,
        "completion_tokens": 0,
        "total_tokens": 0,
        "finish_reason": "",
        "model": "",
        "sample_input": "",
        "sample_output": "",
    }
    expected_keys = {key} | {
        f"{key}_{suffix}"
        for suffix in (
            "score",
            "passed",
            "result",
            "reason",
            "status",
            "threshold",
            "properties",
        )
    }
    assert completed[f"{key}_properties"] == {"custom": "kept", **metadata}
    if alias:
        expected_keys.add(alias)
        assert completed[alias] == 4
    if usage:
        expected_keys.update(f"{key}_{name}" for name in metadata)
        assert completed[f"{key}_prompt_tokens"] == 9
    assert set(completed) == expected_keys
    skipped = configured.parse({"llm_output": {"status": "skipped"}, "input_token_count": 9})
    assert set(skipped) == expected_keys - ({alias} if alias else set())
    assert skipped[f"{key}_properties"] == metadata
    if usage:
        assert skipped[f"{key}_prompt_tokens"] == 9


@pytest.mark.parametrize("strict", [True, False])
@pytest.mark.parametrize("top_level_usage", [True, False])
def test_post_inference_skip_preserves_measured_usage(strict, top_level_usage):
    configured = strategy(strict=strict, top_level_usage=top_level_usage, completed_alias="legacy_metric")
    output = {
        "llm_output": {
            "status": "skipped",
            "score": None,
            "reason": "not applicable",
            "properties": {"custom": "kept"},
        },
        "input_token_count": 9,
        "output_token_count": 3,
        "total_token_count": 12,
        "model_id": "chat-judge-skip-fixture",
    }
    configured.runner.return_value = output
    result = asyncio.run(configured.evaluate({"query": "q"}))
    metadata = {
        "prompt_tokens": 9,
        "completion_tokens": 3,
        "total_tokens": 12,
        "model": "chat-judge-skip-fixture",
        "finish_reason": "",
        "sample_input": "",
        "sample_output": "",
    }
    assert result == {
        "metric": None,
        "metric_score": None,
        "metric_passed": None,
        "metric_result": "not_applicable",
        "metric_reason": "Not applicable: not applicable",
        "metric_status": "skipped",
        "metric_threshold": 3,
        "metric_properties": {"custom": "kept", **metadata},
        **({f"metric_{key}": value for key, value in metadata.items()} if top_level_usage else {}),
    }
    configured.runner.assert_awaited_once_with(timeout=17, query="q")


@pytest.mark.parametrize("top_level_usage", [True, False])
def test_pre_inference_skip_does_not_call_runner_or_manufacture_usage(top_level_usage):
    configured = strategy(top_level_usage=top_level_usage)
    result = configured.skipped("no applicable input")
    assert result["metric_status"] == "skipped"
    assert result["metric"] is result["metric_score"] is result["metric_passed"] is None
    assert result["metric_properties"] is None
    if top_level_usage:
        assert [result[f"metric_{key}"] for key in ("prompt_tokens", "completion_tokens", "total_tokens")] == [0, 0, 0]
        assert result["metric_model"] == ""
    else:
        assert "metric_prompt_tokens" not in result
        assert "metric_model" not in result
    configured.runner.assert_not_called()


def test_runtime_flow_resolution():
    original = AsyncMock(side_effect=AssertionError("stale flow"))
    current = original
    configured = strategy(flow_resolver=lambda: current)
    current = AsyncMock(return_value={"score": 4})
    assert asyncio.run(configured.evaluate({"query": "q"}))["metric"] == 4
    current.assert_awaited_once_with(timeout=17, query="q")
    original.assert_not_awaited()


def test_legacy_empty_envelope_is_invalid():
    with pytest.raises(EvaluationException, match="Evaluator returned invalid output"):
        strategy(strict=False).parse({})
