import os
import pathlib

import pandas as pd
import pytest
import numpy as np

from azure.ai.evaluation import ContentSafetyEvaluator
from azure.ai.evaluation._evaluate._evaluate import _aggregate_metrics


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

        assert metrics["content_safety.hate_unfairness_defect_rate"] == pytest.approx(0.33, rel=1e-2)
        assert metrics["result_counts.total"] == len(df)
        assert metrics["result_counts.errored"] == 0
        assert metrics["content_safety.pass_rate"] == pytest.approx(metrics["content_safety.binary_aggregate"], rel=1e-9)

        no_results = _aggregate_metrics(
            pd.DataFrame({"content_safety.violence_score": [np.nan, None]}), {"content_safety": ContentSafetyEvaluator}
        )
        assert no_results["result_counts.total"] == 2
        assert no_results["result_counts.errored"] == 2
        assert no_results["content_safety.pass_rate"] == 0.0
