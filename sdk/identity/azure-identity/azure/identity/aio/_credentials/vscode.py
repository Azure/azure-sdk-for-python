# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import cast, TYPE_CHECKING

from ..._exceptions import CredentialUnavailableError
from .._internal import AsyncContextManager
from .._internal.aad_client import AadClient
from .._internal.get_token_mixin import GetTokenMixin
from ..._credentials.vscode import _VSCodeCredentialBase

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, Optional
    from azure.core.credentials import AccessToken


class VisualStudioCodeCredential(_VSCodeCredentialBase, AsyncContextManager, GetTokenMixin):
    """Authenticates as the Azure user signed in to Visual Studio Code.

    :keyword str authority: authority of an Azure Active Directory endpoint, for example "login.microsoftonline.com".
        This argument is required for a custom cloud and usually unnecessary otherwise. Defaults to the authority
        matching the "Azure: Cloud" setting in VS Code's user settings or, when that setting has no value, the
        authority for Azure Public Cloud.
    :keyword str tenant_id: ID of the tenant the credential should authenticate in. Defaults to the "Azure: Tenant"
        setting in VS Code's user settings or, when that setting has no value, the "organizations" tenant, which
        supports only Azure Active Directory work or school accounts.
    :keyword bool allow_multitenant_authentication: when True, enables the credential to acquire tokens from any tenant
        the user is registered in. When False, which is the default, the credential will acquire tokens only from the
        user's home tenant or the tenant configured by **tenant_id** or VS Code's user settings.
    """

    async def __aenter__(self) -> "VisualStudioCodeCredential":
        if self._client:
            await self._client.__aenter__()
        return self

    async def close(self) -> None:
        """Close the credential's transport session."""

        if self._client:
            await self._client.__aexit__()

    async def get_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":
        """Request an access token for `scopes` as the user currently signed in to Visual Studio Code.

        This method is called automatically by Azure SDK clients.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
        :keyword str tenant_id: optional tenant to include in the token request. If **allow_multitenant_authentication**
            is False, specifying a tenant with this argument may raise an exception.

        :rtype: :class:`azure.core.credentials.AccessToken`

        :raises ~azure.identity.CredentialUnavailableError: the credential cannot retrieve user details from Visual
            Studio Code
        """
        if self._unavailable_reason:
            raise CredentialUnavailableError(message=self._unavailable_reason)
        if not self._client:
            raise CredentialUnavailableError("Initialization failed")

        return await super().get_token(*scopes, **kwargs)

    async def _acquire_token_silently(self, *scopes: str, **kwargs: "Any") -> "Optional[AccessToken]":
        self._client = cast(AadClient, self._client)
        return self._client.get_cached_access_token(scopes, **kwargs)

    async def _request_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":
        refresh_token = self._get_refresh_token()
        self._client = cast(AadClient, self._client)
        return await self._client.obtain_token_by_refresh_token(scopes, refresh_token, **kwargs)

    def _get_client(self, **kwargs: "Any") -> AadClient:
        return AadClient(**kwargs)
