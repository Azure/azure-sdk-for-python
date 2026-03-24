# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for the MLflowIntegration class in _mlflow_integration.py."""

import json
import os
import pytest
import uuid
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, mock_open, call, PropertyMock

from azure.ai.evaluation._exceptions import (
    EvaluationException,
    ErrorBlame,
    ErrorCategory,
    ErrorTarget,
)
from azure.ai.evaluation._constants import EvaluationRunProperties
from azure.ai.evaluation._version import VERSION
from azure.ai.evaluation._common import RedTeamUpload, ResultType
from azure.ai.evaluation.red_team._mlflow_integration import MLflowIntegration
from azure.ai.evaluation.red_team._red_team_result import RedTeamResult
from azure.core.credentials import TokenCredential


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_logger():
    logger = MagicMock()
    logger.debug = MagicMock()
    logger.info = MagicMock()
    logger.warning = MagicMock()
    logger.error = MagicMock()
    return logger


@pytest.fixture
def mock_azure_ai_project():
    return {
        "subscription_id": "test-subscription",
        "resource_group_name": "test-resource-group",
        "project_name": "test-project",
        "credential": MagicMock(spec=TokenCredential),
    }


@pytest.fixture
def mock_generated_rai_client():
    client = MagicMock()
    client._evaluation_onedp_client = MagicMock()
    client._evaluation_onedp_client.start_red_team_run = MagicMock()
    client._evaluation_onedp_client.update_red_team_run = MagicMock()
    client._evaluation_onedp_client.create_evaluation_result = MagicMock()
    return client


@pytest.fixture
def integration(mock_logger, mock_azure_ai_project, mock_generated_rai_client):
    """Standard MLflowIntegration instance (non-OneDP)."""
    return MLflowIntegration(
        logger=mock_logger,
        azure_ai_project=mock_azure_ai_project,
        generated_rai_client=mock_generated_rai_client,
        one_dp_project=False,
    )


@pytest.fixture
def integration_onedp(mock_logger, mock_azure_ai_project, mock_generated_rai_client):
    """MLflowIntegration instance for OneDP projects."""
    return MLflowIntegration(
        logger=mock_logger,
        azure_ai_project=mock_azure_ai_project,
        generated_rai_client=mock_generated_rai_client,
        one_dp_project=True,
    )


@pytest.fixture
def mock_eval_run():
    """Mock EvalRun object returned by start_redteam_mlflow_run."""
    run = MagicMock()
    run.info = MagicMock()
    run.info.run_id = "test-run-id-123"
    run.id = "test-run-id-123"
    run.display_name = "test-red-team-run"
    run._start_run = MagicMock()
    run._end_run = MagicMock()
    run.log_artifact = MagicMock()
    run.log_metric = MagicMock()
    run.write_properties_to_run_history = MagicMock()
    return run


@pytest.fixture
def mock_redteam_result():
    """Minimal RedTeamResult for logging tests."""
    result = MagicMock(spec=RedTeamResult)
    result.scan_result = {
        "scorecard": {
            "joint_risk_attack_summary": [
                {
                    "risk_category": "Violence",
                    "asr": 0.25,
                    "total_attacks": 4,
                    "successful_attacks": 1,
                },
                {
                    "risk_category": "HateUnfairness",
                    "asr": 0.5,
                    "total_attacks": 4,
                    "successful_attacks": 2,
                },
            ],
        },
        "parameters": {"num_turns": 3},
        "attack_details": [{"detail": "test"}],
    }
    result.attack_details = [{"detail": "test"}]
    return result


@pytest.fixture
def mock_red_team_info():
    """Red team info dict used in logging."""
    return {
        "baseline": {
            "Violence": {
                "num_objectives": 2,
                "evaluation_result": {"should": "be_removed"},
            },
            "HateUnfairness": {
                "num_objectives": 2,
            },
        },
    }


@pytest.fixture
def mock_aoai_summary():
    """Mock AOAI-compatible summary dict."""
    return {
        "id": "run-123",
        "display_name": "test-run",
        "status": "Completed",
        "conversations": [{"role": "user", "content": "test"}],
        "results": [{"score": 0.5}],
    }


# ===========================================================================
# TestMLflowIntegrationInit
# ===========================================================================


