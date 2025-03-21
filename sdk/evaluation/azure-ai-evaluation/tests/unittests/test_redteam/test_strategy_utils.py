"""
Unit tests for red_team_agent.utils.strategy_utils module.
"""

import pytest
import inspect
from unittest.mock import patch, MagicMock, AsyncMock
from azure.ai.evaluation.red_team_agent.utils.strategy_utils import (
    strategy_converter_map, get_converter_for_strategy, get_chat_target,
    get_orchestrators_for_attack_strategies
)
from azure.ai.evaluation.red_team_agent.attack_strategy import AttackStrategy
from pyrit.prompt_converter import PromptConverter
from pyrit.chat import PromptChatTarget, OpenAIChatTarget, CallbackChatTarget


@pytest.fixture
def mock_converter():
    """Create a mock converter for testing."""
    return MagicMock(spec=PromptConverter)


@pytest.fixture
def mock_prompt_chat_target():
    """Create a mock PromptChatTarget for testing."""
    return MagicMock(spec=PromptChatTarget)


def test_strategy_converter_map():
    """Test the strategy converter mapping contains all strategies."""
    converter_map = strategy_converter_map()
    
    # Check that all strategies are in the map
    for strategy in AttackStrategy:
        assert strategy in converter_map
    
    # Check specific converters for key strategies
    assert converter_map[AttackStrategy.Baseline] is None
    assert converter_map[AttackStrategy.EASY] is not None
    assert isinstance(converter_map[AttackStrategy.EASY], list)
    assert len(converter_map[AttackStrategy.EASY]) == 3  # Should have 3 converters for EASY
    assert converter_map[AttackStrategy.Jailbreak] is None


def test_get_converter_for_strategy_single():
    """Test getting converter for a single strategy."""
    with patch('azure.ai.evaluation.red_team_agent.utils.strategy_utils.strategy_converter_map') as mock_map:
        mock_converter = MagicMock(spec=PromptConverter)
        mock_map.return_value = {AttackStrategy.Base64: mock_converter}
        
        result = get_converter_for_strategy(AttackStrategy.Base64)
        
        assert result is mock_converter


def test_get_converter_for_strategy_list():
    """Test getting converters for a list of strategies."""
    with patch('azure.ai.evaluation.red_team_agent.utils.strategy_utils.strategy_converter_map') as mock_map:
        mock_converter1 = MagicMock(spec=PromptConverter)
        mock_converter2 = MagicMock(spec=PromptConverter)
        mock_map.return_value = {
            AttackStrategy.Base64: mock_converter1,
            AttackStrategy.Flip: mock_converter2
        }
        
        result = get_converter_for_strategy([AttackStrategy.Base64, AttackStrategy.Flip])
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0] is mock_converter1
        assert result[1] is mock_converter2


@patch("azure.ai.evaluation.red_team_agent.utils.strategy_utils.OpenAIChatTarget")
def test_get_chat_target_from_prompt_chat_target(mock_open_ai_target, mock_prompt_chat_target):
    """Test that get_chat_target returns input when already a PromptChatTarget."""
    result = get_chat_target(mock_prompt_chat_target)
    
    assert result is mock_prompt_chat_target
    mock_open_ai_target.assert_not_called()


@patch("azure.ai.evaluation.red_team_agent.utils.strategy_utils.OpenAIChatTarget")
def test_get_chat_target_from_azure_openai_config(mock_open_ai_target):
    """Test creating chat target from Azure OpenAI configuration."""
    azure_config = {
        "azure_deployment": "test-deployment",
        "azure_endpoint": "https://test-endpoint",
        "api_key": "test-api-key"
    }
    
    mock_target_instance = MagicMock()
    mock_open_ai_target.return_value = mock_target_instance
    
    result = get_chat_target(azure_config)
    
    assert result is mock_target_instance
    mock_open_ai_target.assert_called_once_with(
        model_name="test-deployment",
        endpoint="https://test-endpoint",
        api_key="test-api-key"
    )


