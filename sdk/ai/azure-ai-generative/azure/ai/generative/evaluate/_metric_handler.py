# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import copy

from azure.ai.generative.evaluate._constants import TYPE_TO_KWARGS_MAPPING
from azure.ai.generative.evaluate._constants import TASK_TYPE_TO_METRICS_MAPPING
from azure.ai.generative.evaluate.metrics.custom_metric import LLMMetric


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
            metrics=None,
            type_to_kwargs=None,
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
        self._type_to_kwargs = type_to_kwargs if type_to_kwargs is not None else TYPE_TO_KWARGS_MAPPING[self.task_type]

    def _get_data_for_metrics(self):
        metrics_mapping = copy.deepcopy(self.metrics_mapping)
        metrics_mapping_to_log = {}

        # if self.prediction_data_column_name:
        #     metrics_mapping.update(
        #         {"y_pred": self.prediction_data_column_name}
        #     )
        #
        # if self.ground_truth_column_name:
        #     metrics_mapping.update(
        #         {"y_test": self.ground_truth_column_name}
        #     )

        metrics_data = {}
        data_mapping = metrics_mapping["data_mapping"]
        data_columns = self._type_to_kwargs
        for data_column in data_columns:
            if data_column in data_mapping.keys():
                data_source = None
                if data_mapping[data_column] in self.test_data.columns.values:
                    data_source = self.test_data
                elif data_mapping[data_column] in self.prediction_data.columns:
                    data_source = self.prediction_data
                elif self.truth_data is not None and data_mapping[data_column] in self.truth_data.columns:
                    data_source = self.truth_data

                if data_column is None:
                    raise Exception(f"{data_column} data needed for metric calculation not found")

                if data_source is not None:
                    metrics_data.update(
                        {
                            data_column: data_source[data_mapping[data_column]].values.tolist()
                        }
                    )
                # popped_value = data_mapping.pop(data_column, None)
                # metrics_mapping_to_log[data_column] = popped_value

        # metrics_data.update(metrics_mapping)

        self._metrics_mapping_to_log = metrics_mapping_to_log

        return metrics_data

    def calculate_metrics(self):
        from azureml.metrics import compute_metrics, constants

        metrics_calculation_data = self._get_data_for_metrics()

        metrics = self.metrics if self.metrics is not None else TASK_TYPE_TO_METRICS_MAPPING[self.task_type].DEFAULT_LIST

        return compute_metrics(
            metrics=metrics,
            task_type=self.task_type,
            use_chat_completion_api=True,
            openai_params=self.metrics_mapping["openai_params"],
            **metrics_calculation_data,
        )
