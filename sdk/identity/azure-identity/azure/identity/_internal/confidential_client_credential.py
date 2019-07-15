# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""A credential which wraps an MSAL ConfidentialClientApplication and delegates token acquisition and caching to it.
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
import msal

from .msal_transport_adapter import MsalTransportAdapter


class ConfidentialClientCredential(MsalTransportAdapter):
    """Wraps an MSAL ConfidentialClientApplication with the TokenCredential API"""

    def __init__(self, client_id, client_credential, authority, **kwargs):
        # type: (str, str, Union[str, Mapping[str, str]], Any) -> None
        super(ConfidentialClientCredential, self).__init__(**kwargs)

        self._client_id = client_id
        self._client_credential = client_credential
        self._authority = authority

        # postpone creating the wrapped application because its initializer uses the network
        self._app = None  # type: Optional[msal.ConfidentialClientApplication]

    def get_token(self, *scopes):
        # type: (str) -> AccessToken

        if not self._app:
            self._app = self._create_msal_application()

        # MSAL requires scopes be a list
        scopes = list(scopes)  # type: ignore
        now = int(time.time())

        # First try to get a cached access token or if a refresh token is cached, redeem it for an access token.
        # Failing that, acquire a new token.
        result = self._app.acquire_token_silent(scopes, account=None) or self._app.acquire_token_for_client(scopes)
        return AccessToken(result["access_token"], now + int(result["expires_in"]))

    def _create_msal_application(self):
        # ConfidentialClientApplication's initializer uses msal.authority to send requests to AAD
        with mock.patch("msal.authority.requests", self):
            app = msal.ConfidentialClientApplication(
                client_id=self._client_id, client_credential=self._client_credential, authority=self._authority
            )
        # replace the client's requests.Session with adapter
        app.client.session = self
        return app
