# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import abc


class Metric(metaclass=abc.ABCMeta):

    def __init__(self, *, name, description, **kwargs):
        self.name = name
        self.description = description


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

    def __init__(self, *, name, calculate, description=None, **kwargs):
        super(CodeMetric, self).__init__(name=name, description=description)
        self.calculate = calculate


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
                prompt="My custom metric prompt"
                name="my_relevance",
            )
    """

    def __init__(self, *, name, prompt, description=None, **kwargs):
        super(PromptMetric, self).__init__(name=name, description=description, **kwargs)

        self.prompt = prompt
        self.description = description
        self.prompt = prompt
        self._template_variable = None

    @staticmethod
    def from_template(*, path, name):
        from jinja2 import Environment
        from jinja2 import meta

        env = Environment()

        with open(path) as template_file:
            template_content = template_file.read()
            template = env.parse(template_content, name="test")

        template_variables = meta.find_undeclared_variables(template)

        metric = PromptMetric(
            name=name,
            prompt=template_content
        )

        metric._template_variable = template_variables
        return metric
