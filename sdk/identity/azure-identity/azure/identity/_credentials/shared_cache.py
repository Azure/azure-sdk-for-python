# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import sys

from azure.core.exceptions import ClientAuthenticationError

from .._authn_client import AuthnClient
from .._internal import wrap_exceptions

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, Optional
    import msal_extensions
    from azure.core.credentials import AccessToken
    from .._authn_client import AuthnClientBase


class SharedTokenCacheCredential(object):
    """Authenticates using tokens in the local cache shared between Microsoft applications.

    :param str username:
        Username (typically an email address) of the user to authenticate as. This is used when the local cache
        contains tokens for multiple identities.

    :keyword str authority: Authority of an Azure Active Directory endpoint, for example 'login.microsoftonline.com',
        the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.KnownAuthorities`
        defines authorities for other clouds.
    :keyword str tenant_id: an Azure Active Directory tenant ID. Used to select an account when the cache contains
        tokens for multiple identities.
    """

    def __init__(self, username=None, **kwargs):  # pylint:disable=unused-argument
        # type: (Optional[str], **Any) -> None

        self._username = username
        self._tenant_id = kwargs.pop("tenant_id", None)

        cache = kwargs.pop("_cache", None)  # for ease of testing

        if not cache and sys.platform.startswith("win") and "LOCALAPPDATA" in os.environ:
            from msal_extensions.token_cache import WindowsTokenCache

            cache = WindowsTokenCache(cache_location=os.environ["LOCALAPPDATA"] + "/.IdentityService/msal.cache")

            # prevent writing to the shared cache
            # TODO: seperating deserializing access tokens from caching them would make this cleaner
            cache.add = lambda *_: None

        if cache:
            self._client = self._get_auth_client(cache=cache, **kwargs)  # type: Optional[AuthnClientBase]
        else:
            self._client = None

    @wrap_exceptions
    def get_token(self, *scopes, **kwargs):  # pylint:disable=unused-argument
        # type (*str, **Any) -> AccessToken
        """Get an access token for `scopes` from the shared cache.

        If no access token is cached, attempt to acquire one using a cached refresh token.

        .. note:: This method is called by Azure SDK clients. It isn't intended for use in application code.

        :param str scopes: desired scopes for the token
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises:
            :class:`azure.core.exceptions.ClientAuthenticationError` when the cache is unavailable or no access token
            can be acquired from it
        """

        if not self._client:
            raise ClientAuthenticationError(message="Shared token cache unavailable")

        return self._client.obtain_token_by_refresh_token(scopes, self._username, self._tenant_id)

    @staticmethod
    def supported():
        # type: () -> bool
        """Whether the shared token cache is supported on the current platform.

        :rtype: bool
        """
        return sys.platform.startswith("win")

    @staticmethod
    def _get_auth_client(**kwargs):
        # type: (msal_extensions.FileTokenCache) -> AuthnClientBase
        return AuthnClient(tenant="common", **kwargs)
