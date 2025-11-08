# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import inspect
import contextlib
import json
import logging
import math
import os
import re
import tempfile
import json
import time
from typing import Any, Callable, Dict, Iterable, Iterator, List, Literal, Optional, Set, Tuple, TypedDict, Union, cast

from openai import OpenAI, AzureOpenAI
from azure.ai.evaluation._legacy._adapters._constants import LINE_NUMBER
from azure.ai.evaluation._legacy._adapters.entities import Run
import pandas as pd

from azure.ai.evaluation._common.math import list_mean_nan_safe, apply_transform_nan_safe
from azure.ai.evaluation._common.utils import validate_azure_ai_project, is_onedp_project
from azure.ai.evaluation._evaluators._common._base_eval import EvaluatorBase
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from azure.ai.evaluation._aoai.aoai_grader import AzureOpenAIGrader

from .._constants import (
    CONTENT_SAFETY_DEFECT_RATE_THRESHOLD_DEFAULT,
    EVALUATION_PASS_FAIL_MAPPING,
    EvaluationMetrics,
    DefaultOpenEncoding,
    Prefixes,
    _InternalEvaluationMetrics,
    BINARY_AGGREGATE_SUFFIX,
    DEFAULT_OAI_EVAL_RUN_NAME,
    EVALUATION_EVENT_NAME,
    _EvaluatorMetricMapping,
)
from .._model_configurations import AzureAIProject, EvaluationResult, EvaluatorConfig, AppInsightsConfig
from .._user_agent import UserAgentSingleton
from ._batch_run import (
    EvalRunContext,
    CodeClient,
    ProxyClient,
    TargetRunContext,
    RunSubmitterClient,
)
from ._utils import (
    _apply_column_mapping,
    _log_metrics_and_instance_results,
    _trace_destination_from_project_scope,
    _write_output,
    DataLoaderFactory,
    _log_metrics_and_instance_results_onedp,
)
from ._batch_run.batch_clients import BatchClient, BatchClientRun

from ._evaluate_aoai import (
    _begin_aoai_evaluation,
    _split_evaluators_and_grader_configs,
    _get_evaluation_run_results,
    OAIEvalRunCreationInfo,
)

LOGGER = logging.getLogger(__name__)

# For metrics (aggregates) whose metric names intentionally differ from their
# originating column name, usually because the aggregation of the original value
# means something sufficiently different.
# Note that content safety metrics are handled separately.
METRIC_COLUMN_NAME_REPLACEMENTS = {
    "groundedness_pro_label": "groundedness_pro_passing_rate",
}


class __EvaluatorInfo(TypedDict):
    result: pd.DataFrame
    metrics: Dict[str, Any]
    run_summary: Dict[str, Any]


class __ValidatedData(TypedDict):
    """
    Simple dictionary that contains ALL pre-processed data and
    the resultant objects that are needed for downstream evaluation.
    """

    evaluators: Dict[str, Callable]
    graders: Dict[str, AzureOpenAIGrader]
    input_data_df: pd.DataFrame
    column_mapping: Dict[str, Dict[str, str]]
    target_run: Optional[BatchClientRun]
    batch_run_client: BatchClient
    batch_run_data: Union[str, os.PathLike, pd.DataFrame]


def _aggregate_other_metrics(df: pd.DataFrame) -> Tuple[List[str], Dict[str, float]]:
    """Identify and average various metrics that need to have the metric name be replaced,
    instead of having the metric match the originating column name.
    :param df: The dataframe of evaluation results.
    :type df: ~pandas.DataFrame
    :return: A tuple; the first element is a list of dataframe columns that were aggregated,
        and the second element is a dictionary of resultant new metric column names and their values.
    :rtype: Tuple[List[str], Dict[str, float]]
    """
    renamed_cols = []
    metric_columns = {}
    for col in df.columns:
        metric_prefix = col.split(".")[0]
        metric_name = col.split(".")[1]
        if metric_name in METRIC_COLUMN_NAME_REPLACEMENTS:
            renamed_cols.append(col)
            new_col_name = metric_prefix + "." + METRIC_COLUMN_NAME_REPLACEMENTS[metric_name]
            col_with_numeric_values = cast(List[float], pd.to_numeric(df[col], errors="coerce"))
            try:
                metric_columns[new_col_name] = round(list_mean_nan_safe(col_with_numeric_values), 2)
            except EvaluationException:  # only exception that can be cause is all NaN values
                msg = f"All score evaluations are NaN/None for column {col}. No aggregation can be performed."
                LOGGER.warning(msg)

    return renamed_cols, metric_columns


# pylint: disable=line-too-long
def _aggregate_content_safety_metrics(
    df: pd.DataFrame, evaluators: Dict[str, Callable]
) -> Tuple[List[str], Dict[str, float]]:
    """Find and aggregate defect rates for content safety metrics. Returns both a list
    of columns that were used to calculate defect rates and the defect rates themselves.

    :param df: The dataframe of evaluation results.
    :type df: ~pandas.DataFrame
    :param evaluators:  A dictionary mapping of strings to evaluator classes. This is used to identify
        content safety metrics, since they should start with a string that matches an evaluator name.
    :type evaluators: Dict[str, type]
    :return: A tuple; the first element is a list of dataframe columns that were used to calculate defect rates,
        and the second element is a dictionary of defect column names and defect rates.
    :rtype: Tuple[List[str], Dict[str, float]]
    """
    content_safety_metrics = [
        EvaluationMetrics.SEXUAL,
        EvaluationMetrics.SELF_HARM,
        EvaluationMetrics.HATE_UNFAIRNESS,
        EvaluationMetrics.VIOLENCE,
    ]
    content_safety_cols = []
    for col in df.columns:
        evaluator_name = col.split(".")[0]
        metric_name = col.split(".")[1]
        if evaluator_name in evaluators:
            # Check the namespace of the evaluator
            module = inspect.getmodule(evaluators[evaluator_name])
            if (
                module
                and metric_name.endswith("_score")
                and metric_name.replace("_score", "") in content_safety_metrics
            ):
                content_safety_cols.append(col)

    content_safety_df = df[content_safety_cols]
    defect_rates = {}
    for col in content_safety_df.columns:
        defect_rate_name = col.replace("_score", "_defect_rate")
        col_with_numeric_values = cast(List[float], pd.to_numeric(content_safety_df[col], errors="coerce"))
        try:
            col_with_boolean_values = apply_transform_nan_safe(
                col_with_numeric_values, lambda x: 1 if x >= CONTENT_SAFETY_DEFECT_RATE_THRESHOLD_DEFAULT else 0
            )
            defect_rates[defect_rate_name] = round(list_mean_nan_safe(col_with_boolean_values), 2)
        except EvaluationException:  # only exception that can be cause is all NaN values
            msg = f"All score evaluations are NaN/None for column {col}. No aggregation can be performed."
            LOGGER.warning(msg)

    return content_safety_cols, defect_rates


def _aggregate_label_defect_metrics(df: pd.DataFrame) -> Tuple[List[str], Dict[str, float]]:
    """Find and aggregate defect rates for label-based metrics. Returns both a list
    of columns that were used to calculate defect rates and the defect rates themselves.

    :param df: The dataframe of evaluation results.
    :type df: ~pandas.DataFrame
    :return: A tuple; the first element is a list of dataframe columns that were used to calculate defect rates,
        and the second element is a dictionary of defect column names and defect rates.
    :rtype: Tuple[List[str], Dict[str, float]]
    """
    handled_metrics = [
        EvaluationMetrics.PROTECTED_MATERIAL,
        EvaluationMetrics.FICTIONAL_CHARACTERS,
        EvaluationMetrics.ARTWORK,
        EvaluationMetrics.LOGOS_AND_BRANDS,
        _InternalEvaluationMetrics.ECI,
        EvaluationMetrics.XPIA,
        EvaluationMetrics.CODE_VULNERABILITY,
        EvaluationMetrics.UNGROUNDED_ATTRIBUTES,
    ]
    label_cols = []
    details_cols = []
    for col in df.columns:
        metric_name = col.split(".")[1]
        if metric_name.endswith("_label") and metric_name.replace("_label", "").lower() in handled_metrics:
            label_cols.append(col)
        if metric_name.endswith("_details") and metric_name.replace("_details", "").lower() in handled_metrics:
            details_cols = col

    label_df = df[label_cols]
    defect_rates = {}
    for col in label_df.columns:
        defect_rate_name = col.replace("_label", "_defect_rate")
        col_with_boolean_values = cast(List[float], pd.to_numeric(label_df[col], errors="coerce"))
        try:
            defect_rates[defect_rate_name] = round(list_mean_nan_safe(col_with_boolean_values), 2)
        except EvaluationException:  # only exception that can be cause is all NaN values
            msg = f"All score evaluations are NaN/None for column {col}. No aggregation can be performed."
            LOGGER.warning(msg)

    if details_cols:
        details_df = df[details_cols]
        detail_defect_rates = {}

        for key, value in details_df.items():
            _process_rows(value, detail_defect_rates)

        for key, value in detail_defect_rates.items():
            col_with_boolean_values = pd.to_numeric(value, errors="coerce")
            try:
                defect_rates[f"{details_cols}.{key}_defect_rate"] = round(
                    list_mean_nan_safe(col_with_boolean_values), 2
                )
            except EvaluationException:  # only exception that can be cause is all NaN values
                msg = f"All score evaluations are NaN/None for column {key}. No aggregation can be performed."
                LOGGER.warning(msg)

    return label_cols, defect_rates


def _process_rows(row, detail_defect_rates):
    for key, value in row.items():
        if key not in detail_defect_rates:
            detail_defect_rates[key] = []
        detail_defect_rates[key].append(value)
    return detail_defect_rates


def _aggregation_binary_output(df: pd.DataFrame) -> Dict[str, float]:
    """
    Aggregate binary output results (pass/fail) from evaluation dataframe.

    For each evaluator, calculates the proportion of "pass" results.

    :param df: The dataframe of evaluation results.
    :type df: ~pandas.DataFrame
    :return: A dictionary mapping evaluator names to the proportion of pass results.
    :rtype: Dict[str, float]
    """
    results = {}

    # Find all columns that end with "_result"
    result_columns = [col for col in df.columns if col.startswith("outputs.") and col.endswith("_result")]

    for col in result_columns:
        # Extract the evaluator name from the column name
        # (outputs.<evaluator>.<metric>_result)
        parts = col.split(".")
        evaluator_name = None
        if len(parts) >= 3:
            evaluator_name = parts[1]
        else:
            LOGGER.warning(
                "Skipping column '%s' due to unexpected format. Expected at least three parts separated by '.'", col
            )
            continue
        if evaluator_name:
            # Count the occurrences of each unique value (pass/fail)
            value_counts = df[col].value_counts().to_dict()

            # Calculate the proportion of EVALUATION_PASS_FAIL_MAPPING[True] results
            total_rows = len(df)
            pass_count = value_counts.get(EVALUATION_PASS_FAIL_MAPPING[True], 0)
            proportion = pass_count / total_rows if total_rows > 0 else 0.0

            # Set the result with the evaluator name as the key
            result_key = f"{evaluator_name}.{BINARY_AGGREGATE_SUFFIX}"
            results[result_key] = round(proportion, 2)

    return results


def _get_token_count_columns_to_exclude(df: pd.DataFrame) -> List[str]:
    """Identify token count columns from known SDK metrics that should be excluded from aggregation.

    Token counts from custom evaluators are not excluded, only those from EvaluationMetrics
    and _InternalEvaluationMetrics.

    :param df: The dataframe of evaluation results.
    :type df: ~pandas.DataFrame
    :return: List of column names to exclude from aggregation.
    :rtype: List[str]
    """
    # Get all metric values from EvaluationMetrics class
    evaluation_metrics_values = [
        getattr(EvaluationMetrics, attr)
        for attr in dir(EvaluationMetrics)
        if not attr.startswith("_") and isinstance(getattr(EvaluationMetrics, attr), str)
    ]

    # Get all metric values from _InternalEvaluationMetrics class
    internal_metrics_values = [
        getattr(_InternalEvaluationMetrics, attr)
        for attr in dir(_InternalEvaluationMetrics)
        if not attr.startswith("_") and isinstance(getattr(_InternalEvaluationMetrics, attr), str)
    ]

    # Combine all known metrics
    all_known_metrics = evaluation_metrics_values + internal_metrics_values

    # Find token count columns that belong to known metrics
    token_count_cols = [
        col
        for col in df.columns
        if (
            any(
                col.endswith(f"{metric}_prompt_tokens")
                or col.endswith(f"{metric}_completion_tokens")
                or col.endswith(f"{metric}_total_tokens")
                for metric in all_known_metrics
            )
        )
    ]

    return token_count_cols


