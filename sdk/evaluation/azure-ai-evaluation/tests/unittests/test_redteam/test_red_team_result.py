"""
Unit tests for red_team_result module.
"""

import pytest
import json
from unittest.mock import patch, MagicMock

from azure.ai.evaluation.red_team._red_team_result import (
    RedTeamResult,
)


@pytest.fixture(scope="function")
def mock_scorecard():
    """Mock scorecard data for testing."""
    return {
        "risk_category_summary": [
            {
                "overall_asr": 25.5,
                "overall_total": 100,
                "overall_successful_attacks": 25,
                "violence_asr": 30.0,
                "violence_total": 50,
                "violence_successful_attacks": 15
            }
        ],
        "attack_technique_summary": [
            {
                "overall_asr": 25.5,
                "overall_total": 100,
                "overall_successful_attacks": 25,
                "baseline_asr": 10.0,
                "baseline_total": 20,
                "baseline_successful_attacks": 2,
                "easy_complexity_asr": 20.0,
                "easy_complexity_total": 30,
                "easy_complexity_successful_attacks": 6
            }
        ],
        "joint_risk_attack_summary": [
            {
                "risk_category": "violence",
                "baseline_asr": 10.0,
                "easy_complexity_asr": 20.0,
                "moderate_complexity_asr": 30.0,
                "difficult_complexity_asr": 40.0
            }
        ],
        "detailed_joint_risk_attack_asr": {
            "easy": {
                "violence": {
                    "Base64Converter_ASR": 15.0,
                    "FlipConverter_ASR": 25.0
                }
            }
        }
    }


@pytest.fixture(scope="function")
def mock_parameters():
    """Mock parameters data for testing."""
    return {
        "attack_objective_generated_from": {
            "application_scenario": "Test scenario",
            "risk_categories": ["violence", "hate_unfairness"],
            "custom_attack_seed_prompts": "",
            "policy_document": ""
        },
        "attack_complexity": ["Easy", "Difficult"],
        "techniques_used": {
            "easy": ["Base64Converter", "FlipConverter"],
            "difficult": ["CharSwapGenerator"]
        }
    }


@pytest.fixture(scope="function")
def mock_conversation():
    """Mock conversation data for testing."""
    return {
        "attack_success": True,
        "attack_technique": "Base64Converter",
        "attack_complexity": "easy",
        "risk_category": "violence",
        "conversation": [
            {"role": "user", "content": "Test attack message"},
            {"role": "assistant", "content": "Test harmful response"}
        ],
        "risk_assessment": {
            "violence": {
                "severity_label": "high",
                "reason": "Contains explicit violence"
            }
        }
    }


@pytest.mark.unittest
class TestRedTeamResultInitialization:
    """Test RedTeamResult initialization."""

    def test_output_initialization(self):
        """Test that RedTeamResult initializes correctly."""
        output = RedTeamResult()
        assert output.scan_result is None
        assert output.attack_details is None
        
        # Test with data
        mock_result = {"test": "data"}
        mock_data = [{"conversation": []}]
        output_with_data = RedTeamResult(scan_result=mock_result, attack_details=mock_data)
        assert output_with_data.scan_result == mock_result
        assert output_with_data.attack_details == mock_data


@pytest.mark.unittest
class TestRedTeamResultMethods:
    """Test RedTeamResult methods."""

    def test_to_json(self, mock_scorecard, mock_parameters, mock_conversation):
        """Test to_json method of RedTeamResult."""
        mock_result = {
            "scorecard": mock_scorecard,
            "parameters": mock_parameters,
            "attack_details": [mock_conversation],
            "studio_url": "https://example.com/studio"
        }
        
        output = RedTeamResult(scan_result=mock_result)
        json_str = output.to_json()
        
        # Parse JSON to verify it's valid
        json_data = json.loads(json_str)
        assert "scorecard" in json_data
        assert "parameters" in json_data
        assert "attack_details" in json_data
        assert "studio_url" in json_data

    def test_to_json_empty(self):
        """Test to_json method with empty result."""
        output = RedTeamResult()
        json_str = output.to_json()
        assert json_str == ""

    def test_to_scorecard(self, mock_scorecard):
        """Test to_scorecard method of RedTeamResult."""
        mock_result = {"scorecard": mock_scorecard}
        output = RedTeamResult(scan_result=mock_result)
        
        scorecard = output.to_scorecard()
        assert scorecard == mock_scorecard

    def test_to_scorecard_none(self):
        """Test to_scorecard method with no result."""
        output = RedTeamResult()
        scorecard = output.to_scorecard()
        assert scorecard is None


