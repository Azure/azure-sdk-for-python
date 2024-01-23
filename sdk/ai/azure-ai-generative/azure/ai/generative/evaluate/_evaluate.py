# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import copy
import json
import os
import shutil
import tempfile
import time
import logging
from json import JSONDecodeError
from pathlib import Path
from typing import Callable, Optional, Dict, List, Mapping

import mlflow
import numpy as np
import pandas as pd
from azure.core.tracing.decorator import distributed_trace
from azure.ai.generative._telemetry import ActivityType, monitor_with_activity, monitor_with_telemetry_mixin, ActivityLogger

from mlflow.entities import Metric
from mlflow.exceptions import MlflowException
from mlflow.protos.databricks_pb2 import ErrorCode, INVALID_PARAMETER_VALUE

from azure.ai.generative.evaluate._metric_handler import MetricHandler
from azure.ai.generative.evaluate._metrics_handler._code_metric_handler import CodeMetricHandler
from azure.ai.generative.evaluate._utils import _is_flow, load_jsonl, _get_artifact_dir_path, _copy_artifact
from azure.ai.generative.evaluate._mlflow_log_collector import RedirectUserOutputStreams
from azure.ai.generative.evaluate._constants import SUPPORTED_TO_METRICS_TASK_TYPE_MAPPING, SUPPORTED_TASK_TYPE, CHAT, \
    TYPE_TO_KWARGS_MAPPING, SUPPORTED_TASK_TYPE_TO_METRICS_MAPPING
from azure.ai.generative.evaluate._evaluation_result import EvaluationResult
from ._metrics_handler._prompt_metric_handler import PromptMetricHandler

from ._utils import _write_properties_to_run_history
from .metrics._custom_metric import CodeMetric, PromptMetric, Metric as GenAIMetric

LOGGER = logging.getLogger(__name__)

activity_logger = ActivityLogger(__name__)
activity_logger.update_info()
package_logger, module_logger = activity_logger.package_logger, activity_logger.module_logger


def _get_handler_class(
        asset,
):
    if _is_flow(asset):
        from azure.ai.generative.evaluate._local_flow_handler import LocalFlowHandler
        handler = LocalFlowHandler
    else:
        from azure.ai.generative.evaluate._local_code_handler import LocalCodeHandler
        handler = LocalCodeHandler

    return handler


def _get_metric_handler_class(
        asset,
):
    if _is_flow(asset):
        from azure.ai.generative.evaluate._local_flow_handler import LocalFlowHandler
        handler = LocalFlowHandler
    else:
        from azure.ai.generative.evaluate._local_code_handler import LocalCodeHandler
        handler = LocalCodeHandler

    return handler


def _validate_data(data, prediction_data, truth_data):
    errors = []
    prediction_data_column = ""
    truth_data_column = ""

    if isinstance(prediction_data, str):
        prediction_data_column = data[0].get(prediction_data, None)

    if isinstance(truth_data, str):
        truth_data_column = data[0].get(truth_data, None)

    if prediction_data_column is None:
        errors.append("prediction_data column not found in data")

    if truth_data_column is None:
        errors.append("truth_data column not found in data")

    if len(errors) > 1:
        raise Exception(f'Invalid data {" ,".join(errors)}')


def _log_metrics(run_id, metrics):
    """
    Helper method to log metrics into specified run.
    """
    client = mlflow.tracking.MlflowClient()
    timestamp = int(time.time() * 1000)
    client.log_batch(
        run_id,
        metrics=[
            Metric(key=key, value=value, timestamp=timestamp, step=0)
            for key, value in metrics.items()
        ],
    )


def _validate_metrics(metrics, task_type):
    genai_metrics = []
    builtin_metrics =[]
    unknown_metrics = []

    for metric in metrics:
        if isinstance(metric, GenAIMetric):
            genai_metrics.append(metric.name)
        elif isinstance(metric, str) and metric in SUPPORTED_TASK_TYPE_TO_METRICS_MAPPING[task_type].SUPPORTED_LIST:
            builtin_metrics.append(metric)
        else:
            unknown_metrics.append(metric)

    if len(unknown_metrics) > 0:
        raise Exception("Unsupported metric found in the list")

    # if len(set(genai_metrics) & set(builtin_metrics)) > 0:
    if len(genai_metrics) != len(set(genai_metrics)) or len(builtin_metrics) != len(set(builtin_metrics))\
            or (len(set(genai_metrics) & set(builtin_metrics)) > 0):
        raise Exception("Duplicate metric name found. Metric names should be unique")


