# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import inspect
import json
import logging
import os
import re
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, TypedDict, TypeVar, Union

import pandas as pd
from promptflow._sdk._constants import LINE_NUMBER
from promptflow.client import PFClient
from promptflow.entities import Run

from azure.ai.evaluation._common.math import list_mean_nan_safe, apply_transform_nan_safe
from azure.ai.evaluation._common.utils import validate_azure_ai_project
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException

from .._constants import (
    CONTENT_SAFETY_DEFECT_RATE_THRESHOLD_DEFAULT,
    EvaluationMetrics,
    Prefixes,
    _InternalEvaluationMetrics,
)
from .._model_configurations import AzureAIProject, EvaluationResult, EvaluatorConfig
from .._user_agent import USER_AGENT
from ._batch_run import EvalRunContext, CodeClient, ProxyClient, TargetRunContext
from ._utils import (
    _apply_column_mapping,
    _log_metrics_and_instance_results,
    _trace_destination_from_project_scope,
    _write_output,
)

TClient = TypeVar("TClient", ProxyClient, CodeClient)
LOGGER = logging.getLogger(__name__)

# For metrics (aggregates) whose metric names intentionally differ from their
# originating column name, usually because the aggregation of the original value
# means something sufficiently different.
# Note that content safety metrics are handled seprately.
METRIC_COLUMN_NAME_REPLACEMENTS = {
    "groundedness_pro_label": "groundedness_pro_passing_rate",
}


class __EvaluatorInfo(TypedDict):
    result: pd.DataFrame
    metrics: Dict[str, Any]
    run_summary: Dict[str, Any]


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
            col_with_numeric_values = pd.to_numeric(df[col], errors="coerce")
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
                and module.__name__.startswith("azure.ai.evaluation.")
                and metric_name.endswith("_score")
                and metric_name.replace("_score", "") in content_safety_metrics
            ):
                content_safety_cols.append(col)

    content_safety_df = df[content_safety_cols]
    defect_rates = {}
    for col in content_safety_df.columns:
        defect_rate_name = col.replace("_score", "_defect_rate")
        col_with_numeric_values = pd.to_numeric(content_safety_df[col], errors="coerce")
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
        _InternalEvaluationMetrics.ECI,
        EvaluationMetrics.XPIA,
    ]
    label_cols = []
    for col in df.columns:
        metric_name = col.split(".")[1]
        if metric_name.endswith("_label") and metric_name.replace("_label", "").lower() in handled_metrics:
            label_cols.append(col)

    label_df = df[label_cols]
    defect_rates = {}
    for col in label_df.columns:
        defect_rate_name = col.replace("_label", "_defect_rate")
        col_with_boolean_values = pd.to_numeric(label_df[col], errors="coerce")
        try:
            defect_rates[defect_rate_name] = round(list_mean_nan_safe(col_with_boolean_values), 2)
        except EvaluationException:  # only exception that can be cause is all NaN values
            msg = f"All score evaluations are NaN/None for column {col}. No aggregation can be performed."
            LOGGER.warning(msg)
    return label_cols, defect_rates


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

    # For rest of metrics, we will calculate mean
    df.drop(columns=handled_columns, inplace=True)

    # NOTE: nan/None values don't count as as booleans, so boolean columns with
    # nan/None values won't have a mean produced from them.
    # This is different from label-based known evaluators, which have special handling.
    mean_value = df.mean(numeric_only=True)
    metrics = mean_value.to_dict()
    # Add defect rates back into metrics
    metrics.update(defect_rates)
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
                    evaluator._OPTIONAL_PARAMS  # pylint: disable=protected-access
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


def _validate_and_load_data(target, data, evaluators, output_path, azure_ai_project, evaluation_name):
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
        initial_data_df = pd.read_json(data, lines=True)
    except Exception as e:
        raise EvaluationException(
            message=f"Unable to load data from '{data}'. Please ensure the input is valid JSONL format. Detailed error: {e}.",
            target=ErrorTarget.EVALUATE,
            category=ErrorCategory.INVALID_VALUE,
            blame=ErrorBlame.USER_ERROR,
        ) from e

    return initial_data_df


