# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Credentials wrapping MSAL applications and delegating token acquisition and caching to them.
This entails monkeypatching MSAL's OAuth client with an adapter substituting an azure-core pipeline for Requests.
"""
import abc
import time

import msal
from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError

from .exception_wrapper import wrap_exceptions
from .msal_transport_adapter import MsalTransportAdapter
from .._constants import KnownAuthorities

try:
    ABC = abc.ABC
except AttributeError:  # Python 2.7, abc exists, but not ABC
    ABC = abc.ABCMeta("ABC", (object,), {"__slots__": ()})  # type: ignore

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, Mapping, Optional, Type, Union


class MsalCredential(ABC):
    """Base class for credentials wrapping MSAL applications"""

    def __init__(self, client_id, client_credential=None, **kwargs):
        # type: (str, Optional[Union[str, Mapping[str, str]]], **Any) -> None
        tenant_id = kwargs.pop("tenant_id", "organizations")
        authority = kwargs.pop("authority", KnownAuthorities.AZURE_PUBLIC_CLOUD)
        self._base_url = "https://" + "/".join((authority.strip("/"), tenant_id.strip("/")))
        self._client_credential = client_credential
        self._client_id = client_id

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
            app = cls(client_id=self._client_id, client_credential=self._client_credential, authority=self._base_url)

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
