import json
import math
import os
import pathlib
import pandas as pd
import pytest
import requests
from ci_tools.variables import in_ci
import uuid
import tempfile

from azure.ai.evaluation import (
    ContentSafetyEvaluator,
    ContentSafetyMultimodalEvaluator,
    SexualMultimodalEvaluator,
    F1ScoreEvaluator,
    FluencyEvaluator,
    GroundednessEvaluator,
    GroundednessProEvaluator,
    evaluate,
)
from azure.ai.evaluation._common.math import list_mean_nan_safe
import azure.ai.evaluation._evaluate._utils as ev_utils


@pytest.fixture
def data_file():
    data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
    return os.path.join(data_path, "evaluate_test_data.jsonl")


@pytest.fixture
def data_convo_file():
    data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
    return os.path.join(data_path, "evaluate_test_data_conversation.jsonl")


@pytest.fixture
def multimodal_file_with_imageurls():
    data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
    return os.path.join(data_path, "dataset_messages_image_urls.jsonl")


@pytest.fixture
def multimodal_file_with_b64_images():
    data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
    return os.path.join(data_path, "dataset_messages_b64_images.jsonl")


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


def answer_evaluator_json(response):
    return json.dumps({"length": len(response)})


def question_evaluator(query):
    return {"length": len(query)}


def _get_run_from_run_history(flow_run_id, ml_client, project_scope):
    """Get run info from run history"""
    from azure.identity import DefaultAzureCredential

    token = "Bearer " + DefaultAzureCredential().get_token("https://management.azure.com/.default").token
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
    }
    workspace = ml_client.workspaces.get(project_scope["project_name"])
    endpoint = workspace.discovery_url.split("discovery")[0]
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
        raise Exception(f"Failed to get run from service. Code: {response.status_code}, text: {response.text}")


