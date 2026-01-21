import pytest
from unittest.mock import MagicMock, patch

from azure.ai.evaluation import AzureOpenAIPythonGrader
from azure.ai.evaluation._model_configurations import AzureOpenAIModelConfiguration


class TestAzureOpenAIPythonGrader:
    """Test cases for AzureOpenAIPythonGrader."""

    def test_init_valid(self):
        """Test valid initialization."""
        model_config = AzureOpenAIModelConfiguration(
            azure_endpoint="https://test.openai.azure.com",
            api_key="test-key",
            azure_deployment="test-deployment",
        )

        source_code = """
def grade(sample: dict, item: dict) -> float:
    output = sample.get("output_text")
    label = item.get("label")
    return 1.0 if output == label else 0.0
"""

        grader = AzureOpenAIPythonGrader(
            model_config=model_config,
            name="python_test",
            image_tag="2025-05-08",
            pass_threshold=0.5,
            source=source_code,
        )

        assert grader.pass_threshold == 0.5
        assert grader.id == "azureai://built-in/evaluators/azure-openai/python_grader"

    def test_invalid_pass_threshold(self):
        """Test invalid pass_threshold values."""
        model_config = AzureOpenAIModelConfiguration(
            azure_endpoint="https://test.openai.azure.com",
            api_key="test-key",
            azure_deployment="test-deployment",
        )

        source_code = "def grade(sample: dict, item: dict) -> float:\n    return 1.0"

        with pytest.raises(
            ValueError, match="pass_threshold must be between 0.0 and 1.0"
        ):
            AzureOpenAIPythonGrader(
                model_config=model_config,
                name="python_test",
                image_tag="2025-05-08",
                pass_threshold=1.5,
                source=source_code,
            )
