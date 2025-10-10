# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import logging
import os
import re
import tempfile
from pathlib import Path
import time
from typing import Any, Dict, List, NamedTuple, Optional, Union, cast
import uuid
import base64
import math

import pandas as pd
from tqdm import tqdm

from azure.core.pipeline.policies import UserAgentPolicy
from azure.ai.evaluation._legacy._adapters.entities import Run

from azure.ai.evaluation._constants import (
    DEFAULT_EVALUATION_RESULTS_FILE_NAME,
    DefaultOpenEncoding,
    EvaluationRunProperties,
    Prefixes,
)
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from azure.ai.evaluation._model_configurations import AzureAIProject, EvaluationResult
from azure.ai.evaluation._version import VERSION
from azure.ai.evaluation._user_agent import UserAgentSingleton
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
    tags: Optional[Dict[str, str]] = None,
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
        credential=credentials,
        user_agent_policy=UserAgentPolicy(base_user_agent=UserAgentSingleton().value),
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
            EvaluationRunProperties.EVALUATION_SDK: f"azure-ai-evaluation:{VERSION}",
            "_azureml.evaluate_artifacts": json.dumps([{"path": artifact_name, "type": "table"}]),
        }
        properties.update(_convert_name_map_into_property_entries(name_map))

        create_evaluation_result_response = client.create_evaluation_result(
            name=uuid.uuid4(), path=tmpdir, metrics=metrics
        )

        upload_run_response = client.start_evaluation_run(
            evaluation=EvaluationUpload(
                display_name=evaluation_name,
                properties=properties,
                tags=tags,
            )
        )

        update_run_response = client.update_evaluation_run(
            name=upload_run_response.id,
            evaluation=EvaluationUpload(
                display_name=evaluation_name,
                status="Completed",
                outputs={
                    "evaluationResultId": create_evaluation_result_response.id,
                },
            ),
        )

    return update_run_response.properties.get("AiStudioEvaluationUri")


