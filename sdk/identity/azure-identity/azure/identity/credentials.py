# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core import Configuration

from .authn_client import AuthnClient
from .exceptions import AuthenticationError

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, Dict, Iterable, Mapping, Optional
    from azure.core.pipeline.policies import HTTPPolicy
    from azure.core.credentials import SupportsGetToken

# pylint:disable=too-few-public-methods


class _ClientCredentialBase(object):
    _OAUTH_ENDPOINT = "https://login.microsoftonline.com/{}/oauth2/v2.0/token"

    def __init__(self, client_id, tenant_id, config=None, policies=None, **kwargs):
        # type: (str, str, Optional[Configuration], Optional[Iterable[HTTPPolicy]], Mapping[str, Any]) -> None
        if not client_id:
            raise ValueError("client_id")
        if not tenant_id:
            raise ValueError("tenant_id")
        self._client = AuthnClient(self._OAUTH_ENDPOINT.format(tenant_id), config, policies, **kwargs)
        self._form_data = {}  # type: Dict[str, str]

    def get_token(self, scopes):
        # type: (Iterable[str]) -> str
        data = self._form_data.copy()
        data["scope"] = " ".join(scopes)
        token = self._client.get_cached_token(scopes)
        if not token:
            return self._client.request_token(scopes, form_data=data)
        return token


class ClientSecretCredential(_ClientCredentialBase):
    def __init__(self, client_id, secret, tenant_id, config=None, **kwargs):
        # type: (str, str, str, Optional[Configuration], Mapping[str, Any]) -> None
        if not secret:
            raise ValueError("secret")
        super(ClientSecretCredential, self).__init__(client_id, tenant_id, config, **kwargs)
        self._form_data = {"client_id": client_id, "client_secret": secret, "grant_type": "client_credentials"}


class TokenCredentialChain:
    """A sequence of token credentials"""

    def __init__(self, credentials):
        # type: (Iterable[SupportsGetToken]) -> None
        if not credentials:
            raise ValueError("at least one credential is required")
        self._credentials = credentials

    def get_token(self, scopes):
        # type: (Iterable[str]) -> str
        """Attempts to get a token from each credential, in order, returning the first token.
           If no token is acquired, raises an exception listing error messages.
        """
        history = []
        for credential in self._credentials:
            try:
                return credential.get_token(scopes)
            except AuthenticationError as ex:
                history.append((credential, ex.message))
            except Exception as ex:  # pylint: disable=broad-except
                history.append((credential, str(ex)))
        error_message = self._get_error_message(history)
        raise AuthenticationError(error_message)

    @staticmethod
    def _get_error_message(history):
        attempts = []
        for credential, error in history:
            if error:
                attempts.append("{}: {}".format(credential.__class__.__name__, error))
            else:
                attempts.append(credential.__class__.__name__)
        return "No valid token received. {}".format(". ".join(attempts))
