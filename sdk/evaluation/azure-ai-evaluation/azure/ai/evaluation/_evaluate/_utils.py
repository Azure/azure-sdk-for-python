# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import logging
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Dict, NamedTuple, Optional, Tuple, Union
import uuid
import base64

import pandas as pd
from promptflow.client import PFClient
from promptflow.entities import Run

from azure.ai.evaluation._constants import (
    DEFAULT_EVALUATION_RESULTS_FILE_NAME,
    DefaultOpenEncoding,
    EvaluationRunProperties,
    Prefixes,
)
from azure.ai.evaluation._evaluate._eval_run import EvalRun
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from azure.ai.evaluation._model_configurations import AzureAIProject

LOGGER = logging.getLogger(__name__)

AZURE_WORKSPACE_REGEX_FORMAT = (
    "^azureml:[/]{1,2}subscriptions/([^/]+)/resource(groups|Groups)/([^/]+)"
    "(/providers/Microsoft.MachineLearningServices)?/workspaces/([^/]+)$"
)


class AzureMLWorkspace(NamedTuple):
    subscription_id: str
    resource_group_name: str
    workspace_name: str


def is_none(value) -> bool:
    return value is None or str(value).lower() == "none"


def extract_workspace_triad_from_trace_provider(  # pylint: disable=name-too-long
    trace_provider: str,
) -> AzureMLWorkspace:
    match = re.match(AZURE_WORKSPACE_REGEX_FORMAT, trace_provider)
    if not match or len(match.groups()) != 5:
        raise EvaluationException(
            message="Malformed trace provider string, expected azureml://subscriptions/<subscription_id>/"
            "resourceGroups/<resource_group>/providers/Microsoft.MachineLearningServices/"
            f"workspaces/<workspace_name>, got {trace_provider}",
            internal_message="Malformed trace provider string, expected azureml://subscriptions/<subscription_id>/"
            "resourceGroups/<resource_group>/providers/Microsoft.MachineLearningServices/"
            "workspaces/<workspace_name>,",
            target=ErrorTarget.UNKNOWN,
            category=ErrorCategory.INVALID_VALUE,
            blame=ErrorBlame.UNKNOWN,
        )
    subscription_id = match.group(1)
    resource_group_name = match.group(3)
    workspace_name = match.group(5)
    return AzureMLWorkspace(subscription_id, resource_group_name, workspace_name)


def load_jsonl(path):
    with open(path, "r", encoding=DefaultOpenEncoding.READ) as f:
        return [json.loads(line) for line in f.readlines()]


def _azure_pf_client_and_triad(trace_destination) -> Tuple[PFClient, AzureMLWorkspace]:
    from promptflow.azure._cli._utils import _get_azure_pf_client

    ws_triad = extract_workspace_triad_from_trace_provider(trace_destination)
    azure_pf_client = _get_azure_pf_client(
        subscription_id=ws_triad.subscription_id,
        resource_group=ws_triad.resource_group_name,
        workspace_name=ws_triad.workspace_name,
    )

    return azure_pf_client, ws_triad


def _store_multimodal_content(messages, tmpdir: str):
    # verify if images folder exists
    images_folder_path = os.path.join(tmpdir, "images")
    os.makedirs(images_folder_path, exist_ok=True)

    # traverse all messages and replace base64 image data with new file name.
    for message in messages:
        if isinstance(message.get("content", []), list):
            for content in message.get("content", []):
                if content.get("type") == "image_url":
                    image_url = content.get("image_url")
                    if image_url and "url" in image_url and image_url["url"].startswith("data:image/jpg;base64,"):
                        # Extract the base64 string
                        base64image = image_url["url"].replace("data:image/jpg;base64,", "")

                        # Generate a unique filename
                        image_file_name = f"{str(uuid.uuid4())}.jpg"
                        image_url["url"] = f"images/{image_file_name}"  # Replace the base64 URL with the file path

                        # Decode the base64 string to binary image data
                        image_data_binary = base64.b64decode(base64image)

                        # Write the binary image data to the file
                        image_file_path = os.path.join(images_folder_path, image_file_name)
                        with open(image_file_path, "wb") as f:
                            f.write(image_data_binary)


def _log_metrics_and_instance_results(
    metrics: Dict[str, Any],
    instance_results: pd.DataFrame,
    trace_destination: Optional[str],
    run: Run,
    evaluation_name: Optional[str],
) -> Optional[str]:
    if trace_destination is None:
        LOGGER.debug("Skip uploading evaluation results to AI Studio since no trace destination was provided.")
        return None

    azure_pf_client, ws_triad = _azure_pf_client_and_triad(trace_destination)
    tracking_uri = azure_pf_client.ml_client.workspaces.get(ws_triad.workspace_name).mlflow_tracking_uri

    # Adding line_number as index column this is needed by UI to form link to individual instance run
    instance_results["line_number"] = instance_results.index.values

    with EvalRun(
        run_name=run.name if run is not None else evaluation_name,
        tracking_uri=tracking_uri,
        subscription_id=ws_triad.subscription_id,
        group_name=ws_triad.resource_group_name,
        workspace_name=ws_triad.workspace_name,
        ml_client=azure_pf_client.ml_client,
        promptflow_run=run,
    ) as ev_run:
        artifact_name = EvalRun.EVALUATION_ARTIFACT if run else EvalRun.EVALUATION_ARTIFACT_DUMMY_RUN

        with tempfile.TemporaryDirectory() as tmpdir:
            # storing multi_modal images if exists
            col_name = "inputs.conversation"
            if col_name in instance_results.columns:
                for item in instance_results[col_name].items():
                    value = item[1]
                    if "messages" in value:
                        _store_multimodal_content(value["messages"], tmpdir)

            # storing artifact result
            tmp_path = os.path.join(tmpdir, artifact_name)

            with open(tmp_path, "w", encoding=DefaultOpenEncoding.WRITE) as f:
                f.write(instance_results.to_json(orient="records", lines=True))

            ev_run.log_artifact(tmpdir, artifact_name)

            # Using mlflow to create a dummy run since once created via PF show traces of dummy run in UI.
            # Those traces can be confusing.
            # adding these properties to avoid showing traces if a dummy run is created.
            # We are doing that only for the pure evaluation runs.
            if run is None:
                ev_run.write_properties_to_run_history(
                    properties={
                        EvaluationRunProperties.RUN_TYPE: "eval_run",
                        EvaluationRunProperties.EVALUATION_RUN: "azure-ai-generative-parent",
                        "_azureml.evaluate_artifacts": json.dumps([{"path": artifact_name, "type": "table"}]),
                        "isEvaluatorRun": "true",
                    }
                )

        for metric_name, metric_value in metrics.items():
            ev_run.log_metric(metric_name, metric_value)

    evaluation_id = ev_run.info.run_name if run is not None else ev_run.info.run_id
    return _get_ai_studio_url(trace_destination=trace_destination, evaluation_id=evaluation_id)


