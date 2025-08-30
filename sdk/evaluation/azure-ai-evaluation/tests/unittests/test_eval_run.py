import json
import logging
import os
import time
from unittest.mock import MagicMock, patch
from uuid import uuid4
import tempfile
import jwt
import pandas as pd
import pathlib
import pytest
from azure.ai.evaluation._azure._token_manager import AzureMLTokenManager

import azure.ai.evaluation._evaluate._utils as ev_utils
from azure.ai.evaluation._evaluate._eval_run import EvalRun, RunStatus
from azure.ai.evaluation._exceptions import EvaluationException


def generate_mock_token():
    expiration_time = time.time() + 3600  # 1 hour in the future
    return jwt.encode({"exp": expiration_time}, "secret", algorithm="HS256")


@pytest.mark.unittest
@patch.object(AzureMLTokenManager, "get_token", return_value=generate_mock_token())
class TestEvalRun:
    """Unit tests for the eval-run object."""

    _MOCK_CREDS = dict(
        tracking_uri=(
            "https://region.api.azureml.ms/mlflow/v2.0/subscriptions"
            "/000000-0000-0000-0000-0000000/resourceGroups/mock-rg-region"
            "/providers/Microsoft.MachineLearningServices"
            "/workspaces/mock-ws-region"
        ),
        subscription_id="000000-0000-0000-0000-0000000",
        group_name="mock-rg-region",
        workspace_name="mock-ws-region",
        management_client=MagicMock(),
    )

    def _get_mock_create_response(self, status=200):
        """Return the mock create request"""
        mock_response = MagicMock()
        mock_response.status_code = status
        if status != 200:
            mock_response.text = lambda: "Mock error"
        else:
            mock_response.json.return_value = {
                "run": {"info": {"run_id": str(uuid4()), "experiment_id": str(uuid4()), "run_name": str(uuid4())}}
            }
        return mock_response

    def _get_mock_end_response(self, status=200):
        """Get the mock end run response."""
        mock_response = MagicMock()
        mock_response.status_code = status
        mock_response.text = lambda: "Everything good" if status == 200 else "Everything bad"
        return mock_response

    @pytest.mark.parametrize(
        "status,should_raise", [("KILLED", False), ("WRONG_STATUS", True), ("FINISHED", False), ("FAILED", False)]
    )
    def test_end_raises(self, token_mock, status, should_raise, caplog):
        """Test that end run raises exception if incorrect status is set."""
        with patch(
            "azure.ai.evaluation._http_utils.HttpPipeline.request", return_value=self._get_mock_create_response()
        ), caplog.at_level(logging.INFO):
            with EvalRun(run_name=None, **TestEvalRun._MOCK_CREDS) as run:
                if should_raise:
                    with pytest.raises(EvaluationException) as cm:
                        run._end_run(status)
                    assert status in cm.value.args[0]
                else:
                    run._end_run(status)
                    assert len(caplog.records) == 0

    def test_run_logs_if_terminated(self, token_mock, caplog):
        """Test that run warn user if we are trying to terminate it twice."""
        with patch(
            "azure.ai.evaluation._http_utils.HttpPipeline.request", return_value=self._get_mock_create_response()
        ), caplog.at_level(logging.INFO):
            logger = logging.getLogger(EvalRun.__module__)
            # All loggers, having promptflow. prefix will have "promptflow" logger
            # as a parent. This logger does not propagate the logs and cannot be
            # captured by caplog. Here we will skip this logger to capture logs.
            logger.parent = logging.root
            run = EvalRun(
                run_name=None,
                tracking_uri="www.microsoft.com",
                subscription_id="mock",
                group_name="mock",
                workspace_name="mock",
                management_client=MagicMock(),
            )
            run._start_run()
            run._end_run("KILLED")
            run._end_run("KILLED")
            assert len(caplog.records) == 1
            assert "Unable to stop run due to Run status=RunStatus.TERMINATED." in caplog.records[0].message

    def test_end_logs_if_fails(self, token_mock, caplog):
        """Test that if the terminal status setting was failed, it is logged."""
        with patch(
            "azure.ai.evaluation._http_utils.HttpPipeline.request",
            side_effect=[self._get_mock_create_response(), self._get_mock_end_response(500)],
        ), caplog.at_level(logging.INFO):
            logger = logging.getLogger(EvalRun.__module__)
            # All loggers, having promptflow. prefix will have "promptflow" logger
            # as a parent. This logger does not propagate the logs and cannot be
            # captured by caplog. Here we will skip this logger to capture logs.
            logger.parent = logging.root
            with EvalRun(
                run_name=None,
                tracking_uri="www.microsoft.com",
                subscription_id="mock",
                group_name="mock",
                workspace_name="mock",
                management_client=MagicMock(),
            ):
                pass
            assert len(caplog.records) == 1
            assert "Unable to terminate the run." in caplog.records[0].message

    def test_start_run_fails(self, token_mock, caplog):
        """Test that there are log messges if run was not started."""
        mock_response_start = MagicMock()
        mock_response_start.status_code = 500
        mock_response_start.text = lambda: "Mock internal service error."
        with patch(
            "azure.ai.evaluation._http_utils.HttpPipeline.request", return_value=mock_response_start
        ), caplog.at_level(logging.INFO):
            logger = logging.getLogger(EvalRun.__module__)
            # All loggers, having promptflow. prefix will have "promptflow" logger
            # as a parent. This logger does not propagate the logs and cannot be
            # captured by caplog. Here we will skip this logger to capture logs.
            logger.parent = logging.root
            run = EvalRun(
                run_name=None,
                tracking_uri="www.microsoft.com",
                subscription_id="mock",
                group_name="mock",
                workspace_name="mock",
                management_client=MagicMock(),
            )
            run._start_run()
            assert len(caplog.records) == 1
            assert "500" in caplog.records[0].message
            assert mock_response_start.text() in caplog.records[0].message
            assert "The results will be saved locally" in caplog.records[0].message
            caplog.clear()
            # Log artifact
            run.log_artifact("test")
            assert len(caplog.records) == 1
            assert "Unable to log artifact due to Run status=RunStatus.BROKEN." in caplog.records[0].message
            caplog.clear()
            # Log metric
            run.log_metric("a", 42)
            assert len(caplog.records) == 1
            assert "Unable to log metric due to Run status=RunStatus.BROKEN." in caplog.records[0].message
            caplog.clear()
            # End run
            run._end_run("FINISHED")
            assert len(caplog.records) == 1
            assert "Unable to stop run due to Run status=RunStatus.BROKEN." in caplog.records[0].message
            caplog.clear()

    def test_run_name(self, token_mock):
        """Test that the run name is the same as ID if name is not given."""
        mock_response = self._get_mock_create_response()
        with patch("azure.ai.evaluation._http_utils.HttpPipeline.request", return_value=mock_response):
            with EvalRun(
                run_name=None,
                tracking_uri="www.microsoft.com",
                subscription_id="mock",
                group_name="mock",
                workspace_name="mock",
                management_client=MagicMock(),
            ) as run:
                pass
        assert run.info.run_id == mock_response.json.return_value["run"]["info"]["run_id"]
        assert run.info.experiment_id == mock_response.json.return_value["run"]["info"]["experiment_id"]
        assert run.info.run_name == mock_response.json.return_value["run"]["info"]["run_name"]

    def test_run_with_name(self, token_mock):
        """Test that the run name is not the same as id if it is given."""
        mock_response = self._get_mock_create_response()
        mock_response.json.return_value["run"]["info"]["run_name"] = "test"
        with patch("azure.ai.evaluation._http_utils.HttpPipeline.request", return_value=mock_response):
            with EvalRun(
                run_name="test",
                tracking_uri="www.microsoft.com",
                subscription_id="mock",
                group_name="mock",
                workspace_name="mock",
                management_client=MagicMock(),
            ) as run:
                pass
        assert run.info.run_id == mock_response.json.return_value["run"]["info"]["run_id"]
        assert run.info.experiment_id == mock_response.json.return_value["run"]["info"]["experiment_id"]
        assert run.info.run_name == "test"
        assert run.info.run_name != run.info.run_id

    def test_get_urls(self, token_mock):
        """Test getting url-s from eval run."""
        with patch(
            "azure.ai.evaluation._http_utils.HttpPipeline.request", return_value=self._get_mock_create_response()
        ):
            with EvalRun(run_name="test", **TestEvalRun._MOCK_CREDS) as run:
                pass
        assert run.get_run_history_uri() == (
            "https://region.api.azureml.ms/history/v1.0/subscriptions"
            "/000000-0000-0000-0000-0000000/resourceGroups/mock-rg-region"
            "/providers/Microsoft.MachineLearningServices"
            "/workspaces/mock-ws-region/experimentids/"
            f"{run.info.experiment_id}/runs/{run.info.run_id}"
        ), "Wrong RunHistory URL"
        assert run.get_artifacts_uri() == (
            "https://region.api.azureml.ms/history/v1.0/subscriptions"
            "/000000-0000-0000-0000-0000000/resourceGroups/mock-rg-region"
            "/providers/Microsoft.MachineLearningServices"
            "/workspaces/mock-ws-region/experimentids/"
            f"{run.info.experiment_id}/runs/{run.info.run_id}"
            "/artifacts/batch/metadata"
        ), "Wrong Artifacts URL"
        assert run.get_metrics_url() == (
            "https://region.api.azureml.ms/mlflow/v2.0/subscriptions"
            "/000000-0000-0000-0000-0000000/resourceGroups/mock-rg-region"
            "/providers/Microsoft.MachineLearningServices"
            "/workspaces/mock-ws-region/api/2.0/mlflow/runs/log-metric"
        ), "Wrong Metrics URL"

    @pytest.mark.parametrize(
        "log_function,expected_str", [("log_artifact", "register artifact"), ("log_metric", "save metrics")]
    )
    def test_log_artifacts_logs_error(self, token_mock, tmp_path, caplog, log_function, expected_str):
        """Test that the error is logged."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = lambda: "Mock not found error."
        if log_function == "log_artifact":
            with open(os.path.join(tmp_path, "test.json"), "w") as fp:
                json.dump({"f1": 0.5}, fp)

        with patch(
            "azure.ai.evaluation._http_utils.HttpPipeline.request",
            side_effect=[
                self._get_mock_create_response(),
                mock_response,
                self._get_mock_end_response(),
            ],
        ), caplog.at_level(logging.INFO):
            logger = logging.getLogger(EvalRun.__module__)
            # All loggers, having promptflow. prefix will have "promptflow" logger
            # as a parent. This logger does not propagate the logs and cannot be
            # captured by caplog. Here we will skip this logger to capture logs.
            logger.parent = logging.root
            with EvalRun(run_name="test", **TestEvalRun._MOCK_CREDS) as run:
                fn = getattr(run, log_function)
                if log_function == "log_artifact":
                    with open(os.path.join(tmp_path, EvalRun.EVALUATION_ARTIFACT), "w") as fp:
                        fp.write("42")
                    kwargs = {"artifact_folder": tmp_path}
                else:
                    kwargs = {"key": "f1", "value": 0.5}
                with patch("azure.ai.evaluation._evaluate._eval_run.BlobServiceClient", return_value=MagicMock()):
                    fn(**kwargs)

        assert len(caplog.records) == 1
        assert mock_response.text() in caplog.records[0].message
        assert "404" in caplog.records[0].message
        assert expected_str in caplog.records[0].message

    @pytest.mark.parametrize(
        "dir_exists,dir_empty,expected_error",
        [
            (True, True, "The path to the artifact is empty."),
            # (False, True, "The path to the artifact is either not a directory or does not exist."),
            (True, False, "The run results file was not found, skipping artifacts upload."),
        ],
    )
    def test_wrong_artifact_path(
        self,
        token_mock,
        tmp_path,
        caplog,
        dir_exists,
        dir_empty,
        expected_error,
    ):
        """Test that if artifact path is empty, or dies not exist we are logging the error."""
        with patch(
            "azure.ai.evaluation._http_utils.HttpPipeline.request", return_value=self._get_mock_create_response()
        ), caplog.at_level(logging.INFO):
            with EvalRun(run_name="test", **TestEvalRun._MOCK_CREDS) as run:
                logger = logging.getLogger(EvalRun.__module__)
                # All loggers, having promptflow. prefix will have "promptflow" logger
                # as a parent. This logger does not propagate the logs and cannot be
                # captured by caplog. Here we will skip this logger to capture logs.
                logger.parent = logging.root
                artifact_folder = tmp_path if dir_exists else "wrong_path_567"
                if not dir_empty:
                    with open(os.path.join(tmp_path, "test.txt"), "w") as fp:
                        fp.write("42")
                run.log_artifact(artifact_folder)
            assert len(caplog.records) == 1
            assert expected_error in caplog.records[0].message

    def test_store_multi_modal_no_images(self, token_mock, caplog):
        data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
        data_file = os.path.join(data_path, "generated_qa_chat_conv.jsonl")
        data_convo = pd.read_json(data_file, lines=True)
        with tempfile.TemporaryDirectory() as tmpdir:
            for value in data_convo["messages"]:
                ev_utils._store_multimodal_content(value, tmpdir)

    def test_store_multi_modal_image_urls(self, token_mock, caplog):
        data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
        data_file = os.path.join(data_path, "generated_conv_image_urls.jsonl")
        data_convo = pd.read_json(data_file, lines=True)
        with tempfile.TemporaryDirectory() as tmpdir:
            for value in data_convo["messages"]:
                ev_utils._store_multimodal_content(value, tmpdir)

    def test_store_multi_modal_images(self, token_mock, caplog):
        data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
        data_file = os.path.join(data_path, "generated_conv_images.jsonl")
        data_convo = pd.read_json(data_file, lines=True)
        with tempfile.TemporaryDirectory() as tmpdir:
            for value in data_convo["messages"]:
                ev_utils._store_multimodal_content(value, tmpdir)

    def test_log_metrics_and_instance_results_logs_error(self, token_mock, caplog):
        """Test that we are logging the error when there is no trace destination."""
        logger = logging.getLogger(ev_utils.__name__)
        # All loggers, having promptflow. prefix will have "promptflow" logger
        # as a parent. This logger does not propagate the logs and cannot be
        # captured by caplog. Here we will skip this logger to capture logs.
        logger.parent = logging.root

        with caplog.at_level(logging.DEBUG):
            ev_utils._log_metrics_and_instance_results(
                metrics=None,
                instance_results=None,
                trace_destination=None,
                run=None,
                name_map={},
                evaluation_name=None,
            )
        assert len(caplog.records) == 1
        assert (
            "Skip uploading evaluation results to AI Studio since no trace destination was provided."
            in caplog.records[0].message
        )

    def test_run_broken_if_no_tracking_uri(self, token_mock, caplog):
        """Test that if no tracking URI is provirded, the run is being marked as broken."""
        logger = logging.getLogger(ev_utils.__name__)
        # All loggers, having promptflow. prefix will have "promptflow" logger
        # as a parent. This logger does not propagate the logs and cannot be
        # captured by caplog. Here we will skip this logger to capture logs.
        logger.parent = logging.root
        with caplog.at_level(logging.INFO), EvalRun(
            run_name=None,
            tracking_uri=None,
            subscription_id="mock",
            group_name="mock",
            workspace_name="mock",
            management_client=MagicMock(),
        ) as run:
            assert len(caplog.records) == 1
            assert "The results will be saved locally, but will not be logged to Azure." in caplog.records[0].message
            with patch("azure.ai.evaluation._evaluate._eval_run.EvalRun.request_with_retry") as mock_request:
                run.log_artifact("mock_dir")
                run.log_metric("foo", 42)
                run.write_properties_to_run_history({"foo": "bar"})
            mock_request.assert_not_called()

    @pytest.mark.parametrize(
        "status_code,pf_run",
        [
            (401, False),
            (200, False),
            (401, True),
            (200, True),
        ],
    )
    def test_lifecycle(self, token_mock, status_code, pf_run):
        """Test the run statuses throughout its life cycle."""
        pf_run_mock = None
        if pf_run:
            pf_run_mock = MagicMock()
            pf_run_mock.name = "mock_pf_run"
            pf_run_mock._experiment_name = "mock_pf_experiment"
        with patch(
            "azure.ai.evaluation._http_utils.HttpPipeline.request",
            return_value=self._get_mock_create_response(status_code),
        ):
            run = EvalRun(run_name="test", **TestEvalRun._MOCK_CREDS, promptflow_run=pf_run_mock)
            assert run.status == RunStatus.NOT_STARTED, f"Get {run.status}, expected {RunStatus.NOT_STARTED}"
            run._start_run()
            if status_code == 200 or pf_run:
                assert run.status == RunStatus.STARTED, f"Get {run.status}, expected {RunStatus.STARTED}"
            else:
                assert run.status == RunStatus.BROKEN, f"Get {run.status}, expected {RunStatus.BROKEN}"
            run._end_run("FINISHED")
            if status_code == 200 or pf_run:
                assert run.status == RunStatus.TERMINATED, f"Get {run.status}, expected {RunStatus.TERMINATED}"
            else:
                assert run.status == RunStatus.BROKEN, f"Get {run.status}, expected {RunStatus.BROKEN}"

    def test_local_lifecycle(self, token_mock):
        """Test that the local run have correct statuses."""
        run = EvalRun(
            run_name=None,
            tracking_uri=None,
            subscription_id="mock",
            group_name="mock",
            workspace_name="mock",
            management_client=MagicMock(),
        )
        assert run.status == RunStatus.NOT_STARTED, f"Get {run.status}, expected {RunStatus.NOT_STARTED}"
        run._start_run()
        assert run.status == RunStatus.BROKEN, f"Get {run.status}, expected {RunStatus.BROKEN}"
        run._end_run("FINISHED")
        assert run.status == RunStatus.BROKEN, f"Get {run.status}, expected {RunStatus.BROKEN}"

    @pytest.mark.parametrize("status_code", [200, 401])
    def test_write_properties(self, token_mock, caplog, status_code):
        """Test writing properties to the evaluate run."""
        mock_write = MagicMock()
        mock_write.status_code = status_code
        mock_write.text = lambda: "Mock error"
        with patch(
            "azure.ai.evaluation._http_utils.HttpPipeline.request",
            side_effect=[self._get_mock_create_response(), mock_write, self._get_mock_end_response()],
        ), caplog.at_level(logging.INFO):
            with EvalRun(run_name="test", **TestEvalRun._MOCK_CREDS) as run:
                run.write_properties_to_run_history({"foo": "bar"})
        if status_code != 200:
            assert len(caplog.records) == 1
            assert "Fail writing properties" in caplog.records[0].message
            assert mock_write.text() in caplog.records[0].message
        else:
            assert len(caplog.records) == 0

    def test_write_properties_to_run_history_logs_error(self, token_mock, caplog):
        """Test that we are logging the error when there is no trace destination."""
        logger = logging.getLogger(EvalRun.__module__)
        # All loggers, having promptflow. prefix will have "promptflow" logger
        # as a parent. This logger does not propagate the logs and cannot be
        # captured by caplog. Here we will skip this logger to capture logs.
        logger.parent = logging.root
        with caplog.at_level(logging.INFO), EvalRun(
            run_name=None,
            tracking_uri=None,
            subscription_id="mock",
            group_name="mock",
            workspace_name="mock",
            management_client=MagicMock(),
        ) as run:
            run.write_properties_to_run_history({"foo": "bar"})
        assert len(caplog.records) == 3
        assert "tracking_uri was not provided," in caplog.records[0].message
        assert "Unable to write properties due to Run status=RunStatus.BROKEN." in caplog.records[1].message
        assert "Unable to stop run due to Run status=RunStatus.BROKEN." in caplog.records[2].message

    @pytest.mark.parametrize(
        "function_literal,args,expected_action",
        [
            ("write_properties_to_run_history", ({"foo": "bar"}), "write properties"),
            ("log_metric", ("foo", 42), "log metric"),
            ("log_artifact", ("mock_folder",), "log artifact"),
        ],
    )
    def test_logs_if_not_started(self, token_mock, caplog, function_literal, args, expected_action):
        """Test that all public functions are raising exception if run is not started."""
        logger = logging.getLogger(ev_utils.__name__)
        # All loggers, having promptflow. prefix will have "promptflow" logger
        # as a parent. This logger does not propagate the logs and cannot be
        # captured by caplog. Here we will skip this logger to capture logs.
        logger.parent = logging.root
        run = EvalRun(run_name=None, **TestEvalRun._MOCK_CREDS)
        with caplog.at_level(logging.INFO):
            getattr(run, function_literal)(*args)
        assert len(caplog.records) == 1
        assert expected_action in caplog.records[0].message, caplog.records[0].message
        assert (
            f"Unable to {expected_action} due to Run status=RunStatus.NOT_STARTED" in caplog.records[0].message
        ), caplog.records[0].message

    @pytest.mark.parametrize("status", [RunStatus.STARTED, RunStatus.BROKEN, RunStatus.TERMINATED])
    def test_starting_started_run(self, token_mock, status):
        """Test exception if the run was already started"""
        run = EvalRun(run_name=None, **TestEvalRun._MOCK_CREDS)
        with patch(
            "azure.ai.evaluation._http_utils.HttpPipeline.request",
            return_value=self._get_mock_create_response(500 if status == RunStatus.BROKEN else 200),
        ):
            run._start_run()
            if status == RunStatus.TERMINATED:
                run._end_run("FINISHED")
        with pytest.raises(EvaluationException) as cm:
            run._start_run()
        assert f"Unable to start run due to Run status={status}" in cm.value.args[0], cm.value.args[0]

    def test_tags_initialization(self, token_mock):
        """Test that tags are properly initialized in EvalRun constructor."""
        # Test with None tags
        run = EvalRun(run_name="test", **TestEvalRun._MOCK_CREDS, tags=None)
        assert run._tags == {}

        # Test with empty tags
        run = EvalRun(run_name="test", **TestEvalRun._MOCK_CREDS, tags={})
        assert run._tags == {}

        # Test with custom tags
        custom_tags = {"environment": "test", "version": "1.0"}
        run = EvalRun(run_name="test", **TestEvalRun._MOCK_CREDS, tags=custom_tags)
        assert run._tags == custom_tags

    def test_tags_default_mlflow_user(self, token_mock):
        """Test that default mlflow.user tag is added when not provided."""
        with patch("azure.ai.evaluation._http_utils.HttpPipeline.request") as mock_request:
            mock_request.return_value = self._get_mock_create_response()

            # Test with no tags - should add default mlflow.user
            run = EvalRun(run_name="test", **TestEvalRun._MOCK_CREDS, tags=None)
            run._start_run()

            # Verify the request was called with default mlflow.user tag
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            request_body = call_args.kwargs["json"]
            # Check that tags include the default mlflow.user
            tags_dict = {tag["key"]: tag["value"] for tag in request_body["tags"]}
            assert "mlflow.user" in tags_dict
            assert tags_dict["mlflow.user"] == "azure-ai-evaluation"

    def test_tags_custom_mlflow_user_override(self, token_mock):
        """Test that user can override the default mlflow.user tag."""
        custom_user = "custom-user"
        custom_tags = {"mlflow.user": custom_user, "environment": "prod"}

        with patch("azure.ai.evaluation._http_utils.HttpPipeline.request") as mock_request:
            mock_request.return_value = self._get_mock_create_response()

            run = EvalRun(run_name="test", **TestEvalRun._MOCK_CREDS, tags=custom_tags)
            run._start_run()

            # Verify the request was called with custom mlflow.user tag
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            request_body = call_args.kwargs["json"]

            # Check that tags include the custom mlflow.user
            tags_dict = {tag["key"]: tag["value"] for tag in request_body["tags"]}
            assert "mlflow.user" in tags_dict
            assert tags_dict["mlflow.user"] == custom_user
            assert "environment" in tags_dict
            assert tags_dict["environment"] == "prod"

    def test_tags_mlflow_format_conversion(self, token_mock):
        """Test that tags are correctly converted to MLflow format."""
        custom_tags = {"project": "ai-evaluation", "team": "sdk-team", "version": "2.1.0"}

        with patch("azure.ai.evaluation._http_utils.HttpPipeline.request") as mock_request:
            mock_request.return_value = self._get_mock_create_response()

            run = EvalRun(run_name="test", **TestEvalRun._MOCK_CREDS, tags=custom_tags)
            run._start_run()

            # Verify the request was called with correctly formatted tags
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            request_body = call_args.kwargs["json"]

            # Check that tags are in the correct MLflow format
            assert "tags" in request_body
            tags_list = request_body["tags"]
            assert isinstance(tags_list, list)

            # Convert back to dict for easy verification
            tags_dict = {tag["key"]: tag["value"] for tag in tags_list}

            # Verify all custom tags are present
            assert tags_dict["project"] == "ai-evaluation"
            assert tags_dict["team"] == "sdk-team"
            assert tags_dict["version"] == "2.1.0"
            assert tags_dict["mlflow.user"] == "azure-ai-evaluation"  # default added

            # Verify each tag has the correct structure
            for tag in tags_list:
                assert "key" in tag
                assert "value" in tag
                assert isinstance(tag["key"], str)
                assert isinstance(tag["value"], str)

    def test_tags_empty_tags_handling(self, token_mock):
        """Test that empty tags are handled correctly without errors."""
        with patch("azure.ai.evaluation._http_utils.HttpPipeline.request") as mock_request:
            mock_request.return_value = self._get_mock_create_response()

            # Test with empty dict
            run = EvalRun(run_name="test", **TestEvalRun._MOCK_CREDS, tags={})
            run._start_run()

            # Verify the request was called and only default tag is added
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            request_body = call_args.kwargs["json"]

            tags_dict = {tag["key"]: tag["value"] for tag in request_body["tags"]}
            assert len(tags_dict) == 1  # Only default mlflow.user tag
            assert tags_dict["mlflow.user"] == "azure-ai-evaluation"

    def test_tags_with_promptflow_run(self, token_mock):
        """Test that tags are stored but not sent to MLflow when using promptflow run."""
        custom_tags = {"environment": "test", "version": "1.0"}
        pf_run_mock = MagicMock()
        pf_run_mock.name = "mock_pf_run"
        pf_run_mock._experiment_name = "mock_pf_experiment"

        with patch("azure.ai.evaluation._http_utils.HttpPipeline.request") as mock_request:
            run = EvalRun(run_name="test", **TestEvalRun._MOCK_CREDS, tags=custom_tags, promptflow_run=pf_run_mock)
            run._start_run()

            # Verify no MLflow API call was made (since using promptflow run)
            mock_request.assert_not_called()

            # Verify tags are still stored
            assert run._tags == custom_tags

    def test_tags_preserved_during_run_lifecycle(self, token_mock):
        """Test that tags are preserved throughout the run lifecycle."""
        custom_tags = {"environment": "test", "team": "ai-team"}

        with patch("azure.ai.evaluation._http_utils.HttpPipeline.request") as mock_request:
            mock_request.side_effect = [self._get_mock_create_response(), self._get_mock_end_response()]

            with EvalRun(run_name="test", **TestEvalRun._MOCK_CREDS, tags=custom_tags) as run:
                # Verify tags are preserved during run
                assert run._tags == custom_tags

            # Verify tags are still there after run ends
            assert run._tags == custom_tags

    def test_tags_not_modified_original_dict(self, token_mock):
        """Test that original tags dictionary is not modified by EvalRun."""
        original_tags = {"environment": "test"}
        tags_copy = original_tags.copy()

        with patch("azure.ai.evaluation._http_utils.HttpPipeline.request") as mock_request:
            mock_request.return_value = self._get_mock_create_response()

            run = EvalRun(run_name="test", **TestEvalRun._MOCK_CREDS, tags=original_tags)
            run._start_run()

            # Verify original dictionary wasn't modified
            assert original_tags == tags_copy
            assert "mlflow.user" not in original_tags  # shouldn't be added to original

    @patch("azure.ai.evaluation._http_utils.HttpPipeline.request")
    def test_tags_in_mlflow_request_body(self, mock_request, token_mock):
        """Test that tags are properly formatted and included in MLflow request body."""
        custom_tags = {"experiment": "test-exp", "version": "1.0"}
        mock_request.return_value = self._get_mock_create_response()

        run = EvalRun(run_name="test", **TestEvalRun._MOCK_CREDS, tags=custom_tags)
        run._start_run()

        # Verify MLflow create request was called
        assert mock_request.call_count == 1

        # Get the request body
        call_args = mock_request.call_args
        request_body = call_args.kwargs["json"]

        # Verify tags are in the request body with correct format
        assert "tags" in request_body
        tags_list = request_body["tags"]

        # Convert back to dict for easier verification
        tags_dict = {tag["key"]: tag["value"] for tag in tags_list}

        # Verify our custom tags are there
        assert tags_dict["experiment"] == "test-exp"
        assert tags_dict["version"] == "1.0"

        # Verify default mlflow.user tag is there
        assert tags_dict["mlflow.user"] == "azure-ai-evaluation"

    @patch("azure.ai.evaluation._http_utils.HttpPipeline.request")
    def test_user_override_mlflow_user_tag(self, mock_request, token_mock):
        """Test that user can override the default mlflow.user tag."""
        custom_tags = {"mlflow.user": "custom-user", "experiment": "test"}
        mock_request.return_value = self._get_mock_create_response()

        run = EvalRun(run_name="test", **TestEvalRun._MOCK_CREDS, tags=custom_tags)
        run._start_run()

        # Get the request body
        call_args = mock_request.call_args
        request_body = call_args.kwargs["json"]
        tags_list = request_body["tags"]
        tags_dict = {tag["key"]: tag["value"] for tag in tags_list}

        # Verify user's mlflow.user value is preserved
        assert tags_dict["mlflow.user"] == "custom-user"
        assert tags_dict["experiment"] == "test"

    @patch("azure.ai.evaluation._http_utils.HttpPipeline.request")
    def test_empty_tags_gets_default_mlflow_user(self, mock_request, token_mock):
        """Test that empty tags still gets the default mlflow.user tag."""
        mock_request.return_value = self._get_mock_create_response()

        run = EvalRun(run_name="test", **TestEvalRun._MOCK_CREDS, tags={})
        run._start_run()

        # Get the request body
        call_args = mock_request.call_args
        request_body = call_args.kwargs["json"]
        tags_list = request_body["tags"]
        tags_dict = {tag["key"]: tag["value"] for tag in tags_list}

        # Should only have the default mlflow.user tag
        assert len(tags_dict) == 1
        assert tags_dict["mlflow.user"] == "azure-ai-evaluation"

    @patch("azure.ai.evaluation._http_utils.HttpPipeline.request")
    def test_none_tags_gets_default_mlflow_user(self, mock_request, token_mock):
        """Test that None tags still gets the default mlflow.user tag."""
        mock_request.return_value = self._get_mock_create_response()

        run = EvalRun(run_name="test", **TestEvalRun._MOCK_CREDS, tags=None)
        run._start_run()

        # Get the request body
        call_args = mock_request.call_args
        request_body = call_args.kwargs["json"]
        tags_list = request_body["tags"]
        tags_dict = {tag["key"]: tag["value"] for tag in tags_list}

        # Should only have the default mlflow.user tag
        assert len(tags_dict) == 1
        assert tags_dict["mlflow.user"] == "azure-ai-evaluation"

    def test_tags_preserved_in_promptflow_run_mode(self, token_mock):
        """Test that tags are preserved when using promptflow run mode."""
        # Mock promptflow run
        pf_run_mock = MagicMock()
        pf_run_mock.name = "pf-run-123"
        pf_run_mock._experiment_name = "test-experiment"

        custom_tags = {"model": "gpt-4", "dataset": "test-data"}

        run = EvalRun(run_name="test", **TestEvalRun._MOCK_CREDS, promptflow_run=pf_run_mock, tags=custom_tags)

        # Verify tags are stored
        assert run._tags == custom_tags

        # Verify run is in promptflow mode (no MLflow requests should be made)
        assert run._is_promptflow_run is True

    def test_tags_format_conversion_to_mlflow(self, token_mock):
        """Test the conversion of tags dict to MLflow tags list format."""
        custom_tags = {"experiment": "test-exp", "version": "1.0", "model": "gpt-4", "special-chars": "test@value#123"}

        run = EvalRun(run_name="test", **TestEvalRun._MOCK_CREDS, tags=custom_tags)

        # Test the internal tag processing (this would normally happen in _start_run)
        run_tags = run._tags.copy()
        if "mlflow.user" not in run_tags:
            run_tags["mlflow.user"] = "azure-ai-evaluation"

        # Convert to MLflow format
        tags_list = [{"key": key, "value": value} for key, value in run_tags.items()]

        # Verify format
        assert len(tags_list) == 5  # 4 custom + 1 default

        # Verify all tags are in correct format
        for tag in tags_list:
            assert "key" in tag
            assert "value" in tag
            assert isinstance(tag["key"], str)
            assert isinstance(tag["value"], str)

        # Verify specific tags
        tags_dict = {tag["key"]: tag["value"] for tag in tags_list}
        assert tags_dict["experiment"] == "test-exp"
        assert tags_dict["version"] == "1.0"
        assert tags_dict["model"] == "gpt-4"
        assert tags_dict["special-chars"] == "test@value#123"
        assert tags_dict["mlflow.user"] == "azure-ai-evaluation"
