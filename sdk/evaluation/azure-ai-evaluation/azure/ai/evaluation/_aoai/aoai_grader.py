# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from typing_extensions import TypeIs

from azure.ai.evaluation._common._experimental import experimental
from azure.ai.evaluation._constants import DEFAULT_AOAI_API_VERSION, TokenScope
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from azure.ai.evaluation._model_configurations import AzureOpenAIModelConfiguration, OpenAIModelConfiguration
from azure.ai.evaluation._user_agent import UserAgentSingleton
from azure.core.credentials import TokenCredential

if TYPE_CHECKING:
    from openai.lib.azure import AzureADTokenProvider


@experimental
class AzureOpenAIGrader:
    """Base class for Azure OpenAI grader wrappers.

    Recommended only for use by experienced OpenAI API users.
    Combines a model configuration and any grader configuration
    into a singular object that can be used in evaluations.

    Supplying an AzureOpenAIGrader to the `evaluate` method will cause an asynchronous request to evaluate
    the grader via the OpenAI API. The results of the evaluation will then be merged into the standard
    evaluation results.

    :param model_config: The model configuration to use for the grader.
    :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration]
    :param grader_config: The grader configuration to use for the grader. This is expected
        to be formatted as a dictionary that matches the specifications of the sub-types of
        the TestingCriterion alias specified in `OpenAI's SDK <https://github.com/openai/openai-python/blob/ed53107e10e6c86754866b48f8bd862659134ca8/src/openai/types/eval_create_params.py#L151>`_.
    :type grader_config: Dict[str, Any]
    :param credential: The credential to use to authenticate to the model. Only applicable to AzureOpenAI models.
    :type credential: ~azure.core.credentials.TokenCredential
    :param kwargs: Additional keyword arguments to pass to the grader.
    :type kwargs: Any
    """

    id = "azureai://built-in/evaluators/azure-openai/custom_grader"

    def __init__(
        self,
        *,
        model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration],
        grader_config: Dict[str, Any],
        credential: Optional[TokenCredential] = None,
        **kwargs: Any,
    ):
        self._model_config = model_config
        self._grader_config = grader_config
        self._credential = credential

        if kwargs.get("validate", True):
            self._validate_model_config()
            self._validate_grader_config()

    def _validate_model_config(self) -> None:
        """Validate the model configuration that this grader wrapper is using."""
        msg = None
        if self._is_azure_model_config(self._model_config):
            if not any(auth for auth in (self._model_config.get("api_key"), self._credential)):
                msg = (
                    f"{type(self).__name__}: Requires an api_key in the supplied model_config, "
                    + "or providing a credential to the grader's __init__ method. "
                )

        else:
            if "api_key" not in self._model_config or not self._model_config.get("api_key"):
                msg = f"{type(self).__name__}: Requires an api_key in the supplied model_config."

        if msg is None:
            return

        raise EvaluationException(
            message=msg,
            blame=ErrorBlame.USER_ERROR,
            category=ErrorCategory.INVALID_VALUE,
            target=ErrorTarget.AOAI_GRADER,
        )

    def _validate_grader_config(self) -> None:
        """Validate the grader configuration that this grader wrapper is using."""

        return

    @staticmethod
    def _is_azure_model_config(
        model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration],
    ) -> TypeIs[AzureOpenAIModelConfiguration]:
        return "azure_endpoint" in model_config

    def get_client(self) -> Any:
        """Construct an appropriate OpenAI client using this grader's model configuration.
        Returns a slightly different client depending on whether or not this grader's model
        configuration is for Azure OpenAI or OpenAI.

        :return: The OpenAI client.
        :rtype: [~openai.OpenAI, ~openai.AzureOpenAI]
        """
        default_headers = {"User-Agent": UserAgentSingleton().value}
        model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration] = self._model_config
        api_key: Optional[str] = model_config.get("api_key")

        if self._is_azure_model_config(model_config):
            from openai import AzureOpenAI

            # TODO set default values?
            return AzureOpenAI(
                azure_endpoint=model_config["azure_endpoint"],
                api_key=api_key,  # Default-style access to appease linters.
                api_version=DEFAULT_AOAI_API_VERSION,  # Force a known working version
                azure_deployment=model_config.get("azure_deployment", ""),
                azure_ad_token_provider=self._get_token_provider(self._credential) if not api_key else None,
                default_headers=default_headers,
            )
        from openai import OpenAI

        # TODO add default values for base_url and organization?
        return OpenAI(
            api_key=api_key,
            base_url=model_config.get("base_url", ""),
            organization=model_config.get("organization", ""),
            default_headers=default_headers,
        )

    @staticmethod
    def _get_token_provider(cred: TokenCredential) -> "AzureADTokenProvider":
        """Get the token provider the AzureOpenAI client.

        :param TokenCredential cred: The Azure authentication credential.
        :return: The token provider if a credential is provided, otherwise None.
        :rtype: openai.lib.azure.AzureADTokenProvider
        """

        return lambda: cred.get_token(TokenScope.COGNITIVE_SERVICES_MANAGEMENT).token