@pytest.mark.unittest
class TestMLflowIntegrationInit:
    """Test MLflowIntegration initialization."""

    def test_init_stores_fields(self, mock_logger, mock_azure_ai_project, mock_generated_rai_client):
        integration = MLflowIntegration(
            logger=mock_logger,
            azure_ai_project=mock_azure_ai_project,
            generated_rai_client=mock_generated_rai_client,
            one_dp_project=False,
            scan_output_dir="/some/dir",
        )
        assert integration.logger is mock_logger
        assert integration.azure_ai_project is mock_azure_ai_project
        assert integration.generated_rai_client is mock_generated_rai_client
        assert integration._one_dp_project is False
        assert integration.scan_output_dir == "/some/dir"
        assert integration.ai_studio_url is None
        assert integration.trace_destination is None

    def test_init_defaults_scan_output_dir_none(self, mock_logger, mock_azure_ai_project, mock_generated_rai_client):
        integration = MLflowIntegration(
            logger=mock_logger,
            azure_ai_project=mock_azure_ai_project,
            generated_rai_client=mock_generated_rai_client,
            one_dp_project=True,
        )
        assert integration.scan_output_dir is None
        assert integration._one_dp_project is True

    def test_init_override_fields_are_none(self, integration):
        assert integration._run_id_override is None
        assert integration._eval_id_override is None
        assert integration._created_at_override is None


# ===========================================================================
# TestSetRunIdentityOverrides
# ===========================================================================


@pytest.mark.unittest
class TestSetRunIdentityOverrides:
    """Test set_run_identity_overrides method."""

    def test_set_all_overrides(self, integration):
        integration.set_run_identity_overrides(
            run_id="run-abc",
            eval_id="eval-xyz",
            created_at=1700000000,
        )
        assert integration._run_id_override == "run-abc"
        assert integration._eval_id_override == "eval-xyz"
        assert integration._created_at_override == 1700000000

    def test_set_overrides_strips_whitespace(self, integration):
        integration.set_run_identity_overrides(
            run_id="  run-abc  ",
            eval_id="  eval-xyz  ",
        )
        assert integration._run_id_override == "run-abc"
        assert integration._eval_id_override == "eval-xyz"

    def test_none_values_clear_overrides(self, integration):
        # Set first
        integration.set_run_identity_overrides(run_id="run-1", eval_id="eval-1", created_at=100)
        # Clear
        integration.set_run_identity_overrides(run_id=None, eval_id=None, created_at=None)
        assert integration._run_id_override is None
        assert integration._eval_id_override is None
        assert integration._created_at_override is None

    def test_empty_string_created_at_becomes_none(self, integration):
        integration.set_run_identity_overrides(created_at="")
        assert integration._created_at_override is None

    def test_datetime_created_at_converted_to_timestamp(self, integration):
        dt = datetime(2024, 1, 15, 12, 0, 0)
        integration.set_run_identity_overrides(created_at=dt)
        assert integration._created_at_override == int(dt.timestamp())

    def test_string_numeric_created_at_converted_to_int(self, integration):
        integration.set_run_identity_overrides(created_at="1700000000")
        assert integration._created_at_override == 1700000000

    def test_invalid_created_at_becomes_none(self, integration):
        integration.set_run_identity_overrides(created_at="not-a-number")
        assert integration._created_at_override is None

    def test_float_created_at_truncated_to_int(self, integration):
        integration.set_run_identity_overrides(created_at=1700000000.999)
        assert integration._created_at_override == 1700000000


# ===========================================================================
# TestStartRedteamMlflowRun
# ===========================================================================


