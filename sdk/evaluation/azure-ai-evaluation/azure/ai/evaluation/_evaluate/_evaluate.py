# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import inspect
import os
import re
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type

import pandas as pd
from promptflow._sdk._constants import LINE_NUMBER
from promptflow.client import PFClient

from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from azure.ai.evaluation._common.math import list_sum

from .._constants import (
    CONTENT_SAFETY_DEFECT_RATE_THRESHOLD_DEFAULT,
    EvaluationMetrics,
    Prefixes,
    _InternalEvaluationMetrics,
)
from .._model_configurations import AzureAIProject, EvaluatorConfig
from .._user_agent import USER_AGENT
from ._batch_run_client import BatchRunContext, CodeClient, ProxyClient
from ._utils import (
    _apply_column_mapping,
    _log_metrics_and_instance_results,
    _trace_destination_from_project_scope,
    _write_output,
)


# pylint: disable=line-too-long
def _aggregate_content_safety_metrics(
    df: pd.DataFrame, evaluators: Dict[str, Type]
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
        defect_rates[defect_rate_name] = round(
            list_sum(col_with_numeric_values >= CONTENT_SAFETY_DEFECT_RATE_THRESHOLD_DEFAULT)
            / col_with_numeric_values.count(),
            2,
        )
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
        defect_rates[defect_rate_name] = round(
            list_sum(col_with_boolean_values) / col_with_boolean_values.count(),
            2,
        )
    return label_cols, defect_rates


def _aggregate_metrics(df: pd.DataFrame, evaluators: Dict[str, Type]) -> Dict[str, float]:
    """Aggregate metrics from the evaluation results.
    On top of naively calculating the mean of most metrics, this function also identifies certain columns
    that represent defect rates and renames them accordingly. Other columns in the dataframe are dropped.
    EX: protected_material_label -> protected_material_defect_rate

    :param df: The dataframe of evaluation results.
    :type df: ~pandas.DataFrame
    :param evaluators:  A dictionary mapping of strings to evaluator classes.
    :type evaluators: Dict[str, Type]
    :return: The aggregated metrics.
    :rtype: Dict[str, float]
    """
    df.rename(columns={col: col.replace("outputs.", "") for col in df.columns}, inplace=True)

    handled_columns = []
    defect_rates = {}
    # Rename certain columns as defect rates if we know that's what their aggregates represent
    # Content safety metrics
    content_safety_cols, cs_defect_rates = _aggregate_content_safety_metrics(df, evaluators)
    handled_columns.extend(content_safety_cols)
    defect_rates.update(cs_defect_rates)
    # Label-based (true/false) metrics where 'true' means 'something is wrong'
    label_cols, label_defect_rates = _aggregate_label_defect_metrics(df)
    handled_columns.extend(label_cols)
    defect_rates.update(label_defect_rates)

    # For rest of metrics, we will calculate mean
    df.drop(columns=handled_columns, inplace=True)

    mean_value = df.mean(numeric_only=True)
    metrics = mean_value.to_dict()
    # Add defect rates back into metrics
    metrics.update(defect_rates)
    return metrics


def _validate_input_data_for_evaluator(evaluator, evaluator_name, df_data, is_target_fn=False):
    required_inputs = [
        param.name
        for param in inspect.signature(evaluator).parameters.values()
        if param.default == inspect.Parameter.empty and param.name not in ["kwargs", "args", "self"]
    ]

    missing_inputs = [col for col in required_inputs if col not in df_data.columns]
    if missing_inputs and "conversation" in required_inputs:
        non_conversation_inputs = [val for val in required_inputs if val != "conversation"]
        if len(missing_inputs) == len(non_conversation_inputs) and [
            input in non_conversation_inputs for input in missing_inputs
        ]:
            missing_inputs = []
    if missing_inputs:
        if not is_target_fn:
            msg = f"Missing required inputs for evaluator {evaluator_name} : {missing_inputs}."
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                target=ErrorTarget.EVALUATE,
                category=ErrorCategory.MISSING_FIELD,
                blame=ErrorBlame.USER_ERROR,
            )
        msg = f"Missing required inputs for target : {missing_inputs}."
        raise EvaluationException(
            message=msg,
            internal_message=msg,
            target=ErrorTarget.EVALUATE,
            category=ErrorCategory.MISSING_FIELD,
            blame=ErrorBlame.USER_ERROR,
        )


