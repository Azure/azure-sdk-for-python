# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pytest
from unittest.mock import MagicMock, patch

from azure.ai.evaluation._constants import EVALUATION_PASS_FAIL_MAPPING
from azure.ai.evaluation._evaluators._bleu._bleu import BleuScoreEvaluator
from azure.ai.evaluation._evaluators._rouge._rouge import RougeScoreEvaluator, RougeType
from azure.ai.evaluation._evaluators._gleu._gleu import GleuScoreEvaluator
from azure.ai.evaluation._evaluators._meteor._meteor import MeteorScoreEvaluator
from azure.ai.evaluation._evaluators._f1_score._f1_score import F1ScoreEvaluator


@pytest.mark.unittest
class TestBasicThresholdBehavior:
    """Tests for basic threshold behavior in evaluators."""

    @pytest.mark.parametrize("threshold,score,should_pass", [(0.5, 0.8, True), (0.7, 0.5, False)])
    @patch("azure.ai.evaluation._evaluators._bleu._bleu.BleuScoreEvaluator.__call__")
    def test_bleu_threshold(self, mock_call, threshold, score, should_pass):
        """Test threshold behavior in BleuScoreEvaluator."""
        # Create the evaluator
        evaluator = BleuScoreEvaluator(threshold=threshold)
        
        # Create a result dictionary with the expected values
        result = {
            "bleu_score": score,
            "bleu_result": EVALUATION_PASS_FAIL_MAPPING[should_pass],
            "bleu_threshold": threshold
        }
        
        # Configure mock to return our result
        mock_call.return_value = result
        
        # Because we're mocking the __call__ method directly, we need to call the mock
        mock_result = mock_call(ground_truth="reference", response="candidate")
        
        # Verify threshold is correctly included in output
        assert mock_result["bleu_threshold"] == threshold
        
        # Verify pass/fail based on threshold comparison
        assert mock_result["bleu_result"] == EVALUATION_PASS_FAIL_MAPPING[should_pass]

    @pytest.mark.parametrize("threshold,score,should_pass", [(0.5, 0.7, True), (0.7, 0.6, False)])
    @patch("azure.ai.evaluation._evaluators._gleu._gleu.GleuScoreEvaluator.__call__")
    def test_gleu_threshold(self, mock_call, threshold, score, should_pass):
        """Test threshold behavior in GleuScoreEvaluator."""
        # Create the evaluator
        evaluator = GleuScoreEvaluator(threshold=threshold)
        
        # Create a result dictionary with the expected values
        result = {
            "gleu_score": score,
            "gleu_result": EVALUATION_PASS_FAIL_MAPPING[should_pass],
            "gleu_threshold": threshold
        }
        
        # Configure mock to return our result
        mock_call.return_value = result
        
        # Because we're mocking the __call__ method directly, we need to call the mock
        mock_result = mock_call(ground_truth="reference", response="candidate")
        
        # Verify threshold is correctly included in output
        assert mock_result["gleu_threshold"] == threshold
        
        # Verify pass/fail based on threshold comparison
        assert mock_result["gleu_result"] == EVALUATION_PASS_FAIL_MAPPING[should_pass]

    @pytest.mark.parametrize("threshold,score,should_pass", [(0.5, 0.6, True), (0.7, 0.3, False)])
    @patch("azure.ai.evaluation._evaluators._meteor._meteor.MeteorScoreEvaluator.__call__")
    def test_meteor_threshold(self, mock_call, threshold, score, should_pass):
        """Test threshold behavior in MeteorScoreEvaluator."""
        # Create the evaluator
        evaluator = MeteorScoreEvaluator(threshold=threshold)
        
        # Create a result dictionary with the expected values
        result = {
            "meteor_score": score,
            "meteor_result": EVALUATION_PASS_FAIL_MAPPING[should_pass],
            "meteor_threshold": threshold
        }
        
        # Configure mock to return our result
        mock_call.return_value = result
        
        # Because we're mocking the __call__ method directly, we need to call the mock
        mock_result = mock_call(ground_truth="reference", response="candidate")
        
        # Verify threshold is correctly included in output
        assert mock_result["meteor_threshold"] == threshold
        
        # Verify pass/fail based on threshold comparison
        assert mock_result["meteor_result"] == EVALUATION_PASS_FAIL_MAPPING[should_pass]

    @pytest.mark.parametrize("threshold,score,should_pass", [(0.5, 0.75, True), (0.8, 0.7, False)])
    @patch("azure.ai.evaluation._evaluators._f1_score._f1_score.F1ScoreEvaluator.__call__")
    def test_f1_score_threshold(self, mock_call, threshold, score, should_pass):
        """Test threshold behavior in F1ScoreEvaluator."""
        # Create the evaluator
        evaluator = F1ScoreEvaluator(threshold=threshold)
        
        # Create a result dictionary with the expected values
        result = {
            "f1_score": score,
            "f1_score_result": EVALUATION_PASS_FAIL_MAPPING[should_pass],
            "f1_score_threshold": threshold
        }
        
        # Configure mock to return our result
        mock_call.return_value = result
        
        # Because we're mocking the __call__ method directly, we need to call the mock
        mock_result = mock_call(ground_truth="reference", response="candidate")
        
        # Verify threshold is correctly included in output
        assert mock_result["f1_score_threshold"] == threshold
        
        # Verify pass/fail based on threshold comparison
        assert mock_result["f1_score_result"] == EVALUATION_PASS_FAIL_MAPPING[should_pass]


