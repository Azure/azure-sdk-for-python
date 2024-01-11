# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import abc
import importlib
import json
import os
import urllib.parse


class Metric(metaclass=abc.ABCMeta):

    def __init__(self, name):
        self.name = name


class CodeMetric(Metric):
    """Evaluation code metric

        :keyword name: Name of the metric.
        :paramtype name: str
        :keyword calculate: Function to compute row level metrics. It should have the following signature:

            .. code-block:: python

                def my_code_metric(
                    *,
                    data: Dict,
                    response: Union[Dict, str],
                    **kwargs,
                ):
                    '''
                        :keyword data: Row data.This method will be called for each row.
                        :paramtype data: Dict
                        :keyword response: Response from target function passed to evaluate API otherwise None.
                        :paramtype response: Dict
                        :keyword kwargs: Includes params like data_mapping for this metric passed to evaluate API.
                        :paramtype kwargs: Dict
                    '''
                ...
        :paramtype calculate: Callable
        :keyword aggregator: Function to aggregate row level metrics. It should have the following signature:
            .. code-block:: python

                def my_aggregator(
                    *,
                    values,
                    **kwargs,
                ):
                    '''
                        :keyword values: Row level metric value calculated by calculate method of the metric.
                        :paramtype values: Union[int, Dict[str, int]]
                        :keyword kwargs: Includes params like data_mapping for this metric passed to evaluate API.
                        :paramtype kwargs: Dict
                    '''
                ...
        :paramtype aggregator: Callable

    """
    def __init__(self, *, name, calculate, aggregator=None, **kwargs):
        super(CodeMetric, self).__init__(name=name)
        self.calculate = calculate
        self.aggregator = aggregator


# WIP: This implementation will change
class PromptMetric(Metric):
    def __init__(self, name, parameters, description=None, examples=None, model_config=None):
        super(PromptMetric, self).__init__(name=name)

        self.parameters = parameters
        self.examples = examples
        self.model_config = model_config
        self.description = description
        self.prompt = self._build_prompt()

    def _build_prompt(self):
        from jinja2 import Template

        with importlib.resources.open_text("azure.ai.generative.evaluate.metrics.templates", "custom_metric_base.jinja2", encoding="utf-8") as template_file:
            template = Template(template_file.read())

        prompt_as_string = template.render({
            "prompt": self.description,
            "examples": self.examples,
            "inputs": {param: f"{{{{{param}}}}}" for param in self.parameters}
        })

        return prompt_as_string

    @staticmethod
    def _from_jinja2_template(path, name):
        from jinja2 import Environment
        from jinja2 import meta

        env = Environment()

        with open(path) as template_file:
            template_content = template_file.read()
            template = env.parse(template_content, name="test")

        template_variables = meta.find_undeclared_variables(template)

        metric = PromptMetric(
            name=name,
            parameters=[param for param in template_variables]
        )

        metric.prompt = template_content

        return metric
