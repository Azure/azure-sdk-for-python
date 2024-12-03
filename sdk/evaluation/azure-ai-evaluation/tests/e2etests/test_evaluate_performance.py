import math
import os
import pathlib
import pandas as pd
from pydash import max_
import pytest
import requests
import time


from azure.ai.evaluation import (
    F1ScoreEvaluator,
    evaluate,
)



@pytest.fixture
def big_f1_data_file():
    data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
    return os.path.join(data_path, "big_f1_data.jsonl")


@pytest.mark.usefixtures("recording_injection", "recorded_test")
class TestEvaluatePerformance:
    @pytest.mark.performance_test
    def test_bulk_evaluate(self, big_f1_data_file):
        """Test local-only evaluation against 100 inputs. Based on initial testing, the
        actual evaluate call shouldn't take more than 6.5 seconds. Initial result durations
        were: 5.24, 5.51, 6.12, 5.44, 5.11"""
        f1_score_eval = F1ScoreEvaluator()
        # run the evaluation with targets
        start = time.perf_counter()
        result = evaluate(
            data=big_f1_data_file,
            evaluators={"f1" : f1_score_eval},
        )
        end = time.perf_counter()
        diff = end - start # diff stored as variable just to make sure pytest output
        # shows actual time rather than (end time - start time)
        max_duration = 6.5
        assert diff < max_duration
        row_result_df = pd.DataFrame(result["rows"])
        assert "outputs.f1.f1_score" in row_result_df.columns
        assert not any(math.isnan(f1) for f1 in row_result_df["outputs.f1.f1_score"])
