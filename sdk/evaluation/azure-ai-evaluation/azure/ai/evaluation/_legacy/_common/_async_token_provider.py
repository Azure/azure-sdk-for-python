# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import os
import threading
from typing import Any, AsyncContextManager, Optional

from azure.core.credentials import AccessToken, TokenCredential
from azure.identity import AzureCliCredential, DefaultAzureCredential, ManagedIdentityCredential

from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget
from azure.ai.evaluation._azure._envs import AzureEnvironmentClient

logger = logging.getLogger(__name__)


class AsyncAzureTokenProvider(AsyncContextManager["AsyncAzureTokenProvider"]):
    """Asynchronous token provider for Azure services that supports non-default Azure clouds
    (e.g. Azure China, Azure US Government, etc.).

    Closing the provider releases both its internally created synchronous credential and environment client.
    Lazy token acquisition remains reusable until the provider is closed.
    """

    def __init__(self, *, base_url: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize the AsyncAzureTokenProvider."""
        self._credential: Optional[TokenCredential] = None
        self._env_client: Optional[AzureEnvironmentClient] = AzureEnvironmentClient(base_url=base_url, **kwargs)
        self._credential_lock = threading.Lock()

    async def close(self) -> None:
        with self._credential_lock:
            credential, client = self._credential, self._env_client
            self._credential = None
            self._env_client = None
        try:
            close_credential = getattr(credential, "close", None)
            if close_credential is not None:
                close_credential()
        finally:
            if client is not None:
                await client.close()

    async def get_credential(self) -> TokenCredential:
        """Return the synchronous credential that supplies this provider's tokens, creating it on first use.

        Concurrent first requests all use the first credential created, so they can share its token.

        :return: The credential.
        :rtype: ~azure.core.credentials.TokenCredential
        """
        credential = self._credential
        if credential is None:
            created = await self._initialize_async(self._env_client)
            with self._credential_lock:
                closed = self._env_client is None
                # A provider closed while the credential was created keeps no credential.
                if self._credential is None and not closed:
                    self._credential = created
                credential = self._credential
            if credential is not created:
                close_created = getattr(created, "close", None)
                if close_created is not None:
                    close_created()
            if closed:
                raise EvaluationException(
                    f"{AsyncAzureTokenProvider.__name__} instance has already been closed.",
                    target=ErrorTarget.UNKNOWN,
                    category=ErrorCategory.INVALID_VALUE,
                    blame=ErrorBlame.USER_ERROR,
                )

        if credential is None:
            raise EvaluationException(
                f"{self.__class__.__name__} could not determine the credential to use.",
                target=ErrorTarget.UNKNOWN,
                category=ErrorCategory.INVALID_VALUE,
                blame=ErrorBlame.SYSTEM_ERROR,
            )
        return credential

    async def get_token(
        self,
        *scopes: str,
        claims: Optional[str] = None,
        tenant_id: Optional[str] = None,
        enable_cae: bool = False,
        **kwargs: Any,
    ) -> AccessToken:
        credential = await self.get_credential()
        return credential.get_token(*scopes, claims=claims, tenant_id=tenant_id, enable_cae=enable_cae, **kwargs)

    async def __aenter__(self) -> "AsyncAzureTokenProvider":
        try:
            await self.get_credential()
        except BaseException:
            try:
                await self.close()
            except Exception as cleanup_error:
                logger.warning("Token provider cleanup failed during initialization: %s", type(cleanup_error).__name__)
            raise
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[Any] = None,
    ) -> None:
        await self.close()

    @staticmethod
    async def _initialize_async(client: Optional[AzureEnvironmentClient]) -> TokenCredential:
        # Determine which credential to use based on the configured Azure cloud environment variables
        # and possibly making network calls to Azure to get the correct Azure cloud metadata.
        if client is None:
            raise EvaluationException(
                f"{AsyncAzureTokenProvider.__name__} instance has already been closed.",
                target=ErrorTarget.UNKNOWN,
                category=ErrorCategory.INVALID_VALUE,
                blame=ErrorBlame.USER_ERROR,
            )

        cloud_name: str = await client.get_default_cloud_name_async()
        if cloud_name != client.DEFAULT_AZURE_CLOUD_NAME:
            # If the cloud name is not the default, we need to get the metadata for the specified cloud
            # and set it in the environment client.
            metadata = await client.get_cloud_async(cloud_name)
            if metadata is None:
                raise EvaluationException(
                    f"Failed to get metadata for cloud '{cloud_name}'.",
                    target=ErrorTarget.UNKNOWN,
                    category=ErrorCategory.INVALID_VALUE,
                    blame=ErrorBlame.USER_ERROR,
                )

            authority = metadata.get("active_directory_endpoint")
            return DefaultAzureCredential(authority=authority, exclude_shared_token_cache_credential=True)
        elif os.getenv("AZUREML_OBO_ENABLED"):
            # using Azure on behalf of credentials requires the use of the azure-ai-ml package
            try:
                from azure.ai.ml.identity import AzureMLOnBehalfOfCredential

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
            # TODO ralphe: Is this still needed? DefaultAzureCredential already includes CLI credentials
            #              albeit with a lower priority
            return AzureCliCredential()
        elif os.environ.get("IS_IN_CI_PIPELINE", "false").lower() == "true":
            # use managed identity when executing in CI pipeline.
            return AzureCliCredential()
        elif identity_client_id := os.environ.get("DEFAULT_IDENTITY_CLIENT_ID"):
            return ManagedIdentityCredential(client_id=identity_client_id)
        else:
            return DefaultAzureCredential()