def _get_ai_studio_url(trace_destination: str, evaluation_id: str) -> str:
    ws_triad = extract_workspace_triad_from_trace_provider(trace_destination)
    studio_base_url = os.getenv("AI_STUDIO_BASE_URL", "https://ai.azure.com")

    studio_url = (
        f"{studio_base_url}/build/evaluation/{evaluation_id}?wsid=/subscriptions/{ws_triad.subscription_id}"
        f"/resourceGroups/{ws_triad.resource_group_name}/providers/Microsoft.MachineLearningServices/"
        f"workspaces/{ws_triad.workspace_name}"
    )

    return studio_url


def _trace_destination_from_project_scope(project_scope: AzureAIProject) -> str:
    subscription_id = project_scope["subscription_id"]
    resource_group_name = project_scope["resource_group_name"]
    workspace_name = project_scope["project_name"]

    trace_destination = (
        f"azureml://subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/"
        f"providers/Microsoft.MachineLearningServices/workspaces/{workspace_name}"
    )

    return trace_destination


def _write_output(path: Union[str, os.PathLike], data_dict: Any) -> None:
    p = Path(path)
    if p.is_dir():
        p = p / DEFAULT_EVALUATION_RESULTS_FILE_NAME

    with open(p, "w", encoding=DefaultOpenEncoding.WRITE) as f:
        json.dump(data_dict, f)


def _apply_column_mapping(
    source_df: pd.DataFrame, mapping_config: Optional[Dict[str, str]], inplace: bool = False
) -> pd.DataFrame:
    """
    Apply column mapping to source_df based on mapping_config.

    This function is used for pre-validation of input data for evaluators
    :param source_df: the data frame to be changed.
    :type source_df: pd.DataFrame
    :param mapping_config: The configuration, containing column mapping.
    :type mapping_config: Dict[str, str].
    :param inplace: If true, the source_df will be changed inplace.
    :type inplace: bool
    :return: The modified data frame.
    :rtype: pd.DataFrame
    """
    result_df = source_df

    if mapping_config:
        column_mapping = {}
        columns_to_drop = set()
        pattern_prefix = "data."
        run_outputs_prefix = "run.outputs."

        for map_to_key, map_value in mapping_config.items():
            match = re.search(r"^\${([^{}]+)}$", map_value)
            if match is not None:
                pattern = match.group(1)
                if pattern.startswith(pattern_prefix):
                    map_from_key = pattern[len(pattern_prefix) :]
                elif pattern.startswith(run_outputs_prefix):
                    # Target-generated columns always starts from .outputs.
                    map_from_key = f"{Prefixes.TSG_OUTPUTS}{pattern[len(run_outputs_prefix) :]}"
                # if we are not renaming anything, skip.
                if map_from_key == map_to_key:
                    continue
                # If column needs to be mapped to already existing column, we will add it
                # to the drop list.
                if map_to_key in source_df.columns:
                    columns_to_drop.add(map_to_key)
                column_mapping[map_from_key] = map_to_key
        # If we map column to another one, which is already present in the data
        # set and the letter also needs to be mapped, we will not drop it, but map
        # instead.
        columns_to_drop = columns_to_drop - set(column_mapping.keys())
        result_df = source_df.drop(columns=columns_to_drop, inplace=inplace)
        result_df.rename(columns=column_mapping, inplace=True)

    return result_df


def _has_aggregator(evaluator: object) -> bool:
    return hasattr(evaluator, "__aggregate__")


def get_int_env_var(env_var_name: str, default_value: int) -> int:
    """
    The function `get_int_env_var` retrieves an integer environment variable value, with a
    default value if the variable is not set or cannot be converted to an integer.

    :param env_var_name: The name of the environment variable you want to retrieve the value of
    :type env_var_name: str
    :param default_value: The default value is the value that will be returned if the environment
        variable is not found or if it cannot be converted to an integer
    :type default_value: int
    :return: an integer value.
    :rtype: int
    """
    try:
        return int(os.environ[env_var_name])
    except (ValueError, KeyError):
        return default_value


def set_event_loop_policy() -> None:
    import asyncio
    import platform

    if platform.system().lower() == "windows":
        # Reference: https://stackoverflow.com/questions/45600579/asyncio-event-loop-is-closed-when-getting-loop
        # On Windows seems to be a problem with EventLoopPolicy, use this snippet to work around it
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # type: ignore[attr-defined]
