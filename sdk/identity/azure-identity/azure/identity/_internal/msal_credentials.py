# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Credentials wrapping MSAL applications and delegating token acquisition and caching to them.
This entails monkeypatching MSAL's OAuth client with an adapter substituting an azure-core pipeline for Requests.
"""
import abc
import base64
import json
import logging
import os
import sys
import time

import msal
from six.moves.urllib_parse import urlparse
from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError

from .exception_wrapper import wrap_exceptions
from .msal_transport_adapter import MsalTransportAdapter
from .._constants import KnownAuthorities
from .._exceptions import AuthenticationRequiredError, CredentialUnavailableError
from .._internal import get_default_authority, normalize_authority
from .._auth_record import AuthenticationRecord

try:
    ABC = abc.ABC
except AttributeError:  # Python 2.7, abc exists, but not ABC
    ABC = abc.ABCMeta("ABC", (object,), {"__slots__": ()})  # type: ignore

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=ungrouped-imports,unused-import
    from typing import Any, Mapping, Optional, Type, Union


_LOGGER = logging.getLogger(__name__)

_DEFAULT_AUTHENTICATE_SCOPES = {
    "https://" + KnownAuthorities.AZURE_CHINA: ("https://management.core.chinacloudapi.cn//.default",),
    "https://" + KnownAuthorities.AZURE_GERMANY: ("https://management.core.cloudapi.de//.default",),
    "https://" + KnownAuthorities.AZURE_GOVERNMENT: ("https://management.core.usgovcloudapi.net//.default",),
    "https://" + KnownAuthorities.AZURE_PUBLIC_CLOUD: ("https://management.core.windows.net//.default",),
}


def _decode_client_info(raw):
    """Taken from msal.oauth2cli.oidc"""

    raw += "=" * (-len(raw) % 4)
    raw = str(raw)  # On Python 2.7, argument of urlsafe_b64decode must be str, not unicode.
    return base64.urlsafe_b64decode(raw).decode("utf-8")


def _build_auth_record(response):
    """Build an AuthenticationRecord from the result of an MSAL ClientApplication token request"""

    try:
        client_info = json.loads(_decode_client_info(response["client_info"]))
        id_token = response["id_token_claims"]

        return AuthenticationRecord(
            authority=urlparse(id_token["iss"]).netloc,  # "iss" is the URL of the issuing tenant
            client_id=id_token["aud"],
            home_account_id="{uid}.{utid}".format(**client_info),
            tenant_id=id_token["tid"],  # tenant which issued the token, not necessarily user's home tenant
            username=id_token["preferred_username"],
        )
    except (KeyError, ValueError):
        # surprising: msal.ClientApplication always requests client_info and an id token, whose shapes shouldn't change
        return None


def _load_persistent_cache():
    # type: () -> msal.TokenCache

    if sys.platform.startswith("win") and "LOCALAPPDATA" in os.environ:
        from msal_extensions.token_cache import WindowsTokenCache

        return WindowsTokenCache(
            cache_location=os.path.join(os.environ["LOCALAPPDATA"], ".IdentityService", "msal.cache")
        )

    raise NotImplementedError("A persistent cache is not available on this platform.")


class MsalCredential(ABC):
    """Base class for credentials wrapping MSAL applications"""

    def __init__(self, client_id, client_credential=None, **kwargs):
        # type: (str, Optional[Union[str, Mapping[str, str]]], **Any) -> None
        authority = kwargs.pop("authority", None)
        self._authority = normalize_authority(authority) if authority else get_default_authority()
        self._tenant_id = kwargs.pop("tenant_id", None) or "organizations"

        self._client_credential = client_credential
        self._client_id = client_id

        self._cache = kwargs.pop("_cache", None)  # internal, for use in tests
        if not self._cache:
            if kwargs.pop("enable_persistent_cache", False):
                self._cache = _load_persistent_cache()
            else:
                self._cache = msal.TokenCache()

        self._adapter = kwargs.pop("msal_adapter", None) or MsalTransportAdapter(**kwargs)

        # postpone creating the wrapped application because its initializer uses the network
        self._msal_app = None  # type: Optional[msal.ClientApplication]

    @abc.abstractmethod
    def get_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> AccessToken
        pass

    @abc.abstractmethod
    def _get_app(self):
        # type: () -> msal.ClientApplication
        pass

    def _create_app(self, cls):
        # type: (Type[msal.ClientApplication]) -> msal.ClientApplication
        """Creates an MSAL application, patching msal.authority to use an azure-core pipeline during tenant discovery"""

        # MSAL application initializers use msal.authority to send AAD tenant discovery requests
        with self._adapter:
            # MSAL's "authority" is a URL e.g. https://login.microsoftonline.com/common
            app = cls(
                client_id=self._client_id,
                client_credential=self._client_credential,
                authority="{}/{}".format(self._authority, self._tenant_id),
                token_cache=self._cache,
            )

        # monkeypatch the app to replace requests.Session with MsalTransportAdapter
        app.client.session.close()
        app.client.session = self._adapter

        return app


class ConfidentialClientCredential(MsalCredential):
    """Wraps an MSAL ConfidentialClientApplication with the TokenCredential API"""

    @wrap_exceptions
    def get_token(self, *scopes, **kwargs):  # pylint:disable=unused-argument
        # type: (*str, **Any) -> AccessToken

        # MSAL requires scopes be a list
        scopes = list(scopes)  # type: ignore
        now = int(time.time())

        # First try to get a cached access token or if a refresh token is cached, redeem it for an access token.
        # Failing that, acquire a new token.
        app = self._get_app()
        result = app.acquire_token_silent(scopes, account=None) or app.acquire_token_for_client(scopes)

        if "access_token" not in result:
            raise ClientAuthenticationError(message="authentication failed: {}".format(result.get("error_description")))

        return AccessToken(result["access_token"], now + int(result["expires_in"]))

    def _get_app(self):
        # type: () -> msal.ConfidentialClientApplication
        if not self._msal_app:
            self._msal_app = self._create_app(msal.ConfidentialClientApplication)
        return self._msal_app


class PublicClientCredential(MsalCredential):
    """Wraps an MSAL PublicClientApplication with the TokenCredential API"""

    @abc.abstractmethod
    def get_token(self, *scopes, **kwargs):  # pylint:disable=unused-argument
        # type: (*str, **Any) -> AccessToken
        pass

    def _get_app(self):
        # type: () -> msal.PublicClientApplication
        if not self._msal_app:
            self._msal_app = self._create_app(msal.PublicClientApplication)
        return self._msal_app


class InteractiveCredential(PublicClientCredential):
    def __init__(self, **kwargs):
        self._disable_automatic_authentication = kwargs.pop("disable_automatic_authentication", False)
        self._auth_record = kwargs.pop("authentication_record", None)  # type: Optional[AuthenticationRecord]
        if self._auth_record:
            kwargs.pop("client_id", None)  # authentication_record overrides client_id argument
            tenant_id = kwargs.pop("tenant_id", None) or self._auth_record.tenant_id
            super(InteractiveCredential, self).__init__(
                client_id=self._auth_record.client_id,
                authority=self._auth_record.authority,
                tenant_id=tenant_id,
                **kwargs
            )
        else:
            super(InteractiveCredential, self).__init__(**kwargs)

    def get_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> AccessToken
        """Request an access token for `scopes`.

        .. note:: This method is called by Azure SDK clients. It isn't intended for use in application code.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises CredentialUnavailableError: the credential is unable to attempt authentication because it lacks
          required data, state, or platform support
        :raises ~azure.core.exceptions.ClientAuthenticationError: authentication failed. The error's ``message``
          attribute gives a reason.
        :raises AuthenticationRequiredError: user interaction is necessary to acquire a token, and the credential is
          configured not to begin this automatically. Call :func:`authenticate` to begin interactive authentication.
        """
        if not scopes:
            raise ValueError("'get_token' requires at least one scope")

        allow_prompt = kwargs.pop("_allow_prompt", not self._disable_automatic_authentication)
        try:
            return self._acquire_token_silent(*scopes, **kwargs)
        except AuthenticationRequiredError:
            if not allow_prompt:
                raise

        # silent authentication failed -> authenticate interactively
        now = int(time.time())

        result = self._request_token(*scopes, **kwargs)
        if "access_token" not in result:
            message = "Authentication failed: {}".format(result.get("error_description") or result.get("error"))
            raise ClientAuthenticationError(message=message)

        # this may be the first authentication, or the user may have authenticated a different identity
        self._auth_record = _build_auth_record(result)

        return AccessToken(result["access_token"], now + int(result["expires_in"]))

    def authenticate(self, **kwargs):
        # type: (**Any) -> AuthenticationRecord
        """Interactively authenticate a user.

        :keyword Sequence[str] scopes: scopes to request during authentication, such as those provided by
          :func:`AuthenticationRequiredError.scopes`. If provided, successful authentication will cache an access token
          for these scopes.
        :rtype: ~azure.identity.AuthenticationRecord
        :raises ~azure.core.exceptions.ClientAuthenticationError: authentication failed. The error's ``message``
          attribute gives a reason.
        """

        scopes = kwargs.pop("scopes", None)
        if not scopes:
            if self._authority not in _DEFAULT_AUTHENTICATE_SCOPES:
                # the credential is configured to use a cloud whose ARM scope we can't determine
                raise CredentialUnavailableError(
                    message="Authenticating in this environment requires a value for the 'scopes' keyword argument."
                )

            scopes = _DEFAULT_AUTHENTICATE_SCOPES[self._authority]

        _ = self.get_token(*scopes, _allow_prompt=True, **kwargs)
        return self.authentication_record  # type: ignore

    @property
    def authentication_record(self):
        # type: () -> Optional[AuthenticationRecord]
        """:class:`~azure.identity.AuthenticationRecord` for the most recent authentication"""
        return self._auth_record

    @wrap_exceptions
    def _acquire_token_silent(self, *scopes, **kwargs):
        # type: (*str, **Any) -> AccessToken
        result = None
        if self._auth_record:
            app = self._get_app()
            for account in app.get_accounts(username=self._auth_record.username):
                if account.get("home_account_id") != self._auth_record.home_account_id:
                    continue

                now = int(time.time())
                result = app.acquire_token_silent_with_error(list(scopes), account=account, **kwargs)
                if result and "access_token" in result and "expires_in" in result:
                    return AccessToken(result["access_token"], now + int(result["expires_in"]))

        # if we get this far, result is either None or the content of an AAD error response
        if result:
            details = result.get("error_description") or result.get("error")
            raise AuthenticationRequiredError(scopes, error_details=details)
        raise AuthenticationRequiredError(scopes)

    @abc.abstractmethod
    def _request_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> dict
        """Request an access token via a non-silent MSAL token acquisition method, returning that method's result"""
