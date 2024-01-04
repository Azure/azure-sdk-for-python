# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import copy
import logging
from concurrent.futures.thread import ThreadPoolExecutor

from numpy import NaN
from tqdm import tqdm

from azure.ai.generative.evaluate._constants import TYPE_TO_KWARGS_MAPPING
from azure.ai.generative.evaluate._constants import TASK_TYPE_TO_METRICS_MAPPING
from azure.ai.generative.evaluate.metrics.custom_metric import LLMMetric, CodeMetric

LOGGER = logging.getLogger(__name__)


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
        LOGGER.info(f"Calculating inbuilt metrics : {[metric for metric in self.metrics]}")
        from azureml.metrics import compute_metrics

        metrics_calculation_data = self._get_data_for_metrics()

        metrics = self.metrics if self.metrics is not None else TASK_TYPE_TO_METRICS_MAPPING[
            self.task_type].DEFAULT_LIST

        metrics_value = compute_metrics(
            metrics=metrics,
            task_type=self.task_type,
            use_chat_completion_api=True,
            openai_params=self.metrics_mapping["openai_params"],
            **metrics_calculation_data,
        )

        if self.task_type == "custom-prompt-metric":
            for metric_value in metrics_value:
                print(metric_value)

        return metrics_value


class CodeMetricHandler(MetricHandler):
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

        super().__init__(
            task_type=task_type,
            prediction_data=prediction_data,
            test_data=test_data,
            truth_data=truth_data,
            prediction_data_column_name=prediction_data_column_name,
            ground_truth_column_name=ground_truth_column_name,
            metrics_mapping=metrics_mapping,
            metrics=metrics,
            type_to_kwargs="test",
        )

        self._validate()

    def _validate(self):
        supported_list = [isinstance(metric, CodeMetric) for metric in self.metrics]
        if not all(supported_list):
            raise Exception(f"{self.__class__.__name__} supports only {CodeMetric.__class__.__name__} type of metrics")

    def calculate_metrics(self):
        LOGGER.info(f"Calculating code metrics : {[metric.name for metric in self.metrics]}")
        metrics_dict = {"artifacts": {}, "metrics": {}}
        metric_results_futures = {}
        with tqdm(total=len(self.metrics)) as progress_bar:
            with ThreadPoolExecutor(thread_name_prefix="CodeMetrics_Metrics") as thread_pool:
                for metric in self.metrics:
                    metric_values = []
                    metric_results_futures.update({metric.name: thread_pool.submit(
                        self._calculate_metric, metric, self.test_data.to_dict('records'),
                        self.prediction_data.to_dict('records') if self.prediction_data is not None else None
                    )}
                    )

                for metric_name, metric_result_future in metric_results_futures.items():
                    try:
                        metric_result = metric_result_future.result()
                        metrics_dict["artifacts"].update(metric_result["artifacts"])
                        if "metrics" in metric_result.keys() and metric_result["metrics"] is not None:
                            metrics_dict["metrics"].update(metric_result["metrics"])
                        progress_bar.update(1)
                    except Exception as ex:
                        # print(ex)
                        progress_bar.update(1)
                        LOGGER.info(f"Error calculating value for {metric_name}, failed with error {str(ex)} : Stack trace : {str(ex.__traceback__)}")

        return metrics_dict

    def _calculate_metric(self, metric, data, response):

        row_metric_futures = []
        row_metric_result = []
        aggregated_metrics = None

        with ThreadPoolExecutor(thread_name_prefix="CodeMetrics_Metrics_Row") as thread_pool:
            for i in range(0, len(data)):
                row_metric_futures.append(thread_pool.submit(
                    metric.calculate, data[i], response[i]
                ))

            for row_metric_future in row_metric_futures:
                try:
                    row_metric_result.append(row_metric_future.result())
                except Exception as ex:
                    LOGGER.info(f"Error calculating value for a row for metric {metric.name} , failed with error {str(ex)} : Stack trace : {str(ex.__traceback__)}")
                    row_metric_result.append(NaN)

        if metric.aggregator:
            aggregated_metrics = metric.aggregator(row_metric_result)

        return {
            "artifacts": {metric.name: row_metric_result},
            "metrics": aggregated_metrics
        }

    # def _calculate_metric(self, metric, data, response):
    #     with ThreadPoolExecutor()
