# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import abc
import base64
import json
import logging
import time

import msal
from six.moves.urllib_parse import urlparse
from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError

from .msal_client import MsalClient
from .persistent_cache import load_user_cache
from .._constants import KnownAuthorities
from .._exceptions import AuthenticationRequiredError, CredentialUnavailableError
from .._internal import get_default_authority, normalize_authority, wrap_exceptions
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
        id_token = response["id_token_claims"]

        if "client_info" in response:
            client_info = json.loads(_decode_client_info(response["client_info"]))
            home_account_id = "{uid}.{utid}".format(**client_info)
        else:
            # MSAL uses the subject claim as home_account_id when the STS doesn't provide client_info
            home_account_id = id_token["sub"]

        return AuthenticationRecord(
            authority=urlparse(id_token["iss"]).netloc,  # "iss" is the URL of the issuing tenant
            client_id=id_token["aud"],
            home_account_id=home_account_id,
            tenant_id=id_token["tid"],  # tenant which issued the token, not necessarily user's home tenant
            username=id_token["preferred_username"],
        )
    except (KeyError, ValueError):
        # surprising: msal.ClientApplication always requests an id token, whose shape shouldn't change
        return None


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
                allow_unencrypted = kwargs.pop("allow_unencrypted_cache", False)
                self._cache = load_user_cache(allow_unencrypted)
            else:
                self._cache = msal.TokenCache()

        self._client = MsalClient(**kwargs)

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
        app = cls(
            client_id=self._client_id,
            client_credential=self._client_credential,
            authority="{}/{}".format(self._authority, self._tenant_id),
            token_cache=self._cache,
            http_client=self._client,
        )

        return app


class InteractiveCredential(MsalCredential):
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
            message = "'get_token' requires at least one scope"
            _LOGGER.warning("%s.get_token failed: %s", self.__class__.__name__, message)
            raise ValueError(message)

        allow_prompt = kwargs.pop("_allow_prompt", not self._disable_automatic_authentication)
        try:
            token = self._acquire_token_silent(*scopes, **kwargs)
            _LOGGER.info("%s.get_token succeeded", self.__class__.__name__)
            return token
        except Exception as ex:  # pylint:disable=broad-except
            if not (isinstance(ex, AuthenticationRequiredError) and allow_prompt):
                _LOGGER.warning(
                    "%s.get_token failed: %s",
                    self.__class__.__name__,
                    ex,
                    exc_info=_LOGGER.isEnabledFor(logging.DEBUG),
                )
                raise

        # silent authentication failed -> authenticate interactively
        now = int(time.time())

        try:
            result = self._request_token(*scopes, **kwargs)
            if "access_token" not in result:
                message = "Authentication failed: {}".format(result.get("error_description") or result.get("error"))
                raise ClientAuthenticationError(message=message)

            # this may be the first authentication, or the user may have authenticated a different identity
            self._auth_record = _build_auth_record(result)
        except Exception as ex:  # pylint:disable=broad-except
            _LOGGER.warning(
                "%s.get_token failed: %s", self.__class__.__name__, ex, exc_info=_LOGGER.isEnabledFor(logging.DEBUG),
            )
            raise

        _LOGGER.info("%s.get_token succeeded", self.__class__.__name__)
        return AccessToken(result["access_token"], now + int(result["expires_in"]))

    def authenticate(self, **kwargs):
        # type: (**Any) -> AuthenticationRecord
        """Interactively authenticate a user.

        :keyword Iterable[str] scopes: scopes to request during authentication, such as those provided by
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
        return self._auth_record  # type: ignore

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

    def _get_app(self):
        # type: () -> msal.PublicClientApplication
        if not self._msal_app:
            self._msal_app = self._create_app(msal.PublicClientApplication)
        return self._msal_app
