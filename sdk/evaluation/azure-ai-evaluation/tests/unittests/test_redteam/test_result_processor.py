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


class TestAggregateRunErrors:
    """Tests for ResultProcessor._aggregate_run_errors."""

    def test_non_dict_returns_none(self):
        """Non-dict red_team_info should return None."""
        assert ResultProcessor._aggregate_run_errors(None) is None
        assert ResultProcessor._aggregate_run_errors("not a dict") is None
        assert ResultProcessor._aggregate_run_errors([]) is None

    def test_no_failed_tasks_returns_none(self):
        """All tasks completed → no error to report."""
        red_team_info = {
            "Foundry": {
                "violence": {"status": "completed", "asr": 0.5},
                "sexual": {"status": "completed", "asr": 0.3},
            }
        }
        assert ResultProcessor._aggregate_run_errors(red_team_info) is None

    def test_failed_tasks_without_error_field_returns_none(self):
        """Failed tasks with no error messages should return None."""
        red_team_info = {
            "Foundry": {
                "violence": {"status": "failed", "asr": 0.0},
                "sexual": {"status": "failed", "asr": 0.0},
            }
        }
        assert ResultProcessor._aggregate_run_errors(red_team_info) is None

    def test_single_failed_task_with_error(self):
        """Single failure produces an error dict with the error message."""
        red_team_info = {
            "Foundry": {
                "violence": {
                    "status": "failed",
                    "error": "Model deployment unavailable",
                    "asr": 0.0,
                },
                "sexual": {"status": "completed", "asr": 0.3},
            }
        }
        result = ResultProcessor._aggregate_run_errors(red_team_info)
        assert result is not None
        assert result["code"] == "scan_failed"
        assert result["message"] == "Model deployment unavailable"

    def test_same_error_across_categories_is_deduplicated(self):
        """Identical errors across categories should collapse into one."""
        shared_error = "Model deployment 'gpt-4' is unavailable"
        red_team_info = {
            "Foundry": {
                "violence": {"status": "failed", "error": shared_error, "asr": 0.0},
                "sexual": {"status": "failed", "error": shared_error, "asr": 0.0},
                "self_harm": {"status": "failed", "error": shared_error, "asr": 0.0},
            }
        }
        result = ResultProcessor._aggregate_run_errors(red_team_info)
        assert result is not None
        assert result["code"] == "scan_failed"
        # Single unique error → message should be just that error
        assert result["message"] == shared_error

    def test_different_errors_produce_summary(self):
        """Different errors across categories should produce a summary."""
        red_team_info = {
            "Foundry": {
                "violence": {
                    "status": "failed",
                    "error": "Model unavailable",
                    "asr": 0.0,
                },
                "sexual": {
                    "status": "failed",
                    "error": "Rate limit exceeded",
                    "asr": 0.0,
                },
            }
        }
        result = ResultProcessor._aggregate_run_errors(red_team_info)
        assert result is not None
        assert result["code"] == "scan_failed"
        assert "2 distinct errors" in result["message"]
        assert "Model unavailable" in result["message"]

    def test_mixed_statuses_only_collects_from_failures(self):
        """Only failed/incomplete/timeout/pending/running produce errors."""
        red_team_info = {
            "Foundry": {
                "violence": {
                    "status": "completed",
                    "error": "should be ignored",
                    "asr": 0.5,
                },
                "sexual": {"status": "failed", "error": "actual error", "asr": 0.0},
            }
        }
        result = ResultProcessor._aggregate_run_errors(red_team_info)
        assert result is not None
        assert result["message"] == "actual error"
        assert "should be ignored" not in result["message"]


class TestDetermineRunStatusAndAggregateErrorsIntegration:
    """Integration tests verifying _determine_run_status and _aggregate_run_errors
    interact correctly in _build_results_payload."""

    @staticmethod
    def _make_processor():
        """Create a minimal ResultProcessor for testing."""
        import logging

        return ResultProcessor(
            logger=logging.getLogger("test"),
            attack_success_thresholds={},
            application_scenario="test",
            risk_categories=[],
        )

    def test_completed_status_produces_no_error(self):
        """When all tasks are completed, error must be None in the payload."""
        from azure.ai.evaluation.red_team._red_team_result import RedTeamResult

        processor = self._make_processor()
        red_team_info = {
            "Baseline": {
                "violence": {"status": "completed", "asr": 0.5},
                "sexual": {"status": "completed", "asr": 0.3},
            }
        }
        result = RedTeamResult(scan_result={"scorecard": {}, "parameters": {}})
        payload = processor._build_results_payload(
            redteam_result=result,
            output_items=[],
            red_team_info=red_team_info,
            run_id_override="test-run",
            eval_id_override="test-eval",
            created_at_override=1000000,
        )
        assert payload["status"] == "completed"
        assert payload["error"] is None

    def test_failed_status_produces_error(self):
        """When a task fails, status should be 'failed' and error should be populated."""
        from azure.ai.evaluation.red_team._red_team_result import RedTeamResult

        processor = self._make_processor()
        red_team_info = {
            "Baseline": {
                "violence": {
                    "status": "failed",
                    "error": "Model unavailable",
                    "asr": 0.0,
                },
                "sexual": {"status": "completed", "asr": 0.3},
            }
        }
        result = RedTeamResult(scan_result={"scorecard": {}, "parameters": {}})
        payload = processor._build_results_payload(
            redteam_result=result,
            output_items=[],
            red_team_info=red_team_info,
            run_id_override="test-run",
            eval_id_override="test-eval",
            created_at_override=1000000,
        )
        assert payload["status"] == "failed"
        assert payload["error"] is not None
        assert payload["error"]["code"] == "scan_failed"
        assert "Model unavailable" in payload["error"]["message"]

    def test_partial_failure_with_completed_results_is_failed(self):
        """Mixed completed and failed tasks should result in 'failed' status."""
        from azure.ai.evaluation.red_team._red_team_result import RedTeamResult
        from azure.ai.evaluation.red_team._foundry._execution_manager import (
            _ERROR_TRACKING_KEY,
        )

        processor = self._make_processor()
        red_team_info = {
            "Baseline": {
                "violence": {"status": "completed", "asr": 0.5},
            },
            _ERROR_TRACKING_KEY: {
                "sexual": {
                    "status": "failed",
                    "error": "Auth failure",
                    "asr": 0.0,
                },
            },
        }
        result = RedTeamResult(scan_result={"scorecard": {}, "parameters": {}})
        payload = processor._build_results_payload(
            redteam_result=result,
            output_items=[],
            red_team_info=red_team_info,
            run_id_override="test-run",
            eval_id_override="test-eval",
            created_at_override=1000000,
        )
        assert payload["status"] == "failed"
        assert payload["error"] is not None
        # _ERROR_TRACKING_KEY should not appear in data_source attack_strategies
        strategies = payload.get("data_source", {}).get("item_generation_params", {}).get("attack_strategies", [])
        assert _ERROR_TRACKING_KEY not in strategies
