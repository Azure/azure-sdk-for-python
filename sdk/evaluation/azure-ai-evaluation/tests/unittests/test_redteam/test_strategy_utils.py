"""
Tests for the strategy_utils module.
"""
import pytest
from unittest.mock import MagicMock, patch
from typing import Dict, List, Callable

try:
    import pyrit
    has_pyrit = True
except ImportError:
    has_pyrit = False
if has_pyrit:
    from azure.ai.evaluation._red_team._utils.strategy_utils import (
        strategy_converter_map,
        get_converter_for_strategy,
        get_chat_target,
        get_orchestrators_for_attack_strategies
    )
    from azure.ai.evaluation._red_team._attack_strategy import AttackStrategy
    from azure.ai.evaluation._red_team._callback_chat_target import _CallbackChatTarget
    from pyrit.prompt_converter import (
        PromptConverter, Base64Converter, FlipConverter, MorseConverter
    )
    from pyrit.prompt_target import PromptChatTarget, OpenAIChatTarget


@pytest.mark.unittest
@pytest.mark.skipif(not has_pyrit, reason="redteam extra is not installed")
class TestStrategyConverterMap:
    """Test the strategy_converter_map function."""

    def test_strategy_converter_map(self):
        """Test that the strategy converter map contains expected mappings."""
        converters = strategy_converter_map()
        
        # Test that all attack strategies have a corresponding converter
        for strategy in AttackStrategy:
            assert strategy in converters, f"Missing converter for {strategy}"
        
        # Test specific converters
        assert converters[AttackStrategy.Baseline] is None
        assert isinstance(converters[AttackStrategy.Base64], Base64Converter)
        assert isinstance(converters[AttackStrategy.Flip], FlipConverter)
        assert isinstance(converters[AttackStrategy.Morse], MorseConverter)
        
        # Test strategy groups
        assert isinstance(converters[AttackStrategy.EASY], list)
        assert len(converters[AttackStrategy.EASY]) == 3
        assert isinstance(converters[AttackStrategy.MODERATE], list)
        assert isinstance(converters[AttackStrategy.DIFFICULT], list)


@pytest.mark.unittest
@pytest.mark.skipif(not has_pyrit, reason="redteam extra is not installed")
class TestConverterForStrategy:
    """Test the get_converter_for_strategy function."""

    def test_get_converter_for_strategy_single(self):
        """Test getting converter for a single strategy."""
        converter = get_converter_for_strategy(AttackStrategy.Base64)
        assert isinstance(converter, Base64Converter)
        
        # Test strategy with no converter
        converter = get_converter_for_strategy(AttackStrategy.Baseline)
        assert converter is None

    def test_get_converter_for_strategy_list(self):
        """Test getting converters for a list of strategies."""
        strategies = [AttackStrategy.Base64, AttackStrategy.Flip]
        converters = get_converter_for_strategy(strategies)
        
        assert isinstance(converters, list)
        assert len(converters) == 2
        assert isinstance(converters[0], Base64Converter)
        assert isinstance(converters[1], FlipConverter)


