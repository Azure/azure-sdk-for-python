import json
import math
import os
import pathlib
import pandas as pd
import pytest
import requests
from typing import Dict
from unittest.mock import Mock, patch

from ci_tools.variables import in_ci

from azure.ai.evaluation import (
    F1ScoreEvaluator,
    FluencyEvaluator,
    evaluate,
)
from azure.ai.evaluation import AzureOpenAIModelConfiguration
from azure.ai.evaluation._common.math import list_mean_nan_safe
from azure.ai.evaluation._azure._clients import LiteMLClient
from azure.ai.evaluation._constants import TokenScope
from azure.ai.evaluation._user_agent import UserAgentSingleton
from azure.ai.evaluation._version import VERSION


@pytest.fixture
def csv_file():
    data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
    return os.path.join(data_path, "evaluate_test_data.csv")


@pytest.fixture
def data_file():
    data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
    return os.path.join(data_path, "evaluate_test_data.jsonl")


@pytest.fixture
def questions_file():
    data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
    return os.path.join(data_path, "questions.jsonl")


def answer_evaluator(response):
    return {"length": len(response)}


def answer_evaluator_int(response):
    return len(response)


def answer_evaluator_int_dict(response):
    return {42: len(response)}


def question_evaluator(query):
    return {"length": len(query)}