def _apply_target_to_data(
    target: Callable,
    data: Union[str, os.PathLike],
    pf_client: PFClient,
    initial_data: pd.DataFrame,
    evaluation_name: Optional[str] = None,
    **kwargs,
) -> Tuple[pd.DataFrame, Set[str], Run]:
    """
    Apply the target function to the data set and return updated data and generated columns.

    :param target: The function to be applied to data.
    :type target: Callable
    :param data: The path to input jsonl file.
    :type data: Union[str, os.PathLike]
    :param pf_client: The promptflow client to be used.
    :type pf_client: PFClient
    :param initial_data: The data frame with the loaded data.
    :type initial_data: pd.DataFrame
    :param evaluation_name: The name of the evaluation.
    :type evaluation_name: Optional[str]
    :return: The tuple, containing data frame and the list of added columns.
    :rtype: Tuple[pandas.DataFrame, List[str]]
    """
    _run_name = kwargs.get("_run_name")
    with TargetRunContext():
        run: Run = pf_client.run(
            flow=target,
            display_name=evaluation_name,
            data=data,
            stream=True,
            name=_run_name,
        )

    target_output: pd.DataFrame = pf_client.runs.get_details(run, all_results=True)
    # Remove input and output prefix
    generated_columns = {
        col[len(Prefixes.OUTPUTS) :] for col in target_output.columns if col.startswith(Prefixes.OUTPUTS)
    }
    # Sort output by line numbers
    target_output.set_index(f"inputs.{LINE_NUMBER}", inplace=True)
    target_output.sort_index(inplace=True)
    target_output.reset_index(inplace=True, drop=False)
    # target_output contains only input columns, taken by function,
    # so we need to concatenate it to the input data frame.
    drop_columns = list(filter(lambda x: x.startswith("inputs"), target_output.columns))
    target_output.drop(drop_columns, inplace=True, axis=1)
    # Rename outputs columns to __outputs
    rename_dict = {col: col.replace(Prefixes.OUTPUTS, Prefixes.TSG_OUTPUTS) for col in target_output.columns}
    target_output.rename(columns=rename_dict, inplace=True)
    # Concatenate output to input
    target_output = pd.concat([target_output, initial_data], axis=1)

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

    unexpected_references = re.compile(r"\${(?!target\.|data\.).+?}")

    if column_mapping:
        for evaluator, mapping_config in column_mapping.items():
            if isinstance(mapping_config, dict):
                processed_config[evaluator] = {}

                for map_to_key, map_value in mapping_config.items():
                    # Check if there's any unexpected reference other than ${target.} or ${data.}
                    if unexpected_references.search(map_value):
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


# @log_evaluate_activity
def evaluate(
    *,
    data: Union[str, os.PathLike],
    evaluators: Dict[str, Callable],
    evaluation_name: Optional[str] = None,
    target: Optional[Callable] = None,
    evaluator_config: Optional[Dict[str, EvaluatorConfig]] = None,
    azure_ai_project: Optional[AzureAIProject] = None,
    output_path: Optional[Union[str, os.PathLike]] = None,
    **kwargs,
) -> EvaluationResult:
    """Evaluates target or data with built-in or custom evaluators. If both target and data are provided,
        data will be run through target function and then results will be evaluated.

    :keyword data: Path to the data to be evaluated or passed to target if target is set.
        Only .jsonl format files are supported.  `target` and `data` both cannot be None. Required.
    :paramtype data: str
    :keyword evaluators: Evaluators to be used for evaluation. It should be a dictionary with key as alias for evaluator
        and value as the evaluator function. Required.
    :paramtype evaluators: Dict[str, Callable]
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
    :keyword azure_ai_project: Logs evaluation results to AI Studio if set.
    :paramtype azure_ai_project: Optional[~azure.ai.evaluation.AzureAIProject]
    :return: Evaluation results.
    :rtype: ~azure.ai.evaluation.EvaluationResult

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_evaluate.py
            :start-after: [START evaluate_method]
            :end-before: [END evaluate_method]
            :language: python
            :dedent: 8
            :caption: Run an evaluation on local data with Coherence and Relevance evaluators.
    """
    try:
        return _evaluate(
            evaluation_name=evaluation_name,
            target=target,
            data=data,
            evaluators=evaluators,
            evaluator_config=evaluator_config,
            azure_ai_project=azure_ai_project,
            output_path=output_path,
            **kwargs,
        )
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