@pytest.mark.unittest
@pytest.mark.skipif(not has_pyrit, reason="redteam extra is not installed")
class TestChatTargetFunctions:
    """Test chat target related functions."""

    @patch("azure.ai.evaluation._red_team._utils.strategy_utils.OpenAIChatTarget")
    def test_get_chat_target_prompt_chat_target(self, mock_openai_chat_target):
        """Test getting chat target from an existing PromptChatTarget."""
        mock_target = MagicMock(spec=PromptChatTarget)
        result = get_chat_target(mock_target)
        
        assert result == mock_target
        # Verify that we don't create a new target
        mock_openai_chat_target.assert_not_called()

    @patch("azure.ai.evaluation._red_team._utils.strategy_utils.OpenAIChatTarget")
    def test_get_chat_target_azure_openai(self, mock_openai_chat_target):
        """Test getting chat target from an Azure OpenAI configuration."""
        mock_instance = MagicMock()
        mock_openai_chat_target.return_value = mock_instance
        
        # Test with API key
        config = {
            "azure_deployment": "gpt-35-turbo",
            "azure_endpoint": "https://example.openai.azure.com",
            "api_key": "test-api-key"
        }
        
        result = get_chat_target(config)
        
        mock_openai_chat_target.assert_called_once_with(
            model_name="gpt-35-turbo",
            endpoint="https://example.openai.azure.com",
            api_key="test-api-key"
        )
        assert result == mock_instance
        
        # Reset mock
        mock_openai_chat_target.reset_mock()
        
        # Test with AAD auth
        config = {
            "azure_deployment": "gpt-35-turbo",
            "azure_endpoint": "https://example.openai.azure.com"
        }
        
        result = get_chat_target(config)
        
        mock_openai_chat_target.assert_called_once_with(
            model_name="gpt-35-turbo",
            endpoint="https://example.openai.azure.com",
            use_aad_auth=True
        )

    @patch("azure.ai.evaluation._red_team._utils.strategy_utils.OpenAIChatTarget")
    def test_get_chat_target_openai(self, mock_openai_chat_target):
        """Test getting chat target from an OpenAI configuration."""
        mock_instance = MagicMock()
        mock_openai_chat_target.return_value = mock_instance
        
        config = {
            "model": "gpt-4",
            "api_key": "test-api-key"
        }
        
        result = get_chat_target(config)
        
        mock_openai_chat_target.assert_called_once_with(
            model_name="gpt-4",
            endpoint=None,
            api_key="test-api-key"
        )
        
        # Test with base_url
        mock_openai_chat_target.reset_mock()
        
        config = {
            "model": "gpt-4",
            "api_key": "test-api-key",
            "base_url": "https://example.com/api"
        }
        
        result = get_chat_target(config)
        
        mock_openai_chat_target.assert_called_once_with(
            model_name="gpt-4",
            endpoint="https://example.com/api",
            api_key="test-api-key"
        )

    @patch("azure.ai.evaluation._red_team._utils.strategy_utils._CallbackChatTarget")
    def test_get_chat_target_callback_function(self, mock_callback_chat_target):
        """Test getting chat target from a callback function with proper signature."""
        mock_instance = MagicMock()
        mock_callback_chat_target.return_value = mock_instance
        
        def callback_fn(messages, stream, session_state, context):
            return {"role": "assistant", "content": "test"}
        
        result = get_chat_target(callback_fn)
        
        mock_callback_chat_target.assert_called_once_with(callback=callback_fn)
        assert result == mock_instance

    @patch("azure.ai.evaluation._red_team._utils.strategy_utils._CallbackChatTarget")
    def test_get_chat_target_simple_function(self, mock_callback_chat_target):
        """Test getting chat target from a simple function without proper signature."""
        mock_instance = MagicMock()
        mock_callback_chat_target.return_value = mock_instance
        
        def simple_fn(query):
            return "test response"
        
        result = get_chat_target(simple_fn)
        
        # Verify that _CallbackChatTarget was called with a function that has been adapted
        mock_callback_chat_target.assert_called_once()
        assert result == mock_instance


@pytest.mark.unittest
@pytest.mark.skipif(not has_pyrit, reason="redteam extra is not installed")
class TestOrchestratorFunctions:
    """Test orchestrator related functions."""

    def test_get_orchestrators_for_attack_strategies(self):
        """Test getting orchestrators for attack strategies."""
        strategies = [AttackStrategy.Base64, AttackStrategy.Flip]
        orchestrators = get_orchestrators_for_attack_strategies(strategies)
        
        assert isinstance(orchestrators, list)
        assert len(orchestrators) == 1
        assert callable(orchestrators[0])
        
        # Test the orchestrator function returns None (since it's a placeholder)
        mock_chat_target = MagicMock()
        mock_prompts = ["test prompt"]
        mock_converter = MagicMock()
        
        result = orchestrators[0](mock_chat_target, mock_prompts, mock_converter, "test-strategy", "test-risk")
        assert result is None