def _get_run_from_run_history(
    flow_run_id, azure_ml_client: LiteMLClient, project_scope
):
    """Get run info from run history"""
    from azure.identity import DefaultAzureCredential

    token = (
        "Bearer "
        + DefaultAzureCredential().get_token(TokenScope.DEFAULT_AZURE_MANAGEMENT).token
    )
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
    }
    workspace = azure_ml_client.workspace_get_info(project_scope["project_name"])
    endpoint = (workspace.discovery_url or "").split("discovery")[0]
    pattern = (
        f"/subscriptions/{project_scope['subscription_id']}"
        f"/resourceGroups/{project_scope['resource_group_name']}"
        f"/providers/Microsoft.MachineLearningServices"
        f"/workspaces/{project_scope['project_name']}"
    )
    url = endpoint + "history/v1.0" + pattern + "/rundata"

    payload = {
        "runId": flow_run_id,
        "selectRunMetadata": True,
        "selectRunDefinition": True,
        "selectJobSpecification": True,
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        run = response.json()
        # if original_form is True, return the original run data from run history, mainly for test use
        return run
    elif response.status_code == 404:
        raise Exception(f"Run {flow_run_id!r} not found.")
    else:
        raise Exception(
            f"Failed to get run from service. Code: {response.status_code}, text: {response.text}"
        )


@pytest.mark.usefixtures("recording_injection", "recorded_test")
@pytest.mark.localtest
class TestEvaluate:
    # Technically unit-test-able, but kept here due to file manipulation
    def test_evaluate_with_relative_data_path(self):
        original_working_dir = os.getcwd()

        try:
            working_dir = os.path.dirname(__file__)
            os.chdir(working_dir)

            data_file = "data/evaluate_test_data.jsonl"

            f1_score_eval = F1ScoreEvaluator()
            # run the evaluation with targets
            result = evaluate(
                data=data_file,
                evaluators={"f1": f1_score_eval},
            )
            row_result_df = pd.DataFrame(result["rows"])
            assert "outputs.f1.f1_score" in row_result_df.columns
            assert not any(
                math.isnan(f1) for f1 in row_result_df["outputs.f1.f1_score"]
            )
        finally:
            os.chdir(original_working_dir)

    # @pytest.mark.performance_test
    @pytest.mark.skip(
        reason="Temporary skip to merge 37201, will re-enable in subsequent pr"
    )
    def test_evaluate_with_async_enabled_evaluator(self, model_config, data_file):
        os.environ["AI_EVALS_BATCH_USE_ASYNC"] = "true"
        fluency_eval = FluencyEvaluator(model_config)

        start_time = time.time()
        result = evaluate(
            data=data_file,
            evaluators={
                "fluency": fluency_eval,
            },
        )
        end_time = time.time()
        duration = end_time - start_time

        row_result_df = pd.DataFrame(result["rows"])
        metrics = result["metrics"]

        # validate the results
        assert result is not None
        assert result["rows"] is not None
        input_data = pd.read_json(data_file, lines=True)
        assert row_result_df.shape[0] == len(input_data)
        assert "outputs.fluency.fluency" in row_result_df.columns.to_list()
        assert "fluency.fluency" in metrics.keys()
        assert duration < 10, f"evaluate API call took too long: {duration} seconds"
        os.environ.pop("AI_EVALS_BATCH_USE_ASYNC")

    @pytest.mark.parametrize(
        "function,column",
        [
            (answer_evaluator, "length"),
            (answer_evaluator_int, "output"),
            (answer_evaluator_int_dict, "42"),
        ],
    )
    @pytest.mark.parametrize("use_pf_client", [True, False])
    def test_evaluate_python_function(self, data_file, use_pf_client, function, column):
        # data
        input_data = pd.read_json(data_file, lines=True)

        # run the evaluation
        result = evaluate(
            data=data_file,
            evaluators={"answer": function},
            _use_pf_client=use_pf_client,
        )

        row_result_df = pd.DataFrame(result["rows"])
        metrics = result["metrics"]

        # validate the results
        assert result is not None
        assert result["rows"] is not None
        assert row_result_df.shape[0] == len(input_data)

        out_column = f"outputs.answer.{column}"
        metric = f"answer.{column}"
        assert out_column in row_result_df.columns.to_list()
        assert metric in metrics.keys()
        assert metrics.get(metric) == list_mean_nan_safe(row_result_df[out_column])
        assert row_result_df[out_column][2] == 31

    def test_evaluate_with_target(self, questions_file, run_from_temp_dir):
        """Test evaluation with target function."""
        # We cannot define target in this file as pytest will load
        # all modules in test folder and target_fn will be imported from the first
        # module named test_evaluate and it will be a different module in unit test
        # folder. By keeping function in separate file we guarantee, it will be loaded
        # from there.
        from .target_fn import target_fn

        f1_score_eval = F1ScoreEvaluator()
        # run the evaluation with targets
        result = evaluate(
            data=questions_file,
            target=target_fn,
            evaluators={"answer": answer_evaluator, "f1": f1_score_eval},
        )
        row_result_df = pd.DataFrame(result["rows"])
        assert "outputs.response" in row_result_df.columns
        assert "outputs.answer.length" in row_result_df.columns
        assert list(row_result_df["outputs.answer.length"]) == [28, 76, 22]
        assert "outputs.f1.f1_score" in row_result_df.columns
        assert not any(math.isnan(f1) for f1 in row_result_df["outputs.f1.f1_score"])

    # TODO move to unit test, rename to column mapping focus
    @pytest.mark.parametrize(
        "evaluation_config",
        [
            None,
            {"default": {}},
            {"default": {}, "question_ev": {}},
            {"default": {"column_mapping": {"query": "${data.__outputs.query}"}}},
            {"default": {"column_mapping": {"query": "${data.query}"}}},
            {
                "default": {},
                "question_ev": {"column_mapping": {"query": "${data.query}"}},
            },
            {
                "default": {},
                "question_ev": {"column_mapping": {"query": "${data.__outputs.query}"}},
            },
            {
                "default": {},
                "question_ev": {
                    "column_mapping": {"another_question": "${data.__outputs.query}"}
                },
            },
            {
                "default": {
                    "column_mapping": {"another_question": "${data.__outputs.query}"}
                }
            },
        ],
    )
    def test_evaluate_another_questions(
        self, questions_file, evaluation_config, run_from_temp_dir
    ):
        """Test evaluation with target function."""
        from .target_fn import target_fn3

        # run the evaluation with targets
        result = evaluate(
            target=target_fn3,
            data=questions_file,
            evaluators={
                "question_ev": question_evaluator,
            },
            evaluator_config=evaluation_config,
        )
        row_result_df = pd.DataFrame(result["rows"])
        assert "outputs.response" in row_result_df.columns
        assert "inputs.query" in row_result_df.columns
        assert "outputs.query" in row_result_df.columns
        assert "outputs.question_ev.length" in row_result_df.columns
        query = "outputs.query"

        mapping = None
        if evaluation_config:
            config = evaluation_config.get(
                "question_ev", evaluation_config.get("default", None)
            )
            mapping = config.get("column_mapping", config)
        if mapping and (
            "another_question" in mapping or mapping.get("query") == "${data.query}"
        ):
            query = "inputs.query"
        expected = list(row_result_df[query].str.len())
        assert expected == list(row_result_df["outputs.question_ev.length"])

    @pytest.mark.parametrize(
        "evaluate_config",
        [
            (
                {
                    "f1_score": {
                        "column_mapping": {
                            "response": "${data.context}",
                            "ground_truth": "${data.ground_truth}",
                        }
                    },
                    "answer": {
                        "column_mapping": {
                            "response": "${data.__outputs.response}",
                        }
                    },
                }
            ),
            (
                {
                    "default": {
                        "column_mapping": {
                            "response": "${data.__outputs.response}",
                            "ground_truth": "${data.ground_truth}",
                        }
                    },
                }
            ),
        ],
    )
    def test_evaluate_with_evaluator_config(
        self, questions_file, evaluate_config, run_from_temp_dir
    ):
        input_data = pd.read_json(questions_file, lines=True)
        from .target_fn import target_fn2

        # run the evaluation
        result = evaluate(
            data=questions_file,
            target=target_fn2,
            evaluators={"f1_score": F1ScoreEvaluator(), "answer": answer_evaluator},
            evaluator_config=evaluate_config,
        )

        row_result_df = pd.DataFrame(result["rows"])
        metrics = result["metrics"]

        # validate the results
        assert result is not None
        assert result["rows"] is not None
        assert row_result_df.shape[0] == len(input_data)

        assert "outputs.answer.length" in row_result_df.columns.to_list()
        assert "outputs.f1_score.f1_score" in row_result_df.columns.to_list()

        assert "answer.length" in metrics.keys()
        assert "f1_score.f1_score" in metrics.keys()

    @pytest.mark.skipif(
        in_ci(),
        reason="This test fails in CI and needs to be investigate. Bug: 3458432",
    )
    @pytest.mark.azuretest
    def test_evaluate_track_in_cloud(
        self,
        questions_file,
        azure_ml_client,
        mock_trace_destination_to_cloud,
        project_scope,
    ):
        """Test evaluation with target function."""
        # We cannot define target in this file as pytest will load
        # all modules in test folder and target_fn will be imported from the first
        # module named test_evaluate and it will be a different module in unit test
        # folder. By keeping function in separate file we guarantee, it will be loaded
        # from there.
        # os.environ["AZURE_TEST_RUN_LIVE"] = "True"
        from .target_fn import target_fn

        f1_score_eval = F1ScoreEvaluator()
        evaluation_name = "test_evaluate_track_in_cloud"
        # run the evaluation with targets
        result = evaluate(
            # azure_ai_project=project_scope,
            evaluation_name=evaluation_name,
            data=questions_file,
            target=target_fn,
            evaluators={"answer": answer_evaluator, "f1": f1_score_eval},
        )
        row_result_df = pd.DataFrame(result["rows"])

        assert "outputs.answer.length" in row_result_df.columns
        assert list(row_result_df["outputs.answer.length"]) == [28, 76, 22]
        assert "outputs.f1.f1_score" in row_result_df.columns
        assert not any(math.isnan(f1) for f1 in row_result_df["outputs.f1.f1_score"])
        assert result["studio_url"] is not None

        # get remote run and validate if it exists
        run_id = result["studio_url"].split("?")[0].split("/")[5]
        remote_run = _get_run_from_run_history(run_id, azure_ml_client, project_scope)

        assert remote_run is not None
        assert remote_run["runMetadata"]["properties"]["runType"] == "eval_run"
        assert (
            remote_run["runMetadata"]["properties"]["_azureml.evaluation_run"]
            == "promptflow.BatchRun"
        )
        assert remote_run["runMetadata"]["displayName"] == evaluation_name

    @pytest.mark.skipif(
        in_ci(),
        reason="This test fails in CI and needs to be investigate. Bug: 3458432",
    )
    @pytest.mark.azuretest
    def test_evaluate_track_in_cloud_no_target(
        self,
        data_file,
        azure_ml_client,
        mock_trace_destination_to_cloud,
        project_scope,
    ):
        # data
        input_data = pd.read_json(data_file, lines=True)

        f1_score_eval = F1ScoreEvaluator()
        evaluation_name = "test_evaluate_track_in_cloud_no_target"

        # run the evaluation
        result = evaluate(
            # azure_ai_project=project_scope,
            evaluation_name=evaluation_name,
            data=data_file,
            evaluators={"f1_score": f1_score_eval},
        )

        row_result_df = pd.DataFrame(result["rows"])
        metrics = result["metrics"]

        # validate the results
        assert result is not None
        assert result["rows"] is not None
        assert row_result_df.shape[0] == len(input_data)
        assert "outputs.f1_score.f1_score" in row_result_df.columns.to_list()
        assert "f1_score.f1_score" in metrics.keys()
        assert metrics.get("f1_score.f1_score") == list_mean_nan_safe(
            row_result_df["outputs.f1_score.f1_score"]
        )
        assert row_result_df["outputs.f1_score.f1_score"][2] == 1
        assert result["studio_url"] is not None

        # get remote run and validate if it exists
        run_id = result["studio_url"].split("?")[0].split("/")[5]
        remote_run = _get_run_from_run_history(run_id, azure_ml_client, project_scope)

        assert remote_run is not None
        assert remote_run["runMetadata"]["properties"]["runType"] == "eval_run"
        assert (
            remote_run["runMetadata"]["properties"]["_azureml.evaluation_run"]
            == "promptflow.BatchRun"
        )
        assert remote_run["runMetadata"]["displayName"] == evaluation_name

    @pytest.mark.parametrize(
        "return_json, aggregate_return_json",
        [
            (True, True),
            (True, False),
            (False, True),
            (False, False),
        ],
    )
    def test_evaluate_aggregation_with_threadpool(
        self, data_file, return_json, aggregate_return_json
    ):
        from .custom_evaluators.answer_length_with_aggregation import AnswerLength

        result = evaluate(
            data=data_file,
            evaluators={
                "answer_length": AnswerLength(
                    return_json=return_json, aggregate_return_json=aggregate_return_json
                ),
                "f1_score": F1ScoreEvaluator(),
            },
        )
        assert result is not None
        assert "metrics" in result
        if aggregate_return_json:
            assert "answer_length.median" in result["metrics"].keys()

    @pytest.mark.parametrize(
        "return_json, aggregate_return_json",
        [
            (True, True),
            (True, False),
            (False, True),
            (False, False),
        ],
    )
    def test_evaluate_aggregation(self, data_file, return_json, aggregate_return_json):
        from .custom_evaluators.answer_length_with_aggregation import AnswerLength

        result = evaluate(
            data=data_file,
            evaluators={
                "answer_length": AnswerLength(
                    return_json=return_json, aggregate_return_json=aggregate_return_json
                ),
                "f1_score": F1ScoreEvaluator(),
            },
        )
        assert result is not None
        assert "metrics" in result
        if aggregate_return_json:
            assert "answer_length.median" in result["metrics"].keys()

    @pytest.mark.skip(reason="TODO: Add test back")
    def test_prompty_with_threadpool_implementation(self):
        pass

    def test_evaluate_with_csv_data(self, csv_file, data_file):
        def remove_whitespace(s):
            import re

            return re.sub(r"\s+", "", s)

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
        assert (
            jsonl_result["rows"][0]["inputs.context"]
            == csv_result["rows"][0]["inputs.context"]
        )
        assert (
            jsonl_result["rows"][0]["inputs.query"]
            == csv_result["rows"][0]["inputs.query"]
        )
        assert (
            jsonl_result["rows"][0]["inputs.ground_truth"]
            == csv_result["rows"][0]["inputs.ground_truth"]
        )
        assert remove_whitespace(
            jsonl_result["rows"][0]["inputs.response"]
        ) == remove_whitespace(csv_result["rows"][0]["inputs.response"])
        assert (
            jsonl_row_result_df.shape[0]
            == len(jsonl_input_data)
            == csv_row_result_df.shape[0]
            == len(csv_input_data)
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


@pytest.mark.usefixtures("recording_injection", "recorded_test")
class TestUserAgent:
    """Test suite to validate that the User-Agent header is overridable."""

    @pytest.fixture(scope="session")
    def user_agent_model_config(
        self, model_config: AzureOpenAIModelConfiguration
    ) -> AzureOpenAIModelConfiguration:

        if (
            model_config["azure_endpoint"]
            != "https://Sanitized.api.cognitive.microsoft.com"
        ):
            return model_config

        return AzureOpenAIModelConfiguration(
            **{**model_config, "azure_endpoint": "https://Sanitized.openai.azure.com/"},
        )

    @staticmethod
    def _transparent_mock_method(cls_to_mock, attribute_name: str) -> Mock:
        """Return a mock that still behaves like the original.

        :param cls_to_mock: The class
        :param attribute_name: The class' attribute to mock
        :return: A mock for the attribute
        :rtype: Mock
        """
        # https://stackoverflow.com/a/70886946
        return patch.object(
            cls_to_mock,
            attribute_name,
            side_effect=getattr(cls_to_mock, attribute_name),
            autospec=True,
        )

    def test_evaluate_user_agent(
        self, user_agent_model_config: AzureOpenAIModelConfiguration, data_file: str
    ) -> None:
        """Validate that user agent can be overriden with evaluate param."""
        base_user_agent = f"azure-ai-evaluation/{VERSION}"
        added_useragent = "test/1.0.0"

        expected_user_agent = f"{base_user_agent} {added_useragent}"

        from httpx import AsyncClient, Request

        with self._transparent_mock_method(AsyncClient, "send") as mock:
            evaluate(
                data=data_file,
                evaluators={"fluency": FluencyEvaluator(user_agent_model_config)},
                user_agent=added_useragent,
            )

            mock.assert_called()

            for call_args in mock.call_args_list:
                _, request, *_ = call_args.args
                request: Request

                # Not checking for strict equality because some evaluators add to the user agent
                assert expected_user_agent in request.headers["User-Agent"]
