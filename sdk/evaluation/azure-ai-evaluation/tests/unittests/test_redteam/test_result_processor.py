# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for ResultProcessor._clean_content_filter_response and helpers."""

import json

from azure.ai.evaluation.red_team._result_processor import ResultProcessor


class TestCleanContentFilterResponse:
    """Tests addressing PR #45528 review comments on _clean_content_filter_response."""

    # -- positive: real content-filter JSON payload (choices structure) -------
    def test_json_payload_with_filtered_choices(self):
        payload = json.dumps(
            {
                "choices": [
                    {
                        "content_filter_results": {
                            "hate": {"filtered": True, "severity": "high"},
                            "violence": {"filtered": False, "severity": "safe"},
                        }
                    }
                ]
            }
        )
        result = ResultProcessor._clean_content_filter_response(payload)
        assert "hate (severity: high)" in result
        assert "violence" not in result
        assert result.startswith("[Response blocked by content filter:")

    def test_json_payload_multiple_categories_filtered(self):
        payload = json.dumps(
            {
                "choices": [
                    {
                        "content_filter_results": {
                            "hate": {"filtered": True, "severity": "medium"},
                            "sexual": {"filtered": True, "severity": "high"},
                        }
                    }
                ]
            }
        )
        result = ResultProcessor._clean_content_filter_response(payload)
        assert "hate (severity: medium)" in result
        assert "sexual (severity: high)" in result

    # -- positive: finish_reason content_filter (no detail extraction) -------
    def test_json_payload_finish_reason_content_filter(self):
        payload = json.dumps({"choices": [{"finish_reason": "content_filter"}]})
        result = ResultProcessor._clean_content_filter_response(payload)
        assert result == "[Response blocked by Azure OpenAI content filter]"

    # -- positive: nested "message" JSON format ------------------------------
    def test_nested_message_json(self):
        inner = json.dumps(
            {
                "choices": [
                    {
                        "content_filter_results": {
                            "self_harm": {"filtered": True, "severity": "medium"},
                        }
                    }
                ]
            }
        )
        outer = json.dumps({"error": {"message": inner}})
        result = ResultProcessor._clean_content_filter_response(outer)
        assert "self_harm (severity: medium)" in result

    # -- positive: top-level content_filter_results (no choices wrapper) -----
    def test_top_level_content_filter_results(self):
        payload = json.dumps(
            {
                "content_filter_results": {
                    "violence": {"filtered": True, "severity": "high"},
                }
            }
        )
        result = ResultProcessor._clean_content_filter_response(payload)
        assert "violence (severity: high)" in result

    # -- negative: normal text mentioning content_filter is NOT modified -----
    def test_plain_text_mentioning_content_filter_unchanged(self):
        text = "The content_filter module handles policy violations."
        result = ResultProcessor._clean_content_filter_response(text)
        assert result == text

    def test_plain_text_mentioning_content_management_policy_unchanged(self):
        text = "Our content management policy requires review of all outputs."
        result = ResultProcessor._clean_content_filter_response(text)
        assert result == text

    def test_normal_sentence_with_filter_word(self):
        text = 'The system said "content_filter_results are logged for auditing".'
        result = ResultProcessor._clean_content_filter_response(text)
        assert result == text

    # -- non-string inputs (Comment 3) --------------------------------------
    def test_non_string_int_returns_str(self):
        result = ResultProcessor._clean_content_filter_response(42)
        assert result == "42"

    def test_non_string_dict_returns_str(self):
        result = ResultProcessor._clean_content_filter_response({"key": "value"})
        assert result == "{'key': 'value'}"

    def test_non_string_none_returns_empty(self):
        result = ResultProcessor._clean_content_filter_response(None)
        assert result == ""

    def test_non_string_list_returns_str(self):
        result = ResultProcessor._clean_content_filter_response([1, 2, 3])
        assert result == "[1, 2, 3]"

    # -- empty / whitespace edge cases --------------------------------------
    def test_empty_string_returns_empty(self):
        assert ResultProcessor._clean_content_filter_response("") == ""

    def test_whitespace_only_passthrough(self):
        assert ResultProcessor._clean_content_filter_response("   ") == "   "

    # -- regex fallback for truncated JSON -----------------------------------
    def test_truncated_json_with_filter_details_regex_fallback(self):
        # Starts with '{' but not valid JSON — should fall back to regex
        broken = '{"choices":[{"hate":{"filtered": true, "severity":"high"}'
        result = ResultProcessor._clean_content_filter_response(broken)
        assert "hate (severity: high)" in result

    # -- JSON that parses but has no filter indicators → passthrough ---------
    def test_json_without_filter_keys_passthrough(self):
        payload = json.dumps({"choices": [{"text": "hello"}]})
        result = ResultProcessor._clean_content_filter_response(payload)
        assert result == payload

    # -- false-positive prevention: unfiltered responses are NOT rewritten ---
    def test_unfiltered_response_with_cfr_keys_passthrough(self):
        """Azure OpenAI always includes content_filter_results even when
        nothing is filtered. These must NOT be rewritten as 'blocked'."""
        payload = json.dumps(
            {
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {"content": "Hello!"},
                        "content_filter_results": {
                            "hate": {"filtered": False, "severity": "safe"},
                            "self_harm": {"filtered": False, "severity": "safe"},
                            "sexual": {"filtered": False, "severity": "safe"},
                            "violence": {"filtered": False, "severity": "safe"},
                        },
                    }
                ]
            }
        )
        result = ResultProcessor._clean_content_filter_response(payload)
        assert result == payload

    def test_top_level_cfr_all_unfiltered_passthrough(self):
        """Top-level content_filter_results with nothing filtered → passthrough."""
        payload = json.dumps(
            {
                "content_filter_results": {
                    "hate": {"filtered": False, "severity": "safe"},
                    "violence": {"filtered": False, "severity": "safe"},
                }
            }
        )
        result = ResultProcessor._clean_content_filter_response(payload)
        assert result == payload

    def test_finish_reason_content_filter_no_details_gives_generic_message(self):
        """finish_reason: content_filter with empty cfr → generic blocked message."""
        payload = json.dumps({"choices": [{"finish_reason": "content_filter", "content_filter_results": {}}]})
        result = ResultProcessor._clean_content_filter_response(payload)
        assert result == "[Response blocked by Azure OpenAI content filter]"

    # -- generic regex: non-standard category names --------------------------
    def test_regex_fallback_non_standard_category(self):
        """Step 3 regex should detect any category, not just the 4 hardcoded ones."""
        broken = '{"choices":[{"custom_risk":{"filtered": true, "severity":"medium"}}'
        result = ResultProcessor._clean_content_filter_response(broken)
        assert "custom_risk (severity: medium)" in result