@pytest.mark.unittest
class TestStartRedteamMlflowRun:
    """Test start_redteam_mlflow_run method."""

    def test_raises_when_no_project(self, integration):
        with pytest.raises(EvaluationException, match="No azure_ai_project provided"):
            integration.start_redteam_mlflow_run(azure_ai_project=None)

    def test_raises_when_no_project_logs_error(self, integration, mock_logger):
        with pytest.raises(EvaluationException):
            integration.start_redteam_mlflow_run(azure_ai_project=None)
        mock_logger.error.assert_called()

    def test_onedp_project_calls_start_red_team_run(self, integration_onedp, mock_generated_rai_client):
        mock_response = MagicMock()
        mock_response.properties = {"AiStudioEvaluationUri": "https://ai.azure.com/test"}
        mock_generated_rai_client._evaluation_onedp_client.start_red_team_run.return_value = mock_response

        result = integration_onedp.start_redteam_mlflow_run(
            azure_ai_project={"subscription_id": "sub"},
            run_name="my-test-run",
        )

        assert result is mock_response
        assert integration_onedp.ai_studio_url == "https://ai.azure.com/test"
        mock_generated_rai_client._evaluation_onedp_client.start_red_team_run.assert_called_once()
        # Verify the RedTeamUpload was created with the provided run name
        call_args = mock_generated_rai_client._evaluation_onedp_client.start_red_team_run.call_args
        assert call_args.kwargs["red_team"].display_name == "my-test-run"

    def test_onedp_project_auto_generates_run_name(self, integration_onedp, mock_generated_rai_client):
        mock_response = MagicMock()
        mock_response.properties = {}
        mock_generated_rai_client._evaluation_onedp_client.start_red_team_run.return_value = mock_response

        integration_onedp.start_redteam_mlflow_run(
            azure_ai_project={"subscription_id": "sub"},
            run_name=None,
        )

        call_args = mock_generated_rai_client._evaluation_onedp_client.start_red_team_run.call_args
        assert call_args.kwargs["red_team"].display_name.startswith("redteam-agent-")

    @patch("azure.ai.evaluation.red_team._mlflow_integration._get_ai_studio_url")
    @patch("azure.ai.evaluation.red_team._mlflow_integration.EvalRun")
    @patch("azure.ai.evaluation.red_team._mlflow_integration.LiteMLClient")
    @patch("azure.ai.evaluation.red_team._mlflow_integration.extract_workspace_triad_from_trace_provider")
    @patch("azure.ai.evaluation.red_team._mlflow_integration._trace_destination_from_project_scope")
    def test_non_onedp_creates_eval_run(
        self,
        mock_trace_dest,
        mock_extract_triad,
        mock_lite_client_cls,
        mock_eval_run_cls,
        mock_get_url,
        integration,
        mock_azure_ai_project,
    ):
        mock_trace_dest.return_value = "azureml://some/trace/dest"
        mock_triad = MagicMock()
        mock_triad.subscription_id = "sub-id"
        mock_triad.resource_group_name = "rg-name"
        mock_triad.workspace_name = "ws-name"
        mock_extract_triad.return_value = mock_triad

        mock_mgmt = MagicMock()
        mock_mgmt.workspace_get_info.return_value = MagicMock(ml_flow_tracking_uri="https://tracking.mlflow.com")
        mock_lite_client_cls.return_value = mock_mgmt

        mock_run = MagicMock()
        mock_run.info.run_id = "eval-run-789"
        mock_eval_run_cls.return_value = mock_run

        mock_get_url.return_value = "https://ai.azure.com/eval/eval-run-789"

        result = integration.start_redteam_mlflow_run(
            azure_ai_project=mock_azure_ai_project,
            run_name="custom-run",
        )

        assert result is mock_run
        mock_run._start_run.assert_called_once()
        assert integration.trace_destination == "azureml://some/trace/dest"
        assert integration.ai_studio_url == "https://ai.azure.com/eval/eval-run-789"

    @patch("azure.ai.evaluation.red_team._mlflow_integration._trace_destination_from_project_scope")
    def test_non_onedp_raises_when_no_trace_destination(self, mock_trace_dest, integration, mock_azure_ai_project):
        mock_trace_dest.return_value = None

        with pytest.raises(EvaluationException, match="Could not determine trace destination"):
            integration.start_redteam_mlflow_run(azure_ai_project=mock_azure_ai_project)


# ===========================================================================
# TestLogRedteamResultsToMlflow
# ===========================================================================


