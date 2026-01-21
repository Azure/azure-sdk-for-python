# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Dict, Optional, Union

from openai.types.graders import PythonGrader

from azure.ai.evaluation._common._experimental import experimental
from azure.ai.evaluation._model_configurations import (
    AzureOpenAIModelConfiguration,
    OpenAIModelConfiguration,
)
from azure.core.credentials import TokenCredential

from .aoai_grader import AzureOpenAIGrader


@experimental
class AzureOpenAIPythonGrader(AzureOpenAIGrader):
    """Wrapper class for OpenAI's Python code graders.

    Enables custom Python-based evaluation logic with flexible scoring and
    pass/fail thresholds. The grader executes user-provided Python code
    to evaluate outputs against custom criteria.

    Supplying a PythonGrader to the `evaluate` method will cause an
    asynchronous request to evaluate the grader via the OpenAI API. The
    results of the evaluation will then be merged into the standard
    evaluation results.

    :param model_config: The model configuration to use for the grader.
    :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration]
    :param name: The name of the grader.
    :type name: str
    :param image_tag: The image tag for the Python execution environment.
    :type image_tag: str
    :param pass_threshold: Score threshold for pass/fail classification. Scores >= threshold are considered passing.
    :type pass_threshold: float
    :param source: Python source code containing the grade function.
        Must define: def grade(sample: dict, item: dict) -> float
    :type source: str
    :param credential: The credential to use to authenticate to the model. Only applicable to AzureOpenAI models.
    :type credential: ~azure.core.credentials.TokenCredential
    :param kwargs: Additional keyword arguments to pass to the grader.
    :type kwargs: Any


    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_common.py
            :start-after: [START python_grader_example]
            :end-before: [END python_grader_example]
            :language: python
            :dedent: 8
            :caption: Using AzureOpenAIPythonGrader for custom evaluation logic.
    """

    id = "azureai://built-in/evaluators/azure-openai/python_grader"
    _type = "python"

    def __init__(
        self,
        *,
        model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration],
        name: str,
        pass_threshold: float,
        source: str,
        image_tag: Optional[str] = None,
        credential: Optional[TokenCredential] = None,
        **kwargs: Any,
    ):
        # Validate pass_threshold
        if not 0.0 <= pass_threshold <= 1.0:
            raise ValueError("pass_threshold must be between 0.0 and 1.0")

        # Store pass_threshold as instance attribute for potential future use
        self.pass_threshold = pass_threshold

        # Create OpenAI PythonGrader instance
        grader = PythonGrader(
            name=name,
            image_tag=image_tag,
            pass_threshold=pass_threshold,
            source=source,
            type=AzureOpenAIPythonGrader._type,
        )

        super().__init__(
            model_config=model_config,
            grader_config=grader,
            credential=credential,
            **kwargs,
        )
