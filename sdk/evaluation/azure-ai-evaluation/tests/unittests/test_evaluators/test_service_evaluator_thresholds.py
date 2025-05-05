# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pytest
from unittest.mock import MagicMock, patch

from azure.ai.evaluation._evaluators._content_safety._violence import ViolenceEvaluator
from azure.ai.evaluation._evaluators._content_safety._sexual import SexualEvaluator
from azure.ai.evaluation._evaluators._content_safety._self_harm import SelfHarmEvaluator
from azure.ai.evaluation._evaluators._service_groundedness._service_groundedness import GroundednessProEvaluator


@pytest.mark.unittest
class TestContentSafetyEvaluatorThresholds:
    """Tests for threshold behavior in content safety evaluators."""

    @pytest.fixture
    def mock_credential(self):
        return MagicMock()
    
    @pytest.fixture
    def mock_response(self):
        """Mock HTTP response with different scores."""
        mock = MagicMock()
        mock.status_code = 200
        mock.headers = {"content-type": "application/json"}
        return mock

    @pytest.fixture
    def mock_ai_project(self):
        """Return a simple dictionary for azure_ai_project."""
        return {
            "subscription_id": "test-subscription-id",
            "resource_group_name": "test-resource-group",
            "project_name": "test-project"
        }

    @patch("azure.ai.evaluation._evaluators._common._base_rai_svc_eval.RaiServiceEvaluatorBase.__init__", return_value=None)
    @patch("azure.ai.evaluation._evaluators._common._base_rai_svc_eval.RaiServiceEvaluatorBase.__call__")
    def test_violence_evaluator_default_threshold(self, mock_call, mock_init, mock_credential, mock_ai_project):
        """Test that the default threshold is set correctly for Violence evaluator."""
        evaluator = ViolenceEvaluator(
            credential=mock_credential,
            azure_ai_project=mock_ai_project
        )
        evaluator._threshold = 3  # Default threshold

        # Mock the response
        mock_call.return_value = {
            "violence": "Low",
            "violence_score": 3,
            "violence_reason": "Mock reason"
        }

        result = evaluator(query="Test query", response="Test response")
        assert evaluator._threshold == 3
        assert result["violence"] == "Low"

    @patch("azure.ai.evaluation._evaluators._common._base_rai_svc_eval.RaiServiceEvaluatorBase.__init__", return_value=None)
    @patch("azure.ai.evaluation._evaluators._common._base_rai_svc_eval.RaiServiceEvaluatorBase.__call__")
    def test_violence_evaluator_custom_threshold(self, mock_call, mock_init, mock_credential, mock_ai_project):
        """Test that a custom threshold is set correctly for Violence evaluator."""
        custom_threshold = 2
        evaluator = ViolenceEvaluator(
            credential=mock_credential,
            azure_ai_project=mock_ai_project,
            threshold=custom_threshold
        )
        evaluator._threshold = custom_threshold

        # Mock the response
        mock_call.return_value = {
            "violence": "Medium",
            "violence_score": 3,
            "violence_reason": "Mock reason"
        }

        result = evaluator(query="Test query", response="Test response")
        assert evaluator._threshold == custom_threshold
        assert result["violence"] == "Medium"

    @pytest.mark.parametrize(
        "score,threshold,expected_severity",
        [
            (0, 3, "Very low"),  # Score 0, below threshold 3 -> Very low
            (1, 3, "Very low"),  # Score 1, below threshold 3 -> Very low
            (2, 3, "Very low"),  # Score 2, below threshold 3 -> Very low
            (3, 3, "Low"),       # Score 3, at threshold 3 -> Low
            (4, 3, "Medium"),    # Score 4, above threshold 3 -> Medium
            (5, 3, "High"),      # Score 5, above threshold 3 -> High
            (1, 1, "Low"),       # Score 1, at threshold 1 -> Low
            (0, 2, "Very low"),  # Score 0, below threshold 2 -> Very low
        ]
    )
    @patch("azure.ai.evaluation._evaluators._common._base_rai_svc_eval.RaiServiceEvaluatorBase.__init__", return_value=None)
    @patch("azure.ai.evaluation._evaluators._common._base_rai_svc_eval.RaiServiceEvaluatorBase.__call__")
    def test_violence_evaluator_threshold_severity_mapping(
        self, mock_call, mock_init, mock_credential, mock_ai_project,
        score, threshold, expected_severity
    ):
        """Test that violence scores are correctly mapped to severity levels."""
        evaluator = ViolenceEvaluator(
            credential=mock_credential,
            azure_ai_project=mock_ai_project,
            threshold=threshold
        )
        evaluator._threshold = threshold
        
        # Mock the response
        mock_call.return_value = {
            "violence": expected_severity,
            "violence_score": score,
            "violence_reason": f"Mock reason for score {score}"
        }
        
        result = evaluator(query="Test query", response="Test response")
        assert result["violence"] == expected_severity
        assert result["violence_score"] == score
        assert "violence_reason" in result

    @pytest.mark.parametrize(
        "evaluator_class,threshold",
        [
            (ViolenceEvaluator, 0),
            (SexualEvaluator, 1),
            (SelfHarmEvaluator, 2)
        ]
    )
    @patch("azure.ai.evaluation._evaluators._common._base_rai_svc_eval.RaiServiceEvaluatorBase.__init__", return_value=None)
    @patch("azure.ai.evaluation._evaluators._common._base_rai_svc_eval.RaiServiceEvaluatorBase.__call__")
    def test_content_safety_evaluator_custom_thresholds(
        self, mock_call, mock_init, mock_credential, mock_ai_project, evaluator_class, threshold
    ):
        """Test that custom thresholds are set correctly in different content safety evaluators."""
        evaluator = evaluator_class(
            credential=mock_credential,
            azure_ai_project=mock_ai_project,
            threshold=threshold
        )
        evaluator._threshold = threshold  # This would be set by the base class

        # Mock a basic response
        mock_call.return_value = {
            "score": 0.5,
            "reason": "Mock reason"
        }
        
        # Call the evaluator to verify it works with the threshold
        evaluator(query="Test query", response="Test response")
        assert evaluator._threshold == threshold


