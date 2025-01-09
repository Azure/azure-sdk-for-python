import os
import pathlib
import pandas as pd
import pytest

from azure.ai.evaluation import (
    F1ScoreEvaluator,
    evaluate,
)
from azure.ai.evaluation._common.math import list_mean_nan_safe


@pytest.fixture
def csv_file():
    data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
    return os.path.join(data_path, "evaluate_test_data.csv")


@pytest.fixture
def data_file():
    data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
    return os.path.join(data_path, "evaluate_test_data.jsonl")


@pytest.mark.usefixtures("recording_injection", "recorded_test")
class TestEvaluate:
    def test_evaluate_with_csv_data(self, model_config, csv_file, data_file):
        def remove_whitespace(s):
            import re
            return re.sub(r'\s+', '', s)

        # load identical data files in different formats
        jsonl_input_data = pd.read_json(data_file, lines=True)
        csv_input_data = pd.read_csv(csv_file)

        # create evaluator
        f1_score_eval = F1ScoreEvaluator()

        # run the evaluation on jsonl data
        jsonl_result = evaluate(
            data=data_file,
            evaluators={"f1_score": f1_score_eval},
        )

        jsonl_row_result_df = pd.DataFrame(jsonl_result["rows"])
        jsonl_metrics = jsonl_result["metrics"]

        # run the evaluation on csv data
        csv_result = evaluate(
            data=csv_file,
            evaluators={"f1_score": f1_score_eval},
        )

        csv_row_result_df = pd.DataFrame(csv_result["rows"])
        csv_metrics = csv_result["metrics"]

        # validate the results
        assert jsonl_result["metrics"] == csv_result["metrics"]
        assert jsonl_result["rows"][0]["inputs.context"] == csv_result["rows"][0]["inputs.context"]
        assert jsonl_result["rows"][0]["inputs.query"] == csv_result["rows"][0]["inputs.query"]
        assert jsonl_result["rows"][0]["inputs.ground_truth"] == csv_result["rows"][0]["inputs.ground_truth"]
        assert remove_whitespace(jsonl_result["rows"][0]["inputs.response"]) == remove_whitespace(csv_result["rows"][0]["inputs.response"])
        assert (
            jsonl_row_result_df.shape[0] == len(jsonl_input_data) == csv_row_result_df.shape[0] == len(csv_input_data)
        )

        assert "outputs.f1_score.f1_score" in jsonl_row_result_df.columns.to_list()
        assert "outputs.f1_score.f1_score" in csv_row_result_df.columns.to_list()

        assert "f1_score.f1_score" in jsonl_metrics.keys()
        assert "f1_score.f1_score" in csv_metrics.keys()

        assert jsonl_metrics.get("f1_score.f1_score") == list_mean_nan_safe(
            jsonl_row_result_df["outputs.f1_score.f1_score"]
        )
        assert csv_metrics.get("f1_score.f1_score") == list_mean_nan_safe(
            csv_row_result_df["outputs.f1_score.f1_score"]
        )

        assert (
            jsonl_row_result_df["outputs.f1_score.f1_score"][2]
            == csv_row_result_df["outputs.f1_score.f1_score"][2]
            == 1
        )
        assert jsonl_result["studio_url"] == csv_result["studio_url"] == None
