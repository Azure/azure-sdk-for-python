# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any
import logging
from azure.core.credentials import AccessToken
from .token_exchange import TokenExchangeCredential
from .._internal.decorators import log_get_token_async
from .._internal import AsyncContextManager

_LOGGER = logging.getLogger(__name__)


class WorkloadIdentityCredential(AsyncContextManager):
    """WorkloadIdentityCredential supports Azure workload identity on Kubernetes.
    See https://learn.microsoft.com/azure/aks/workload-identity-overview for more information

    :param str tenant_id: ID of the application's Azure Active Directory tenant. Also called its "directory" ID.
    :param str client_id: the client ID of an Azure AD app registration.
    :param str file: The path to a file containing a Kubernetes service account token that authenticates the identity.
    """
    def __init__(self, tenant_id: str, client_id: str, file: str, **kwargs: Any) -> None:
        kwargs.pop("token_file_path", None)
        self._credential = TokenExchangeCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            token_file_path=file,
            **kwargs
        )

    async def __aenter__(self):
        if self._credential:
            await self._credential.__aenter__()
        return self

    async def close(self) -> None:
        """Close the credential's transport session."""

        if self._credential:
            await self._credential.__aexit__()

    @log_get_token_async
    async def get_token(self, *scopes: str, **kwargs: Any) -> AccessToken:
        """Asynchronously request an access token for `scopes`.

        This method is called automatically by Azure SDK clients.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
            For more information about scopes, see
            https://learn.microsoft.com/azure/active-directory/develop/scopes-oidc.
        :keyword str tenant_id: optional tenant to include in the token request.
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises ~azure.identity.CredentialUnavailableError: environment variable configuration is incomplete
        """
        return await self._credential.get_token(*scopes, **kwargs)
