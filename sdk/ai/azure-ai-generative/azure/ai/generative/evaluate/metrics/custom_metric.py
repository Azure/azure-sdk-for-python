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
        self._name = name


class LLMMetric(Metric):
    def __init__(self, name, parameters, description=None, examples=None, model_config=None):
        super(LLMMetric, self).__init__(name=name)

        self.parameters = parameters
        self.examples = examples
        self.model_config = model_config
        self.description = description
        self._prompt = self._build_prompt()

    def _build_prompt(self):
        from jinja2 import Template, Environment, FileSystemLoader
        from jinja2 import meta

        env = Environment()

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
        from jinja2 import Template, Environment
        from jinja2 import meta

        env = Environment()

        with open(path) as template_file:
            template_content = template_file.read()
            template = env.parse(template_content, name="test")

        template_variables = meta.find_undeclared_variables(template)

        metric = LLMMetric(
            name=name,
            parameters=[param for param in template_variables]
        )

        metric._prompt = template_content

        return metric

    def _to_aml_metric(self, openai_params):
        from azureml.metrics import AzureMLCustomPromptMetric

        openai_params.update({
            "max_tokens": 1000
        })

        custom_prompt_config = {
            "input_vars": self.parameters,
            "metric_name": self._name,
            "user_prompt_template": self._prompt,
            "openai_params": openai_params,
        }

        return AzureMLCustomPromptMetric(**custom_prompt_config)
