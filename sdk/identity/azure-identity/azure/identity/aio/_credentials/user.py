# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING
from azure.core.exceptions import ClientAuthenticationError

from ... import SharedTokenCacheCredential as SyncSharedTokenCacheCredential
from .._authn_client import AsyncAuthnClient
from .._internal.exception_wrapper import wrap_exceptions

if TYPE_CHECKING:
    from typing import Any
    from azure.core.credentials import AccessToken
    from azure.identity._authn_client import AuthnClientBase
    import msal_extensions


class SharedTokenCacheCredential(SyncSharedTokenCacheCredential):
    """Authenticates using tokens in the local cache shared between Microsoft applications.

    :param str username:
        Username (typically an email address) of the user to authenticate as. This is required because the local cache
        may contain tokens for multiple identities.
    """

    @wrap_exceptions
    async def get_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":  # pylint:disable=unused-argument
        """Get an access token for `scopes` from the shared cache.

        If no access token is cached, attempt to acquire one using a cached refresh token.

        :param str scopes: desired scopes for the token
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises ~azure.core.exceptions.ClientAuthenticationError: when the cache is unavailable or no access token
            can be acquired from it

        :keyword str authority: Authority of an Azure Active Directory endpoint, for example
              'login.microsoftonline.com', the authority for Azure Public Cloud (which is the default).
              :class:`~azure.identity.KnownAuthorities` defines authorities for other clouds.
        """

        if not self._client:
            raise ClientAuthenticationError(message="Shared token cache unavailable")

        return await self._client.obtain_token_by_refresh_token(scopes, self._username)

    @staticmethod
    def _get_auth_client(cache: "msal_extensions.FileTokenCache") -> "AuthnClientBase":
        return AsyncAuthnClient(tenant="common", cache=cache)
