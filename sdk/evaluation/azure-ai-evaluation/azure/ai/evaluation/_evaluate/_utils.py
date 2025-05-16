# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import logging
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Dict, NamedTuple, Optional, Union, cast
import uuid
import base64
import math

import pandas as pd
from azure.ai.evaluation._legacy._adapters.entities import Run

from azure.ai.evaluation._constants import (
    DEFAULT_EVALUATION_RESULTS_FILE_NAME,
    DefaultOpenEncoding,
    EvaluationRunProperties,
    Prefixes,
)
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from azure.ai.evaluation._model_configurations import AzureAIProject
from azure.ai.evaluation._version import VERSION
from azure.ai.evaluation._azure._clients import LiteMLClient

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
    from azure.ai.evaluation._legacy._adapters.utils import get_workspace_triad_from_local

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

    # In theory this if statement should never evaluate to True, but we'll keep it here just in case
    # for backwards compatibility with what the original code that depended on promptflow-azure did
    if not (subscription_id and resource_group_name and workspace_name):
        local = get_workspace_triad_from_local()
        subscription_id = subscription_id or local.subscription_id or os.getenv("AZUREML_ARM_SUBSCRIPTION")
        resource_group_name = resource_group_name or local.resource_group_name or os.getenv("AZUREML_ARM_RESOURCEGROUP")
        workspace_name = workspace_name or local.workspace_name or os.getenv("AZUREML_ARM_WORKSPACE_NAME")

    return AzureMLWorkspace(subscription_id or "", resource_group_name or "", workspace_name or "")


def load_jsonl(path):
    with open(path, "r", encoding=DefaultOpenEncoding.READ) as f:
        return [json.loads(line) for line in f.readlines()]


def _store_multimodal_content(messages, tmpdir: str):
    # verify if images folder exists
    images_folder_path = os.path.join(tmpdir, "images")
    os.makedirs(images_folder_path, exist_ok=True)

    # traverse all messages and replace base64 image data with new file name.
    for message in messages:
        if isinstance(message.get("content", []), list):
            for content in message.get("content", []):
                process_message_content(content, images_folder_path)


def process_message_content(content, images_folder_path):
    if content.get("type", "") == "image_url":
        image_url = content.get("image_url")

        if not image_url or "url" not in image_url:
            return None

        url = image_url["url"]
        if not url.startswith("data:image/"):
            return None

        match = re.search("data:image/([^;]+);", url)
        if not match:
            return None

        ext = match.group(1)
        # Extract the base64 string
        base64image = image_url["url"].replace(f"data:image/{ext};base64,", "")

        # Generate a unique filename
        image_file_name = f"{str(uuid.uuid4())}.{ext}"
        image_url["url"] = f"images/{image_file_name}"  # Replace the base64 URL with the file path

        # Decode the base64 string to binary image data
        image_data_binary = base64.b64decode(base64image)

        # Write the binary image data to the file
        image_file_path = os.path.join(images_folder_path, image_file_name)
        with open(image_file_path, "wb") as f:
            f.write(image_data_binary)
    return None

def _log_metrics_and_instance_results_onedp(
    metrics: Dict[str, Any],
    instance_results: pd.DataFrame,
    project_url: str,
    evaluation_name: Optional[str],
    name_map: Dict[str, str],
    **kwargs,
) -> Optional[str]:

    # One RP Client
    from azure.ai.evaluation._azure._token_manager import AzureMLTokenManager
    from azure.ai.evaluation._constants import TokenScope
    from azure.ai.evaluation._common import EvaluationServiceOneDPClient, EvaluationUpload

    credentials = AzureMLTokenManager(
        TokenScope.COGNITIVE_SERVICES_MANAGEMENT.value, LOGGER, credential=kwargs.get("credential")
    )
    client = EvaluationServiceOneDPClient(
        endpoint=project_url,
        credential=credentials
    )

    # Massaging before artifacts are put on disk
    # Adding line_number as index column this is needed by UI to form link to individual instance run
    instance_results["line_number"] = instance_results.index.values

    artifact_name = "instance_results.jsonl"

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

        properties = {
            EvaluationRunProperties.RUN_TYPE: "eval_run",
            EvaluationRunProperties.EVALUATION_RUN: "promptflow.BatchRun",
            EvaluationRunProperties.EVALUATION_SDK: f"azure-ai-evaluation:{VERSION}",
            "_azureml.evaluate_artifacts": json.dumps([{"path": artifact_name, "type": "table"}]),
        }               
        properties.update(_convert_name_map_into_property_entries(name_map))

        create_evaluation_result_response = client.create_evaluation_result(
            name=uuid.uuid4(),
            path=tmpdir,
            metrics=metrics
        )

        upload_run_response = client.start_evaluation_run(
            evaluation=EvaluationUpload(
                display_name=evaluation_name,
            )
        )

        update_run_response = client.update_evaluation_run(
            name=upload_run_response.id,
            evaluation=EvaluationUpload(
                display_name=evaluation_name,
                status="Completed",
                outputs={
                    'evaluationResultId': create_evaluation_result_response.id,
                },
                properties=properties,
            )
        )

    return update_run_response.properties.get("AiStudioEvaluationUri")

