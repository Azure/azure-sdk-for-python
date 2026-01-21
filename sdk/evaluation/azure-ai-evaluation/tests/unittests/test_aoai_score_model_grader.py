# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
Comprehensive unit tests for AzureOpenAIScoreModelGrader.
This test suite covers initialization scenarios, edge cases, validation logic,
error handling, registry integration, and usage patterns.
"""

import pytest
from unittest.mock import patch, AsyncMock

from azure.ai.evaluation import AzureOpenAIModelConfiguration
from azure.ai.evaluation._aoai.score_model_grader import AzureOpenAIScoreModelGrader
from azure.ai.evaluation._evaluate._evaluate_aoai import (
    _split_evaluators_and_grader_configs,
    _convert_remote_eval_params_to_grader,
)


def _sampling_params_as_dict(value):
    """Normalize sampling params to a plain dictionary for assertions."""

    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump(exclude_none=True)
    if hasattr(value, "dict"):
        return value.dict(exclude_none=True)
    if hasattr(value, "__dict__"):
        return {
            k: v
            for k, v in vars(value).items()
            if v is not None and not k.startswith("_")
        }
    return value


@pytest.fixture
def mock_aoai_model_config():
    """Mock Azure OpenAI model configuration for testing."""
    return AzureOpenAIModelConfiguration(
        azure_deployment="test-deployment",
        azure_endpoint="https://test-endpoint.openai.azure.com/",
        api_key="test-api-key",
        api_version="2024-12-01-preview",
    )


@pytest.fixture
def basic_score_grader_config():
    """Basic configuration for score model grader."""
    return {
        "name": "Test Score Grader",
        "model": "gpt-4o-mini",
        "input": [
            {
                "role": "system",
                "content": "You are a test evaluator. Rate from 0.0 to 1.0.",
            },
            {
                "role": "user",
                "content": "Rate this conversation: {{ item.conversation }}",
            },
        ],
        "range": [0.0, 1.0],
        "pass_threshold": 0.5,
        "sampling_params": {"temperature": 0.0, "max_tokens": 100},
    }


@pytest.mark.unittest
class TestAzureOpenAIScoreModelGrader:
    """Test suite for AzureOpenAIScoreModelGrader."""

    def test_grader_initialization_valid_config(
        self, mock_aoai_model_config, basic_score_grader_config
    ):
        """Test successful grader initialization with valid configuration."""
        grader = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config, **basic_score_grader_config
        )

        assert grader is not None
        assert grader.id == AzureOpenAIScoreModelGrader.id
        assert grader._model_config == mock_aoai_model_config
        assert grader._grader_config.name == "Test Score Grader"
        assert grader._grader_config.model == "gpt-4o-mini"
        assert grader._grader_config.range == [0.0, 1.0]
        assert grader.pass_threshold == 0.5

    def test_grader_initialization_minimal_config(self, mock_aoai_model_config):
        """Test grader initialization with minimal required configuration."""
        minimal_config = {
            "name": "Minimal Grader",
            "model": "gpt-4",
            "input": [{"role": "user", "content": "Rate this: {{ item.data }}"}],
        }

        grader = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config, **minimal_config
        )

        assert grader is not None
        assert grader._grader_config.name == "Minimal Grader"
        assert grader._grader_config.range == [0.0, 1.0]  # Default range
        assert grader.pass_threshold == 0.5  # Default threshold

    def test_grader_initialization_missing_model_config(
        self, basic_score_grader_config
    ):
        """Test that grader initialization fails without model config."""
        with pytest.raises(TypeError):
            AzureOpenAIScoreModelGrader(**basic_score_grader_config)

    def test_grader_initialization_invalid_model_config(
        self, basic_score_grader_config
    ):
        """Test grader initialization with invalid model config."""
        bad_model_config = AzureOpenAIModelConfiguration(
            azure_deployment="test-deployment",
            azure_endpoint="https://test-endpoint.openai.azure.com/",
            # Missing api_key
        )

        with pytest.raises(Exception) as excinfo:
            AzureOpenAIScoreModelGrader(
                model_config=bad_model_config, **basic_score_grader_config
            )

        assert "api_key" in str(excinfo.value)

    def test_grader_initialization_missing_required_fields(
        self, mock_aoai_model_config
    ):
        """Test grader initialization fails with missing required fields."""
        # Missing name
        with pytest.raises(TypeError):
            AzureOpenAIScoreModelGrader(
                model_config=mock_aoai_model_config,
                model="gpt-4",
                input=[{"role": "user", "content": "test"}],
            )

        # Missing model
        with pytest.raises(TypeError):
            AzureOpenAIScoreModelGrader(
                model_config=mock_aoai_model_config,
                name="Test",
                input=[{"role": "user", "content": "test"}],
            )

        # Missing input
        with pytest.raises(TypeError):
            AzureOpenAIScoreModelGrader(
                model_config=mock_aoai_model_config, name="Test", model="gpt-4"
            )

    def test_grader_initialization_invalid_range(self, mock_aoai_model_config):
        """Test grader initialization with invalid range values."""
        config = {
            "name": "Test Grader",
            "model": "gpt-4",
            "input": [{"role": "user", "content": "test"}],
            "range": [1.0, 0.0],  # Invalid: min > max
        }

        with pytest.raises(ValueError) as excinfo:
            AzureOpenAIScoreModelGrader(model_config=mock_aoai_model_config, **config)

        assert "range" in str(excinfo.value).lower()

    def test_grader_initialization_invalid_threshold(self, mock_aoai_model_config):
        """Test grader initialization with invalid pass threshold."""
        config = {
            "name": "Test Grader",
            "model": "gpt-4",
            "input": [{"role": "user", "content": "test"}],
            "range": [0.0, 1.0],
            "pass_threshold": 1.5,  # Outside range
        }

        with pytest.raises(ValueError) as excinfo:
            AzureOpenAIScoreModelGrader(model_config=mock_aoai_model_config, **config)

        assert "pass_threshold" in str(excinfo.value).lower()

    def test_grader_validation_bypass(self, basic_score_grader_config):
        """Test that validation can be bypassed for testing purposes."""
        bad_model_config = AzureOpenAIModelConfiguration(
            azure_deployment="test-deployment",
            azure_endpoint="https://test-endpoint.openai.azure.com/",
            # Missing api_key
        )

        # Should not raise exception when validate=False
        grader = AzureOpenAIScoreModelGrader(
            model_config=bad_model_config, validate=False, **basic_score_grader_config
        )

        assert grader is not None

    def test_grader_registry_integration(
        self, mock_aoai_model_config, basic_score_grader_config
    ):
        """Test that score model grader integrates with the grader registry."""
        grader = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config, **basic_score_grader_config
        )

        # Test grader conversion
        init_params = {
            "model_config": mock_aoai_model_config,
            **basic_score_grader_config,
        }

        converted_grader = _convert_remote_eval_params_to_grader(
            AzureOpenAIScoreModelGrader.id, init_params=init_params
        )

        assert isinstance(converted_grader, AzureOpenAIScoreModelGrader)
        assert converted_grader._model_config == mock_aoai_model_config

    def test_grader_split_recognition(
        self, mock_aoai_model_config, basic_score_grader_config
    ):
        """Test that score model grader is correctly recognized as AOAI grader."""
        from azure.ai.evaluation import F1ScoreEvaluator

        built_in_eval = F1ScoreEvaluator()
        custom_eval = lambda x: x
        score_grader = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config, **basic_score_grader_config
        )

        evaluators = {
            "f1_score": built_in_eval,
            "custom_eval": custom_eval,
            "score_grader": score_grader,
        }

        just_evaluators, aoai_graders = _split_evaluators_and_grader_configs(evaluators)

        assert len(just_evaluators) == 2
        assert len(aoai_graders) == 1
        assert "f1_score" in just_evaluators
        assert "custom_eval" in just_evaluators
        assert "score_grader" in aoai_graders

    @pytest.mark.skip
    def test_grader_config_properties(
        self, mock_aoai_model_config, basic_score_grader_config
    ):
        """Test that grader configuration properties are accessible."""
        grader = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config, **basic_score_grader_config
        )

        config = grader._grader_config

        assert config.name == "Test Score Grader"
        assert config.model == "gpt-4o-mini"
        assert len(config.input) == 2
        assert config.input[0].role == "system"
        assert config.input[1].role == "user"
        assert config.range == [0.0, 1.0]
        sampling_params = _sampling_params_as_dict(config.sampling_params)
        assert sampling_params["temperature"] == 0.0
        assert sampling_params["max_tokens"] == 100
        assert grader.pass_threshold == 0.5

    def test_different_score_ranges(self, mock_aoai_model_config):
        """Test grader with different score ranges."""
        # Test 1-5 scale
        config_1_to_5 = {
            "name": "1-5 Scale Grader",
            "model": "gpt-4",
            "input": [{"role": "user", "content": "Rate 1-5: {{ item.text }}"}],
            "range": [1.0, 5.0],
            "pass_threshold": 3.0,
        }

        grader = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config, **config_1_to_5
        )

        assert grader._grader_config.range == [1.0, 5.0]
        assert grader.pass_threshold == 3.0

        # Test 0-10 scale with default threshold
        config_0_to_10 = {
            "name": "0-10 Scale Grader",
            "model": "gpt-4",
            "input": [{"role": "user", "content": "Rate 0-10: {{ item.text }}"}],
            "range": [0.0, 10.0],
            # No pass_threshold specified - should default to 5.0 (midpoint)
        }

        grader = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config, **config_0_to_10
        )

        assert grader._grader_config.range == [0.0, 10.0]
        assert grader.pass_threshold == 5.0  # Midpoint default

    @patch("azure.ai.evaluation._aoai.score_model_grader.AzureOpenAIGrader.get_client")
    def test_grader_with_mocked_client(
        self, mock_get_client, mock_aoai_model_config, basic_score_grader_config
    ):
        """Test grader creation and basic properties with mocked client."""
        # Mock the client to avoid actual API calls
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client

        grader = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config, **basic_score_grader_config
        )

        assert grader is not None
        assert grader.id == AzureOpenAIScoreModelGrader.id
        assert hasattr(grader, "pass_threshold")
        assert grader.pass_threshold == 0.5


@pytest.mark.unittest
class TestScoreModelGraderUsagePatterns:
    """Test common usage patterns for score model grader."""

    def test_conversation_quality_pattern(self, mock_aoai_model_config):
        """Test conversation quality grading pattern."""
        config = {
            "name": "Conversation Quality",
            "model": "gpt-4o-mini",
            "input": [
                {
                    "role": "system",
                    "content": (
                        "Assess conversation quality based on helpfulness, "
                        "accuracy, and completeness."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Context: {{ item.context }}\n"
                        "Conversation: {{ item.conversation }}\n"
                        "Rate quality (0.0-1.0):"
                    ),
                },
            ],
            "range": [0.0, 1.0],
            "pass_threshold": 0.7,
        }

        grader = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config, **config
        )

        assert grader._grader_config.name == "Conversation Quality"
        assert grader.pass_threshold == 0.7

    def test_helpfulness_scoring_pattern(self, mock_aoai_model_config):
        """Test helpfulness scoring pattern."""
        config = {
            "name": "Helpfulness Score",
            "model": "gpt-4",
            "input": [
                {
                    "role": "system",
                    "content": (
                        "Rate how helpful the AI response is to " "the user's question."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Question: {{ item.question }}\n"
                        "Response: {{ item.response }}\n"
                        "Helpfulness (0-10):"
                    ),
                },
            ],
            "range": [0.0, 10.0],
            "pass_threshold": 6.0,
            "sampling_params": {"temperature": 0.0},
        }

        grader = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config, **config
        )

        assert grader._grader_config.range == [0.0, 10.0]
        assert grader.pass_threshold == 6.0


@pytest.mark.unittest
class TestScoreModelGraderIntegration:
    """Test integration with evaluation framework."""

    def test_grader_in_evaluators_dict(
        self, mock_aoai_model_config, basic_score_grader_config
    ):
        """Test using score grader in evaluators dictionary."""
        grader = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config, **basic_score_grader_config
        )

        # Test that grader can be used in evaluators dict
        evaluators = {"quality_score": grader}

        # Verify grader separation works
        just_evaluators, aoai_graders = _split_evaluators_and_grader_configs(evaluators)
        assert len(just_evaluators) == 0
        assert len(aoai_graders) == 1
        assert "quality_score" in aoai_graders

    def test_multiple_graders_recognition(self, mock_aoai_model_config):
        """Test multiple score graders in evaluation."""
        quality_grader = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config,
            name="Quality Assessment",
            model="gpt-4o-mini",
            input=[
                {"role": "user", "content": "Rate quality: {{ item.conversation }}"}
            ],
            range=[0.0, 1.0],
        )

        helpfulness_grader = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config,
            name="Helpfulness Assessment",
            model="gpt-4o-mini",
            input=[
                {"role": "user", "content": "Rate helpfulness: {{ item.conversation }}"}
            ],
            range=[0.0, 1.0],
        )

        evaluators = {"quality": quality_grader, "helpfulness": helpfulness_grader}

        # Test grader recognition
        just_evaluators, aoai_graders = _split_evaluators_and_grader_configs(evaluators)

        assert len(just_evaluators) == 0
        assert len(aoai_graders) == 2
        assert "quality" in aoai_graders
        assert "helpfulness" in aoai_graders

    def test_mixed_evaluator_types(self, mock_aoai_model_config):
        """Test mixing score graders with built-in evaluators."""
        from azure.ai.evaluation import F1ScoreEvaluator

        f1_evaluator = F1ScoreEvaluator()
        score_grader = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config,
            name="Custom Score",
            model="gpt-4",
            input=[{"role": "user", "content": "Rate: {{ item.data }}"}],
        )

        evaluators = {"f1_score": f1_evaluator, "custom_score": score_grader}

        just_evaluators, aoai_graders = _split_evaluators_and_grader_configs(evaluators)

        assert len(just_evaluators) == 1
        assert len(aoai_graders) == 1
        assert "f1_score" in just_evaluators
        assert "custom_score" in aoai_graders

    def test_grader_conversion_error_handling(self, mock_aoai_model_config):
        """Test error handling in grader conversion."""
        init_params = {
            "model_config": mock_aoai_model_config,
            "name": "Test",
            "model": "gpt-4",
            "input": [{"role": "user", "content": "test"}],
        }

        # Test invalid grader ID
        with pytest.raises(Exception) as excinfo:
            _convert_remote_eval_params_to_grader("invalid_id", init_params=init_params)

        assert "not recognized" in str(excinfo.value)

        # Test successful conversion
        grader = _convert_remote_eval_params_to_grader(
            AzureOpenAIScoreModelGrader.id, init_params=init_params
        )

        assert isinstance(grader, AzureOpenAIScoreModelGrader)


@pytest.mark.unittest
class TestAzureOpenAIScoreModelGraderEdgeCases:
    """Comprehensive edge case testing for AzureOpenAIScoreModelGrader."""

    def test_grader_with_empty_input(self, mock_aoai_model_config):
        """Test grader creation with empty input list."""
        # Empty input should be allowed - validation happens at runtime
        grader = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config,
            name="Empty Input",
            model="gpt-4",
            input=[],
        )
        assert grader is not None
        assert len(grader._grader_config.input) == 0

    def test_grader_with_none_values(self, mock_aoai_model_config):
        """Test grader creation with None values for optional fields."""
        # Test with None sampling_params
        grader = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config,
            name="None Values Test",
            model="gpt-4",
            input=[{"role": "user", "content": "test"}],
            sampling_params=None,
        )
        assert grader is not None

        # Test with None range - should use default
        grader = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config,
            name="None Range Test",
            model="gpt-4",
            input=[{"role": "user", "content": "test"}],
            range=None,
        )
        assert grader._grader_config.range == [0.0, 1.0]

    def test_grader_with_extreme_ranges(self, mock_aoai_model_config):
        """Test grader with extreme score ranges."""
        # Very large range
        grader_large = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config,
            name="Large Range",
            model="gpt-4",
            input=[{"role": "user", "content": "test"}],
            range=[-1000.0, 1000.0],
            pass_threshold=0.0,
        )
        assert grader_large._grader_config.range == [-1000.0, 1000.0]
        assert grader_large.pass_threshold == 0.0

        # Very small range
        grader_small = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config,
            name="Small Range",
            model="gpt-4",
            input=[{"role": "user", "content": "test"}],
            range=[0.0, 0.1],
            pass_threshold=0.05,
        )
        assert grader_small._grader_config.range == [0.0, 0.1]
        assert grader_small.pass_threshold == 0.05

    def test_grader_with_negative_ranges(self, mock_aoai_model_config):
        """Test grader with negative score ranges."""
        grader = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config,
            name="Negative Range",
            model="gpt-4",
            input=[{"role": "user", "content": "test"}],
            range=[-10.0, -1.0],
            pass_threshold=-5.0,
        )
        assert grader._grader_config.range == [-10.0, -1.0]
        assert grader.pass_threshold == -5.0

    def test_grader_boundary_threshold_values(self, mock_aoai_model_config):
        """Test grader with boundary threshold values."""
        # Threshold at minimum
        grader_min = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config,
            name="Min Threshold",
            model="gpt-4",
            input=[{"role": "user", "content": "test"}],
            range=[0.0, 10.0],
            pass_threshold=0.0,
        )
        assert grader_min.pass_threshold == 0.0

        # Threshold at maximum
        grader_max = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config,
            name="Max Threshold",
            model="gpt-4",
            input=[{"role": "user", "content": "test"}],
            range=[0.0, 10.0],
            pass_threshold=10.0,
        )
        assert grader_max.pass_threshold == 10.0

    def test_grader_with_invalid_input_structures(self, mock_aoai_model_config):
        """Test grader with invalid input message structures."""
        # Missing role
        with pytest.raises((TypeError, ValueError, KeyError)):
            AzureOpenAIScoreModelGrader(
                model_config=mock_aoai_model_config,
                name="Missing Role",
                model="gpt-4",
                input=[{"content": "test"}],
            )

        # Missing content
        with pytest.raises((TypeError, ValueError, KeyError)):
            AzureOpenAIScoreModelGrader(
                model_config=mock_aoai_model_config,
                name="Missing Content",
                model="gpt-4",
                input=[{"role": "user"}],
            )

        # Invalid role
        with pytest.raises((TypeError, ValueError)):
            AzureOpenAIScoreModelGrader(
                model_config=mock_aoai_model_config,
                name="Invalid Role",
                model="gpt-4",
                input=[{"role": "invalid", "content": "test"}],
                validate=True,
            )

    @pytest.mark.skip
    def test_grader_with_complex_sampling_params(self, mock_aoai_model_config):
        """Test grader with various sampling parameter combinations."""
        complex_params = {
            "temperature": 0.7,
            "max_tokens": 150,
            "top_p": 0.9,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1,
            "stop": ["END", "STOP"],
        }

        grader = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config,
            name="Complex Params",
            model="gpt-4",
            input=[{"role": "user", "content": "test"}],
            sampling_params=complex_params,
        )

        assert (
            _sampling_params_as_dict(grader._grader_config.sampling_params)
            == complex_params
        )

    def test_grader_with_unicode_content(self, mock_aoai_model_config):
        """Test grader with Unicode and special characters in content."""
        unicode_content = "测试 🌟 émojis and spéciål characters ñ"

        grader = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config,
            name="Unicode Test",
            model="gpt-4",
            input=[
                {
                    "role": "user",
                    "content": f"Evaluate: {unicode_content} - {{{{ item.text }}}}",
                }
            ],
        )

        assert unicode_content in grader._grader_config.input[0].content

    def test_grader_with_very_long_content(self, mock_aoai_model_config):
        """Test grader with very long input content."""
        long_content = "Very long content " * 1000  # ~18KB

        grader = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config,
            name="Long Content",
            model="gpt-4",
            input=[{"role": "user", "content": long_content}],
        )

        assert len(grader._grader_config.input[0].content) > 10000

    def test_grader_invalid_type_parameters(self, mock_aoai_model_config):
        """Test grader with wrong parameter types."""
        # String range instead of list
        with pytest.raises((TypeError, ValueError)):
            AzureOpenAIScoreModelGrader(
                model_config=mock_aoai_model_config,
                name="String Range",
                model="gpt-4",
                input=[{"role": "user", "content": "test"}],
                range="0-10",
            )

        # String threshold instead of number
        with pytest.raises((TypeError, ValueError)):
            AzureOpenAIScoreModelGrader(
                model_config=mock_aoai_model_config,
                name="String Threshold",
                model="gpt-4",
                input=[{"role": "user", "content": "test"}],
                pass_threshold="5.0",
            )

        # Invalid input type
        with pytest.raises((TypeError, ValueError)):
            AzureOpenAIScoreModelGrader(
                model_config=mock_aoai_model_config,
                name="String Input",
                model="gpt-4",
                input="This should be a list",
            )

    def test_grader_with_floating_point_precision(self, mock_aoai_model_config):
        """Test grader with high precision floating point values."""
        precise_range = [0.0000001, 0.9999999]
        precise_threshold = 0.5000001

        grader = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config,
            name="Precise Values",
            model="gpt-4",
            input=[{"role": "user", "content": "test"}],
            range=precise_range,
            pass_threshold=precise_threshold,
        )

        assert grader._grader_config.range == precise_range
        assert grader.pass_threshold == precise_threshold

    def test_grader_with_zero_range(self, mock_aoai_model_config):
        """Test grader with zero-width range."""
        with pytest.raises(ValueError):
            AzureOpenAIScoreModelGrader(
                model_config=mock_aoai_model_config,
                name="Zero Range",
                model="gpt-4",
                input=[{"role": "user", "content": "test"}],
                range=[5.0, 5.0],  # Same min and max
            )

    def test_grader_with_inf_nan_values(self, mock_aoai_model_config):
        """Test grader with infinity and NaN values."""
        # These values should be allowed at initialization
        # but may fail at runtime
        grader_inf = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config,
            name="Infinity Range",
            model="gpt-4",
            input=[{"role": "user", "content": "test"}],
            range=[0.0, float("inf")],
            validate=False,
        )
        assert grader_inf is not None

        # Test with NaN - should be allowed at init
        grader_nan = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config,
            name="NaN Threshold",
            model="gpt-4",
            input=[{"role": "user", "content": "test"}],
            pass_threshold=float("nan"),
            validate=False,
        )
        assert grader_nan is not None


@pytest.mark.unittest
class TestAzureOpenAIScoreModelGraderTemplateEdgeCases:
    """Test edge cases related to template processing."""

    def test_grader_with_complex_templates(self, mock_aoai_model_config):
        """Test grader with complex template structures."""
        complex_template = """
        Context: {{ item.context }}
        Question: {{ item.question }}
        Response: {{ item.response }}
        {% if item.additional_info %}
        Additional: {{ item.additional_info }}
        {% endif %}
        Rate the response quality (0-10):
        """

        grader = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config,
            name="Complex Template",
            model="gpt-4",
            input=[{"role": "user", "content": complex_template}],
        )

        assert "item.context" in grader._grader_config.input[0].content
        assert "{% if" in grader._grader_config.input[0].content

    def test_grader_with_nested_templates(self, mock_aoai_model_config):
        """Test grader with nested template variables."""
        nested_template = (
            "{{ item.conversation[0].message }} vs "
            "{{ item.conversation[1].message }}"
        )

        grader = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config,
            name="Nested Template",
            model="gpt-4",
            input=[{"role": "user", "content": nested_template}],
        )

        assert "conversation[0]" in grader._grader_config.input[0].content

    def test_grader_with_malformed_templates(self, mock_aoai_model_config):
        """Test grader with malformed template syntax."""
        # Missing closing brace
        malformed_template = "Rate this: {{ item.text"

        grader = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config,
            name="Malformed Template",
            model="gpt-4",
            input=[{"role": "user", "content": malformed_template}],
        )

        # Should still create grader (template validation happens at runtime)
        assert grader is not None


@pytest.mark.unittest
class TestAzureOpenAIScoreModelGraderConfigurationEdgeCases:
    """Test edge cases in model configuration."""

    def test_grader_with_different_api_versions(self, mock_aoai_model_config):
        """Test grader with different API versions."""
        old_config = AzureOpenAIModelConfiguration(
            azure_deployment="test-deployment",
            azure_endpoint="https://test-endpoint.openai.azure.com/",
            api_key="test-api-key",
            api_version="2023-05-15",  # Older version
        )

        grader = AzureOpenAIScoreModelGrader(
            model_config=old_config,
            name="Old API Version",
            model="gpt-4",
            input=[{"role": "user", "content": "test"}],
            validate=False,
        )

        # Model config gets converted to dict internally
        assert grader._model_config["api_version"] == "2023-05-15"

    def test_grader_with_various_endpoints(self, mock_aoai_model_config):
        """Test grader with different endpoint formats."""
        configs = [
            ("https://test.openai.azure.com/", True),
            ("https://test.openai.azure.com", True),  # No trailing slash
            # HTTP (should work with validate=False)
            ("http://localhost:8080/", False),
            ("https://custom-domain.com/", False),  # Custom domain
        ]

        for endpoint, should_validate in configs:
            config = AzureOpenAIModelConfiguration(
                azure_deployment="test-deployment",
                azure_endpoint=endpoint,
                api_key="test-api-key",
                api_version="2024-12-01-preview",
            )

            grader = AzureOpenAIScoreModelGrader(
                model_config=config,
                name="Endpoint Test",
                model="gpt-4",
                input=[{"role": "user", "content": "test"}],
                validate=False,
            )

            # Model config gets converted to dict internally
            assert grader._model_config["azure_endpoint"] == endpoint

    def test_grader_with_empty_credentials(self):
        """Test grader with empty/invalid credentials."""
        # Should raise EvaluationException as expected
        from azure.ai.evaluation._exceptions import EvaluationException

        with pytest.raises(EvaluationException):
            config = AzureOpenAIModelConfiguration(
                azure_deployment="", azure_endpoint="", api_key="", api_version=""
            )
            AzureOpenAIScoreModelGrader(
                model_config=config,
                name="Empty Creds",
                model="gpt-4",
                input=[{"role": "user", "content": "test"}],
                validate=True,
            )

    def test_grader_with_very_long_names(self, mock_aoai_model_config):
        """Test grader with very long names and model names."""
        long_name = "A" * 1000
        long_model = "gpt-4-very-long-model-name-" + "x" * 100

        grader = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config,
            name=long_name,
            model=long_model,
            input=[{"role": "user", "content": "test"}],
        )

        assert grader._grader_config.name == long_name
        assert grader._grader_config.model == long_model


@pytest.mark.unittest
class TestAzureOpenAIScoreModelGraderRegistryEdgeCases:
    """Test edge cases in grader registry integration."""

    def test_registry_with_duplicate_grader_names(self, mock_aoai_model_config):
        """Test registry behavior with duplicate grader names."""
        grader1 = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config,
            name="Duplicate Name",
            model="gpt-4",
            input=[{"role": "user", "content": "test1"}],
        )

        grader2 = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config,
            name="Duplicate Name",
            model="gpt-4o",
            input=[{"role": "user", "content": "test2"}],
        )

        evaluators = {"grader_a": grader1, "grader_b": grader2}

        just_evaluators, aoai_graders = _split_evaluators_and_grader_configs(evaluators)

        assert len(aoai_graders) == 2
        assert "grader_a" in aoai_graders
        assert "grader_b" in aoai_graders

    def test_registry_with_none_evaluators(self):
        """Test registry behavior with None evaluators."""
        evaluators = {"valid_grader": None, "another_none": None}

        # Should handle None values gracefully
        just_evaluators, aoai_graders = _split_evaluators_and_grader_configs(evaluators)

        # All None values should be in just_evaluators
        assert len(just_evaluators) == 2
        assert len(aoai_graders) == 0

    def test_registry_conversion_with_invalid_params(self):
        """Test grader conversion with invalid initialization parameters."""
        # Missing required parameter
        invalid_params = {
            "name": "Test",
            # Missing model and input
        }

        with pytest.raises(Exception):
            _convert_remote_eval_params_to_grader(
                AzureOpenAIScoreModelGrader.id, init_params=invalid_params
            )

    def test_registry_conversion_with_extra_params(self, mock_aoai_model_config):
        """Test grader conversion with extra unknown parameters."""
        params_with_extra = {
            "model_config": mock_aoai_model_config,
            "name": "Extra Params",
            "model": "gpt-4",
            "input": [{"role": "user", "content": "test"}],
            "unknown_param": "should_be_ignored",
            "another_extra": 42,
        }

        # Should succeed and ignore extra params
        grader = _convert_remote_eval_params_to_grader(
            AzureOpenAIScoreModelGrader.id, init_params=params_with_extra
        )

        assert isinstance(grader, AzureOpenAIScoreModelGrader)
        assert grader._grader_config.name == "Extra Params"


@pytest.mark.unittest
class TestAzureOpenAIScoreModelGraderPerformanceEdgeCases:
    """Test edge cases related to performance and resource usage."""

    def test_grader_with_many_input_messages(self, mock_aoai_model_config):
        """Test grader with large number of input messages."""
        many_messages = []
        for i in range(100):
            many_messages.append(
                {
                    "role": "user" if i % 2 == 0 else "assistant",
                    "content": f"Message {i}: {{{{ item.data_{i} }}}}",
                }
            )

        grader = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config,
            name="Many Messages",
            model="gpt-4",
            input=many_messages,
        )

        assert len(grader._grader_config.input) == 100

    def test_grader_creation_performance(self, mock_aoai_model_config):
        """Test creating many graders doesn't cause memory issues."""
        graders = []

        for i in range(50):  # Create 50 graders
            grader = AzureOpenAIScoreModelGrader(
                model_config=mock_aoai_model_config,
                name=f"Grader {i}",
                model="gpt-4",
                input=[{"role": "user", "content": f"Test {i}"}],
                validate=False,
            )
            graders.append(grader)

        assert len(graders) == 50
        # Check that all graders are unique instances
        assert len(set(id(g) for g in graders)) == 50