@pytest.mark.unittest
class TestLogRedteamResultsToMlflow:
    """Test log_redteam_results_to_mlflow method."""

    @pytest.mark.asyncio
    async def test_raises_when_aoai_summary_none_no_scan_output_dir(
        self, integration, mock_redteam_result, mock_eval_run, mock_red_team_info
    ):
        """Without scan_output_dir, aoai_summary=None raises ValueError at the tmpdir block."""
        with pytest.raises(ValueError, match="aoai_summary parameter is required"):
            await integration.log_redteam_results_to_mlflow(
                redteam_result=mock_redteam_result,
                eval_run=mock_eval_run,
                red_team_info=mock_red_team_info,
                aoai_summary=None,
            )

    @pytest.mark.asyncio
    async def test_non_onedp_logs_artifacts_and_metrics(
        self, integration, mock_redteam_result, mock_eval_run, mock_red_team_info, mock_aoai_summary
    ):
        """Non-OneDP: logs artifacts, metrics, properties, and ends run."""
        result = await integration.log_redteam_results_to_mlflow(
            redteam_result=mock_redteam_result,
            eval_run=mock_eval_run,
            red_team_info=mock_red_team_info,
            aoai_summary=mock_aoai_summary,
        )

        assert result is None
        # Artifacts logged
        mock_eval_run.log_artifact.assert_called()
        # Metrics logged: violence_asr, violence_total_attacks, etc.
        assert mock_eval_run.log_metric.call_count > 0
        logged_metric_names = [c.args[0] for c in mock_eval_run.log_metric.call_args_list]
        assert "violence_asr" in logged_metric_names
        assert "hateunfairness_asr" in logged_metric_names
        # Properties written
        mock_eval_run.write_properties_to_run_history.assert_called_once()
        props = mock_eval_run.write_properties_to_run_history.call_args.args[0]
        assert props["redteaming"] == "asr"
        assert f"azure-ai-evaluation:{VERSION}" in props[EvaluationRunProperties.EVALUATION_SDK]
        # Run ended
        mock_eval_run._end_run.assert_called_once_with("FINISHED")

    @pytest.mark.asyncio
    async def test_non_onedp_skip_evals_still_logs(
        self, integration, mock_eval_run, mock_red_team_info, mock_aoai_summary
    ):
        """With _skip_evals=True, no metrics are logged if scan_result is empty."""
        empty_result = MagicMock(spec=RedTeamResult)
        empty_result.scan_result = None
        empty_result.attack_details = [{"detail": "test"}]

        await integration.log_redteam_results_to_mlflow(
            redteam_result=empty_result,
            eval_run=mock_eval_run,
            red_team_info=mock_red_team_info,
            _skip_evals=True,
            aoai_summary=mock_aoai_summary,
        )

        # No metrics logged when scan_result is None
        mock_eval_run.log_metric.assert_not_called()
        # But run still ends
        mock_eval_run._end_run.assert_called_once_with("FINISHED")

    @pytest.mark.asyncio
    async def test_non_onedp_artifact_logging_failure_is_warning(
        self, integration, mock_redteam_result, mock_eval_run, mock_red_team_info, mock_aoai_summary, mock_logger
    ):
        """Failed artifact logging should warn, not crash."""
        mock_eval_run.log_artifact.side_effect = Exception("blob upload failed")

        # Should not raise
        await integration.log_redteam_results_to_mlflow(
            redteam_result=mock_redteam_result,
            eval_run=mock_eval_run,
            red_team_info=mock_red_team_info,
            aoai_summary=mock_aoai_summary,
        )

        mock_logger.warning.assert_any_call("Failed to log artifacts to AI Foundry: blob upload failed")

    @pytest.mark.asyncio
    async def test_onedp_creates_evaluation_result_and_updates_run(
        self,
        integration_onedp,
        mock_generated_rai_client,
        mock_redteam_result,
        mock_eval_run,
        mock_red_team_info,
        mock_aoai_summary,
    ):
        """OneDP path: creates evaluation result then updates the run."""
        mock_result_response = MagicMock()
        mock_result_response.id = "eval-result-456"
        mock_generated_rai_client._evaluation_onedp_client.create_evaluation_result.return_value = mock_result_response

        await integration_onedp.log_redteam_results_to_mlflow(
            redteam_result=mock_redteam_result,
            eval_run=mock_eval_run,
            red_team_info=mock_red_team_info,
            aoai_summary=mock_aoai_summary,
        )

        mock_generated_rai_client._evaluation_onedp_client.create_evaluation_result.assert_called_once()
        create_call = mock_generated_rai_client._evaluation_onedp_client.create_evaluation_result.call_args
        assert create_call.kwargs["result_type"] == ResultType.REDTEAM

        mock_generated_rai_client._evaluation_onedp_client.update_red_team_run.assert_called_once()
        update_call = mock_generated_rai_client._evaluation_onedp_client.update_red_team_run.call_args
        assert update_call.kwargs["red_team"].status == "Completed"
        assert update_call.kwargs["red_team"].outputs == {"evaluationResultId": "eval-result-456"}

    @pytest.mark.asyncio
    async def test_onedp_updates_run_even_when_result_upload_fails(
        self,
        integration_onedp,
        mock_generated_rai_client,
        mock_redteam_result,
        mock_eval_run,
        mock_red_team_info,
        mock_aoai_summary,
        mock_logger,
    ):
        """OneDP: even if create_evaluation_result fails, update_red_team_run still called."""
        mock_generated_rai_client._evaluation_onedp_client.create_evaluation_result.side_effect = Exception(
            "upload boom"
        )

        await integration_onedp.log_redteam_results_to_mlflow(
            redteam_result=mock_redteam_result,
            eval_run=mock_eval_run,
            red_team_info=mock_red_team_info,
            aoai_summary=mock_aoai_summary,
        )

        # Error logged for result upload
        mock_logger.error.assert_called()
        # But update_red_team_run still called (without outputs)
        mock_generated_rai_client._evaluation_onedp_client.update_red_team_run.assert_called_once()
        update_call = mock_generated_rai_client._evaluation_onedp_client.update_red_team_run.call_args
        assert update_call.kwargs["red_team"].outputs is None

    @pytest.mark.asyncio
    async def test_onedp_update_run_failure_is_logged(
        self,
        integration_onedp,
        mock_generated_rai_client,
        mock_redteam_result,
        mock_eval_run,
        mock_red_team_info,
        mock_aoai_summary,
        mock_logger,
    ):
        """OneDP: failed update_red_team_run is logged, not raised."""
        mock_result_response = MagicMock()
        mock_result_response.id = "eval-result-789"
        mock_generated_rai_client._evaluation_onedp_client.create_evaluation_result.return_value = mock_result_response
        mock_generated_rai_client._evaluation_onedp_client.update_red_team_run.side_effect = Exception("update boom")

        # Should not raise
        await integration_onedp.log_redteam_results_to_mlflow(
            redteam_result=mock_redteam_result,
            eval_run=mock_eval_run,
            red_team_info=mock_red_team_info,
            aoai_summary=mock_aoai_summary,
        )

        error_calls = [str(c) for c in mock_logger.error.call_args_list]
        assert any("update boom" in c for c in error_calls)

    @pytest.mark.asyncio
    async def test_metrics_extracted_from_scorecard(
        self, integration, mock_eval_run, mock_red_team_info, mock_aoai_summary
    ):
        """Verify metric extraction from joint_risk_attack_summary."""
        result = MagicMock(spec=RedTeamResult)
        result.scan_result = {
            "scorecard": {
                "joint_risk_attack_summary": [
                    {
                        "risk_category": "SelfHarm",
                        "asr": 0.1,
                        "total_attacks": 10,
                        "successful_attacks": 1,
                    },
                ],
            },
        }
        result.attack_details = []

        await integration.log_redteam_results_to_mlflow(
            redteam_result=result,
            eval_run=mock_eval_run,
            red_team_info=mock_red_team_info,
            aoai_summary=mock_aoai_summary,
        )

        metric_calls = {c.args[0]: c.args[1] for c in mock_eval_run.log_metric.call_args_list}
        assert metric_calls["selfharm_asr"] == 0.1
        assert metric_calls["selfharm_total_attacks"] == 10
        assert metric_calls["selfharm_successful_attacks"] == 1

    @pytest.mark.asyncio
    async def test_no_metrics_when_joint_summary_empty(
        self, integration, mock_eval_run, mock_red_team_info, mock_aoai_summary
    ):
        """Empty joint_risk_attack_summary → no metrics logged."""
        result = MagicMock(spec=RedTeamResult)
        result.scan_result = {
            "scorecard": {"joint_risk_attack_summary": []},
        }
        result.attack_details = []

        await integration.log_redteam_results_to_mlflow(
            redteam_result=result,
            eval_run=mock_eval_run,
            red_team_info=mock_red_team_info,
            aoai_summary=mock_aoai_summary,
        )

        mock_eval_run.log_metric.assert_not_called()

    @pytest.mark.asyncio
    async def test_no_metrics_when_joint_summary_none(
        self, integration, mock_eval_run, mock_red_team_info, mock_aoai_summary
    ):
        """None joint_risk_attack_summary → no metrics logged."""
        result = MagicMock(spec=RedTeamResult)
        result.scan_result = {
            "scorecard": {"joint_risk_attack_summary": None},
        }
        result.attack_details = []

        await integration.log_redteam_results_to_mlflow(
            redteam_result=result,
            eval_run=mock_eval_run,
            red_team_info=mock_red_team_info,
            aoai_summary=mock_aoai_summary,
        )

        mock_eval_run.log_metric.assert_not_called()

    @pytest.mark.asyncio
    async def test_scan_output_dir_writes_files(
        self,
        mock_logger,
        mock_azure_ai_project,
        mock_generated_rai_client,
        mock_redteam_result,
        mock_eval_run,
        mock_red_team_info,
        mock_aoai_summary,
        tmp_path,
    ):
        """With scan_output_dir set, files are written to disk."""
        scan_dir = str(tmp_path / "scan_output")
        os.makedirs(scan_dir, exist_ok=True)

        integration = MLflowIntegration(
            logger=mock_logger,
            azure_ai_project=mock_azure_ai_project,
            generated_rai_client=mock_generated_rai_client,
            one_dp_project=False,
            scan_output_dir=scan_dir,
        )

        # Use _skip_evals=True to avoid format_scorecard needing risk_category_summary
        await integration.log_redteam_results_to_mlflow(
            redteam_result=mock_redteam_result,
            eval_run=mock_eval_run,
            red_team_info=mock_red_team_info,
            _skip_evals=True,
            aoai_summary=mock_aoai_summary,
        )

        # Verify files were written to scan_output_dir
        assert os.path.exists(os.path.join(scan_dir, "results.json"))
        assert os.path.exists(os.path.join(scan_dir, "instance_results.json"))
        assert os.path.exists(os.path.join(scan_dir, "redteam_info.json"))

        # Verify results.json content
        with open(os.path.join(scan_dir, "results.json")) as f:
            results = json.load(f)
            assert results["id"] == "run-123"

        # Verify redteam_info.json strips evaluation_result
        with open(os.path.join(scan_dir, "redteam_info.json")) as f:
            info = json.load(f)
            assert "evaluation_result" not in info["baseline"]["Violence"]
            assert info["baseline"]["Violence"]["num_objectives"] == 2

    @pytest.mark.asyncio
    async def test_scan_output_dir_writes_scorecard_when_not_skip_evals(
        self,
        mock_logger,
        mock_azure_ai_project,
        mock_generated_rai_client,
        mock_eval_run,
        mock_red_team_info,
        mock_aoai_summary,
        tmp_path,
    ):
        """Scorecard is written when _skip_evals=False and scan_result exists."""
        scan_dir = str(tmp_path / "scan_output")
        os.makedirs(scan_dir, exist_ok=True)

        integration = MLflowIntegration(
            logger=mock_logger,
            azure_ai_project=mock_azure_ai_project,
            generated_rai_client=mock_generated_rai_client,
            one_dp_project=False,
            scan_output_dir=scan_dir,
        )

        result = MagicMock(spec=RedTeamResult)
        result.scan_result = {
            "scorecard": {"joint_risk_attack_summary": []},
        }
        result.attack_details = []

        # format_scorecard is a lazy import inside the method; patch at its source module
        with patch(
            "azure.ai.evaluation.red_team._utils.formatting_utils.format_scorecard",
            return_value="SCORECARD",
        ):
            await integration.log_redteam_results_to_mlflow(
                redteam_result=result,
                eval_run=mock_eval_run,
                red_team_info=mock_red_team_info,
                _skip_evals=False,
                aoai_summary=mock_aoai_summary,
            )

        assert os.path.exists(os.path.join(scan_dir, "scorecard.txt"))
        with open(os.path.join(scan_dir, "scorecard.txt")) as f:
            assert f.read() == "SCORECARD"

    @pytest.mark.asyncio
    async def test_raises_when_aoai_summary_none_with_scan_output_dir(
        self,
        mock_logger,
        mock_azure_ai_project,
        mock_generated_rai_client,
        mock_redteam_result,
        mock_eval_run,
        mock_red_team_info,
        tmp_path,
    ):
        """With scan_output_dir, aoai_summary=None raises ValueError."""
        scan_dir = str(tmp_path / "scan_output")
        os.makedirs(scan_dir, exist_ok=True)

        integration = MLflowIntegration(
            logger=mock_logger,
            azure_ai_project=mock_azure_ai_project,
            generated_rai_client=mock_generated_rai_client,
            one_dp_project=False,
            scan_output_dir=scan_dir,
        )

        with pytest.raises(ValueError, match="aoai_summary parameter is required"):
            await integration.log_redteam_results_to_mlflow(
                redteam_result=mock_redteam_result,
                eval_run=mock_eval_run,
                red_team_info=mock_red_team_info,
                aoai_summary=None,
            )


