# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Dict, Union
from typing_extensions import Literal

from azure.ai.evaluation._model_configurations import AzureOpenAIModelConfiguration, OpenAIModelConfiguration
from openai.types.graders import TextSimilarityGrader
from azure.ai.evaluation._common._experimental import experimental

from .aoai_grader import AzureOpenAIGrader

@experimental
class AzureOpenAITextSimilarityGrader(AzureOpenAIGrader):
    """
    Wrapper class for OpenAI's string check graders.

    Supplying a StringCheckGrader to the `evaluate` method will cause an asynchronous request to evaluate
    the grader via the OpenAI API. The results of the evaluation will then be merged into the standard
    evaluation results.

    :param model_config: The model configuration to use for the grader.
    :type model_config: Union[
        ~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration
    ]
    :param evaluation_metric: The evaluation metric to use.
    :type evaluation_metric: Literal[
            "fuzzy_match",
            "bleu",
            "gleu",
            "meteor",
            "rouge_1",
            "rouge_2",
            "rouge_3",
            "rouge_4",
            "rouge_5",
            "rouge_l",
            "cosine",
        ]
    :param input: The text being graded.
    :type input: str
    :param pass_threshold: A float score where a value greater than or equal indicates a passing grade.
    :type pass_threshold: float
    :param reference: The text being graded against.
    :type reference: str
    :param name: The name of the grader.
    :type name: str
    :param kwargs: Additional keyword arguments to pass to the grader.
    :type kwargs: Any


    """

    id = "aoai://text_similarity"

    def __init__(
        self,
        *,
        model_config : Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration],
        evaluation_metric: Literal[
            "fuzzy_match",
            "bleu",
            "gleu",
            "meteor",
            "rouge_1",
            "rouge_2",
            "rouge_3",
            "rouge_4",
            "rouge_5",
            "rouge_l",
            "cosine",
        ],
        input: str,
        pass_threshold: float,
        reference: str,
        name: str,
        **kwargs: Any
    ):
        grader = TextSimilarityGrader(
            evaluation_metric=evaluation_metric,
            input=input,
            pass_threshold=pass_threshold,
            name=name,
            reference=reference,
            type="text_similarity",
        )
        super().__init__(model_config=model_config, grader_config=grader, **kwargs)