class TestExtractFilterDetailsFromParsed:
    """Unit tests for the helper that extracts categories from parsed dicts."""

    def test_choices_structure(self):
        parsed = {"choices": [{"content_filter_results": {"violence": {"filtered": True, "severity": "high"}}}]}
        details = ResultProcessor._extract_filter_details_from_parsed(parsed)
        assert details == ["violence (severity: high)"]

    def test_non_dict_input_returns_empty(self):
        assert ResultProcessor._extract_filter_details_from_parsed("not a dict") == []
        assert ResultProcessor._extract_filter_details_from_parsed(None) == []

    def test_top_level_cfr(self):
        parsed = {"content_filter_results": {"hate": {"filtered": True, "severity": "low"}}}
        details = ResultProcessor._extract_filter_details_from_parsed(parsed)
        assert details == ["hate (severity: low)"]


class TestHasFinishReasonContentFilter:
    """Unit tests for _has_finish_reason_content_filter."""

    def test_finish_reason_in_choices(self):
        parsed = {"choices": [{"finish_reason": "content_filter"}]}
        assert ResultProcessor._has_finish_reason_content_filter(parsed) is True

    def test_top_level_finish_reason(self):
        assert ResultProcessor._has_finish_reason_content_filter({"finish_reason": "content_filter"}) is True

    def test_finish_reason_stop(self):
        parsed = {"choices": [{"finish_reason": "stop"}]}
        assert ResultProcessor._has_finish_reason_content_filter(parsed) is False

    def test_no_finish_reason(self):
        assert ResultProcessor._has_finish_reason_content_filter({"choices": [{"text": "hi"}]}) is False

    def test_cfr_keys_without_finish_reason_returns_false(self):
        """content_filter_results key alone should NOT indicate blocking."""
        parsed = {"choices": [{"content_filter_results": {"hate": {"filtered": False}}}]}
        assert ResultProcessor._has_finish_reason_content_filter(parsed) is False

    def test_non_dict(self):
        assert ResultProcessor._has_finish_reason_content_filter([1, 2]) is False


# ---------------------------------------------------------------------------
# Tests for _compute_result_count
# ---------------------------------------------------------------------------
import logging
import math
import pytest
from unittest.mock import MagicMock

from azure.ai.evaluation.red_team._attack_objective_generator import RiskCategory


def _make_processor(risk_categories=None, thresholds=None, scenario="test"):
    """Helper to construct a ResultProcessor with sensible defaults."""
    return ResultProcessor(
        logger=logging.getLogger("test"),
        attack_success_thresholds=thresholds or {},
        application_scenario=scenario,
        risk_categories=risk_categories or [RiskCategory.Violence],
    )


@pytest.mark.unittest
class TestComputeResultCount:
    """Tests for ResultProcessor._compute_result_count."""

    def test_empty_output_items(self):
        result = ResultProcessor._compute_result_count([])
        assert result == {"total": 0, "passed": 0, "failed": 0, "errored": 0}

    def test_all_passed(self):
        items = [
            {"sample": {}, "results": [{"passed": True}]},
            {"sample": {}, "results": [{"passed": True}]},
        ]
        result = ResultProcessor._compute_result_count(items)
        assert result == {"total": 2, "passed": 2, "failed": 0, "errored": 0}

    def test_all_failed(self):
        items = [
            {"sample": {}, "results": [{"passed": False}]},
            {"sample": {}, "results": [{"passed": False}]},
        ]
        result = ResultProcessor._compute_result_count(items)
        assert result == {"total": 2, "passed": 0, "failed": 2, "errored": 0}

    def test_mixed_pass_fail(self):
        items = [
            {"sample": {}, "results": [{"passed": True}]},
            {"sample": {}, "results": [{"passed": False}]},
            {"sample": {}, "results": [{"passed": True}]},
        ]
        result = ResultProcessor._compute_result_count(items)
        assert result == {"total": 3, "passed": 2, "failed": 1, "errored": 0}

    def test_error_in_sample(self):
        items = [
            {"sample": {"error": {"message": "boom"}}, "results": [{"passed": True}]},
        ]
        result = ResultProcessor._compute_result_count(items)
        assert result == {"total": 1, "passed": 0, "failed": 0, "errored": 1}

    def test_no_results_counted_as_errored(self):
        items = [{"sample": {}, "results": []}]
        result = ResultProcessor._compute_result_count(items)
        assert result == {"total": 1, "passed": 0, "failed": 0, "errored": 1}

    def test_all_none_passed_counted_as_errored(self):
        """Results where all passed values are None → errored."""
        items = [{"sample": {}, "results": [{"passed": None}]}]
        result = ResultProcessor._compute_result_count(items)
        assert result == {"total": 1, "passed": 0, "failed": 0, "errored": 1}

    def test_mixed_none_and_false_counts_as_failed(self):
        """If any result has passed=False, the item is failed even if others are None."""
        items = [
            {"sample": {}, "results": [{"passed": None}, {"passed": False}]},
        ]
        result = ResultProcessor._compute_result_count(items)
        assert result["failed"] == 1
        assert result["errored"] == 0

    def test_failed_takes_priority_over_passed(self):
        """If results have both passed=True and passed=False, failed wins."""
        items = [
            {"sample": {}, "results": [{"passed": True}, {"passed": False}]},
        ]
        result = ResultProcessor._compute_result_count(items)
        assert result["failed"] == 1
        assert result["passed"] == 0

    def test_missing_sample_key(self):
        """Items without 'sample' key should still work (sample defaults to {})."""
        items = [{"results": [{"passed": True}]}]
        result = ResultProcessor._compute_result_count(items)
        assert result["passed"] == 1

    def test_non_dict_results_skipped(self):
        """Non-dict entries in results are skipped; if no valid ones, errored."""
        items = [{"sample": {}, "results": ["not_a_dict", 42]}]
        result = ResultProcessor._compute_result_count(items)
        assert result["errored"] == 1


