# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Dict, List, Optional, Union

from openai.types.graders import ScoreModelGrader

from azure.ai.evaluation._common._experimental import experimental
from azure.ai.evaluation._model_configurations import (
    AzureOpenAIModelConfiguration,
    OpenAIModelConfiguration,
)
from azure.core.credentials import TokenCredential

from .aoai_grader import AzureOpenAIGrader


@experimental
class AzureOpenAIScoreModelGrader(AzureOpenAIGrader):
    """Wrapper class for OpenAI's score model graders.

    Enables continuous scoring evaluation with custom prompts and flexible
    conversation-style inputs. Supports configurable score ranges and
    pass thresholds for binary classification.

    Supplying a ScoreModelGrader to the `evaluate` method will cause an
    asynchronous request to evaluate the grader via the OpenAI API. The
    results of the evaluation will then be merged into the standard
    evaluation results.

    :param model_config: The model configuration to use for the grader.
    :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration]
    :param input: The input messages for the grader. List of conversation
        messages with role and content.
    :type input: List[Dict[str, str]]
    :param model: The model to use for the evaluation.
    :type model: str
    :param name: The name of the grader.
    :type name: str
    :param range: The range of the score. Defaults to [0, 1].
    :type range: Optional[List[float]]
    :param pass_threshold: Score threshold for pass/fail classification.
        Defaults to midpoint of range.
    :type pass_threshold: Optional[float]
    :param sampling_params: The sampling parameters for the model.
    :type sampling_params: Optional[Dict[str, Any]]
    :param credential: The credential to use to authenticate to the model. Only applicable to AzureOpenAI models.
    :type credential: ~azure.core.credentials.TokenCredential
    :param kwargs: Additional keyword arguments to pass to the grader.
    :type kwargs: Any
    """

    id = "azureai://built-in/evaluators/azure-openai/score_model_grader"
    _type = "score_model"

    def __init__(
        self,
        *,
        model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration],
        input: List[Dict[str, str]],
        model: str,
        name: str,
        range: Optional[List[float]] = None,
        pass_threshold: Optional[float] = None,
        sampling_params: Optional[Dict[str, Any]] = None,
        credential: Optional[TokenCredential] = None,
        **kwargs: Any,
    ):
        # Validate range and pass_threshold
        if range is not None:
            if len(range) != 2 or range[0] >= range[1]:
                raise ValueError(
                    "range must be a list of two numbers [min, max] where min < max"
                )
        else:
            range = [0.0, 1.0]  # Default range

        if pass_threshold is not None:
            if range and (pass_threshold < range[0] or pass_threshold > range[1]):
                raise ValueError(
                    f"pass_threshold {pass_threshold} must be within range {range}"
                )
        else:
            pass_threshold = (range[0] + range[1]) / 2  # Default to midpoint

        # Store pass_threshold as instance attribute
        self.pass_threshold = pass_threshold

        # Create OpenAI ScoreModelGrader instance
        grader_kwargs = {
            "input": input,
            "model": model,
            "name": name,
            "type": AzureOpenAIScoreModelGrader._type,
        }

        if range is not None:
            grader_kwargs["range"] = range
        if sampling_params is not None:
            grader_kwargs["sampling_params"] = sampling_params
        grader_kwargs["pass_threshold"] = self.pass_threshold

        grader = ScoreModelGrader(**grader_kwargs)

        super().__init__(
            model_config=model_config,
            grader_config=grader,
            credential=credential,
            **kwargs,
        )
