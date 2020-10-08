# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Demonstrates custom credential implementation"""

import time
from typing import TYPE_CHECKING

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
from azure.identity import AzureAuthorityHosts
import msal

if TYPE_CHECKING:
    from typing import Any, Union


class StaticTokenCredential(object):
    """Authenticates with a previously acquired access token

    Note that an access token is valid only for certain resources and eventually expires. This credential is therefore
    quite limited. An application using it must ensure the token is valid and contains all claims required by any
    service client given an instance of this credential.
    """
    def __init__(self, access_token):
        # type: (Union[str, AccessToken]) -> None
        if isinstance(access_token, AccessToken):
            self._token = access_token
        else:
            # setting expires_on in the past causes Azure SDK clients to call get_token every time they need a token
            self._token = AccessToken(token=access_token, expires_on=0)

    def get_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> AccessToken
        """get_token is the only method a credential must implement"""

        return self._token


class OnBehalfOfCredential(object):
    """Authenticates via the On-Behalf-Of flow using MSAL for Python

    A future version of azure-identity will include a credential supporting the On-Behalf-Of flow. Until then,
    applications needing to authenticate through that flow can use a custom credential like this one.
    """

    def __init__(self, tenant_id, client_id, client_secret, user_access_token):
        # type: (str, str, str, str) -> None
        self._confidential_client = msal.ConfidentialClientApplication(
            client_id=client_id,
            client_credential=client_secret,
            authority="https://{}/{}".format(AzureAuthorityHosts.AZURE_PUBLIC_CLOUD, tenant_id)
        )
        self._user_token = user_access_token

    def get_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> AccessToken
        """get_token is the only method a credential must implement"""

        now = int(time.time())
        result = self._confidential_client.acquire_token_on_behalf_of(
            user_assertion=self._user_token, scopes=list(scopes)
        )

        if result and "access_token" in result and "expires_in" in result:
            return AccessToken(result["access_token"], now + int(result["expires_in"]))

        raise ClientAuthenticationError(
            message="Authentication failed: {}".format(result.get("error_description") or result.get("error"))
        )
