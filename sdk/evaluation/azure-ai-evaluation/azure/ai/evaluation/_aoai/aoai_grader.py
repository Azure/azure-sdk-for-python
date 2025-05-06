# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azure.ai.evaluation._model_configurations import AzureOpenAIModelConfiguration, OpenAIModelConfiguration

from azure.ai.evaluation._constants import DEFAULT_AOAI_API_VERSION
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from typing import Any, Dict, Union
from azure.ai.evaluation._common._experimental import experimental


@experimental
class AzureOpenAIGrader():
    """
    Base class for Azure OpenAI grader wrappers, recommended only for use by experienced OpenAI API users.
    Combines a model configuration and any grader configuration
    into a singular object that can be used in evaluations.

    Supplying an AzureOpenAIGrader to the `evaluate` method will cause an asynchronous request to evaluate
    the grader via the OpenAI API. The results of the evaluation will then be merged into the standard
    evaluation results.

    :param model_config: The model configuration to use for the grader.
    :type model_config: Union[
        ~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration
    ]
    :param grader_config: The grader configuration to use for the grader. This is expected
        to be formatted as a dictionary that matches the specifications of the sub-types of
        the TestingCriterion alias specified in (OpenAI's SDK)[https://github.com/openai/openai-python/blob/ed53107e10e6c86754866b48f8bd862659134ca8/src/openai/types/eval_create_params.py#L151].
    :type grader_config: Dict[str, Any]
    :param kwargs: Additional keyword arguments to pass to the grader.
    :type kwargs: Any


    """

    id = "aoai://general"

    def __init__(self, *, model_config : Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration], grader_config: Dict[str, Any], **kwargs: Any):
        self._model_config = model_config
        self._grader_config = grader_config

        if kwargs.get("validate", True):
            self._validate_model_config()
            self._validate_grader_config()



    def _validate_model_config(self) -> None:
        """Validate the model configuration that this grader wrapper is using."""
        if "api_key" not in self._model_config or not self._model_config.get("api_key"):
            msg = f"{type(self).__name__}: Requires an api_key in the supplied model_config."
            raise EvaluationException(
                message=msg,
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.INVALID_VALUE,
                target=ErrorTarget.AOAI_GRADER,
            )
    
    def _validate_grader_config(self) -> None:
        """Validate the grader configuration that this grader wrapper is using."""

        return

    def get_client(self) -> Any:
        """Construct an appropriate OpenAI client using this grader's model configuration.
        Returns a slightly different client depending on whether or not this grader's model
        configuration is for Azure OpenAI or OpenAI.

        :return: The OpenAI client.
        :rtype: [~openai.OpenAI, ~openai.AzureOpenAI]
        """
        if "azure_endpoint" in self._model_config:
           from openai import AzureOpenAI
           # TODO set default values?
           return AzureOpenAI(
                azure_endpoint=self._model_config["azure_endpoint"],
                api_key=self._model_config.get("api_key", None), # Default-style access to appease linters.
                api_version=DEFAULT_AOAI_API_VERSION, # Force a known working version
                azure_deployment=self._model_config.get("azure_deployment", ""),
            )
        from openai import OpenAI
        # TODO add default values for base_url and organization?
        return OpenAI(
            api_key=self._model_config["api_key"],
            base_url=self._model_config.get("base_url", ""),
            organization=self._model_config.get("organization", ""),
        )
