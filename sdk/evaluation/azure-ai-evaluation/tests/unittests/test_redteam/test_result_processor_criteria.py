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
        assert result[0] == {"testing_criteria": "self_harm", "passed": 1, "failed": 0}
        assert result[1] == {"testing_criteria": "violence", "passed": 1, "failed": 1}
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
        assert result[0] == {"testing_criteria": "violence", "passed": 1, "failed": 1}
        # Then attack strategies sorted alphabetically
        assert result[1] == {"testing_criteria": "Base64", "attack_strategy": "Base64", "passed": 0, "failed": 1}
        assert result[2] == {"testing_criteria": "baseline", "attack_strategy": "baseline", "passed": 1, "failed": 0}

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

    def test_passed_none_skipped(self):
        """Results with passed=None are excluded from counting."""
        output_items = [
            {
                "results": [
                    {"name": "violence", "passed": None, "properties": {"attack_technique": "baseline"}},
                    {"name": "violence", "passed": True, "properties": {"attack_technique": "baseline"}},
                ]
            }
        ]
        result = ResultProcessor._compute_per_testing_criteria(output_items)
        violence_entry = next(r for r in result if r["testing_criteria"] == "violence")
        assert violence_entry["passed"] == 1
        assert violence_entry["failed"] == 0
        baseline_entry = next(r for r in result if r.get("attack_strategy") == "baseline")
        assert baseline_entry["passed"] == 1
        assert baseline_entry["failed"] == 0

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
        assert result[0] == {"testing_criteria": "violence", "passed": 1, "failed": 0}

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
