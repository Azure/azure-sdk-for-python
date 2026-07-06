import os
import pathlib

import pandas as pd
import pytest

from azure.ai.evaluation import ContentSafetyEvaluator
from azure.ai.evaluation._evaluate._evaluate import _aggregate_metrics
from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget


def _get_file(name):
    """Get the file from the unittest data folder."""
    data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
    return os.path.join(data_path, name)


@pytest.mark.unittest
class TestContentSafetyDefectRate:
    def test_content_safety_defect_rate(self):
        file_path = _get_file("validate_defect_rate_test_data.jsonl")
        df = pd.read_json(file_path, lines=True, orient="records")
        df = df.fillna("n/a")
        metrics = _aggregate_metrics(df, {"content_safety": ContentSafetyEvaluator})

        assert metrics["content_safety.hate_unfairness_defect_rate"] == 0.33

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"violence_threshold": 0.5},
            {"sexual_threshold": "3"},
            {"self_harm_threshold": None},
            {"hate_unfairness_threshold": [3]},
        ],
    )
    def test_invalid_threshold_type_error_metadata(self, kwargs):
        """Test that a non-int threshold raises EvaluationException with correct metadata."""
        with pytest.raises(EvaluationException) as exc_info:
            ContentSafetyEvaluator(credential=None, azure_ai_project=None, **kwargs)  # type: ignore

        exc = exc_info.value
        assert exc.blame == ErrorBlame.USER_ERROR
        assert exc.category == ErrorCategory.INVALID_VALUE
        assert exc.target == ErrorTarget.CONTENT_SAFETY_CHAT_EVALUATOR
