# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azure.ai.generative.evaluate._constants import TYPE_TO_KWARGS_MAPPING
from azure.ai.generative.evaluate._utils import _has_column


def fetch_data_for_metrics_calculation(task_type, test_data, prediction_data, truth_data=None,
                                       metrics_config=None):
    metrics_data = {}
    data_columns = TYPE_TO_KWARGS_MAPPING[task_type]
    for data_column in data_columns:
        if data_column in metrics_config.keys():
            data_source = None
            if _has_column(test_data, metrics_config[data_column]):
                data_source = test_data
            elif _has_column(prediction_data, metrics_config[data_column]):
                data_source = prediction_data
            elif _has_column(truth_data, metrics_config[data_column]):
                data_source = truth_data

            if data_column is None:
                raise Exception(f"{data_column} data needed for metric calculation not found")

            metrics_data.update(
                {
                    data_column: [d.get(metrics_config[data_column]) for d in data_source]
                }
            )
            metrics_config.pop(data_column, None)

    metrics_data.update(metrics_config)

    return metrics_data
