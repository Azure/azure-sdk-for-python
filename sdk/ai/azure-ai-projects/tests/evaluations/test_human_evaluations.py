# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
import logging
import sys
from pathlib import Path

import pytest

SAMPLES_EVALUATIONS_DIR = Path(__file__).resolve().parents[1] / ".." / "samples" / "evaluations"
sys.path.insert(0, str(SAMPLES_EVALUATIONS_DIR.resolve()))

from sample_human_evaluations import (
    emit_5_point_ordinal_evaluation,
    emit_boolean_evaluation,
)  # noqa: E402


class _RecordCapture(logging.Handler):
    """Capture emitted ``LogRecord`` instances so tests can inspect ``extra=`` attributes."""

    def __init__(self) -> None:
        super().__init__(level=logging.DEBUG)
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


@pytest.fixture(autouse=True)
def capture():
    logger = logging.getLogger("human_evaluations")
    handler = _RecordCapture()
    logger.addHandler(handler)
    try:
        yield handler
    finally:
        logger.removeHandler(handler)


def _only_attrs(capture: _RecordCapture) -> dict:
    assert len(capture.records) == 1, f"expected exactly 1 emitted record, got {len(capture.records)}"
    return capture.records[0].__dict__


def _internal_properties(attrs: dict) -> dict:
    raw = attrs["internal_properties"]
    assert isinstance(raw, str)
    return json.loads(raw)


def test_boolean_failed_emits_score_0_with_fail_label(capture):
    emit_boolean_evaluation(evaluation_metric_name="task_completion", passed=False)
    attrs = _only_attrs(capture)
    assert attrs["gen_ai.evaluation.score.label"] == "fail"
    assert attrs["gen_ai.evaluation.score.value"] == 0.0


def test_boolean_passed_emits_score_1_with_pass_label(capture):
    emit_boolean_evaluation(evaluation_metric_name="task_completion", passed=True)
    attrs = _only_attrs(capture)
    assert attrs["gen_ai.evaluation.score.label"] == "pass"
    assert attrs["gen_ai.evaluation.score.value"] == 1.0


@pytest.mark.parametrize(
    "score_value, expected_label",
    [
        (1.0, "fail"),
        (3.0, "pass"),
        (5.0, "pass"),
    ],
)
def test_ordinal_score_emits_expected_label(capture, score_value, expected_label):
    emit_5_point_ordinal_evaluation(evaluation_metric_name="relevance", score_value=score_value)
    attrs = _only_attrs(capture)
    assert attrs["gen_ai.evaluation.score.label"] == expected_label
    assert attrs["gen_ai.evaluation.score.value"] == score_value


def test_ordinal_custom_threshold_controls_label_and_flows_to_internal_properties(
    capture,
):
    emit_5_point_ordinal_evaluation(evaluation_metric_name="relevance", score_value=2.0, threshold=4.0)
    attrs = _only_attrs(capture)
    decoded = _internal_properties(attrs)
    assert attrs["gen_ai.evaluation.score.label"] == "fail"
    assert decoded["gen_ai.evaluation.threshold"] == "4.0"


def test_ordinal_non_integer_score_raises():
    with pytest.raises(ValueError):
        emit_5_point_ordinal_evaluation(evaluation_metric_name="relevance", score_value=2.5)


@pytest.mark.parametrize("score_value", [0.0, 6.0])
def test_ordinal_score_out_of_range_raises(score_value):
    with pytest.raises(ValueError):
        emit_5_point_ordinal_evaluation(evaluation_metric_name="relevance", score_value=score_value)


@pytest.mark.parametrize("threshold", [0.0, 6.0])
def test_ordinal_threshold_out_of_range_raises(threshold):
    with pytest.raises(ValueError):
        emit_5_point_ordinal_evaluation(evaluation_metric_name="relevance", score_value=4.0, threshold=threshold)


