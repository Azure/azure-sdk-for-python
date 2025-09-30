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
        results_name = "results.json"
        eval_info_name = "redteam_info.json"
        properties = {}

        with tempfile.TemporaryDirectory() as tmpdir:
            if self.scan_output_dir:
                # Save new format as results.json
                results_path = os.path.join(self.scan_output_dir, results_name)
                self.logger.debug(f"Saving results to scan output directory: {results_path}")
                with open(results_path, "w", encoding=DefaultOpenEncoding.WRITE) as f:
                    payload = self._build_results_payload(
                        redteam_result=redteam_result,
                        eval_run=eval_run,
                        red_team_info=red_team_info,
                        include_conversations=True,
                        scan_name=getattr(eval_run, "display_name", None),
                    )
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
                    payload = self._build_results_payload(
                        redteam_result=redteam_result,
                        eval_run=eval_run,
                        red_team_info=red_team_info,
                        include_conversations=False,
                        scan_name=getattr(eval_run, "display_name", None),
                    )
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
                    payload = self._build_results_payload(
                        redteam_result=redteam_result,
                        eval_run=eval_run,
                        red_team_info=red_team_info,
                        include_conversations=_skip_evals,
                        scan_name=getattr(eval_run, "display_name", None),
                    )
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

    @staticmethod
    def _compute_result_count(output_items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Aggregate run-level pass/fail counts from individual output items."""

        total = len(output_items)
        passed = failed = errored = 0

        for item in output_items:
            item_status: Optional[bool] = None
            for result in item.get("results", []):
                result_properties = result.get("properties", {}) if isinstance(result, dict) else {}
                attack_success = result_properties.get("attack_success")
                if attack_success is True:
                    item_status = False
                    break
                if attack_success is False:
                    item_status = True
                elif item_status is None and result.get("passed") is not None:
                    item_status = bool(result.get("passed"))

            if item_status is True:
                passed += 1
            elif item_status is False:
                failed += 1
            else:
                errored += 1

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "errored": errored,
        }

    @staticmethod
    def _compute_per_testing_criteria(output_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build aggregated pass/fail counts per testing criteria (risk category)."""

        criteria: Dict[str, Dict[str, int]] = {}

        for item in output_items:
            for result in item.get("results", []):
                if not isinstance(result, dict):
                    continue
                name = result.get("name")
                if not name:
                    continue
                passed_value = result.get("passed")
                if passed_value is None:
                    continue

                bucket = criteria.setdefault(str(name), {"passed": 0, "failed": 0})
                if passed_value:
                    bucket["passed"] += 1
                else:
                    bucket["failed"] += 1

        return [
            {
                "testing_criteria": criteria_name,
                "passed": counts["passed"],
                "failed": counts["failed"],
            }
            for criteria_name, counts in sorted(criteria.items())
        ]

    @staticmethod
    def _build_data_source_section(parameters: Dict[str, Any], red_team_info: Optional[Dict]) -> Dict[str, Any]:
        """Build the data_source portion of the run payload for red-team scans."""

        attack_strategies: List[str] = []
        if isinstance(red_team_info, dict):
            attack_strategies = sorted(str(strategy) for strategy in red_team_info.keys())

        item_generation_params: Dict[str, Any] = {"type": "red_team"}
        if attack_strategies:
            item_generation_params["attack_strategies"] = attack_strategies

        # Attempt to infer turns from parameters if available
        num_turns = parameters.get("max_turns") if isinstance(parameters, dict) else None
        if isinstance(num_turns, int) and num_turns > 0:
            item_generation_params["num_turns"] = num_turns

        data_source: Dict[str, Any] = {"type": "azure_ai_red_team", "target": {}}
        if item_generation_params:
            data_source["item_generation_params"] = item_generation_params

        return data_source

    def _determine_run_status(
        self,
        scan_result: Dict[str, Any],
        red_team_info: Optional[Dict],
        output_items: List[Dict[str, Any]],
    ) -> str:
        """Determine the run-level status based on red team info status values."""

        # Check if any tasks are still incomplete/failed
        if isinstance(red_team_info, dict):
            for risk_data in red_team_info.values():
                if not isinstance(risk_data, dict):
                    continue
                for details in risk_data.values():
                    if not isinstance(details, dict):
                        continue
                    status = details.get("status", "").lower()
                    if status in ("incomplete", "failed", "timeout"):
                        return "failed"
                    elif status in ("running", "pending"):
                        return "in_progress"

        return "completed"

    def _build_results_payload(
        self,
        redteam_result: RedTeamResult,
        eval_run: Optional[Any] = None,
        red_team_info: Optional[Dict] = None,
        include_conversations: bool = False,
        scan_name: Optional[str] = None,
    ) -> RedTeamRun:
        """Assemble the new structure for results.json with eval.run format."""

        scan_result = cast(Dict[str, Any], redteam_result.scan_result or {})
        output_items = cast(List[Dict[str, Any]], scan_result.get("output_items") or [])
        scorecard = cast(Dict[str, Any], scan_result.get("scorecard") or {})
        parameters = cast(Dict[str, Any], scan_result.get("parameters") or {})

        run_id = self._run_id_override
        eval_id = self._eval_id_override
        run_name: Optional[str] = None
        created_at = self._created_at_override

        if eval_run is not None:
            run_info = getattr(eval_run, "info", None)

            if run_id is None:
                candidate_run_id = (
                    getattr(run_info, "run_id", None)
                    or getattr(eval_run, "run_id", None)
                    or getattr(eval_run, "id", None)
                )
                if candidate_run_id is not None:
                    run_id = str(candidate_run_id)

            if eval_id is None:
                candidate_eval_id = (
                    getattr(run_info, "experiment_id", None)
                    or getattr(eval_run, "experiment_id", None)
                    or getattr(eval_run, "eval_id", None)
                )
                if candidate_eval_id is not None:
                    eval_id = str(candidate_eval_id)

            if run_name is None:
                candidate_run_name = (
                    getattr(run_info, "run_name", None)
                    or getattr(eval_run, "run_name", None)
                    or getattr(eval_run, "display_name", None)
                    or getattr(eval_run, "name", None)
                )
                if candidate_run_name is not None:
                    run_name = str(candidate_run_name)

            if created_at is None:
                raw_created = (
                    getattr(run_info, "created_time", None)
                    or getattr(eval_run, "created_at", None)
                    or getattr(eval_run, "created_time", None)
                )
                if isinstance(raw_created, datetime):
                    created_at = int(raw_created.timestamp())
                elif isinstance(raw_created, (int, float)):
                    created_at = int(raw_created)
                elif isinstance(raw_created, str):
                    try:
                        created_at = int(float(raw_created))
                    except ValueError:
                        created_at = None

        if run_id is None:
            run_id = str(uuid.uuid4())
        if eval_id is None:
            eval_id = str(uuid.uuid4())
        if created_at is None:
            created_at = int(datetime.now().timestamp())
        if run_name is None:
            run_name = scan_name or f"redteam-run-{run_id[:8]}"

        result_count = self._compute_result_count(output_items)
        per_testing_results = self._compute_per_testing_criteria(output_items)
        data_source = self._build_data_source_section(parameters, red_team_info)
        status = self._determine_run_status(scan_result, red_team_info, output_items)

        list_wrapper: OutputItemsList = {
            "object": "list",
            "data": output_items,
        }

        run_payload: RedTeamRun = {
            "object": "eval.run",
            "id": run_id,
            "eval_id": eval_id,
            "created_at": created_at,
            "status": status,
            "name": run_name,
            "report_url": scan_result.get("studio_url") or self.ai_studio_url,
            "data_source": data_source,
            "metadata": {},
            "result_count": result_count,
            "per_model_usage": [],
            "per_testing_criteria_results": per_testing_results,
            "output_items": list_wrapper,
        }

        if include_conversations:
            run_payload["conversations"] = redteam_result.attack_details or scan_result.get("attack_details") or []

        return run_payload

    def _build_results_payload(
        self,
        redteam_result: RedTeamResult,
        eval_run: Optional[Any] = None,
        red_team_info: Optional[Dict] = None,
        include_conversations: bool = False,
        scan_name: Optional[str] = None,
    ) -> RedTeamRun:
        """Assemble the new structure for results.json with eval.run format."""

        scan_result = cast(Dict[str, Any], redteam_result.scan_result or {})
        output_items = cast(List[Dict[str, Any]], scan_result.get("output_items") or [])
        scorecard = cast(Dict[str, Any], scan_result.get("scorecard") or {})
        parameters = cast(Dict[str, Any], scan_result.get("parameters") or {})

        run_id = self._run_id_override
        eval_id = self._eval_id_override
        run_name: Optional[str] = None
        created_at = self._created_at_override

        if eval_run is not None:
            run_info = getattr(eval_run, "info", None)

            if run_id is None:
                candidate_run_id = (
                    getattr(run_info, "run_id", None)
                    or getattr(eval_run, "run_id", None)
                    or getattr(eval_run, "id", None)
                )
                if candidate_run_id is not None:
                    run_id = str(candidate_run_id)

            if eval_id is None:
                candidate_eval_id = (
                    getattr(run_info, "experiment_id", None)
                    or getattr(eval_run, "experiment_id", None)
                    or getattr(eval_run, "eval_id", None)
                )
                if candidate_eval_id is not None:
                    eval_id = str(candidate_eval_id)

            if run_name is None:
                candidate_run_name = (
                    getattr(run_info, "run_name", None)
                    or getattr(eval_run, "run_name", None)
                    or getattr(eval_run, "display_name", None)
                    or getattr(eval_run, "name", None)
                )
                if candidate_run_name is not None:
                    run_name = str(candidate_run_name)

            if created_at is None:
                raw_created = (
                    getattr(run_info, "created_time", None)
                    or getattr(eval_run, "created_at", None)
                    or getattr(eval_run, "created_time", None)
                )
                if isinstance(raw_created, datetime):
                    created_at = int(raw_created.timestamp())
                elif isinstance(raw_created, (int, float)):
                    created_at = int(raw_created)
                elif isinstance(raw_created, str):
                    try:
                        created_at = int(float(raw_created))
                    except ValueError:
                        created_at = None

        if run_id is None:
            run_id = str(uuid.uuid4())
        if eval_id is None:
            eval_id = str(uuid.uuid4())
        if created_at is None:
            created_at = int(datetime.now().timestamp())
        if run_name is None:
            run_name = scan_name or f"redteam-run-{run_id[:8]}"

        result_count = self._compute_result_count(output_items)
        per_testing_results = self._compute_per_testing_criteria(output_items)
        data_source = self._build_data_source_section(parameters, red_team_info)
        status = self._determine_run_status(scan_result, red_team_info, output_items)

        list_wrapper: OutputItemsList = {
            "object": "list",
            "data": output_items,
        }

        run_payload: RedTeamRun = {
            "object": "eval.run",
            "id": run_id,
            "eval_id": eval_id,
            "created_at": created_at,
            "status": status,
            "name": run_name,
            "report_url": scan_result.get("studio_url") or self.ai_studio_url,
            "data_source": data_source,
            "metadata": {},
            "result_count": result_count,
            "per_model_usage": [],
            "per_testing_criteria_results": per_testing_results,
            "output_items": list_wrapper,
        }

        if include_conversations:
            run_payload["conversations"] = redteam_result.attack_details or scan_result.get("attack_details") or []

        return run_payload

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
        legacy_payload = scan_result.copy() if scan_result else {}

        # Ensure we have the basic required fields
        if "scorecard" not in legacy_payload:
            legacy_payload["scorecard"] = {}
        if "parameters" not in legacy_payload:
            legacy_payload["parameters"] = {}
        if "output_items" not in legacy_payload:
            legacy_payload["output_items"] = []
        if "attack_details" not in legacy_payload:
            legacy_payload["attack_details"] = redteam_result.attack_details or []

        return legacy_payload