@patch("azure.ai.evaluation.red_team_agent.utils.strategy_utils.OpenAIChatTarget")
def test_get_chat_target_from_azure_openai_config_with_aad_auth(mock_open_ai_target):
    """Test creating chat target from Azure OpenAI configuration with AAD auth."""
    azure_config = {
        "azure_deployment": "test-deployment",
        "azure_endpoint": "https://test-endpoint"
    }
    
    mock_target_instance = MagicMock()
    mock_open_ai_target.return_value = mock_target_instance
    
    result = get_chat_target(azure_config)
    
    assert result is mock_target_instance
    mock_open_ai_target.assert_called_once_with(
        model_name="test-deployment",
        endpoint="https://test-endpoint",
        use_aad_auth=True
    )


@patch("azure.ai.evaluation.red_team_agent.utils.strategy_utils.OpenAIChatTarget")
def test_get_chat_target_from_openai_config(mock_open_ai_target):
    """Test creating chat target from OpenAI configuration."""
    openai_config = {
        "model": "test-model",
        "api_key": "test-api-key",
        "base_url": "https://test-base-url"
    }
    
    mock_target_instance = MagicMock()
    mock_open_ai_target.return_value = mock_target_instance
    
    result = get_chat_target(openai_config)
    
    assert result is mock_target_instance
    mock_open_ai_target.assert_called_once_with(
        model_name="test-model",
        endpoint="https://test-base-url",
        api_key="test-api-key"
    )


@patch("azure.ai.evaluation.red_team_agent.utils.strategy_utils.inspect.signature")
@patch("azure.ai.evaluation.red_team_agent.utils.strategy_utils.CallbackChatTarget")
def test_get_chat_target_from_valid_callback_target(mock_callback_chat_target, mock_signature):
    """Test creating chat target from callback with valid signature."""
    callback_fn = MagicMock()
    
    # Mock that the function has the expected signature
    mock_signature.return_value = MagicMock()
    mock_signature.return_value.parameters = {
        "messages": None, "stream": None, "session_state": None, "context": None
    }
    
    mock_target_instance = MagicMock()
    mock_callback_chat_target.return_value = mock_target_instance
    
    result = get_chat_target(callback_fn)
    
    assert result is mock_target_instance
    mock_callback_chat_target.assert_called_once_with(callback=callback_fn)


@patch("azure.ai.evaluation.red_team_agent.utils.strategy_utils.inspect.signature")
@patch("azure.ai.evaluation.red_team_agent.utils.strategy_utils.CallbackChatTarget")
def test_get_chat_target_from_simple_callback(mock_callback_chat_target, mock_signature):
    """Test creating chat target from simple callback function."""
    callback_fn = lambda query: f"Response to {query}"
    
    # Mock that the function doesn't have the expected signature
    mock_signature.return_value = MagicMock()
    mock_signature.return_value.parameters = {"query": None}
    
    mock_target_instance = MagicMock()
    mock_callback_chat_target.return_value = mock_target_instance
    
    result = get_chat_target(callback_fn)
    
    assert result is mock_target_instance
    mock_callback_chat_target.assert_called_once()


@patch("azure.ai.evaluation.red_team_agent.utils.strategy_utils.inspect.signature")
def test_get_chat_target_from_callback_handles_exception(mock_signature):
    """Test that get_chat_target handles exceptions when inspecting signature."""
    callback_fn = MagicMock()
    
    # Mock that inspecting the signature raises an exception
    mock_signature.side_effect = ValueError("Test exception")
    
    # Should create a CallbackChatTarget with a wrapper function
    result = get_chat_target(callback_fn)
    
    assert isinstance(result, CallbackChatTarget)


def test_get_orchestrators_for_attack_strategies():
    """Test that get_orchestrators_for_attack_strategies returns expected orchestrators."""
    attack_strategies = [AttackStrategy.Base64, AttackStrategy.Flip]
    
    result = get_orchestrators_for_attack_strategies(attack_strategies)
    
    assert isinstance(result, list)
    assert len(result) == 1  # Should return 1 orchestrator in current implementation
    assert callable(result[0])  # Result should be a callable function