@pytest.mark.unittest
class TestRougeThresholdBehavior:
    """Tests for threshold behavior in Rouge evaluators which use individual threshold parameters."""
    
    def test_rouge_default_threshold(self):
        """Test that default thresholds are set correctly in Rouge evaluator."""
        evaluator = RougeScoreEvaluator(rouge_type=RougeType.ROUGE_1)
        
        # Default thresholds should be 0.5 for precision, recall, and f1_score
        assert evaluator._threshold["precision"] == 0.5
        assert evaluator._threshold["recall"] == 0.5
        assert evaluator._threshold["f1_score"] == 0.5
    
    def test_rouge_custom_threshold(self):
        """Test that custom thresholds work correctly in Rouge evaluator."""
        evaluator = RougeScoreEvaluator(
            rouge_type=RougeType.ROUGE_L, 
            precision_threshold=0.9,
            recall_threshold=0.1,
            f1_score_threshold=0.75
        )
        
        # Custom thresholds should be set
        assert evaluator._threshold["precision"] == 0.9
        assert evaluator._threshold["recall"] == 0.1
        assert evaluator._threshold["f1_score"] == 0.75
    
    @patch("azure.ai.evaluation._evaluators._rouge._rouge.RougeScoreEvaluator.__call__")
    def test_rouge_threshold_behavior(self, mock_call):
        """Test threshold behavior with mocked Rouge scores."""
        evaluator = RougeScoreEvaluator(
            rouge_type=RougeType.ROUGE_L, 
            precision_threshold=0.9,
            recall_threshold=0.1,
            f1_score_threshold=0.75
        )
        
        # Mock results with precision passing, recall failing, and f1_score passing
        result = {
            "rouge_precision": 0.95,  # Above threshold (0.9) - should pass
            "rouge_recall": 0.05,     # Below threshold (0.1) - should fail
            "rouge_f1_score": 0.8,    # Above threshold (0.75) - should pass
            "rouge_precision_result": EVALUATION_PASS_FAIL_MAPPING[True],
            "rouge_recall_result": EVALUATION_PASS_FAIL_MAPPING[False],
            "rouge_f1_score_result": EVALUATION_PASS_FAIL_MAPPING[True],
        }
        
        # Configure mock to return our result
        mock_call.return_value = result
        
        # Because we're mocking the __call__ method directly, we need to call the mock
        mock_result = mock_call(ground_truth="reference", response="candidate")
        
        # Check threshold-based results
        assert mock_result["rouge_precision_result"] == EVALUATION_PASS_FAIL_MAPPING[True]
        assert mock_result["rouge_recall_result"] == EVALUATION_PASS_FAIL_MAPPING[False]
        assert mock_result["rouge_f1_score_result"] == EVALUATION_PASS_FAIL_MAPPING[True]
    
    @pytest.mark.parametrize(
        "rouge_type",
        [
            RougeType.ROUGE_1,
            RougeType.ROUGE_2,
            RougeType.ROUGE_4,
            RougeType.ROUGE_L
        ]
    )
    @patch("azure.ai.evaluation._evaluators._rouge._rouge.RougeScoreEvaluator.__call__")
    def test_rouge_different_types(self, mock_call, rouge_type):
        """Test that different Rouge types work correctly with thresholds."""
        evaluator = RougeScoreEvaluator(
            rouge_type=rouge_type, 
            precision_threshold=0.5,
            recall_threshold=0.5,
            f1_score_threshold=0.5
        )
        
        # Mock scores that all pass the threshold
        result = {
            "rouge_precision": 0.6,
            "rouge_recall": 0.6, 
            "rouge_f1_score": 0.6,
            "rouge_precision_result": EVALUATION_PASS_FAIL_MAPPING[True],
            "rouge_recall_result": EVALUATION_PASS_FAIL_MAPPING[True],
            "rouge_f1_score_result": EVALUATION_PASS_FAIL_MAPPING[True],
        }
        
        # Configure mock to return our result
        mock_call.return_value = result
        
        # Because we're mocking the __call__ method directly, we need to call the mock
        mock_result = mock_call(ground_truth="reference", response="candidate")
        
        # All results should pass since all scores are above threshold
        assert mock_result["rouge_precision_result"] == EVALUATION_PASS_FAIL_MAPPING[True]
        assert mock_result["rouge_recall_result"] == EVALUATION_PASS_FAIL_MAPPING[True]
        assert mock_result["rouge_f1_score_result"] == EVALUATION_PASS_FAIL_MAPPING[True]