def _validate_and_load_data(target, data, evaluators, output_path, azure_ai_project, evaluation_name):
    if data is None:
        msg = "data parameter must be provided for evaluation."
        raise EvaluationException(
            message=msg,
            internal_message=msg,
            target=ErrorTarget.EVALUATE,
            category=ErrorCategory.MISSING_FIELD,
            blame=ErrorBlame.USER_ERROR,
        )

    if target is not None:
        if not callable(target):
            msg = "target parameter must be a callable function."
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                target=ErrorTarget.EVALUATE,
                category=ErrorCategory.INVALID_VALUE,
                blame=ErrorBlame.USER_ERROR,
            )

    if data is not None:
        if not isinstance(data, str):
            msg = "data parameter must be a string."
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                target=ErrorTarget.EVALUATE,
                category=ErrorCategory.INVALID_VALUE,
                blame=ErrorBlame.USER_ERROR,
            )

    if evaluators is not None:
        if not isinstance(evaluators, dict):
            msg = "evaluators parameter must be a dictionary."
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                target=ErrorTarget.EVALUATE,
                category=ErrorCategory.INVALID_VALUE,
                blame=ErrorBlame.USER_ERROR,
            )

    if output_path is not None:
        if not isinstance(output_path, str):
            msg = "output_path parameter must be a string."
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                target=ErrorTarget.EVALUATE,
                category=ErrorCategory.INVALID_VALUE,
                blame=ErrorBlame.USER_ERROR,
            )

    if azure_ai_project is not None:
        if not isinstance(azure_ai_project, Dict):
            msg = "azure_ai_project parameter must be a dictionary."
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                target=ErrorTarget.EVALUATE,
                category=ErrorCategory.INVALID_VALUE,
                blame=ErrorBlame.USER_ERROR,
            )

    if evaluation_name is not None:
        if not isinstance(evaluation_name, str):
            msg = "evaluation_name parameter must be a string."
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                target=ErrorTarget.EVALUATE,
                category=ErrorCategory.INVALID_VALUE,
                blame=ErrorBlame.USER_ERROR,
            )

    try:
        initial_data_df = pd.read_json(data, lines=True)
    except Exception as e:
        raise EvaluationException(
            message=f"Failed to load data from {data}. Confirm that it is valid jsonl data. Error: {str(e)}.",
            internal_message="Failed to load data. Confirm that it is valid jsonl data.",
            target=ErrorTarget.EVALUATE,
            category=ErrorCategory.INVALID_VALUE,
            blame=ErrorBlame.USER_ERROR,
        ) from e

    return initial_data_df


def _validate_columns(
    df: pd.DataFrame,
    evaluators: Dict[str, Any],
    target: Optional[Callable],
    column_mapping: Dict[str, Dict[str, str]],
) -> None:
    """
    Check that all columns needed by evaluator or target function are present.

    :param df: The data frame to be validated.
    :type df: pd.DataFrame
    :param evaluators: The dictionary of evaluators.
    :type evaluators: Dict[str, Any]
    :param target: The callable to be applied to data set.
    :type target: Optional[Callable]
    :param column_mapping: Dictionary mapping evaluator name to evaluator column mapping
    :type column_mapping: Dict[str, Dict[str, str]]
    :raises EvaluationException: If column starts from "__outputs." while target is defined.
    """
    if target:
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
        _validate_input_data_for_evaluator(target, None, df, is_target_fn=True)
    else:
        for evaluator_name, evaluator in evaluators.items():
            # Apply column mapping
            mapping_config = column_mapping.get(evaluator_name, column_mapping.get("default", None))
            new_df = _apply_column_mapping(df, mapping_config)

            # Validate input data for evaluator
            _validate_input_data_for_evaluator(evaluator, evaluator_name, new_df)


