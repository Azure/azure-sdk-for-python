# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from concurrent.futures.thread import ThreadPoolExecutor
import tqdm

from numpy import NaN

from .._metric_handler import MetricHandler
from ..metrics._custom_metric import CodeMetric

LOGGER = logging.getLogger(__name__)


class CodeMetricHandler(MetricHandler):
    def __init__(
        self,
        task_type,
        prediction_data,
        test_data,
        input_output_data,
        metrics_mapping=None,
        metrics=None,
    ):

        super().__init__(
            task_type=task_type,
            prediction_data=prediction_data,
            test_data=test_data,
            metrics_mapping=metrics_mapping,
            metrics=metrics,
            input_output_data=input_output_data,
        )

        self._validate()

    def _validate(self):
        supported_list = [isinstance(metric, CodeMetric) for metric in self.metrics]
        if not all(supported_list):
            raise Exception(f"{self.__class__.__name__} supports only {CodeMetric.__class__.__name__} type of metrics")

    def calculate_metrics(self):
        LOGGER.info("Calculating code metrics : %s", [metric.name for metric in self.metrics])
        metrics_dict = {"artifacts": {}, "metrics": {}}
        metric_results_futures = {}
        test_data_as_dict = self.test_data.to_dict("records")
        prediction_data_as_dict = self.prediction_data.to_dict("records") if self.prediction_data is not None else None
        with tqdm.tqdm(total=len(self.metrics)) as progress_bar:
            with ThreadPoolExecutor(thread_name_prefix="code_metrics") as thread_pool:
                for metric in self.metrics:
                    metric_results_futures.update(
                        {
                            metric.name: thread_pool.submit(
                                self._calculate_metric, metric, test_data_as_dict, prediction_data_as_dict
                            )
                        }
                    )

                for metric_name, metric_result_future in metric_results_futures.items():
                    try:
                        metric_result = metric_result_future.result()
                        metrics_dict["artifacts"].update(metric_result["artifacts"])
                        if "metrics" in metric_result.keys() and metric_result["metrics"] is not None:
                            metrics_dict["metrics"].update(metric_result["metrics"])
                        progress_bar.update(1)
                    except Exception as ex:  # pylint: disable=broad-except
                        progress_bar.update(1)
                        msg = (
                            f"Error calculating value for {metric_name}, "
                            f"failed with error {str(ex)} : Stack trace : {str(ex.__traceback__)}"
                        )
                        LOGGER.info(msg)

        return metrics_dict

    def _submit_method(self, method, *args, **kwargs):
        import inspect

        if inspect.iscoroutinefunction(method):
            import asyncio

            return asyncio.run(method(*args, **kwargs))
        return method(*args, **kwargs)

    def _calculate_metric(self, metric, data, response):
        row_metric_futures = []
        row_metric_results = []

        with ThreadPoolExecutor(thread_name_prefix="code_metrics_row") as thread_pool:
            for idx, value in enumerate(data):
                row_metric_futures.append(
                    thread_pool.submit(self._submit_method, metric.calculate, data={**value, **response[idx]})
                )

            for row_metric_future in row_metric_futures:
                try:
                    row_metric_results.append(row_metric_future.result())
                except Exception as ex:  # pylint: disable=broad-except
                    msg_1 = f"Error calculating value for a row for metric {metric.name}, "
                    msg_2 = f"failed with error {str(ex)} : Stack trace : {str(ex.__traceback__)}"
                    LOGGER.info(msg_1 + msg_2)
                    row_metric_results.append(NaN)

            results = {"artifacts": {}, "metrics": {}}

            if isinstance(row_metric_results[0], dict):
                for key in row_metric_results[0].keys():
                    results["artifacts"].update({key: [row[key] for row in row_metric_results]})
            else:
                results["artifacts"].update({metric.name: row_metric_results})

        return results
