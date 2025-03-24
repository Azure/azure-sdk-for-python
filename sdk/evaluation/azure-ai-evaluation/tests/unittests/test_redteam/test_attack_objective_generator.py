"""
Unit tests for attack_objective_generator module.
"""

import os
from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch, mock_open, ANY as mock_ANY

from azure.ai.evaluation.red_team_agent.attack_objective_generator import (
    AttackObjectiveGenerator, RiskCategory
)


@pytest.mark.unittest
class TestRiskCategoryEnum:
    """Test the RiskCategory enum."""
    
    def test_risk_category_enum_values(self):
        """Test that RiskCategory enum has the expected values."""
        assert RiskCategory.HateUnfairness.value == "hate_unfairness"
        assert RiskCategory.Violence.value == "violence"
        assert RiskCategory.Sexual.value == "sexual"
        assert RiskCategory.SelfHarm.value == "self_harm"
        
        # Ensure all values are lower case with underscores
        for category in RiskCategory:
            assert category.value.islower()
            assert "_" in category.value or category.value.isalpha()


@pytest.mark.unittest
class TestObjectiveGeneratorInitialization:
    """Test AttackObjectiveGenerator initialization."""

    def test_objective_generator_init_default(self):
        """Test AttackObjectiveGenerator initialization with default parameters."""
        generator = AttackObjectiveGenerator(
            risk_categories=[RiskCategory.Violence, RiskCategory.HateUnfairness]
        )
        assert generator.risk_categories == [RiskCategory.Violence, RiskCategory.HateUnfairness]
        assert generator.num_objectives == 10  # Default value
    
    def test_objective_generator_init_custom(self):
        """Test AttackObjectiveGenerator initialization with custom num_objectives."""
        generator_custom = AttackObjectiveGenerator(
            risk_categories=[RiskCategory.Violence], num_objectives=5
        )
        assert generator_custom.risk_categories == [RiskCategory.Violence]
        assert generator_custom.num_objectives == 5

    def test_objective_generator_empty_categories(self):
        """Test AttackObjectiveGenerator with empty categories."""
        generator = AttackObjectiveGenerator(risk_categories=[])
        assert generator.risk_categories == []
        assert generator.num_objectives == 10

    def test_objective_generator_single_category(self):
        """Test AttackObjectiveGenerator with a single category."""
        generator = AttackObjectiveGenerator(risk_categories=[RiskCategory.Sexual])
        assert len(generator.risk_categories) == 1
        assert generator.risk_categories[0] == RiskCategory.Sexual


@pytest.mark.unittest
class TestObjectiveGeneratorFeatures:
    """Test features of the AttackObjectiveGenerator."""
    
    def test_objective_generator_with_all_categories(self):
        """Test AttackObjectiveGenerator with all risk categories."""
        all_categories = list(RiskCategory)
        generator = AttackObjectiveGenerator(risk_categories=all_categories)
        assert set(generator.risk_categories) == set(all_categories)

    def test_objective_generator_with_num_objectives_zero(self):
        """Test AttackObjectiveGenerator with num_objectives=0."""
        # This is technically valid but not useful in practice
        generator = AttackObjectiveGenerator(
            risk_categories=[RiskCategory.Violence], num_objectives=0
        )
        assert generator.num_objectives == 0
        
    def test_objective_generator_with_custom_attack_seed_prompts(self):
        """Test AttackObjectiveGenerator with custom attack seed prompts."""
        # Test with a valid custom prompts file
        custom_prompts_path = os.path.join(os.path.dirname(__file__), "data", "custom_prompts.json")
        generator = AttackObjectiveGenerator(
            custom_attack_seed_prompts=custom_prompts_path
        )
        
        # Check that risk categories were auto-detected
        assert RiskCategory.Violence in generator.risk_categories
        assert RiskCategory.HateUnfairness in generator.risk_categories
        
        # Check that prompts were loaded
        assert len(generator.validated_prompts) == 2
        assert len(generator.valid_prompts_by_category.get(RiskCategory.Violence.value, [])) == 1
        assert len(generator.valid_prompts_by_category.get(RiskCategory.HateUnfairness.value, [])) == 1
        
    def test_objective_generator_with_invalid_custom_attack_seed_prompts(self):
        """Test AttackObjectiveGenerator with invalid custom attack seed prompts path."""
        with pytest.raises(ValueError, match="Custom attack seed prompts file not found"):
            AttackObjectiveGenerator(
                custom_attack_seed_prompts="nonexistent_file.json"
            )
            
    def test_objective_generator_with_relative_path(self):
        """Test AttackObjectiveGenerator with a relative path."""
        # Mock the JSON content with valid prompts
        mock_json_data = """[
            {
                "metadata": {
                    "lang": "en",
                    "target_harms": [
                        {
                            "risk-type": "violence",
                            "risk-subtype": ""
                        }
                    ]
                },
                "messages": [
                    {
                        "role": "user",
                        "content": "test content"
                    }
                ],
                "modality": "text",
                "source": ["test"],
                "id": "1"
            }
        ]"""

        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.is_absolute", return_value=False), \
             patch("pathlib.Path.cwd", return_value=Path("/current/dir")), \
             patch("builtins.open", mock_open(read_data=mock_json_data)), \
             patch("logging.getLogger") as mock_logger:
            
            generator = AttackObjectiveGenerator(
                custom_attack_seed_prompts="relative/path/custom_prompts.json"
            )
            
            # Verify that the path was converted to absolute
            mock_logger.return_value.info.assert_any_call("Converting relative path 'relative/path/custom_prompts.json' to absolute path")
            
    def test_objective_generator_with_absolute_path(self):
        """Test AttackObjectiveGenerator with an absolute path."""
        # Mock the JSON content with valid prompts
        mock_json_data = """[
            {
                "metadata": {
                    "lang": "en",
                    "target_harms": [
                        {
                            "risk-type": "violence",
                            "risk-subtype": ""
                        }
                    ]
                },
                "messages": [
                    {
                        "role": "user",
                        "content": "test content"
                    }
                ],
                "modality": "text",
                "source": ["test"],
                "id": "1"
            }
        ]"""

        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.is_absolute", return_value=True), \
             patch("builtins.open", mock_open(read_data=mock_json_data)), \
             patch("logging.getLogger") as mock_logger:
            
            generator = AttackObjectiveGenerator(
                custom_attack_seed_prompts="/absolute/path/custom_prompts.json"
            )
            
            # Verify that the path was not converted
            for call in mock_logger.return_value.info.call_args_list:
                assert "Converting relative path" not in str(call)