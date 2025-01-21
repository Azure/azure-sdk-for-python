import math
import os
import pathlib
import pandas as pd
import pytest
import time
from ci_tools.variables import in_ci

# import SlowEvaluator from test evals
from test_evaluators.slow_eval import SlowEvaluator

from azure.ai.evaluation import (
    F1ScoreEvaluator,
    evaluate,
)


@pytest.fixture
def big_f1_data_file():
    data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
    return os.path.join(data_path, "big_f1_data.jsonl")


@pytest.fixture
def ten_queries_file():
    data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
    return os.path.join(data_path, "ten_queries.jsonl")


@pytest.mark.unittest
class TestEvaluatePerformance:
    @pytest.mark.performance_test
    def test_bulk_evaluate(self, big_f1_data_file):
        """Test local-only evaluation against 100 inputs."""
        f1_score_eval = F1ScoreEvaluator()
        # run the evaluation with targets
        start = time.perf_counter()
        result = evaluate(
            data=big_f1_data_file,
            evaluators={"f1": f1_score_eval},
            _use_pf_client=False,
        )
        end = time.perf_counter()
        diff = end - start  # diff stored as variable just to make sure pytest output
        # shows actual time rather than (end time - start time)
        # CI run takes around 1.5 seconds, so allow up to 2.
        max_duration = 2
        # Running this in CI has a massive startup lag. Account for it here:
        if in_ci():
            max_duration += 40

        assert diff < max_duration
        row_result_df = pd.DataFrame(result["rows"])
        assert "outputs.f1.f1_score" in row_result_df.columns
        assert not any(math.isnan(f1) for f1 in row_result_df["outputs.f1.f1_score"])

    def test_evaluate_parallelism(self, ten_queries_file):
        """Test that ensures that parallelism speeds up evaluation as expected by running
        an a test evaluator with a built-in sleep in both non-parallel and parallel modes."""
        slow_eval = SlowEvaluator()
        # run the evaluation with targets
        start = time.perf_counter()
        result = evaluate(
            data=ten_queries_file,
            evaluators={"slow": slow_eval},
            _use_pf_client=False,
        )
        end = time.perf_counter()
        # Time duration is stored as variable just to make sure pytest output
        # shows actual time rather than (end time - start time)
        diff = end - start
        # Assume any system running this test can manage to multithread 10 runs into
        # 2 batches at most, so it should take between 1 and 1.5 seconds.
        # Increase to 1.75 to account for CI lag.
        max_duration = 1.75
        assert diff < max_duration
        row_result_df = pd.DataFrame(result["rows"])
        assert "outputs.slow.result" in row_result_df.columns
