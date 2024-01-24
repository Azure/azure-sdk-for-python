# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import abc
import importlib
import json
import os
import urllib.parse

from azure.ai.generative.evaluate.metrics._aggregators import mean
from azure.ai.generative.evaluate.metrics._parsers import ScoreReasonParser, ScoreParser


class Metric(metaclass=abc.ABCMeta):

    def __init__(self, name):
        self.name = name


class CodeMetric(Metric):
    """Evaluation code metric

    :keyword name: Name of the metric.
    :paramtype name: str
    :keyword calculate: Function to compute row level metrics. It should have the following signature:

        .. code:: python

            def my_code_metric(
                data: Dict,
                response: Union[Dict, str],
                **kwargs,
            ):
                '''
                :keyword data: Row data. This method will be called for each row.
                :paramtype data: Dict
                :keyword response: Response from target function passed to evaluate API otherwise None.
                :paramtype response: Dict
                :keyword kwargs: Includes params like data_mapping for this metric passed to evaluate API.
                :paramtype kwargs: Dict
                '''

    :paramtype calculate: Callable
    :keyword aggregator: Function to aggregate row level metrics. It should have the following signature:

        .. code:: python

            def my_aggregator(
                values: Union[int, Dict[str, int]],
                **kwargs,
            ):
                '''
                :keyword values: Row level metric value calculated by calculate method of the metric.
                :paramtype values: Union[int, Dict[str, int]]
                :keyword kwargs: Includes params like data_mapping for this metric passed to evaluate API.
                :paramtype kwargs: Dict
                '''

    :paramtype aggregator: Callable
    """

    def __init__(self, *, name, calculate, aggregator=None, **kwargs):
        super(CodeMetric, self).__init__(name=name)
        self.calculate = calculate
        self.aggregator = aggregator if aggregator else mean


# WIP: This implementation will change
class PromptMetric(Metric):
    """
    Evaluation prompt metric

    :keyword name: Name of the metric.
    :paramtype name: str
    :keyword parameters: Parameters to be filled into prompt.
    :paramtype name: List[str]
    :keyword name: Description of the metric. This will be added to the prompt sent to LLM
    :paramtype name: str
    :keyword examples: Examples showing input and expected output for this metric
    :paramtype name: str

    .. code-block:: python

        # Metric from prompt template
        custom_prompt_metric = PromptMetric.from_template(path="test_template.jinja2", name="my_relevance_from_template")

        # Creating metric by provided details needed to build the prompt
        metric = PromptMetric(
                description="Relevance measures how well the answer addresses the main aspects of the question,"
                            "based on the context. Consider whether all and only the important aspects are contained in the"
                            "answer when evaluating relevance. Given the context and question, score the relevance of the"
                            "answer between one to five stars using the following rating scale:"
                            "One star: the answer completely lacks relevance"
                            "Two stars: the answer mostly lacks relevance"
                            "Three stars: the answer is partially relevant"
                            "Four stars: the answer is mostly relevant"
                            "Five stars: the answer has perfect relevance"
                            "This rating value should always be an integer between 1 and 5. So the rating produced"
                            "should be 1 or 2 or 3 or 4 or 5 and should be a single digit",
                examples="context: Marie Curie was a Polish-born physicist and chemist who pioneered research on radioactivity"
                         "and was the first woman to win a Nobel Prize."
                         "question: What field did Marie Curie excel in?"
                         "answer: Marie Curie was a renowned painter who focused mainly on impressionist styles and techniques."
                         "stars: 1",
                         "                                                                                                     "
                         "context: The Beatles were an English rock band formed in Liverpool in 1960, and they are widely"
                         "regarded as the most influential music band in history."
                         "question: Where were The Beatles formed? "
                         "answer: The band The Beatles began their journey in London, England, and they changed the history of"
                         "music."
                         "stars: 2",
                name="my_relevance",
                parameters=["question", "answer", "context"]
            )
    """

    def __init__(self, *, name, parameters, description=None, examples=None, **kwargs):
        super(PromptMetric, self).__init__(name=name)

        self.parameters = parameters
        self.examples = examples
        self.description = description
        self.prompt = self._build_prompt()
        self._parser = ScoreReasonParser
        self.aggregator = kwargs.get("aggregator") if kwargs.get("aggregator", None) else mean

    def _build_prompt(self):
        from jinja2 import Template

        with importlib.resources.open_text("azure.ai.generative.evaluate.metrics.templates",
                                           "custom_metric_base.jinja2", encoding="utf-8") as template_file:
            template = Template(template_file.read())

        prompt_as_string = template.render({
            "prompt": self.description,
            "examples": self.examples,
            "inputs": {param: f"{{{{{param}}}}}" for param in self.parameters}
        })

        return prompt_as_string

    @staticmethod
    def from_template(path, name):
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
        metric._parser = ScoreParser

        return metric