@pytest.mark.unittest
class TestAzureOpenAIScoreModelGraderCompatibility:
    """Test compatibility with different SDK components."""

    def test_grader_with_different_evaluator_types(self, mock_aoai_model_config):
        """Test grader compatibility with various evaluator types."""
        try:
            from azure.ai.evaluation import F1ScoreEvaluator

            f1_eval = F1ScoreEvaluator()

            score_grader = AzureOpenAIScoreModelGrader(
                model_config=mock_aoai_model_config,
                name="Compatibility Test",
                model="gpt-4",
                input=[{"role": "user", "content": "test"}],
            )

            def custom_eval(x):
                return {"score": 0.5}

            evaluators = {
                "f1": f1_eval,
                "custom": custom_eval,
                "score_grader": score_grader,
            }

            just_evaluators, aoai_graders = _split_evaluators_and_grader_configs(
                evaluators
            )

            assert len(just_evaluators) >= 2  # f1 and custom
            assert len(aoai_graders) == 1
            assert "score_grader" in aoai_graders

        except ImportError:
            # Skip if evaluators not available
            pytest.skip("Built-in evaluators not available")

    def test_grader_string_representation(self, mock_aoai_model_config):
        """Test string representation of grader for debugging."""
        grader = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config,
            name="String Repr Test",
            model="gpt-4",
            input=[{"role": "user", "content": "test"}],
        )

        # Should have meaningful string representation
        grader_str = str(grader)
        assert (
            "AzureOpenAIScoreModelGrader" in grader_str
            or "String Repr Test" in grader_str
        )

    @patch(
        "azure.ai.evaluation._aoai.score_model_grader." "AzureOpenAIGrader.get_client"
    )
    def test_grader_with_client_initialization_error(
        self, mock_get_client, mock_aoai_model_config
    ):
        """Test grader behavior when client initialization fails."""
        mock_get_client.side_effect = Exception("Client initialization failed")

        # Should still create grader object (client is created lazily)
        grader = AzureOpenAIScoreModelGrader(
            model_config=mock_aoai_model_config,
            name="Client Error Test",
            model="gpt-4",
            input=[{"role": "user", "content": "test"}],
            validate=False,
        )

        assert grader is not None
