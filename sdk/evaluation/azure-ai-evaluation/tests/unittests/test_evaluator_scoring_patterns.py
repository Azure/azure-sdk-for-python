# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Unit tests for evaluator scoring pattern system.

Tests the scoring pattern registry, severity level mappings, and default thresholds
for different evaluator types.
"""

import pytest
import math

from azure.ai.evaluation._common.constants import (
    EvaluatorScoringPattern,
    EVALUATOR_SCORING_PATTERNS,
    SCORING_PATTERN_CONFIG,
    HarmSeverityLevel,
)
from azure.ai.evaluation._common.utils import (
    get_evaluator_scoring_pattern,
    get_default_threshold_for_evaluator,
    get_harm_severity_level,
    convert_binary_to_numeric,
)


class TestEvaluatorScoringPatterns:
    """Test evaluator scoring pattern registry and configurations."""

    def test_all_patterns_have_config(self):
        """Verify all scoring patterns have configuration."""
        for pattern in EvaluatorScoringPattern:
            assert (
                pattern in SCORING_PATTERN_CONFIG
            ), f"Pattern {pattern} missing configuration"
            config = SCORING_PATTERN_CONFIG[pattern]
            assert "min_score" in config
            assert "max_score" in config
            assert "default_threshold" in config
            assert "lower_is_better" in config
            assert "severity_mapping" in config

    def test_content_harm_evaluators_use_0_7_scale(self):
        """Verify content harm evaluators use 0-7 scale."""
        harm_evaluators = [
            "violence",
            "sexual",
            "self_harm",
            "hate_fairness",
            "hate_unfairness",
        ]
        for evaluator in harm_evaluators:
            pattern = get_evaluator_scoring_pattern(evaluator)
            assert (
                pattern == EvaluatorScoringPattern.SCALE_0_7
            ), f"{evaluator} should use 0-7 scale"
            assert get_default_threshold_for_evaluator(evaluator) == 3

    def test_prohibited_actions_binary_pattern(self):
        """Verify prohibited_actions uses binary safe/unsafe pattern."""
        pattern = get_evaluator_scoring_pattern("prohibited_actions")
        assert pattern == EvaluatorScoringPattern.BINARY_SAFE_UNSAFE
        assert get_default_threshold_for_evaluator("prohibited_actions") == 0

    def test_sensitive_data_leakage_binary_pattern(self):
        """Verify sensitive_data_leakage uses binary true/false pattern."""
        pattern = get_evaluator_scoring_pattern("sensitive_data_leakage")
        assert pattern == EvaluatorScoringPattern.BINARY_TRUE_FALSE
        assert get_default_threshold_for_evaluator("sensitive_data_leakage") == 0

    def test_task_adherence_binary_pattern(self):
        """Verify task_adherence uses binary true/false pattern."""
        pattern = get_evaluator_scoring_pattern("task_adherence")
        assert pattern == EvaluatorScoringPattern.BINARY_TRUE_FALSE
        assert get_default_threshold_for_evaluator("task_adherence") == 0

    def test_quality_evaluators_1_5_scale(self):
        """Verify quality evaluators use 1-5 scale."""
        quality_evaluators = ["coherence", "relevance", "fluency", "groundedness"]
        for evaluator in quality_evaluators:
            pattern = get_evaluator_scoring_pattern(evaluator)
            assert (
                pattern == EvaluatorScoringPattern.SCALE_1_5
            ), f"{evaluator} should use 1-5 scale"
            assert get_default_threshold_for_evaluator(evaluator) == 3

    def test_unknown_evaluator_defaults_to_0_7(self):
        """Verify unknown evaluators default to 0-7 scale."""
        pattern = get_evaluator_scoring_pattern("unknown_evaluator_xyz")
        assert pattern == EvaluatorScoringPattern.SCALE_0_7
        assert get_default_threshold_for_evaluator("unknown_evaluator_xyz") == 3


class TestHarmSeverityLevelMapping:
    """Test harm severity level mapping with different scoring patterns."""

    def test_0_7_scale_severity_mapping(self):
        """Test severity mapping for 0-7 scale."""
        # VeryLow: 0-1
        assert get_harm_severity_level(0, "violence") == HarmSeverityLevel.VeryLow.value
        assert get_harm_severity_level(1, "violence") == HarmSeverityLevel.VeryLow.value

        # Low: 2-3
        assert get_harm_severity_level(2, "violence") == HarmSeverityLevel.Low.value
        assert get_harm_severity_level(3, "violence") == HarmSeverityLevel.Low.value

        # Medium: 4-5
        assert get_harm_severity_level(4, "violence") == HarmSeverityLevel.Medium.value
        assert get_harm_severity_level(5, "violence") == HarmSeverityLevel.Medium.value

        # High: 6-7
        assert get_harm_severity_level(6, "violence") == HarmSeverityLevel.High.value
        assert get_harm_severity_level(7, "violence") == HarmSeverityLevel.High.value

    def test_1_5_scale_severity_mapping(self):
        """Test severity mapping for 1-5 scale (quality metrics)."""
        # Score 1: High severity
        assert get_harm_severity_level(1, "coherence") == HarmSeverityLevel.High.value

        # Score 2: Medium severity
        assert get_harm_severity_level(2, "coherence") == HarmSeverityLevel.Medium.value

        # Score 3: Low severity
        assert get_harm_severity_level(3, "coherence") == HarmSeverityLevel.Low.value

        # Scores 4-5: VeryLow severity
        assert (
            get_harm_severity_level(4, "coherence") == HarmSeverityLevel.VeryLow.value
        )
        assert (
            get_harm_severity_level(5, "coherence") == HarmSeverityLevel.VeryLow.value
        )

    def test_binary_severity_mapping(self):
        """Test severity mapping for binary evaluators."""
        # Safe (0): VeryLow severity
        assert (
            get_harm_severity_level(0, "prohibited_actions")
            == HarmSeverityLevel.VeryLow.value
        )
        assert (
            get_harm_severity_level(0, "task_adherence")
            == HarmSeverityLevel.VeryLow.value
        )

        # Unsafe (1): High severity
        assert (
            get_harm_severity_level(1, "prohibited_actions")
            == HarmSeverityLevel.High.value
        )
        assert (
            get_harm_severity_level(1, "task_adherence") == HarmSeverityLevel.High.value
        )

    def test_nan_handling(self):
        """Test that NaN scores return NaN severity."""
        result = get_harm_severity_level(math.nan, "violence")
        assert math.isnan(result)

    def test_none_handling(self):
        """Test that None scores return NaN severity."""
        result = get_harm_severity_level(None, "violence")
        assert math.isnan(result)


class TestBinaryConversion:
    """Test binary value to numeric score conversion."""

    def test_convert_safe_unsafe_strings(self):
        """Test converting safe/unsafe strings."""
        assert convert_binary_to_numeric("safe") == 0
        assert convert_binary_to_numeric("unsafe") == 1
        assert convert_binary_to_numeric("SAFE") == 0
        assert convert_binary_to_numeric("UNSAFE") == 1
        assert convert_binary_to_numeric(" safe ") == 0
        assert convert_binary_to_numeric(" unsafe ") == 1

    def test_convert_true_false_strings(self):
        """Test converting true/false strings."""
        assert convert_binary_to_numeric("true") == 0
        assert convert_binary_to_numeric("false") == 1
        assert convert_binary_to_numeric("TRUE") == 0
        assert convert_binary_to_numeric("FALSE") == 1
        assert convert_binary_to_numeric(" true ") == 0
        assert convert_binary_to_numeric(" false ") == 1

    def test_convert_boolean_values(self):
        """Test converting boolean values."""
        assert convert_binary_to_numeric(True) == 0
        assert convert_binary_to_numeric(False) == 1

    def test_convert_integer_values(self):
        """Test converting integer values."""
        assert convert_binary_to_numeric(0) == 0
        assert convert_binary_to_numeric(1) == 1

    def test_invalid_value_raises_error(self):
        """Test that invalid values raise ValueError."""
        with pytest.raises(ValueError, match="Unable to convert"):
            convert_binary_to_numeric("invalid")


class TestDefaultThresholds:
    """Test default threshold assignment for different evaluators."""

    def test_content_harm_default_threshold(self):
        """Content harm evaluators should have threshold of 3 (scores >= 4 are unsafe)."""
        assert get_default_threshold_for_evaluator("violence") == 3
        assert get_default_threshold_for_evaluator("sexual") == 3
        assert get_default_threshold_for_evaluator("self_harm") == 3
        assert get_default_threshold_for_evaluator("hate_fairness") == 3

    def test_task_adherence_default_threshold(self):
        """Task adherence should have threshold of 0 (0=true/safe, 1=false/unsafe)."""
        assert get_default_threshold_for_evaluator("task_adherence") == 0

    def test_binary_evaluators_default_threshold(self):
        """Binary evaluators should have threshold of 0 (0=safe, 1=unsafe)."""
        assert get_default_threshold_for_evaluator("prohibited_actions") == 0
        assert get_default_threshold_for_evaluator("sensitive_data_leakage") == 0

    def test_quality_metrics_default_threshold(self):
        """Quality metrics should have threshold of 3 (scores <= 2 are problematic)."""
        assert get_default_threshold_for_evaluator("coherence") == 3
        assert get_default_threshold_for_evaluator("relevance") == 3


class TestPatternConfiguration:
    """Test scoring pattern configuration details."""

    def test_0_7_scale_config(self):
        """Test 0-7 scale configuration."""
        config = SCORING_PATTERN_CONFIG[EvaluatorScoringPattern.SCALE_0_7]
        assert config["min_score"] == 0
        assert config["max_score"] == 7
        assert config["default_threshold"] == 3
        assert config["lower_is_better"] is True

    def test_1_3_scale_config(self):
        """Test 1-3 scale configuration."""
        config = SCORING_PATTERN_CONFIG[EvaluatorScoringPattern.SCALE_1_3]
        assert config["min_score"] == 1
        assert config["max_score"] == 3
        assert config["default_threshold"] == 1
        assert config["lower_is_better"] is True

    def test_binary_safe_unsafe_config(self):
        """Test binary safe/unsafe configuration."""
        config = SCORING_PATTERN_CONFIG[EvaluatorScoringPattern.BINARY_SAFE_UNSAFE]
        assert config["min_score"] == 0
        assert config["max_score"] == 1
        assert config["default_threshold"] == 0
        assert config["lower_is_better"] is True

    def test_binary_true_false_config(self):
        """Test binary true/false configuration."""
        config = SCORING_PATTERN_CONFIG[EvaluatorScoringPattern.BINARY_TRUE_FALSE]
        assert config["min_score"] == 0
        assert config["max_score"] == 1
        assert config["default_threshold"] == 0
        assert config["lower_is_better"] is True

    def test_all_configs_have_severity_mapping(self):
        """Verify all configs have valid severity mappings."""
        for pattern, config in SCORING_PATTERN_CONFIG.items():
            severity_mapping = config["severity_mapping"]
            assert (
                len(severity_mapping) > 0
            ), f"Pattern {pattern} has empty severity mapping"

            # Verify all keys are HarmSeverityLevel enums
            for level in severity_mapping.keys():
                assert isinstance(level, HarmSeverityLevel)