# ===========================================================================
# TestUpdateRunStatus
# ===========================================================================


@pytest.mark.unittest
class TestUpdateRunStatus:
    """Test update_run_status method."""

    def test_non_onedp_is_noop(self, integration, mock_eval_run):
        """Non-OneDP projects should return immediately."""
        integration.update_run_status(mock_eval_run, "Failed")
        integration.generated_rai_client._evaluation_onedp_client.update_red_team_run.assert_not_called()

    def test_onedp_updates_status(self, integration_onedp, mock_eval_run, mock_generated_rai_client):
        """OneDP: calls update_red_team_run with correct status."""
        integration_onedp.update_run_status(mock_eval_run, "Failed")

        mock_generated_rai_client._evaluation_onedp_client.update_red_team_run.assert_called_once()
        call_args = mock_generated_rai_client._evaluation_onedp_client.update_red_team_run.call_args
        assert call_args.kwargs["red_team"].status == "Failed"
        assert call_args.kwargs["name"] == mock_eval_run.id

    def test_onedp_logs_success(self, integration_onedp, mock_eval_run, mock_logger):
        """OneDP: successful update logs info."""
        integration_onedp.update_run_status(mock_eval_run, "Completed")
        mock_logger.info.assert_called()

    def test_onedp_failure_is_logged_not_raised(
        self, integration_onedp, mock_eval_run, mock_generated_rai_client, mock_logger
    ):
        """OneDP: failed update logs error but does not raise."""
        mock_generated_rai_client._evaluation_onedp_client.update_red_team_run.side_effect = Exception("boom")

        # Should not raise
        integration_onedp.update_run_status(mock_eval_run, "Failed")

        error_calls = [str(c) for c in mock_logger.error.call_args_list]
        assert any("boom" in c for c in error_calls)

    def test_onedp_uses_fallback_display_name(self, integration_onedp, mock_generated_rai_client):
        """OneDP: when display_name is None, generates a default."""
        run = MagicMock()
        run.id = "run-no-name"
        run.display_name = None

        integration_onedp.update_run_status(run, "Failed")

        call_args = mock_generated_rai_client._evaluation_onedp_client.update_red_team_run.call_args
        assert call_args.kwargs["red_team"].display_name.startswith("redteam-agent-")


