# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import asyncio
import json
from json import JSONDecodeError

import numpy as np
import pandas as pd
import logging
import tqdm.asyncio
from numpy import NaN

from .._client.openai_client import AzureOpenAIClient
from .._metric_handler import MetricHandler
from ..metrics._custom_metric import PromptMetric
from ..metrics._parsers import JsonParser, NumberParser

LOGGER = logging.getLogger(__name__)

SUPPORTED_PARSERS = [JsonParser, NumberParser]


class PromptMetricHandler(MetricHandler):
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
        self._client = AzureOpenAIClient(openai_params=metrics_mapping["openai_params"])

    def _validate(self):
        supported_list = [isinstance(metric, PromptMetric) for metric in self.metrics]
        if not all(supported_list):
            raise Exception \
                (f"{self.__class__.__name__} supports only {PromptMetric.__class__.__name__} type of metrics")


    def _convert_metric_to_message(self, metric, data):
        from jinja2 import Template

        template = Template(metric.prompt)

        prompt_as_string = template.render(data)

        message = [{
            "role": "user",
            "content": prompt_as_string
        }]

        return message

    def _get_data_for_metric(self, metric):
        pd_list = []
        for param, data_column in self.metrics_mapping.get(metric.name).items():
            data_source = None
            if data_column in self.test_data.columns.values:
                data_source = self.test_data
            elif data_column in self.prediction_data.columns:
                data_source = self.prediction_data
            elif self.truth_data is not None and data_column in self.truth_data.columns:
                data_source = self.truth_data

            if data_source is None:
                raise Exception(f"{data_column} data needed for metric calculation not found")

            pd_list.append(data_source[[data_column]].rename(columns={data_column: param}))

        data_as_jsonl = pd.concat(pd_list, axis=1, verify_integrity=True) \
            .to_dict(orient="records")

        return data_as_jsonl

    def _parser_response(self, value, metric):
        result = {metric.name: NaN}
        parsed_value = None

        for parser in SUPPORTED_PARSERS:
            parsed_value = parser.parse(value)
            if parsed_value:
                result = parsed_value
                break

        if parsed_value:
            if isinstance(parsed_value, dict):
                result = {f"{metric.name}_{key}": value for key, value in parsed_value.items()}
            else:
                result = {metric.name: parsed_value}

        if parsed_value is None:
            LOGGER.debug("Result from LLM should be in json format or a number")

        return result

    async def _compute_metric_row(self, metric, data):
        message = self._convert_metric_to_message(metric, data)
        response = await self._client.bounded_chat_completion(message)
        content = self._client.get_chat_completion_content_from_response(response)
        result = self._parser_response(content if content is not None else response, metric)
        return result

    async def _compute_metric(self, metric):
        data = self._get_data_for_metric(metric)
        tasks = []
        for row_data in data:
            task = asyncio.ensure_future(
                self._compute_metric_row(metric, row_data)
            )
            tasks.append(task)

        responses = await asyncio.gather(*tasks, return_exceptions=True)
        results = {"artifacts": {}, "metrics": {}}
        for key in responses[0].keys():
            results["artifacts"].update({
                key: [row[key] for row in responses]
            })

        return results

    async def _compute_metrics(self, metrics):
        tasks = []
        metrics_dict = {"artifacts": {}, "metrics": {}}
        for metric in self.metrics:
            task = asyncio.ensure_future(
                self._compute_metric(metric)
            )
            tasks.append(task)

        # responses = await asyncio.gather(*tasks, return_exceptions=True)
        responses = await tqdm.asyncio.tqdm.gather(*tasks)
        for response in responses:
            for k, v in metrics_dict.items():
                v.update(response[k])

        return metrics_dict

    def calculate_metrics(self):
        LOGGER.info(f"Calculating prompt metric {[metric.name for metric in self.metrics]}")
        result = asyncio.run(self._compute_metrics(self.metrics), debug=True)
        return result
