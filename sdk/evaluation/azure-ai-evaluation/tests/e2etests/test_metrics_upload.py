import json
import logging
import os
import pathlib
from unittest.mock import MagicMock, patch

import pytest
from devtools_testutils import is_live
from ci_tools.variables import in_ci
from promptflow.tracing import _start_trace

from azure.ai.evaluation import F1ScoreEvaluator
from azure.ai.evaluation._evaluate import _utils as ev_utils
from azure.ai.evaluation._evaluate._eval_run import EvalRun
from azure.ai.evaluation._evaluate._evaluate import evaluate
from azure.ai.evaluation._azure._clients import LiteMLClient


@pytest.fixture
def data_file():
    data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
    return os.path.join(data_path, "evaluate_test_data.jsonl")


@pytest.fixture
def questions_answers_file():
    data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
    return os.path.join(data_path, "questions_answers.jsonl")


@pytest.fixture
def questions_file():
    data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
    return os.path.join(data_path, "questions.jsonl")


def _get_tracking_uri(azure_ml_client: LiteMLClient, project_scope: dict) -> str:
    return azure_ml_client.workspace_get_info(project_scope["project_name"]).ml_flow_tracking_uri or ""


@pytest.mark.usefixtures("model_config", "recording_injection", "project_scope", "recorded_test")
class TestMetricsUpload(object):
    """End to end tests to check how the metrics were uploaded to cloud."""

    # NOTE:
    # If you are re-recording the tests, remember to disable Promptflow telemetry from the command line using:
    # pf config set telemetry.enabled=false
    # Otherwise you will capture telemetry requests in the recording which will cause test playback failures.

    def _assert_no_errors_for_module(self, records, module_names):
        """Check there are no errors in the log."""
        error_messages = []
        if records:
            error_messages = [
                lg_rec.message
                for lg_rec in records
                if lg_rec.levelno == logging.WARNING and (lg_rec.name in module_names)
            ]
            assert not error_messages, "\n".join(error_messages)

    @pytest.mark.azuretest
    def test_writing_to_run_history(self, caplog, project_scope, azure_ml_client: LiteMLClient):
        """Test logging data to RunHistory service."""
        logger = logging.getLogger(EvalRun.__module__)
        # All loggers, having promptflow. prefix will have "promptflow" logger
        # as a parent. This logger does not propagate the logs and cannot be
        # captured by caplog. Here we will skip this logger to capture logs.
        logger.parent = logging.root
        # Just for sanity check let us make sure that the logging actually works
        mock_response = MagicMock()
        mock_response.status_code = 418
        with EvalRun(
            run_name="test",
            tracking_uri=_get_tracking_uri(azure_ml_client, project_scope),
            subscription_id=project_scope["subscription_id"],
            group_name=project_scope["resource_group_name"],
            workspace_name=project_scope["project_name"],
            management_client=azure_ml_client,
        ) as ev_run:
            with patch(
                "azure.ai.evaluation._evaluate._eval_run.EvalRun.request_with_retry", return_value=mock_response
            ):
                ev_run.write_properties_to_run_history({"test": 42})
                assert any(
                    lg_rec.levelno == logging.ERROR for lg_rec in caplog.records
                ), "The error log was not captured!"
            caplog.clear()
            ev_run.write_properties_to_run_history({"test": 42})
        self._assert_no_errors_for_module(caplog.records, [EvalRun.__module__])

    @pytest.mark.azuretest
    def test_logging_metrics(self, caplog, project_scope, azure_ml_client):
        """Test logging metrics."""
        logger = logging.getLogger(EvalRun.__module__)
        # All loggers, having promptflow. prefix will have "promptflow" logger
        # as a parent. This logger does not propagate the logs and cannot be
        # captured by caplog. Here we will skip this logger to capture logs.
        logger.parent = logging.root
        with EvalRun(
            run_name="test",
            tracking_uri=_get_tracking_uri(azure_ml_client, project_scope),
            subscription_id=project_scope["subscription_id"],
            group_name=project_scope["resource_group_name"],
            workspace_name=project_scope["project_name"],
            management_client=azure_ml_client,
        ) as ev_run:
            mock_response = MagicMock()
            mock_response.status_code = 418
            with patch(
                "azure.ai.evaluation._evaluate._eval_run.EvalRun.request_with_retry", return_value=mock_response
            ):
                ev_run.log_metric("f1", 0.54)
                assert any(
                    lg_rec.levelno == logging.WARNING for lg_rec in caplog.records
                ), "The error log was not captured!"
            caplog.clear()
            ev_run.log_metric("f1", 0.54)
        self._assert_no_errors_for_module(caplog.records, EvalRun.__module__)

    @pytest.mark.azuretest
    @pytest.mark.parametrize("config_name", ["sas", "none"])
    def test_log_artifact(self, project_scope, azure_cred, datastore_project_scopes, caplog, tmp_path, config_name):
        """Test uploading artifact to the service."""
        logger = logging.getLogger(EvalRun.__module__)
        # All loggers, having promptflow. prefix will have "promptflow" logger
        # as a parent. This logger does not propagate the logs and cannot be
        # captured by caplog. Here we will skip this logger to capture logs.
        logger.parent = logging.root

        project_scope = datastore_project_scopes[config_name]
        azure_ml_client = LiteMLClient(
            subscription_id=project_scope["subscription_id"],
            resource_group=project_scope["resource_group_name"],
            logger=logger,
            credential=azure_cred,
        )

        with EvalRun(
            run_name="test",
            tracking_uri=_get_tracking_uri(azure_ml_client, project_scope),
            subscription_id=project_scope["subscription_id"],
            group_name=project_scope["resource_group_name"],
            workspace_name=project_scope["project_name"],
            management_client=azure_ml_client,
        ) as ev_run:
            mock_response = MagicMock()
            mock_response.status_code = 418
            with open(os.path.join(tmp_path, EvalRun.EVALUATION_ARTIFACT), "w") as fp:
                json.dump({"f1": 0.5}, fp)
            os.makedirs(os.path.join(tmp_path, "internal_dir"), exist_ok=True)
            with open(os.path.join(tmp_path, "internal_dir", "test.json"), "w") as fp:
                json.dump({"internal_f1": 0.6}, fp)
            with patch(
                "azure.ai.evaluation._evaluate._eval_run.EvalRun.request_with_retry", return_value=mock_response
            ):
                ev_run.log_artifact(tmp_path)
                assert any(
                    lg_rec.levelno == logging.WARNING for lg_rec in caplog.records
                ), "The error log was not captured!"
            caplog.clear()
            ev_run.log_artifact(tmp_path)
        self._assert_no_errors_for_module(caplog.records, EvalRun.__module__)

    @pytest.mark.performance_test
    @pytest.mark.skipif(
        in_ci(),
        reason="There is some weird JSON serialiazation issue that only appears in CI where a \n becomes a \r\n",
    )
    def test_e2e_run_target_fn(self, caplog, project_scope, questions_answers_file, monkeypatch, azure_cred):
        """Test evaluation run logging."""
        # Afer re-recording this test, please make sure, that the cassette contains the POST
        # request ending by 00000/rundata and it has status 200.
        # Also make sure that the cosmos request ending by workspaces/00000/TraceSessions
        # and log metric call anding on /mlflow/runs/log-metric are also present.
        # pytest-cov generates coverage files, which are being uploaded. When recording tests,
        # make sure to enable coverage, check that .coverage.sanitized-suffix is present
        # in the cassette.

        # We cannot define target in this file as pytest will load
        # all modules in test folder and target_fn will be imported from the first
        # module named test_evaluate and it will be a different module in unit test
        # folder. By keeping function in separate file we guarantee, it will be loaded
        # from there.
        logger = logging.getLogger(EvalRun.__module__)
        # Switch off tracing as it is running in the second thread, wile
        # thread pool executor is not compatible with VCR.py.
        if not is_live():
            monkeypatch.setattr(_start_trace, "_is_devkit_installed", lambda: False)
        # All loggers, having promptflow. prefix will have "promptflow" logger
        # as a parent. This logger does not propagate the logs and cannot be
        # captured by caplog. Here we will skip this logger to capture logs.
        logger.parent = logging.root
        from .target_fn import target_fn

        f1_score_eval = F1ScoreEvaluator()
        evaluate(
            data=questions_answers_file,
            target=target_fn,
            evaluators={"f1": f1_score_eval},
            azure_ai_project=project_scope,
            credential=azure_cred,
        )
        self._assert_no_errors_for_module(caplog.records, (ev_utils.__name__, EvalRun.__module__))

    @pytest.mark.performance_test
    @pytest.mark.skipif(
        in_ci(),
        reason="There is some weird JSON serialiazation issue that only appears in CI where a \n becomes a \r\n",
    )
    def test_e2e_run(self, caplog, project_scope, questions_answers_file, monkeypatch, azure_cred):
        """Test evaluation run logging."""
        # Afer re-recording this test, please make sure, that the cassette contains the POST
        # request ending by /BulkRuns/create.
        # Also make sure that the cosmos request ending by workspaces/00000/TraceSessions
        # is also present.
        # pytest-cov generates coverage files, which are being uploaded. When recording tests,
        # make sure to enable coverage, check that .coverage.sanitized-suffix is present
        # in the cassette.
        logger = logging.getLogger(EvalRun.__module__)
        # All loggers, having promptflow. prefix will have "promptflow" logger
        # as a parent. This logger does not propagate the logs and cannot be
        # captured by caplog. Here we will skip this logger to capture logs.
        logger.parent = logging.root
        # Switch off tracing as it is running in the second thread, wile
        # thread pool executor is not compatible with VCR.py.
        if not is_live():
            monkeypatch.setattr(_start_trace, "_is_devkit_installed", lambda: False)
        f1_score_eval = F1ScoreEvaluator()
        evaluate(
            data=questions_answers_file,
            evaluators={"f1": f1_score_eval},
            azure_ai_project=project_scope,
            credential=azure_cred,
        )
        self._assert_no_errors_for_module(caplog.records, (ev_utils.__name__, EvalRun.__module__))
