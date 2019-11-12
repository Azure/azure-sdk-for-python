# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime
import os
import sys
import time

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError

from .._authn_client import AuthnClient
from .._internal import PublicClientCredential, wrap_exceptions

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, Callable, Optional
    import msal_extensions
    from .._authn_client import AuthnClientBase


class DeviceCodeCredential(PublicClientCredential):
    """Authenticates users through the device code flow.

    When :func:`get_token` is called, this credential acquires a verification URL and code from Azure Active Directory.
    A user must browse to the URL, enter the code, and authenticate with Azure Active Directory. If the user
    authenticates successfully, the credential receives an access token.

    This credential doesn't cache tokens--each :func:`get_token` call begins a new authentication flow.

    For more information about the device code flow, see Azure Active Directory documentation:
    https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-device-code

    :param str client_id: the application's ID

    :keyword str authority: Authority of an Azure Active Directory endpoint, for example 'login.microsoftonline.com',
          the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.KnownAuthorities`
          defines authorities for other clouds.
    :keyword str tenant_id: an Azure Active Directory tenant ID. Defaults to the 'organizations' tenant, which can
          authenticate work or school accounts. **Required for single-tenant applications.**
    :keyword int timeout: seconds to wait for the user to authenticate. Defaults to the validity period of the
          device code as set by Azure Active Directory, which also prevails when ``timeout`` is longer.
    :keyword prompt_callback: A callback enabling control of how authentication
          instructions are presented. Must accept arguments (``verification_uri``, ``user_code``, ``expires_on``):

            - ``verification_uri`` (str) the URL the user must visit
            - ``user_code`` (str) the code the user must enter there
            - ``expires_on`` (datetime.datetime) the UTC time at which the code will expire
          If this argument isn't provided, the credential will print instructions to stdout.
    :paramtype prompt_callback: Callable[str, str, ~datetime.datetime]
    """

    def __init__(self, client_id, **kwargs):
        # type: (str, **Any) -> None
        self._timeout = kwargs.pop("timeout", None)  # type: Optional[int]
        self._prompt_callback = kwargs.pop("prompt_callback", None)
        super(DeviceCodeCredential, self).__init__(client_id=client_id, **kwargs)

    @wrap_exceptions
    def get_token(self, *scopes, **kwargs):  # pylint:disable=unused-argument
        # type: (*str, **Any) -> AccessToken
        """Request an access token for `scopes`.

        This credential won't cache the token. Each call begins a new authentication flow.

        .. note:: This method is called by Azure SDK clients. It isn't intended for use in application code.

        :param str scopes: desired scopes for the token
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises ~azure.core.exceptions.ClientAuthenticationError:
        """

        # MSAL requires scopes be a list
        scopes = list(scopes)  # type: ignore
        now = int(time.time())

        app = self._get_app()
        flow = app.initiate_device_flow(scopes)
        if "error" in flow:
            raise ClientAuthenticationError(
                message="Couldn't begin authentication: {}".format(flow.get("error_description") or flow.get("error"))
            )

        if self._prompt_callback:
            self._prompt_callback(
                flow["verification_uri"], flow["user_code"], datetime.utcfromtimestamp(flow["expires_at"])
            )
        else:
            print(flow["message"])

        if self._timeout is not None and self._timeout < flow["expires_in"]:
            # user specified an effective timeout we will observe
            deadline = now + self._timeout
            result = app.acquire_token_by_device_flow(flow, exit_condition=lambda flow: time.time() > deadline)
        else:
            # MSAL will stop polling when the device code expires
            result = app.acquire_token_by_device_flow(flow)

        if "access_token" not in result:
            if result.get("error") == "authorization_pending":
                message = "Timed out waiting for user to authenticate"
            else:
                message = "Authentication failed: {}".format(result.get("error_description") or result.get("error"))
            raise ClientAuthenticationError(message=message)

        token = AccessToken(result["access_token"], now + int(result["expires_in"]))
        return token