def _aggregate_metrics(df: pd.DataFrame, evaluators: Dict[str, Callable]) -> Dict[str, float]:
    """Aggregate metrics from the evaluation results.
    On top of naively calculating the mean of most metrics, this function also identifies certain columns
    that represent defect rates and renames them accordingly. Other columns in the dataframe are dropped.
    EX: protected_material_label -> protected_material_defect_rate

    :param df: The dataframe of evaluation results.
    :type df: ~pandas.DataFrame
    :param evaluators:  A dictionary mapping of strings to evaluator classes.
    :type evaluators: Dict[str, Callable]
    :return: The aggregated metrics.
    :rtype: Dict[str, float]
    """
    binary_metrics = _aggregation_binary_output(df)

    df.rename(columns={col: col.replace("outputs.", "") for col in df.columns}, inplace=True)

    handled_columns = []
    defect_rates = {}
    # Rename certain columns as defect rates if we know that's what their aggregates represent
    # Content safety metrics
    content_safety_cols, cs_defect_rates = _aggregate_content_safety_metrics(df, evaluators)
    other_renamed_cols, renamed_cols = _aggregate_other_metrics(df)
    handled_columns.extend(content_safety_cols)
    handled_columns.extend(other_renamed_cols)
    defect_rates.update(cs_defect_rates)
    defect_rates.update(renamed_cols)
    # Label-based (true/false) metrics where 'true' means 'something is wrong'
    label_cols, label_defect_rates = _aggregate_label_defect_metrics(df)
    handled_columns.extend(label_cols)
    defect_rates.update(label_defect_rates)

    # Exclude token count columns from aggregation for known SDK metrics
    token_count_cols = _get_token_count_columns_to_exclude(df)
    handled_columns.extend(token_count_cols)

    # For rest of metrics, we will calculate mean
    df.drop(columns=handled_columns, inplace=True)

    # Convert "not applicable" strings to None to allow proper numeric aggregation
    df = df.replace(EvaluatorBase._NOT_APPLICABLE_RESULT, None)

    # NOTE: nan/None values don't count as as booleans, so boolean columns with
    # nan/None values won't have a mean produced from them.
    # This is different from label-based known evaluators, which have special handling.
    mean_value = df.mean(numeric_only=True)
    metrics = mean_value.to_dict()
    # Add defect rates back into metrics
    metrics.update(defect_rates)

    # Add binary threshold metrics based on pass/fail results
    metrics.update(binary_metrics)

    return metrics


def _validate_columns_for_target(
    df: pd.DataFrame,
    target: Callable,
) -> None:
    """
    Check that all columns needed by target function are present.

    :param df: The data frame to be validated.
    :type df: pd.DataFrame
    :param target: The callable to be applied to data set.
    :type target: Optional[Callable]
    :raises EvaluationException: If the column starts with "__outputs." or if the input data contains missing fields.
    """
    if any(c.startswith(Prefixes.TSG_OUTPUTS) for c in df.columns):
        msg = "The column cannot start from " f'"{Prefixes.TSG_OUTPUTS}" if target was defined.'
        raise EvaluationException(
            message=msg,
            internal_message=msg,
            target=ErrorTarget.EVALUATE,
            category=ErrorCategory.INVALID_VALUE,
            blame=ErrorBlame.USER_ERROR,
        )
    # If the target function is given, it may return
    # several columns and hence we cannot check the availability of columns
    # without knowing target function semantics.
    # Instead, here we will validate the columns, taken by target.
    required_inputs = [
        param.name
        for param in inspect.signature(target).parameters.values()
        if param.default == inspect.Parameter.empty and param.name not in ["kwargs", "args", "self"]
    ]

    missing_inputs = [col for col in required_inputs if col not in df.columns]
    if missing_inputs:
        msg = f"Missing required inputs for target: {missing_inputs}."
        raise EvaluationException(
            message=msg,
            target=ErrorTarget.EVALUATE,
            category=ErrorCategory.MISSING_FIELD,
            blame=ErrorBlame.USER_ERROR,
        )


def _validate_columns_for_evaluators(
    df: pd.DataFrame,
    evaluators: Dict[str, Callable],
    target: Optional[Callable],
    target_generated_columns: Optional[Set[str]],
    column_mapping: Dict[str, Dict[str, str]],
) -> None:
    """
    Check that all columns needed by evaluators are present.

    :param df: The data frame to be validated.
    :type df: pd.DataFrame
    :param evaluators: The dictionary of evaluators.
    :type evaluators: Dict[str, Callable]
    :param target: The callable to be applied to data set.
    :type target: Optional[Callable]
    :param target_generated_columns: The set of columns generated by the target callable.
    :type target_generated_columns: Optional[Set[str]]
    :param column_mapping: Dictionary mapping evaluator name to evaluator column mapping.
    :type column_mapping: Dict[str, Dict[str, str]]
    :raises EvaluationException: If data is missing required inputs or if the target callable did not generate the necessary columns.
    """
    missing_inputs_per_evaluator = {}

    for evaluator_name, evaluator in evaluators.items():
        # Apply column mapping
        mapping_config = column_mapping.get(evaluator_name, column_mapping.get("default", None))
        new_df = _apply_column_mapping(df, mapping_config)

        # Validate input data for evaluator
        is_built_in = evaluator.__module__.startswith("azure.ai.evaluation")
        if is_built_in:
            # Note that for built-in evaluators supporting the "conversation" parameter,
            # input parameters are now optional.
            evaluator_params = [
                param.name
                for param in inspect.signature(evaluator).parameters.values()
                if param.name not in ["kwargs", "args", "self"]
            ]

            if "conversation" in evaluator_params and "conversation" in new_df.columns:
                # Ignore the missing fields if "conversation" presents in the input data
                missing_inputs = []
            else:
                optional_params = (
                    cast(Any, evaluator)._OPTIONAL_PARAMS  # pylint: disable=protected-access
                    if hasattr(evaluator, "_OPTIONAL_PARAMS")
                    else []
                )
                excluded_params = set(new_df.columns).union(optional_params)
                missing_inputs = [col for col in evaluator_params if col not in excluded_params]

                # If "conversation" is the only parameter and it is missing, keep it in the missing inputs
                # Otherwise, remove it from the missing inputs
                if "conversation" in missing_inputs:
                    if not (evaluator_params == ["conversation"] and missing_inputs == ["conversation"]):
                        missing_inputs.remove("conversation")
        else:
            evaluator_params = [
                param.name
                for param in inspect.signature(evaluator).parameters.values()
                if param.default == inspect.Parameter.empty and param.name not in ["kwargs", "args", "self"]
            ]

            missing_inputs = [col for col in evaluator_params if col not in new_df.columns]

        if missing_inputs:
            missing_inputs_per_evaluator[evaluator_name] = missing_inputs

    if missing_inputs_per_evaluator:
        msg = "Some evaluators are missing required inputs:\n"
        for evaluator_name, missing in missing_inputs_per_evaluator.items():
            msg += f"- {evaluator_name}: {missing}\n"

        # Add the additional notes
        msg += "\nTo resolve this issue:\n"
        msg += "- Ensure the data contains required inputs.\n"
        if target is not None:
            msg += "- Verify that the target is generating the necessary columns for the evaluators. "
            msg += f"Currently generated columns: {target_generated_columns} \n"
        msg += "- Check that the column mapping is correctly configured."

        raise EvaluationException(
            message=msg.strip(),
            target=ErrorTarget.EVALUATE,
            category=ErrorCategory.MISSING_FIELD,
            blame=ErrorBlame.USER_ERROR,
        )


def _validate_and_load_data(target, data, evaluators, output_path, azure_ai_project, evaluation_name, tags):
    if data is None:
        msg = "The 'data' parameter is required for evaluation."
        raise EvaluationException(
            message=msg,
            target=ErrorTarget.EVALUATE,
            category=ErrorCategory.INVALID_VALUE,
            blame=ErrorBlame.USER_ERROR,
        )
    if not isinstance(data, (os.PathLike, str)):
        msg = "The 'data' parameter must be a string or a path-like object."
        raise EvaluationException(
            message=msg,
            target=ErrorTarget.EVALUATE,
            category=ErrorCategory.INVALID_VALUE,
            blame=ErrorBlame.USER_ERROR,
        )
    if not os.path.exists(data):
        msg = f"The input data file path '{data}' does not exist."
        raise EvaluationException(
            message=msg,
            target=ErrorTarget.EVALUATE,
            category=ErrorCategory.INVALID_VALUE,
            blame=ErrorBlame.USER_ERROR,
        )

    if target is not None:
        if not callable(target):
            msg = "The 'target' parameter must be a callable function."
            raise EvaluationException(
                message=msg,
                target=ErrorTarget.EVALUATE,
                category=ErrorCategory.INVALID_VALUE,
                blame=ErrorBlame.USER_ERROR,
            )

    if not evaluators:
        msg = "The 'evaluators' parameter is required and cannot be None or empty."
        raise EvaluationException(
            message=msg,
            target=ErrorTarget.EVALUATE,
            category=ErrorCategory.INVALID_VALUE,
            blame=ErrorBlame.USER_ERROR,
        )
    if not isinstance(evaluators, dict):
        msg = "The 'evaluators' parameter must be a dictionary."
        raise EvaluationException(
            message=msg,
            target=ErrorTarget.EVALUATE,
            category=ErrorCategory.INVALID_VALUE,
            blame=ErrorBlame.USER_ERROR,
        )

    if output_path is not None:
        if not isinstance(output_path, (os.PathLike, str)):
            msg = "The 'output_path' parameter must be a string or a path-like object."
            raise EvaluationException(
                message=msg,
                target=ErrorTarget.EVALUATE,
                category=ErrorCategory.INVALID_VALUE,
                blame=ErrorBlame.USER_ERROR,
            )

        output_dir = output_path if os.path.isdir(output_path) else os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            msg = f"The output directory '{output_dir}' does not exist. Please create the directory manually."
            raise EvaluationException(
                message=msg,
                target=ErrorTarget.EVALUATE,
                category=ErrorCategory.INVALID_VALUE,
                blame=ErrorBlame.USER_ERROR,
            )

    if azure_ai_project is not None:
        validate_azure_ai_project(azure_ai_project)

    if evaluation_name is not None:
        if not isinstance(evaluation_name, str) or not evaluation_name.strip():
            msg = "The 'evaluation_name' parameter must be a non-empty string."
            raise EvaluationException(
                message=msg,
                target=ErrorTarget.EVALUATE,
                category=ErrorCategory.INVALID_VALUE,
                blame=ErrorBlame.USER_ERROR,
            )

    try:
        data_loader = DataLoaderFactory.get_loader(data)
        initial_data_df = data_loader.load()
    except Exception as e:
        raise EvaluationException(
            message=f"Unable to load data from '{data}'. Supported formats are JSONL and CSV. Detailed error: {e}.",
            target=ErrorTarget.EVALUATE,
            category=ErrorCategory.INVALID_VALUE,
            blame=ErrorBlame.USER_ERROR,
        ) from e

    return initial_data_df


