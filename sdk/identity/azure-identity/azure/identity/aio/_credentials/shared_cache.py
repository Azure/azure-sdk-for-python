# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

from ... import CredentialUnavailableError
from ..._constants import AZURE_CLI_CLIENT_ID
from ..._internal.shared_token_cache import NO_TOKEN, SharedTokenCacheBase
from .._internal.aad_client import AadClient
from .._internal.exception_wrapper import wrap_exceptions
from .base import AsyncCredentialBase

if TYPE_CHECKING:
    from typing import Any
    from azure.core.credentials import AccessToken
    from ..._internal.aad_client import AadClientBase


class SharedTokenCacheCredential(SharedTokenCacheBase, AsyncCredentialBase):
    """Authenticates using tokens in the local cache shared between Microsoft applications.

    :param str username:
        Username (typically an email address) of the user to authenticate as. This is required because the local cache
        may contain tokens for multiple identities.

    :keyword str authority: Authority of an Azure Active Directory endpoint, for example 'login.microsoftonline.com',
        the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.KnownAuthorities`
        defines authorities for other clouds.
    :keyword str tenant_id: an Azure Active Directory tenant ID. Used to select an account when the cache contains
        tokens for multiple identities.
    """

    async def __aenter__(self):
        if self._client:
            await self._client.__aenter__()
        return self

    async def close(self):
        """Close the credential's transport session."""

        if self._client:
            await self._client.__aexit__()

    @wrap_exceptions
    async def get_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":  # pylint:disable=unused-argument
        """Get an access token for `scopes` from the shared cache.

        If no access token is cached, attempt to acquire one using a cached refresh token.

        .. note:: This method is called by Azure SDK clients. It isn't intended for use in application code.

        :param str scopes: desired scopes for the token
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises ~azure.identity.CredentialUnavailableError: the cache is unavailable or contains insufficient user
            information
        :raises ~azure.core.exceptions.ClientAuthenticationError: authentication failed
        """

        if not self._client:
            raise CredentialUnavailableError(message="Shared token cache unavailable")

        account = self._get_account(self._username, self._tenant_id)

        # try each refresh token, returning the first access token acquired
        for refresh_token in self._get_refresh_tokens(account):
            token = await self._client.obtain_token_by_refresh_token(refresh_token, scopes)
            return token

        raise CredentialUnavailableError(message=NO_TOKEN.format(account.get("username")))

    def _get_auth_client(self, **kwargs: "Any") -> "AadClientBase":
        return AadClient(tenant_id="common", client_id=AZURE_CLI_CLIENT_ID, **kwargs)
