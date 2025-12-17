# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Evaluation processing module for Red Team Agent.

This module handles the evaluation of conversations against risk categories,
processing evaluation results, and managing evaluation workflows.
"""

import asyncio
import json
import os
import tempfile
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Union
from pathlib import Path
from tqdm import tqdm

# Retry imports
import httpx
import httpcore
from tenacity import retry

# Azure AI Evaluation imports
from azure.ai.evaluation._constants import EVALUATION_PASS_FAIL_MAPPING
from azure.ai.evaluation._common.rai_service import evaluate_with_rai_service_sync
from azure.ai.evaluation._common.utils import get_default_threshold_for_evaluator, is_onedp_project
from azure.ai.evaluation._evaluate._utils import _write_output

# Local imports
from ._attack_strategy import AttackStrategy
from ._attack_objective_generator import RiskCategory
from ._utils.constants import RESULTS_EXT, TASK_STATUS
from ._utils.metric_mapping import (
    get_annotation_task_from_risk_category,
    get_metric_from_risk_category,
    get_attack_objective_from_risk_category,
)
from ._utils.logging_utils import log_error
from ._utils.formatting_utils import get_strategy_name


class EvaluationProcessor:
    """Handles evaluation of red team attack conversations."""

    def __init__(
        self,
        logger,
        azure_ai_project,
        credential,
        attack_success_thresholds,
        retry_config,
        scan_session_id=None,
        scan_output_dir=None,
        taxonomy_risk_categories=None,
    ):
        """Initialize the evaluation processor.

        :param logger: Logger instance for logging
        :param azure_ai_project: Azure AI project configuration
        :param credential: Authentication credential
        :param attack_success_thresholds: Configured attack success thresholds
        :param retry_config: Retry configuration for network errors
        :param scan_session_id: Session ID for the current scan
        :param scan_output_dir: Directory for scan outputs
        :param taxonomy_risk_categories: Dictionary mapping risk categories to taxonomy values
        """
        self.logger = logger
        self.azure_ai_project = azure_ai_project
        self.credential = credential
        self.attack_success_thresholds = attack_success_thresholds
        self.retry_config = retry_config
        self.scan_session_id = scan_session_id
        self.scan_output_dir = scan_output_dir
        self.taxonomy_risk_categories = taxonomy_risk_categories or {}

    async def evaluate_conversation(
        self,
        conversation: Dict,
        metric_name: str,
        strategy_name: str,
        risk_category: RiskCategory,
        idx: int,
        risk_sub_type: Optional[str] = None,
    ) -> Dict:
        """Evaluate a single conversation using the specified metric and risk category.

        :param conversation: Dictionary containing the conversation to evaluate
        :type conversation: Dict
        :param metric_name: Name of the evaluation metric to apply
        :type metric_name: str
        :param strategy_name: Name of the attack strategy used in the conversation
        :type strategy_name: str
        :param risk_category: Risk category to evaluate against
        :type risk_category: RiskCategory
        :param idx: Index of the conversation for tracking purposes
        :type idx: int
        :param risk_sub_type: Optional risk sub type for the evaluation
        :type risk_sub_type: Optional[str]
        :return: Dictionary containing evaluation results
        :rtype: Dict
        """
        annotation_task = get_annotation_task_from_risk_category(risk_category)

        messages = conversation["conversation"]["messages"]

        # Extract all assistant messages for evaluation
        assistant_messages = [msg["content"] for msg in messages if msg.get("role") == "assistant"]

        context = [msg["context"] for msg in messages if msg.get("role") == "user"]
        tool_calls = [
            msg.get("tool_calls", []) for msg in messages if msg.get("role") == "assistant" and msg.get("tool_calls")
        ]

        if assistant_messages:
            # Create query-response pair with empty query and all assistant messages
            query_response = {
                "query": "query",
                "response": " ".join(assistant_messages),
                "scenario": "redteam",
            }

            # Add context to query_response if found
            if context and context[0] is not None:
                # If context is a string, wrap it in the expected format for the RAI service
                context_value = context[0]
                if isinstance(context_value, str):
                    query_response["context"] = {"contexts": [{"content": context_value}]}
                else:
                    query_response["context"] = context_value

            if tool_calls and any(tool_calls):
                query_response["tool_calls"] = [call for sublist in tool_calls for call in sublist if call]

            # Add risk_sub_type to query_response if it exists
            if risk_sub_type:
                query_response["risk_sub_type"] = risk_sub_type

            # Add taxonomy to query_response if it exists for this risk category
            if self.taxonomy_risk_categories and risk_category.value in self.taxonomy_risk_categories:
                taxonomy_value = self.taxonomy_risk_categories[risk_category.value]
                # Convert taxonomy to string if it's not already a string
                if taxonomy_value is not None:
                    query_response["taxonomy"] = str(taxonomy_value)

            try:
                self.logger.debug(f"Evaluating conversation {idx+1} for {risk_category.value}/{strategy_name}")

                use_sync_endpoint = is_onedp_project(self.azure_ai_project)
                effective_metric_name = (
                    "hate_unfairness" if use_sync_endpoint and metric_name == "hate_fairness" else metric_name
                )

                @retry(**self.retry_config["network_retry"])
                async def evaluate_with_rai_service_with_retry():
                    try:
                        # Always use sync_evals endpoint for all projects
                        return await evaluate_with_rai_service_sync(
                            data=query_response,
                            metric_name=metric_name,
                            project_scope=self.azure_ai_project,
                            credential=self.credential,
                            annotation_task=annotation_task,
                            scan_session_id=self.scan_session_id,
                        )
                    except (
                        httpx.ConnectTimeout,
                        httpx.ReadTimeout,
                        httpx.ConnectError,
                        httpx.HTTPError,
                        httpx.TimeoutException,
                        ConnectionError,
                        ConnectionRefusedError,
                        ConnectionResetError,
                        TimeoutError,
                        OSError,
                        IOError,
                    ) as e:
                        self.logger.warning(
                            f"Network error while evaluating conversation {idx+1} for {risk_category.value}/{strategy_name}: {type(e).__name__}: {str(e)}"
                        )
                        await asyncio.sleep(2)
                        raise

                # Call the retry-enabled function
                evaluate_output = await evaluate_with_rai_service_with_retry()

                # Create a row with the format expected by result processing
                row = {"inputs.conversation": {"messages": messages}}

                # Check if we got an EvalRunOutputItem (from sync_evals) or legacy dict format
                risk_cat_value = risk_category.value

                # Handle EvalRunOutputItem format (from sync_evals for OneDP)
                if hasattr(evaluate_output, "results") or (
                    isinstance(evaluate_output, dict) and "results" in evaluate_output
                ):
                    # Extract results from EvalRunOutputItem
                    results = (
                        evaluate_output.results
                        if hasattr(evaluate_output, "results")
                        else evaluate_output.get("results", [])
                    )

                    # Find the result matching our metric/risk category
                    eval_result = None
                    lookup_names = {metric_name, risk_cat_value, effective_metric_name}
                    for result_item in results:
                        result_dict = result_item if isinstance(result_item, dict) else result_item.__dict__
                        result_name = str(result_dict.get("name") or "")
                        metric_field = str(result_dict.get("metric") or "")
                        if result_name in lookup_names or metric_field in lookup_names:
                            eval_result = result_dict
                            break

                    if eval_result:
                        # Extract values from EvalRunOutputItem result format
                        score = eval_result.get("score", 0)
                        reason = eval_result.get("reason", "")

                        # Convert score to severity label if needed
                        severity_label = eval_result.get("label")
                        if severity_label is None:
                            # Calculate severity from score
                            from azure.ai.evaluation._common.utils import get_harm_severity_level

                            severity_label = get_harm_severity_level(score)

                        row[f"outputs.{risk_cat_value}.{risk_cat_value}"] = severity_label
                        row[f"outputs.{risk_cat_value}.{risk_cat_value}_reason"] = reason
                        row[f"outputs.{risk_cat_value}.{risk_cat_value}_score"] = score

                        # Store the EvalRunOutputItem as dict for new format processing
                        # Use model's serialization method or JSON round-trip
                        if hasattr(evaluate_output, "as_dict"):
                            row["_eval_run_output_item"] = evaluate_output.as_dict()
                        elif hasattr(evaluate_output, "model_dump"):
                            row["_eval_run_output_item"] = evaluate_output.model_dump()
                        else:
                            # Fallback: JSON serialize and parse back
                            row["_eval_run_output_item"] = json.loads(
                                json.dumps(evaluate_output, default=lambda o: o.__dict__)
                            )

                        # Add result field based on score and threshold comparison
                        # Get pattern-specific default threshold for this evaluator
                        default_threshold = get_default_threshold_for_evaluator(risk_cat_value)

                        # Content safety evaluators use "lower is better" scoring by default
                        # If attack success thresholds are configured for this category, use them
                        if risk_cat_value in self.attack_success_thresholds:
                            attack_threshold = self.attack_success_thresholds[risk_cat_value]
                            row[f"outputs.{risk_cat_value}.{risk_cat_value}_threshold"] = attack_threshold
                            result = int(score) <= int(attack_threshold)
                            self.logger.debug(f"Using attack success threshold {attack_threshold} for {risk_cat_value}")
                            self.logger.debug(f"Score: {score}, Attack Threshold: {attack_threshold}, Pass: {result}")
                        else:
                            # Store the default threshold in the results for transparency
                            row[f"outputs.{risk_cat_value}.{risk_cat_value}_threshold"] = default_threshold
                            result = int(score) <= int(default_threshold)
                            self.logger.debug(f"Using default threshold {default_threshold} for {risk_cat_value}")
                            self.logger.debug(f"Score: {score}, Default Threshold: {default_threshold}, Pass: {result}")

                        row[f"outputs.{risk_cat_value}.{risk_cat_value}_result"] = EVALUATION_PASS_FAIL_MAPPING[result]
                        self.logger.debug(
                            f"Successfully evaluated conversation {idx+1} for {risk_category.value}/{strategy_name}"
                        )
                        return row

                # Handle legacy dict format (from evaluate_with_rai_service)
                if evaluate_output and isinstance(evaluate_output, dict):
                    if risk_cat_value in evaluate_output:
                        row[f"outputs.{risk_cat_value}.{risk_cat_value}"] = evaluate_output.get(risk_cat_value)
                        row[f"outputs.{risk_cat_value}.{risk_cat_value}_reason"] = evaluate_output.get(
                            f"{risk_cat_value}_reason", ""
                        )
                        row[f"outputs.{risk_cat_value}.{risk_cat_value}_score"] = evaluate_output.get(
                            f"{risk_cat_value}_score", 0
                        )

                        # Add result field based on score and threshold comparison
                        score = evaluate_output.get(f"{risk_cat_value}_score", 0)
                        # Get pattern-specific default threshold for this evaluator
                        default_threshold = evaluate_output.get(
                            f"{risk_cat_value}_threshold", get_default_threshold_for_evaluator(risk_cat_value)
                        )

                        # Content safety evaluators use "lower is better" scoring by default
                        # If attack success thresholds are configured for this category, use them
                        if risk_cat_value in self.attack_success_thresholds:
                            attack_threshold = self.attack_success_thresholds[risk_cat_value]
                            row[f"outputs.{risk_cat_value}.{risk_cat_value}_threshold"] = attack_threshold
                            result = int(score) <= int(attack_threshold)
                            self.logger.debug(f"Using attack success threshold {attack_threshold} for {risk_cat_value}")
                            self.logger.debug(f"Score: {score}, Attack Threshold: {attack_threshold}, Pass: {result}")
                        else:
                            # Store the default threshold in the results for transparency
                            row[f"outputs.{risk_cat_value}.{risk_cat_value}_threshold"] = default_threshold
                            result = int(score) <= int(default_threshold)
                            self.logger.debug(f"Using default threshold {default_threshold} for {risk_cat_value}")
                            self.logger.debug(f"Score: {score}, Default Threshold: {default_threshold}, Pass: {result}")

                        row[f"outputs.{risk_cat_value}.{risk_cat_value}_result"] = EVALUATION_PASS_FAIL_MAPPING[result]
                        self.logger.debug(
                            f"Successfully evaluated conversation {idx+1} for {risk_category.value}/{strategy_name}"
                        )
                        return row
                    else:
                        if risk_cat_value in self.attack_success_thresholds:
                            self.logger.warning(
                                "Unable to use attack success threshold for evaluation as the evaluator does not return a score."
                            )

                        result = evaluate_output.get(f"{risk_cat_value}_label", "")
                        row[f"outputs.{risk_cat_value}.{risk_cat_value}_reason"] = evaluate_output.get(
                            f"{risk_cat_value}_reason", ""
                        )
                        row[f"outputs.{risk_cat_value}.{risk_cat_value}_result"] = EVALUATION_PASS_FAIL_MAPPING[
                            result == False
                        ]
                        self.logger.debug(
                            f"Successfully evaluated conversation {idx+1} for {risk_category.value}/{strategy_name}"
                        )
                        return row
            except Exception as e:
                error_msg = str(e)
                self.logger.error(
                    f"Error evaluating conversation {idx+1} for {risk_category.value}/{strategy_name}: {error_msg}"
                )
                # Return a row with error information AND conversation data so it can be matched
                # The error field will be picked up by result processing to populate sample.error
                return {
                    "inputs.conversation": {"messages": messages},
                    "error": error_msg,
                }

        return {}

    async def evaluate(
        self,
        data_path: Union[str, os.PathLike],
        risk_category: RiskCategory,
        strategy: Union[AttackStrategy, List[AttackStrategy]],
        scan_name: Optional[str] = None,
        output_path: Optional[Union[str, os.PathLike]] = None,
        _skip_evals: bool = False,
        red_team_info: Dict = None,
    ) -> None:
        """Perform evaluation on collected red team attack data.

        :param data_path: Path to the input data containing red team conversations
        :type data_path: Union[str, os.PathLike]
        :param risk_category: Risk category to evaluate against
        :type risk_category: RiskCategory
        :param strategy: Attack strategy or strategies used to generate the data
        :type strategy: Union[AttackStrategy, List[AttackStrategy]]
        :param scan_name: Optional name for the evaluation
        :type scan_name: Optional[str]
        :param output_path: Path for storing evaluation results
        :type output_path: Optional[Union[str, os.PathLike]]
        :param _skip_evals: Whether to skip the actual evaluation process
        :type _skip_evals: bool
        :param red_team_info: Dictionary to store evaluation results
        :type red_team_info: Dict
        :return: None
        """
        strategy_name = get_strategy_name(strategy)
        self.logger.debug(
            f"Evaluate called with data_path={data_path}, risk_category={risk_category.value}, strategy={strategy_name}, output_path={output_path}, skip_evals={_skip_evals}, scan_name={scan_name}"
        )
        self.logger.debug(f"EvaluationProcessor scan_output_dir: {self.scan_output_dir}")

        if _skip_evals:
            return None

        # If output_path is provided, use it; otherwise create one in the scan output directory if available
        if output_path:
            result_path = output_path
            self.logger.debug(f"Using provided output_path: {result_path}")
        elif self.scan_output_dir:
            result_filename = f"{strategy_name}_{risk_category.value}_{str(uuid.uuid4())}{RESULTS_EXT}"
            result_path = os.path.join(self.scan_output_dir, result_filename)
            # Ensure the result path is absolute
            if not os.path.isabs(result_path):
                result_path = os.path.abspath(result_path)
            self.logger.debug(f"Using scan_output_dir: {self.scan_output_dir}, result_path: {result_path}")
        else:
            result_path = f"{str(uuid.uuid4())}{RESULTS_EXT}"
            # Make it absolute if not already
            if not os.path.isabs(result_path):
                result_path = os.path.abspath(result_path)
            self.logger.debug(f"Using fallback path: {result_path}")

        self.logger.debug(f"Final result_path: {result_path}")

        try:
            # Get the appropriate metric for this risk category
            metric_name = get_metric_from_risk_category(risk_category)

            # For hate_unfairness, always use "hate_unfairness" metric name for Sync API
            if risk_category == RiskCategory.HateUnfairness:
                metric_name = "hate_unfairness"
                self.logger.debug(f"Using metric 'hate_unfairness' for Sync API")

            self.logger.debug(f"Using metric '{metric_name}' for risk category '{risk_category.value}'")

            # Load all conversations from the data file
            conversations = []
            try:
                with open(data_path, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            data = json.loads(line)
                            if "conversation" in data and "messages" in data["conversation"]:
                                conversations.append(data)
                        except json.JSONDecodeError:
                            self.logger.warning(f"Skipping invalid JSON line in {data_path}")
            except Exception as e:
                self.logger.error(f"Failed to read conversations from {data_path}: {str(e)}")
                return None

            if not conversations:
                self.logger.warning(f"No valid conversations found in {data_path}, skipping evaluation")
                return None

            self.logger.debug(f"Found {len(conversations)} conversations in {data_path}")

            # Evaluate each conversation
            eval_start_time = datetime.now()
            tasks = [
                self.evaluate_conversation(
                    conversation=conversation,
                    metric_name=metric_name,
                    strategy_name=strategy_name,
                    risk_category=risk_category,
                    idx=idx,
                    risk_sub_type=conversation.get("risk_sub_type"),
                )
                for idx, conversation in enumerate(conversations)
            ]
            rows = await asyncio.gather(*tasks)

            if not rows:
                self.logger.warning(f"No conversations could be successfully evaluated in {data_path}")
                return None

            # Create the evaluation result structure
            evaluation_result = {
                "rows": rows,
                "metrics": {},
            }

            # Write evaluation results to the output file
            os.makedirs(os.path.dirname(result_path), exist_ok=True)
            with open(result_path, "w", encoding="utf-8") as f:
                json.dump(evaluation_result, f, indent=2)

            # Log the full path for debugging
            tqdm.write(f'Evaluation results saved to "{result_path}".')

            eval_duration = (datetime.now() - eval_start_time).total_seconds()
            self.logger.debug(
                f"Evaluation of {len(rows)} conversations for {risk_category.value}/{strategy_name} completed in {eval_duration} seconds"
            )
            self.logger.debug(f"Successfully wrote evaluation results for {len(rows)} conversations to {result_path}")

        except Exception as e:
            self.logger.error(f"Error during evaluation for {risk_category.value}/{strategy_name}: {str(e)}")
            evaluation_result = None

        # Update red_team_info with evaluation results
        if red_team_info:
            red_team_info[strategy_name][risk_category.value]["evaluation_result_file"] = str(result_path)
            red_team_info[strategy_name][risk_category.value]["evaluation_result"] = evaluation_result
            red_team_info[strategy_name][risk_category.value]["status"] = TASK_STATUS["COMPLETED"]
            self.logger.debug(
                f"Evaluation complete for {strategy_name}/{risk_category.value}, results stored in red_team_info"
            )
            self.logger.debug(f"Updated red_team_info evaluation_result_file path: {result_path}")

    def get_attack_success(self, result: Union[str, float], risk_category: Optional[str] = None) -> bool:
        """Determine if an attack was successful based on evaluation result.

        :param result: The evaluation result - either a string or numeric score
        :type result: Union[str, float]
        :param risk_category: The risk category (for API compatibility)
        :type risk_category: Optional[str]
        :return: Boolean indicating whether the attack was successful
        :rtype: bool
        """
        # If result is already a boolean, return it directly
        if isinstance(result, bool):
            return result

        # If the result is already a pass/fail string from EVALUATION_PASS_FAIL_MAPPING
        # we can directly determine success without rechecking thresholds
        if isinstance(result, str) and result.lower() in ("pass", "fail"):
            # For safety evaluations, "pass" means the content is safe (attack failed)
            # "fail" means content violated safety policy (attack succeeded)
            return result.lower() == "fail"

        # Fall back to binary string evaluation for all other cases
        from ._utils.formatting_utils import get_attack_success

        return get_attack_success(str(result))
