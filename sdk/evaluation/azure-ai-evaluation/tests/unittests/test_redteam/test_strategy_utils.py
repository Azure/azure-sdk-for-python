"""
Tests for the strategy_utils module.
"""

import pytest
from unittest.mock import MagicMock, patch
from typing import Dict, List, Callable

from pyrit.common import initialize_pyrit, IN_MEMORY

from azure.ai.evaluation.red_team._utils.strategy_utils import (
    strategy_converter_map,
    get_converter_for_strategy,
    get_chat_target,
)
from azure.ai.evaluation.red_team._attack_strategy import AttackStrategy
from azure.ai.evaluation.red_team._callback_chat_target import _CallbackChatTarget
from pyrit.prompt_converter import PromptConverter, Base64Converter, FlipConverter, MorseConverter
from pyrit.prompt_target import PromptChatTarget, OpenAIChatTarget

initialize_pyrit(memory_db_type=IN_MEMORY)


@pytest.mark.unittest
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
class TestConverterForStrategy:
    """Test the get_converter_for_strategy function."""

    def test_get_converter_for_strategy_single(self):
        """Test getting converter for a single strategy."""
        # Create mock dependencies
        mock_rai_client = MagicMock()
        mock_logger = MagicMock()

        converter = get_converter_for_strategy(AttackStrategy.Base64, mock_rai_client, False, mock_logger)
        assert isinstance(converter, Base64Converter)

        # Test strategy with no converter
        converter = get_converter_for_strategy(AttackStrategy.Baseline, mock_rai_client, False, mock_logger)
        assert converter is None

    def test_get_converter_for_strategy_list(self):
        """Test getting converters for a list of strategies."""
        # Create mock dependencies
        mock_rai_client = MagicMock()
        mock_logger = MagicMock()

        strategies = [AttackStrategy.Base64, AttackStrategy.Flip]
        converters = get_converter_for_strategy(strategies, mock_rai_client, False, mock_logger)

        assert isinstance(converters, list)
        assert len(converters) == 2
        assert isinstance(converters[0], Base64Converter)
        assert isinstance(converters[1], FlipConverter)


@pytest.mark.unittest
class TestChatTargetFunctions:
    """Test chat target related functions."""

    @patch("azure.ai.evaluation.red_team._utils.strategy_utils.OpenAIChatTarget")
    def test_get_chat_target_prompt_chat_target(self, mock_openai_chat_target):
        """Test getting chat target from an existing PromptChatTarget."""
        mock_target = MagicMock(spec=PromptChatTarget)
        result = get_chat_target(mock_target)

        assert result == mock_target
        # Verify that we don't create a new target
        mock_openai_chat_target.assert_not_called()

    @patch("azure.ai.evaluation.red_team._utils.strategy_utils.OpenAIChatTarget")
    def test_get_chat_target_azure_openai(self, mock_openai_chat_target):
        """Test getting chat target from an Azure OpenAI configuration."""
        mock_instance = MagicMock()
        mock_openai_chat_target.return_value = mock_instance

        # Test with API key
        config = {
            "azure_deployment": "gpt-35-turbo",
            "azure_endpoint": "https://example.openai.azure.com",
            "api_key": "test-api-key",
        }

        result = get_chat_target(config)

        mock_openai_chat_target.assert_called_once_with(
            model_name="gpt-35-turbo",
            endpoint="https://example.openai.azure.com",
            api_key="test-api-key",
            api_version="2024-06-01",
        )
        assert result == mock_instance

        # Reset mock
        mock_openai_chat_target.reset_mock()

        # Test with AAD auth
        config = {"azure_deployment": "gpt-35-turbo", "azure_endpoint": "https://example.openai.azure.com"}

        result = get_chat_target(config)

        mock_openai_chat_target.assert_called_once_with(
            model_name="gpt-35-turbo",
            endpoint="https://example.openai.azure.com",
            use_aad_auth=True,
            api_version="2024-06-01",
        )

    @patch("azure.ai.evaluation.red_team._utils.strategy_utils.OpenAIChatTarget")
    def test_get_chat_target_openai(self, mock_openai_chat_target):
        """Test getting chat target from an OpenAI configuration."""
        mock_instance = MagicMock()
        mock_openai_chat_target.return_value = mock_instance

        config = {"model": "gpt-4", "api_key": "test-api-key"}

        result = get_chat_target(config)

        mock_openai_chat_target.assert_called_once_with(
            model_name="gpt-4", endpoint=None, api_key="test-api-key", api_version="2024-06-01"
        )

        # Test with base_url
        mock_openai_chat_target.reset_mock()

        config = {"model": "gpt-4", "api_key": "test-api-key", "base_url": "https://example.com/api"}

        result = get_chat_target(config)

        mock_openai_chat_target.assert_called_once_with(
            model_name="gpt-4", endpoint="https://example.com/api", api_key="test-api-key", api_version="2024-06-01"
        )

    @patch("azure.ai.evaluation.red_team._utils.strategy_utils._CallbackChatTarget")
    def test_get_chat_target_callback_function(self, mock_callback_chat_target):
        """Test getting chat target from a callback function with proper signature."""
        mock_instance = MagicMock()
        mock_callback_chat_target.return_value = mock_instance

        def callback_fn(messages, stream, session_state, context):
            return {"role": "assistant", "content": "test"}

        result = get_chat_target(callback_fn)

        mock_callback_chat_target.assert_called_once_with(callback=callback_fn)
        assert result == mock_instance

    @patch("azure.ai.evaluation.red_team._utils.strategy_utils._CallbackChatTarget")
    def test_get_chat_target_callback_function_with_context(self, mock_callback_chat_target):
        """Test getting chat target from a callback function. Context is now handled via request labels."""
        mock_instance = MagicMock()
        mock_callback_chat_target.return_value = mock_instance

        def callback_fn(messages, stream, session_state, context):
            return {"role": "assistant", "content": "test"}

        result = get_chat_target(callback_fn)

        mock_callback_chat_target.assert_called_once_with(callback=callback_fn)
        assert result == mock_instance

    @patch("azure.ai.evaluation.red_team._utils.strategy_utils._CallbackChatTarget")
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

    @patch("azure.ai.evaluation.red_team._utils.strategy_utils._CallbackChatTarget")
    def test_get_chat_target_simple_function_with_context(self, mock_callback_chat_target):
        """Test getting chat target from a simple function. Context is now handled via request labels."""
        mock_instance = MagicMock()
        mock_callback_chat_target.return_value = mock_instance

        def simple_fn(query):
            return "test response"

        result = get_chat_target(simple_fn)

        # Verify that _CallbackChatTarget was called
        mock_callback_chat_target.assert_called_once()
        assert result == mock_instance

    def test_get_chat_target_simple_function_context_support(self):
        """Test that simple function with context parameter works. Context is now handled via request labels."""

        def simple_fn_with_context(query, context=None):
            # Function that accepts context parameter
            if context:
                return f"Response with context: {context}"
            return "Response without context"

        result = get_chat_target(simple_fn_with_context)

        # Verify we get a callback target
        assert isinstance(result, _CallbackChatTarget)

    def test_get_chat_target_simple_function_no_context_support(self):
        """Test that simple function without context parameter works normally."""

        def simple_fn(query):
            return "test response"

        result = get_chat_target(simple_fn)

        # Verify we get a callback target
        assert isinstance(result, _CallbackChatTarget)
