# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import logging
import time
import inspect
from typing import cast, Optional, Union, Any

from azure.core.credentials import TokenCredential, AccessToken
from azure.identity import AzureCliCredential, DefaultAzureCredential, ManagedIdentityCredential
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException

from ..simulator._model_tools._identity_manager import APITokenManager, AZURE_TOKEN_REFRESH_INTERVAL


class AzureMLTokenManager(APITokenManager):
    """API Token manager for Azure Management API.

    :param token_scope: Token scopes for Azure endpoint
    :type token_scope: str
    :param logger: Logger object
    :type logger: logging.Logger
    :keyword kwargs: Additional keyword arguments
    :paramtype kwargs: Dict
    """

    def __init__(
        self,
        token_scope: str,
        logger: logging.Logger,
        credential: Optional[TokenCredential] = None,
    ):
        super().__init__(logger, credential=credential)
        self.token_scope = token_scope
        self.token_expiry_time: Optional[int] = None

    def get_aad_credential(self) -> Union[DefaultAzureCredential, ManagedIdentityCredential]:
        """Get the Azure credentials to use for the management APIs.

        :return: Azure credentials
        :rtype: DefaultAzureCredential or ManagedIdentityCredential
        """
        # Adds some of the additional types credentials that the previous Azure AI ML code used
        # These may or may not be needed but kept here for backwards compatibility

        if os.getenv("AZUREML_OBO_ENABLED"):
            # using Azure on behalf of credentials requires the use of the azure-ai-ml package
            try:
                from azure.ai.ml.identity import AzureMLOnBehalfOfCredential

                self.logger.debug("User identity is configured, use OBO credential.")
                return AzureMLOnBehalfOfCredential()  # type: ignore
            except (ModuleNotFoundError, ImportError):
                raise EvaluationException(  # pylint: disable=raise-missing-from
                    message=(
                        "The required packages for OBO credentials are missing.\n"
                        'To resolve this, please install them by running "pip install azure-ai-ml".'
                    ),
                    target=ErrorTarget.EVALUATE,
                    category=ErrorCategory.MISSING_PACKAGE,
                    blame=ErrorBlame.USER_ERROR,
                )
        elif os.environ.get("PF_USE_AZURE_CLI_CREDENTIAL", "false").lower() == "true":
            self.logger.debug("Use azure cli credential since specified in environment variable.")
            return AzureCliCredential()  # type: ignore
        elif os.environ.get("IS_IN_CI_PIPELINE", "false").lower() == "true":
            # use managed identity when executing in CI pipeline.
            self.logger.debug("Use azure cli credential since in CI pipeline.")
            return AzureCliCredential()  # type: ignore
        else:
            # Fall back to using the parent implementation
            return super().get_aad_credential()

    def get_token(
            self, scopes = None, claims: Union[str, None] = None, tenant_id: Union[str, None] = None, enable_cae: bool = False, **kwargs: Any) -> AccessToken:
        """Get the API token. If the token is not available or has expired, refresh the token.

        :return: API token
        :rtype: str
        """
        if self._token_needs_update():
            credential = cast(TokenCredential, self.credential)
            token_scope = self.token_scope
            if scopes:
                token_scope = scopes
            access_token = credential.get_token(token_scope)
            self._update_token(access_token)

        return cast(AccessToken, self.token)  # check for none is hidden in the _token_needs_update method

    async def get_token_async(self) -> AccessToken:
        """Get the API token asynchronously. If the token is not available or has expired, refresh it.

        :return: API token
        :rtype: str
        """
        if self._token_needs_update():
            credential = cast(TokenCredential, self.credential)
            get_token_method = credential.get_token(self.token_scope)
            if inspect.isawaitable(get_token_method):
                access_token = await get_token_method
            else:
                access_token = get_token_method
            self._update_token(access_token)

        return cast(AccessToken, self.token)  # check for none is hidden in the _token_needs_update method

    def _token_needs_update(self) -> bool:
        current_time = time.time()
        return (
            self.token is None
            or self.last_refresh_time is None
            or self.token_expiry_time is None
            or self.token_expiry_time - current_time < AZURE_TOKEN_REFRESH_INTERVAL
            or current_time - self.last_refresh_time > AZURE_TOKEN_REFRESH_INTERVAL
        )

    def _update_token(self, access_token: AccessToken) -> None:
        self.token = access_token
        self.token_expiry_time = access_token.expires_on
        self.last_refresh_time = time.time()
        self.logger.info("Refreshed Azure management token.")