def _apply_target_to_data(
    target: Callable,
    data: str,
    pf_client: PFClient,
    initial_data: pd.DataFrame,
    evaluation_name: Optional[str] = None,
    _run_name: Optional[str] = None,
) -> Tuple[pd.DataFrame, Set[str]]:
    """
    Apply the target function to the data set and return updated data and generated columns.

    :param target: The function to be applied to data.
    :type target: Callable
    :param data: The path to input jsonl file.
    :type data: str
    :param pf_client: The promptflow client to be used.
    :type pf_client: PFClient
    :param initial_data: The data frame with the loaded data.
    :type initial_data: pd.DataFrame
    :param evaluation_name: The name of the evaluation.
    :type evaluation_name: Optional[str]
    :param _run_name: The name of target run. Used for testing only.
    :type _run_name: Optional[str]
    :return: The tuple, containing data frame and the list of added columns.
    :rtype: Tuple[pandas.DataFrame, List[str]]
    """
    # We are manually creating the temporary directory for the flow
    # because the way tempdir remove temporary directories will
    # hang the debugger, because promptflow will keep flow directory.
    run = pf_client.run(
        flow=target,
        display_name=evaluation_name,
        data=data,
        properties={"runType": "eval_run", "isEvaluatorRun": "true"},
        stream=True,
        name=_run_name,
    )
    target_output = pf_client.runs.get_details(run, all_results=True)
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


def _process_column_mappings(column_mapping: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    """Process column_mapping to replace ${target.} with ${data.}

    :param column_mapping: The configuration for evaluators.
    :type column_mapping: Dict[str, Dict[str, str]]
    :return: The processed configuration.
    :rtype: Dict[str, Dict[str, str]]
    """

    processed_config = {}

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
    data: str,
    evaluators: Dict[str, Callable],
    evaluation_name: Optional[str] = None,
    target: Optional[Callable] = None,
    evaluator_config: Optional[Dict[str, EvaluatorConfig]] = None,
    azure_ai_project: Optional[AzureAIProject] = None,
    output_path: Optional[str] = None,
    **kwargs,
):
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
    :rtype: dict

    :Example:

    Evaluate API can be used as follows:

    .. code-block:: python

            from azure.ai.evaluation import evaluate, RelevanceEvaluator, CoherenceEvaluator


            model_config = {
                "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
                "api_key": os.environ.get("AZURE_OPENAI_KEY"),
                "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
            }

            coherence_eval = CoherenceEvaluator(model_config=model_config)
            relevance_eval = RelevanceEvaluator(model_config=model_config)

            path = "evaluate_test_data.jsonl"
            result = evaluate(
                data=path,
                evaluators={
                    "coherence": coherence_eval,
                    "relevance": relevance_eval,
                },
                evaluator_config={
                    "coherence": {
                        "column_mapping": {
                            "response": "${data.response}",
                            "query": "${data.query}",
                        },
                    },
                    "relevance": {
                        "column_mapping": {
                            "response": "${data.response}",
                            "context": "${data.context}",
                            "query": "${data.query}",
                        },
                    },
                },
            )

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
                blame=ErrorBlame.UNKNOWN,
            ) from e

        raise e


