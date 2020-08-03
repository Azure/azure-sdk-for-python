# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

from ..._exceptions import CredentialUnavailableError
from .._credentials.base import AsyncCredentialBase
from ..._constants import AZURE_VSCODE_CLIENT_ID
from .._internal.aad_client import AadClient
from .._internal.decorators import log_get_token_async
from ..._credentials.vscode import get_credentials

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any
    from azure.core.credentials import AccessToken


class VisualStudioCodeCredential(AsyncCredentialBase):
    """Authenticates as the Azure user signed in to Visual Studio Code.

    :keyword str authority: Authority of an Azure Active Directory endpoint, for example 'login.microsoftonline.com',
          the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.AzureAuthorityHosts`
          defines authorities for other clouds.
    :keyword str tenant_id: ID of the tenant the credential should authenticate in. Defaults to the "organizations"
        tenant, which supports only Azure Active Directory work or school accounts.
    """

    def __init__(self, **kwargs: "Any") -> None:
        self._refresh_token = None
        self._client = kwargs.pop("_client", None)
        if not self._client:
            tenant_id = kwargs.pop("tenant_id", None) or "organizations"
            self._client = AadClient(tenant_id, AZURE_VSCODE_CLIENT_ID, **kwargs)

    async def __aenter__(self):
        if self._client:
            await self._client.__aenter__()
        return self

    async def close(self):
        """Close the credential's transport session."""

        if self._client:
            await self._client.__aexit__()

    @log_get_token_async
    async def get_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> AccessToken
        """Request an access token for `scopes` as the user currently signed in to Visual Studio Code.

        .. note:: This method is called by Azure SDK clients. It isn't intended for use in application code.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises ~azure.identity.CredentialUnavailableError: the credential cannot retrieve user details from Visual
          Studio Code
        """
        if not scopes:
            raise ValueError("'get_token' requires at least one scope")

        token = self._client.get_cached_access_token(scopes)
        if not token:
            token = await self._redeem_refresh_token(scopes, **kwargs)
        elif self._client.should_refresh(token):
            try:
                await self._redeem_refresh_token(scopes, **kwargs)
            except Exception:  # pylint: disable=broad-except
                pass
        return token

    async def _redeem_refresh_token(self, scopes: "Sequence[str]", **kwargs: "Any") -> "Optional[AccessToken]":
        if not self._refresh_token:
            self._refresh_token = get_credentials()
            if not self._refresh_token:
                raise CredentialUnavailableError(message="Failed to get Azure user details from Visual Studio Code.")

        token = await self._client.obtain_token_by_refresh_token(scopes, self._refresh_token, **kwargs)
        return token