def _apply_target_to_data(
    target: Callable,
    data: Union[str, os.PathLike, pd.DataFrame],
    batch_client: BatchClient,
    initial_data: pd.DataFrame,
    evaluation_name: Optional[str] = None,
    **kwargs,
) -> Tuple[pd.DataFrame, Set[str], BatchClientRun]:
    """
    Apply the target function to the data set and return updated data and generated columns.

    :param target: The function to be applied to data.
    :type target: Callable
    :param data: The path to input jsonl or csv file.
    :type data: Union[str, os.PathLike]
    :param batch_client: The promptflow client to be used.
    :type batch_client: PFClient
    :param initial_data: The data frame with the loaded data.
    :type initial_data: pd.DataFrame
    :param evaluation_name: The name of the evaluation.
    :type evaluation_name: Optional[str]
    :return: The tuple, containing data frame and the list of added columns.
    :rtype: Tuple[pandas.DataFrame, List[str]]
    """

    _run_name = kwargs.get("_run_name")
    with TargetRunContext(batch_client):
        run: BatchClientRun = batch_client.run(
            flow=target,
            display_name=evaluation_name,
            data=data,
            stream=True,
            name=_run_name,
            evaluator_name=getattr(target, "__qualname__", "TARGET"),
        )
        target_output: pd.DataFrame = batch_client.get_details(run, all_results=True)
        run_summary = batch_client.get_run_summary(run)

    if run_summary["completed_lines"] == 0:
        msg = (
            f"Evaluation target failed to produce any results."
            f" Please check the logs at {run_summary['log_path']} for more details about cause of failure."
        )
        raise EvaluationException(
            message=msg,
            target=ErrorTarget.EVALUATE,
            category=ErrorCategory.FAILED_EXECUTION,
            blame=ErrorBlame.USER_ERROR,
        )

    # Log a warning if some rows failed
    failed_lines = run_summary.get("failed_lines", 0)
    completed_lines = run_summary["completed_lines"]
    total_lines = failed_lines + completed_lines

    if failed_lines > 0:
        LOGGER.warning(
            f"Target function completed {completed_lines} out of {total_lines} rows. "
            f"{failed_lines} rows failed and will be filled with NaN values."
        )

    # Remove input and output prefix
    generated_columns = {
        col[len(Prefixes.OUTPUTS) :] for col in target_output.columns if col.startswith(Prefixes.OUTPUTS)
    }
    # Sort output by line numbers
    target_output.set_index(f"inputs.{LINE_NUMBER}", inplace=True)
    target_output.sort_index(inplace=True)

    initial_data_with_line_numbers = initial_data.copy()
    initial_data_with_line_numbers[LINE_NUMBER] = range(len(initial_data))

    complete_index = initial_data_with_line_numbers[LINE_NUMBER]
    target_output = target_output.reindex(complete_index)

    target_output.reset_index(inplace=True, drop=False)
    # target_output contains only input columns, taken by function,
    # so we need to concatenate it to the input data frame.
    drop_columns = list(filter(lambda x: x.startswith("inputs"), target_output.columns))
    target_output.drop(drop_columns, inplace=True, axis=1)
    # Rename outputs columns to __outputs
    rename_dict = {col: col.replace(Prefixes.OUTPUTS, Prefixes.TSG_OUTPUTS) for col in target_output.columns}
    target_output.rename(columns=rename_dict, inplace=True)
    # Concatenate output to input - now both dataframes have the same number of rows
    target_output = pd.concat([initial_data, target_output], axis=1)

    return target_output, generated_columns, run


def _process_column_mappings(
    column_mapping: Dict[str, Optional[Dict[str, str]]],
) -> Dict[str, Dict[str, str]]:
    """Process column_mapping to replace ${target.} with ${data.}

    :param column_mapping: The configuration for evaluators.
    :type column_mapping: Dict[str, Optional[Dict[str, str]]]
    :return: The processed configuration.
    :rtype: Dict[str, Dict[str, str]]
    """

    processed_config: Dict[str, Dict[str, str]] = {}

    expected_references = re.compile(r"^\$\{(target|data)\.([a-zA-Z0-9_]+(?:\.[a-zA-Z0-9_]+)*)\}$")

    if column_mapping:
        for evaluator, mapping_config in column_mapping.items():
            if isinstance(mapping_config, dict):
                processed_config[evaluator] = {}

                for map_to_key, map_value in mapping_config.items():
                    # Check if there's any unexpected reference other than ${target.} or ${data.}
                    if not expected_references.search(map_value):
                        msg = "Unexpected references detected in 'column_mapping'. Ensure only ${target.} and ${data.} are used."
                        raise EvaluationException(
                            message=msg,
                            internal_message=msg,
                            target=ErrorTarget.EVALUATE,
                            category=ErrorCategory.INVALID_VALUE,
                            blame=ErrorBlame.USER_ERROR,
                        )

                    # Replace ${target.} with ${run.outputs.}
                    processed_config[evaluator][map_to_key] = map_value.replace("${target.", "${run.outputs.")

    return processed_config


def _rename_columns_conditionally(df: pd.DataFrame) -> pd.DataFrame:
    """
    Change the column names for data frame. The change happens inplace.

    The columns with _OUTPUTS prefix will not be changed. _OUTPUTS prefix will
    will be added to columns in target_generated set. The rest columns will get
    ".inputs" prefix.

    :param df: The data frame to apply changes to.
    :type df: pandas.DataFrame
    :return: The changed data frame.
    :rtype: pandas.DataFrame
    """
    rename_dict = {}
    for col in df.columns:
        # Rename columns generated by target.
        if Prefixes.TSG_OUTPUTS in col:
            rename_dict[col] = col.replace(Prefixes.TSG_OUTPUTS, Prefixes.OUTPUTS)
        else:
            rename_dict[col] = f"inputs.{col}"
    df.rename(columns=rename_dict, inplace=True)
    return df


def evaluate(
    *,
    data: Union[str, os.PathLike],
    evaluators: Dict[str, Union[Callable, AzureOpenAIGrader]],
    evaluation_name: Optional[str] = None,
    target: Optional[Callable] = None,
    evaluator_config: Optional[Dict[str, EvaluatorConfig]] = None,
    azure_ai_project: Optional[Union[str, AzureAIProject]] = None,
    output_path: Optional[Union[str, os.PathLike]] = None,
    fail_on_evaluator_errors: bool = False,
    tags: Optional[Dict[str, str]] = None,
    **kwargs,
) -> EvaluationResult:
    """Evaluates target or data with built-in or custom evaluators. If both target and data are provided,
        data will be run through target function and then results will be evaluated.

    :keyword data: Path to the data to be evaluated or passed to target if target is set.
        JSONL and CSV files are supported.  `target` and `data` both cannot be None. Required.
    :paramtype data: str
    :keyword evaluators: Evaluators to be used for evaluation. It should be a dictionary with key as alias for evaluator
        and value as the evaluator function. Also accepts AzureOpenAIGrader instances as values, which are processed separately.
        Required.
    :paramtype evaluators: Dict[str, Union[Callable, ~azure.ai.evaluation.AzureOpenAIGrader]]
    :keyword evaluation_name: Display name of the evaluation.
    :paramtype evaluation_name: Optional[str]
    :keyword target: Target to be evaluated. `target` and `data` both cannot be None
    :paramtype target: Optional[Callable]
    :keyword evaluator_config: Configuration for evaluators. The configuration should be a dictionary with evaluator
        names as keys and a values that are dictionaries containing the column mappings. The column mappings should
        be a dictionary with keys as the column names in the evaluator input and values as the column names in the
        input data or data generated by target.
    :paramtype evaluator_config: Optional[Dict[str, ~azure.ai.evaluation.EvaluatorConfig]]
    :keyword output_path: The local folder or file path to save evaluation results to if set. If folder path is provided
          the results will be saved to a file named `evaluation_results.json` in the folder.
    :paramtype output_path: Optional[str]
    :keyword azure_ai_project: The Azure AI project, which can either be a string representing the project endpoint
        or an instance of AzureAIProject. It contains subscription id, resource group, and project name.
    :paramtype azure_ai_project: Optional[Union[str, ~azure.ai.evaluation.AzureAIProject]]
    :keyword fail_on_evaluator_errors: Whether or not the evaluation should cancel early with an EvaluationException
        if ANY evaluator fails during their evaluation.
        Defaults to false, which means that evaluations will continue regardless of failures.
        If such failures occur, metrics may be missing, and evidence of failures can be found in the evaluation's logs.
    :paramtype fail_on_evaluator_errors: bool
    :keyword tags: A dictionary of tags to be added to the evaluation run for tracking and organization purposes.
        Keys and values must be strings. For more information about tag limits, see:
        https://learn.microsoft.com/en-us/azure/machine-learning/resource-limits-capacity?view=azureml-api-2#runs
    :paramtype tags: Optional[Dict[str, str]]
    :keyword user_agent: A string to append to the default user-agent sent with evaluation http requests
    :paramtype user_agent: Optional[str]
    :return: Evaluation results.
    :rtype: ~azure.ai.evaluation.EvaluationResult

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_evaluate.py
            :start-after: [START evaluate_method]
            :end-before: [END evaluate_method]
            :language: python
            :dedent: 8
            :caption: Run an evaluation on local data with one or more evaluators using azure.ai.evaluation.AzureAIProject

    .. admonition:: Example using Azure AI Project URL:

        .. literalinclude:: ../samples/evaluation_samples_evaluate_fdp.py
            :start-after: [START evaluate_method]
            :end-before: [END evaluate_method]
            :language: python
            :dedent: 8
            :caption: Run an evaluation on local data with one or more evaluators using Azure AI Project URL in following format
                https://{resource_name}.services.ai.azure.com/api/projects/{project_name}
    """
    try:
        user_agent: Optional[str] = kwargs.get("user_agent")
        with UserAgentSingleton().add_useragent_product(user_agent) if user_agent else contextlib.nullcontext():
            results = _evaluate(
                evaluation_name=evaluation_name,
                target=target,
                data=data,
                evaluators_and_graders=evaluators,
                evaluator_config=evaluator_config,
                azure_ai_project=azure_ai_project,
                output_path=output_path,
                fail_on_evaluator_errors=fail_on_evaluator_errors,
                tags=tags,
                **kwargs,
            )
            return results
    except Exception as e:
        # Handle multiprocess bootstrap error
        bootstrap_error = (
            "An attempt has been made to start a new process before the\n        "
            "current process has finished its bootstrapping phase."
        )
        if bootstrap_error in str(e):
            error_message = (
                "The evaluation failed due to an error during multiprocess bootstrapping."
                "Please ensure the evaluate API is properly guarded with the '__main__' block:\n\n"
                "    if __name__ == '__main__':\n"
                "        evaluate(...)"
            )
            raise EvaluationException(
                message=error_message,
                internal_message=error_message,
                target=ErrorTarget.EVALUATE,
                category=ErrorCategory.FAILED_EXECUTION,
                blame=ErrorBlame.USER_ERROR,
            ) from e

        # Ensure a consistent user experience when encountering errors by converting
        # all other exceptions to EvaluationException.
        if not isinstance(e, EvaluationException):
            raise EvaluationException(
                message=str(e),
                target=ErrorTarget.EVALUATE,
                category=ErrorCategory.FAILED_EXECUTION,
                blame=ErrorBlame.SYSTEM_ERROR,
            ) from e

        raise e


def _print_summary(per_evaluator_results: Dict[str, Any]) -> None:
    # Extract evaluators with a non-empty "run_summary"
    output_dict = {
        name: result["run_summary"] for name, result in per_evaluator_results.items() if result.get("run_summary")
    }

    if output_dict:
        print("======= Combined Run Summary (Per Evaluator) =======\n")
        print(json.dumps(output_dict, indent=4))
        print("\n====================================================\n")


def _print_fail_flag_warning() -> None:
    print(
        "Notice: fail_on_evaluator_errors is enabled. It is recommended that you disable "
        + "this flag for evaluations on large datasets (loosely defined as more than 10 rows of inputs, "
        + "or more than 4 evaluators). Using this flag on large datasets runs the risk of large runs failing "
        + "without producing any outputs, since a single failure will cancel the entire run "
        "when fail_on_evaluator_errors is enabled."
    )