# ===========================================================================
# TestBuildInstanceResultsPayload
# ===========================================================================


@pytest.mark.unittest
class TestBuildInstanceResultsPayload:
    """Test _build_instance_results_payload method."""

    def test_returns_scan_result_fields(self, integration, mock_redteam_result, mock_eval_run):
        payload = integration._build_instance_results_payload(
            redteam_result=mock_redteam_result,
            eval_run=mock_eval_run,
        )

        assert "scorecard" in payload
        assert "parameters" in payload
        assert "attack_details" in payload

    def test_filters_out_aoai_compatible_keys(self, integration, mock_eval_run):
        result = MagicMock(spec=RedTeamResult)
        result.scan_result = {
            "scorecard": {"data": 1},
            "AOAI_Compatible_Summary": {"should": "be_removed"},
            "AOAI_Compatible_Row_Results": [{"also": "removed"}],
            "parameters": {},
            "attack_details": [],
        }
        result.attack_details = []

        payload = integration._build_instance_results_payload(
            redteam_result=result,
            eval_run=mock_eval_run,
        )

        assert "AOAI_Compatible_Summary" not in payload
        assert "AOAI_Compatible_Row_Results" not in payload
        assert "scorecard" in payload

    def test_empty_scan_result_returns_defaults(self, integration, mock_eval_run):
        result = MagicMock(spec=RedTeamResult)
        result.scan_result = None
        result.attack_details = None

        payload = integration._build_instance_results_payload(
            redteam_result=result,
            eval_run=mock_eval_run,
        )

        assert payload["scorecard"] == {}
        assert payload["parameters"] == {}
        assert payload["attack_details"] == []

    def test_uses_redteam_result_attack_details_as_fallback(self, integration, mock_eval_run):
        result = MagicMock(spec=RedTeamResult)
        result.scan_result = {"scorecard": {}, "parameters": {}}
        result.attack_details = [{"detail": "from_result"}]

        payload = integration._build_instance_results_payload(
            redteam_result=result,
            eval_run=mock_eval_run,
        )

        assert payload["attack_details"] == [{"detail": "from_result"}]

    def test_scan_result_attack_details_preserved(self, integration, mock_eval_run):
        """When scan_result already has attack_details, use those."""
        result = MagicMock(spec=RedTeamResult)
        result.scan_result = {
            "scorecard": {},
            "parameters": {},
            "attack_details": [{"detail": "from_scan"}],
        }
        result.attack_details = [{"detail": "from_result_obj"}]

        payload = integration._build_instance_results_payload(
            redteam_result=result,
            eval_run=mock_eval_run,
        )

        assert payload["attack_details"] == [{"detail": "from_scan"}]


