"""
Unit tests for red_team.utils.formatting_utils module.
"""

import pytest
import math
import json
import logging
from unittest.mock import patch, MagicMock, mock_open
from azure.ai.evaluation.red_team._utils.formatting_utils import (
    message_to_dict,
    get_strategy_name,
    get_flattened_attack_strategies,
    get_attack_success,
    format_scorecard,
    is_none_or_nan,
    list_mean_nan_safe,
    write_pyrit_outputs_to_file,
)
from azure.ai.evaluation.red_team._attack_strategy import AttackStrategy
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


def _make_mock_pieces(conversation_id, messages):
    """Create mock prompt request pieces for a conversation.

    :param conversation_id: The conversation ID to assign to all pieces
    :param messages: List of (role, content) tuples
    :return: List of mock PromptRequestPiece objects
    """
    pieces = []
    for role, content in messages:
        piece = MagicMock()
        piece.conversation_id = conversation_id
        piece.original_value = content
        piece.labels = {
            "context": "",
            "tool_calls": [],
            "risk_sub_type": None,
            "token_usage": None,
        }
        chat_msg = MagicMock(spec=ChatMessage)
        chat_msg.role = role
        chat_msg.content = content
        piece.to_chat_message.return_value = chat_msg
        pieces.append(piece)
    return pieces


@pytest.mark.unittest
class TestUnicodeJSONLRoundTrip:
    """Test that JSONL files with non-ASCII content survive write/read round-trips.

    Regression tests for the encoding bug where open() without encoding='utf-8'
    caused UnicodeDecodeError on Windows for UnicodeConfusable and CJK content.
    These tests exercise the production write_pyrit_outputs_to_file code path.
    """

    def test_jsonl_roundtrip_cjk_characters(self, tmp_path):
        """Test JSONL round-trip with CJK characters (Japanese, Chinese)."""
        output_path = str(tmp_path / "cjk_test.jsonl")
        pieces = _make_mock_pieces(
            "conv-cjk",
            [("user", "これはテストです"), ("assistant", "这是一个测试")],
        )
        mock_memory = MagicMock()
        mock_memory.get_prompt_request_pieces.return_value = pieces

        with patch("azure.ai.evaluation.red_team._utils.formatting_utils.CentralMemory") as mock_cm:
            mock_cm.get_memory_instance.return_value = mock_memory
            write_pyrit_outputs_to_file(
                output_path=output_path,
                logger=logging.getLogger("test"),
                prompt_to_context={},
            )

        with open(output_path, "r", encoding="utf-8") as f:
            data = json.loads(f.readline())
            assert data["conversation"]["messages"][0]["content"] == "これはテストです"
            assert data["conversation"]["messages"][1]["content"] == "这是一个测试"

    def test_jsonl_roundtrip_unicode_confusable(self, tmp_path):
        """Test JSONL round-trip with Unicode confusable characters."""
        output_path = str(tmp_path / "confusable_test.jsonl")
        confusable_text = "Ⓗⓔⓛⓛⓞ ⓦⓞⓡⓛⓓ"
        pieces = _make_mock_pieces(
            "conv-confusable",
            [("user", confusable_text), ("assistant", "I understand your request.")],
        )
        mock_memory = MagicMock()
        mock_memory.get_prompt_request_pieces.return_value = pieces

        with patch("azure.ai.evaluation.red_team._utils.formatting_utils.CentralMemory") as mock_cm:
            mock_cm.get_memory_instance.return_value = mock_memory
            write_pyrit_outputs_to_file(
                output_path=output_path,
                logger=logging.getLogger("test"),
                prompt_to_context={},
            )

        with open(output_path, "r", encoding="utf-8") as f:
            data = json.loads(f.readline())
            assert data["conversation"]["messages"][0]["content"] == confusable_text

    def test_jsonl_roundtrip_mixed_scripts(self, tmp_path):
        """Test JSONL round-trip with mixed scripts (Arabic, Cyrillic, emoji)."""
        output_path = str(tmp_path / "mixed_test.jsonl")
        pieces = _make_mock_pieces(
            "conv-mixed",
            [
                ("user", "مرحبا Привет 🔥 café"),
                ("assistant", "Multi-script response: αβγ"),
            ],
        )
        mock_memory = MagicMock()
        mock_memory.get_prompt_request_pieces.return_value = pieces

        with patch("azure.ai.evaluation.red_team._utils.formatting_utils.CentralMemory") as mock_cm:
            mock_cm.get_memory_instance.return_value = mock_memory
            write_pyrit_outputs_to_file(
                output_path=output_path,
                logger=logging.getLogger("test"),
                prompt_to_context={},
            )

        with open(output_path, "r", encoding="utf-8") as f:
            data = json.loads(f.readline())
            assert "مرحبا" in data["conversation"]["messages"][0]["content"]
            assert "αβγ" in data["conversation"]["messages"][1]["content"]