@distributed_trace
@monitor_with_activity(package_logger, "Evaluate", ActivityType.PUBLICAPI)
def evaluate(
        *,
        evaluation_name: Optional[str] = None,
        target: Optional[Callable] = None,
        data: Optional[str] = None,
        task_type: Optional[str] = None,
        metrics_list: Optional[List[str]] = None,
        model_config: Optional[Dict[str, str]] = None,
        data_mapping: Optional[Mapping] = None,
        output_path: Optional[str] = None,
        **kwargs
):
    """Evaluates target or data with built-in evaluation metrics

    :keyword evaluation_name: Display name of the evaluation.
    :paramtype evaluation_name: Optional[str]
    :keyword target: Target to be evaluated. `target` and `data` both cannot be None
    :paramtype target: Optional[Callable]
    :keyword data: Path to the data to be evaluated or passed to target if target is set.
        Only .jsonl format files are supported.  `target` and `data` both cannot be None
    :paramtype data: Optional[str]
    :keyword task_type: Task type for evaluation. This helps to pick a set of pre-defined metrics.
        Supported values are `qa` and `chat`
    :paramtype task_type: str
    :keyword metrics_list: List of metrics to calculate. A default list is picked based on task_type if not set.
    :paramtype metrics_list: Optional[List[str]]
    :keyword model_config: GPT configuration details needed for AI-assisted metrics.
    :paramtype model_config: Dict[str, str]
    :keyword data_mapping: GPT configuration details needed for AI-assisted metrics.
    :paramtype data_mapping: typing.Mapping
    :keyword output_path: The local folder path to save evaluation artifacts to if set
    :paramtype output_path: Optional[str]
    :keyword tracking_uri: Tracking uri to log evaluation results to AI Studio
    :paramtype tracking_uri: Optional[str]
    :return: A EvaluationResult object.
    :rtype: ~azure.ai.generative.evaluate.EvaluationResult

    .. admonition:: Example:

        .. literalinclude:: ../samples/ai_samples_evaluate.py
            :start-after: [START evaluate_task_type_qa]
            :end-before: [END evaluate_task_type_qa]
            :language: python
            :dedent: 8
            :caption: Evaluates target or data with built-in evaluation metrics.
    """

    results_list = []
    metrics_config = {}
    if "tracking_uri" in kwargs:
        mlflow.set_tracking_uri(kwargs.get("tracking_uri"))

    if model_config:
        metrics_config.update({"openai_params": model_config})

    if data_mapping:
        metrics_config.update(data_mapping)

    sweep_args = kwargs.pop("sweep_args", None)
    if sweep_args:
        import itertools
        keys, values = zip(*sweep_args.items())
        params_permutations_dicts = [dict(zip(keys, v)) for v in itertools.product(*values)]

        with mlflow.start_run(run_name=evaluation_name) as run:
            log_property_and_tag("_azureml.evaluation_run", "azure-ai-generative-parent")
            for index, params_permutations_dict in enumerate(params_permutations_dicts):
                evaluation_name_variant = f"{evaluation_name}_{index}" if evaluation_name else f"{run.info.run_name}_{index}"

                evaluation_results = _evaluate(
                    evaluation_name=evaluation_name_variant,
                    target=target,
                    data=data,
                    task_type=task_type,
                    model_config=model_config,
                    data_mapping=data_mapping,
                    params_dict=params_permutations_dict,
                    metrics=metrics_list,
                    output_path=output_path,
                    **kwargs
                )
            results_list.append(evaluation_results)
        return results_list
    else:
        evaluation_result = _evaluate(
            evaluation_name=evaluation_name,
            target=target,
            data=data,
            task_type=task_type,
            model_config=model_config,
            data_mapping=data_mapping,
            metrics=metrics_list,
            output_path=output_path,
            **kwargs
        )

        return evaluation_result