def _log_metrics_and_instance_results(
    metrics: Dict[str, Any],
    instance_results: pd.DataFrame,
    trace_destination: Optional[str],
    run: Optional[Run],
    evaluation_name: Optional[str],
    name_map: Dict[str, str],
    **kwargs,
) -> Optional[str]:
    from azure.ai.evaluation._evaluate._eval_run import EvalRun

    if trace_destination is None:
        LOGGER.debug("Skip uploading evaluation results to AI Studio since no trace destination was provided.")
        return None

    ws_triad = extract_workspace_triad_from_trace_provider(trace_destination)
    management_client = LiteMLClient(
        subscription_id=ws_triad.subscription_id,
        resource_group=ws_triad.resource_group_name,
        logger=LOGGER,
        credential=kwargs.get("credential"),
        # let the client automatically determine the credentials to use
    )
    tracking_uri = management_client.workspace_get_info(ws_triad.workspace_name).ml_flow_tracking_uri

    # Adding line_number as index column this is needed by UI to form link to individual instance run
    instance_results["line_number"] = instance_results.index.values

    with EvalRun(
        run_name=run.name if run is not None else evaluation_name,
        tracking_uri=cast(str, tracking_uri),
        subscription_id=ws_triad.subscription_id,
        group_name=ws_triad.resource_group_name,
        workspace_name=ws_triad.workspace_name,
        management_client=management_client,
        promptflow_run=run,
    ) as ev_run:
        artifact_name = EvalRun.EVALUATION_ARTIFACT

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
                properties = {
                        EvaluationRunProperties.RUN_TYPE: "eval_run",
                        EvaluationRunProperties.EVALUATION_RUN: "promptflow.BatchRun",
                        EvaluationRunProperties.EVALUATION_SDK: f"azure-ai-evaluation:{VERSION}",
                        "_azureml.evaluate_artifacts": json.dumps([{"path": artifact_name, "type": "table"}]),
                    }
                properties.update(_convert_name_map_into_property_entries(name_map))
                ev_run.write_properties_to_run_history(properties=properties)
            else:
                ev_run.write_properties_to_run_history(
                    properties={
                        EvaluationRunProperties.EVALUATION_SDK: f"azure-ai-evaluation:{VERSION}",
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
        json.dump(data_dict, f, ensure_ascii=False)

    print(f'Evaluation results saved to "{p.resolve()}".\n')


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

# textwrap.wrap tries to do fancy nonsense that we don't want
def _wrap(s, w):
    return [s[i:i + w] for i in range(0, len(s), w)]

def _convert_name_map_into_property_entries(
    name_map: Dict[str, str], segment_length: int = 950, max_segments: int = 10
) -> Dict[str, Any]:
    """
    Convert the name map into property entries.

    :param name_map: The name map to be converted.
    :type name_map: Dict[str, str]
    :param segment_length: The max length of each individual segment,
        which will each have their own dictionary entry
    :type segment_length: str
    :param max_segments: The max number of segments we can have. If the stringified
        name map is too long, we just return a length entry with a value
        of -1 to indicate that the map was too long.
    :type max_segments: str
    :return: The converted name map.
    :rtype: Dict[str, Any]
    """
    name_map_string = json.dumps(name_map)
    num_segments = math.ceil(len(name_map_string) / segment_length)
    # Property map is somehow still too long to encode within the space
    # we allow, so give up, but make sure the service knows we gave up
    if (num_segments > max_segments):
        return {EvaluationRunProperties.NAME_MAP_LENGTH: -1}

    result: Dict[str, Any] = {EvaluationRunProperties.NAME_MAP_LENGTH: num_segments}
    segments_list = _wrap(name_map_string, segment_length)
    for i in range(0, num_segments):
        segment_key = f"{EvaluationRunProperties.NAME_MAP}_{i}"
        result[segment_key] = segments_list[i]
    return result

class JSONLDataFileLoader:
    def __init__(self, filename: Union[os.PathLike, str]):
        self.filename = filename

    def load(self) -> pd.DataFrame:
        return pd.read_json(self.filename, lines=True)


class CSVDataFileLoader:
    def __init__(self, filename: Union[os.PathLike, str]):
        self.filename = filename

    def load(self) -> pd.DataFrame:
        return pd.read_csv(self.filename)


class DataLoaderFactory:
    @staticmethod
    def get_loader(filename: Union[os.PathLike, str]) -> Union[JSONLDataFileLoader, CSVDataFileLoader]:
        filename_str = str(filename).lower()
        if filename_str.endswith(".csv"):
            return CSVDataFileLoader(filename)

        # fallback to JSONL to maintain backward compatibility
        return JSONLDataFileLoader(filename)
