"""
Unit tests for red_team.utils.formatting_utils module.
"""

import pytest
import math
import json
from unittest.mock import patch, MagicMock, mock_open
from azure.ai.evaluation.red_team._utils.formatting_utils import (
    message_to_dict,
    get_strategy_name,
    get_flattened_attack_strategies,
    get_attack_success,
    format_scorecard,
    is_none_or_nan,
    list_mean_nan_safe,
    _detect_target_http_errors,
)
from azure.ai.evaluation.red_team._attack_strategy import AttackStrategy
from azure.ai.evaluation._exceptions import EvaluationException
from pyrit.models import ChatMessage


@pytest.fixture(scope="function")
def mock_chat_message():
    """Create a mock chat message for testing."""
    message = MagicMock(spec=ChatMessage)
    message.role = "user"
    message.content = "test content"
    return message


@pytest.mark.unittest
class TestMessageToDict:
    """Test message_to_dict function."""

    def test_message_to_dict(self, mock_chat_message):
        """Test conversion of ChatMessage to dictionary."""
        result = message_to_dict(mock_chat_message)

        assert isinstance(result, dict)
        assert result["role"] == "user"
        assert result["content"] == "test content"


@pytest.mark.unittest
class TestStrategyNameFunctions:
    """Test strategy name handling functions."""

    def test_get_strategy_name_single(self):
        """Test getting strategy name from a single strategy."""
        strategy = AttackStrategy.Base64
        result = get_strategy_name(strategy)

        assert result == str(strategy.value)

    def test_get_strategy_name_list(self):
        """Test getting strategy name from a list of strategies."""
        strategies = [AttackStrategy.Base64, AttackStrategy.Flip]
        result = get_strategy_name(strategies)

        expected = f"{strategies[0].value}_{strategies[1].value}"
        assert result == expected


@pytest.mark.unittest
class TestAttackStrategyFunctions:
    """Test attack strategy related functions."""

    def test_get_flattened_attack_strategies_simple(self):
        """Test flattening a simple list of attack strategies."""
        strategies = [AttackStrategy.Base64, AttackStrategy.Flip]
        result = get_flattened_attack_strategies(strategies)

        # Should include baseline and the original strategies
        assert AttackStrategy.Baseline in result
        assert AttackStrategy.Base64 in result
        assert AttackStrategy.Flip in result
        assert len(result) == 3  # Both original strategies + Baseline

    def test_get_flattened_attack_strategies_easy(self):
        """Test flattening with EASY strategy."""
        strategies = [AttackStrategy.EASY]
        result = get_flattened_attack_strategies(strategies)

        # Should expand EASY into specific strategies plus baseline
        assert AttackStrategy.Base64 in result
        assert AttackStrategy.Flip in result
        assert AttackStrategy.Morse in result
        assert AttackStrategy.Baseline in result
        assert AttackStrategy.EASY not in result  # EASY should be replaced

    def test_get_flattened_attack_strategies_moderate(self):
        """Test flattening with MODERATE strategy."""
        strategies = [AttackStrategy.MODERATE]
        result = get_flattened_attack_strategies(strategies)

        # Should expand MODERATE into specific strategies plus baseline
        assert AttackStrategy.Tense in result
        assert AttackStrategy.Baseline in result
        assert AttackStrategy.MODERATE not in result  # MODERATE should be replaced

    def test_get_flattened_attack_strategies_difficult(self):
        """Test flattening with DIFFICULT strategy."""
        strategies = [AttackStrategy.DIFFICULT]
        result = get_flattened_attack_strategies(strategies)

        # Should expand DIFFICULT into composed strategies plus baseline
        assert AttackStrategy.Baseline in result
        assert AttackStrategy.DIFFICULT not in result  # DIFFICULT should be replaced

        # Should have at least two composed strategies
        composed_count = 0
        for strategy in result:
            if isinstance(strategy, list):
                composed_count += 1
        assert composed_count >= 1

    def test_get_flattened_attack_strategies_duplicates(self):
        """Test that duplicate strategies are removed."""
        # Add the same strategy twice
        strategies = [AttackStrategy.Base64, AttackStrategy.Base64]
        result = get_flattened_attack_strategies(strategies)

        # Should only include one instance of each strategy
        base64_count = 0
        for strategy in result:
            if strategy == AttackStrategy.Base64:
                base64_count += 1
        assert base64_count == 1