def _evaluate(  # pylint: disable=too-many-locals,too-many-statements
    *,
    evaluation_name: Optional[str] = None,
    target: Optional[Callable] = None,
    data: Optional[str] = None,
    evaluators: Optional[Dict[str, Callable]] = None,
    evaluator_config: Optional[Dict[str, EvaluatorConfig]] = None,
    azure_ai_project: Optional[AzureAIProject] = None,
    output_path: Optional[str] = None,
    **kwargs,
):
    input_data_df = _validate_and_load_data(target, data, evaluators, output_path, azure_ai_project, evaluation_name)

    # Process evaluator config to replace ${target.} with ${data.}
    if evaluator_config is None:
        evaluator_config = {}
    # extract column mapping dicts into dictionary mapping evaluator name to column mapping
    column_mapping = {
        evaluator_name: evaluator_configuration.get("column_mapping", None)
        for evaluator_name, evaluator_configuration in evaluator_config.items()
    }
    column_mapping = _process_column_mappings(column_mapping)
    _validate_columns(input_data_df, evaluators, target, column_mapping)

    # Target Run
    pf_client = PFClient(
        config=(
            {"trace.destination": _trace_destination_from_project_scope(azure_ai_project)} if azure_ai_project else None
        ),
        user_agent=USER_AGENT,
    )

    trace_destination = pf_client._config.get_trace_destination()  # pylint: disable=protected-access
    target_run = None
    target_generated_columns = set()

    # Create default configuration for evaluators that directly maps
    # input data names to keyword inputs of the same name in the evaluators.
    column_mapping = column_mapping or {}
    column_mapping.setdefault("default", {})

    # If target is set, apply 1-1 column mapping from target outputs to evaluator inputs
    if data is not None and target is not None:
        input_data_df, target_generated_columns, target_run = _apply_target_to_data(
            target, data, pf_client, input_data_df, evaluation_name, _run_name=kwargs.get("_run_name")
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

        # After we have generated all columns we can check if we have
        # everything we need for evaluators.
        _validate_columns(input_data_df, evaluators, target=None, column_mapping=column_mapping)

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
    # Batch Run
    evaluators_info = {}
    use_pf_client = kwargs.get("_use_pf_client", True)
    if use_pf_client:
        # A user reported intermittent errors when PFClient uploads evaluation runs to the cloud.
        # The root cause is still unclear, but it seems related to a conflict between the async run uploader
        # and the async batch run. As a quick mitigation, use a PFClient without a trace destination for batch runs.
        batch_run_client = ProxyClient(PFClient(user_agent=USER_AGENT))

        # Ensure the absolute path is passed to pf.run, as relative path doesn't work with
        # multiple evaluators. If the path is already absolute, abspath will return the original path.
        data = os.path.abspath(data)
    else:
        batch_run_client = CodeClient()
        data = input_data_df

    with BatchRunContext(batch_run_client):
        for evaluator_name, evaluator in evaluators.items():
            evaluators_info[evaluator_name] = {}
            evaluators_info[evaluator_name]["run"] = batch_run_client.run(
                flow=evaluator,
                run=target_run,
                evaluator_name=evaluator_name,
                column_mapping=column_mapping.get(evaluator_name, column_mapping.get("default", None)),
                data=data,
                stream=True,
                name=kwargs.get("_run_name"),
            )

        # get_details needs to be called within BatchRunContext scope in order to have user agent populated
        for evaluator_name, evaluator_info in evaluators_info.items():
            evaluator_info["result"] = batch_run_client.get_details(evaluator_info["run"], all_results=True)
            evaluator_info["metrics"] = batch_run_client.get_metrics(evaluator_info["run"])

    # Concatenate all results
    evaluators_result_df = None
    evaluators_metric = {}
    for evaluator_name, evaluator_info in evaluators_info.items():
        evaluator_result_df = evaluator_info["result"]

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

        evaluators_metric.update({f"{evaluator_name}.{k}": v for k, v in evaluator_info["metrics"].items()})

    # Rename columns, generated by target function to outputs instead of inputs.
    # If target generates columns, already present in the input data, these columns
    # will be marked as outputs already so we do not need to rename them.
    input_data_df = _rename_columns_conditionally(input_data_df)

    result_df = pd.concat([input_data_df, evaluators_result_df], axis=1, verify_integrity=True)
    metrics = _aggregate_metrics(evaluators_result_df, evaluators)
    metrics.update(evaluators_metric)
    studio_url = _log_metrics_and_instance_results(
        metrics,
        result_df,
        trace_destination,
        target_run,
        evaluation_name,
    )

    result = {"rows": result_df.to_dict("records"), "metrics": metrics, "studio_url": studio_url}

    if output_path:
        _write_output(output_path, result)

    return result
