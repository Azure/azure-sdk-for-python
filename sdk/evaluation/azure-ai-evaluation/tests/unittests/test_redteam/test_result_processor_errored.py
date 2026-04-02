# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for ResultProcessor._compute_result_count, _determine_run_status, and _extract_expected_total."""

import pytest
from azure.ai.evaluation.red_team._result_processor import ResultProcessor


@pytest.mark.unittest
class TestComputeResultCount:
    """Tests for ResultProcessor._compute_result_count — errored tracking."""

    def test_empty_output_items(self):
        """Empty input returns all-zero counts."""
        result = ResultProcessor._compute_result_count([])
        assert result == {"total": 0, "passed": 0, "failed": 0, "errored": 0}

    def test_all_passed(self):
        """All items with passed=True count as passed."""
        items = [
            {"sample": {}, "results": [{"passed": True, "name": "violence"}]},
            {"sample": {}, "results": [{"passed": True, "name": "self_harm"}]},
        ]
        result = ResultProcessor._compute_result_count(items)
        assert result == {"total": 2, "passed": 2, "failed": 0, "errored": 0}

    def test_all_failed(self):
        """All items with passed=False count as failed."""
        items = [
            {"sample": {}, "results": [{"passed": False, "name": "violence"}]},
            {"sample": {}, "results": [{"passed": False, "name": "self_harm"}]},
        ]
        result = ResultProcessor._compute_result_count(items)
        assert result == {"total": 2, "passed": 0, "failed": 2, "errored": 0}

    def test_mixed_results(self):
        """Mix of passed and failed items."""
        items = [
            {"sample": {}, "results": [{"passed": True, "name": "violence"}]},
            {"sample": {}, "results": [{"passed": False, "name": "self_harm"}]},
            {"sample": {}, "results": [{"passed": True, "name": "sexual"}]},
        ]
        result = ResultProcessor._compute_result_count(items)
        assert result == {"total": 3, "passed": 2, "failed": 1, "errored": 0}

    def test_sample_error_counts_as_errored(self):
        """Items with error in sample count as errored."""
        items = [
            {"sample": {"error": {"message": "Some error"}}, "results": [{"passed": True}]},
            {"sample": {}, "results": [{"passed": True, "name": "violence"}]},
        ]
        result = ResultProcessor._compute_result_count(items)
        assert result == {"total": 2, "passed": 1, "failed": 0, "errored": 1}

    def test_missing_results_counts_as_errored(self):
        """Items with no results array count as errored."""
        items = [
            {"sample": {}, "results": []},
            {"sample": {}, "results": [{"passed": True, "name": "violence"}]},
        ]
        result = ResultProcessor._compute_result_count(items)
        assert result == {"total": 2, "passed": 1, "failed": 0, "errored": 1}

    def test_null_passed_counts_as_errored(self):
        """Items where all results have passed=None count as errored."""
        items = [
            {"sample": {}, "results": [{"passed": None, "name": "violence"}]},
            {"sample": {}, "results": [{"passed": True, "name": "self_harm"}]},
        ]
        result = ResultProcessor._compute_result_count(items)
        assert result == {"total": 2, "passed": 1, "failed": 0, "errored": 1}

    def test_expected_total_none_no_effect(self):
        """When expected_total is None, behaviour is unchanged."""
        items = [
            {"sample": {}, "results": [{"passed": True, "name": "violence"}]},
        ]
        result = ResultProcessor._compute_result_count(items, expected_total=None)
        assert result == {"total": 1, "passed": 1, "failed": 0, "errored": 0}

    def test_expected_total_equals_actual_no_extra_errored(self):
        """When expected_total equals actual item count, no extra errored added."""
        items = [
            {"sample": {}, "results": [{"passed": True, "name": "v"}]},
            {"sample": {}, "results": [{"passed": False, "name": "s"}]},
        ]
        result = ResultProcessor._compute_result_count(items, expected_total=2)
        assert result == {"total": 2, "passed": 1, "failed": 1, "errored": 0}

    def test_expected_total_greater_than_actual_adds_errored(self):
        """Missing objectives (expected > actual) are counted as errored."""
        items = [
            {"sample": {}, "results": [{"passed": True, "name": "violence"}]},
        ]
        result = ResultProcessor._compute_result_count(items, expected_total=5)
        assert result["total"] == 5
        assert result["passed"] == 1
        assert result["failed"] == 0
        assert result["errored"] == 4  # 5 expected - 1 actual = 4 missing

    def test_expected_total_with_existing_errors(self):
        """Missing objectives add to already-errored items."""
        items = [
            {"sample": {}, "results": [{"passed": True, "name": "v"}]},
            {"sample": {"error": {"message": "eval failed"}}, "results": []},
        ]
        # 2 actual items: 1 passed, 1 errored from sample error
        # expected_total=5 means 3 more missing → errored = 1 + 3 = 4
        result = ResultProcessor._compute_result_count(items, expected_total=5)
        assert result["total"] == 5
        assert result["passed"] == 1
        assert result["failed"] == 0
        assert result["errored"] == 4

    def test_expected_total_less_than_actual_no_negative_errored(self):
        """If expected_total < actual (shouldn't happen), don't add negative errored."""
        items = [
            {"sample": {}, "results": [{"passed": True, "name": "v"}]},
            {"sample": {}, "results": [{"passed": True, "name": "s"}]},
        ]
        result = ResultProcessor._compute_result_count(items, expected_total=1)
        assert result["total"] == 2  # actual count used when expected < actual
        assert result["errored"] == 0

    def test_entirely_missing_scenario(self):
        """When zero output items exist but expected_total > 0, all are errored."""
        result = ResultProcessor._compute_result_count([], expected_total=32)
        assert result == {"total": 32, "passed": 0, "failed": 0, "errored": 32}


