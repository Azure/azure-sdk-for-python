# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
from typing import TYPE_CHECKING

from azure.core.exceptions import ClientAuthenticationError
from .._internal import AadClient

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, Collection, Optional
    from azure.core.credentials import AccessToken


class AuthorizationCodeCredential(object):
    """
    Authenticates by redeeming an authorization code previously obtained from Azure Active Directory.
    See https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow for more information
    about the authentication flow.

    :param str client_id: the application's client ID
    :param str tenant_id: ID of the application's Azure Active Directory tenant. Also called its 'directory' ID.
    :param str authorization_code: the authorization code from the user's log-in
    :param str redirect_uri: The application's redirect URI. Must match the URI used to request the authorization code.
    :param str client_secret: One of the application's client secrets. Required only for web apps and web APIs.

    Keyword arguments
        - **authority**: Authority of an Azure Active Directory endpoint, for example 'login.microsoftonline.com', the
          authority for Azure Public Cloud (which is the default). :class:`~azure.identity.KnownAuthorities` defines
          authorities for other clouds.
    """

    def __init__(
        self,
        client_id: str,
        tenant_id: str,
        authorization_code: str,
        redirect_uri: str,
        client_secret: "Optional[str]" = None,
        **kwargs: "Any"
    ) -> None:
        self._authorization_code = authorization_code  # type: Optional[str]
        self._client_id = client_id
        self._client_secret = client_secret
        self._client = kwargs.pop("client", None) or AadClient(client_id, tenant_id, **kwargs)
        self._redirect_uri = redirect_uri

    async def get_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":
        """
        Request an access token for ``scopes``. The first time this method is called, the credential will redeem its
        authorization code. On subsequent calls the credential will return a cached access token or redeem a refresh
        token, if it acquired a refresh token upon redeeming the authorization code.

        :param str scopes: desired scopes for the access token
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises: :class:`azure.core.exceptions.ClientAuthenticationError`

        **Keyword arguments:**
          - **executor** - (optional) a :class:`concurrent.futures.Executor` used to execute asynchronous calls
          - **loop** - (optional) an event loop on which to schedule network I/O. If not provided, the currently running
            loop will be used.
        """

        if self._authorization_code:
            loop = kwargs.pop("loop", None) or asyncio.get_event_loop()
            token = await self._client.obtain_token_by_authorization_code(
                code=self._authorization_code, redirect_uri=self._redirect_uri, scopes=scopes, loop=loop, **kwargs
            )
            self._authorization_code = None  # auth codes are single-use
            return token

        token = self._client.get_cached_access_token(scopes)
        if not token:
            token = await self._redeem_refresh_token(scopes, **kwargs)

        if not token:
            raise ClientAuthenticationError(
                message="No authorization code, cached access token, or refresh token available."
            )

        return token

    async def _redeem_refresh_token(self, scopes: "Collection[str]", **kwargs: "Any") -> "Optional[AccessToken]":
        loop = kwargs.pop("loop", None) or asyncio.get_event_loop()
        for refresh_token in self._client.get_cached_refresh_tokens(scopes):
            token = await self._client.obtain_token_by_refresh_token(refresh_token, scopes, loop=loop, **kwargs)
            if token:
                return token
        return None