class SharedTokenCacheCredential(object):
    """Authenticates using tokens in the local cache shared between Microsoft applications.

    :param str username:
        Username (typically an email address) of the user to authenticate as. This is required because the local cache
        may contain tokens for multiple identities.

    :keyword str authority: Authority of an Azure Active Directory endpoint, for example 'login.microsoftonline.com',
          the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.KnownAuthorities`
          defines authorities for other clouds.
    """

    def __init__(self, username=None, **kwargs):  # pylint:disable=unused-argument
        # type: (Optional[str], **Any) -> None

        self._username = username

        cache = None

        if sys.platform.startswith("win") and "LOCALAPPDATA" in os.environ:
            from msal_extensions.token_cache import WindowsTokenCache

            cache = WindowsTokenCache(
                cache_location=os.path.join(os.environ["LOCALAPPDATA"], ".IdentityService", "msal.cache")
            )

            # prevent writing to the shared cache
            # TODO: seperating deserializing access tokens from caching them would make this cleaner
            cache.add = lambda *_: None

        if cache:
            self._client = self._get_auth_client(cache)  # type: Optional[AuthnClientBase]
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

        return self._client.obtain_token_by_refresh_token(scopes, self._username)

    @staticmethod
    def supported():
        # type: () -> bool
        """Whether the shared token cache is supported on the current platform.

        :rtype: bool
        """
        return sys.platform.startswith("win")

    @staticmethod
    def _get_auth_client(cache):
        # type: (msal_extensions.FileTokenCache) -> AuthnClientBase
        return AuthnClient(tenant="common", cache=cache)


class UsernamePasswordCredential(PublicClientCredential):
    """Authenticates a user with a username and password.

    In general, Microsoft doesn't recommend this kind of authentication, because it's less secure than other
    authentication flows.

    Authentication with this credential is not interactive, so it is **not compatible with any form of
    multi-factor authentication or consent prompting**. The application must already have consent from the user or
    a directory admin.

    This credential can only authenticate work and school accounts; Microsoft accounts are not supported.
    See this document for more information about account types:
    https://docs.microsoft.com/en-us/azure/active-directory/fundamentals/sign-up-organization

    :param str client_id: the application's client ID
    :param str username: the user's username (usually an email address)
    :param str password: the user's password

    :keyword str authority: Authority of an Azure Active Directory endpoint, for example 'login.microsoftonline.com',
          the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.KnownAuthorities`
          defines authorities for other clouds.
    :keyword str tenant_id: tenant ID or a domain associated with a tenant. If not provided, defaults to the
          'organizations' tenant, which supports only Azure Active Directory work or school accounts.
    """

    def __init__(self, client_id, username, password, **kwargs):
        # type: (str, str, str, Any) -> None
        super(UsernamePasswordCredential, self).__init__(client_id=client_id, **kwargs)
        self._username = username
        self._password = password

    @wrap_exceptions
    def get_token(self, *scopes, **kwargs):  # pylint:disable=unused-argument
        # type: (*str, **Any) -> AccessToken
        """Request an access token for `scopes`.

        .. note:: This method is called by Azure SDK clients. It isn't intended for use in application code.

        :param str scopes: desired scopes for the token
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises ~azure.core.exceptions.ClientAuthenticationError:
        """

        # MSAL requires scopes be a list
        scopes = list(scopes)  # type: ignore
        now = int(time.time())

        app = self._get_app()
        accounts = app.get_accounts(username=self._username)
        result = None
        for account in accounts:
            result = app.acquire_token_silent(scopes, account=account)
            if result:
                break

        if not result:
            # cache miss -> request a new token
            with self._adapter:
                result = app.acquire_token_by_username_password(
                    username=self._username, password=self._password, scopes=scopes
                )

        if "access_token" not in result:
            raise ClientAuthenticationError(message="authentication failed: {}".format(result.get("error_description")))

        return AccessToken(result["access_token"], now + int(result["expires_in"]))