@pytest.mark.usefixtures("recording_injection", "recorded_test")
@pytest.mark.localtest
class TestEvaluate:
    @pytest.mark.skip(reason="Temporary skip to merge 37201, will re-enable in subsequent pr")
    def test_evaluate_with_groundedness_evaluator(self, model_config, data_file):
        # data
        input_data = pd.read_json(data_file, lines=True)

        groundedness_eval = GroundednessEvaluator(model_config)
        f1_score_eval = F1ScoreEvaluator()

        # run the evaluation
        result = evaluate(
            data=data_file,
            evaluators={"grounded": groundedness_eval, "f1_score": f1_score_eval},
        )

        row_result_df = pd.DataFrame(result["rows"])
        metrics = result["metrics"]

        # validate the results
        assert result is not None
        assert result["rows"] is not None
        assert row_result_df.shape[0] == len(input_data)

        assert "outputs.grounded.groundedness" in row_result_df.columns.to_list()
        assert "outputs.f1_score.f1_score" in row_result_df.columns.to_list()

        assert "grounded.groundedness" in metrics.keys()
        assert "f1_score.f1_score" in metrics.keys()

        assert metrics.get("grounded.groundedness") == list_mean_nan_safe(
            row_result_df["outputs.grounded.groundedness"]
        )
        assert metrics.get("f1_score.f1_score") == list_mean_nan_safe(row_result_df["outputs.f1_score.f1_score"])

        assert row_result_df["outputs.grounded.groundedness"][2] in [4, 5]
        assert row_result_df["outputs.f1_score.f1_score"][2] == 1
        assert result["studio_url"] is None

    @pytest.mark.skip(reason="Temporary skip to merge 37201, will re-enable in subsequent pr")
    def test_evaluate_with_relative_data_path(self, model_config):
        original_working_dir = os.getcwd()

        try:
            working_dir = os.path.dirname(__file__)
            os.chdir(working_dir)

            data_file = "data/evaluate_test_data.jsonl"
            input_data = pd.read_json(data_file, lines=True)

            groundedness_eval = GroundednessEvaluator(model_config)
            fluency_eval = FluencyEvaluator(model_config)

            # Run the evaluation
            result = evaluate(
                data=data_file,
                evaluators={"grounded": groundedness_eval, "fluency": fluency_eval},
            )

            row_result_df = pd.DataFrame(result["rows"])
            metrics = result["metrics"]

            # Validate the results
            assert result is not None
            assert result["rows"] is not None
            assert row_result_df.shape[0] == len(input_data)

            assert "outputs.grounded.groundedness" in row_result_df.columns.to_list()
            assert "outputs.fluency.fluency" in row_result_df.columns.to_list()

            assert "grounded.groundedness" in metrics.keys()
            assert "fluency.fluency" in metrics.keys()
        finally:
            os.chdir(original_working_dir)

    def test_evaluate_with_content_safety_evaluator(self, project_scope, azure_cred, data_file):
        input_data = pd.read_json(data_file, lines=True)

        # CS evaluator tries to store the credential, which breaks multiprocessing at
        # pickling stage. So we pass None for credential and let child evals
        # generate a default credential at runtime.
        # Internal Parallelism is also disabled to avoid faulty recordings.
        content_safety_eval = ContentSafetyEvaluator(
            azure_ai_project=project_scope, credential=azure_cred, parallel=False
        )

        # run the evaluation
        result = evaluate(
            data=data_file,
            evaluators={"content_safety": content_safety_eval},
        )

        row_result_df = pd.DataFrame(result["rows"])
        metrics = result["metrics"]
        # validate the results
        assert result is not None
        assert result["rows"] is not None
        assert row_result_df.shape[0] == len(input_data)

        assert "outputs.content_safety.sexual" in row_result_df.columns.to_list()
        assert "outputs.content_safety.violence" in row_result_df.columns.to_list()
        assert "outputs.content_safety.self_harm" in row_result_df.columns.to_list()
        assert "outputs.content_safety.hate_unfairness" in row_result_df.columns.to_list()

        assert "content_safety.sexual_defect_rate" in metrics.keys()
        assert "content_safety.violence_defect_rate" in metrics.keys()
        assert "content_safety.self_harm_defect_rate" in metrics.keys()
        assert "content_safety.hate_unfairness_defect_rate" in metrics.keys()

        assert 0 <= metrics.get("content_safety.sexual_defect_rate") <= 1
        assert 0 <= metrics.get("content_safety.violence_defect_rate") <= 1
        assert 0 <= metrics.get("content_safety.self_harm_defect_rate") <= 1
        assert 0 <= metrics.get("content_safety.hate_unfairness_defect_rate") <= 1

    def test_saving_b64_images(self, multimodal_file_with_b64_images):
        instance_results = pd.read_json(multimodal_file_with_b64_images, lines=True)
        with tempfile.TemporaryDirectory() as tmpdir:
            for key, item in instance_results["conversation"].items():
                ev_utils._store_multimodal_content(item["messages"], tmpdir)
            image_folder = os.path.join(tmpdir, "images")
            files = [file for file in os.listdir(image_folder)]
            assert isinstance(files, list), "The result should be a list"
            assert 1 == len(files), "file1.txt should be present in the folder"

    def test_evaluate_with_content_safety_multimodal_evaluator(
        self, project_scope, azure_cred, multimodal_file_with_imageurls
    ):
        os.environ["PF_EVALS_BATCH_USE_ASYNC"] = "false"
        input_data = pd.read_json(multimodal_file_with_imageurls, lines=True)
        content_safety_eval = ContentSafetyMultimodalEvaluator(
            azure_ai_project=project_scope, credential=azure_cred, parallel=False
        )
        result = evaluate(
            evaluation_name=f"test-mm-eval-dataset-img-url-{str(uuid.uuid4())}",
            azure_ai_project=project_scope,
            data=multimodal_file_with_imageurls,
            evaluators={"content_safety": content_safety_eval},
            evaluator_config={
                "content_safety": {"conversation": "${data.conversation}"},
            },
        )

        row_result_df = pd.DataFrame(result["rows"])
        metrics = result["metrics"]
        # validate the results
        assert result is not None
        assert result["rows"] is not None
        assert row_result_df.shape[0] == len(input_data)

        assert "outputs.content_safety.sexual" in row_result_df.columns.to_list()
        assert "outputs.content_safety.violence" in row_result_df.columns.to_list()
        assert "outputs.content_safety.self_harm" in row_result_df.columns.to_list()
        assert "outputs.content_safety.hate_unfairness" in row_result_df.columns.to_list()

        assert "content_safety.sexual_defect_rate" in metrics.keys()
        assert "content_safety.violence_defect_rate" in metrics.keys()
        assert "content_safety.self_harm_defect_rate" in metrics.keys()
        assert "content_safety.hate_unfairness_defect_rate" in metrics.keys()

        assert 0 <= metrics.get("content_safety.sexual_defect_rate") <= 1
        assert 0 <= metrics.get("content_safety.violence_defect_rate") <= 1
        assert 0 <= metrics.get("content_safety.self_harm_defect_rate") <= 1
        assert 0 <= metrics.get("content_safety.hate_unfairness_defect_rate") <= 1

    def test_evaluate_with_content_safety_multimodal_evaluator_with_target(
        self, project_scope, azure_cred, multimodal_file_with_imageurls
    ):
        os.environ["PF_EVALS_BATCH_USE_ASYNC"] = "false"
        from .target_fn import target_multimodal_fn1

        input_data = pd.read_json(multimodal_file_with_imageurls, lines=True)
        content_safety_eval = ContentSafetyMultimodalEvaluator(
            azure_ai_project=project_scope, credential=azure_cred, parallel=False
        )
        result = evaluate(
            evaluation_name=f"test-mm-eval-dataset-img-url-target-{str(uuid.uuid4())}",
            azure_ai_project=project_scope,
            data=multimodal_file_with_imageurls,
            target=target_multimodal_fn1,
            evaluators={"content_safety": content_safety_eval},
            evaluator_config={
                "content_safety": {"conversation": "${data.conversation}"},
            },
        )

        row_result_df = pd.DataFrame(result["rows"])
        metrics = result["metrics"]
        # validate the results
        assert result is not None
        assert result["rows"] is not None
        assert row_result_df.shape[0] == len(input_data)

        assert "outputs.content_safety.sexual" in row_result_df.columns.to_list()
        assert "outputs.content_safety.violence" in row_result_df.columns.to_list()
        assert "outputs.content_safety.self_harm" in row_result_df.columns.to_list()
        assert "outputs.content_safety.hate_unfairness" in row_result_df.columns.to_list()

        assert "content_safety.sexual_defect_rate" in metrics.keys()
        assert "content_safety.violence_defect_rate" in metrics.keys()
        assert "content_safety.self_harm_defect_rate" in metrics.keys()
        assert "content_safety.hate_unfairness_defect_rate" in metrics.keys()

        assert 0 <= metrics.get("content_safety.sexual_defect_rate") <= 1
        assert 0 <= metrics.get("content_safety.violence_defect_rate") <= 1
        assert 0 <= metrics.get("content_safety.self_harm_defect_rate") <= 1
        assert 0 <= metrics.get("content_safety.hate_unfairness_defect_rate") <= 1

    def test_evaluate_with_sexual_multimodal_evaluator(self, project_scope, azure_cred, multimodal_file_with_imageurls):
        os.environ["PF_EVALS_BATCH_USE_ASYNC"] = "false"
        input_data = pd.read_json(multimodal_file_with_imageurls, lines=True)
        eval = SexualMultimodalEvaluator(azure_ai_project=project_scope, credential=azure_cred)

        result = evaluate(
            evaluation_name=f"test-mm-sexual-eval-dataset-img-url-{str(uuid.uuid4())}",
            azure_ai_project=project_scope,
            data=multimodal_file_with_imageurls,
            evaluators={"sexual": eval},
            evaluator_config={
                "sexual": {"conversation": "${data.conversation}"},
            },
        )

        row_result_df = pd.DataFrame(result["rows"])
        metrics = result["metrics"]
        # validate the results
        assert result is not None
        assert result["rows"] is not None
        assert row_result_df.shape[0] == len(input_data)

        assert "outputs.sexual.sexual" in row_result_df.columns.to_list()
        assert "sexual.sexual_defect_rate" in metrics.keys()
        assert 0 <= metrics.get("sexual.sexual_defect_rate") <= 1

    def test_evaluate_with_sexual_multimodal_evaluator_b64_images(
        self, project_scope, azure_cred, multimodal_file_with_b64_images
    ):
        os.environ["PF_EVALS_BATCH_USE_ASYNC"] = "false"
        input_data = pd.read_json(multimodal_file_with_b64_images, lines=True)
        eval = SexualMultimodalEvaluator(azure_ai_project=project_scope, credential=azure_cred)
        result = evaluate(
            evaluation_name=f"test-mm-sexual-eval-dataset-img-b64-{str(uuid.uuid4())}",
            azure_ai_project=project_scope,
            data=multimodal_file_with_b64_images,
            evaluators={"sexual": eval},
            evaluator_config={
                "sexual": {"conversation": "${data.conversation}"},
            },
        )

        row_result_df = pd.DataFrame(result["rows"])
        metrics = result["metrics"]
        # validate the results
        assert result is not None
        assert result["rows"] is not None
        assert row_result_df.shape[0] == len(input_data)

        assert "outputs.sexual.sexual" in row_result_df.columns.to_list()
        assert "sexual.sexual_defect_rate" in metrics.keys()
        assert 0 <= metrics.get("sexual.sexual_defect_rate") <= 1

    def test_evaluate_with_groundedness_pro_evaluator(self, project_scope, data_convo_file, azure_cred):

        # CS evaluator tries to store the credential, which breaks multiprocessing at
        # pickling stage. So we pass None for credential and let child evals
        # generate a default credential at runtime.
        # Internal Parallelism is also disabled to avoid faulty recordings.
        gp_eval = GroundednessProEvaluator(azure_ai_project=project_scope, credential=azure_cred)

        convo_input_data = pd.read_json(data_convo_file, lines=True)
        # run the evaluation
        convo_result = evaluate(
            data=data_convo_file,
            evaluators={"groundedness_pro": gp_eval},
        )

        convo_row_result_df = pd.DataFrame(convo_result["rows"])
        convo_metrics = convo_result["metrics"]
        assert convo_row_result_df.shape[0] == len(convo_input_data)
        assert "outputs.groundedness_pro.groundedness_pro_label" in convo_row_result_df.columns.to_list()
        assert "outputs.groundedness_pro.evaluation_per_turn" in convo_row_result_df.columns.to_list()

        per_turn_results = convo_row_result_df["outputs.groundedness_pro.evaluation_per_turn"][0]
        assert "groundedness_pro_label" in per_turn_results.keys()
        assert "groundedness_pro_reason" in per_turn_results.keys()

        # Check that label is renamed to passsing rate in metrics
        assert "groundedness_pro.groundedness_pro_passing_rate" in convo_metrics.keys()
        assert 0 <= convo_metrics.get("groundedness_pro.groundedness_pro_passing_rate") <= 1

    # @pytest.mark.performance_test
    @pytest.mark.skip(reason="Temporary skip to merge 37201, will re-enable in subsequent pr")
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
        "use_pf_client,function,column",
        [
            (True, answer_evaluator, "length"),
            (False, answer_evaluator, "length"),
            (True, answer_evaluator_int, "output"),
            (False, answer_evaluator_int, "output"),
            (True, answer_evaluator_int_dict, "42"),
            (False, answer_evaluator_int_dict, "42"),
        ],
    )
    def test_evaluate_python_function(self, data_file, use_pf_client, function, column):
        # data
        input_data = pd.read_json(data_file, lines=True)

        # run the evaluation
        result = evaluate(data=data_file, evaluators={"answer": function}, _use_pf_client=use_pf_client)

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

    def test_evaluate_with_target(self, questions_file):
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
        assert "outputs.answer" in row_result_df.columns
        assert "outputs.answer.length" in row_result_df.columns
        assert list(row_result_df["outputs.answer.length"]) == [28, 76, 22]
        assert "outputs.f1.f1_score" in row_result_df.columns
        assert not any(math.isnan(f1) for f1 in row_result_df["outputs.f1.f1_score"])

    @pytest.mark.parametrize(
        "evaluation_config",
        [
            None,
            {"default": {}},
            {"default": {}, "question_ev": {}},
            {"default": {"column_mapping": {"query": "${target.query}"}}},
            {"default": {"column_mapping": {"query": "${data.query}"}}},
            {"default": {}, "question_ev": {"column_mapping": {"query": "${data.query}"}}},
            {"default": {}, "question_ev": {"column_mapping": {"query": "${target.query}"}}},
            {"default": {}, "question_ev": {"column_mapping": {"another_question": "${target.query}"}}},
            {"default": {"column_mapping": {"another_question": "${target.query}"}}},
        ],
    )
    def test_evaluate_another_questions(self, questions_file, evaluation_config):
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
            mapping = evaluation_config.get("question_ev", evaluation_config.get("default", None))
        if mapping and ("another_question" in mapping or mapping["query"] == "${data.query}"):
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
                            "response": "${target.response}",
                        }
                    },
                }
            ),
            (
                {
                    "default": {
                        "column_mapping": {
                            "response": "${target.response}",
                            "ground_truth": "${data.ground_truth}",
                        }
                    },
                }
            ),
        ],
    )
    def test_evaluate_with_evaluator_config(self, questions_file, evaluate_config):
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

    @pytest.mark.skipif(in_ci(), reason="This test fails in CI and needs to be investigate. Bug: 3458432")
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
            azure_ai_project=project_scope,
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
        assert remote_run["runMetadata"]["properties"]["azureml.promptflow.local_to_cloud"] == "true"
        assert remote_run["runMetadata"]["properties"]["runType"] == "eval_run"
        assert remote_run["runMetadata"]["properties"]["_azureml.evaluation_run"] == "promptflow.BatchRun"
        assert remote_run["runMetadata"]["displayName"] == evaluation_name

    @pytest.mark.skipif(in_ci(), reason="This test fails in CI and needs to be investigate. Bug: 3458432")
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
            azure_ai_project=project_scope,
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
        assert metrics.get("f1_score.f1_score") == list_mean_nan_safe(row_result_df["outputs.f1_score.f1_score"])
        assert row_result_df["outputs.f1_score.f1_score"][2] == 1
        assert result["studio_url"] is not None

        # get remote run and validate if it exists
        run_id = result["studio_url"].split("?")[0].split("/")[5]
        remote_run = _get_run_from_run_history(run_id, azure_ml_client, project_scope)

        assert remote_run is not None
        assert remote_run["runMetadata"]["properties"]["runType"] == "eval_run"
        assert remote_run["runMetadata"]["properties"]["_azureml.evaluation_run"] == "azure-ai-generative-parent"
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
    def test_evaluate_aggregation_with_threadpool(self, data_file, return_json, aggregate_return_json):
        from .custom_evaluators.answer_length_with_aggregation import AnswerLength

        result = evaluate(
            data=data_file,
            evaluators={
                "answer_length": AnswerLength(return_json=return_json, aggregate_return_json=aggregate_return_json),
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
                "answer_length": AnswerLength(return_json=return_json, aggregate_return_json=aggregate_return_json),
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