def test_top_level_attributes_have_canonical_keys_and_routing(capture):
    emit_boolean_evaluation(evaluation_metric_name="task_completion", passed=True)
    attrs = _only_attrs(capture)
    assert attrs["microsoft.custom_event.name"] == "gen_ai.evaluation.result"
    assert attrs["gen_ai.evaluation.name"] == "task_completion"
    assert attrs["gen_ai.evaluation.score.value"] == 1.0
    assert attrs["gen_ai.evaluation.score.label"] == "pass"
    assert attrs["microsoft.gen_ai.human_evaluation.source"] == "end_user"
    assert attrs["microsoft.gen_ai.evaluation.actor.type"] == "human"
    assert "internal_properties" in attrs


def test_internal_properties_is_json_encoded_string_with_boolean_defaults(capture):
    emit_boolean_evaluation(evaluation_metric_name="task_completion", passed=True)
    decoded = _internal_properties(_only_attrs(capture))
    assert decoded["gen_ai.evaluation.threshold"] == "1.0"
    assert decoded["gen_ai.evaluation.min_value"] == "0.0"
    assert decoded["gen_ai.evaluation.max_value"] == "1.0"
    assert decoded["gen_ai.evaluation.desirable_direction"] == "increase"
    assert decoded["gen_ai.evaluation.type"] == "boolean"


def test_internal_properties_ordinal_defaults(capture):
    emit_5_point_ordinal_evaluation(evaluation_metric_name="relevance", score_value=4.0)
    decoded = _internal_properties(_only_attrs(capture))
    assert decoded["gen_ai.evaluation.threshold"] == "3.0"
    assert decoded["gen_ai.evaluation.min_value"] == "1.0"
    assert decoded["gen_ai.evaluation.max_value"] == "5.0"
    assert decoded["gen_ai.evaluation.desirable_direction"] == "increase"
    assert decoded["gen_ai.evaluation.type"] == "ordinal"


def test_response_id_set_adds_top_level_id(capture):
    emit_boolean_evaluation(
        evaluation_metric_name="task_completion",
        passed=True,
        response_id="resp_abc123",
    )
    attrs = _only_attrs(capture)
    assert attrs["gen_ai.response.id"] == "resp_abc123"


def test_response_id_omitted_omits_top_level_id(capture):
    emit_boolean_evaluation(evaluation_metric_name="task_completion", passed=True)
    attrs = _only_attrs(capture)
    assert "gen_ai.response.id" not in attrs


def test_conversation_id_set_adds_top_level_id(capture):
    emit_boolean_evaluation(
        evaluation_metric_name="task_completion",
        passed=True,
        conversation_id="conv_abc123",
    )
    attrs = _only_attrs(capture)
    assert attrs["gen_ai.conversation.id"] == "conv_abc123"


