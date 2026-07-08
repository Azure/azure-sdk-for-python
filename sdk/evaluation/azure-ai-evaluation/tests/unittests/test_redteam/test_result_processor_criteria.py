import pytest
from azure.ai.evaluation.red_team._result_processor import ResultProcessor


@pytest.mark.unittest
class TestComputePerTestingCriteria:
    """Tests for ResultProcessor._compute_per_testing_criteria."""

    def test_empty_output_items(self):
        """Empty input returns empty list."""
        result = ResultProcessor._compute_per_testing_criteria([])
        assert result == []

    def test_risk_categories_only(self):
        """Results without attack_technique in properties produce only risk category entries."""
        output_items = [
            {
                "results": [
                    {"name": "violence", "passed": True, "properties": {}},
                    {"name": "violence", "passed": False, "properties": {}},
                    {"name": "self_harm", "passed": True, "properties": {}},
                ]
            }
        ]
        result = ResultProcessor._compute_per_testing_criteria(output_items)
        assert len(result) == 2
        # Sorted alphabetically: self_harm before violence
        assert result[0] == {"testing_criteria": "self_harm", "passed": 1, "failed": 0, "skipped": 0, "errored": 0}
        assert result[1] == {"testing_criteria": "violence", "passed": 1, "failed": 1, "skipped": 0, "errored": 0}
        # No attack_strategy field on risk category entries
        for entry in result:
            assert "attack_strategy" not in entry

    def test_attack_strategies_included(self):
        """Results with attack_technique in properties produce both risk category and attack strategy entries."""
        output_items = [
            {
                "results": [
                    {"name": "violence", "passed": True, "properties": {"attack_technique": "baseline"}},
                    {"name": "violence", "passed": False, "properties": {"attack_technique": "Base64"}},
                ]
            }
        ]
        result = ResultProcessor._compute_per_testing_criteria(output_items)
        # Should have: 1 risk category (violence) + 2 strategies (Base64, baseline)
        assert len(result) == 3
        # Risk categories come first
        assert result[0] == {"testing_criteria": "violence", "passed": 1, "failed": 1, "skipped": 0, "errored": 0}
        # Then attack strategies sorted alphabetically
        assert result[1] == {
            "testing_criteria": "Base64",
            "attack_strategy": "Base64",
            "passed": 0,
            "failed": 1,
            "skipped": 0,
            "errored": 0,
        }
        assert result[2] == {
            "testing_criteria": "baseline",
            "attack_strategy": "baseline",
            "passed": 1,
            "failed": 0,
            "skipped": 0,
            "errored": 0,
        }

    def test_multiple_risk_categories_and_strategies(self):
        """Multiple risk categories and strategies are all represented."""
        output_items = [
            {
                "results": [
                    {"name": "violence", "passed": False, "properties": {"attack_technique": "baseline"}},
                ]
            },
            {
                "results": [
                    {"name": "self_harm", "passed": True, "properties": {"attack_technique": "baseline"}},
                ]
            },
            {
                "results": [
                    {"name": "violence", "passed": True, "properties": {"attack_technique": "Base64"}},
                ]
            },
        ]
        result = ResultProcessor._compute_per_testing_criteria(output_items)
        criteria_names = [r["testing_criteria"] for r in result]
        # Risk categories first (sorted), then strategies (sorted)
        assert "self_harm" in criteria_names
        assert "violence" in criteria_names
        assert "Base64" in criteria_names
        assert "baseline" in criteria_names
        # 2 risk categories + 2 strategies = 4 entries
        assert len(result) == 4

        # Verify risk categories come before strategies
        risk_entries = [r for r in result if "attack_strategy" not in r]
        strategy_entries = [r for r in result if "attack_strategy" in r]
        assert len(risk_entries) == 2
        assert len(strategy_entries) == 2
        # Risk entries are first in the list
        assert result.index(risk_entries[-1]) < result.index(strategy_entries[0])

    def test_strategy_aggregation_across_items(self):
        """Same attack strategy across multiple output items aggregates correctly."""
        output_items = [
            {
                "results": [
                    {"name": "violence", "passed": True, "properties": {"attack_technique": "baseline"}},
                ]
            },
            {
                "results": [
                    {"name": "self_harm", "passed": False, "properties": {"attack_technique": "baseline"}},
                ]
            },
        ]
        result = ResultProcessor._compute_per_testing_criteria(output_items)
        strategy_entries = [r for r in result if r.get("attack_strategy") == "baseline"]
        assert len(strategy_entries) == 1
        assert strategy_entries[0]["passed"] == 1  # from violence result
        assert strategy_entries[0]["failed"] == 1  # from self_harm result

    def test_passed_none_classified_as_skipped(self):
        """Results with passed=None (no explicit status) are classified as skipped."""
        output_items = [
            {
                "results": [
                    {"name": "violence", "passed": None, "properties": {"attack_technique": "baseline"}},
                    {"name": "violence", "passed": True, "properties": {"attack_technique": "baseline"}},
                ]
            }
        ]
        result = ResultProcessor._compute_per_testing_criteria(output_items)
        violence_entry = next(r for r in result if r["testing_criteria"] == "violence" and "attack_strategy" not in r)
        assert violence_entry["passed"] == 1
        assert violence_entry["failed"] == 0
        assert violence_entry["skipped"] == 1
        baseline_entry = next(r for r in result if r.get("attack_strategy") == "baseline")
        assert baseline_entry["passed"] == 1
        assert baseline_entry["failed"] == 0
        assert baseline_entry["skipped"] == 1

    def test_missing_name_skipped(self):
        """Results without a name field are skipped."""
        output_items = [
            {
                "results": [
                    {"passed": True, "properties": {"attack_technique": "baseline"}},
                    {"name": "violence", "passed": True, "properties": {}},
                ]
            }
        ]
        result = ResultProcessor._compute_per_testing_criteria(output_items)
        assert len(result) == 1
        assert result[0]["testing_criteria"] == "violence"

    def test_missing_properties_no_strategy_entry(self):
        """Results without properties dict don't create strategy entries."""
        output_items = [
            {
                "results": [
                    {"name": "violence", "passed": True},
                ]
            }
        ]
        result = ResultProcessor._compute_per_testing_criteria(output_items)
        assert len(result) == 1
        assert result[0] == {"testing_criteria": "violence", "passed": 1, "failed": 0, "skipped": 0, "errored": 0}

    def test_non_dict_results_skipped(self):
        """Non-dict entries in results list are skipped gracefully."""
        output_items = [
            {
                "results": [
                    "not a dict",
                    None,
                    42,
                    {"name": "violence", "passed": True, "properties": {}},
                ]
            }
        ]
        result = ResultProcessor._compute_per_testing_criteria(output_items)
        assert len(result) == 1
        assert result[0]["testing_criteria"] == "violence"

    def test_explicit_status_skipped_in_criteria(self):
        """Results with explicit status='skipped' are classified as skipped regardless of passed field."""
        output_items = [
            {
                "results": [
                    {"name": "violence", "passed": None, "status": "skipped", "properties": {}},
                    {"name": "violence", "passed": True, "properties": {}},
                ]
            }
        ]
        result = ResultProcessor._compute_per_testing_criteria(output_items)
        violence_entry = next(r for r in result if r["testing_criteria"] == "violence")
        assert violence_entry["passed"] == 1
        assert violence_entry["skipped"] == 1
        assert violence_entry["errored"] == 0

    def test_explicit_status_error_in_criteria(self):
        """Results with explicit status='error' are classified as errored."""
        output_items = [
            {
                "results": [
                    {"name": "violence", "passed": None, "status": "error", "properties": {}},
                    {"name": "violence", "passed": False, "properties": {}},
                ]
            }
        ]
        result = ResultProcessor._compute_per_testing_criteria(output_items)
        violence_entry = next(r for r in result if r["testing_criteria"] == "violence")
        assert violence_entry["failed"] == 1
        assert violence_entry["errored"] == 1
        assert violence_entry["skipped"] == 0

    def test_explicit_status_errored_variant(self):
        """Results with status='errored' (alternate spelling) are also classified as errored."""
        output_items = [
            {
                "results": [
                    {"name": "self_harm", "passed": None, "status": "errored", "properties": {}},
                ]
            }
        ]
        result = ResultProcessor._compute_per_testing_criteria(output_items)
        entry = result[0]
        assert entry["errored"] == 1
        assert entry["passed"] == 0


