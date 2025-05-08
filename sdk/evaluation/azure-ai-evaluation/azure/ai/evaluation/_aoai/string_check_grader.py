# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Dict, Union
from typing_extensions import Literal

from azure.ai.evaluation._model_configurations import AzureOpenAIModelConfiguration, OpenAIModelConfiguration
from openai.types.graders import StringCheckGrader
from azure.ai.evaluation._common._experimental import experimental

from .aoai_grader import AzureOpenAIGrader

@experimental
class AzureOpenAIStringCheckGrader(AzureOpenAIGrader):
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
    :param input: The input text. This may include template strings.
    :type input: str
    :param name: The name of the grader.
    :type name: str
    :param operation: The string check operation to perform. One of `eq`, `ne`, `like`, or `ilike`.
    :type operation: Literal["eq", "ne", "like", "ilike"]
    :param reference: The reference text. This may include template strings.
    :type reference: str
    :param kwargs: Additional keyword arguments to pass to the grader.
    :type kwargs: Any


    """

    id = "aoai://string_check"

    def __init__(
        self,
        *,
        model_config : Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration],
        input: str,
        name: str,
        operation: Literal[
            "eq",
            "ne",
            "like",
            "ilike",
        ],
        reference: str,
        **kwargs: Any
    ):
        grader = StringCheckGrader(
            input=input,
            name=name,
            operation=operation,
            reference=reference,
            type="string_check",
        )
        super().__init__(model_config=model_config, grader_config=grader, **kwargs)