def _evaluate(  # pylint: disable=too-many-locals,too-many-statements
    *,
    evaluators: Dict[str, Callable],
    evaluation_name: Optional[str] = None,
    target: Optional[Callable] = None,
    data: Union[str, os.PathLike],
    evaluator_config: Optional[Dict[str, EvaluatorConfig]] = None,
    azure_ai_project: Optional[AzureAIProject] = None,
    output_path: Optional[Union[str, os.PathLike]] = None,
    **kwargs,
) -> EvaluationResult:
    input_data_df = _validate_and_load_data(target, data, evaluators, output_path, azure_ai_project, evaluation_name)

    # Process evaluator config to replace ${target.} with ${data.}
    if evaluator_config is None:
        evaluator_config = {}
    # extract column mapping dicts into dictionary mapping evaluator name to column mapping
    column_mapping = _process_column_mappings(
        {
            evaluator_name: evaluator_configuration.get("column_mapping", None)
            for evaluator_name, evaluator_configuration in evaluator_config.items()
        }
    )

    if target is not None:
        _validate_columns_for_target(input_data_df, target)

    pf_client = PFClient(user_agent=USER_AGENT)
    target_run: Optional[Run] = None

    # Create default configuration for evaluators that directly maps
    # input data names to keyword inputs of the same name in the evaluators.
    column_mapping = column_mapping or {}
    column_mapping.setdefault("default", {})

    # If target is set, apply 1-1 column mapping from target outputs to evaluator inputs
    target_generated_columns: Set[str] = set()
    if data is not None and target is not None:
        input_data_df, target_generated_columns, target_run = _apply_target_to_data(
            target, data, pf_client, input_data_df, evaluation_name, **kwargs
        )

        for evaluator_name, mapping in column_mapping.items():
            mapped_to_values = set(mapping.values())
            for col in target_generated_columns:
                # If user defined mapping differently, do not change it.
                # If it was mapped to target, we have already changed it
                # in _process_column_mappings
                run_output = f"${{run.outputs.{col}}}"
                # We will add our mapping only if
                # customer did not mapped target output.
                if col not in mapping and run_output not in mapped_to_values:
                    column_mapping[evaluator_name][col] = run_output  # pylint: disable=unnecessary-dict-index-lookup

    # After we have generated all columns, we can check if we have everything we need for evaluators.
    _validate_columns_for_evaluators(input_data_df, evaluators, target, target_generated_columns, column_mapping)

    # Apply 1-1 mapping from input data to evaluator inputs, excluding values already assigned
    # via target mapping.
    # If both the data and the output dictionary of the target function
    # have the same column, then the target function value is used.
    if input_data_df is not None:
        for col in input_data_df.columns:
            # Ignore columns added by target mapping. These are formatted as "__outputs.<column_name>"
            # Also ignore columns that are already in config, since they've been covered by target mapping.
            if not col.startswith(Prefixes.TSG_OUTPUTS) and col not in column_mapping["default"].keys():
                column_mapping["default"][col] = f"${{data.{col}}}"

    def eval_batch_run(
        batch_run_client: TClient, *, data=Union[str, os.PathLike, pd.DataFrame]
    ) -> Dict[str, __EvaluatorInfo]:
        with EvalRunContext(batch_run_client):
            runs = {
                evaluator_name: batch_run_client.run(
                    flow=evaluator,
                    run=target_run,
                    evaluator_name=evaluator_name,
                    column_mapping=column_mapping.get(evaluator_name, column_mapping.get("default", None)),
                    data=data,
                    stream=True,
                    name=kwargs.get("_run_name"),
                )
                for evaluator_name, evaluator in evaluators.items()
            }

            # get_details needs to be called within EvalRunContext scope in order to have user agent populated
            return {
                evaluator_name: {
                    "result": batch_run_client.get_details(run, all_results=True),
                    "metrics": batch_run_client.get_metrics(run),
                    "run_summary": batch_run_client.get_run_summary(run),
                }
                for evaluator_name, run in runs.items()
            }

    # Batch Run
    use_pf_client = kwargs.get("_use_pf_client", True)
    if use_pf_client:
        # Ensure the absolute path is passed to pf.run, as relative path doesn't work with
        # multiple evaluators. If the path is already absolute, abspath will return the original path.
        data = os.path.abspath(data)
        per_evaluator_results = eval_batch_run(ProxyClient(pf_client), data=data)
    else:
        data = input_data_df
        per_evaluator_results = eval_batch_run(CodeClient(), data=input_data_df)

    # Concatenate all results
    evaluators_result_df = None
    evaluators_metric = {}
    for evaluator_name, evaluator_result in per_evaluator_results.items():
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
    input_data_df = _rename_columns_conditionally(input_data_df)

    result_df = pd.concat([input_data_df, evaluators_result_df], axis=1, verify_integrity=True)
    metrics = _aggregate_metrics(evaluators_result_df, evaluators)
    metrics.update(evaluators_metric)

    # Since tracing is disabled, pass None for target_run so a dummy evaluation run will be created each time.
    target_run = None
    trace_destination = _trace_destination_from_project_scope(azure_ai_project) if azure_ai_project else None
    studio_url = None
    if trace_destination:
        studio_url = _log_metrics_and_instance_results(
            metrics, result_df, trace_destination, target_run, evaluation_name, **kwargs
        )

    result_df_dict = result_df.to_dict("records")
    result: EvaluationResult = {"rows": result_df_dict, "metrics": metrics, "studio_url": studio_url}  # type: ignore

    _print_summary(per_evaluator_results)

    if output_path:
        _write_output(output_path, result)

    return result