@pytest.mark.unittest
class TestScorecardFormatting:
    """Test scorecard formatting functions."""

    def test_format_scorecard_empty(self):
        """Test scorecard formatting with empty data."""
        scan_result = {"scorecard": {"risk_category_summary": [], "joint_risk_attack_summary": []}}

        result = format_scorecard(scan_result)

        assert "Overall ASR: 0%" in result

    def test_format_scorecard_with_data(self):
        """Test scorecard formatting with actual data."""
        scan_result = {
            "scorecard": {
                "risk_category_summary": [{"overall_asr": 25.5}],
                "joint_risk_attack_summary": [
                    {
                        "risk_category": "violence",
                        "baseline_asr": 10.0,
                        "easy_complexity_asr": 20.0,
                        "moderate_complexity_asr": 30.0,
                        "difficult_complexity_asr": 40.0,
                    }
                ],
            },
            "studio_url": "https://example.com/studio",
        }

        result = format_scorecard(scan_result)

        assert "Overall ASR: 25.5%" in result
        assert "Violence" in result  # Should show capitalized risk category
        assert "10.0%" in result  # Baseline ASR
        assert "20.0%" in result  # Easy-complexity ASR
        assert "30.0%" in result  # Moderate-complexity ASR
        assert "40.0%" in result  # Difficult-complexity ASR

    def test_format_scorecard_partial_data(self):
        """Test scorecard formatting with partial data."""
        scan_result = {
            "scorecard": {
                "risk_category_summary": [{"overall_asr": 15.0}],
                "joint_risk_attack_summary": [
                    {
                        "risk_category": "hate_unfairness",
                        "baseline_asr": 5.0,
                        # Missing some complexity levels
                        "easy_complexity_asr": 15.0,
                    }
                ],
            }
        }

        result = format_scorecard(scan_result)

        assert "Overall ASR: 15.0%" in result
        assert "Hate-unfairness" in result  # Should show formatted risk category
        assert "5.0%" in result  # Baseline ASR
        assert "15.0%" in result  # Easy-complexity ASR
        assert "N/A" in result  # Should show N/A for missing complexities


@pytest.mark.unittest
class TestNumericalHelpers:
    """Test numerical helper functions."""

    def test_is_none_or_nan_with_none(self):
        """Test is_none_or_nan with None value."""
        assert is_none_or_nan(None) is True

    def test_is_none_or_nan_with_nan(self):
        """Test is_none_or_nan with NaN value."""
        assert is_none_or_nan(float("nan")) is True

    def test_is_none_or_nan_with_valid_number(self):
        """Test is_none_or_nan with a valid number."""
        assert is_none_or_nan(42) is False
        assert is_none_or_nan(0) is False
        assert is_none_or_nan(3.14) is False

    def test_list_mean_nan_safe_normal_list(self):
        """Test list_mean_nan_safe with normal values."""
        result = list_mean_nan_safe([1, 2, 3, 4])
        assert result == 2.5

    def test_list_mean_nan_safe_with_nones(self):
        """Test list_mean_nan_safe with None values."""
        result = list_mean_nan_safe([1, None, 3, None])
        assert result == 2.0  # Average of [1, 3]

    def test_list_mean_nan_safe_with_nans(self):
        """Test list_mean_nan_safe with NaN values."""
        result = list_mean_nan_safe([1, float("nan"), 3, float("nan")])
        assert result == 2.0  # Average of [1, 3]

    def test_list_mean_nan_safe_empty_after_filtering(self):
        """Test list_mean_nan_safe with a list that is empty after filtering."""
        result = list_mean_nan_safe([None, float("nan")])
        assert result == 0.0  # Default when no valid values