def _evaluate(  # pylint: disable=too-many-locals,too-many-statements
    *,
    evaluators_and_graders: Dict[str, Union[Callable, AzureOpenAIGrader]],
    evaluation_name: Optional[str] = None,
    target: Optional[Callable] = None,
    data: Union[str, os.PathLike],
    evaluator_config: Optional[Dict[str, EvaluatorConfig]] = None,
    azure_ai_project: Optional[Union[str, AzureAIProject]] = None,
    output_path: Optional[Union[str, os.PathLike]] = None,
    fail_on_evaluator_errors: bool = False,
    tags: Optional[Dict[str, str]] = None,
    **kwargs,
) -> EvaluationResult:
    if fail_on_evaluator_errors:
        _print_fail_flag_warning()

    # Turn inputted mess of data into a dataframe, apply targets if needed
    # split graders and evaluators, and verify that column mappings are sensible.
    validated_data = _preprocess_data(
        data=data,
        evaluators_and_graders=evaluators_and_graders,
        evaluator_config=evaluator_config,
        target=target,
        output_path=output_path,
        azure_ai_project=azure_ai_project,
        evaluation_name=evaluation_name,
        fail_on_evaluator_errors=fail_on_evaluator_errors,
        tags=tags,
        **kwargs,
    )

    # extract relevant info from validated data
    column_mapping = validated_data["column_mapping"]
    evaluators = validated_data["evaluators"]
    graders = validated_data["graders"]
    input_data_df = validated_data["input_data_df"]
    results_df = pd.DataFrame()
    metrics: Dict[str, float] = {}
    eval_run_info_list: List[OAIEvalRunCreationInfo] = []
    eval_run_summary_dict = {}

    # Start OAI eval runs if any graders are present.
    need_oai_run = len(graders) > 0
    need_local_run = len(evaluators) > 0
    need_get_oai_results = False
    got_local_results = False
    if need_oai_run:
        try:
            aoi_name = evaluation_name if evaluation_name else DEFAULT_OAI_EVAL_RUN_NAME
            eval_run_info_list = _begin_aoai_evaluation(graders, column_mapping, input_data_df, aoi_name, **kwargs)
            need_get_oai_results = len(eval_run_info_list) > 0
        except EvaluationException as e:
            if need_local_run:
                # If there are normal evaluators, don't stop execution and try to run
                # those.
                LOGGER.warning(
                    "Remote Azure Open AI grader evaluations failed during run creation."
                    + " Continuing with local evaluators."
                )
                LOGGER.warning(e)
            else:
                raise e

    # Evaluate 'normal' evaluators. This includes built-in evaluators and any user-supplied callables.
    if need_local_run:
        try:
            eval_result_df, eval_metrics, per_evaluator_results = _run_callable_evaluators(
                validated_data=validated_data, fail_on_evaluator_errors=fail_on_evaluator_errors
            )
            results_df = eval_result_df
            metrics = eval_metrics
            got_local_results = True
            # TODO figure out how to update this printing to include OAI results?
            _print_summary(per_evaluator_results)
            eval_run_summary_dict = {name: result["run_summary"] for name, result in per_evaluator_results.items()}
            LOGGER.info(f"run_summary: \r\n{json.dumps(eval_run_summary_dict, indent=4)}")
        except EvaluationException as e:
            if need_get_oai_results:
                # If there are OAI graders, we only print a warning on local failures.
                LOGGER.warning("Local evaluations failed. Will still attempt to retrieve online grader results.")
                LOGGER.warning(e)
            else:
                raise e

    # Retrieve OAI eval run results if needed.
    if need_get_oai_results:
        try:
            aoai_results, aoai_metrics = _get_evaluation_run_results(eval_run_info_list)  # type: ignore
            # Post build TODO: add equivalent of  _print_summary(per_evaluator_results) here

            # Combine results if both evaluators and graders are present
            if len(evaluators) > 0:
                results_df = pd.concat([results_df, aoai_results], axis=1)
                metrics.update(aoai_metrics)
            else:
                # Otherwise combine aoai results with input data df to include input columns in outputs.
                results_df = pd.concat([input_data_df, aoai_results], axis=1)
                metrics = aoai_metrics
        except EvaluationException as e:
            if got_local_results:
                # If there are local eval results, we only print a warning on OAI failure.
                LOGGER.warning("Remote Azure Open AI grader evaluations failed. Still returning local results.")
                LOGGER.warning(e)
            else:
                raise e

    # Done with all evaluations, message outputs into final forms, and log results if needed.
    name_map = _map_names_to_builtins(evaluators, graders)
    if is_onedp_project(azure_ai_project):
        studio_url = _log_metrics_and_instance_results_onedp(
            metrics, results_df, azure_ai_project, evaluation_name, name_map, tags=tags, **kwargs
        )
    else:
        # Since tracing is disabled, pass None for target_run so a dummy evaluation run will be created each time.
        trace_destination = _trace_destination_from_project_scope(azure_ai_project) if azure_ai_project else None
        studio_url = None
        if trace_destination:
            studio_url = _log_metrics_and_instance_results(
                metrics, results_df, trace_destination, None, evaluation_name, name_map, tags=tags, **kwargs
            )

    result_df_dict = results_df.to_dict("records")
    result: EvaluationResult = {"rows": result_df_dict, "metrics": metrics, "studio_url": studio_url}  # type: ignore
    # _add_aoai_structured_results_to_results(result, LOGGER, kwargs.get("eval_meta_data"))

    eval_id: Optional[str] = kwargs.get("_eval_id")
    eval_run_id: Optional[str] = kwargs.get("_eval_run_id")
    eval_meta_data: Optional[Dict[str, Any]] = kwargs.get("_eval_meta_data")
    if kwargs.get("_convert_to_aoai_evaluation_result", False):
        _convert_results_to_aoai_evaluation_results(
            result, LOGGER, eval_id, eval_run_id, evaluators_and_graders, eval_run_summary_dict, eval_meta_data
        )
        if app_insights_configuration := kwargs.get("_app_insights_configuration"):
            emit_eval_result_events_to_app_insights(
                app_insights_configuration, result["_evaluation_results_list"], evaluator_config
            )

    if output_path:
        _write_output(output_path, result)
    return result


def _build_internal_log_attributes(
    event_data: Dict[str, Any],
    metric_name: str,
    evaluator_config: Optional[Dict[str, EvaluatorConfig]],
    internal_log_attributes: Dict[str, str],
) -> Dict[str, str]:
    """
    Build internal log attributes for OpenTelemetry logging.

    :param event_data: The event data containing threshold and name information
    :type event_data: Dict[str, Any]
    :param metric_name: The name of the metric being evaluated
    :type metric_name: str
    :param evaluator_config: Configuration for evaluators
    :type evaluator_config: Optional[Dict[str, EvaluatorConfig]]
    :return: Dictionary of internal log attributes
    :rtype: Dict[str, str]
    """
    # Add threshold if present
    if event_data.get("threshold"):
        internal_log_attributes["gen_ai.evaluation.threshold"] = str(event_data["threshold"])

    # Add testing criteria details if present
    testing_criteria_name = event_data.get("name")
    if testing_criteria_name:
        internal_log_attributes["gen_ai.evaluation.testing_criteria.name"] = testing_criteria_name

        # Get evaluator definition details
        if evaluator_config and testing_criteria_name in evaluator_config:
            testing_criteria_config = evaluator_config[testing_criteria_name]

            if evaluator_name := testing_criteria_config.get("_evaluator_name"):
                internal_log_attributes["gen_ai.evaluator.name"] = str(evaluator_name)

            if evaluator_version := testing_criteria_config.get("_evaluator_version"):
                internal_log_attributes["gen_ai.evaluator.version"] = str(evaluator_version)

            if evaluator_id := testing_criteria_config.get("_evaluator_id"):
                internal_log_attributes["gen_ai.evaluator.id"] = str(evaluator_id)

            if evaluator_definition := testing_criteria_config.get("_evaluator_definition"):
                metric_config_detail = evaluator_definition.get("metrics").get(metric_name)

                if metric_config_detail:
                    if metric_config_detail.get("min_value") is not None:
                        internal_log_attributes["gen_ai.evaluation.min_value"] = str(metric_config_detail["min_value"])
                    if metric_config_detail.get("max_value") is not None:
                        internal_log_attributes["gen_ai.evaluation.max_value"] = str(metric_config_detail["max_value"])

    return internal_log_attributes


def _log_events_to_app_insights(
    event_logger,
    events: List[Dict[str, Any]],
    log_attributes: Dict[str, Any],
    app_insights_config: AppInsightsConfig,
    data_source_item: Optional[Dict[str, Any]] = None,
    evaluator_config: Optional[Dict[str, EvaluatorConfig]] = None,
) -> None:
    """
    Log independent events directly to App Insights using OpenTelemetry event logging.

    :param event_logger: OpenTelemetry event logger instance
    :type event_logger: EventLogger
    :param events: List of event data dictionaries to log
    :type events: List[Dict[str, Any]]
    :param log_attributes: Attributes dict to use for each event (already includes extra_attributes if present)
    :type log_attributes: Dict[str, Any]
    :param app_insights_config: App Insights configuration containing connection string
    :type app_insights_config: AppInsightsConfig
    :param data_source_item: Data source item containing trace, response, and agent information
    :type data_source_item: Optional[Dict[str, Any]]
    """

    from opentelemetry._events import Event

    try:
        # Initialize values from AppInsights config as defaults
        trace_id = None
        span_id = None
        response_id = None
        conversation_id = None
        previous_response_id = None
        agent_id = app_insights_config.get("agent_id", None)
        agent_version = app_insights_config.get("agent_version", None)
        agent_name = app_insights_config.get("agent_name", None)

        # Data source item values have higher priority and will override AppInsights config defaults
        if data_source_item:
            for key, value in data_source_item.items():
                if key.endswith("trace_id") and value and isinstance(value, str):
                    # Remove dashes if present
                    trace_id_str = str(value).replace("-", "").lower()
                    if len(trace_id_str) == 32:  # Valid trace_id length
                        trace_id = int(trace_id_str, 16)
                elif key == "previous_response_id" and value and isinstance(value, str):
                    previous_response_id = value
                elif key == "response_id" and value and isinstance(value, str):
                    response_id = value
                elif key == "conversation_id" and value and isinstance(value, str):
                    conversation_id = value
                elif key == "agent_id" and value and isinstance(value, str):
                    agent_id = value
                elif key.endswith("span_id") and value and isinstance(value, str):
                    # Remove dashes if present and convert to int
                    span_id_str = str(value).replace("-", "").lower()
                    if len(span_id_str) == 16:  # Valid span_id length (64-bit = 16 hex chars)
                        span_id = int(span_id_str, 16)
                elif key == "agent_version" and value and isinstance(value, str):
                    agent_version = value
                elif key == "agent_name" and value and isinstance(value, str):
                    agent_name = value

        # Log each event as a separate log record
        for i, event_data in enumerate(events):
            try:
                # Prepare log record attributes with specific mappings
                # The standard attributes are already in https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-events.md#event-eventgen_aievaluationresult
                metric_name = event_data.get("metric")
                standard_log_attributes = {}
                # This attributes makes evaluation events to go into customEvents table in App Insights
                standard_log_attributes["microsoft.custom_event.name"] = EVALUATION_EVENT_NAME
                standard_log_attributes["gen_ai.evaluation.name"] = metric_name
                if event_data.get("score") is not None:
                    standard_log_attributes["gen_ai.evaluation.score.value"] = event_data.get("score")
                if event_data.get("label") is not None:
                    standard_log_attributes["gen_ai.evaluation.score.label"] = event_data.get("label")

                # Internal proposed attributes
                # Put it in internal property bag for now, will be expanded if we got sign-off to Otel standard later.
                internal_log_attributes = _build_internal_log_attributes(
                    event_data, metric_name, evaluator_config, log_attributes
                )

                # Optional field that may not always be present
                if "reason" in event_data:
                    standard_log_attributes["gen_ai.evaluation.explanation"] = str(event_data["reason"])

                # Handle error from sample if present
                # Put the error message in error.type to follow OTel semantic conventions
                error = event_data.get("sample", {}).get("error", {}).get("message", None)
                if error:
                    standard_log_attributes["error.type"] = error

                # Handle redteam attack properties if present
                if "properties" in event_data:
                    properties = event_data["properties"]

                    if "attack_success" in properties:
                        internal_log_attributes["gen_ai.redteam.attack.success"] = str(properties["attack_success"])

                    if "attack_technique" in properties:
                        internal_log_attributes["gen_ai.redteam.attack.technique"] = str(properties["attack_technique"])

                    if "attack_complexity" in properties:
                        internal_log_attributes["gen_ai.redteam.attack.complexity"] = str(
                            properties["attack_complexity"]
                        )

                    if "attack_success_threshold" in properties:
                        internal_log_attributes["gen_ai.redteam.attack.success_threshold"] = str(
                            properties["attack_success_threshold"]
                        )

                # Add data source item attributes if present
                if response_id:
                    standard_log_attributes["gen_ai.response.id"] = response_id
                if conversation_id:
                    standard_log_attributes["gen_ai.conversation.id"] = conversation_id
                if previous_response_id:
                    internal_log_attributes["gen_ai.previous.response.id"] = previous_response_id
                if agent_id:
                    standard_log_attributes["gen_ai.agent.id"] = agent_id
                if agent_name:
                    standard_log_attributes["gen_ai.agent.name"] = agent_name
                if agent_version:
                    internal_log_attributes["gen_ai.agent.version"] = agent_version

                # Combine standard and internal attributes, put internal under the properties bag
                standard_log_attributes["internal_properties"] = json.dumps(internal_log_attributes)
                # Anonymize IP address to prevent Azure GeoIP enrichment and location tracking
                standard_log_attributes["http.client_ip"] = "0.0.0.0"

                event_logger.emit(
                    Event(
                        name=EVALUATION_EVENT_NAME,
                        attributes=standard_log_attributes,
                        body=EVALUATION_EVENT_NAME,
                        trace_id=trace_id if trace_id is not None else None,
                        span_id=span_id if span_id is not None else None,
                    )
                )

            except Exception as e:
                LOGGER.warning(f"Failed to log event {i}: {e}")

    except Exception as e:
        LOGGER.error(f"Failed to log events to App Insights: {e}")