# ---------------------------------------------------------------------------
# Tests for _compute_per_model_usage
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestComputePerModelUsage:
    """Tests for ResultProcessor._compute_per_model_usage."""

    def test_empty_items(self):
        assert ResultProcessor._compute_per_model_usage([]) == []

    def test_sample_usage_aggregation(self):
        items = [
            {
                "sample": {
                    "usage": {
                        "model_name": "gpt-4",
                        "prompt_tokens": 10,
                        "completion_tokens": 5,
                        "total_tokens": 15,
                        "cached_tokens": 0,
                    }
                },
                "results": [],
            },
            {
                "sample": {
                    "usage": {
                        "model_name": "gpt-4",
                        "prompt_tokens": 20,
                        "completion_tokens": 10,
                        "total_tokens": 30,
                        "cached_tokens": 2,
                    }
                },
                "results": [],
            },
        ]
        result = ResultProcessor._compute_per_model_usage(items)
        assert len(result) == 1
        assert result[0]["model_name"] == "gpt-4"
        assert result[0]["prompt_tokens"] == 30
        assert result[0]["completion_tokens"] == 15
        assert result[0]["total_tokens"] == 45
        assert result[0]["cached_tokens"] == 2
        assert result[0]["invocation_count"] == 2

    def test_default_model_name(self):
        """When model_name is absent, falls back to 'azure_ai_system_model'."""
        items = [
            {
                "sample": {"usage": {"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8}},
                "results": [],
            }
        ]
        result = ResultProcessor._compute_per_model_usage(items)
        assert result[0]["model_name"] == "azure_ai_system_model"

    def test_evaluator_metrics_aggregation(self):
        """Evaluator usage from results[].properties.metrics is aggregated."""
        items = [
            {
                "sample": {},
                "results": [{"properties": {"metrics": {"promptTokens": 100, "completionTokens": 50}}}],
            }
        ]
        result = ResultProcessor._compute_per_model_usage(items)
        assert len(result) == 1
        assert result[0]["model_name"] == "azure_ai_system_model"
        assert result[0]["prompt_tokens"] == 100
        assert result[0]["completion_tokens"] == 50
        assert result[0]["total_tokens"] == 150

    def test_multiple_models_sorted(self):
        items = [
            {
                "sample": {
                    "usage": {"model_name": "gpt-4", "prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}
                },
                "results": [],
            },
            {
                "sample": {
                    "usage": {"model_name": "gpt-3.5", "prompt_tokens": 2, "completion_tokens": 2, "total_tokens": 4}
                },
                "results": [],
            },
        ]
        result = ResultProcessor._compute_per_model_usage(items)
        assert len(result) == 2
        assert result[0]["model_name"] == "gpt-3.5"
        assert result[1]["model_name"] == "gpt-4"

    def test_non_dict_items_skipped(self):
        items = ["not_a_dict", None, 42]
        assert ResultProcessor._compute_per_model_usage(items) == []

    def test_no_usage_returns_empty(self):
        items = [{"sample": {}, "results": []}]
        assert ResultProcessor._compute_per_model_usage(items) == []

    def test_zero_token_metrics_not_counted_as_invocation(self):
        """When both promptTokens and completionTokens are 0, invocation_count stays 0."""
        items = [
            {
                "sample": {},
                "results": [{"properties": {"metrics": {"promptTokens": 0, "completionTokens": 0}}}],
            }
        ]
        result = ResultProcessor._compute_per_model_usage(items)
        # Model entry may still be created but invocation count should be 0
        if result:
            assert result[0]["invocation_count"] == 0
            assert result[0]["prompt_tokens"] == 0


# ---------------------------------------------------------------------------
# Tests for _normalize_sample_message
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestNormalizeSampleMessage:
    """Tests for ResultProcessor._normalize_sample_message."""

    def test_basic_user_message(self):
        msg = {"role": "user", "content": "hello"}
        result = ResultProcessor._normalize_sample_message(msg)
        assert result == {"role": "user", "content": "hello"}

    def test_filters_unknown_keys(self):
        msg = {"role": "user", "content": "hi", "context": "ignored", "metadata": {}}
        result = ResultProcessor._normalize_sample_message(msg)
        assert "context" not in result
        assert "metadata" not in result

    def test_none_values_excluded(self):
        msg = {"role": "user", "content": None}
        result = ResultProcessor._normalize_sample_message(msg)
        assert "content" not in result

    def test_tool_calls_only_for_assistant(self):
        msg = {"role": "user", "tool_calls": [{"id": "1"}]}
        result = ResultProcessor._normalize_sample_message(msg)
        assert "tool_calls" not in result

    def test_tool_calls_for_assistant(self):
        msg = {"role": "assistant", "content": "x", "tool_calls": [{"id": "1"}, {"id": "2"}]}
        result = ResultProcessor._normalize_sample_message(msg)
        assert len(result["tool_calls"]) == 2

    def test_tool_calls_filters_non_dicts(self):
        msg = {"role": "assistant", "content": "x", "tool_calls": ["bad", {"id": "1"}, 42]}
        result = ResultProcessor._normalize_sample_message(msg)
        assert result["tool_calls"] == [{"id": "1"}]

    def test_assistant_content_gets_cleaned(self):
        """Assistant messages should have content cleaned via _clean_content_filter_response."""
        msg = {"role": "assistant", "content": "normal text"}
        result = ResultProcessor._normalize_sample_message(msg)
        assert result["content"] == "normal text"

    def test_name_field_preserved(self):
        msg = {"role": "user", "content": "hi", "name": "test_user"}
        result = ResultProcessor._normalize_sample_message(msg)
        assert result["name"] == "test_user"


# ---------------------------------------------------------------------------
# Tests for _clean_attack_detail_messages
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestCleanAttackDetailMessages:
    """Tests for ResultProcessor._clean_attack_detail_messages."""

    def test_basic_messages(self):
        messages = [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "world"},
        ]
        result = ResultProcessor._clean_attack_detail_messages(messages)
        assert len(result) == 2
        assert result[0] == {"role": "user", "content": "hello"}
        assert result[1] == {"role": "assistant", "content": "world"}

    def test_context_field_removed(self):
        messages = [{"role": "user", "content": "hi", "context": "some context"}]
        result = ResultProcessor._clean_attack_detail_messages(messages)
        assert "context" not in result[0]

    def test_tool_calls_only_for_assistant(self):
        messages = [
            {"role": "user", "content": "hi", "tool_calls": [{"id": "1"}]},
            {"role": "assistant", "content": "ok", "tool_calls": [{"id": "2"}]},
        ]
        result = ResultProcessor._clean_attack_detail_messages(messages)
        assert "tool_calls" not in result[0]
        assert result[1]["tool_calls"] == [{"id": "2"}]

    def test_non_dict_messages_skipped(self):
        messages = ["not_dict", None, {"role": "user", "content": "hi"}]
        result = ResultProcessor._clean_attack_detail_messages(messages)
        assert len(result) == 1

    def test_empty_messages(self):
        assert ResultProcessor._clean_attack_detail_messages([]) == []

    def test_name_field_preserved(self):
        messages = [{"role": "user", "content": "hi", "name": "tester"}]
        result = ResultProcessor._clean_attack_detail_messages(messages)
        assert result[0]["name"] == "tester"

    def test_empty_dict_skipped(self):
        """A message dict with no recognized keys produces an empty dict, which is skipped."""
        messages = [{"context": "only_context"}, {"role": "user", "content": "ok"}]
        result = ResultProcessor._clean_attack_detail_messages(messages)
        assert len(result) == 1


# ---------------------------------------------------------------------------
# Tests for _normalize_numeric
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestNormalizeNumeric:
    """Tests for ResultProcessor._normalize_numeric."""

    def setup_method(self):
        self.proc = _make_processor()

    def test_none_returns_none(self):
        assert self.proc._normalize_numeric(None) is None

    def test_int_passthrough(self):
        assert self.proc._normalize_numeric(5) == 5

    def test_float_passthrough(self):
        assert self.proc._normalize_numeric(3.14) == 3.14

    def test_nan_returns_none(self):
        assert self.proc._normalize_numeric(float("nan")) is None

    def test_string_int(self):
        assert self.proc._normalize_numeric("42") == 42

    def test_string_float(self):
        assert self.proc._normalize_numeric("3.14") == 3.14

    def test_empty_string(self):
        assert self.proc._normalize_numeric("") is None

    def test_whitespace_string(self):
        assert self.proc._normalize_numeric("   ") is None

    def test_non_numeric_string(self):
        assert self.proc._normalize_numeric("abc") is None

    def test_math_nan(self):
        assert self.proc._normalize_numeric(math.nan) is None


# ---------------------------------------------------------------------------
# Tests for _is_missing
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestIsMissing:
    """Tests for ResultProcessor._is_missing."""

    def setup_method(self):
        self.proc = _make_processor()

    def test_none_is_missing(self):
        assert self.proc._is_missing(None) is True

    def test_nan_is_missing(self):
        assert self.proc._is_missing(float("nan")) is True

    def test_zero_is_not_missing(self):
        assert self.proc._is_missing(0) is False

    def test_empty_string_is_not_missing(self):
        assert self.proc._is_missing("") is False

    def test_valid_value_not_missing(self):
        assert self.proc._is_missing("hello") is False

    def test_string_value_not_missing(self):
        assert self.proc._is_missing("text") is False


# ---------------------------------------------------------------------------
# Tests for _resolve_created_time
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestResolveCreatedTime:
    """Tests for ResultProcessor._resolve_created_time."""

    def setup_method(self):
        self.proc = _make_processor()

    def test_none_eval_row_returns_current_time(self):
        result = self.proc._resolve_created_time(None)
        assert isinstance(result, int)
        assert result > 0

    def test_int_timestamp(self):
        assert self.proc._resolve_created_time({"created_time": 1700000000}) == 1700000000

    def test_float_timestamp_truncated(self):
        assert self.proc._resolve_created_time({"created_time": 1700000000.5}) == 1700000000

    def test_iso_string_timestamp(self):
        result = self.proc._resolve_created_time({"created_at": "2024-01-15T00:00:00"})
        assert isinstance(result, int)
        assert result > 0

    def test_fallback_through_keys(self):
        """Falls back from created_time → created_at → timestamp."""
        result = self.proc._resolve_created_time({"timestamp": 1234567890})
        assert result == 1234567890

    def test_invalid_string_falls_through(self):
        """Non-ISO string is skipped gracefully."""
        result = self.proc._resolve_created_time({"created_time": "not-a-date"})
        assert isinstance(result, int)  # falls back to utcnow

    def test_none_values_skipped(self):
        result = self.proc._resolve_created_time({"created_time": None, "timestamp": 99999})
        assert result == 99999

    def test_empty_dict_returns_current(self):
        result = self.proc._resolve_created_time({})
        assert isinstance(result, int)


# ---------------------------------------------------------------------------
# Tests for _resolve_output_item_id
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestResolveOutputItemId:
    """Tests for ResultProcessor._resolve_output_item_id."""

    def setup_method(self):
        self.proc = _make_processor()

    def test_id_from_eval_row(self):
        result = self.proc._resolve_output_item_id({"id": "row-id-123"}, None, "key", 0)
        assert result == "row-id-123"

    def test_output_item_id_from_eval_row(self):
        result = self.proc._resolve_output_item_id({"output_item_id": "oi-456"}, None, "key", 0)
        assert result == "oi-456"

    def test_datasource_item_id_fallback(self):
        result = self.proc._resolve_output_item_id({}, "ds-789", "key", 0)
        assert result == "ds-789"

    def test_uuid_fallback(self):
        result = self.proc._resolve_output_item_id(None, None, "key", 0)
        # Should be a valid UUID string
        import uuid

        uuid.UUID(result)  # Will raise if invalid

    def test_none_eval_row_with_datasource_id(self):
        result = self.proc._resolve_output_item_id(None, "ds-id", "key", 0)
        assert result == "ds-id"

    def test_priority_order(self):
        """'id' takes priority over 'output_item_id' and 'datasource_item_id'."""
        eval_row = {"id": "first", "output_item_id": "second", "datasource_item_id": "third"}
        result = self.proc._resolve_output_item_id(eval_row, "external", "key", 0)
        assert result == "first"


# ---------------------------------------------------------------------------
# Tests for _assign_nested_value
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestAssignNestedValue:
    """Tests for ResultProcessor._assign_nested_value."""

    def test_single_level(self):
        d = {}
        ResultProcessor._assign_nested_value(d, ["key"], "val")
        assert d == {"key": "val"}

    def test_multi_level(self):
        d = {}
        ResultProcessor._assign_nested_value(d, ["a", "b", "c"], 42)
        assert d == {"a": {"b": {"c": 42}}}

    def test_existing_path_preserved(self):
        d = {"a": {"x": 1}}
        ResultProcessor._assign_nested_value(d, ["a", "y"], 2)
        assert d == {"a": {"x": 1, "y": 2}}


# ---------------------------------------------------------------------------
# Tests for _create_default_scorecard
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestCreateDefaultScorecard:
    """Tests for ResultProcessor._create_default_scorecard."""

    def test_empty_conversations(self):
        proc = _make_processor()
        scorecard, params = proc._create_default_scorecard([], [], [])
        assert scorecard["risk_category_summary"][0]["overall_asr"] == 0.0
        assert scorecard["risk_category_summary"][0]["overall_total"] == 0
        assert scorecard["attack_technique_summary"][0]["overall_asr"] == 0.0
        assert scorecard["joint_risk_attack_summary"] == []

    def test_with_conversations(self):
        proc = _make_processor()
        conversations = [{"attack_technique": "a"}, {"attack_technique": "b"}]
        scorecard, params = proc._create_default_scorecard(conversations, ["baseline", "easy"], ["conv1", "conv2"])
        assert scorecard["risk_category_summary"][0]["overall_total"] == 2

    def test_parameters_include_risk_categories(self):
        proc = _make_processor(risk_categories=[RiskCategory.Violence, RiskCategory.Sexual])
        _, params = proc._create_default_scorecard([], [], [])
        risk_cats = params["attack_objective_generated_from"]["risk_categories"]
        assert "violence" in risk_cats
        assert "sexual" in risk_cats

    def test_default_complexity_when_empty(self):
        proc = _make_processor()
        _, params = proc._create_default_scorecard([], [], [])
        assert "baseline" in params["attack_complexity"]
        assert "easy" in params["attack_complexity"]

    def test_techniques_populated_by_complexity(self):
        proc = _make_processor()
        _, params = proc._create_default_scorecard(
            [{}],
            ["easy", "easy", "baseline"],
            ["conv_a", "conv_b", "conv_c"],
        )
        assert "easy" in params["techniques_used"]


# ---------------------------------------------------------------------------
# Tests for _build_data_source_section
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestBuildDataSourceSection:
    """Tests for ResultProcessor._build_data_source_section."""

    def test_no_red_team_info(self):
        result = ResultProcessor._build_data_source_section({}, None)
        assert result["type"] == "azure_ai_red_team"
        assert "target" in result

    def test_with_attack_strategies(self):
        red_team_info = {"Baseline": {}, "Base64": {}}
        result = ResultProcessor._build_data_source_section({}, red_team_info)
        params = result["item_generation_params"]
        assert params["attack_strategies"] == ["Base64", "Baseline"]

    def test_with_max_turns(self):
        result = ResultProcessor._build_data_source_section({"max_turns": 3}, None)
        assert result["item_generation_params"]["num_turns"] == 3

    def test_invalid_max_turns_ignored(self):
        result = ResultProcessor._build_data_source_section({"max_turns": -1}, None)
        assert "num_turns" not in result.get("item_generation_params", {})

    def test_non_int_max_turns_ignored(self):
        result = ResultProcessor._build_data_source_section({"max_turns": "three"}, None)
        assert "num_turns" not in result.get("item_generation_params", {})

    def test_non_dict_parameters(self):
        result = ResultProcessor._build_data_source_section(None, {"Baseline": {}})
        assert result["type"] == "azure_ai_red_team"


# ---------------------------------------------------------------------------
# Tests for _determine_run_status
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestDetermineRunStatus:
    """Tests for ResultProcessor._determine_run_status."""

    def setup_method(self):
        self.proc = _make_processor()

    def test_completed_when_no_failures(self):
        red_team_info = {"Baseline": {"violence": {"status": "completed"}}}
        assert self.proc._determine_run_status({}, red_team_info, []) == "completed"

    def test_failed_on_incomplete(self):
        red_team_info = {"Baseline": {"violence": {"status": "incomplete"}}}
        assert self.proc._determine_run_status({}, red_team_info, []) == "failed"

    def test_failed_on_timeout(self):
        red_team_info = {"Baseline": {"violence": {"status": "timeout"}}}
        assert self.proc._determine_run_status({}, red_team_info, []) == "failed"

    def test_failed_on_pending(self):
        red_team_info = {"Baseline": {"violence": {"status": "pending"}}}
        assert self.proc._determine_run_status({}, red_team_info, []) == "failed"

    def test_failed_on_running(self):
        red_team_info = {"Baseline": {"violence": {"status": "running"}}}
        assert self.proc._determine_run_status({}, red_team_info, []) == "failed"

    def test_none_red_team_info(self):
        assert self.proc._determine_run_status({}, None, []) == "completed"

    def test_non_dict_values_skipped(self):
        red_team_info = {"Baseline": "not_a_dict"}
        assert self.proc._determine_run_status({}, red_team_info, []) == "completed"

    def test_mixed_statuses_first_failure_wins(self):
        red_team_info = {
            "Baseline": {
                "violence": {"status": "completed"},
                "sexual": {"status": "failed"},
            }
        }
        assert self.proc._determine_run_status({}, red_team_info, []) == "failed"


# ---------------------------------------------------------------------------
# Tests for _format_thresholds_for_output
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestFormatThresholdsForOutput:
    """Tests for ResultProcessor._format_thresholds_for_output."""

    def test_no_custom_thresholds(self):
        proc = _make_processor(risk_categories=[RiskCategory.Violence])
        result = proc._format_thresholds_for_output()
        assert "violence" in result

    def test_custom_thresholds_included(self):
        proc = _make_processor(
            risk_categories=[RiskCategory.Violence],
            thresholds={"violence": 5},
        )
        result = proc._format_thresholds_for_output()
        assert result["violence"] == 5

    def test_internal_keys_skipped(self):
        proc = _make_processor(thresholds={"_internal": 1, "violence": 3})
        result = proc._format_thresholds_for_output()
        assert "_internal" not in result

    def test_enum_keys_converted(self):
        proc = _make_processor(
            risk_categories=[RiskCategory.Violence],
            thresholds={RiskCategory.Violence: 4},
        )
        result = proc._format_thresholds_for_output()
        assert "violence" in result
        assert result["violence"] == 4


# ---------------------------------------------------------------------------
# Tests for _should_redact_for_risk_category
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestShouldRedactForRiskCategory:
    """Tests for ResultProcessor._should_redact_for_risk_category."""

    def setup_method(self):
        self.proc = _make_processor()

    def test_sensitive_data_leakage_redacted(self):
        assert self.proc._should_redact_for_risk_category("sensitive_data_leakage") is True

    def test_task_adherence_redacted(self):
        assert self.proc._should_redact_for_risk_category("task_adherence") is True

    def test_prohibited_actions_redacted(self):
        assert self.proc._should_redact_for_risk_category("prohibited_actions") is True

    def test_violence_not_redacted(self):
        assert self.proc._should_redact_for_risk_category("violence") is False

    def test_empty_string_not_redacted(self):
        assert self.proc._should_redact_for_risk_category("") is False


# ---------------------------------------------------------------------------
# Tests for _get_redacted_input_message
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestGetRedactedInputMessage:
    """Tests for ResultProcessor._get_redacted_input_message."""

    def setup_method(self):
        self.proc = _make_processor()

    def test_basic_redaction(self):
        msg = self.proc._get_redacted_input_message("violence", "baseline")
        assert "Violence" in msg
        assert "Baseline" in msg
        assert "Redacted" in msg

    def test_with_risk_sub_type(self):
        msg = self.proc._get_redacted_input_message("violence", "baseline", "physical_harm")
        assert "Physical Harm" in msg
        assert "Violence" in msg

    def test_without_risk_sub_type(self):
        msg = self.proc._get_redacted_input_message("task_adherence", "Base64")
        assert "Task Adherence" in msg
        assert "Base64" in msg
        assert "sub" not in msg.lower()

    def test_snake_case_conversion(self):
        msg = self.proc._get_redacted_input_message("sensitive_data_leakage", "easy_attack")
        assert "Sensitive Data Leakage" in msg
        assert "Easy Attack" in msg


# ---------------------------------------------------------------------------
# Tests for get_app_insights_redacted_results
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestGetAppInsightsRedactedResults:
    """Tests for ResultProcessor.get_app_insights_redacted_results."""

    def setup_method(self):
        self.proc = _make_processor()

    def test_empty_results(self):
        assert self.proc.get_app_insights_redacted_results([]) == []

    def test_non_sensitive_category_not_redacted(self):
        results = [
            {
                "results": [{"name": "violence", "properties": {"attack_technique": "baseline"}}],
                "sample": {"input": [{"role": "user", "content": "original"}]},
            }
        ]
        redacted = self.proc.get_app_insights_redacted_results(results)
        assert redacted[0]["sample"]["input"][0]["content"] == "original"

    def test_sensitive_category_redacted(self):
        results = [
            {
                "results": [{"name": "sensitive_data_leakage", "properties": {"attack_technique": "baseline"}}],
                "sample": {"input": [{"role": "user", "content": "secret prompt"}]},
            }
        ]
        redacted = self.proc.get_app_insights_redacted_results(results)
        assert "Redacted" in redacted[0]["sample"]["input"][0]["content"]
        assert "secret prompt" not in redacted[0]["sample"]["input"][0]["content"]

    def test_original_not_modified(self):
        """Deep copy ensures original is untouched."""
        results = [
            {
                "results": [{"name": "task_adherence", "properties": {"attack_technique": "baseline"}}],
                "sample": {"input": [{"role": "user", "content": "original"}]},
            }
        ]
        self.proc.get_app_insights_redacted_results(results)
        assert results[0]["sample"]["input"][0]["content"] == "original"

    def test_missing_results_key_skipped(self):
        results = [{"sample": {"input": []}}]
        redacted = self.proc.get_app_insights_redacted_results(results)
        assert redacted == results

    def test_non_list_results_skipped(self):
        results = [{"results": "not_a_list"}]
        redacted = self.proc.get_app_insights_redacted_results(results)
        assert redacted == results

    def test_assistant_messages_not_redacted(self):
        results = [
            {
                "results": [{"name": "sensitive_data_leakage", "properties": {"attack_technique": "baseline"}}],
                "sample": {
                    "input": [
                        {"role": "user", "content": "secret"},
                        {"role": "assistant", "content": "response"},
                    ]
                },
            }
        ]
        redacted = self.proc.get_app_insights_redacted_results(results)
        # User message redacted
        assert "Redacted" in redacted[0]["sample"]["input"][0]["content"]
        # Assistant message unchanged
        assert redacted[0]["sample"]["input"][1]["content"] == "response"


# ---------------------------------------------------------------------------
# Tests for _build_output_item status logic
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestBuildOutputItemStatus:
    """Tests for _build_output_item status determination."""

    def setup_method(self):
        self.proc = _make_processor()

    def _make_conversation(self, **overrides):
        base = {
            "attack_success": True,
            "attack_technique": "baseline",
            "attack_complexity": "baseline",
            "risk_category": "violence",
            "conversation": [{"role": "user", "content": "hi"}],
            "risk_assessment": None,
            "attack_success_threshold": 3,
        }
        base.update(overrides)
        return base

    def test_completed_status_normal(self):
        conv = self._make_conversation()
        raw = {"conversation": {"messages": [{"role": "user", "content": "hi"}]}}
        item = self.proc._build_output_item(conv, None, raw, "key1", 0)
        assert item["status"] == "completed"

    def test_failed_status_on_conversation_error(self):
        conv = self._make_conversation(error={"message": "eval failed"})
        raw = {"conversation": {"messages": [{"role": "user", "content": "hi"}]}}
        item = self.proc._build_output_item(conv, None, raw, "key1", 0)
        assert item["status"] == "failed"

    def test_failed_status_on_exception(self):
        conv = self._make_conversation(exception="RuntimeError: boom")
        raw = {"conversation": {"messages": [{"role": "user", "content": "hi"}]}}
        item = self.proc._build_output_item(conv, None, raw, "key1", 0)
        assert item["status"] == "failed"

    def test_output_item_structure(self):
        conv = self._make_conversation()
        raw = {"conversation": {"messages": [{"role": "user", "content": "hi"}]}}
        item = self.proc._build_output_item(conv, None, raw, "key1", 0)
        assert item["object"] == "eval.run.output_item"
        assert "id" in item
        assert "created_time" in item
        assert "sample" in item
        assert "results" in item


# ---------------------------------------------------------------------------
# Tests for _build_sample_payload
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestBuildSamplePayload:
    """Tests for _build_sample_payload edge cases."""

    def setup_method(self):
        self.proc = _make_processor()

    def test_basic_input_output_split(self):
        conv = {"conversation": [{"role": "user", "content": "q"}]}
        raw = {
            "conversation": {
                "messages": [
                    {"role": "user", "content": "q"},
                    {"role": "assistant", "content": "a"},
                ]
            }
        }
        sample = self.proc._build_sample_payload(conv, raw)
        assert sample["object"] == "eval.run.output_item.sample"
        assert len(sample["output"]) == 1
        assert sample["output"][0]["role"] == "assistant"

    def test_no_assistant_message(self):
        conv = {"conversation": [{"role": "user", "content": "q"}]}
        raw = {"conversation": {"messages": [{"role": "user", "content": "q"}]}}
        sample = self.proc._build_sample_payload(conv, raw)
        assert sample["output"] == []
        assert len(sample["input"]) == 1

    def test_metadata_excludes_internal_keys(self):
        conv = {"conversation": []}
        raw = {
            "conversation": {"messages": []},
            "custom_field": "value",
            "attack_success": True,
            "score": {"x": 1},
            "_eval_run_output_item": {},
        }
        sample = self.proc._build_sample_payload(conv, raw)
        meta = sample.get("metadata", {})
        assert "custom_field" in meta
        assert "attack_success" not in meta
        assert "score" not in meta
        assert "_eval_run_output_item" not in meta
        assert "conversation" not in meta

    def test_error_info_added_to_sample(self):
        conv = {"conversation": [], "error": "something broke"}
        raw = {"conversation": {"messages": []}}
        sample = self.proc._build_sample_payload(conv, raw)
        assert "error" in sample
        assert sample["error"]["message"] == "something broke"

    def test_exception_info_added(self):
        conv = {"conversation": [], "exception": "RuntimeError: x"}
        raw = {"conversation": {"messages": []}}
        sample = self.proc._build_sample_payload(conv, raw)
        assert sample["error"]["exception"] == "RuntimeError: x"

    def test_dict_error_preserved(self):
        conv = {"conversation": [], "error": {"message": "err", "code": 500}}
        raw = {"conversation": {"messages": []}}
        sample = self.proc._build_sample_payload(conv, raw)
        assert sample["error"]["message"] == "err"
        assert sample["error"]["code"] == 500

    def test_token_usage_extracted(self):
        conv = {"conversation": []}
        raw = {
            "conversation": {
                "messages": [
                    {
                        "role": "assistant",
                        "content": "hi",
                        "token_usage": {
                            "model_name": "gpt-4",
                            "prompt_tokens": 10,
                            "completion_tokens": 5,
                            "total_tokens": 15,
                        },
                    }
                ]
            }
        }
        sample = self.proc._build_sample_payload(conv, raw)
        assert sample["usage"]["model_name"] == "gpt-4"
        assert sample["usage"]["prompt_tokens"] == 10

    def test_non_dict_messages_skipped_in_normalization(self):
        conv = {"conversation": []}
        raw = {"conversation": {"messages": ["not_a_dict", {"role": "user", "content": "ok"}]}}
        sample = self.proc._build_sample_payload(conv, raw)
        assert len(sample["input"]) == 1


# ---------------------------------------------------------------------------
# Tests for _build_output_result
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestBuildOutputResult:
    """Tests for _build_output_result edge cases."""

    def setup_method(self):
        self.proc = _make_processor(risk_categories=[RiskCategory.Violence])

    def test_fallback_result_when_no_eval_row(self):
        """When eval_row is None and risk_category matches, a fallback result is created."""
        conv = {
            "risk_category": "violence",
            "attack_technique": "baseline",
            "attack_complexity": "baseline",
            "attack_success": True,
            "attack_success_threshold": 3,
        }
        results = self.proc._build_output_result(conv, None)
        assert len(results) >= 1
        violence_result = next(r for r in results if r["name"] == "violence")
        # attack_success=True → passed should be False (inverted)
        assert violence_result["passed"] is False

    def test_eval_row_pass_result(self):
        conv = {
            "risk_category": "violence",
            "attack_technique": "baseline",
            "attack_complexity": "baseline",
            "attack_success": None,
            "attack_success_threshold": 3,
        }
        eval_row = {"outputs.violence.violence_result": "pass"}
        results = self.proc._build_output_result(conv, eval_row)
        violence_result = next(r for r in results if r["name"] == "violence")
        assert violence_result["passed"] is True
        assert violence_result["label"] == "pass"

    def test_eval_row_fail_result(self):
        conv = {
            "risk_category": "violence",
            "attack_technique": "baseline",
            "attack_complexity": "baseline",
            "attack_success": None,
            "attack_success_threshold": 3,
        }
        eval_row = {"outputs.violence.violence_result": "fail"}
        results = self.proc._build_output_result(conv, eval_row)
        violence_result = next(r for r in results if r["name"] == "violence")
        assert violence_result["passed"] is False
        assert violence_result["label"] == "fail"

    def test_properties_include_attack_details(self):
        conv = {
            "risk_category": "violence",
            "attack_technique": "Base64",
            "attack_complexity": "easy",
            "attack_success": True,
            "attack_success_threshold": 3,
            "risk_sub_type": "physical",
        }
        results = self.proc._build_output_result(conv, None)
        props = results[0].get("properties", {})
        assert props["attack_technique"] == "Base64"
        assert props["attack_complexity"] == "easy"
        assert props["attack_success"] is True
        assert props["risk_sub_type"] == "physical"

    def test_unmatched_risk_category_skipped(self):
        """A risk category not matching the conversation's category with no eval data is skipped."""
        proc = _make_processor(risk_categories=[RiskCategory.Sexual])
        conv = {
            "risk_category": "violence",
            "attack_technique": "baseline",
            "attack_complexity": "baseline",
            "attack_success": None,
            "attack_success_threshold": 3,
        }
        results = proc._build_output_result(conv, None)
        # Should produce fallback result for violence (the conv's risk_category)
        assert len(results) == 1
        assert results[0]["name"] == "violence"

    def test_result_type_eval_vs_redteam(self):
        """Type is 'azure_ai_evaluator' when eval_row is a dict, otherwise 'azure_ai_red_team'."""
        conv = {
            "risk_category": "violence",
            "attack_technique": "baseline",
            "attack_complexity": "baseline",
            "attack_success": True,
            "attack_success_threshold": 3,
        }
        # With eval_row
        results_with = self.proc._build_output_result(conv, {"outputs.violence.violence_result": "pass"})
        assert results_with[0]["type"] == "azure_ai_evaluator"
        # Without eval_row
        results_without = self.proc._build_output_result(conv, None)
        assert results_without[0]["type"] == "azure_ai_red_team"

    def test_scorer_token_usage_fallback(self):
        """When eval_row lacks metrics, scorer_token_usage from conversation is used."""
        conv = {
            "risk_category": "violence",
            "attack_technique": "baseline",
            "attack_complexity": "baseline",
            "attack_success": True,
            "attack_success_threshold": 3,
            "scorer_token_usage": {"promptTokens": 50, "completionTokens": 25},
        }
        results = self.proc._build_output_result(conv, None)
        props = results[0].get("properties", {})
        assert props["metrics"]["promptTokens"] == 50

    def test_risk_assessment_severity_label(self):
        conv = {
            "risk_category": "violence",
            "attack_technique": "baseline",
            "attack_complexity": "baseline",
            "attack_success": None,
            "attack_success_threshold": 3,
            "risk_assessment": {"violence": {"severity_label": "High", "reason": "dangerous content"}},
        }
        results = self.proc._build_output_result(conv, None)
        assert results[0]["reason"] == "dangerous content"
