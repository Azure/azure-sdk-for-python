"""
Unit tests for strategy_mapping module.
"""

import pytest
from unittest.mock import MagicMock, patch

from azure.ai.evaluation.red_team._attack_strategy import AttackStrategy
from azure.ai.evaluation.red_team._utils.strategy_mapping import (
    convert_attack_strategy_to_foundry,
    is_foundry_supported,
    ATTACK_STRATEGY_TO_FOUNDRY_STRATEGY,
)


@pytest.mark.unittest
class TestStrategyMapping:
    """Test the strategy mapping functionality."""

    def test_baseline_returns_none(self):
        """Test that Baseline strategy returns None."""
        result = convert_attack_strategy_to_foundry(AttackStrategy.Baseline)
        assert result is None

    def test_supported_strategies_in_mapping(self):
        """Test that supported strategies are in the mapping."""
        # Test strategies that should be supported
        supported = [
            AttackStrategy.Baseline,
            AttackStrategy.ROT13,
            AttackStrategy.Base64,
            AttackStrategy.MultiTurn,
            AttackStrategy.Crescendo,
            AttackStrategy.Jailbreak,
        ]
        for strategy in supported:
            assert strategy in ATTACK_STRATEGY_TO_FOUNDRY_STRATEGY

    def test_unsupported_strategy_raises_error(self):
        """Test that unsupported strategy raises ValueError."""
        # IndirectJailbreak is not in the mapping
        with pytest.raises(ValueError) as excinfo:
            convert_attack_strategy_to_foundry(AttackStrategy.IndirectJailbreak)
        assert "is not supported with FoundryScenario" in str(excinfo.value)

    def test_rot13_mapping(self):
        """Test ROT13 strategy mapping."""
        # Should return a FoundryStrategy value or string
        result = convert_attack_strategy_to_foundry(AttackStrategy.ROT13)
        assert result is not None

    def test_base64_mapping(self):
        """Test Base64 strategy mapping."""
        result = convert_attack_strategy_to_foundry(AttackStrategy.Base64)
        assert result is not None

    def test_multiturn_mapping(self):
        """Test MultiTurn strategy mapping."""
        result = convert_attack_strategy_to_foundry(AttackStrategy.MultiTurn)
        assert result is not None

    def test_crescendo_mapping(self):
        """Test Crescendo strategy mapping."""
        result = convert_attack_strategy_to_foundry(AttackStrategy.Crescendo)
        assert result is not None

    def test_jailbreak_mapping(self):
        """Test Jailbreak strategy mapping."""
        result = convert_attack_strategy_to_foundry(AttackStrategy.Jailbreak)
        assert result is not None


@pytest.mark.unittest
class TestIsFoundrySupported:
    """Test the is_foundry_supported function."""

    def test_baseline_supported(self):
        """Test that Baseline is supported."""
        assert is_foundry_supported(AttackStrategy.Baseline) is True

    def test_rot13_supported(self):
        """Test that ROT13 is supported."""
        assert is_foundry_supported(AttackStrategy.ROT13) is True

    def test_base64_supported(self):
        """Test that Base64 is supported."""
        assert is_foundry_supported(AttackStrategy.Base64) is True

    def test_multiturn_supported(self):
        """Test that MultiTurn is supported."""
        assert is_foundry_supported(AttackStrategy.MultiTurn) is True

    def test_crescendo_supported(self):
        """Test that Crescendo is supported."""
        assert is_foundry_supported(AttackStrategy.Crescendo) is True

    def test_jailbreak_supported(self):
        """Test that Jailbreak is supported."""
        assert is_foundry_supported(AttackStrategy.Jailbreak) is True

    def test_indirect_jailbreak_not_supported(self):
        """Test that IndirectJailbreak is not supported."""
        assert is_foundry_supported(AttackStrategy.IndirectJailbreak) is False

    def test_ascii_art_not_supported(self):
        """Test that AsciiArt is not supported."""
        assert is_foundry_supported(AttackStrategy.AsciiArt) is False
