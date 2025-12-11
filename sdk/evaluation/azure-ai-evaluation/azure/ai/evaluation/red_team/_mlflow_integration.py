# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
MLflow integration module for Red Team Agent.

This module handles MLflow run creation, logging, and tracking for red team evaluations.
"""

import json
import os
import tempfile
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, cast
from pathlib import Path

# Azure AI Evaluation imports
from azure.ai.evaluation._evaluate._eval_run import EvalRun
from azure.ai.evaluation._evaluate._utils import _trace_destination_from_project_scope, _get_ai_studio_url
from azure.ai.evaluation._evaluate._utils import extract_workspace_triad_from_trace_provider
from azure.ai.evaluation._version import VERSION
from azure.ai.evaluation._azure._clients import LiteMLClient
from azure.ai.evaluation._constants import EvaluationRunProperties, DefaultOpenEncoding
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from azure.ai.evaluation._common import RedTeamUpload, ResultType
from azure.ai.evaluation._model_configurations import AzureAIProject

# Local imports
from ._red_team_result import (
    RedTeamResult,
    RedTeamRun,
    ResultCount,
    PerTestingCriteriaResult,
    DataSource,
    OutputItemsList,
)
from ._utils.logging_utils import log_error


class MLflowIntegration:
    """Handles MLflow integration for red team evaluations."""

    def __init__(self, logger, azure_ai_project, generated_rai_client, one_dp_project, scan_output_dir=None):
        """Initialize the MLflow integration.

        :param logger: Logger instance for logging
        :param azure_ai_project: Azure AI project configuration
        :param generated_rai_client: RAI client for service interactions
        :param one_dp_project: Whether this is a OneDP project
        :param scan_output_dir: Directory for scan outputs
        """
        self.logger = logger
        self.azure_ai_project = azure_ai_project
        self.generated_rai_client = generated_rai_client
        self._one_dp_project = one_dp_project
        self.scan_output_dir = scan_output_dir
        self.ai_studio_url = None
        self.trace_destination = None
        self._run_id_override: Optional[str] = None
        self._eval_id_override: Optional[str] = None
        self._created_at_override: Optional[int] = None

    def set_run_identity_overrides(
        self,
        *,
        run_id: Optional[str] = None,
        eval_id: Optional[str] = None,
        created_at: Optional[Any] = None,
    ) -> None:
        """Allow callers to supply pre-existing identifiers for the run payload."""

        self._run_id_override = str(run_id).strip() if run_id else None
        self._eval_id_override = str(eval_id).strip() if eval_id else None

        if created_at is None or created_at == "":
            self._created_at_override = None
        else:
            if isinstance(created_at, datetime):
                self._created_at_override = int(created_at.timestamp())
            else:
                try:
                    self._created_at_override = int(created_at)
                except (TypeError, ValueError):
                    self._created_at_override = None

    def start_redteam_mlflow_run(
        self,
        azure_ai_project: Optional[AzureAIProject] = None,
        run_name: Optional[str] = None,
    ) -> EvalRun:
        """Start an MLFlow run for the Red Team Agent evaluation.

        :param azure_ai_project: Azure AI project details for logging
        :type azure_ai_project: Optional[AzureAIProject]
        :param run_name: Optional name for the MLFlow run
        :type run_name: Optional[str]
        :return: The MLFlow run object
        :rtype: EvalRun
        :raises EvaluationException: If no azure_ai_project is provided or trace destination cannot be determined
        """
        if not azure_ai_project:
            log_error(self.logger, "No azure_ai_project provided, cannot upload run")
            raise EvaluationException(
                message="No azure_ai_project provided",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.MISSING_FIELD,
                target=ErrorTarget.RED_TEAM,
            )

        if self._one_dp_project:
            response = self.generated_rai_client._evaluation_onedp_client.start_red_team_run(
                red_team=RedTeamUpload(
                    display_name=run_name or f"redteam-agent-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                )
            )

            self.ai_studio_url = response.properties.get("AiStudioEvaluationUri")
            return response

        else:
            trace_destination = _trace_destination_from_project_scope(azure_ai_project)
            if not trace_destination:
                self.logger.warning("Could not determine trace destination from project scope")
                raise EvaluationException(
                    message="Could not determine trace destination",
                    blame=ErrorBlame.SYSTEM_ERROR,
                    category=ErrorCategory.UNKNOWN,
                    target=ErrorTarget.RED_TEAM,
                )

            ws_triad = extract_workspace_triad_from_trace_provider(trace_destination)

            management_client = LiteMLClient(
                subscription_id=ws_triad.subscription_id,
                resource_group=ws_triad.resource_group_name,
                logger=self.logger,
                credential=azure_ai_project.get("credential"),
            )

            tracking_uri = management_client.workspace_get_info(ws_triad.workspace_name).ml_flow_tracking_uri

            run_display_name = run_name or f"redteam-agent-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            self.logger.debug(f"Starting MLFlow run with name: {run_display_name}")
            eval_run = EvalRun(
                run_name=run_display_name,
                tracking_uri=cast(str, tracking_uri),
                subscription_id=ws_triad.subscription_id,
                group_name=ws_triad.resource_group_name,
                workspace_name=ws_triad.workspace_name,
                management_client=management_client,
            )
            eval_run._start_run()
            self.logger.debug(f"MLFlow run started successfully with ID: {eval_run.info.run_id}")

            self.trace_destination = trace_destination
            self.logger.debug(f"MLFlow run created successfully with ID: {eval_run}")

            self.ai_studio_url = _get_ai_studio_url(
                trace_destination=self.trace_destination,
                evaluation_id=eval_run.info.run_id,
            )

            return eval_run

    def test_storage_upload(self) -> bool:
        """Test storage account connectivity before starting the scan.

        This method validates that storage upload will work by testing with the
        appropriate client (OneDP or MLFlow) depending on project configuration.

        :return: True if the test upload succeeds
        :rtype: bool
        :raises EvaluationException: If the storage account is inaccessible or lacks permissions
        """
        if self._one_dp_project:
            # For OneDP projects, test using the evaluation client
            return self.generated_rai_client._evaluation_onedp_client.test_storage_upload()
        else:
            # For non-OneDP projects (MLFlow), we don't have a direct upload test
            # Storage is tested when we create artifacts during log_artifact
            # So we just return True here and let the actual upload fail if there are issues
            self.logger.debug("Storage upload test skipped for non-OneDP project (will be tested during actual upload)")
            return True

    async def log_redteam_results_to_mlflow(
        self,
        redteam_result: RedTeamResult,
        eval_run: EvalRun,
        red_team_info: Dict,
        _skip_evals: bool = False,
        aoai_summary: Optional["RedTeamRun"] = None,
    ) -> Optional[str]:
        """Log the Red Team Agent results to MLFlow.

        :param redteam_result: The output from the red team agent evaluation
        :type redteam_result: RedTeamResult
        :param eval_run: The MLFlow run object
        :type eval_run: EvalRun
        :param red_team_info: Red team tracking information
        :type red_team_info: Dict
        :param _skip_evals: Whether to log only data without evaluation results
        :type _skip_evals: bool
        :param aoai_summary: Pre-built AOAI-compatible summary (optional, will be built if not provided)
        :type aoai_summary: Optional[RedTeamRun]
        :return: The URL to the run in Azure AI Studio, if available
        :rtype: Optional[str]
        """
        self.logger.debug(f"Logging results to MLFlow, _skip_evals={_skip_evals}")
        artifact_name = "instance_results.json"
        results_name = "results.json"
        eval_info_name = "redteam_info.json"
        properties = {}

        with tempfile.TemporaryDirectory() as tmpdir:
            if self.scan_output_dir:
                # Save new format as results.json
                results_path = os.path.join(self.scan_output_dir, results_name)
                self.logger.debug(f"Saving results to scan output directory: {results_path}")
                with open(results_path, "w", encoding=DefaultOpenEncoding.WRITE) as f:
                    # Use provided aoai_summary
                    if aoai_summary is None:
                        self.logger.error("aoai_summary must be provided to log_redteam_results_to_mlflow")
                        raise ValueError("aoai_summary parameter is required but was not provided")

                    payload = dict(aoai_summary)  # Make a copy
                    json.dump(payload, f)

                # Save legacy format as instance_results.json
                artifact_path = os.path.join(self.scan_output_dir, artifact_name)
                self.logger.debug(f"Saving artifact to scan output directory: {artifact_path}")
                with open(artifact_path, "w", encoding=DefaultOpenEncoding.WRITE) as f:
                    legacy_payload = self._build_instance_results_payload(
                        redteam_result=redteam_result,
                        eval_run=eval_run,
                        red_team_info=red_team_info,
                        scan_name=getattr(eval_run, "display_name", None),
                    )
                    json.dump(legacy_payload, f)

                eval_info_path = os.path.join(self.scan_output_dir, eval_info_name)
                self.logger.debug(f"Saving evaluation info to scan output directory: {eval_info_path}")
                with open(eval_info_path, "w", encoding=DefaultOpenEncoding.WRITE) as f:
                    # Remove evaluation_result from red_team_info before logging
                    red_team_info_logged = {}
                    for strategy, harms_dict in red_team_info.items():
                        red_team_info_logged[strategy] = {}
                        for harm, info_dict in harms_dict.items():
                            # Create a copy to avoid modifying the original
                            info_dict_copy = info_dict.copy()
                            info_dict_copy.pop("evaluation_result", None)
                            red_team_info_logged[strategy][harm] = info_dict_copy
                    f.write(json.dumps(red_team_info_logged, indent=2))
                self.logger.debug(f"Successfully wrote redteam_info.json to: {eval_info_path}")

                # Also save a human-readable scorecard if available
                if not _skip_evals and redteam_result.scan_result:
                    from ._utils.formatting_utils import format_scorecard

                    scorecard_path = os.path.join(self.scan_output_dir, "scorecard.txt")
                    with open(scorecard_path, "w", encoding=DefaultOpenEncoding.WRITE) as f:
                        f.write(format_scorecard(redteam_result.scan_result))
                    self.logger.debug(f"Saved scorecard to: {scorecard_path}")

                # Create a dedicated artifacts directory with proper structure for MLFlow
                # First, create the main artifact file that MLFlow expects (new format)
                with open(
                    os.path.join(tmpdir, results_name),
                    "w",
                    encoding=DefaultOpenEncoding.WRITE,
                ) as f:
                    # Use provided aoai_summary (required)
                    if aoai_summary is None:
                        self.logger.error("aoai_summary must be provided to log_redteam_results_to_mlflow")
                        raise ValueError("aoai_summary parameter is required but was not provided")

                    payload = dict(aoai_summary)  # Make a copy
                    # Remove conversations for MLFlow artifact
                    payload.pop("conversations", None)
                    json.dump(payload, f)

                # Also create legacy instance_results.json for compatibility
                with open(
                    os.path.join(tmpdir, artifact_name),
                    "w",
                    encoding=DefaultOpenEncoding.WRITE,
                ) as f:
                    legacy_payload = self._build_instance_results_payload(
                        redteam_result=redteam_result,
                        eval_run=eval_run,
                        red_team_info=red_team_info,
                        scan_name=getattr(eval_run, "display_name", None),
                    )
                    json.dump(legacy_payload, f)

                # Copy all relevant files to the temp directory
                import shutil

                for file in os.listdir(self.scan_output_dir):
                    file_path = os.path.join(self.scan_output_dir, file)

                    # Skip directories and log files if not in debug mode
                    if os.path.isdir(file_path):
                        continue
                    if file.endswith(".log") and not os.environ.get("DEBUG"):
                        continue
                    if file.endswith(".gitignore"):
                        continue
                    if file == artifact_name:
                        continue

                    try:
                        shutil.copy(file_path, os.path.join(tmpdir, file))
                        self.logger.debug(f"Copied file to artifact directory: {file}")
                    except Exception as e:
                        self.logger.warning(f"Failed to copy file {file} to artifact directory: {str(e)}")

                properties.update({"scan_output_dir": str(self.scan_output_dir)})
            else:
                # Use temporary directory as before if no scan output directory exists
                results_file = Path(tmpdir) / results_name
                with open(results_file, "w", encoding=DefaultOpenEncoding.WRITE) as f:
                    # Use provided aoai_summary (required)
                    if aoai_summary is None:
                        self.logger.error("aoai_summary must be provided to log_redteam_results_to_mlflow")
                        raise ValueError("aoai_summary parameter is required but was not provided")

                    payload = dict(aoai_summary)  # Make a copy
                    # Include conversations only if _skip_evals is True
                    if _skip_evals and "conversations" not in payload:
                        payload["conversations"] = (
                            redteam_result.attack_details or redteam_result.scan_result.get("attack_details") or []
                        )
                    elif not _skip_evals:
                        payload.pop("conversations", None)
                    json.dump(payload, f)
                self.logger.debug(f"Logged artifact: {results_name}")

                # Also create legacy instance_results.json
                artifact_file = Path(tmpdir) / artifact_name
                with open(artifact_file, "w", encoding=DefaultOpenEncoding.WRITE) as f:
                    legacy_payload = self._build_instance_results_payload(
                        redteam_result=redteam_result,
                        eval_run=eval_run,
                        red_team_info=red_team_info,
                        scan_name=getattr(eval_run, "display_name", None),
                    )
                    json.dump(legacy_payload, f)
                self.logger.debug(f"Logged artifact: {artifact_name}")

            properties.update(
                {
                    "redteaming": "asr",
                    EvaluationRunProperties.EVALUATION_SDK: f"azure-ai-evaluation:{VERSION}",
                }
            )

            metrics = {}
            if redteam_result.scan_result:
                scorecard = redteam_result.scan_result["scorecard"]
                joint_attack_summary = scorecard["joint_risk_attack_summary"]

                if joint_attack_summary:
                    for risk_category_summary in joint_attack_summary:
                        risk_category = risk_category_summary.get("risk_category").lower()
                        for key, value in risk_category_summary.items():
                            if key != "risk_category":
                                metrics.update({f"{risk_category}_{key}": cast(float, value)})
                                self.logger.debug(f"Logged metric: {risk_category}_{key} = {value}")

            if self._one_dp_project:
                try:
                    create_evaluation_result_response = (
                        self.generated_rai_client._evaluation_onedp_client.create_evaluation_result(
                            name=str(uuid.uuid4()),
                            path=tmpdir,
                            metrics=metrics,
                            result_type=ResultType.REDTEAM,
                        )
                    )

                    update_run_response = self.generated_rai_client._evaluation_onedp_client.update_red_team_run(
                        name=eval_run.id,
                        red_team=RedTeamUpload(
                            id=eval_run.id,
                            display_name=eval_run.display_name
                            or f"redteam-agent-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                            status="Completed",
                            outputs={
                                "evaluationResultId": create_evaluation_result_response.id,
                            },
                            properties=properties,
                        ),
                    )
                    self.logger.debug(f"Updated UploadRun: {update_run_response.id}")
                except Exception as e:
                    self.logger.warning(f"Failed to upload red team results to AI Foundry: {str(e)}")
            else:
                # Log the entire directory to MLFlow
                try:
                    eval_run.log_artifact(tmpdir, artifact_name)
                    if self.scan_output_dir:
                        eval_run.log_artifact(tmpdir, eval_info_name)
                    self.logger.debug(f"Successfully logged artifacts directory to AI Foundry")
                except Exception as e:
                    self.logger.warning(f"Failed to log artifacts to AI Foundry: {str(e)}")

                for k, v in metrics.items():
                    eval_run.log_metric(k, v)
                    self.logger.debug(f"Logged metric: {k} = {v}")

                eval_run.write_properties_to_run_history(properties)
                eval_run._end_run("FINISHED")

        self.logger.info("Successfully logged results to AI Foundry")
        return None

    def _build_instance_results_payload(
        self,
        redteam_result: RedTeamResult,
        eval_run: Optional[Any] = None,
        red_team_info: Optional[Dict] = None,
        scan_name: Optional[str] = None,
    ) -> Dict:
        """Assemble the legacy structure for instance_results.json (scan_result format)."""

        scan_result = cast(Dict[str, Any], redteam_result.scan_result or {})

        # Return the scan_result directly for legacy compatibility
        # This maintains the old format that was expected previously
        # Filter out AOAI_Compatible properties - those belong in results.json only
        legacy_payload = (
            {
                k: v
                for k, v in scan_result.items()
                if k not in ["AOAI_Compatible_Summary", "AOAI_Compatible_Row_Results"]
            }
            if scan_result
            else {}
        )

        # Ensure we have the basic required fields
        if "scorecard" not in legacy_payload:
            legacy_payload["scorecard"] = {}
        if "parameters" not in legacy_payload:
            legacy_payload["parameters"] = {}
        if "attack_details" not in legacy_payload:
            legacy_payload["attack_details"] = redteam_result.attack_details or []

        return legacy_payload