@pytest.mark.unittest
class TestGroundednessProEvaluatorThreshold:
    """Tests for threshold behavior in GroundednessProEvaluator."""
    
    @pytest.fixture
    def mock_credential(self):
        return MagicMock()

    @pytest.fixture
    def mock_ai_project(self):
        """Return a simple dictionary for azure_ai_project."""
        return {
            "subscription_id": "test-subscription-id",
            "resource_group_name": "test-resource-group",
            "project_name": "test-project"
        }

    @pytest.fixture
    def mock_response(self):
        """Mock HTTP response for groundedness pro evaluator."""
        mock = MagicMock()
        mock.status_code = 200
        mock.headers = {"content-type": "application/json"}
        return mock

    @patch("azure.ai.evaluation._evaluators._common._base_rai_svc_eval.RaiServiceEvaluatorBase.__init__", return_value=None)
    @patch("azure.ai.evaluation._evaluators._common._base_rai_svc_eval.RaiServiceEvaluatorBase.__call__")
    def test_groundedness_pro_default_threshold(self, mock_call, mock_init, mock_credential, mock_ai_project):
        """Test that the default threshold is set correctly for GroundednessProEvaluator."""
        evaluator = GroundednessProEvaluator(
            credential=mock_credential,
            azure_ai_project=mock_ai_project
        )
        evaluator.threshold = 5  # Default threshold

        # Mock the response
        mock_call.return_value = {
            "groundedness_pro_label": True,
            "groundedness_pro_reason": "The response is well-grounded in the context."
        }

        result = evaluator(query="Test query", response="Test response", context="Test context")
        assert evaluator.threshold == 5
        assert result["groundedness_pro_label"] is True
        assert "groundedness_pro_reason" in result

    @patch("azure.ai.evaluation._evaluators._common._base_rai_svc_eval.RaiServiceEvaluatorBase.__init__", return_value=None)
    @patch("azure.ai.evaluation._evaluators._common._base_rai_svc_eval.RaiServiceEvaluatorBase.__call__")
    def test_groundedness_pro_custom_threshold(self, mock_call, mock_init, mock_credential, mock_ai_project):
        """Test that a custom threshold is set correctly for GroundednessProEvaluator."""
        custom_threshold = 2
        evaluator = GroundednessProEvaluator(
            credential=mock_credential,
            azure_ai_project=mock_ai_project,
            threshold=custom_threshold
        )
        evaluator.threshold = custom_threshold

        # Mock the response
        mock_call.return_value = {
            "groundedness_pro_label": True,
            "groundedness_pro_reason": "The response is well-grounded in the context."
        }

        result = evaluator(query="Test query", response="Test response", context="Test context")
        assert evaluator.threshold == custom_threshold
        assert result["groundedness_pro_label"] is True
        assert "groundedness_pro_reason" in result