def test_saved_trace_context_is_current_while_emitting(capture):
    from opentelemetry import trace

    trace_id = "4bf92f3577b34da6a3ce929d0e0e4736"
    span_id = "00f067aa0ba902b7"
    captured_contexts = []

    class _ContextCapture(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            captured_contexts.append(trace.get_current_span().get_span_context())

    logger = logging.getLogger("human_evaluations")
    handler = _ContextCapture()
    logger.addHandler(handler)
    try:
        emit_boolean_evaluation(
            evaluation_metric_name="task_completion",
            passed=True,
            trace_id=trace_id,
            span_id=span_id,
        )
    finally:
        logger.removeHandler(handler)

    _only_attrs(capture)
    assert len(captured_contexts) == 1
    assert captured_contexts[0].trace_id == int(trace_id, 16)
    assert captured_contexts[0].span_id == int(span_id, 16)


@pytest.mark.parametrize(
    "trace_id, span_id",
    [
        ("4bf92f3577b34da6a3ce929d0e0e4736", None),
        (None, "00f067aa0ba902b7"),
    ],
)
def test_trace_id_and_span_id_must_be_provided_together(trace_id, span_id):
    with pytest.raises(ValueError):
        emit_boolean_evaluation(
            evaluation_metric_name="task_completion",
            passed=True,
            trace_id=trace_id,
            span_id=span_id,
        )


def test_project_resource_id_set_added_to_internal_properties(capture):
    arm_id = (
        "/subscriptions/sub-id/resourceGroups/rg/providers/Microsoft.CognitiveServices" "/accounts/acct/projects/proj"
    )
    emit_boolean_evaluation(
        evaluation_metric_name="task_completion",
        passed=True,
        project_resource_id=arm_id,
    )
    decoded = _internal_properties(_only_attrs(capture))
    assert decoded["gen_ai.azure_ai_project.id"] == arm_id


def test_project_resource_id_omitted_omits_key(capture):
    emit_boolean_evaluation(evaluation_metric_name="task_completion", passed=True)
    decoded = _internal_properties(_only_attrs(capture))
    assert "gen_ai.azure_ai_project.id" not in decoded


def test_enduser_id_only_sets_only_authenticated_attribute(capture):
    emit_boolean_evaluation(
        evaluation_metric_name="task_completion",
        passed=True,
        enduser_id="user-oid-123",
    )
    attrs = _only_attrs(capture)
    assert attrs["enduser.id"] == "user-oid-123"
    assert "enduser.pseudo.id" not in attrs


def test_enduser_pseudo_id_only_sets_only_pseudo_attribute(capture):
    emit_boolean_evaluation(
        evaluation_metric_name="task_completion",
        passed=True,
        enduser_pseudo_id="sess_abc",
    )
    attrs = _only_attrs(capture)
    assert attrs["enduser.pseudo.id"] == "sess_abc"
    assert "enduser.id" not in attrs


def test_both_enduser_ids_set_both_attributes(capture):
    emit_boolean_evaluation(
        evaluation_metric_name="task_completion",
        passed=True,
        enduser_id="user-oid-123",
        enduser_pseudo_id="sess_abc",
    )
    attrs = _only_attrs(capture)
    assert attrs["enduser.id"] == "user-oid-123"
    assert attrs["enduser.pseudo.id"] == "sess_abc"


def test_tags_fan_out_as_top_level_attributes(capture):
    emit_boolean_evaluation(
        evaluation_metric_name="task_completion",
        passed=True,
        tags={"subscription_tier": "basic_plan", "department": "marketing"},
    )
    attrs = _only_attrs(capture)
    assert attrs["microsoft.gen_ai.evaluation.tags.subscription_tier"] == "basic_plan"
    assert attrs["microsoft.gen_ai.evaluation.tags.department"] == "marketing"


def test_evaluation_id_omitted_omits_attribute(capture):
    emit_boolean_evaluation(evaluation_metric_name="task_completion", passed=True)
    attrs = _only_attrs(capture)
    assert "microsoft.gen_ai.human_evaluation.id" not in attrs


def test_evaluation_id_provided_flows_through_verbatim_as_top_level_attribute(capture):
    emit_boolean_evaluation(
        evaluation_metric_name="task_completion",
        passed=True,
        evaluation_id="custom-eval-id-42",
    )
    attrs = _only_attrs(capture)
    assert attrs["microsoft.gen_ai.human_evaluation.id"] == "custom-eval-id-42"


def test_explanation_flows_through_as_top_level_attribute(capture):
    emit_boolean_evaluation(
        evaluation_metric_name="task_completion",
        passed=True,
        explanation="The agent answered correctly.",
    )
    attrs = _only_attrs(capture)
    assert attrs["gen_ai.evaluation.explanation"] == "The agent answered correctly."


def test_explanation_omitted_omits_attribute(capture):
    emit_boolean_evaluation(evaluation_metric_name="task_completion", passed=True)
    attrs = _only_attrs(capture)
    assert "gen_ai.evaluation.explanation" not in attrs
