# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Demonstrates custom credential implementations using existing access tokens and an MSAL client"""

import time
from typing import Optional, Union

import msal

from azure.core.credentials import AccessToken
from azure.identity import AuthenticationRequiredError, AzureAuthorityHosts


class StaticTokenCredential(object):
    """Authenticates with a previously-acquired access token

    Note that an access token is valid only for certain resources and eventually expires. This credential is therefore
    quite limited. An application using it must ensure the token is valid and contains all claims required by any
    service client given an instance of this credential.
    """

    def __init__(self, access_token: Union[str, AccessToken]) -> None:
        if isinstance(access_token, AccessToken):
            self._token = access_token
        else:
            # setting expires_on in the past causes Azure SDK clients to call get_token every time they need a token
            self._token = AccessToken(token=access_token, expires_on=0)

    def get_token(
        self, *scopes: str, claims: Optional[str] = None, tenant_id: Optional[str] = None, **kwargs
    ) -> AccessToken:
        """Get an access token for the requested scopes.

        :param str scopes: desired scopes for the access token.
        :keyword str claims: additional claims required in the token request.
        :keyword str tenant_id: optional tenant to include in the token request.
        :return: An access token with the requested scopes.
        :rtype: ~azure.core.credentials.AccessToken
        """

        return self._token


class MsalTokenCredential(object):
    """Uses an MSAL client directly to obtain access tokens with an interactive flow."""

    def __init__(self, tenant_id: str, client_id: str) -> None:
        self._app = msal.PublicClientApplication(
            client_id=client_id, authority="https://{}/{}".format(AzureAuthorityHosts.AZURE_PUBLIC_CLOUD, tenant_id)
        )

    def get_token(
        self, *scopes: str, claims: Optional[str] = None, tenant_id: Optional[str] = None, **kwargs
    ) -> AccessToken:
        """Get an access token for the requested scopes.

        :param str scopes: desired scopes for the access token.
        :keyword str claims: additional claims required in the token request.
        :keyword str tenant_id: optional tenant to include in the token request.
        :return: An access token with the requested scopes.
        :rtype: ~azure.core.credentials.AccessToken
        """

        now = int(time.time())
        result = self._app.acquire_token_interactive(list(scopes), claims=claims, tenant_id=tenant_id, **kwargs)

        try:
            return AccessToken(result["access_token"], now + int(result["expires_in"]))
        except Exception as ex:
            print("\nFailed to get a valid access token")
            raise AuthenticationRequiredError(scopes) from ex
