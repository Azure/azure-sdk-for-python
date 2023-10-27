# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import copy

from azure.ai.generative.evaluate._constants import TYPE_TO_KWARGS_MAPPING
from azure.ai.generative.evaluate._constants import TASK_TYPE_TO_METRICS_MAPPING


class MetricHandler(object):

    def __init__(
            self,
            task_type,
            prediction_data,
            test_data,
            truth_data=None,
            prediction_data_column_name=None,
            ground_truth_column_name=None,
            metrics_mapping=None,
            metrics=None
    ):
        self.task_type = task_type
        self.prediction_data = prediction_data
        self.truth_data = truth_data
        self.test_data = test_data
        self.metrics_mapping = metrics_mapping
        self.prediction_data_column_name = prediction_data_column_name
        self.ground_truth_column_name = ground_truth_column_name
        self._metrics_mapping_to_log = {}
        self.metrics = metrics

    def _get_data_for_metrics(self):
        metrics_mapping = copy.deepcopy(self.metrics_mapping)
        metrics_mapping_to_log = {}

        if self.prediction_data_column_name:
            metrics_mapping.update(
                {"y_pred": self.prediction_data_column_name}
            )

        if self.ground_truth_column_name:
            metrics_mapping.update(
                {"y_test": self.ground_truth_column_name}
            )

        metrics_data = {}
        data_columns = TYPE_TO_KWARGS_MAPPING[self.task_type]
        for data_column in data_columns:
            if data_column in metrics_mapping.keys():
                data_source = None
                if metrics_mapping[data_column] in self.test_data.columns.values:
                    data_source = self.test_data
                elif metrics_mapping[data_column] in self.prediction_data.columns:
                    data_source = self.prediction_data
                elif self.truth_data is not None and metrics_mapping[data_column] in self.truth_data.columns:
                    data_source = self.truth_data

                if data_column is None:
                    raise Exception(f"{data_column} data needed for metric calculation not found")

                if data_source is not None:
                    metrics_data.update(
                        {
                            data_column: data_source[metrics_mapping[data_column]].values.tolist()
                        }
                    )
                popped_value = metrics_mapping.pop(data_column, None)
                metrics_mapping_to_log[data_column] = popped_value

        metrics_data.update(metrics_mapping)

        self._metrics_mapping_to_log = metrics_mapping_to_log

        return metrics_data

    def calculate_metrics(self):
        from azureml.metrics import compute_metrics, constants

        metrics_calculation_data = self._get_data_for_metrics()

        metrics = self.metrics if self.metrics is not None else TASK_TYPE_TO_METRICS_MAPPING[self.task_type].DEFAULT_LIST

        return compute_metrics(
            metrics=metrics,
            task_type=self.task_type,
            **metrics_calculation_data,
        )