def emit_eval_result_events_to_app_insights(
    app_insights_config: AppInsightsConfig,
    results: List[Dict],
    evaluator_config: Optional[Dict[str, EvaluatorConfig]] = None,
) -> None:
    """
    Emit evaluation result events to App Insights using OpenTelemetry logging.
    Each result is logged as an independent log record, potentially including trace context.

    :param app_insights_config: App Insights configuration containing connection string
    :type app_insights_config: AppInsightsConfig
    :param results: List of evaluation results to log
    :type results: List[Dict]
    """

    from opentelemetry import _logs
    from opentelemetry.sdk._logs import LoggerProvider
    from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.semconv.resource import ResourceAttributes
    from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter
    from opentelemetry._events import get_event_logger
    from opentelemetry.sdk._events import EventLoggerProvider

    if not results:
        LOGGER.debug("No results to log to App Insights")
        return

    try:
        # Configure OpenTelemetry logging with anonymized Resource attributes

        # Create a resource with minimal attributes to prevent sensitive data collection
        # SERVICE_INSTANCE_ID maps to cloud_RoleInstance in Azure Monitor and prevents
        # Azure Monitor from auto-detecting the device hostname
        anonymized_resource = Resource.create(
            {
                ResourceAttributes.SERVICE_NAME: "unknown",
                ResourceAttributes.SERVICE_INSTANCE_ID: "unknown",
            }
        )

        logger_provider = LoggerProvider(resource=anonymized_resource)
        _logs.set_logger_provider(logger_provider)

        # Create Azure Monitor log exporter
        azure_log_exporter = AzureMonitorLogExporter(connection_string=app_insights_config["connection_string"])

        # Add the Azure Monitor exporter to the logger provider
        logger_provider.add_log_record_processor(BatchLogRecordProcessor(azure_log_exporter))

        # Create event logger
        event_provider = EventLoggerProvider(logger_provider)
        event_logger = get_event_logger(__name__, event_logger_provider=event_provider)

        # Initialize base log attributes with extra_attributes if present, otherwise empty dict
        base_log_attributes = app_insights_config.get("extra_attributes", {})

        # Add AppInsights config attributes with proper semantic convention mappings
        if "run_type" in app_insights_config:
            base_log_attributes["gen_ai.evaluation.azure_ai_type"] = str(app_insights_config["run_type"])
        if "schedule_type" in app_insights_config:
            base_log_attributes["gen_ai.evaluation.azure_ai_scheduled"] = str(app_insights_config["schedule_type"])
        if "run_id" in app_insights_config:
            base_log_attributes["gen_ai.evaluation.run.id"] = str(app_insights_config["run_id"])
        if "project_id" in app_insights_config:
            base_log_attributes["gen_ai.azure_ai_project.id"] = str(app_insights_config["project_id"])

        for result in results:
            # Create a copy of base attributes for this result's events
            log_attributes = base_log_attributes.copy()

            _log_events_to_app_insights(
                event_logger=event_logger,
                events=result["results"],
                log_attributes=log_attributes,
                data_source_item=result["datasource_item"] if "datasource_item" in result else None,
                evaluator_config=evaluator_config,
                app_insights_config=app_insights_config,
            )
        # Force flush to ensure events are sent
        logger_provider.force_flush()
        LOGGER.info(f"Successfully logged {len(results)} evaluation results to App Insights")

    except Exception as e:
        LOGGER.error(f"Failed to emit evaluation results to App Insights: {e}")


def _preprocess_data(
    data: Union[str, os.PathLike],
    evaluators_and_graders: Dict[str, Union[Callable, AzureOpenAIGrader]],
    evaluator_config: Optional[Dict[str, EvaluatorConfig]] = None,
    target: Optional[Callable] = None,
    output_path: Optional[Union[str, os.PathLike]] = None,
    azure_ai_project: Optional[Union[str, AzureAIProject]] = None,
    evaluation_name: Optional[str] = None,
    fail_on_evaluator_errors: bool = False,
    tags: Optional[Dict[str, str]] = None,
    **kwargs,
) -> __ValidatedData:
    # Process evaluator config to replace ${target.} with ${data.}
    if evaluator_config is None:
        evaluator_config = {}

    input_data_df = _validate_and_load_data(
        target, data, evaluators_and_graders, output_path, azure_ai_project, evaluation_name, tags
    )
    if target is not None:
        _validate_columns_for_target(input_data_df, target)

    # extract column mapping dicts into dictionary mapping evaluator name to column mapping
    column_mapping = _process_column_mappings(
        {
            evaluator_name: evaluator_configuration.get("column_mapping", None)
            for evaluator_name, evaluator_configuration in evaluator_config.items()
        }
    )

    # Create default configuration for evaluators that directly maps
    # input data names to keyword inputs of the same name in the evaluators.
    column_mapping = column_mapping or {}
    column_mapping.setdefault("default", {})

    # Split normal evaluators and OAI graders
    evaluators, graders = _split_evaluators_and_grader_configs(evaluators_and_graders)

    target_run: Optional[BatchClientRun] = None
    target_generated_columns: Set[str] = set()
    batch_run_client: BatchClient
    batch_run_data: Union[str, os.PathLike, pd.DataFrame] = data

    def get_client_type(evaluate_kwargs: Dict[str, Any]) -> Literal["run_submitter", "pf_client", "code_client"]:
        """Determines the BatchClient to use from provided kwargs (_use_run_submitter_client and _use_pf_client)"""
        _use_run_submitter_client = cast(Optional[bool], kwargs.pop("_use_run_submitter_client", None))
        _use_pf_client = cast(Optional[bool], kwargs.pop("_use_pf_client", None))

        if _use_run_submitter_client is None and _use_pf_client is None:
            # If both are unset, return default
            return "run_submitter"

        if _use_run_submitter_client and _use_pf_client:
            raise EvaluationException(
                message="Only one of _use_pf_client and _use_run_submitter_client should be set to True.",
                target=ErrorTarget.EVALUATE,
                category=ErrorCategory.INVALID_VALUE,
                blame=ErrorBlame.USER_ERROR,
            )

        if _use_run_submitter_client == False and _use_pf_client == False:
            return "code_client"

        if _use_run_submitter_client:
            return "run_submitter"
        if _use_pf_client:
            return "pf_client"

        if _use_run_submitter_client is None and _use_pf_client == False:
            return "run_submitter"
        if _use_run_submitter_client == False and _use_pf_client is None:
            return "pf_client"

        assert False, "This should be impossible"

    client_type: Literal["run_submitter", "pf_client", "code_client"] = get_client_type(kwargs)

    if client_type == "run_submitter":
        batch_run_client = RunSubmitterClient(raise_on_errors=fail_on_evaluator_errors)
        batch_run_data = input_data_df
    elif client_type == "pf_client":
        batch_run_client = ProxyClient(user_agent=UserAgentSingleton().value)
        # Ensure the absolute path is Re to pf.run, as relative path doesn't work with
        # multiple evaluators. If the path is already absolute, abspath will return the original path.
        batch_run_data = os.path.abspath(data)
    elif client_type == "code_client":
        batch_run_client = CodeClient()
        batch_run_data = input_data_df

    # If target is set, apply 1-1 column mapping from target outputs to evaluator inputs
    if data is not None and target is not None:
        input_data_df, target_generated_columns, target_run = _apply_target_to_data(
            target, batch_run_data, batch_run_client, input_data_df, evaluation_name, **kwargs
        )

        # IMPORTANT FIX: For ProxyClient, create a temporary file with the complete dataframe
        # This ensures that evaluators get all rows (including failed ones with NaN values)
        if isinstance(batch_run_client, ProxyClient):
            # Create a temporary JSONL file with the complete dataframe
            temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
            try:
                for _, row in input_data_df.iterrows():
                    row_dict = row.to_dict()
                    temp_file.write(json.dumps(row_dict) + "\n")
                temp_file.close()
                batch_run_data = temp_file.name

                # Update column mappings to use data references instead of run outputs
                for evaluator_name, mapping in column_mapping.items():
                    mapped_to_values = set(mapping.values())
                    for col in target_generated_columns:
                        # Use data reference instead of run output to ensure we get all rows
                        target_reference = f"${{data.{Prefixes.TSG_OUTPUTS}{col}}}"

                        # We will add our mapping only if customer did not map target output.
                        if col not in mapping and target_reference not in mapped_to_values:
                            column_mapping[evaluator_name][col] = target_reference

                # Don't pass the target_run since we're now using the complete dataframe
                target_run = None

            except Exception as e:
                # Clean up the temp file if something goes wrong
                if os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)
                raise e
        else:
            # For DataFrame-based clients, update batch_run_data to use the updated input_data_df
            batch_run_data = input_data_df

            # Update column mappings for DataFrame clients
            for evaluator_name, mapping in column_mapping.items():
                mapped_to_values = set(mapping.values())
                for col in target_generated_columns:
                    target_reference = f"${{data.{Prefixes.TSG_OUTPUTS}{col}}}"

                    # We will add our mapping only if customer did not map target output.
                    if col not in mapping and target_reference not in mapped_to_values:
                        column_mapping[evaluator_name][col] = target_reference

    # After we have generated all columns, we can check if we have everything we need for evaluators.
    _validate_columns_for_evaluators(input_data_df, evaluators, target, target_generated_columns, column_mapping)

    # Apply 1-1 mapping from input data to evaluator inputs, excluding values already assigned
    # via target mapping.
    # If both the data and the output dictionary of the target function
    # have the same column, then the target function value is used.
    # NEW: flatten nested object columns (e.g., 'item') so we can map leaf values automatically.
    # Ensure the data does not contain top-level 'conversation' or 'messages' columns (which indicate chat/conversation data)
    if input_data_df is not None:
        if "conversation" in input_data_df.columns or "messages" in input_data_df.columns:
            # No action is taken when 'conversation' or 'messages' columns are present,
            # as these indicate chat/conversation data which should not be flattened or mapped by default.
            pass
        else:
            input_data_df = _flatten_object_columns_for_default_mapping(input_data_df)

    # Build default mapping for leaves:
    if input_data_df is not None:
        # First, map flattened nested columns (those containing a dot) to leaf names.
        for col in input_data_df.columns:
            # Skip target output columns
            if col.startswith(Prefixes.TSG_OUTPUTS):
                continue
            # Skip root container columns (no dot) here; they'll be handled below if truly primitive.
            if "." in col:
                leaf_name = col.split(".")[-1]
                if leaf_name not in column_mapping["default"]:
                    column_mapping["default"][leaf_name] = f"${{data.{col}}}"

        # Then, handle remaining top-level primitive columns (original logic).
        for col in input_data_df.columns:
            if (
                not col.startswith(Prefixes.TSG_OUTPUTS)
                and col not in column_mapping["default"].keys()
                and "." not in col  # only pure top-level primitives
            ):
                column_mapping["default"][col] = f"${{data.{col}}}"

    return __ValidatedData(
        evaluators=evaluators,
        graders=graders,
        input_data_df=input_data_df,
        column_mapping=column_mapping,
        target_run=target_run,
        batch_run_client=batch_run_client,
        batch_run_data=batch_run_data,
    )


def _flatten_object_columns_for_default_mapping(
    df: pd.DataFrame, root_prefixes: Optional[Iterable[str]] = None
) -> pd.DataFrame:
    """Flatten nested dictionary-valued columns into dotted leaf columns.

    For any column whose cells (in at least one row) are ``dict`` objects, this utility discovers all
    leaf paths (recursively descending only through ``dict`` nodes) and materializes new DataFrame
    columns named ``"<original_col>.<nested.path.leaf>"`` for every unique leaf encountered across
    all rows. A *leaf* is defined as any value that is **not** a ``dict`` (lists / primitives / ``None``
    are all treated as leaves). Existing columns are never overwritten (idempotent behavior).

    Example
        If a column ``item`` contains objects like ``{"a": {"b": 1, "c": 2}}`` a pair of new
        columns ``item.a.b`` and ``item.a.c`` will be added with the corresponding scalar values.

    :param df: Input DataFrame to flatten in place.
    :type df: ~pandas.DataFrame
    :param root_prefixes: Optional iterable restricting which top-level columns are considered
        for flattening. If ``None``, all columns containing at least one ``dict`` value are processed.
    :type root_prefixes: Optional[Iterable[str]]
    :return: The same DataFrame instance (returned for convenient chaining).
    :rtype: ~pandas.DataFrame
    """
    candidate_cols = []
    if root_prefixes is not None:
        candidate_cols = [c for c in root_prefixes if c in df.columns]
    else:
        # pick columns where at least one non-null value is a dict
        for c in df.columns:
            series = df[c]
            if series.map(lambda v: isinstance(v, dict)).any():
                candidate_cols.append(c)

    def _extract_leaves(obj: Any, prefix: str) -> Iterator[Tuple[str, Any]]:
        if isinstance(obj, dict):
            for k, v in obj.items():
                new_prefix = f"{prefix}.{k}" if prefix else k
                if isinstance(v, dict):
                    yield from _extract_leaves(v, new_prefix)
                else:
                    # treat list / primitive / None as leaf
                    yield new_prefix, v

    for root_col in candidate_cols:
        # Build a union of leaf paths across rows to ensure consistent columns
        leaf_paths: Set[str] = set()
        for val in df[root_col]:
            if isinstance(val, dict):
                for path, _ in _extract_leaves(val, root_col):
                    leaf_paths.add(path)

        if not leaf_paths:
            continue

        # Create each flattened column if absent
        for path in leaf_paths:
            if path in df.columns:
                continue  # already present
            relative_keys = path[len(root_col) + 1 :].split(".") if len(path) > len(root_col) else []

            def getter(root_val: Any) -> Any:
                cur = root_val
                for rk in relative_keys:
                    if not isinstance(cur, dict):
                        return None
                    cur = cur.get(rk, None)
                return cur

            df[path] = df[root_col].map(lambda rv: getter(rv) if isinstance(rv, dict) else None)

    return df


