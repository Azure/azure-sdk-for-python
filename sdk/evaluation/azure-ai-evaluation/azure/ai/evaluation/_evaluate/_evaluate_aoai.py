# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import logging
import re

from openai import AzureOpenAI, OpenAI
import pandas as pd
from typing import Any, Callable, Dict, Tuple, TypeVar, Union, Type, Optional, TypedDict, List, cast, Set
from time import sleep

from ._batch_run import CodeClient, ProxyClient

# import aoai_mapping
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from azure.ai.evaluation._constants import EVALUATION_PASS_FAIL_MAPPING
from azure.ai.evaluation._aoai.aoai_grader import AzureOpenAIGrader
from azure.ai.evaluation._common._experimental import experimental


TClient = TypeVar("TClient", ProxyClient, CodeClient)
LOGGER = logging.getLogger(__name__)

# Precompiled regex for extracting data paths from mapping expressions of the form
# ${data.some.dotted.path}. Compiled once at import time to avoid repeated
# recompilation on each call to _generate_data_source_config.
DATA_PATH_PATTERN = re.compile(r"^\$\{data\.([a-zA-Z0-9_\.]+)\}$")

# Canonical top-level wrapper key expected in nested JSONL evaluation rows.
# Centralizing here avoids magic strings sprinkled through schema/content generation code.
WRAPPER_KEY = "item"

# Keys that must remain at the top level (outside the wrapper) when we
# normalize flat JSONL rows into the canonical `item` structure.
_RESERVED_ROOT_KEYS: Set[str] = {"sample"}


