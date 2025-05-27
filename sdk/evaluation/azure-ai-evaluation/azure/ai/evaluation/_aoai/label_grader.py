# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Dict, Union, List

from azure.ai.evaluation._model_configurations import AzureOpenAIModelConfiguration, OpenAIModelConfiguration
from openai.types.graders import LabelModelGrader
from azure.ai.evaluation._common._experimental import experimental

from .aoai_grader import AzureOpenAIGrader

@experimental
class AzureOpenAILabelGrader(AzureOpenAIGrader):
    """
    Wrapper class for OpenAI's label model graders.

    Supplying a LabelGrader to the `evaluate` method will cause an asynchronous request to evaluate
    the grader via the OpenAI API. The results of the evaluation will then be merged into the standard
    evaluation results.

    :param model_config: The model configuration to use for the grader.
    :type model_config: Union[
        ~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration
    ]
    :param input: The list of label-based testing criterion for this grader. Individual
        values of this list are expected to be dictionaries that match the format of any of the valid
        (TestingCriterionLabelModelInput)[https://github.com/openai/openai-python/blob/ed53107e10e6c86754866b48f8bd862659134ca8/src/openai/types/eval_create_params.py#L125C1-L125C32]
        subtypes.
    :type input: List[Dict[str, str]]
    :param labels: A list of strings representing the classification labels of this grader.
    :type labels: List[str]
    :param model: The model to use for the evaluation. Must support structured outputs.
    :type model: str
    :param name: The name of the grader.
    :type name: str
    :param passing_labels: The labels that indicate a passing result. Must be a subset of labels.
    :type passing_labels: List[str]
    :param kwargs: Additional keyword arguments to pass to the grader.
    :type kwargs: Any


    """

    id = "aoai://label_model"

    def __init__(
        self,
        *,
        model_config : Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration],
        input: List[Dict[str, str]],
        labels: List[str],
        model: str,
        name: str,
        passing_labels: List[str],
        **kwargs: Any
    ):
        grader = LabelModelGrader(
            input=input,
            labels=labels,
            model=model,
            name=name,
            passing_labels=passing_labels,
            type="label_model",
        )
        super().__init__(model_config=model_config, grader_config=grader, **kwargs)