def _run_callable_evaluators(
    validated_data: __ValidatedData,
    fail_on_evaluator_errors: bool = False,
    **kwargs,
) -> Tuple[pd.DataFrame, Dict[str, Any], Dict[str, __EvaluatorInfo]]:

    # Extract needed values
    batch_run_client = validated_data["batch_run_client"]
    target_run = validated_data["target_run"]
    batch_run_data = validated_data["batch_run_data"]
    column_mapping = validated_data["column_mapping"]
    evaluators = validated_data["evaluators"]

    # Clean up temporary file after evaluation if it was created
    temp_file_to_cleanup = None
    if (
        isinstance(batch_run_client, ProxyClient)
        and isinstance(batch_run_data, str)
        and batch_run_data.endswith(".jsonl")
    ):
        # Check if it's a temporary file (contains temp directory path)
        if tempfile.gettempdir() in batch_run_data:
            temp_file_to_cleanup = batch_run_data

    try:
        with EvalRunContext(batch_run_client):
            runs = {
                evaluator_name: batch_run_client.run(
                    flow=evaluator,
                    data=batch_run_data,
                    # Don't pass target_run when using complete dataframe
                    run=target_run,
                    evaluator_name=evaluator_name,
                    column_mapping=column_mapping.get(evaluator_name, column_mapping.get("default", None)),
                    stream=True,
                    name=kwargs.get("_run_name"),
                )
                for evaluator_name, evaluator in evaluators.items()
            }

            # get_details needs to be called within EvalRunContext scope in order to have user agent populated
            per_evaluator_results: Dict[str, __EvaluatorInfo] = {
                evaluator_name: {
                    "result": batch_run_client.get_details(run, all_results=True),
                    "metrics": batch_run_client.get_metrics(run),
                    "run_summary": batch_run_client.get_run_summary(run),
                }
                for evaluator_name, run in runs.items()
            }
    finally:
        # Clean up temporary file if it was created
        if temp_file_to_cleanup and os.path.exists(temp_file_to_cleanup):
            try:
                os.unlink(temp_file_to_cleanup)
            except Exception as e:
                LOGGER.warning(f"Failed to clean up temporary file {temp_file_to_cleanup}: {e}")
    # Concatenate all results
    evaluators_result_df = pd.DataFrame()
    evaluators_metric = {}
    for evaluator_name, evaluator_result in per_evaluator_results.items():
        if fail_on_evaluator_errors and evaluator_result["run_summary"]["failed_lines"] > 0:
            _print_summary(per_evaluator_results)
            _turn_error_logs_into_exception(evaluator_result["run_summary"]["log_path"] + "/error.json")

        evaluator_result_df = evaluator_result["result"]

        # drop input columns
        evaluator_result_df = evaluator_result_df.drop(
            columns=[col for col in evaluator_result_df.columns if str(col).startswith(Prefixes.INPUTS)]
        )

        # rename output columns
        # Assuming after removing inputs columns, all columns are output columns
        evaluator_result_df.rename(
            columns={
                col: f"outputs.{evaluator_name}.{str(col).replace(Prefixes.OUTPUTS, '')}"
                for col in evaluator_result_df.columns
            },
            inplace=True,
        )

        evaluators_result_df = (
            pd.concat([evaluators_result_df, evaluator_result_df], axis=1, verify_integrity=True)
            if evaluators_result_df is not None
            else evaluator_result_df
        )

        evaluators_metric.update({f"{evaluator_name}.{k}": v for k, v in evaluator_result["metrics"].items()})

    # Rename columns, generated by target function to outputs instead of inputs.
    # If target generates columns, already present in the input data, these columns
    # will be marked as outputs already so we do not need to rename them.

    input_data_df = _rename_columns_conditionally(validated_data["input_data_df"])
    eval_result_df = pd.concat([input_data_df, evaluators_result_df], axis=1, verify_integrity=True)
    eval_metrics = _aggregate_metrics(evaluators_result_df, evaluators)
    eval_metrics.update(evaluators_metric)

    return eval_result_df, eval_metrics, per_evaluator_results


def _map_names_to_builtins(
    evaluators: Dict[str, Callable],
    graders: Dict[str, AzureOpenAIGrader],
) -> Dict[str, str]:
    """
    Construct a mapping from user-supplied evaluator names to which known, built-in
    evaluator or grader they refer to. Custom evaluators are excluded from the mapping
    as we only want to track built-in evaluators and graders.

    :param evaluators: The dictionary of evaluators.
    :type evaluators: Dict[str, Callable]
    :param graders: The dictionary of graders.
    :type graders: Dict[str, AzureOpenAIGrader]
    :param evaluator_config: The configuration for evaluators.
    :type evaluator_config: Optional[Dict[str, EvaluatorConfig]]

    """
    from .._eval_mapping import EVAL_CLASS_MAP

    name_map = {}

    for name, evaluator in evaluators.items():
        # Check if the evaluator is a known built-in evaluator
        found_eval = False
        for eval_class, eval_id in EVAL_CLASS_MAP.items():
            if isinstance(evaluator, eval_class):
                name_map[name] = eval_id
                found_eval = True
                break
        if not found_eval:
            # Skip custom evaluators - we only want to track built-in evaluators
            pass

    for name, grader in graders.items():
        name_map[name] = grader.id

    return name_map


def _turn_error_logs_into_exception(log_path: str) -> None:
    """Produce an EvaluationException using the contents of the inputted
    file as the error message.

    :param log_path: The path to the error log file.
    :type log_path: str
    """
    with open(log_path, "r", encoding=DefaultOpenEncoding.READ) as file:
        error_message = file.read()
    raise EvaluationException(
        message=error_message,
        target=ErrorTarget.EVALUATE,
        category=ErrorCategory.FAILED_EXECUTION,
        blame=ErrorBlame.UNKNOWN,
    )