@pytest.mark.unittest
class TestExtractExpectedTotal:
    """Tests for ResultProcessor._extract_expected_total."""

    def test_none_red_team_info(self):
        """None input returns None."""
        assert ResultProcessor._extract_expected_total(None) is None

    def test_empty_red_team_info(self):
        """Empty dict returns None."""
        assert ResultProcessor._extract_expected_total({}) is None

    def test_no_expected_count_fields(self):
        """red_team_info without expected_count returns None."""
        info = {
            "baseline": {
                "violence": {"data_file": "v.jsonl", "status": "completed"},
            }
        }
        assert ResultProcessor._extract_expected_total(info) is None

    def test_single_strategy_single_risk(self):
        """Simple case: one strategy, one risk category."""
        info = {
            "baseline": {
                "violence": {"status": "completed", "expected_count": 32},
            }
        }
        assert ResultProcessor._extract_expected_total(info) == 32

    def test_single_strategy_multiple_risks(self):
        """Multiple risk categories sum their expected counts."""
        info = {
            "baseline": {
                "violence": {"status": "completed", "expected_count": 32},
                "self_harm": {"status": "completed", "expected_count": 32},
                "task_adherence": {"status": "failed", "expected_count": 1},
            }
        }
        assert ResultProcessor._extract_expected_total(info) == 65  # 32+32+1

    def test_duplicate_risk_across_strategies_deduplicates(self):
        """Same risk category under multiple strategies is counted once (max)."""
        info = {
            "baseline": {
                "violence": {"status": "completed", "expected_count": 32},
            },
            "crescendo": {
                "violence": {"status": "completed", "expected_count": 32},
            },
        }
        # violence appears in both strategies but should only count once
        assert ResultProcessor._extract_expected_total(info) == 32

    def test_different_counts_across_strategies_takes_max(self):
        """If counts differ across strategies (unlikely), take the max."""
        info = {
            "baseline": {
                "violence": {"status": "completed", "expected_count": 10},
            },
            "crescendo": {
                "violence": {"status": "completed", "expected_count": 32},
            },
        }
        assert ResultProcessor._extract_expected_total(info) == 32

    def test_zero_objective_category_included(self):
        """Categories with expected_count=0 (failed to prepare) are included."""
        info = {
            "baseline": {
                "violence": {"status": "completed", "expected_count": 32},
                "sensitive_data_leakage": {"status": "failed", "expected_count": 0},
            }
        }
        assert ResultProcessor._extract_expected_total(info) == 32  # 32 + 0

    def test_non_dict_values_skipped(self):
        """Non-dict entries in red_team_info are gracefully skipped."""
        info = {
            "baseline": {
                "violence": {"status": "completed", "expected_count": 32},
            },
            "_metadata": "not a dict",
        }
        assert ResultProcessor._extract_expected_total(info) == 32

    def test_invalid_expected_count_value_skipped(self):
        """Non-numeric expected_count values are gracefully skipped."""
        info = {
            "baseline": {
                "violence": {"status": "completed", "expected_count": 32},
                "self_harm": {"status": "completed", "expected_count": "invalid"},
            }
        }
        assert ResultProcessor._extract_expected_total(info) == 32


