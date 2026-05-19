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

from sample_human_evaluations import emit_human_evaluation_event  # noqa: E402


class _RecordCapture(logging.Handler):
    """Capture every ``LogRecord`` the helper emits so tests can introspect
    the ``extra=`` kwargs that ended up as attributes on the record."""

    def __init__(self) -> None:
        super().__init__(level=logging.DEBUG)
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


@pytest.fixture(autouse=True)
def capture():
    """Attach a fresh capture handler to the ``human_evaluations`` logger for
    each test and detach on teardown."""
    logger = logging.getLogger("human_evaluations")
    handler = _RecordCapture()
    logger.addHandler(handler)
    try:
        yield handler
    finally:
        logger.removeHandler(handler)


def _only_record(capture: _RecordCapture) -> logging.LogRecord:
    assert len(capture.records) == 1, f"expected exactly 1 emitted record, got {len(capture.records)}"
    return capture.records[0]


# ---------------------------------------------------------------------------
# Validation: range / integer / unknown kind
# ---------------------------------------------------------------------------


def test_binary_score_0_emits_with_fail_label(capture):
    emit_human_evaluation_event(evaluation_name="thumbs", score_value=0.0, kind="binary")
    record = _only_record(capture)
    assert record.__dict__["gen_ai.evaluation.score.label"] == "fail"
    assert record.__dict__["gen_ai.evaluation.score.value"] == 0.0


def test_binary_score_1_emits_with_pass_label(capture):
    emit_human_evaluation_event(evaluation_name="thumbs", score_value=1.0, kind="binary")
    record = _only_record(capture)
    assert record.__dict__["gen_ai.evaluation.score.label"] == "pass"
    assert record.__dict__["gen_ai.evaluation.score.value"] == 1.0


def test_binary_score_fractional_raises():
    with pytest.raises(ValueError):
        emit_human_evaluation_event(evaluation_name="thumbs", score_value=0.5, kind="binary")


def test_binary_score_out_of_range_raises():
    with pytest.raises(ValueError):
        emit_human_evaluation_event(evaluation_name="thumbs", score_value=2.0, kind="binary")


def test_likert_5_score_1_emits_with_fail_label(capture):
    emit_human_evaluation_event(evaluation_name="relevance", score_value=1.0, kind="likert_5")
    assert _only_record(capture).__dict__["gen_ai.evaluation.score.label"] == "fail"


def test_likert_5_score_at_threshold_emits_with_pass_label(capture):
    """Guards the `>=` vs `>` mistake: score == threshold must be pass."""
    emit_human_evaluation_event(evaluation_name="relevance", score_value=3.0, kind="likert_5")
    assert _only_record(capture).__dict__["gen_ai.evaluation.score.label"] == "pass"


def test_likert_5_score_5_emits_with_pass_label(capture):
    emit_human_evaluation_event(evaluation_name="relevance", score_value=5.0, kind="likert_5")
    assert _only_record(capture).__dict__["gen_ai.evaluation.score.label"] == "pass"


def test_likert_5_non_integer_score_raises():
    with pytest.raises(ValueError):
        emit_human_evaluation_event(evaluation_name="relevance", score_value=2.5, kind="likert_5")


def test_likert_5_score_out_of_range_raises():
    with pytest.raises(ValueError):
        emit_human_evaluation_event(evaluation_name="relevance", score_value=6.0, kind="likert_5")


def test_unknown_kind_raises():
    with pytest.raises(ValueError):
        emit_human_evaluation_event(
            evaluation_name="relevance",
            score_value=1.0,
            kind="unknown",  # type: ignore[arg-type]
        )


# ---------------------------------------------------------------------------
# Shape: top-level attributes + internal_properties JSON encoding
# ---------------------------------------------------------------------------


def test_top_level_attributes_have_canonical_keys_and_routing(capture):
    emit_human_evaluation_event(evaluation_name="task_completion", score_value=1.0, kind="binary")
    record = _only_record(capture)
    attrs = record.__dict__
    assert attrs["microsoft.custom_event.name"] == "gen_ai.evaluation.result"
    assert attrs["gen_ai.evaluation.name"] == "task_completion"
    assert attrs["gen_ai.evaluation.score.value"] == 1.0
    assert attrs["gen_ai.evaluation.score.label"] == "pass"
    # internal_properties must be present as a top-level attribute too.
    assert "internal_properties" in attrs


def test_internal_properties_is_json_encoded_string_with_binary_defaults(capture):
    """internal_properties MUST be a JSON-encoded string, not a nested dict,
    per the genai_human_evaluations spec.
    """
    emit_human_evaluation_event(evaluation_name="task_completion", score_value=1.0, kind="binary")
    raw = _only_record(capture).__dict__["internal_properties"]
    assert isinstance(raw, str)
    decoded = json.loads(raw)
    assert decoded["gen_ai.evaluation.threshold"] == "1.0"
    assert decoded["gen_ai.evaluation.min_value"] == "0.0"
    assert decoded["gen_ai.evaluation.max_value"] == "1.0"
    assert decoded["gen_ai.evaluation.desirable_direction"] == "increase"
    assert decoded["gen_ai.evaluation.type"] == "boolean"
    assert decoded["microsoft.human_evaluation.source"] == "end_user"
    assert decoded["microsoft.human_evaluation.kind"] == "binary"


def test_internal_properties_likert_5_defaults(capture):
    emit_human_evaluation_event(evaluation_name="relevance", score_value=4.0, kind="likert_5")
    decoded = json.loads(_only_record(capture).__dict__["internal_properties"])
    assert decoded["gen_ai.evaluation.threshold"] == "3.0"
    assert decoded["gen_ai.evaluation.min_value"] == "1.0"
    assert decoded["gen_ai.evaluation.max_value"] == "5.0"
    assert decoded["gen_ai.evaluation.type"] == "ordinal"
    assert decoded["microsoft.human_evaluation.kind"] == "likert_5"


