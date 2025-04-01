"""
Unit tests for attack_objective_generator module.
"""

import os
from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch, mock_open, ANY as mock_ANY

try: 
    import pyrit 
    has_pyrit = True
except ImportError:
    has_pyrit = False

if has_pyrit:
    from azure.ai.evaluation._red_team._attack_objective_generator import (
        _AttackObjectiveGenerator, RiskCategory
    )


@pytest.mark.unittest
@pytest.mark.skipif(not has_pyrit, reason="redteam extra is not installed")
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
@pytest.mark.skipif(not has_pyrit, reason="redteam extra is not installed")
class TestObjectiveGeneratorInitialization:
    """Test _AttackObjectiveGenerator initialization."""

    def test_objective_generator_init_default(self):
        """Test _AttackObjectiveGenerator initialization with default parameters."""
        generator = _AttackObjectiveGenerator(
            risk_categories=[RiskCategory.Violence, RiskCategory.HateUnfairness]
        )
        assert generator.risk_categories == [RiskCategory.Violence, RiskCategory.HateUnfairness]
        assert generator.num_objectives == 10  # Default value
    
    def test_objective_generator_init_custom(self):
        """Test _AttackObjectiveGenerator initialization with custom num_objectives."""
        generator_custom = _AttackObjectiveGenerator(
            risk_categories=[RiskCategory.Violence], num_objectives=5
        )
        assert generator_custom.risk_categories == [RiskCategory.Violence]
        assert generator_custom.num_objectives == 5

    def test_objective_generator_empty_categories(self):
        """Test _AttackObjectiveGenerator with empty categories."""
        generator = _AttackObjectiveGenerator(risk_categories=[])
        assert generator.risk_categories == []
        assert generator.num_objectives == 10

    def test_objective_generator_single_category(self):
        """Test _AttackObjectiveGenerator with a single category."""
        generator = _AttackObjectiveGenerator(risk_categories=[RiskCategory.Sexual])
        assert len(generator.risk_categories) == 1
        assert generator.risk_categories[0] == RiskCategory.Sexual


@pytest.mark.unittest
@pytest.mark.skipif(not has_pyrit, reason="redteam extra is not installed")
class TestObjectiveGeneratorFeatures:
    """Test features of the _AttackObjectiveGenerator."""
    
    def test_objective_generator_with_all_categories(self):
        """Test _AttackObjectiveGenerator with all risk categories."""
        all_categories = list(RiskCategory)
        generator = _AttackObjectiveGenerator(risk_categories=all_categories)
        assert set(generator.risk_categories) == set(all_categories)

    def test_objective_generator_with_num_objectives_zero(self):
        """Test _AttackObjectiveGenerator with num_objectives=0."""
        # This is technically valid but not useful in practice
        generator = _AttackObjectiveGenerator(
            risk_categories=[RiskCategory.Violence], num_objectives=0
        )
        assert generator.num_objectives == 0
        
    def test_objective_generator_with_custom_attack_seed_prompts(self):
        """Test _AttackObjectiveGenerator with custom attack seed prompts."""
        # Test with a valid custom prompts file
        custom_prompts_path = os.path.join(os.path.dirname(__file__), "data", "custom_prompts.json")
        generator = _AttackObjectiveGenerator(
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
        """Test _AttackObjectiveGenerator with invalid custom attack seed prompts path."""
        with pytest.raises(ValueError, match="Custom attack seed prompts file not found"):
            _AttackObjectiveGenerator(
                custom_attack_seed_prompts="nonexistent_file.json"
            )
            
    def test_objective_generator_with_relative_path(self):
        """Test _AttackObjectiveGenerator with a relative path."""
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
        
        expected_abs_path = Path("/current/dir/relative/path/custom_prompts.json")

        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.is_absolute", return_value=False), \
             patch("pathlib.Path.cwd", return_value=Path("/current/dir")), \
             patch("pathlib.Path.resolve", return_value=expected_abs_path), \
             patch("builtins.open", mock_open(read_data=mock_json_data)):
            
            rel_path = "relative/path/custom_prompts.json"
            generator = _AttackObjectiveGenerator(
                custom_attack_seed_prompts=rel_path
            )
            
            # Instead of checking for a specific log message, verify that the path was processed correctly
            # by confirming the generator was successfully created and has the expected data
            assert generator is not None
            assert RiskCategory.Violence in generator.risk_categories
            assert len(generator.validated_prompts) == 1
    
    def test_objective_generator_with_absolute_path(self):
        """Test _AttackObjectiveGenerator with an absolute path."""
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
            
            generator = _AttackObjectiveGenerator(
                custom_attack_seed_prompts="/absolute/path/custom_prompts.json"
            )
            
            # Verify that the path was not converted
            for call in mock_logger.return_value.info.call_args_list:
                assert "Converting relative path" not in str(call)