def _convert_results_to_aoai_evaluation_results(
    results: EvaluationResult,
    logger: logging.Logger,
    eval_id: Optional[str] = None,
    eval_run_id: Optional[str] = None,
    evaluators: Dict[str, Union[Callable, AzureOpenAIGrader]] = None,
    eval_run_summary: Optional[Dict[str, Any]] = None,
    eval_meta_data: Optional[Dict[str, Any]] = None,
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

    if evaluators is None:
        return

    # Get the testing_criteria_name and testing_criteria_type from evaluators
    testing_criteria_name_types_metrics: Optional[Dict[str, Any]] = {}
    criteria_name_types_from_meta: Optional[Dict[str, str]] = {}
    if eval_meta_data and "testing_criteria" in eval_meta_data:
        testing_criteria_list: Optional[List[Dict[str, Any]]] = eval_meta_data.get("testing_criteria")
        if testing_criteria_list is not None:
            for criteria in testing_criteria_list:
                criteria_name = criteria.get("name")
                criteria_type = criteria.get("type")
                if criteria_name is not None and criteria_type is not None:
                    criteria_name_types_from_meta[criteria_name] = criteria

    for criteria_name, evaluator in evaluators.items():
        criteria_type = None
        metrics = []
        if criteria_name in criteria_name_types_from_meta:
            criteria_type = criteria_name_types_from_meta[criteria_name].get("type", None)
            evaluator_name = criteria_name_types_from_meta[criteria_name].get("evaluator_name", None)
            current_evaluator_metrics = criteria_name_types_from_meta[criteria_name].get("metrics", None)
            if current_evaluator_metrics and len(current_evaluator_metrics) > 0:
                metrics.extend(current_evaluator_metrics)
            elif evaluator_name:
                if criteria_type == "azure_ai_evaluator" and evaluator_name.startswith("builtin."):
                    evaluator_name = evaluator_name.replace("builtin.", "")
                metrics_mapped = _EvaluatorMetricMapping.EVALUATOR_NAME_METRICS_MAPPINGS.get(evaluator_name, [])
                if metrics_mapped and len(metrics_mapped) > 0:
                    metrics.extend(metrics_mapped)
                else:
                    metrics.append(criteria_name)
            else:
                metrics.append(criteria_name)
        elif isinstance(evaluator, AzureOpenAIGrader):
            criteria_type = evaluator._type  # pylint: disable=protected-access
            metrics.append(criteria_name)
        elif isinstance(evaluator, EvaluatorBase):
            criteria_type = "azure_ai_evaluator"
            evaluator_class_name = evaluator.__class__.__name__
            eval_name = _EvaluatorMetricMapping.EVAL_CLASS_NAME_MAP.get(evaluator_class_name, None)
            if eval_name:
                metrics_mapped = _EvaluatorMetricMapping.EVALUATOR_NAME_METRICS_MAPPINGS.get(eval_name, [])
                if metrics_mapped and len(metrics_mapped) > 0:
                    metrics.extend(metrics_mapped)
            else:
                metrics.append(criteria_name)
        else:
            criteria_type = "unknown"
            metrics.append(criteria_name)
        testing_criteria_name_types_metrics[criteria_name] = {"type": criteria_type, "metrics": metrics}

    created_time = int(time.time())
    converted_rows = []

    for row_idx, row in enumerate(results.get("rows", [])):
        # Group outputs by test criteria name
        criteria_groups = {criteria: {} for criteria in testing_criteria_name_types_metrics.keys()}
        input_groups = {}
        top_sample = {}
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
                input_key = key.replace("inputs.", "")
                if input_key not in input_groups:
                    input_groups[input_key] = value

        # Convert each criteria group to RunOutputItem result
        run_output_results = []
        for criteria_name, metrics in criteria_groups.items():
            # Extract metrics for this criteria
            expected_metrics = testing_criteria_name_types_metrics.get(criteria_name, {}).get("metrics", [])
            criteria_type = testing_criteria_name_types_metrics.get(criteria_name, {}).get("type", "unknown")
            result_per_metric = {}
            # Find score - look for various score patterns
            for metric_key, metric_value in metrics.items():
                if metric_key.endswith("_score") or metric_key == "score":
                    metric = _get_metric_from_criteria(criteria_name, metric_key, expected_metrics)
                    if metric not in result_per_metric:
                        result_per_metric[metric] = {"score": metric_value}
                    else:
                        result_per_metric[metric]["score"] = metric_value
                    _append_indirect_attachments_to_results(result_per_metric, "score", metric, metric_value)
                if metric_key == "passed":
                    metric = _get_metric_from_criteria(criteria_name, metric_key, expected_metrics)
                    if metric not in result_per_metric:
                        result_per_metric[metric] = {"passed": metric_value}
                    else:
                        result_per_metric[metric]["passed"] = metric_value
                    _append_indirect_attachments_to_results(result_per_metric, "passed", metric, metric_value)
                elif metric_key.endswith("_result") or metric_key == "result" or metric_key.endswith("_label"):
                    metric = _get_metric_from_criteria(criteria_name, metric_key, expected_metrics)
                    label = metric_value
                    passed = (
                        True if (str(metric_value).lower() == "pass" or str(metric_value).lower() == "true") else False
                    )
                    if metric not in result_per_metric:
                        if criteria_type == "azure_ai_evaluator":
                            result_per_metric[metric] = {"label": label, "passed": passed}
                        else:
                            result_per_metric[metric] = {"label": label}
                    else:
                        result_per_metric[metric]["label"] = metric_value
                        if criteria_type == "azure_ai_evaluator":
                            result_per_metric[metric]["passed"] = passed
                    _append_indirect_attachments_to_results(result_per_metric, "label", metric, label)
                    if criteria_type == "azure_ai_evaluator":
                        _append_indirect_attachments_to_results(result_per_metric, "passed", metric, passed)
                elif (
                    metric_key.endswith("_reason") and not metric_key.endswith("_finish_reason")
                ) or metric_key == "reason":
                    metric = _get_metric_from_criteria(criteria_name, metric_key, expected_metrics)
                    if metric not in result_per_metric:
                        result_per_metric[metric] = {"reason": metric_value}
                    else:
                        result_per_metric[metric]["reason"] = metric_value
                    _append_indirect_attachments_to_results(result_per_metric, "reason", metric, metric_value)
                elif metric_key.endswith("_threshold") or metric_key == "threshold":
                    metric = _get_metric_from_criteria(criteria_name, metric_key, expected_metrics)
                    if metric not in result_per_metric:
                        result_per_metric[metric] = {"threshold": metric_value}
                    else:
                        result_per_metric[metric]["threshold"] = metric_value
                    _append_indirect_attachments_to_results(result_per_metric, "threshold", metric, metric_value)
                elif metric_key == "sample":
                    metric = _get_metric_from_criteria(criteria_name, metric_key, expected_metrics)
                    if metric not in result_per_metric:
                        result_per_metric[metric] = {"sample": metric_value}
                    else:
                        result_per_metric[metric]["sample"] = metric_value
                    _append_indirect_attachments_to_results(result_per_metric, "sample", metric, metric_value)
                elif metric_key.endswith("_finish_reason"):
                    metric = _get_metric_from_criteria(criteria_name, metric_key, expected_metrics)
                    if metric not in result_per_metric:
                        result_per_metric[metric] = {"sample": {"finish_reason": metric_value}}
                    elif metric in result_per_metric and "sample" not in result_per_metric[metric]:
                        result_per_metric[metric]["sample"] = {"finish_reason": metric_value}
                    elif (
                        metric in result_per_metric
                        and "sample" in result_per_metric[metric]
                        and "finish_reason" not in result_per_metric[metric]["sample"]
                    ):
                        result_per_metric[metric]["sample"]["finish_reason"] = metric_value
                    _append_indirect_attachments_to_results(
                        result_per_metric, "sample", metric, metric_value, "finish_reason"
                    )
                elif metric_key.endswith("_model"):
                    metric = _get_metric_from_criteria(criteria_name, metric_key, expected_metrics)
                    if metric not in result_per_metric:
                        result_per_metric[metric] = {"sample": {"model": metric_value}}
                    elif metric in result_per_metric and "sample" not in result_per_metric[metric]:
                        result_per_metric[metric]["sample"] = {"model": metric_value}
                    elif (
                        metric in result_per_metric
                        and "sample" in result_per_metric[metric]
                        and "model" not in result_per_metric[metric]["sample"]
                    ):
                        result_per_metric[metric]["sample"]["model"] = metric_value
                    _append_indirect_attachments_to_results(result_per_metric, "sample", metric, metric_value, "model")
                elif metric_key.endswith("_sample_input"):
                    metric = _get_metric_from_criteria(criteria_name, metric_key, expected_metrics)
                    input_metric_val_json: Optional[List[Dict[str, Any]]] = []
                    try:
                        input_metric_val_json = json.loads(metric_value)
                    except Exception as e:
                        logger.warning(f"Failed to parse _sample_input value as JSON: {e}")
                    if metric not in result_per_metric:
                        result_per_metric[metric] = {"sample": {"input": input_metric_val_json}}
                    elif metric in result_per_metric and "sample" not in result_per_metric[metric]:
                        result_per_metric[metric]["sample"] = {"input": input_metric_val_json}
                    elif (
                        metric in result_per_metric
                        and "sample" in result_per_metric[metric]
                        and "input" not in result_per_metric[metric]["sample"]
                    ):
                        result_per_metric[metric]["sample"]["input"] = input_metric_val_json
                    _append_indirect_attachments_to_results(
                        result_per_metric, "sample", metric, input_metric_val_json, "input"
                    )
                elif metric_key.endswith("_sample_output"):
                    metric = _get_metric_from_criteria(criteria_name, metric_key, expected_metrics)
                    output_metric_val_json: Optional[List[Dict[str, Any]]] = []
                    try:
                        output_metric_val_json = json.loads(metric_value)
                    except Exception as e:
                        logger.warning(f"Failed to parse _sample_output value as JSON: {e}")
                    if metric not in result_per_metric:
                        result_per_metric[metric] = {"sample": {"output": output_metric_val_json}}
                    elif metric in result_per_metric and "sample" not in result_per_metric[metric]:
                        result_per_metric[metric]["sample"] = {"output": output_metric_val_json}
                    elif (
                        metric in result_per_metric
                        and "sample" in result_per_metric[metric]
                        and "output" not in result_per_metric[metric]["sample"]
                    ):
                        result_per_metric[metric]["sample"]["output"] = output_metric_val_json
                    _append_indirect_attachments_to_results(
                        result_per_metric, "sample", metric, output_metric_val_json, "output"
                    )
                elif metric_key.endswith("_total_tokens"):
                    metric = _get_metric_from_criteria(criteria_name, metric_key, expected_metrics)
                    metric_value = None if _is_none_or_nan(metric_value) else metric_value
                    if metric not in result_per_metric:
                        result_per_metric[metric] = {"sample": {"usage": {"total_tokens": metric_value}}}
                    elif metric in result_per_metric and "sample" not in result_per_metric[metric]:
                        result_per_metric[metric]["sample"] = {"usage": {"total_tokens": metric_value}}
                    elif (
                        metric in result_per_metric
                        and "sample" in result_per_metric[metric]
                        and "usage" not in result_per_metric[metric]["sample"]
                    ):
                        result_per_metric[metric]["sample"]["usage"] = {"total_tokens": metric_value}
                    else:
                        result_per_metric[metric]["sample"]["usage"]["total_tokens"] = metric_value
                    _append_indirect_attachments_to_results(
                        result_per_metric, "sample", metric, metric_value, "usage", "total_tokens"
                    )
                elif metric_key.endswith("_prompt_tokens"):
                    metric = _get_metric_from_criteria(criteria_name, metric_key, expected_metrics)
                    metric_value = None if _is_none_or_nan(metric_value) else metric_value
                    if metric not in result_per_metric:
                        result_per_metric[metric] = {"sample": {"usage": {"prompt_tokens": metric_value}}}
                    elif metric in result_per_metric and "sample" not in result_per_metric[metric]:
                        result_per_metric[metric]["sample"] = {"usage": {"prompt_tokens": metric_value}}
                    elif (
                        metric in result_per_metric
                        and "sample" in result_per_metric[metric]
                        and "usage" not in result_per_metric[metric]["sample"]
                    ):
                        result_per_metric[metric]["sample"]["usage"] = {"prompt_tokens": metric_value}
                    else:
                        result_per_metric[metric]["sample"]["usage"]["prompt_tokens"] = metric_value
                    _append_indirect_attachments_to_results(
                        result_per_metric, "sample", metric, metric_value, "usage", "prompt_tokens"
                    )
                elif metric_key.endswith("_completion_tokens"):
                    metric = _get_metric_from_criteria(criteria_name, metric_key, expected_metrics)
                    metric_value = None if _is_none_or_nan(metric_value) else metric_value
                    if metric not in result_per_metric:
                        result_per_metric[metric] = {"sample": {"usage": {"completion_tokens": metric_value}}}
                    elif metric in result_per_metric and "sample" not in result_per_metric[metric]:
                        result_per_metric[metric]["sample"] = {"usage": {"completion_tokens": metric_value}}
                    elif (
                        metric in result_per_metric
                        and "sample" in result_per_metric[metric]
                        and "usage" not in result_per_metric[metric]["sample"]
                    ):
                        result_per_metric[metric]["sample"]["usage"] = {"completion_tokens": metric_value}
                    else:
                        result_per_metric[metric]["sample"]["usage"]["completion_tokens"] = metric_value
                    _append_indirect_attachments_to_results(
                        result_per_metric, "sample", metric, metric_value, "usage", "completion_tokens"
                    )
                elif not any(
                    metric_key.endswith(suffix)
                    for suffix in [
                        "_result",
                        "_reason",
                        "_threshold",
                        "_label",
                        "_score",
                        "_model",
                        "_finish_reason",
                        "_sample_input",
                        "_sample_output",
                        "_total_tokens",
                        "_prompt_tokens",
                        "_completion_tokens",
                    ]
                ):
                    metric = _get_metric_from_criteria(criteria_name, metric_key, expected_metrics)
                    # If no score found yet and this doesn't match other patterns, use as score
                    if metric_key == metric and metric not in result_per_metric:
                        result_per_metric[metric] = {"score": metric_value}
                    elif metric_key == metric and result_per_metric[metric].get("score", None) is None:
                        result_per_metric[metric]["score"] = metric_value

            for metric, metric_values in result_per_metric.items():
                score = metric_values.get("score", None)
                label = metric_values.get("label", None)
                reason = metric_values.get("reason", None)
                threshold = metric_values.get("threshold", None)
                passed = metric_values.get("passed", None)
                sample = metric_values.get("sample", None)

                # Create result object for this criteria
                result_obj = {
                    "type": testing_criteria_name_types_metrics.get(criteria_name, {}).get(
                        "type", "azure_ai_evaluator"
                    ),
                    "name": criteria_name,  # Use criteria name as name
                    "metric": metric if metric is not None else criteria_name,  # Use criteria name as metric
                }
                # Add optional fields
                if (
                    metric in _EvaluatorMetricMapping.EVALUATOR_NAME_METRICS_MAPPINGS["indirect_attack"]
                    or metric in _EvaluatorMetricMapping.EVALUATOR_NAME_METRICS_MAPPINGS["code_vulnerability"]
                    or metric in _EvaluatorMetricMapping.EVALUATOR_NAME_METRICS_MAPPINGS["protected_material"]
                ):
                    copy_label = label
                    if copy_label is not None and isinstance(copy_label, bool) and copy_label == True:
                        label = "fail"
                        score = 0.0
                        passed = False
                    else:
                        label = "pass"
                        score = 1.0
                        passed = True
                result_obj["score"] = (
                    score if not (score is None or (isinstance(score, float) and math.isnan(score))) else None
                )
                result_obj["label"] = label
                result_obj["reason"] = reason
                result_obj["threshold"] = threshold
                result_obj["passed"] = passed

                if sample is not None:
                    result_obj["sample"] = sample
                    top_sample = sample  # Save top sample for the row
                run_output_results.append(result_obj)

            if (
                eval_run_summary
                and criteria_name in eval_run_summary
                and isinstance(eval_run_summary[criteria_name], dict)
                and "error_code" in eval_run_summary[criteria_name]
            ) and eval_run_summary[criteria_name].get("error_code", None) is not None:
                error_info = (
                    {
                        "code": eval_run_summary[criteria_name].get("error_code", None),
                        "message": eval_run_summary[criteria_name].get("error_message", None),
                    }
                    if eval_run_summary[criteria_name].get("error_code", None) is not None
                    else None
                )
                sample = {"error": error_info} if error_info is not None else None
                # Create result object for this criteria
                metrics = testing_criteria_name_types_metrics.get(criteria_name, {}).get("metrics", [])
                for metric in metrics:
                    should_add_error_summary = True
                    for result in run_output_results:
                        if result.get("name", None) == criteria_name and result.get("metric", None) == metric:
                            rs_score = result.get("score", None)
                            rs_threshold = result.get("threshold", None)
                            rs_label = result.get("label", None)
                            rs_reason = result.get("reason", None)
                            if (
                                _is_none_or_nan(rs_score)
                                and _is_none_or_nan(rs_threshold)
                                and _is_none_or_nan(rs_label)
                                and _is_none_or_nan(rs_reason)
                            ):
                                run_output_results.remove(result)
                            else:
                                should_add_error_summary = False
                            break  # Skip if already have result for this criteria and metric
                    if should_add_error_summary:
                        result_obj = {
                            "type": testing_criteria_name_types_metrics.get(criteria_name, {}).get(
                                "type", "azure_ai_evaluator"
                            ),
                            "name": criteria_name,  # Use criteria name as name
                            "metric": metric if metric is not None else criteria_name,  # Use criteria name as metric
                            "score": None,
                            "label": None,
                            "reason": None,
                            "threshold": None,
                            "passed": None,
                            "sample": sample,
                        }
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
            "status": "completed" if len(run_output_results) > 0 else "error",
        }

        run_output_item["sample"] = top_sample

        converted_rows.append(run_output_item)

    # Create converted results maintaining the same structure
    results["_evaluation_results_list"] = converted_rows
    logger.info(
        f"Converted {len(converted_rows)} rows to AOAI evaluation format, eval_id: {eval_id}, eval_run_id: {eval_run_id}"
    )
    # Calculate summary statistics
    evaluation_summary = _calculate_aoai_evaluation_summary(converted_rows, logger, criteria_name_types_from_meta)
    results["_evaluation_summary"] = evaluation_summary
    logger.info(
        f"Summary statistics calculated for {len(converted_rows)} rows, eval_id: {eval_id}, eval_run_id: {eval_run_id}"
    )


