# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING, Any, Optional

from .silent import SilentAuthenticationCredential
from .. import CredentialUnavailableError
from .._constants import DEVELOPER_SIGN_ON_CLIENT_ID
from .._internal import AadClient
from .._internal.decorators import log_get_token
from .._internal.shared_token_cache import NO_TOKEN, SharedTokenCacheBase

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    from .._internal import AadClientBase


class SharedTokenCacheCredential(object):
    """Authenticates using tokens in the local cache shared between Microsoft applications.

    :param str username: Username (typically an email address) of the user to authenticate as. This is used when the
        local cache contains tokens for multiple identities.

    :keyword str authority: Authority of an Azure Active Directory endpoint, for example 'login.microsoftonline.com',
        the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.AzureAuthorityHosts`
        defines authorities for other clouds.
    :keyword str tenant_id: an Azure Active Directory tenant ID. Used to select an account when the cache contains
        tokens for multiple identities.
    :keyword AuthenticationRecord authentication_record: an authentication record returned by a user credential such as
        :class:`DeviceCodeCredential` or :class:`InteractiveBrowserCredential`
    :keyword cache_persistence_options: configuration for persistent token caching. If not provided, the credential
        will use the persistent cache shared by Microsoft development applications
    :paramtype cache_persistence_options: ~azure.identity.TokenCachePersistenceOptions
    """

    def __init__(self, username: str = None, **kwargs) -> None:
        if "authentication_record" in kwargs:
            self._credential = SilentAuthenticationCredential(**kwargs)  # type: TokenCredential
        else:
            self._credential = _SharedTokenCacheCredential(username=username, **kwargs)

    def __enter__(self):
        self._credential.__enter__()
        return self

    def __exit__(self, *args):
        self._credential.__exit__(*args)

    def close(self) -> None:
        """Close the credential's transport session."""
        self.__exit__()

    @log_get_token("SharedTokenCacheCredential")
    def get_token(self, *scopes, **kwargs):
        # type (*str, **Any) -> AccessToken
        """Get an access token for `scopes` from the shared cache.

        If no access token is cached, attempt to acquire one using a cached refresh token.

        This method is called automatically by Azure SDK clients.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.

        :keyword str claims: additional claims required in the token, such as those returned in a resource provider's
            claims challenge following an authorization failure

        :rtype: :class:`azure.core.credentials.AccessToken`

        :raises ~azure.identity.CredentialUnavailableError: the cache is unavailable or contains insufficient user
            information
        :raises ~azure.core.exceptions.ClientAuthenticationError: authentication failed. The error's ``message``
            attribute gives a reason.
        """
        return self._credential.get_token(*scopes, **kwargs)

    @staticmethod
    def supported() -> bool:
        """Whether the shared token cache is supported on the current platform.

        :rtype: bool
        """
        return SharedTokenCacheBase.supported()


class _SharedTokenCacheCredential(SharedTokenCacheBase):
    """The original SharedTokenCacheCredential, which doesn't use msal.ClientApplication"""

    def __enter__(self):
        if self._client:
            self._client.__enter__()
        return self

    def __exit__(self, *args):
        if self._client:
            self._client.__exit__(*args)

    def get_token(self, *scopes, **kwargs):
        # type (*str, **Any) -> AccessToken
        if not scopes:
            raise ValueError("'get_token' requires at least one scope")

        if not self._initialized:
            self._initialize()

        if not self._cache:
            raise CredentialUnavailableError(message="Shared token cache unavailable")

        account = self._get_account(self._username, self._tenant_id)

        token = self._get_cached_access_token(scopes, account)
        if token:
            return token

        # try each refresh token, returning the first access token acquired
        for refresh_token in self._get_refresh_tokens(account):
            token = self._client.obtain_token_by_refresh_token(scopes, refresh_token, **kwargs)
            return token

        raise CredentialUnavailableError(message=NO_TOKEN.format(account.get("username")))

    def _get_auth_client(self, **kwargs):
        # type: (**Any) -> AadClientBase
        return AadClient(client_id=DEVELOPER_SIGN_ON_CLIENT_ID, **kwargs)