def _evaluate(
        evaluation_name=None,
        target=None,
        data=None,
        truth_data=None,
        prediction_data=None,
        task_type=None,
        metrics=None,
        data_mapping=None,
        model_config=None,
        output_path=None,
        **kwargs
):
    try:
        if Path(data).exists():
            test_data = load_jsonl(data)
            _data_is_file = True
    except Exception as ex:
        LOGGER.debug("test data is not a file but loaded data")
        test_data = data
        _data_is_file = False

    if "y_pred" in data_mapping:
        prediction_data = data_mapping.get("y_pred")

    if "y_test" in data_mapping:
        truth_data = data_mapping.get("y_test")

    if target is None and prediction_data is None:
        raise Exception("target and prediction data cannot be null")

    if task_type not in SUPPORTED_TASK_TYPE:
        raise Exception(f"task type {task_type} is not supported")

    metrics_config = {}
    if model_config:
        metrics_config.update({"openai_params": model_config})

    if data_mapping:
        metrics_config.update({"data_mapping": data_mapping})

    with mlflow.start_run(nested=True if mlflow.active_run() else False, run_name=evaluation_name) as run, \
            RedirectUserOutputStreams(logger=LOGGER) as _:

        log_property_and_tag(
            "_azureml.evaluation_run",
            "azure-ai-generative-parent" if run.data.tags.get("mlflow.parentRunId") is None else "azure-ai-generative"
        )
        # Log input is a preview feature behind an allowlist. Uncomment this line once the feature is broadly available.
        # log_input(data=data, data_is_file=_data_is_file)

        asset_handler_class = _get_handler_class(target)

        asset_handler = asset_handler_class(
            asset=target,
            prediction_data=prediction_data,
            ground_truth=truth_data,
            test_data=test_data,
            metrics_config=metrics_config,
            **kwargs
        )

        metrics_results = {"artifacts": {}, "metrics": {}}

        if metrics is None:
            metrics = SUPPORTED_TASK_TYPE_TO_METRICS_MAPPING[task_type].DEFAULT_LIST

        _validate_metrics(metrics, task_type)

        inbuilt_metrics = [metric for metric in metrics if not isinstance(metric, GenAIMetric)]
        custom_prompt_metrics = [metric for metric in metrics if isinstance(metric, PromptMetric)]
        code_metrics = [metric for metric in metrics if isinstance(metric, CodeMetric)]

        # TODO : Once PF is used for inbuilt metrics parallelize submission of metrics calculation of different kind

        if custom_prompt_metrics:
            for metric in custom_prompt_metrics:
                metrics_config.setdefault(metric.name, {param: param for param in metric.parameters})

            prompt_metric_handler = PromptMetricHandler(
                task_type="custom-prompt-metric",
                metrics=custom_prompt_metrics,
                prediction_data=asset_handler.prediction_data,
                truth_data=asset_handler.ground_truth,
                test_data=asset_handler.test_data,
                metrics_mapping=metrics_config,
                prediction_data_column_name=prediction_data if isinstance(prediction_data, str) else None,
                ground_truth_column_name=truth_data if isinstance(truth_data, str) else None,
                type_to_kwargs="custom-prompt-metric"
            )

            prompt_metric_results = prompt_metric_handler.calculate_metrics()

            if prompt_metric_results is not None:
                for k, v in metrics_results.items():
                    v.update(prompt_metric_results[k])

        if code_metrics:
            code_metric_handler = CodeMetricHandler(
                task_type="custom-code-metric",
                metrics=code_metrics,
                prediction_data=asset_handler.prediction_data,
                truth_data=asset_handler.ground_truth,
                test_data=asset_handler.test_data,
                metrics_mapping=metrics_config,
                prediction_data_column_name=prediction_data if isinstance(prediction_data, str) else None,
                ground_truth_column_name=truth_data if isinstance(truth_data, str) else None,
                type_to_kwargs="code-prompt-metric"
            )

            code_metric_results = code_metric_handler.calculate_metrics()

            if code_metric_results is not None:
                for k, v in metrics_results.items():
                    v.update(code_metric_results[k])

        if inbuilt_metrics:
            inbuilt_metrics_handler = MetricHandler(
                task_type=SUPPORTED_TO_METRICS_TASK_TYPE_MAPPING[task_type],
                metrics=inbuilt_metrics,
                prediction_data=asset_handler.prediction_data,
                truth_data=asset_handler.ground_truth,
                test_data=asset_handler.test_data,
                metrics_mapping=metrics_config,
                prediction_data_column_name=prediction_data if isinstance(prediction_data, str) else None,
                ground_truth_column_name=truth_data if isinstance(truth_data, str) else None,
                type_to_kwargs=TYPE_TO_KWARGS_MAPPING[task_type]
            )

            inbuilt_metrics_results = inbuilt_metrics_handler.calculate_metrics()

            if inbuilt_metrics_results is not None:
                for k, v in metrics_results.items():
                    v.update(inbuilt_metrics_results[k])

        if metrics_results.get("metrics"):
            _log_metrics(run_id=run.info.run_id, metrics=metrics_results.get("metrics"))

        with tempfile.TemporaryDirectory() as tmpdir:
            for param_name, param_value in kwargs.get("params_dict", {}).items():

                try:
                    mlflow.log_param(param_name, param_value)
                except MlflowException as ex:
                    # This is to work around the 500 bytes mlflow limit for param values.
                    # We may need to find a more restricted way to identify the param-value-too-long error.
                    # But since we control how params are logged, this is prob fine for now.

                    if ex.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE):
                        LOGGER.warning(
                            f"Parameter {param_name} value is too long to log. Truncating and logging it as an artifact.")

                        # Truncate the value to 500 bytes and log it.
                        truncated_value = param_value.encode('utf-8')[:500].decode('utf-8', 'ignore')
                        mlflow.log_param(param_name, truncated_value)

                        # Log the full value as an artifact.
                        param_path = os.path.join(tmpdir, param_name)
                        with open(param_path, "w") as f:
                            f.write(param_value)
                        mlflow.log_artifact(param_path)
                    else:
                        raise ex

            eval_artifact_df = _get_instance_table(metrics_results, task_type, asset_handler).to_json(orient="records",
                                                                                                      lines=True,
                                                                                                      force_ascii=False)
            tmp_path = os.path.join(tmpdir, "eval_results.jsonl")

            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(eval_artifact_df)

            mlflow.log_artifact(tmp_path)
            log_property_and_tag("_azureml.evaluate_artifacts",
                                 json.dumps([{"path": "eval_results.jsonl", "type": "table"}]))
            mlflow.log_param("task_type", task_type)
            if task_type == CHAT:
                log_property("_azureml.chat_history_column", data_mapping.get("y_pred"))

            if output_path:
                _copy_artifact(tmp_path, output_path)

    evaluation_result = EvaluationResult(
        metrics_summary=metrics_results.get("metrics"),
        artifacts={
            "eval_results.jsonl": f"runs:/{run.info.run_id}/eval_results.jsonl"
        },
        tracking_uri=kwargs.get("tracking_uri"),
        evaluation_id=run.info.run_id,
    )

    return evaluation_result