# ---------------------------------------------------------------------------
# Conditional fields
# ---------------------------------------------------------------------------


def test_response_id_set_adds_top_level_id_and_internal_type(capture):
    emit_human_evaluation_event(
        evaluation_name="task_completion",
        score_value=1.0,
        kind="binary",
        response_id="resp_abc123",
    )
    record = _only_record(capture)
    assert record.__dict__["gen_ai.response.id"] == "resp_abc123"
    decoded = json.loads(record.__dict__["internal_properties"])
    assert decoded["gen_ai.response.id.type"] == "responses"


def test_response_id_omitted_omits_both_keys(capture):
    emit_human_evaluation_event(evaluation_name="task_completion", score_value=1.0, kind="binary")
    record = _only_record(capture)
    assert "gen_ai.response.id" not in record.__dict__
    decoded = json.loads(record.__dict__["internal_properties"])
    assert "gen_ai.response.id.type" not in decoded


def test_project_resource_id_set_added_to_internal_properties(capture):
    arm_id = (
        "/subscriptions/sub-id/resourceGroups/rg/providers/Microsoft.CognitiveServices"
        "/accounts/acct/projects/proj"
    )
    emit_human_evaluation_event(
        evaluation_name="task_completion",
        score_value=1.0,
        kind="binary",
        project_resource_id=arm_id,
    )
    decoded = json.loads(_only_record(capture).__dict__["internal_properties"])
    assert decoded["gen_ai.azure_ai_project.id"] == arm_id


def test_project_resource_id_omitted_omits_key(capture):
    emit_human_evaluation_event(evaluation_name="task_completion", score_value=1.0, kind="binary")
    decoded = json.loads(_only_record(capture).__dict__["internal_properties"])
    assert "gen_ai.azure_ai_project.id" not in decoded


def test_enduser_id_only_sets_only_authenticated_attribute(capture):
    emit_human_evaluation_event(
        evaluation_name="task_completion",
        score_value=1.0,
        kind="binary",
        enduser_id="user-oid-123",
    )
    attrs = _only_record(capture).__dict__
    assert attrs["enduser.id"] == "user-oid-123"
    assert "enduser.pseudo.id" not in attrs


def test_enduser_pseudo_id_only_sets_only_pseudo_attribute(capture):
    emit_human_evaluation_event(
        evaluation_name="task_completion",
        score_value=1.0,
        kind="binary",
        enduser_pseudo_id="sess_abc",
    )
    attrs = _only_record(capture).__dict__
    assert attrs["enduser.pseudo.id"] == "sess_abc"
    assert "enduser.id" not in attrs


def test_both_enduser_ids_set_both_attributes(capture):
    emit_human_evaluation_event(
        evaluation_name="task_completion",
        score_value=1.0,
        kind="binary",
        enduser_id="user-oid-123",
        enduser_pseudo_id="sess_abc",
    )
    attrs = _only_record(capture).__dict__
    assert attrs["enduser.id"] == "user-oid-123"
    assert attrs["enduser.pseudo.id"] == "sess_abc"


def test_tags_fan_out_as_top_level_attributes(capture):
    emit_human_evaluation_event(
        evaluation_name="task_completion",
        score_value=1.0,
        kind="binary",
        tags={"subscription_tier": "basic_plan", "department": "marketing"},
    )
    attrs = _only_record(capture).__dict__
    assert attrs["microsoft.human_evaluation.tags.subscription_tier"] == "basic_plan"
    assert attrs["microsoft.human_evaluation.tags.department"] == "marketing"
    # And explicitly: tags must NOT also be inside internal_properties.
    decoded = json.loads(attrs["internal_properties"])
    assert "microsoft.human_evaluation.tags.subscription_tier" not in decoded
    assert "microsoft.human_evaluation.tags.department" not in decoded


def test_evaluation_id_omitted_omits_attribute(capture):
    emit_human_evaluation_event(evaluation_name="task_completion", score_value=1.0, kind="binary")
    attrs = _only_record(capture).__dict__
    assert "microsoft.human_evaluation.id" not in attrs
    # And explicitly: id must not be inside internal_properties either.
    decoded = json.loads(attrs["internal_properties"])
    assert "microsoft.human_evaluation.id" not in decoded


def test_evaluation_id_provided_flows_through_verbatim_as_top_level_attribute(capture):
    emit_human_evaluation_event(
        evaluation_name="task_completion",
        score_value=1.0,
        kind="binary",
        evaluation_id="custom-eval-id-42",
    )
    attrs = _only_record(capture).__dict__
    assert attrs["microsoft.human_evaluation.id"] == "custom-eval-id-42"
    # And explicitly: id must not also be inside internal_properties.
    decoded = json.loads(attrs["internal_properties"])
    assert "microsoft.human_evaluation.id" not in decoded


def test_explanation_flows_through_as_top_level_attribute(capture):
    emit_human_evaluation_event(
        evaluation_name="task_completion",
        score_value=1.0,
        kind="binary",
        explanation="The agent answered correctly.",
    )
    record = _only_record(capture)
    assert record.__dict__["gen_ai.evaluation.explanation"] == "The agent answered correctly."


def test_explanation_omitted_omits_attribute(capture):
    emit_human_evaluation_event(evaluation_name="task_completion", score_value=1.0, kind="binary")
    record = _only_record(capture)
    assert "gen_ai.evaluation.explanation" not in record.__dict__
