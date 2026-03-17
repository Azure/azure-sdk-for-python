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
