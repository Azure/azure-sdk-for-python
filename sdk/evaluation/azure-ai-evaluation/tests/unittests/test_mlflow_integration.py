# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for MLflowIntegration — ensures update_red_team_run fires reliably."""

import importlib
import pytest
from unittest.mock import MagicMock, patch

# _mlflow_integration transitively imports red_team._utils which requires
# redteam-extra dependencies (tenacity, httpx, tqdm).  Skip this entire
# module when those are not installed.
try:
    _mlflow_mod = importlib.import_module("azure.ai.evaluation.red_team._mlflow_integration")
    MLflowIntegration = _mlflow_mod.MLflowIntegration
except ImportError:
    pytest.skip("redteam extras not installed", allow_module_level=True)


def _make_mlflow_integration(*, one_dp_project=True):
    """Create an MLflowIntegration with mocked dependencies."""
    logger = MagicMock()
    generated_rai_client = MagicMock()
    return MLflowIntegration(
        logger=logger,
        azure_ai_project="https://fake.services.ai.azure.com/api/projects/fake",
        generated_rai_client=generated_rai_client,
        one_dp_project=one_dp_project,
    )


def _make_eval_run():
    """Create a mock eval_run object."""
    eval_run = MagicMock()
    eval_run.id = "test-run-id"
    eval_run.display_name = "test-run"
    return eval_run


def _make_redteam_result():
    """Create a minimal RedTeamResult-like mock for testing."""
    result = MagicMock()
    result.scan_result = {
        "scorecard": {"joint_risk_attack_summary": []},
        "parameters": {},
        "attack_details": [],
    }
    result.attack_details = []
    return result


def _make_aoai_summary():
    return {"output_items": {"data": []}, "scorecard": {}}


class TestUpdateRunAlwaysFires:
    """Verify update_red_team_run is called even when create_evaluation_result fails."""

    @pytest.mark.asyncio
    async def test_update_run_called_when_create_eval_result_fails(self):
        """If create_evaluation_result throws, update_red_team_run should still be called."""
        integration = _make_mlflow_integration(one_dp_project=True)
        eval_run = _make_eval_run()
        onedp_client = integration.generated_rai_client._evaluation_onedp_client

        # Make create_evaluation_result raise
        onedp_client.create_evaluation_result.side_effect = Exception("blob upload failed")

        # Make update succeed
        update_response = MagicMock()
        update_response.id = "updated-id"
        onedp_client.update_red_team_run.return_value = update_response

        with patch("tempfile.TemporaryDirectory") as mock_tmpdir:
            mock_tmpdir.return_value.__enter__ = MagicMock(return_value="/tmp/fake")
            mock_tmpdir.return_value.__exit__ = MagicMock(return_value=False)
            with patch("builtins.open", MagicMock()), patch("json.dump"):
                await integration.log_redteam_results_to_mlflow(
                    redteam_result=_make_redteam_result(),
                    eval_run=eval_run,
                    red_team_info={},
                    aoai_summary=_make_aoai_summary(),
                )

        # update_red_team_run must have been called despite create_evaluation_result failing
        onedp_client.update_red_team_run.assert_called_once()
        call_kwargs = onedp_client.update_red_team_run.call_args
        assert call_kwargs.kwargs["name"] == "test-run-id"
        red_team_arg = call_kwargs.kwargs["red_team"]
        assert red_team_arg.status == "Completed"
        # evaluationResultId should be absent since create failed
        assert "evaluationResultId" not in (red_team_arg.outputs or {})

    @pytest.mark.asyncio
    async def test_update_run_called_with_result_id_on_success(self):
        """On full success, update_red_team_run should include the evaluationResultId."""
        integration = _make_mlflow_integration(one_dp_project=True)
        eval_run = _make_eval_run()
        onedp_client = integration.generated_rai_client._evaluation_onedp_client

        # Make create succeed
        create_response = MagicMock()
        create_response.id = "eval-result-123"
        onedp_client.create_evaluation_result.return_value = create_response

        # Make update succeed
        update_response = MagicMock()
        update_response.id = "updated-id"
        onedp_client.update_red_team_run.return_value = update_response

        with patch("tempfile.TemporaryDirectory") as mock_tmpdir:
            mock_tmpdir.return_value.__enter__ = MagicMock(return_value="/tmp/fake")
            mock_tmpdir.return_value.__exit__ = MagicMock(return_value=False)
            with patch("builtins.open", MagicMock()), patch("json.dump"):
                await integration.log_redteam_results_to_mlflow(
                    redteam_result=_make_redteam_result(),
                    eval_run=eval_run,
                    red_team_info={},
                    aoai_summary=_make_aoai_summary(),
                )

        onedp_client.update_red_team_run.assert_called_once()
        red_team_arg = onedp_client.update_red_team_run.call_args.kwargs["red_team"]
        assert red_team_arg.outputs["evaluationResultId"] == "eval-result-123"

    @pytest.mark.asyncio
    async def test_update_run_error_logged_at_error_level(self):
        """If update_red_team_run itself fails, it should be logged at ERROR level."""
        integration = _make_mlflow_integration(one_dp_project=True)
        eval_run = _make_eval_run()
        onedp_client = integration.generated_rai_client._evaluation_onedp_client

        # Both calls fail
        onedp_client.create_evaluation_result.side_effect = Exception("create failed")
        onedp_client.update_red_team_run.side_effect = Exception("update failed")

        with patch("tempfile.TemporaryDirectory") as mock_tmpdir:
            mock_tmpdir.return_value.__enter__ = MagicMock(return_value="/tmp/fake")
            mock_tmpdir.return_value.__exit__ = MagicMock(return_value=False)
            with patch("builtins.open", MagicMock()), patch("json.dump"):
                await integration.log_redteam_results_to_mlflow(
                    redteam_result=_make_redteam_result(),
                    eval_run=eval_run,
                    red_team_info={},
                    aoai_summary=_make_aoai_summary(),
                )

        # Verify error-level logging for both failures
        error_messages = [str(c) for c in integration.logger.error.call_args_list]
        assert any("create" in m.lower() for m in error_messages)
        assert any("update" in m.lower() for m in error_messages)


class TestUpdateRunStatusHelper:
    """Test the update_run_status helper method."""

    def test_update_run_status_calls_update(self):
        integration = _make_mlflow_integration(one_dp_project=True)
        eval_run = _make_eval_run()
        onedp_client = integration.generated_rai_client._evaluation_onedp_client

        integration.update_run_status(eval_run, "Failed")

        onedp_client.update_red_team_run.assert_called_once()
        red_team_arg = onedp_client.update_red_team_run.call_args.kwargs["red_team"]
        assert red_team_arg.status == "Failed"

    def test_update_run_status_noop_for_non_onedp(self):
        integration = _make_mlflow_integration(one_dp_project=False)
        eval_run = _make_eval_run()
        onedp_client = integration.generated_rai_client._evaluation_onedp_client

        integration.update_run_status(eval_run, "Failed")

        onedp_client.update_red_team_run.assert_not_called()

    def test_update_run_status_swallows_exception(self):
        integration = _make_mlflow_integration(one_dp_project=True)
        eval_run = _make_eval_run()
        onedp_client = integration.generated_rai_client._evaluation_onedp_client
        onedp_client.update_red_team_run.side_effect = Exception("network error")

        # Should not raise
        integration.update_run_status(eval_run, "Failed")

        integration.logger.error.assert_called_once()
