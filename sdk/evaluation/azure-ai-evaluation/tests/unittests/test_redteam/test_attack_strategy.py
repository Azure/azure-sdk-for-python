"""
Unit tests for attack_strategy module.
"""

import pytest
from unittest.mock import MagicMock, patch

try:
    import pyrit
    has_pyrit = True
except ImportError:
    has_pyrit = False

if has_pyrit:
    from azure.ai.evaluation._red_team._attack_strategy import AttackStrategy


@pytest.mark.unittest
@pytest.mark.skipif(not has_pyrit, reason="redteam extra is not installed")
class TestAttackStrategyEnum:
    """Test the AttackStrategy enum values and behavior."""

    def test_attack_strategy_enum_values(self):
        """Test that AttackStrategy enum has the expected values."""
        # Test some key values
        assert AttackStrategy.EASY.value == "easy"
        assert AttackStrategy.MODERATE.value == "moderate"
        assert AttackStrategy.DIFFICULT.value == "difficult"
        assert AttackStrategy.Baseline.value == "baseline"
        assert AttackStrategy.Jailbreak.value == "jailbreak"
        
        # Test some specific attack strategies
        assert AttackStrategy.Base64.value == "base64"
        assert AttackStrategy.Morse.value == "morse"
        assert AttackStrategy.CharSwap.value == "char_swap"
        
        # Make sure all values are lowercase
        for strategy in AttackStrategy:
            assert strategy.value.islower()


@pytest.mark.unittest
@pytest.mark.skipif(not has_pyrit, reason="redteam extra is not installed")
class TestAttackStrategyCompose:
    """Test the AttackStrategy.Compose functionality."""

    def test_compose_valid(self):
        """Test AttackStrategy.Compose with valid inputs."""
        composed = AttackStrategy.Compose([AttackStrategy.Base64, AttackStrategy.Morse])
        assert isinstance(composed, list)
        assert len(composed) == 2
        assert composed[0] == AttackStrategy.Base64
        assert composed[1] == AttackStrategy.Morse

    def test_compose_single(self):
        """Test AttackStrategy.Compose with a single strategy."""
        composed = AttackStrategy.Compose([AttackStrategy.Base64])
        assert isinstance(composed, list)
        assert len(composed) == 1
        assert composed[0] == AttackStrategy.Base64

    def test_compose_invalid_type(self):
        """Test AttackStrategy.Compose with invalid type."""
        with pytest.raises(ValueError) as excinfo:
            AttackStrategy.Compose(["not_an_enum_instance"])
        assert "All items must be instances of AttackStrategy" in str(excinfo.value)

    def test_compose_too_many(self):
        """Test AttackStrategy.Compose with too many strategies."""
        with pytest.raises(ValueError) as excinfo:
            AttackStrategy.Compose([
                AttackStrategy.Base64, 
                AttackStrategy.Morse, 
                AttackStrategy.Flip
            ])
        assert "Composed strategies must have at most 2 items" in str(excinfo.value)

    def test_compose_empty(self):
        """Test AttackStrategy.Compose with an empty list."""
        composed = AttackStrategy.Compose([])
        assert isinstance(composed, list)
        assert len(composed) == 0