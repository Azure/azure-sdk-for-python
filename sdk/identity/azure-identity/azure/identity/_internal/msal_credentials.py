# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Credentials wrapping MSAL applications and delegating token acquisition and caching to them.
This entails monkeypatching MSAL's OAuth client with an adapter substituting an azure-core pipeline for Requests.
"""

import time

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

try:
    from unittest import mock
except ImportError:  # python < 3.3
    import mock  # type: ignore

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, Mapping, Optional, Union

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
import msal

from .msal_transport_adapter import MsalTransportAdapter


class MsalCredential(object):
    """Base class for credentials wrapping MSAL applications"""

    def __init__(self, client_id, authority, app_class, client_credential=None, **kwargs):
        # type: (str, str, msal.ClientApplication, Optional[Union[str, Mapping[str, str]]], Any) -> None
        self._authority = authority
        self._client_credential = client_credential
        self._client_id = client_id

        self._adapter = kwargs.pop("msal_adapter", None) or MsalTransportAdapter(**kwargs)

        # postpone creating the wrapped application because its initializer uses the network
        self._app_class = app_class
        self._msal_app = None  # type: Optional[msal.ClientApplication]

    @property
    def _app(self):
        # type: () -> msal.ClientApplication
        """The wrapped MSAL application"""

        if not self._msal_app:
            # MSAL application initializers use msal.authority to send AAD tenant discovery requests
            with mock.patch("msal.authority.requests", self._adapter):
                app = self._app_class(
                    client_id=self._client_id, client_credential=self._client_credential, authority=self._authority
                )

            # monkeypatch the app to replace requests.Session with MsalTransportAdapter
            app.client.session = self._adapter
            self._msal_app = app

        return self._msal_app


class ConfidentialClientCredential(MsalCredential):
    """Wraps an MSAL ConfidentialClientApplication with the TokenCredential API"""

    def __init__(self, **kwargs):
        # type: (Any) -> None
        super(ConfidentialClientCredential, self).__init__(app_class=msal.ConfidentialClientApplication, **kwargs)

    def get_token(self, *scopes):
        # type: (str) -> AccessToken

        # MSAL requires scopes be a list
        scopes = list(scopes)  # type: ignore
        now = int(time.time())

        # First try to get a cached access token or if a refresh token is cached, redeem it for an access token.
        # Failing that, acquire a new token.
        app = self._app  # type: msal.ConfidentialClientApplication
        result = app.acquire_token_silent(scopes, account=None) or app.acquire_token_for_client(scopes)

        if "access_token" not in result:
            raise ClientAuthenticationError(message="authentication failed: {}".format(result.get("error_description")))

        return AccessToken(result["access_token"], now + int(result["expires_in"]))