@pytest.mark.unittest
class TestComputeResultCount:
    """Tests for ResultProcessor._compute_result_count (row-level classification)."""

    def test_empty_output_items(self):
        """Empty input returns all zeros."""
        result = ResultProcessor._compute_result_count([])
        assert result == {"total": 0, "passed": 0, "failed": 0, "errored": 0, "skipped": 0}

    def test_sample_error_classified_as_errored(self):
        """Items with sample.error are immediately classified as errored."""
        output_items = [
            {
                "sample": {"error": {"code": "TIMEOUT", "message": "Timed out"}},
                "results": [{"name": "violence", "passed": True}],
            }
        ]
        result = ResultProcessor._compute_result_count(output_items)
        assert result["total"] == 1
        assert result["errored"] == 1
        assert result["passed"] == 0

    def test_empty_results_classified_as_errored(self):
        """Items with empty results list are classified as errored."""
        output_items = [
            {"sample": {}, "results": []},
        ]
        result = ResultProcessor._compute_result_count(output_items)
        assert result["total"] == 1
        assert result["errored"] == 1

    def test_missing_results_classified_as_errored(self):
        """Items without results key at all are classified as errored."""
        output_items = [
            {"sample": {}},
        ]
        result = ResultProcessor._compute_result_count(output_items)
        assert result["total"] == 1
        assert result["errored"] == 1

    def test_passed_row(self):
        """A row with all passed results is classified as passed."""
        output_items = [{"results": [{"name": "v", "passed": True}, {"name": "s", "passed": True}]}]
        result = ResultProcessor._compute_result_count(output_items)
        assert result["passed"] == 1
        assert result["failed"] == 0

    def test_failed_row(self):
        """A row with any failed result is classified as failed (failed > passed)."""
        output_items = [{"results": [{"name": "v", "passed": True}, {"name": "s", "passed": False}]}]
        result = ResultProcessor._compute_result_count(output_items)
        assert result["failed"] == 1
        assert result["passed"] == 0

    def test_failed_takes_priority_over_passed(self):
        """ASR semantics: failed (attack succeeded) takes priority over passed."""
        output_items = [{"results": [{"name": "v", "passed": False}, {"name": "s", "passed": True}]}]
        result = ResultProcessor._compute_result_count(output_items)
        assert result["failed"] == 1
        assert result["passed"] == 0

    def test_skipped_row(self):
        """A row where all results are skipped is classified as skipped."""
        output_items = [{"results": [{"name": "v", "passed": None, "status": "skipped"}]}]
        result = ResultProcessor._compute_result_count(output_items)
        assert result["skipped"] == 1
        assert result["errored"] == 0

    def test_errored_row(self):
        """A row where results have status='error' is classified as errored."""
        output_items = [{"results": [{"name": "v", "passed": None, "status": "error"}]}]
        result = ResultProcessor._compute_result_count(output_items)
        assert result["errored"] == 1
        assert result["skipped"] == 0

    def test_passed_plus_skipped_classified_as_passed(self):
        """A row with 1 pass + 1 skip is 'passed' — skipped is non-execution."""
        output_items = [
            {
                "results": [
                    {"name": "v", "passed": True},
                    {"name": "s", "passed": None, "status": "skipped"},
                ]
            }
        ]
        result = ResultProcessor._compute_result_count(output_items)
        assert result["passed"] == 1
        assert result["skipped"] == 0

    def test_failed_plus_errored_classified_as_failed(self):
        """A row with 1 fail + 1 error is 'failed' — failed takes priority."""
        output_items = [
            {
                "results": [
                    {"name": "v", "passed": False},
                    {"name": "s", "passed": None, "status": "error"},
                ]
            }
        ]
        result = ResultProcessor._compute_result_count(output_items)
        assert result["failed"] == 1
        assert result["errored"] == 0

    def test_error_plus_skip_classified_as_errored(self):
        """A row with only errors and skips is 'errored' — errored > skipped."""
        output_items = [
            {
                "results": [
                    {"name": "v", "passed": None, "status": "error"},
                    {"name": "s", "passed": None, "status": "skipped"},
                ]
            }
        ]
        result = ResultProcessor._compute_result_count(output_items)
        assert result["errored"] == 1
        assert result["skipped"] == 0

    def test_passed_none_without_status_is_skipped(self):
        """passed=None without explicit status is treated as skipped."""
        output_items = [{"results": [{"name": "v", "passed": None}]}]
        result = ResultProcessor._compute_result_count(output_items)
        assert result["skipped"] == 1

    def test_total_equals_sum_of_buckets(self):
        """Invariant: total must equal sum of all buckets."""
        output_items = [
            {"results": [{"name": "v", "passed": True}]},
            {"results": [{"name": "v", "passed": False}]},
            {"results": [{"name": "v", "passed": None, "status": "skipped"}]},
            {"results": [{"name": "v", "passed": None, "status": "error"}]},
            {"sample": {"error": {"code": "E", "message": "m"}}, "results": []},
        ]
        result = ResultProcessor._compute_result_count(output_items)
        bucket_sum = result["passed"] + result["failed"] + result["errored"] + result["skipped"]
        assert result["total"] == bucket_sum
        assert result["total"] == 5