# ===========================================================================
# TestScanOutputDirFileCopying
# ===========================================================================


@pytest.mark.unittest
class TestScanOutputDirFileCopying:
    """Test file copying behavior when scan_output_dir is set."""

    @pytest.mark.asyncio
    async def test_skips_directories_and_log_files(
        self,
        mock_logger,
        mock_azure_ai_project,
        mock_generated_rai_client,
        mock_eval_run,
        mock_red_team_info,
        mock_aoai_summary,
        tmp_path,
    ):
        """Log files are skipped (unless DEBUG), directories skipped."""
        scan_dir = str(tmp_path / "scan_output")
        os.makedirs(scan_dir, exist_ok=True)
        # Create files that should/shouldn't be copied
        (tmp_path / "scan_output" / "data.json").write_text("{}")
        (tmp_path / "scan_output" / "debug.log").write_text("log data")
        (tmp_path / "scan_output" / ".gitignore").write_text("*")
        os.makedirs(os.path.join(scan_dir, "subdir"), exist_ok=True)

        result = MagicMock(spec=RedTeamResult)
        result.scan_result = {"scorecard": {"joint_risk_attack_summary": []}}
        result.attack_details = []

        integration = MLflowIntegration(
            logger=mock_logger,
            azure_ai_project=mock_azure_ai_project,
            generated_rai_client=mock_generated_rai_client,
            one_dp_project=False,
            scan_output_dir=scan_dir,
        )

        await integration.log_redteam_results_to_mlflow(
            redteam_result=result,
            eval_run=mock_eval_run,
            red_team_info=mock_red_team_info,
            _skip_evals=True,
            aoai_summary=mock_aoai_summary,
        )

        # data.json should have been copied (via log_artifact), .log and .gitignore should not
        copy_debug_calls = [str(c) for c in mock_logger.debug.call_args_list]
        assert any("data.json" in c for c in copy_debug_calls)
        # .gitignore should NOT be copied
        assert not any(".gitignore" in c and "Copied" in c for c in copy_debug_calls)

    @pytest.mark.asyncio
    async def test_file_copy_failure_warns(
        self,
        mock_logger,
        mock_azure_ai_project,
        mock_generated_rai_client,
        mock_eval_run,
        mock_red_team_info,
        mock_aoai_summary,
        tmp_path,
    ):
        """Failed file copy logs a warning."""
        scan_dir = str(tmp_path / "scan_output")
        os.makedirs(scan_dir, exist_ok=True)
        (tmp_path / "scan_output" / "data.json").write_text("{}")

        result = MagicMock(spec=RedTeamResult)
        result.scan_result = {"scorecard": {"joint_risk_attack_summary": []}}
        result.attack_details = []

        integration = MLflowIntegration(
            logger=mock_logger,
            azure_ai_project=mock_azure_ai_project,
            generated_rai_client=mock_generated_rai_client,
            one_dp_project=False,
            scan_output_dir=scan_dir,
        )

        with patch("shutil.copy", side_effect=PermissionError("access denied")):
            await integration.log_redteam_results_to_mlflow(
                redteam_result=result,
                eval_run=mock_eval_run,
                red_team_info=mock_red_team_info,
                _skip_evals=True,
                aoai_summary=mock_aoai_summary,
            )

        warning_calls = [str(c) for c in mock_logger.warning.call_args_list]
        assert any("Failed to copy file" in c for c in warning_calls)

    @pytest.mark.asyncio
    async def test_scan_output_dir_properties_include_path(
        self,
        mock_logger,
        mock_azure_ai_project,
        mock_generated_rai_client,
        mock_eval_run,
        mock_red_team_info,
        mock_aoai_summary,
        tmp_path,
    ):
        """Properties should include scan_output_dir when set."""
        scan_dir = str(tmp_path / "scan_output")
        os.makedirs(scan_dir, exist_ok=True)

        result = MagicMock(spec=RedTeamResult)
        result.scan_result = {"scorecard": {"joint_risk_attack_summary": []}}
        result.attack_details = []

        integration = MLflowIntegration(
            logger=mock_logger,
            azure_ai_project=mock_azure_ai_project,
            generated_rai_client=mock_generated_rai_client,
            one_dp_project=False,
            scan_output_dir=scan_dir,
        )

        await integration.log_redteam_results_to_mlflow(
            redteam_result=result,
            eval_run=mock_eval_run,
            red_team_info=mock_red_team_info,
            _skip_evals=True,
            aoai_summary=mock_aoai_summary,
        )

        props = mock_eval_run.write_properties_to_run_history.call_args.args[0]
        assert props["scan_output_dir"] == scan_dir
