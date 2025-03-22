"""
Unit tests for attack_objective_generator module.
"""

import pytest
from unittest.mock import MagicMock, patch

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