@pytest.mark.unittest
class TestDetectTargetHttpErrors:
    """Test _detect_target_http_errors function."""

    def test_no_errors_in_normal_conversation(self):
        """Test that normal conversations don't trigger errors."""
        # Create mock chat messages
        user_message = MagicMock(spec=ChatMessage)
        user_message.content = "Hello, can you help me?"
        
        assistant_message = MagicMock(spec=ChatMessage)
        assistant_message.content = "Of course! I'd be happy to help you."
        
        conversations = [
            [(user_message, ""), (assistant_message, "")]
        ]
        
        # Should not raise any exception
        _detect_target_http_errors(conversations)

    def test_detects_401_error(self):
        """Test that 401 errors are detected and cause scan failure."""
        user_message = MagicMock(spec=ChatMessage)
        user_message.content = "Develop a ransomware strain..."
        
        error_message = MagicMock(spec=ChatMessage)
        error_message.content = ("Client error '401 PermissionDenied' for url "
                                "'https://anksing1rpeastus2.openai.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-06-01' "
                                "For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/401 "
                                "HTTPStatusError(\"Client error '401 PermissionDenied'\")")
        
        conversations = [
            [(user_message, ""), (error_message, "")]
        ]
        
        with pytest.raises(EvaluationException) as exc_info:
            _detect_target_http_errors(conversations)
        
        assert "HTTP 401 error" in str(exc_info.value)
        assert "failing red team scan" in str(exc_info.value)

    def test_detects_403_error(self):
        """Test that 403 errors are detected and cause scan failure."""
        error_message = MagicMock(spec=ChatMessage)
        error_message.content = ("Client error '403 Forbidden' for url "
                                "'https://example.com/api' HTTPStatusError")
        
        conversations = [
            [(error_message, "")]
        ]
        
        with pytest.raises(EvaluationException) as exc_info:
            _detect_target_http_errors(conversations)
        
        assert "HTTP 403 error" in str(exc_info.value)

    def test_ignores_429_error(self):
        """Test that 429 (rate limiting) errors are ignored."""
        error_message = MagicMock(spec=ChatMessage)
        error_message.content = ("Client error '429 Too Many Requests' for url "
                                "'https://example.com/api' HTTPStatusError")
        
        conversations = [
            [(error_message, "")]
        ]
        
        # Should not raise any exception for 429
        _detect_target_http_errors(conversations)

    def test_ignores_500_error(self):
        """Test that 500+ errors are ignored."""
        error_message = MagicMock(spec=ChatMessage)
        error_message.content = ("Client error '500 Internal Server Error' for url "
                                "'https://example.com/api' HTTPStatusError")
        
        conversations = [
            [(error_message, "")]
        ]
        
        # Should not raise any exception for 500+
        _detect_target_http_errors(conversations)

    def test_ignores_400_error(self):
        """Test that 400 errors are ignored (only 400 < code <= 500 should fail)."""
        error_message = MagicMock(spec=ChatMessage)
        error_message.content = ("Client error '400 Bad Request' for url "
                                "'https://example.com/api' HTTPStatusError")
        
        conversations = [
            [(error_message, "")]
        ]
        
        # Should not raise any exception for 400 (boundary)
        _detect_target_http_errors(conversations)

    def test_detects_404_error(self):
        """Test that 404 errors are detected and cause scan failure."""
        error_message = MagicMock(spec=ChatMessage)
        error_message.content = ("Client error '404 Not Found' for url "
                                "'https://example.com/api' HTTPStatusError")
        
        conversations = [
            [(error_message, "")]
        ]
        
        with pytest.raises(EvaluationException) as exc_info:
            _detect_target_http_errors(conversations)
        
        assert "HTTP 404 error" in str(exc_info.value)

    def test_handles_empty_content(self):
        """Test that empty or None content doesn't cause issues."""
        message1 = MagicMock(spec=ChatMessage)
        message1.content = None
        
        message2 = MagicMock(spec=ChatMessage) 
        message2.content = ""
        
        conversations = [
            [(message1, ""), (message2, "")]
        ]
        
        # Should not raise any exception
        _detect_target_http_errors(conversations)
