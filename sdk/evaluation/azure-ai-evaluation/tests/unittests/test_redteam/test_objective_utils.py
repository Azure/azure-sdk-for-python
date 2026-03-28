"""
Unit tests for red_team._utils.objective_utils module.
"""

import pytest
from unittest.mock import patch

from azure.ai.evaluation.red_team._utils.objective_utils import (
    extract_risk_subtype,
    get_objective_id,
)


@pytest.mark.unittest
class TestExtractRiskSubtype:
    """Test extract_risk_subtype function."""

    def test_returns_subtype_from_valid_objective(self):
        """Extract risk-subtype when present in target_harms."""
        objective = {"metadata": {"target_harms": [{"risk-subtype": "violence_physical"}]}}
        assert extract_risk_subtype(objective) == "violence_physical"

    def test_returns_first_non_empty_subtype(self):
        """Return the first non-empty risk-subtype when multiple harms exist."""
        objective = {
            "metadata": {
                "target_harms": [
                    {"risk-subtype": ""},
                    {"risk-subtype": "hate_speech"},
                    {"risk-subtype": "self_harm"},
                ]
            }
        }
        assert extract_risk_subtype(objective) == "hate_speech"

    def test_returns_none_when_all_subtypes_empty(self):
        """Return None when all risk-subtype values are empty strings."""
        objective = {
            "metadata": {
                "target_harms": [
                    {"risk-subtype": ""},
                    {"risk-subtype": ""},
                ]
            }
        }
        assert extract_risk_subtype(objective) is None

    def test_returns_none_when_no_metadata(self):
        """Return None when objective has no metadata key."""
        assert extract_risk_subtype({}) is None

    def test_returns_none_when_metadata_empty(self):
        """Return None when metadata is an empty dict."""
        assert extract_risk_subtype({"metadata": {}}) is None

    def test_returns_none_when_target_harms_empty_list(self):
        """Return None when target_harms is an empty list."""
        objective = {"metadata": {"target_harms": []}}
        assert extract_risk_subtype(objective) is None

    def test_returns_none_when_target_harms_not_a_list(self):
        """Return None when target_harms is not a list."""
        objective = {"metadata": {"target_harms": "not_a_list"}}
        assert extract_risk_subtype(objective) is None

    def test_skips_non_dict_harm_entries(self):
        """Skip entries in target_harms that are not dicts."""
        objective = {
            "metadata": {
                "target_harms": [
                    "string_entry",
                    42,
                    {"risk-subtype": "valid_subtype"},
                ]
            }
        }
        assert extract_risk_subtype(objective) == "valid_subtype"

    def test_skips_dict_without_risk_subtype_key(self):
        """Skip dict entries that don't have the risk-subtype key."""
        objective = {
            "metadata": {
                "target_harms": [
                    {"other_key": "value"},
                    {"risk-subtype": "found_it"},
                ]
            }
        }
        assert extract_risk_subtype(objective) == "found_it"

    def test_returns_none_when_only_non_dict_entries(self):
        """Return None when target_harms contains only non-dict entries."""
        objective = {"metadata": {"target_harms": ["a", 1, None]}}
        assert extract_risk_subtype(objective) is None

    def test_returns_none_when_subtype_is_none(self):
        """Return None when risk-subtype value is None (falsy)."""
        objective = {"metadata": {"target_harms": [{"risk-subtype": None}]}}
        assert extract_risk_subtype(objective) is None


@pytest.mark.unittest
class TestGetObjectiveId:
    """Test get_objective_id function."""

    def test_returns_existing_id(self):
        """Return the existing 'id' field as a string."""
        objective = {"id": "abc-123"}
        assert get_objective_id(objective) == "abc-123"

    def test_returns_numeric_id_as_string(self):
        """Convert a numeric 'id' field to string."""
        objective = {"id": 42}
        assert get_objective_id(objective) == "42"

    def test_generates_uuid_when_no_id(self):
        """Generate a UUID-based identifier when no 'id' key exists."""
        objective = {"name": "test"}
        result = get_objective_id(objective)
        assert result.startswith("generated-")
        # UUID portion should be 36 chars (8-4-4-4-12 with hyphens)
        uuid_part = result[len("generated-") :]
        assert len(uuid_part) == 36

    def test_generates_uuid_for_empty_dict(self):
        """Generate a UUID-based identifier for an empty dict."""
        result = get_objective_id({})
        assert result.startswith("generated-")

    def test_returns_id_when_value_is_zero(self):
        """Return '0' when id is 0 (falsy but not None)."""
        objective = {"id": 0}
        assert get_objective_id(objective) == "0"

    def test_returns_id_when_value_is_empty_string(self):
        """Return empty string when id is '' (falsy but not None)."""
        objective = {"id": ""}
        assert get_objective_id(objective) == ""

    def test_generates_uuid_when_id_is_none(self):
        """Generate UUID when 'id' key exists but value is None."""
        objective = {"id": None}
        result = get_objective_id(objective)
        assert result.startswith("generated-")

    def test_generated_ids_are_unique(self):
        """Each call without 'id' should produce a unique identifier."""
        objective = {"name": "test"}
        id1 = get_objective_id(objective)
        id2 = get_objective_id(objective)
        assert id1 != id2

    @patch("azure.ai.evaluation.red_team._utils.objective_utils.uuid.uuid4")
    def test_generated_id_uses_uuid4(self, mock_uuid4):
        """Verify the generated id uses uuid.uuid4()."""
        mock_uuid4.return_value = "fake-uuid-value"
        result = get_objective_id({})
        assert result == "generated-fake-uuid-value"
        mock_uuid4.assert_called_once()