def _normalize_row_for_item_wrapper(row: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure every row exposes an `item` object without losing reserved keys."""

    wrapper = row.get(WRAPPER_KEY)
    if isinstance(wrapper, dict):
        return row

    normalized: Dict[str, Any] = {}
    item_payload: Dict[str, Any] = {}

    for key, value in row.items():
        if key in _RESERVED_ROOT_KEYS:
            normalized[key] = value
        elif key != WRAPPER_KEY:
            item_payload[key] = value

    normalized[WRAPPER_KEY] = item_payload
    return normalized


class OAIEvalRunCreationInfo(TypedDict, total=True):
    """Configuration for an evaluator"""

    client: Union[AzureOpenAI, OpenAI]
    eval_group_id: str
    eval_run_id: str
    grader_name_map: Dict[str, str]
    # Total number of expected rows in the original dataset. Used to
    # re-align AOAI grader results to guard against silent row drops
    # causing horizontal concatenation misalignment.
    expected_rows: int


def _split_evaluators_and_grader_configs(
    evaluators: Dict[str, Union[Callable, AzureOpenAIGrader]],
) -> Tuple[Dict[str, Callable], Dict[str, AzureOpenAIGrader]]:
    """
    Given a dictionary of strings to Evaluators and AOAI graders. Identity which is which, and return two
    dictionaries that each contain one subset, the first containing the evaluators and the second containing
    the AOAI graders. AOAI graders are defined as anything that is an instance of the AoaiGrader class,
    including child class instances.

    :param evaluators: Evaluators to be used for evaluation. It should be a dictionary with key as alias for evaluator
        and value as the evaluator function or AOAI grader.
    :type evaluators: Dict[str, Union[Callable, ]]
    :return: Tuple of two dictionaries, the first containing evaluators and the second containing AOAI graders.
    :rtype: Tuple[Dict[str, Callable], Dict[str, AoaiGrader]]
    """
    LOGGER.info(f"AOAI: Splitting {len(evaluators)} evaluators into AOAI graders and standard evaluators...")
    true_evaluators = {}
    aoai_graders = {}
    for key, value in evaluators.items():
        if isinstance(value, AzureOpenAIGrader):
            aoai_graders[key] = value
        else:
            true_evaluators[key] = value
    LOGGER.info(f"AOAI: Found {len(aoai_graders)} AOAI graders and {len(true_evaluators)} standard evaluators.")
    return true_evaluators, aoai_graders


@experimental
def _begin_aoai_evaluation(
    graders: Dict[str, AzureOpenAIGrader],
    column_mappings: Optional[Dict[str, Dict[str, str]]],
    data: pd.DataFrame,
    run_name: str,
    **kwargs: Any,
) -> List[OAIEvalRunCreationInfo]:
    """
    Use the AOAI SDK to start an evaluation of the inputted dataset against the supplied graders.
    AOAI evaluation runs must be queried for completion, so this returns the IDs needed to poll for the
    results, and map those results to the user-supplied names of the graders.

    If any of the graders require unique column mappings, this function will
    create a separate evaluation run for each grader. Otherwise, all graders
    will be evaluated in a single run.

    :param client: The AOAI client to use for the evaluation.
    :type client: Union[OpenAI, AzureOpenAI]
    :param graders: The graders to use for the evaluation. Should be a dictionary of string to AOAIGrader.
    :type graders: Dict[str, AoaiGrader]
    :param column_mappings: The column mappings to use for the evaluation.
    :type column_mappings: Optional[Dict[str, Dict[str, str]]]
    :param data: The data to evaluate, preprocessed by the `_validate_and_load_data` method.
    :type data: pd.DataFrame
    :param run_name: The name of the evaluation run.
    :type run_name: str
    :return: A list of evaluation run info that can be used to retrieve the results of the evaluation later
    :rtype: List[OAIEvalRunCreationInfo]
    """

    LOGGER.info("AOAI: Aoai graders detected among evaluator inputs. Preparing to create OAI eval group...")
    all_eval_run_info: List[OAIEvalRunCreationInfo] = []

    grader_mapping_list = list(_get_graders_and_column_mappings(graders, column_mappings))
    LOGGER.info(f"AOAI: Will create {len(grader_mapping_list)} separate evaluation run(s) based on column mappings.")

    for idx, (selected_graders, selected_column_mapping) in enumerate(grader_mapping_list):
        LOGGER.info(
            f"AOAI: Starting evaluation run {idx + 1}/{len(grader_mapping_list)} with {len(selected_graders)} grader(s)..."
        )
        all_eval_run_info.append(
            _begin_single_aoai_evaluation(selected_graders, data, selected_column_mapping, run_name, **kwargs)
        )

    LOGGER.info(f"AOAI: Successfully created {len(all_eval_run_info)} evaluation run(s).")
    return all_eval_run_info


def _begin_single_aoai_evaluation(
    graders: Dict[str, AzureOpenAIGrader],
    data: pd.DataFrame,
    column_mapping: Optional[Dict[str, str]],
    run_name: str,
    **kwargs: Any,
) -> OAIEvalRunCreationInfo:
    """
    Use the AOAI SDK to start an evaluation of the inputted dataset against the supplied graders.
    AOAI evaluation runs must be queried for completion, so this returns a poller to accomplish that task
    at a later time.

    :param graders: The graders to use for the evaluation. Should be a dictionary of string to AOAIGrader.
    :type graders: Dict[str, AoaiGrader]
    :param data: The input data to evaluate, as a pandas DataFrame.
    :type data: pd.DataFrame
    :param column_mapping: The column mapping to apply. If None, an empty mapping is used.
    :type column_mapping: Optional[Dict[str, str]]
    :param run_name: The name of the evaluation run.
    :type run_name: str
    :return: A tuple containing the eval group ID and eval run ID of the resultant eval run, as well as a dictionary
        that maps the user-supplied evaluators to the names of the graders as generated by the OAI service.
    :rtype: Tuple[str, str, Dict[str, str]]
    """
    # Format data for eval group creation
    LOGGER.info(f"AOAI: Preparing evaluation for {len(graders)} grader(s): {list(graders.keys())}")
    grader_name_list = []
    grader_list = []

    data_source: Dict[str, Any] = {}
    data_source_config: Dict[str, Any] = {}

    if kwargs.get("data_source_config") is not None:
        data_source_config = kwargs.get("data_source_config", {})

    if kwargs.get("data_source") is not None:
        data_source = kwargs.get("data_source", {})

    # It's expected that all graders supplied for a single eval run use the same credentials
    # so grab a client from the first grader.
    client = list(graders.values())[0].get_client()

    for name, grader in graders.items():
        grader_name_list.append(name)
        grader_list.append(grader._grader_config)
    effective_column_mapping: Dict[str, str] = column_mapping or {}
    LOGGER.info(f"AOAI: Generating data source config with {len(effective_column_mapping)} column mapping(s)...")
    if data_source_config == {}:
        data_source_config = _generate_data_source_config(data, effective_column_mapping)
    LOGGER.info(f"AOAI: Data source config generated with schema type: {data_source_config.get('type')}")

    # Create eval group
    LOGGER.info(f"AOAI: Creating eval group with {len(grader_list)} testing criteria...")

    # Combine with the item schema with generated data outside Eval SDK
    _combine_item_schemas(data_source_config, kwargs)

    eval_group_info = client.evals.create(
        data_source_config=data_source_config, testing_criteria=grader_list, metadata={"is_foundry_eval": "true"}
    )

    LOGGER.info(f"AOAI: Eval group created with id {eval_group_info.id}. Creating eval run next...")
    # Use eval group info to map grader IDs back to user-assigned names.
    grader_name_map = {}
    num_criteria = len(eval_group_info.testing_criteria)
    if num_criteria != len(grader_name_list):
        raise EvaluationException(
            message=f"Number of testing criteria ({num_criteria})"
            + f" returned by OAI eval group does not match oai graders({len(grader_name_list)}).",
            blame=ErrorBlame.USER_ERROR,
            category=ErrorCategory.INVALID_VALUE,
            target=ErrorTarget.AOAI_GRADER,
        )
    for name, criteria in zip(grader_name_list, eval_group_info.testing_criteria):
        grader_name_map[criteria.id] = name

    # Create eval run
    LOGGER.info(f"AOAI: Creating eval run '{run_name}' with {len(data)} data rows...")
    eval_run_id = _begin_eval_run(client, eval_group_info.id, run_name, data, effective_column_mapping, data_source)
    LOGGER.info(
        f"AOAI: Eval run created with id {eval_run_id}."
        + " Results will be retrieved after normal evaluation is complete..."
    )

    return OAIEvalRunCreationInfo(
        client=client,
        eval_group_id=eval_group_info.id,
        eval_run_id=eval_run_id,
        grader_name_map=grader_name_map,
        expected_rows=len(data),
    )


def _combine_item_schemas(data_source_config: Dict[str, Any], kwargs: Dict[str, Any]) -> None:
    if (
        not kwargs
        or not kwargs.get("item_schema")
        or not isinstance(kwargs["item_schema"], dict)
        or "properties" not in kwargs["item_schema"]
    ):
        return

    if "item_schema" in data_source_config:
        item_schema = kwargs["item_schema"]["required"] if "required" in kwargs["item_schema"] else []
        for key in kwargs["item_schema"]["properties"]:
            if key not in data_source_config["item_schema"]["properties"]:
                data_source_config["item_schema"]["properties"][key] = kwargs["item_schema"]["properties"][key]

                if key in item_schema:
                    data_source_config["item_schema"]["required"].append(key)


def _get_evaluation_run_results(all_run_info: List[OAIEvalRunCreationInfo]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Get the results of an OAI evaluation run, formatted in a way that is easy for the rest of the evaluation
    pipeline to consume. This method accepts a list of eval run information, and will combine the
    results into a single dataframe and metrics dictionary.

    :param all_run_info: A list of evaluation run information that contains the needed values
        to retrieve the results of the evaluation run.
    :type all_run_info: List[OAIEvalRunCreationInfo]
    :return: A tuple containing the results of the evaluation run as a dataframe, and a dictionary of metrics
        calculated from the evaluation run.
    :rtype: Tuple[pd.DataFrame, Dict[str, Any]]
    :raises EvaluationException: If the evaluation run fails or is not completed before timing out.
    """

    LOGGER.info(f"AOAI: Retrieving results from {len(all_run_info)} evaluation run(s)...")
    run_metrics = {}
    output_df = pd.DataFrame()
    for idx, run_info in enumerate(all_run_info):
        LOGGER.info(f"AOAI: Fetching results for run {idx + 1}/{len(all_run_info)} (ID: {run_info['eval_run_id']})...")
        cur_output_df, cur_run_metrics = _get_single_run_results(run_info)
        output_df = pd.concat([output_df, cur_output_df], axis=1)
        run_metrics.update(cur_run_metrics)

    LOGGER.info(f"AOAI: Successfully retrieved all results. Combined dataframe shape: {output_df.shape}")
    return output_df, run_metrics


def _get_single_run_results(
    run_info: OAIEvalRunCreationInfo,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Get the results of an OAI evaluation run, formatted in a way that is easy for the rest of the evaluation
    pipeline to consume.

    :param run_info: The evaluation run information that contains the needed values
        to retrieve the results of the evaluation run.
    :type run_info: OAIEvalRunCreationInfo
    :return: A tuple containing the results of the evaluation run as a dataframe, and a dictionary of metrics
        calculated from the evaluation run.
    :rtype: Tuple[pd.DataFrame, Dict[str, Any]]
    :raises EvaluationException: If the evaluation run fails or is not completed before timing out.
    """
    # Wait for evaluation run to complete
    LOGGER.info(f"AOAI: Waiting for eval run {run_info['eval_run_id']} to complete...")
    run_results = _wait_for_run_conclusion(run_info["client"], run_info["eval_group_id"], run_info["eval_run_id"])

    LOGGER.info(f"AOAI: Eval run {run_info['eval_run_id']} completed with status: {run_results.status}")
    if run_results.status != "completed":
        raise EvaluationException(
            message=f"AOAI evaluation run {run_info['eval_group_id']}/{run_info['eval_run_id']}"
            + f" failed with status {run_results.status}.",
            blame=ErrorBlame.UNKNOWN,
            category=ErrorCategory.FAILED_EXECUTION,
            target=ErrorTarget.AOAI_GRADER,
        )

    # Convert run results into a dictionary of metrics
    LOGGER.info(f"AOAI: Processing results and calculating metrics for run {run_info['eval_run_id']}...")
    run_metrics: Dict[str, Any] = {}
    if run_results.per_testing_criteria_results is None:
        msg = (
            "AOAI evaluation run returned no results, despite 'completed' status. This might"
            + " occur when invalid or conflicting models are selected in the model and grader configs."
            f" Navigate to the evaluation run's report URL for more details: {run_results.report_url}"
        )
        raise EvaluationException(
            message=msg,
            blame=ErrorBlame.UNKNOWN,
            category=ErrorCategory.FAILED_EXECUTION,
            target=ErrorTarget.AOAI_GRADER,
        )
    for criteria_result in run_results.per_testing_criteria_results:
        grader_name = run_info["grader_name_map"][criteria_result.testing_criteria]
        passed = criteria_result.passed
        failed = criteria_result.failed
        ratio = passed / (passed + failed) if (passed + failed) else 0.0
        formatted_column_name = f"{grader_name}.pass_rate"
        run_metrics[formatted_column_name] = ratio
        LOGGER.info(f"AOAI: Grader '{grader_name}': {passed} passed, {failed} failed, pass_rate={ratio:.4f}")

    # Collect all results with pagination
    LOGGER.info(f"AOAI: Collecting output items for run {run_info['eval_run_id']} with pagination...")
    all_results: List[Any] = []
    next_cursor: Optional[str] = None
    limit = 100  # Max allowed by API

    while True:
        list_kwargs = {"eval_id": run_info["eval_group_id"], "run_id": run_info["eval_run_id"], "limit": limit}
        if next_cursor is not None:
            list_kwargs["after"] = next_cursor

        raw_list_results = run_info["client"].evals.runs.output_items.list(**list_kwargs)

        # Add current page results
        all_results.extend(raw_list_results.data)

        # Check for more pages
        if hasattr(raw_list_results, "has_more") and raw_list_results.has_more:
            if hasattr(raw_list_results, "data") and len(raw_list_results.data) > 0:
                next_cursor = raw_list_results.data[-1].id
            else:
                break
        else:
            break

    LOGGER.info(f"AOAI: Collected {len(all_results)} total output items across all pages.")
    listed_results: Dict[str, List[Any]] = {"index": []}
    # Raw data has no order guarantees; capture datasource_item_id per row for ordering.
    for row_result in all_results:
        listed_results["index"].append(row_result.datasource_item_id)
        for single_grader_row_result in row_result.results:
            if isinstance(single_grader_row_result, dict):
                result_dict = single_grader_row_result
            elif hasattr(single_grader_row_result, "model_dump"):
                result_dict = single_grader_row_result.model_dump()
            elif hasattr(single_grader_row_result, "dict"):
                result_dict = single_grader_row_result.dict()
            elif hasattr(single_grader_row_result, "__dict__"):
                result_dict = vars(single_grader_row_result)
            else:
                raise EvaluationException(
                    message=("Unsupported AOAI evaluation result type: " f"{type(single_grader_row_result)!r}."),
                    blame=ErrorBlame.UNKNOWN,
                    category=ErrorCategory.FAILED_EXECUTION,
                    target=ErrorTarget.AOAI_GRADER,
                )

            grader_result_name = result_dict.get("name", None)
            if grader_result_name is None:
                raise EvaluationException(
                    message="AOAI evaluation response missing grader result name; unable to map to original grader.",
                    blame=ErrorBlame.UNKNOWN,
                    category=ErrorCategory.FAILED_EXECUTION,
                    target=ErrorTarget.AOAI_GRADER,
                )

            grader_name = run_info["grader_name_map"][grader_result_name]
            for name, value in result_dict.items():
                if name in ["name"]:
                    continue
                if name.lower() == "passed":
                    # Create a `_result` column for each grader
                    result_column_name = f"outputs.{grader_name}.{grader_name}_result"
                    if len(result_column_name) < 50:
                        if result_column_name not in listed_results:
                            listed_results[result_column_name] = []
                        listed_results[result_column_name].append(EVALUATION_PASS_FAIL_MAPPING[value])

                formatted_column_name = f"outputs.{grader_name}.{name}"
                if formatted_column_name not in listed_results:
                    listed_results[formatted_column_name] = []
                listed_results[formatted_column_name].append(value)

    # Ensure all columns are the same length as the 'index' list
    num_rows = len(listed_results["index"])
    LOGGER.info(f"AOAI: Processing {num_rows} result rows into dataframe...")
    for col_name in list(listed_results.keys()):
        if col_name != "index":
            col_length = len(listed_results[col_name])
            if col_length < num_rows:
                listed_results[col_name].extend([None] * (num_rows - col_length))
            elif col_length > num_rows:
                listed_results[col_name] = listed_results[col_name][:num_rows]

    output_df = pd.DataFrame(listed_results)

    # If the 'index' column is missing for any reason, synthesize it from the current RangeIndex.
    if "index" not in output_df.columns:
        output_df["index"] = list(range(len(output_df)))

    # Deterministic ordering by original datasource_item_id
    output_df = output_df.sort_values("index", ascending=True)

    # Keep a temporary row-id copy for debugging/inspection.
    # Use underscores (not hyphens) to avoid pandas column handling quirks.
    output_df["__azure_ai_evaluation_index"] = output_df["index"]

    # Preserve original ids as index, then pad to expected length
    output_df.set_index("index", inplace=True)

    expected = run_info.get("expected_rows", None)
    if expected is not None:
        pre_len = len(output_df)
        LOGGER.info(f"AOAI: Validating result count: expected {expected} rows, received {pre_len} rows.")
        # Assumes original datasource_item_id space is 0..expected-1
        output_df = output_df.reindex(range(expected))
        if pre_len != expected:
            missing_rows = expected - pre_len
            LOGGER.warning(
                "AOAI grader run %s returned %d/%d rows; %d missing row(s) padded with NaN for alignment.",
                run_info["eval_run_id"],
                pre_len,
                expected,
                missing_rows,
            )
            # Add a per-grader 'row_missing' boolean for padded rows
            grader_user_names: Set[str] = set()
            for col in output_df.columns:
                if col.startswith("outputs."):
                    parts = col.split(".")
                    if len(parts) > 2:
                        grader_user_names.add(parts[1])
            if grader_user_names:
                missing_index_mask = output_df.isna().all(axis=1)
                for g in grader_user_names:
                    col_name = f"outputs.{g}.row_missing"
                    if col_name not in output_df:
                        output_df[col_name] = False
                    output_df.loc[missing_index_mask, col_name] = True

    # Drop the temporary helper column before returning (no public surface change)
    if "__azure_ai_evaluation_index" in output_df.columns:
        output_df.drop(columns=["__azure_ai_evaluation_index"], inplace=True, errors="ignore")

    # Reset to RangeIndex so downstream concatenation aligns on position
    output_df.reset_index(drop=True, inplace=True)
    LOGGER.info(
        f"AOAI: Successfully processed run {run_info['eval_run_id']} with final dataframe shape: {output_df.shape}"
    )
    return output_df, run_metrics


def _convert_remote_eval_params_to_grader(grader_id: str, init_params: Dict[str, Any]) -> AzureOpenAIGrader:
    """
    Helper function for the remote evaluation service.
    Given a model ID that refers to a specific AOAI grader wrapper class, return an instance of that class
    using the provided initialization parameters.

    :param grader_id: The model ID that refers to a specific AOAI grader wrapper class.
    :type grader_id: str
    :param init_params: The initialization parameters to be used for the AOAI grader wrapper class.
        Requires that it contain a model_config and grader_config as top-level keys.
    :type init_params: Dict[str, Any]
    """

    model_config = init_params.get("model_config", None)
    if model_config is None:
        raise EvaluationException(
            message="Grader converter needs a valid 'model_config' key in init_params.",
            blame=ErrorBlame.USER_ERROR,
            category=ErrorCategory.INVALID_VALUE,
            target=ErrorTarget.AOAI_GRADER,
        )

    grader_class = _get_grader_class(grader_id)
    return grader_class(**init_params)


def _get_grader_class(model_id: str) -> Type[AzureOpenAIGrader]:
    """
    Given a model ID, return the class of the corresponding grader wrapper.
    """

    from azure.ai.evaluation import (
        AzureOpenAIGrader,
        AzureOpenAILabelGrader,
        AzureOpenAIStringCheckGrader,
        AzureOpenAITextSimilarityGrader,
        AzureOpenAIScoreModelGrader,
        AzureOpenAIPythonGrader,
    )

    id_map = {
        AzureOpenAIGrader.id: AzureOpenAIGrader,
        AzureOpenAILabelGrader.id: AzureOpenAILabelGrader,
        AzureOpenAIStringCheckGrader.id: AzureOpenAIStringCheckGrader,
        AzureOpenAITextSimilarityGrader.id: AzureOpenAITextSimilarityGrader,
        AzureOpenAIScoreModelGrader.id: AzureOpenAIScoreModelGrader,
        AzureOpenAIPythonGrader.id: AzureOpenAIPythonGrader,
    }

    for key in id_map.keys():
        if model_id == key:
            return id_map[key]
    raise EvaluationException(
        message=f"Model ID {model_id} not recognized as an AOAI grader ID",
        blame=ErrorBlame.USER_ERROR,
        category=ErrorCategory.INVALID_VALUE,
        target=ErrorTarget.AOAI_GRADER,
    )


def _get_graders_and_column_mappings(
    graders: Dict[str, AzureOpenAIGrader],
    column_mappings: Optional[Dict[str, Dict[str, str]]],
) -> List[Tuple[Dict[str, AzureOpenAIGrader], Optional[Dict[str, str]]]]:
    """
    Given a dictionary of column mappings and a dictionary of AOAI graders,
    Split them into sub-lists and sub-dictionaries that each correspond to a single evaluation run
    that must be performed to evaluate the entire dataset.

    Currently this function is fairly naive; it always splits the data if there are multiple
    graders present and any of them have a unique column mapping.

    This odd separate of data is necessary because our system allows for different evaluators
    to have different dataset columns mapped to the same input name for each evaluator, while
    the OAI API can't. So, if if there's a possibility that such a conflict might arise,
    we need to split the incoming data up.

    Currently splits each grader into its own eval group/run to ensure they each use
    their own credentials later on. Planned fast follow is to group things by
    matching credentials later.

    :param graders: The graders to use for the evaluation. Should be a dictionary of string to AOAIGrader.
    :type graders: Dict[str, AoaiGrader]
    :param column_mappings: The column mappings to use for the evaluation.
    :type column_mappings:  Optional[Dict[str, Dict[str, str]]]
    :return: A list of tuples, each containing dictionary of AOAI graders,
        and the column mapping they should use.
    :rtype: List[Tuple[Dict[str, AoaiGrader], Optional[Dict[str, str]]]]
    """

    LOGGER.info(f"AOAI: Organizing {len(graders)} graders with column mappings...")
    if column_mappings is None:
        LOGGER.info("AOAI: No column mappings provided, each grader will have its own eval run.")
        return [({name: grader}, None) for name, grader in graders.items()]
    default_mapping = column_mappings.get("default", None)
    if default_mapping is None:
        default_mapping = {}
    LOGGER.info(
        f"AOAI: Using default mapping with {len(default_mapping)} entries for graders without specific mappings."
    )
    return [
        ({name: grader}, None if column_mappings is None else column_mappings.get(name, default_mapping))
        for name, grader in graders.items()
    ]


def _build_schema_tree_from_paths(
    paths: List[str],
    force_leaf_type: str = "string",
) -> Dict[str, Any]:
    """
    Build a nested JSON schema (object) from a list of dot-delimited paths.
    Each path represents a leaf. Intermediate segments become nested object properties.

    Example input paths:
        ["item.query",
         "item.context.company.policy.security.passwords.rotation_days",
         "item.context.company.policy.security.network.vpn.required"]

    Returns schema fragment:
    {
      "type": "object",
      "properties": {
        "item": {
          "type": "object",
          "properties": {
            "query": {"type": "string"},
            "context": {
              "type": "object",
              "properties": {
                "company": { ... }
              },
              "required": ["company"]
            }
          },
          "required": ["query", "context"]
        }
      },
      "required": ["item"]
    }

    :param paths: A list of dot-delimited strings, each representing a leaf path
        in the logical object hierarchy (e.g. ``"item.context.company.policy.security.passwords.rotation_days"``).
        Empty path segments are ignored.
    :type paths: List[str]
    :param force_leaf_type: The JSON Schema ``type`` value to assign to every leaf node
        produced from the supplied paths. Defaults to ``"string"``.
    :type force_leaf_type: str
    :return: A JSON Schema fragment describing the hierarchical structure implied by
        the input paths. The returned schema root always has ``type: object`` with
        recursively nested ``properties`` / ``required`` keys.
    :rtype: Dict[str, Any]
    """
    # Build tree where each node: {"__children__": { segment: node, ... }, "__leaf__": bool }
    root: Dict[str, Any] = {"__children__": {}, "__leaf__": False}

    def insert(path: str):
        parts = [p for p in path.split(".") if p]
        node = root
        for i, part in enumerate(parts):
            children = node["__children__"]
            if part not in children:
                children[part] = {"__children__": {}, "__leaf__": False}
            node = children[part]
            if i == len(parts) - 1:
                node["__leaf__"] = True

    for p in paths:
        insert(p)

    def to_schema(node: Dict[str, Any]) -> Dict[str, Any]:
        children = node["__children__"]
        if not children:
            # Leaf node
            return {"type": force_leaf_type}
        props = {}
        required = []
        for name, child in children.items():
            props[name] = to_schema(child)
        return {
            "type": "object",
            "properties": props,
            "required": required,
        }

    return to_schema(root)


def _generate_data_source_config(input_data_df: pd.DataFrame, column_mapping: Dict[str, str]) -> Dict[str, Any]:
    """
    Produce a data source config (JSON schema) that reflects nested object structure
    when column mappings reference dotted paths (e.g., item.context.company...).

    Backward compatibility:
      - If all referenced source paths are single tokens (flat), fall back to legacy flat schema.
      - Otherwise build a nested object schema covering only referenced leaves.

    :type input_data_df: pd.DataFrame
    :param input_data_df: The input data to be evaluated, as produced by the `_validate_and_load_data`
    :type column_mapping: Optional[Dict[str, str]]
    :param column_mapping: The column mapping to use for the evaluation. If None, the default mapping will be used.
    :return: A dictionary that can act as data source config for OAI evaluation group creation.
    :rtype: Dict[str, Any]
    helper function.
    """
    # Extract referenced data paths from mapping values of the form ${data.<path>} (ignore ${run.outputs.*})
    LOGGER.info(
        f"AOAI: Generating data source config for {len(input_data_df)} rows with {len(column_mapping)} column mapping(s)..."
    )
    referenced_paths: List[str] = []
    for v in column_mapping.values():
        m = DATA_PATH_PATTERN.match(v)
        if m:
            referenced_paths.append(m.group(1))

    LOGGER.info(f"AOAI: Found {len(referenced_paths)} referenced paths in column mappings: {referenced_paths}")
    # Decide if we have nested structures
    has_nested = any("." in p for p in referenced_paths)
    LOGGER.info(f"AOAI: Schema generation mode: {'nested' if has_nested else 'flat'}")

    if not referenced_paths or not has_nested:
        # Legacy flat behavior (existing logic): treat each mapping key as independent string field
        LOGGER.info("AOAI: Using flat schema generation (no nested structures detected).")
        data_source_config = {
            "type": "custom",
            "item_schema": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        }
        props = data_source_config["item_schema"]["properties"]
        req = data_source_config["item_schema"]["required"]
        for key in column_mapping.keys():
            if key in input_data_df and len(input_data_df[key]) > 0 and isinstance(input_data_df[key].iloc[0], list):
                props[key] = {"type": "array"}
            else:
                props[key] = {"type": "string"}
            req.append(key)
        LOGGER.info(f"AOAI: Flat schema generated with {len(props)} properties: {list(props.keys())}")
        return data_source_config

    # NEW: If all nested paths share the same first segment (e.g. 'item'),
    # treat that segment as the wrapper already provided by the JSONL line ("item": {...})
    # so we exclude it from the schema (schema describes the *inside* of "item").
    first_segments = {p.split(".")[0] for p in referenced_paths}
    strip_wrapper = False
    wrapper_name = None
    LOGGER.info(f"AOAI: First segments in referenced paths: {first_segments}")
    if len(first_segments) == 1:
        only_seg = next(iter(first_segments))
        # We only strip if that segment looks like the canonical wrapper.
        if only_seg == WRAPPER_KEY:
            strip_wrapper = True
            wrapper_name = only_seg
            LOGGER.info(f"AOAI: All paths start with wrapper '{WRAPPER_KEY}', will strip from schema.")

    effective_paths = referenced_paths
    if strip_wrapper:
        stripped = []
        for p in referenced_paths:
            parts = p.split(".", 1)
            if len(parts) == 2:
                stripped.append(parts[1])  # drop leading 'item.'
            else:
                # Path was just 'item' (no leaf) – ignore; it doesn't define a leaf value.
                continue
        # If stripping produced at least one usable path, adopt; else fall back to original.
        if stripped:
            effective_paths = stripped
            LOGGER.info(f"AOAI: Effective paths after stripping wrapper: {effective_paths}")

    LOGGER.info(f"AOAI: Building nested schema from {len(effective_paths)} effective paths...")
    nested_schema = _build_schema_tree_from_paths(effective_paths, force_leaf_type="string")

    LOGGER.info(f"AOAI: Nested schema generated successfully with type '{nested_schema.get('type')}'")
    return {
        "type": "custom",
        "item_schema": nested_schema,
    }


def _generate_default_data_source_config(input_data_df: pd.DataFrame) -> Dict[str, Any]:
    """Produce a data source config that naively maps all columns from the supplied data source into
    the OAI API.

    :param input_data_df: The input data to be evaluated, as produced by the `_validate_and_load_data`
    helper function.
    :type input_data_df: pd.DataFrame
    :return: A dictionary that can act as data source config for OAI evaluation group creation.
    :rtype: Dict[str, Any]
    """

    properties = {}
    required = []

    for column in input_data_df.columns:
        properties[column] = {
            "type": "string",
        }
        required.append(column)
    data_source_config = {
        "type": "custom",
        "item_schema": {
            "type": "object",
            "properties": properties,
            "required": required,
        },
    }
    return data_source_config


def _get_data_source(input_data_df: pd.DataFrame, column_mapping: Dict[str, str]) -> Dict[str, Any]:
    """
    Given a dataframe of data to be evaluated, and a column mapping,
    produce a dictionary that can be used as the data source input for an OAI evaluation run.
    Builds a nested 'item' object mirroring the hierarchical paths in the mapping values.
    :param input_data_df: The input data to be evaluated, as produced by the `_validate_and_load_data`
        helper function.
    :type input_data_df: pd.DataFrame
    :param column_mapping: The column mapping to use for the evaluation. If None, a naive 1:1 mapping is used.
    :type column_mapping: Optional[Dict[str, str]]
    :return: A dictionary that can be used as the data source input for an OAI evaluation run.
    :rtype: Dict[str, Any]
    """

    def _convert_value(val: Any) -> Any:
        """Convert to AOAI-friendly representation while preserving structure when useful."""
        if val is None:
            return ""
        if isinstance(val, str):
            return val
        if isinstance(val, bool):
            return val
        # Align numerics with legacy text-only JSONL payloads by turning them into strings.
        if isinstance(val, (int, float)):
            return str(val)
        if isinstance(val, (dict, list)):
            return val
        return str(val)

    def _get_value_from_path(normalized_row: Dict[str, Any], path: str) -> Any:
        cursor: Any = normalized_row
        for segment in path.split("."):
            if not isinstance(cursor, dict):
                return None
            cursor = cursor.get(segment)
            if cursor is None:
                return None
        return cursor

    LOGGER.info(
        f"AOAI: Building data source from {len(input_data_df)} rows with {len(column_mapping)} column mappings..."
    )
    # Gather path specs: list of tuples (original_mapping_value, relative_parts, dataframe_column_name)
    # relative_parts excludes the wrapper (so schema + content align).
    path_specs: List[Dict[str, Any]] = []

    for name, formatted_entry in column_mapping.items():
        if not (
            isinstance(formatted_entry, str) and formatted_entry.startswith("${") and formatted_entry.endswith("}")
        ):
            continue
        body = formatted_entry[2:-1]  # remove ${ }
        pieces = body.split(".")

        if not pieces:
            continue

        if pieces[0] == "data":
            # Data path: data.<maybe wrapper>.<...>
            if len(pieces) == 1:
                continue
            source_path = ".".join(pieces[1:])  # e.g. item.context.company...
            # Skip mapping of wrapper itself
            if source_path == WRAPPER_KEY:
                continue

            # Determine dataframe column name (it is the full dotted path as flattened earlier)
            dataframe_col = source_path

            # Relative parts for nested insertion (drop leading wrapper if present)
            if source_path.startswith(WRAPPER_KEY + "."):
                relative_path = source_path[len(WRAPPER_KEY) + 1 :]
            else:
                # Path not under wrapper; treat its segments as is (will live directly under wrapper)
                relative_path = source_path

            relative_parts = [p for p in relative_path.split(".") if p]

            # Defensive: if mapping alias differs from leaf, prefer actual path leaf to stay consistent.
            # (If you want alias override, replace relative_parts[-1] with name when name != path_leaf.)
            if not relative_parts:
                continue

            path_specs.append(
                {
                    "source_path": source_path,
                    "relative_parts": relative_parts,
                    "dataframe_col": dataframe_col,
                    "is_run_output": False,
                }
            )

        elif pieces[0] == "run" and len(pieces) >= 3 and pieces[1] == "outputs":
            # Target / run outputs become __outputs.<rest> columns
            run_col = "__outputs." + ".".join(pieces[2:])
            leaf_name = pieces[-1]
            path_specs.append(
                {
                    "source_path": None,
                    "relative_parts": [leaf_name],
                    "dataframe_col": run_col,
                    "is_run_output": True,
                }
            )

    LOGGER.info(f"AOAI: Processed {len(path_specs)} path specifications from column mappings.")
    content: List[Dict[str, Any]] = []

    for _, row in input_data_df.iterrows():
        normalized_row = _normalize_row_for_item_wrapper(row.to_dict())
        item_root: Dict[str, Any] = {}

        # Track which top-level keys under the wrapper have been populated via mappings
        processed_root_keys: Set[str] = set()

        for spec in path_specs:
            rel_parts = spec["relative_parts"]
            if not rel_parts:
                continue

            if spec["is_run_output"]:
                val = row.get(spec["dataframe_col"], None)
            else:
                source_path = cast(str, spec["source_path"])
                val = _get_value_from_path(normalized_row, source_path)
                if val is None:
                    val = row.get(spec["dataframe_col"], None)

            norm_val = _convert_value(val)

            cursor = item_root
            for seg in rel_parts[:-1]:
                nxt = cursor.get(seg)
                if not isinstance(nxt, dict):
                    nxt = {}
                    cursor[seg] = nxt
                cursor = nxt
            leaf_key = rel_parts[-1]
            cursor[leaf_key] = norm_val

            processed_root_keys.add(rel_parts[0])

        # Pull through any wrapper entries that were never explicitly mapped
        wrapper_view = normalized_row.get(WRAPPER_KEY, {})
        if isinstance(wrapper_view, dict):
            for key, raw_val in wrapper_view.items():
                if key in processed_root_keys:
                    continue
                if key in item_root:
                    continue
                item_root[key] = _convert_value(raw_val)

        content_row: Dict[str, Any] = {}
        for root_key in _RESERVED_ROOT_KEYS:
            if root_key in normalized_row:
                content_row[root_key] = _convert_value(normalized_row[root_key])

        content_row[WRAPPER_KEY] = item_root
        content.append(content_row)

    LOGGER.info(f"AOAI: Generated {len(content)} content items for data source.")
    return {
        "type": "jsonl",
        "source": {
            "type": "file_content",
            "content": content,
        },
    }


def _begin_eval_run(
    client: Union[OpenAI, AzureOpenAI],
    eval_group_id: str,
    run_name: str,
    input_data_df: pd.DataFrame,
    column_mapping: Dict[str, str],
    data_source_params: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Given an eval group id and a dataset file path, use the AOAI API to
    start an evaluation run with the given name and description.
    Returns a poller that can be used to monitor the run.

    :param client: The AOAI client to use for the evaluation.
    :type client: Union[OpenAI, AzureOpenAI]
    :param eval_group_id: The ID of the evaluation group to use for the evaluation run.
    :type eval_group_id: str
    :param run_name: The name of the evaluation run.
    :type run_name: str
    :param input_data_df: The input data to be evaluated, as produced by the `_validate_and_load_data`
        helper function.
    :type input_data_df: pd.DataFrame
    :return: The ID of the evaluation run.
    :rtype: str
    """

    LOGGER.info(f"AOAI: Creating eval run '{run_name}' for eval group {eval_group_id}...")
    data_source = _get_data_source(input_data_df, column_mapping)
    if data_source_params is not None:
        data_source.update(data_source_params)

    eval_run = client.evals.runs.create(
        eval_id=eval_group_id,
        data_source=cast(Any, data_source),  # Cast for type checker: dynamic schema dict accepted by SDK at runtime
        name=run_name,
        metadata={"sample_generation": "off", "file_format": "jsonl", "is_foundry_eval": "true"},
        # TODO decide if we want to add our own timeout value?
    )
    LOGGER.info(f"AOAI: Eval run created successfully with ID: {eval_run.id}")
    return eval_run.id


# Post built TODO: replace with _red_team.py's retry logic?
def _wait_for_run_conclusion(
    client: Union[OpenAI, AzureOpenAI], eval_group_id: str, eval_run_id: str, max_wait_seconds=21600
) -> Any:
    """
    Perform exponential backoff polling to get the results of an AOAI evaluation run.
    Raises an EvaluationException if max attempts are reached without receiving a concluding status.

    :param client: The AOAI client to use for the evaluation.
    :type client: Union[OpenAI, AzureOpenAI]
    :param eval_group_id: The ID of the evaluation group that contains the evaluation run of interest.
    :type eval_group_id: str
    :param eval_run_id: The evaluation run ID to get the results of.
    :type eval_run_id: str
    :param max_wait_seconds: The maximum amount of time to wait for the evaluation run to complete.
    :type max_wait_seconds: int
    :return: The results of the evaluation run.
    :rtype: Any
    """

    LOGGER.info(f"AOAI: Getting OAI eval run results from group/run {eval_group_id}/{eval_run_id}...")
    total_wait = 0
    iters = 0
    # start with ~51 minutes of exponential backoff
    # max wait time = 2^10 * 3 = 3072 seconds ~= 51 minutes
    wait_interval = 3  # Seconds.
    while True:
        wait_interval *= 1.5
        total_wait += wait_interval
        # Reduce last wait interval if total wait time exceeds max wait time
        if total_wait > max_wait_seconds:
            wait_interval -= total_wait - max_wait_seconds
        sleep(wait_interval)
        iters += 1
        response = client.evals.runs.retrieve(eval_id=eval_group_id, run_id=eval_run_id)
        LOGGER.info(f"AOAI: Polling iteration {iters}, status: {response.status}, total wait: {total_wait:.1f}s")
        if response.status not in ["queued", "in_progress"]:
            LOGGER.info(f"AOAI: Eval run {eval_run_id} reached terminal status: {response.status}")
            return response
        if total_wait > max_wait_seconds:
            raise EvaluationException(
                message=f"Timed out waiting for AOAI evaluation to complete after {iters}"
                + f" rounds of polling. Final status was {response.status}",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.FAILED_EXECUTION,
                target=ErrorTarget.AOAI_GRADER,
            )