@pytest.mark.unittest
class TestRedTeamResultConversion:
    """Test RedTeamResult conversion methods."""

    def test_to_eval_qr_json_lines_with_data(self, mock_conversation):
        """Test to_eval_qr_json_lines method with data."""
        output = RedTeamResult(attack_details=[mock_conversation])
        json_lines = output.to_eval_qr_json_lines()
        
        # Should have one valid JSON line
        json_data = json.loads(json_lines[0])
        assert json_data["query"] == "Test attack message"
        assert json_data["response"] == "Test harmful response"
        assert json_data["attack_strategy"] == "Base64Converter"
        assert json_data["attack_complexity"] == "easy"
        assert json_data["risk_category"] == "violence"
        assert json_data["attack_success"] == "true"
        assert json_data["category"] == "violence"
        assert json_data["severity_level"] == "high"

    def test_to_eval_qr_json_lines_multiple_messages(self):
        """Test to_eval_qr_json_lines with multiple messages in conversation."""
        mock_multi_turn = {
            "attack_success": True,
            "attack_technique": "Base64Converter",
            "attack_complexity": "easy",
            "risk_category": "violence",
            "conversation": [
                {"role": "user", "content": "First message"},
                {"role": "assistant", "content": "First response"},
                {"role": "user", "content": "Second message"},
                {"role": "assistant", "content": "Second response"}
            ]
        }
        
        output = RedTeamResult(attack_details=[mock_multi_turn])
        lines = output.to_eval_qr_json_lines()
        
        assert len(lines) == 2
        
        first_turn = json.loads(lines[0])
        assert first_turn["query"] == "First message"
        assert first_turn["response"] == "First response"
        
        second_turn = json.loads(lines[1])
        assert second_turn["query"] == "Second message"
        assert second_turn["response"] == "Second response"

    def test_to_eval_qr_json_lines_empty(self):
        """Test to_eval_qr_json_lines method with no data."""
        output = RedTeamResult()
        json_lines = output.to_eval_qr_json_lines()
        assert json_lines == ''


@pytest.mark.unittest
class TestRedTeamResultRendering:
    """Test RedTeamResult rendering methods."""

    def test_attack_simulation_with_data(self, mock_conversation):
        """Test attack_simulation method with data."""
        output = RedTeamResult(attack_details=[mock_conversation])
        simulation_text = output.attack_simulation()
        
        # Check for expected parts of the output
        assert "Attack Technique: Base64Converter" in simulation_text
        assert "Attack Complexity: easy" in simulation_text
        assert "Risk Category: violence" in simulation_text
        assert "User: Test attack message" in simulation_text
        assert "Assistant: Test harmful response" in simulation_text
        assert "Attack Success: Successful" in simulation_text
        assert "Category: violence" in simulation_text
        assert "Severity Level: high" in simulation_text

    def test_attack_simulation_no_data(self):
        """Test attack_simulation method with no data."""
        output = RedTeamResult()
        simulation_text = output.attack_simulation()
        assert simulation_text == ""

    def test_attack_simulation_with_failed_attack(self):
        """Test attack_simulation method with a failed attack."""
        mock_failed = {
            "attack_success": False,
            "attack_technique": "Base64Converter",
            "attack_complexity": "easy",
            "risk_category": "violence",
            "conversation": [
                {"role": "user", "content": "Test attack message"},
                {"role": "assistant", "content": "Safe response"}
            ]
        }
        
        output = RedTeamResult(attack_details=[mock_failed])
        simulation_text = output.attack_simulation()
        
        assert "Attack Success: Failed" in simulation_text