@distributed_trace
@monitor_with_activity(package_logger, "LogInput", ActivityType.PUBLICAPI)
def log_input(data, data_is_file):
    try:
        # Mlflow service supports only uri_folder, hence this is need to create a dir to log input data.
        # once support is extended, we can revisit this logic
        with tempfile.TemporaryDirectory() as tempdir:
            if data_is_file:
                file_name = os.path.basename(data)
                destination_file = os.path.join(tempdir, file_name)
                shutil.copy2(data, destination_file)

                mlflow.log_artifact(tempdir)
                artifact_aml_uri = _get_artifact_dir_path(os.path.join(os.path.basename(tempdir), file_name))

                mlflow.log_input(
                    mlflow.data.from_pandas(pd.read_json(destination_file, lines=True), source=artifact_aml_uri)
                )
            else:
                mlflow.log_input(
                    mlflow.data.from_pandas(pd.DataFrame.from_dict(data))
                )
    except Exception as ex:
        LOGGER.error("Error logging data as dataset, continuing without it")
        LOGGER.exception(ex, stack_info=True)


@distributed_trace
@monitor_with_activity(package_logger, "LogParamAndTag", ActivityType.PUBLICAPI)
def log_param_and_tag(key, value):
    mlflow.log_param(key, value)
    mlflow.set_tag(key, value)


@distributed_trace
@monitor_with_activity(package_logger, "LogPropertyAndTag", ActivityType.PUBLICAPI)
def log_property_and_tag(key, value, logger=LOGGER):
    _write_properties_to_run_history({key: value}, logger)
    mlflow.set_tag(key, value)


@distributed_trace
@monitor_with_activity(package_logger, "LogProperty", ActivityType.PUBLICAPI)
def log_property(key, value, logger=LOGGER):
    _write_properties_to_run_history({key: value}, logger)


def _get_chat_instance_table(metrics):
    instance_table_metrics_dict = {}
    for artifact, value in metrics.items():
        if "score_per_conversation" in value.keys():
            instance_table_metrics_dict.update({
                artifact: value["score_per_conversation"]
            })

    instance_level_metrics_table = pd.DataFrame(instance_table_metrics_dict)
    return instance_level_metrics_table


def _get_instance_table(metrics, task_type, asset_handler):
    if metrics.get("artifacts"):
        metrics.get("artifacts").pop("bertscore", None)
    if task_type == CHAT:
        instance_level_metrics_table = _get_chat_instance_table(metrics.get("artifacts"))
    else:
        instance_level_metrics_table = pd.DataFrame(metrics.get("artifacts"))

    prediction_data = asset_handler.prediction_data
    for column in asset_handler.prediction_data.columns.values:
        if column in asset_handler.test_data.columns.values:
            prediction_data.drop(column, axis=1, inplace=True)

    combined_table = pd.concat(
        [asset_handler.test_data,
         prediction_data,
         asset_handler.ground_truth,
         instance_level_metrics_table
         ],
        axis=1,
        verify_integrity=True
    )
    return combined_table
