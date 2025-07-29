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
from typing import Dict, Optional, cast
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
from ._red_team_result import RedTeamResult
from ._utils.logging_utils import log_error


class MLflowIntegration:
    """Handles MLflow integration for red team evaluations."""

    def __init__(self, logger, azure_ai_project, generated_rai_client, one_dp_project, 
                 scan_output_dir=None):
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

    async def log_redteam_results_to_mlflow(
        self,
        redteam_result: RedTeamResult,
        eval_run: EvalRun,
        red_team_info: Dict,
        _skip_evals: bool = False,
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
        :return: The URL to the run in Azure AI Studio, if available
        :rtype: Optional[str]
        """
        self.logger.debug(f"Logging results to MLFlow, _skip_evals={_skip_evals}")
        artifact_name = "instance_results.json"
        eval_info_name = "redteam_info.json"
        properties = {}

        with tempfile.TemporaryDirectory() as tmpdir:
            if self.scan_output_dir:
                artifact_path = os.path.join(self.scan_output_dir, artifact_name)
                self.logger.debug(f"Saving artifact to scan output directory: {artifact_path}")
                with open(artifact_path, "w", encoding=DefaultOpenEncoding.WRITE) as f:
                    if _skip_evals:
                        # In _skip_evals mode, we write the conversations in conversation/messages format
                        f.write(json.dumps({"conversations": redteam_result.attack_details or []}))
                    elif redteam_result.scan_result:
                        # Create a copy to avoid modifying the original scan result
                        result_with_conversations = (
                            redteam_result.scan_result.copy() if isinstance(redteam_result.scan_result, dict) else {}
                        )

                        # Preserve all original fields needed for scorecard generation
                        result_with_conversations["scorecard"] = result_with_conversations.get("scorecard", {})
                        result_with_conversations["parameters"] = result_with_conversations.get("parameters", {})

                        # Add conversations field with all conversation data including user messages
                        result_with_conversations["conversations"] = redteam_result.attack_details or []

                        # Keep original attack_details field to preserve compatibility with existing code
                        if (
                            "attack_details" not in result_with_conversations
                            and redteam_result.attack_details is not None
                        ):
                            result_with_conversations["attack_details"] = redteam_result.attack_details

                        json.dump(result_with_conversations, f)

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
                # First, create the main artifact file that MLFlow expects
                with open(
                    os.path.join(tmpdir, artifact_name),
                    "w",
                    encoding=DefaultOpenEncoding.WRITE,
                ) as f:
                    if _skip_evals:
                        f.write(json.dumps({"conversations": redteam_result.attack_details or []}))
                    elif redteam_result.scan_result:
                        json.dump(redteam_result.scan_result, f)

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
                artifact_file = Path(tmpdir) / artifact_name
                with open(artifact_file, "w", encoding=DefaultOpenEncoding.WRITE) as f:
                    if _skip_evals:
                        f.write(json.dumps({"conversations": redteam_result.attack_details or []}))
                    elif redteam_result.scan_result:
                        json.dump(redteam_result.scan_result, f)
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
                            name=uuid.uuid4(),
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
