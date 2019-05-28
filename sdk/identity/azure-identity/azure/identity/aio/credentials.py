# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any, Dict, Iterable, Mapping, Optional

from azure.core import Configuration
from azure.core.pipeline.policies import HTTPPolicy

from .authn_client import AsyncAuthnClient
from ..credentials import TokenCredentialChain
from ..exceptions import AuthenticationError


# pylint:disable=too-few-public-methods

# TODO: could share more code with sync
class _AsyncClientCredentialBase(object):
    _OAUTH_ENDPOINT = "https://login.microsoftonline.com/{}/oauth2/v2.0/token"

    def __init__(
        self,
        client_id: str,
        tenant_id: str,
        config: Optional[Configuration] = None,
        policies: Optional[Iterable[HTTPPolicy]] = None,
        **kwargs: Mapping[str, Any]
    ) -> None:
        if not client_id:
            raise ValueError("client_id")
        if not tenant_id:
            raise ValueError("tenant_id")
        self._client = AsyncAuthnClient(self._OAUTH_ENDPOINT.format(tenant_id), config, policies, **kwargs)
        self._form_data = {}  # type: Dict[str, str]

    async def get_token(self, scopes: Iterable[str]) -> str:
        data = self._form_data.copy()
        data["scope"] = " ".join(scopes)
        token = self._client.get_cached_token(scopes)
        if not token:
            token = await self._client.request_token(scopes, form_data=data)
        return token  # type: ignore


class AsyncClientSecretCredential(_AsyncClientCredentialBase):
    def __init__(
        self,
        client_id: str,
        secret: str,
        tenant_id: str,
        config: Optional[Configuration] = None,
        **kwargs: Mapping[str, Any]
    ) -> None:
        if not secret:
            raise ValueError("secret")
        super(AsyncClientSecretCredential, self).__init__(client_id, tenant_id, config, **kwargs)
        self._form_data = {"client_id": client_id, "client_secret": secret, "grant_type": "client_credentials"}


class AsyncTokenCredentialChain(TokenCredentialChain):
    """A sequence of token credentials"""

    async def get_token(self, scopes: Iterable[str]) -> str:
        """Attempts to get a token from each credential, in order, returning the first token.
           If no token is acquired, raises an exception listing error messages.
        """
        history = []
        for credential in self._credentials:
            try:
                return await credential.get_token(scopes)
            except AuthenticationError as ex:
                history.append((credential, ex.message))
            except Exception as ex:  # pylint: disable=broad-except
                history.append((credential, str(ex)))
        error_message = self._get_error_message(history)
        raise AuthenticationError(error_message)
