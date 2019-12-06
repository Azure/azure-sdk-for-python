# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import abc
import copy
import functools
import time

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

from msal import TokenCache
from msal.oauth2cli.oauth2 import Client

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
from .._constants import KnownAuthorities

try:
    ABC = abc.ABC
except AttributeError:  # Python 2.7, abc exists, but not ABC
    ABC = abc.ABCMeta("ABC", (object,), {"__slots__": ()})  # type: ignore

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, Callable, Iterable, Optional


class AadClientBase(ABC):
    """Sans I/O methods for AAD clients wrapping MSAL's OAuth client"""

    def __init__(self, tenant_id, client_id, cache=None, **kwargs):
        # type: (str, str, Optional[TokenCache], **Any) -> None
        authority = kwargs.pop("authority", KnownAuthorities.AZURE_PUBLIC_CLOUD)
        if authority[-1] == "/":
            authority = authority[:-1]
        token_endpoint = "https://" + "/".join((authority, tenant_id, "oauth2/v2.0/token"))
        config = {"token_endpoint": token_endpoint}

        self._cache = cache or TokenCache()

        self._client = Client(server_configuration=config, client_id=client_id)
        self._client.session.close()
        self._client.session = self._get_client_session(**kwargs)

    def get_cached_access_token(self, scopes):
        # type: (Iterable[str]) -> Optional[AccessToken]
        tokens = self._cache.find(TokenCache.CredentialType.ACCESS_TOKEN, target=list(scopes))
        for token in tokens:
            expires_on = int(token["expires_on"])
            if expires_on - 300 > int(time.time()):
                return AccessToken(token["secret"], expires_on)
        return None

    def get_cached_refresh_tokens(self, scopes):
        """Assumes all cached refresh tokens belong to the same user"""
        return self._cache.find(TokenCache.CredentialType.REFRESH_TOKEN, target=list(scopes))

    def obtain_token_by_authorization_code(self, code, redirect_uri, scopes, **kwargs):
        # type: (str, str, Iterable[str], **Any) -> AccessToken
        fn = functools.partial(
            self._client.obtain_token_by_authorization_code, code=code, redirect_uri=redirect_uri, **kwargs
        )
        return self._obtain_token(scopes, fn, **kwargs)

    def obtain_token_by_refresh_token(self, refresh_token, scopes, **kwargs):
        # type: (str, Iterable[str], **Any) -> AccessToken
        fn = functools.partial(
            self._client.obtain_token_by_refresh_token,
            token_item=refresh_token,
            scope=scopes,
            rt_getter=lambda token: token["secret"],
            **kwargs
        )
        return self._obtain_token(scopes, fn, **kwargs)

    def _process_response(self, response, scopes, now):
        # type: (dict, Iterable[str], int) -> AccessToken
        _raise_for_error(response)

        # TokenCache.add mutates the response. In particular, it removes tokens.
        response_copy = copy.deepcopy(response)

        self._cache.add(event={"response": response, "scope": scopes}, now=now)
        if "expires_on" in response_copy:
            expires_on = int(response_copy["expires_on"])
        elif "expires_in" in response_copy:
            expires_on = now + int(response_copy["expires_in"])
        else:
            _scrub_secrets(response_copy)
            raise ClientAuthenticationError(
                message="Unexpected response from Azure Active Directory: {}".format(response_copy)
            )
        return AccessToken(response_copy["access_token"], expires_on)

    @abc.abstractmethod
    def _get_client_session(self, **kwargs):
        pass

    @abc.abstractmethod
    def _obtain_token(self, scopes, fn, **kwargs):
        # type: (Iterable[str], Callable, **Any) -> AccessToken
        pass


def _scrub_secrets(response):
    for secret in ("access_token", "refresh_token"):
        if secret in response:
            response[secret] = "***"


def _raise_for_error(response):
    # type: (dict) -> None
    if "error" not in response:
        return

    _scrub_secrets(response)
    if "error_description" in response:
        message = "Azure Active Directory error '({}) {}'".format(response["error"], response["error_description"])
    else:
        message = "Azure Active Directory error '{}'".format(response)
    raise ClientAuthenticationError(message=message)