def _is_none_or_nan(value: Any) -> bool:
    """
    Check if a value is None or NaN.

    :param value: The value to check
    :type value: Any
    :return: True if the value is None or NaN, False otherwise
    :rtype: bool
    """
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    if isinstance(value, str) and value.lower() in ["nan", "null", "none", ""]:
        return True
    return False


def _append_indirect_attachments_to_results(
    current_result_dict: Dict[str, Any],
    result_name: str,
    metric: str,
    metric_value: Any,
    nested_result_name: Optional[str] = None,
    secondnested_result_name: Optional[str] = None,
) -> None:
    """
    Append indirect attachments to the current result dictionary.

    :param current_result_dict: The current result dictionary to update
    :type current_result_dict: Dict[str, Any]
    :param result_name: The result name
    :type result_name: str
    :param metric: The metric name
    :type metric: str
    :param metric_value: The value of the metric
    :type metric_value: Any
    """
    if metric == "xpia" and result_name:
        for metric_extended in ["xpia_manipulated_content", "xpia_intrusion", "xpia_information_gathering"]:
            if nested_result_name is None:
                if metric_extended not in current_result_dict:
                    current_result_dict[metric_extended] = {result_name: metric_value}
                else:
                    current_result_dict[metric_extended][result_name] = metric_value
            elif nested_result_name is not None and secondnested_result_name is None:
                if metric_extended not in current_result_dict:
                    current_result_dict[metric_extended] = {result_name: {nested_result_name: metric_value}}
                elif metric_extended in current_result_dict and result_name not in current_result_dict[metric_extended]:
                    current_result_dict[metric_extended][result_name] = {nested_result_name: metric_value}
                elif (
                    metric_extended in current_result_dict
                    and result_name in current_result_dict[metric_extended]
                    and nested_result_name not in current_result_dict[metric_extended][result_name]
                ):
                    current_result_dict[metric_extended][result_name][nested_result_name] = metric_value
            elif nested_result_name is not None and secondnested_result_name is not None:
                if metric_extended not in current_result_dict:
                    current_result_dict[metric_extended] = {
                        result_name: {nested_result_name: {secondnested_result_name: metric_value}}
                    }
                elif metric_extended in current_result_dict and result_name not in current_result_dict[metric_extended]:
                    current_result_dict[metric_extended][result_name] = {
                        nested_result_name: {secondnested_result_name: metric_value}
                    }
                elif (
                    metric_extended in current_result_dict
                    and result_name in current_result_dict[metric_extended]
                    and nested_result_name not in current_result_dict[metric_extended][result_name]
                ):
                    current_result_dict[metric_extended][result_name][nested_result_name] = {
                        secondnested_result_name: metric_value
                    }
                else:
                    (
                        current_result_dict[metric_extended][result_name][nested_result_name][secondnested_result_name]
                    ) = metric_value


def _get_metric_from_criteria(testing_criteria_name: str, metric_key: str, metric_list: List[str]) -> str:
    """
    Get the metric name from the testing criteria and metric key.

    :param testing_criteria_name: The name of the testing criteria
    :type testing_criteria_name: str
    :param metric_key: The metric key to look for
    :type metric_key: str
    :param metric_list: List of expected metrics for the testing criteria
    :type metric_list: List[str]
    :return: The metric name if found, otherwise the testing criteria name
    :rtype: str
    """
    metric = None

    if metric_key == "xpia_manipulated_content":
        metric = "xpia_manipulated_content"
        return metric
    elif metric_key == "xpia_intrusion":
        metric = "xpia_intrusion"
        return metric
    elif metric_key == "xpia_information_gathering":
        metric = "xpia_information_gathering"
        return metric
    for expected_metric in metric_list:
        if metric_key.startswith(expected_metric):
            metric = expected_metric
            break
    if metric is None:
        metric = testing_criteria_name
    return metric


def _is_primary_metric(metric_name: str, evaluator_name: str) -> bool:
    """
    Check if the given metric name is a primary metric.

    :param metric_name: The name of the metric
    :type metric_name: str
    :param evaluator_name: The name of the evaluator
    :type evaluator_name: str
    :return: True if the metric is a primary metric, False otherwise
    :rtype: bool
    """
    if (
        not _is_none_or_nan(metric_name)
        and not _is_none_or_nan(evaluator_name)
        and evaluator_name in _EvaluatorMetricMapping.EVALUATOR_NAME_METRICS_MAPPINGS
        and isinstance(_EvaluatorMetricMapping.EVALUATOR_NAME_METRICS_MAPPINGS[evaluator_name], list)
        and len(_EvaluatorMetricMapping.EVALUATOR_NAME_METRICS_MAPPINGS[evaluator_name]) > 1
        and metric_name in _EvaluatorMetricMapping.EVALUATOR_NAME_METRICS_MAPPINGS[evaluator_name]
        and metric_name.lower() != _EvaluatorMetricMapping.EVALUATOR_NAME_METRICS_MAPPINGS[evaluator_name][0].lower()
    ):
        return False
    else:
        return True


def _calculate_aoai_evaluation_summary(
    aoai_results: list, logger: logging.Logger, criteria_name_types_from_meta: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate summary statistics for AOAI evaluation results.

    :param aoai_results: List of AOAI result objects (run_output_items)
    :type aoai_results: list
    :return: Summary statistics dictionary
    :rtype: Dict[str, Any]
    """
    # Calculate result counts based on aoaiResults
    result_counts = {"total": 0, "errored": 0, "failed": 0, "passed": 0}

    # Count results by status and calculate per model usage
    model_usage_stats = {}  # Dictionary to aggregate usage by model
    result_counts_stats = {}  # Dictionary to aggregate usage by model

    for aoai_result in aoai_results:
        logger.info(
            f"Processing aoai_result with id: {getattr(aoai_result, 'id', 'unknown')}, row keys: {aoai_result.keys() if hasattr(aoai_result, 'keys') else 'N/A'}"
        )
        result_counts["total"] += 1
        passed_count = 0
        failed_count = 0
        error_count = 0
        if isinstance(aoai_result, dict) and "results" in aoai_result:
            logger.info(
                f"Processing aoai_result with id: {getattr(aoai_result, 'id', 'unknown')}, results count: {len(aoai_result['results'])}"
            )
            for result_item in aoai_result["results"]:
                if isinstance(result_item, dict):
                    testing_criteria = result_item.get("name", "")
                    is_primary_metric = True
                    if (
                        criteria_name_types_from_meta is not None
                        and isinstance(criteria_name_types_from_meta, dict)
                        and testing_criteria in criteria_name_types_from_meta
                    ):
                        evaluator_name = criteria_name_types_from_meta[testing_criteria].get("evaluator_name", None)
                        criteria_type = criteria_name_types_from_meta[testing_criteria].get("type", None)
                        if criteria_type == "azure_ai_evaluator" and evaluator_name.startswith("builtin."):
                            evaluator_name = evaluator_name.replace("builtin.", "")
                        is_primary_metric = _is_primary_metric(result_item.get("metric", ""), evaluator_name)
                    if not is_primary_metric:
                        logger.info(
                            f"Skip counts for non-primary metric for testing_criteria: {testing_criteria}, metric: {result_item.get('metric', '')}"
                        )
                        continue
                    # Check if the result has a 'passed' field
                    if "passed" in result_item and result_item["passed"] is not None:
                        if testing_criteria not in result_counts_stats:
                            result_counts_stats[testing_criteria] = {
                                "testing_criteria": testing_criteria,
                                "failed": 0,
                                "passed": 0,
                            }
                        if result_item["passed"] is True:
                            passed_count += 1
                            result_counts_stats[testing_criteria]["passed"] += 1

                        elif result_item["passed"] is False:
                            failed_count += 1
                            result_counts_stats[testing_criteria]["failed"] += 1
                    # Check if the result indicates an error status
                    elif ("status" in result_item and result_item["status"] in ["error", "errored"]) or (
                        "sample" in result_item
                        and isinstance(result_item["sample"], dict)
                        and result_item["sample"].get("error", None) is not None
                    ):
                        error_count += 1
        elif hasattr(aoai_result, "status") and aoai_result.status == "error":
            error_count += 1
        elif isinstance(aoai_result, dict) and aoai_result.get("status") == "error":
            error_count += 1

        # Update overall result counts, error counts will not be considered for passed/failed
        if error_count > 0:
            result_counts["errored"] += 1

        if failed_count > 0:
            result_counts["failed"] += 1
        elif (
            failed_count == 0 and passed_count > 0 and passed_count == len(aoai_result.get("results", [])) - error_count
        ):
            result_counts["passed"] += 1

        # Extract usage statistics from aoai_result.sample
        sample_data_list = []
        dup_usage_list = _EvaluatorMetricMapping.EVALUATOR_NAME_METRICS_MAPPINGS["indirect_attack"].copy()
        dup_usage_list.remove("xpia")
        if isinstance(aoai_result, dict) and aoai_result["results"] and isinstance(aoai_result["results"], list):
            for result_item in aoai_result["results"]:
                if (
                    isinstance(result_item, dict)
                    and "sample" in result_item
                    and result_item["sample"]
                    and result_item["metric"] not in dup_usage_list
                ):
                    sample_data_list.append(result_item["sample"])

        for sample_data in sample_data_list:
            if sample_data and isinstance(sample_data, dict) and "usage" in sample_data:
                usage_data = sample_data["usage"]
                model_name = sample_data.get("model", "unknown") if usage_data.get("model", "unknown") else "unknown"
                if _is_none_or_nan(model_name):
                    continue
                if model_name not in model_usage_stats:
                    model_usage_stats[model_name] = {
                        "invocation_count": 0,
                        "total_tokens": 0,
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "cached_tokens": 0,
                    }
                # Aggregate usage statistics
                model_stats = model_usage_stats[model_name]
                model_stats["invocation_count"] += 1
                if isinstance(usage_data, dict):
                    cur_total_tokens = usage_data.get("total_tokens", 0)
                    if _is_none_or_nan(cur_total_tokens):
                        cur_total_tokens = 0
                    cur_prompt_tokens = usage_data.get("prompt_tokens", 0)
                    if _is_none_or_nan(cur_prompt_tokens):
                        cur_prompt_tokens = 0
                    cur_completion_tokens = usage_data.get("completion_tokens", 0)
                    if _is_none_or_nan(cur_completion_tokens):
                        cur_completion_tokens = 0
                    cur_cached_tokens = usage_data.get("cached_tokens", 0)
                    if _is_none_or_nan(cur_cached_tokens):
                        cur_cached_tokens = 0
                    logger.info(
                        f"Model: {model_name}, cur_total_tokens: {cur_total_tokens}, {_is_none_or_nan(cur_total_tokens)}, cur_prompt_tokens: {cur_prompt_tokens}, cur_completion_tokens: {cur_completion_tokens}, cur_cached_tokens: {cur_cached_tokens}"
                    )
                    model_stats["total_tokens"] += cur_total_tokens
                    model_stats["prompt_tokens"] += cur_prompt_tokens
                    model_stats["completion_tokens"] += cur_completion_tokens
                    model_stats["cached_tokens"] += cur_cached_tokens

    # Convert model usage stats to list format matching EvaluationRunPerModelUsage
    per_model_usage = []
    for model_name, stats in model_usage_stats.items():
        per_model_usage.append(
            {
                "model_name": model_name,
                "invocation_count": stats["invocation_count"],
                "total_tokens": stats["total_tokens"],
                "prompt_tokens": stats["prompt_tokens"],
                "completion_tokens": stats["completion_tokens"],
                "cached_tokens": stats["cached_tokens"],
            }
        )
    result_counts_stats_val = []
    logger.info(f"\r\n Result counts stats: {result_counts_stats}")
    for criteria_name, stats_val in result_counts_stats.items():
        if isinstance(stats_val, dict):
            logger.info(f"\r\n  Criteria: {criteria_name}, stats: {stats_val}")
            cur_passed = stats_val.get("passed", 0)
            if _is_none_or_nan(cur_passed):
                cur_passed = 0
            cur_failed_count = stats_val.get("failed", 0)
            if _is_none_or_nan(cur_failed_count):
                cur_failed_count = 0
            result_counts_stats_val.append(
                {
                    "testing_criteria": criteria_name if not _is_none_or_nan(criteria_name) else "unknown",
                    "passed": cur_passed,
                    "failed": cur_failed_count,
                }
            )
    return {
        "result_counts": result_counts,
        "per_model_usage": per_model_usage,
        "per_testing_criteria_results": result_counts_stats_val,
    }