@pytest.mark.unittest
class TestDetermineRunStatus:
    """Tests for ResultProcessor._determine_run_status."""

    def _make_processor(self):
        return ResultProcessor.__new__(ResultProcessor)

    def test_completed_when_all_ok(self):
        """Run is completed when all categories succeeded."""
        proc = self._make_processor()
        info = {
            "baseline": {
                "violence": {"status": "completed"},
                "self_harm": {"status": "completed"},
            }
        }
        assert proc._determine_run_status({}, info, []) == "completed"

    def test_failed_when_category_failed(self):
        """Run is failed when any category has status 'failed'."""
        proc = self._make_processor()
        info = {
            "baseline": {
                "violence": {"status": "completed"},
                "task_adherence": {"status": "failed"},
            }
        }
        assert proc._determine_run_status({}, info, []) == "failed"

    def test_failed_when_category_incomplete(self):
        """Run is failed when any category has status 'incomplete'."""
        proc = self._make_processor()
        info = {
            "baseline": {
                "violence": {"status": "incomplete"},
            }
        }
        assert proc._determine_run_status({}, info, []) == "failed"

    def test_failed_when_category_pending(self):
        """Run is failed when any category is still pending (was never executed)."""
        proc = self._make_processor()
        info = {
            "baseline": {
                "violence": {"status": "pending"},
            }
        }
        assert proc._determine_run_status({}, info, []) == "failed"

    def test_failed_when_category_partial_failure(self):
        """Run is failed when any category has status 'partial_failure'."""
        proc = self._make_processor()
        info = {
            "baseline": {
                "violence": {"status": "completed"},
                "self_harm": {"status": "partial_failure"},
            }
        }
        assert proc._determine_run_status({}, info, []) == "failed"

    def test_failed_when_category_timeout(self):
        """Run is failed when any category has status 'timeout'."""
        proc = self._make_processor()
        info = {
            "baseline": {
                "violence": {"status": "timeout"},
            }
        }
        assert proc._determine_run_status({}, info, []) == "failed"

    def test_completed_when_no_red_team_info(self):
        """Run is completed when red_team_info is None."""
        proc = self._make_processor()
        assert proc._determine_run_status({}, None, []) == "completed"

    def test_non_dict_entries_skipped(self):
        """Non-dict entries in red_team_info are ignored."""
        proc = self._make_processor()
        info = {
            "baseline": {
                "violence": {"status": "completed"},
            },
            "_metadata": "some string",
        }
        assert proc._determine_run_status({}, info, []) == "completed"

    def test_zero_objective_category_recorded_as_failed_triggers_failure(self):
        """A risk category with 0 objectives that was recorded as failed makes the run fail."""
        proc = self._make_processor()
        info = {
            "baseline": {
                "violence": {"status": "completed", "expected_count": 32},
                "sensitive_data_leakage": {
                    "status": "failed",
                    "error": "No attack objectives could be prepared for this risk category",
                    "expected_count": 0,
                },
            }
        }
        assert proc._determine_run_status({}, info, []) == "failed"