def _log_metrics_and_instance_results(
    metrics: Dict[str, Any],
    instance_results: pd.DataFrame,
    trace_destination: Optional[str],
    run: Optional[Run],
    evaluation_name: Optional[str],
    name_map: Dict[str, str],
    tags: Optional[Dict[str, str]] = None,
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
        tags=tags,
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

    # Use tqdm.write to print message without interfering with any current progress bar
    # Fall back to regular print if tqdm.write fails (e.g., when progress bar is closed)
    try:
        tqdm.write(f'Evaluation results saved to "{p.resolve()}".\n')
    except Exception:
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
    return [s[i : i + w] for i in range(0, len(s), w)]


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
    if num_segments > max_segments:
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
        return pd.read_json(self.filename, lines=True, dtype=object)


class CSVDataFileLoader:
    def __init__(self, filename: Union[os.PathLike, str]):
        self.filename = filename

    def load(self) -> pd.DataFrame:
        return pd.read_csv(self.filename, dtype=str)


class DataLoaderFactory:
    @staticmethod
    def get_loader(filename: Union[os.PathLike, str]) -> Union[JSONLDataFileLoader, CSVDataFileLoader]:
        filename_str = str(filename).lower()
        if filename_str.endswith(".csv"):
            return CSVDataFileLoader(filename)

        # fallback to JSONL to maintain backward compatibility
        return JSONLDataFileLoader(filename)


def _convert_results_to_aoai_evaluation_results(
        results: EvaluationResult, 
        logger: logging.Logger, 
        eval_meta_data: Optional[Dict[str, Any]] = None,
        eval_run_summary: Optional[Dict[str, Any]] = None
) -> None:
    """
    Convert evaluation results to AOAI evaluation results format.
    
    Each row of input results.rows looks like:
    {"inputs.query":"What is the capital of France?","inputs.context":"France is in Europe",
     "inputs.generated_response":"Paris is the capital of France.","inputs.ground_truth":"Paris is the capital of France.",
     "outputs.F1_score.f1_score":1.0,"outputs.F1_score.f1_result":"pass","outputs.F1_score.f1_threshold":0.5}
    
    Convert each row into new RunOutputItem object with results array.
    
    :param results: The evaluation results to convert
    :type results: EvaluationResult
    :param eval_meta_data: The evaluation metadata, containing eval_id, eval_run_id, and testing_criteria
    :type eval_meta_data: Dict[str, Any]
    :param logger: Logger instance
    :type logger: logging.Logger
    :return: EvaluationResult with converted evaluation results in AOAI format
    :rtype: EvaluationResult
    """
        
    if eval_meta_data is None:
        return
    
    created_time = int(time.time())
    converted_rows = []

    eval_id: Optional[str] = eval_meta_data.get("eval_id")
    eval_run_id: Optional[str] = eval_meta_data.get("eval_run_id")
    testing_criteria_list: Optional[List[Dict[str, Any]]] = eval_meta_data.get("testing_criteria")

    testing_criteria_name_types: Optional[Dict[str, str]] = {}
    if testing_criteria_list is not None:
        for criteria in testing_criteria_list:
            criteria_name = criteria.get("name")
            criteria_type = criteria.get("type")
            if criteria_name is not None and criteria_type is not None:
                testing_criteria_name_types[criteria_name] = criteria_type

    for row_idx, row in enumerate(results.get("rows", [])):
        # Group outputs by test criteria name
        criteria_groups = {criteria: {} for criteria in testing_criteria_name_types.keys()}
        input_groups = {}
        top_sample = []
        for key, value in row.items():
            if key.startswith("outputs."):
                # Parse key: outputs.<test-criteria-name>.<metric>
                parts = key.split(".", 2)  # Split into max 3 parts: ['outputs', '<criteria-name>', '<metric>']
                if len(parts) >= 3:
                    criteria_name = parts[1]
                    metric_name = parts[2]

                    if criteria_name not in criteria_groups:
                        criteria_groups[criteria_name] = {}

                    criteria_groups[criteria_name][metric_name] = value
            elif key.startswith("inputs."):
                input_key = key.replace('inputs.', '')
                if input_key not in input_groups:
                    input_groups[input_key] = value

        # Convert each criteria group to RunOutputItem result
        run_output_results = []
        for criteria_name, metrics in criteria_groups.items():
            # Extract metrics for this criteria
            score = None
            label = None
            reason = None
            threshold = None
            passed = None
            sample = None
            # Find score - look for various score patterns
            for metric_key, metric_value in metrics.items():
                if metric_key.endswith("_score") or metric_key == "score":
                    score = metric_value
                elif metric_key.endswith("_result") or metric_key == "result" or metric_key == "passed":
                    label = metric_value
                    passed = True if (str(metric_value).lower() == 'pass' or str(metric_value).lower() == 'true') else False
                elif metric_key.endswith("_reason") or metric_key == "reason":
                    reason = metric_value
                elif metric_key.endswith("_threshold") or metric_key == "threshold":
                    threshold = metric_value
                elif metric_key == "sample":
                    sample = metric_value
                elif not any(metric_key.endswith(suffix) for suffix in ["_result", "_reason", "_threshold"]):
                    # If no score found yet and this doesn't match other patterns, use as score
                    if score is None:
                        score = metric_value

            # Determine passed status
            passed = True if (str(label).lower() == 'pass' or str(label).lower() == 'true') else False  

            # Create result object for this criteria
            result_obj = {
                "type": testing_criteria_name_types[criteria_name] if testing_criteria_name_types and criteria_name in testing_criteria_name_types else "azure_ai_evaluator",  # Use criteria name as type
                "name": criteria_name,  # Use criteria name as name
                "metric": criteria_name  # Use criteria name as metric
            }
            # Add optional fields if they exist
            #if score is not None:
            result_obj["score"] = score
            #if label is not None:
            result_obj["label"] = label
            #if reason is not None:
            result_obj["reason"] = reason
            #if threshold is not None:
            result_obj["threshold"] = threshold
            #if passed is not None:
            result_obj["passed"] = passed
            
            if sample is not None:
                result_obj["sample"] = sample
                top_sample.append(sample)  # Save top sample for the row
            elif (eval_run_summary and criteria_name in eval_run_summary 
                  and isinstance(eval_run_summary[criteria_name], dict) 
                  and "error_code" in eval_run_summary[criteria_name]):
                error_info = {
                    "code": eval_run_summary[criteria_name].get("error_code", None),
                    "message": eval_run_summary[criteria_name].get("error_message", None),
                } if eval_run_summary[criteria_name].get("error_code", None) is not None else None
                sample = {
                    "error": error_info
                } if error_info is not None else None
                result_obj["sample"] = sample
                if sample is not None:
                    top_sample.append(sample)

            run_output_results.append(result_obj)

        # Create RunOutputItem structure
        run_output_item = {
            "object": "eval.run.output_item",
            "id": f"{row_idx+1}",
            "run_id": eval_run_id,
            "eval_id": eval_id,
            "created_at": created_time,
            "datasource_item_id": row_idx,
            "datasource_item": input_groups,
            "results": run_output_results,
            "status": "completed" if len(run_output_results) > 0 else "error"
        }

        run_output_item["sample"] = top_sample

        converted_rows.append(run_output_item)

    # Create converted results maintaining the same structure
    results["evaluation_results_list"] = converted_rows
    logger.info(f"Converted {len(converted_rows)} rows to AOAI evaluation format, eval_id: {eval_id}, eval_run_id: {eval_run_id}")
    # Calculate summary statistics
    evaluation_summary = _calculate_aoai_evaluation_summary(converted_rows, logger)
    results["evaluation_summary"] = evaluation_summary
    logger.info(f"Summary statistics calculated for {len(converted_rows)} rows, eval_id: {eval_id}, eval_run_id: {eval_run_id}")


def _calculate_aoai_evaluation_summary(aoai_results: list, logger: logging.Logger) -> Dict[str, Any]:
    """
    Calculate summary statistics for AOAI evaluation results.
    
    :param aoai_results: List of AOAI result objects (run_output_items)
    :type aoai_results: list
    :return: Summary statistics dictionary
    :rtype: Dict[str, Any]
    """
    # Calculate result counts based on aoaiResults
    result_counts = {
        "total": 0,
        "errored": 0,
        "failed": 0,
        "passed": 0
    }

    # Count results by status and calculate per model usage
    model_usage_stats = {}  # Dictionary to aggregate usage by model
    result_counts_stats = {}  # Dictionary to aggregate usage by model

    for aoai_result in aoai_results:
        logger.info(f"Processing aoai_result with id: {getattr(aoai_result, 'id', 'unknown')}, row keys: {aoai_result.keys() if hasattr(aoai_result, 'keys') else 'N/A'}")
        if isinstance(aoai_result, dict) and 'results' in aoai_result:
            logger.info(f"Processing aoai_result with id: {getattr(aoai_result, 'id', 'unknown')}, results count: {len(aoai_result['results'])}")
            result_counts["total"] += len(aoai_result['results'])
            for result_item in aoai_result['results']:
                if isinstance(result_item, dict):
                    # Check if the result has a 'passed' field
                    if 'passed' in result_item:
                        testing_criteria = result_item.get("name", "")
                        if testing_criteria not in result_counts_stats:
                            result_counts_stats[testing_criteria] = {
                                "testing_criteria": testing_criteria,
                                "failed": 0,
                                "passed": 0
                            }
                        if result_item['passed'] is True:
                            result_counts["passed"] += 1
                            result_counts_stats[testing_criteria]["passed"] += 1
                            
                        elif result_item['passed'] is False:
                            result_counts["failed"] += 1
                            result_counts_stats[testing_criteria]["failed"] += 1
                    # Check if the result indicates an error status
                    elif 'status' in result_item and result_item['status'] in ['error', 'errored']:
                        result_counts["errored"] += 1
        elif hasattr(aoai_result, 'status') and aoai_result.status == 'error':
            result_counts["errored"] += 1
        elif isinstance(aoai_result, dict) and aoai_result.get('status') == 'error':
            result_counts["errored"] += 1

        # Extract usage statistics from aoai_result.sample
        sample_data_list = None
        if isinstance(aoai_result, dict) and 'sample' in aoai_result:
            sample_data_list = aoai_result['sample']

        for sample_data in sample_data_list:
            if sample_data and isinstance(sample_data, dict) and 'usage' in sample_data:
                usage_data = sample_data['usage']
                model_name = sample_data.get('model', 'unknown')
                if model_name not in model_usage_stats:
                    model_usage_stats[model_name] = {
                        'invocation_count': 0,
                        'total_tokens': 0,
                        'prompt_tokens': 0,
                        'completion_tokens': 0,
                        'cached_tokens': 0
                    }
            # Aggregate usage statistics
            model_stats = model_usage_stats[model_name]
            model_stats['invocation_count'] += 1
            if isinstance(usage_data, dict):
                model_stats['total_tokens'] += usage_data.get('total_tokens', 0)
                model_stats['prompt_tokens'] += usage_data.get('prompt_tokens', 0)
                model_stats['completion_tokens'] += usage_data.get('completion_tokens', 0)
                model_stats['cached_tokens'] += usage_data.get('cached_tokens', 0)
    # Convert model usage stats to list format matching EvaluationRunPerModelUsage
    per_model_usage = []
    for model_name, stats in model_usage_stats.items():
        per_model_usage.append({
            'model_name': model_name,
            'invocation_count': stats['invocation_count'],
            'total_tokens': stats['total_tokens'],
            'prompt_tokens': stats['prompt_tokens'],
            'completion_tokens': stats['completion_tokens'],
            'cached_tokens': stats['cached_tokens']
        })
    result_counts_stats_val = []
    logger.info(f"\r\n Result counts stats: {result_counts_stats}")
    for criteria_name, stats_val in result_counts_stats.items():
        if isinstance(stats_val, dict):
            logger.info(f"\r\n  Criteria: {criteria_name}, stats: {stats_val}")
            result_counts_stats_val.append({
                'testing_criteria': criteria_name,
                'passed': stats_val.get('passed', 0),
                'failed': stats_val.get('failed', 0)
            })
    return {
        "result_counts": result_counts,
        "per_model_usage": per_model_usage,
        "per_testing_criteria_results": result_counts_stats_val
    }
