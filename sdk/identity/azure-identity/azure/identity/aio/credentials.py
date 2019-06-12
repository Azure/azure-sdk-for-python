# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# ------------------------------------------------------------------------
import os
from typing import Any, Dict, Mapping, Optional, Union

from azure.core import Configuration
from azure.core.pipeline.policies import ContentDecodePolicy, HeadersPolicy, NetworkTraceLoggingPolicy, AsyncRetryPolicy

from ._authn_client import AsyncAuthnClient
from ._internal import AsyncImdsCredential, AsyncMsiCredential
from .._base import ClientSecretCredentialBase, CertificateCredentialBase
from ..constants import Endpoints, EnvironmentVariables, MSI_ENDPOINT, MSI_SECRET
from ..credentials import TokenCredentialChain
from ..exceptions import AuthenticationError

# pylint:disable=too-few-public-methods


class AsyncClientSecretCredential(ClientSecretCredentialBase):
    def __init__(
        self,
        client_id: str,
        secret: str,
        tenant_id: str,
        config: Optional[Configuration] = None,
        **kwargs: Mapping[str, Any]
    ) -> None:
        super(AsyncClientSecretCredential, self).__init__(client_id, secret, tenant_id, **kwargs)
        self._client = AsyncAuthnClient(Endpoints.AAD_OAUTH2_V2_FORMAT.format(tenant_id), config, **kwargs)

    async def get_token(self, *scopes: str) -> str:
        token = self._client.get_cached_token(scopes)
        if not token:
            data = dict(self._form_data, scope=" ".join(scopes))
            token = await self._client.request_token(scopes, form_data=data)
        return token  # type: ignore


class AsyncCertificateCredential(CertificateCredentialBase):
    def __init__(
        self,
        client_id: str,
        tenant_id: str,
        certificate_path: str,
        config: Optional[Configuration] = None,
        **kwargs: Mapping[str, Any]
    ) -> None:
        super(AsyncCertificateCredential, self).__init__(client_id, tenant_id, certificate_path, **kwargs)
        self._client = AsyncAuthnClient(Endpoints.AAD_OAUTH2_V2_FORMAT.format(tenant_id), config, **kwargs)

    async def get_token(self, *scopes: str) -> str:
        token = self._client.get_cached_token(scopes)
        if not token:
            data = dict(self._form_data, scope=" ".join(scopes))
            token = await self._client.request_token(scopes, form_data=data)
        return token  # type: ignore


class AsyncEnvironmentCredential:
    def __init__(self, **kwargs: Mapping[str, Any]) -> None:
        self._credential = None  # type: Optional[Union[AsyncCertificateCredential, AsyncClientSecretCredential]]

        if all(os.environ.get(v) is not None for v in EnvironmentVariables.CLIENT_SECRET_VARS):
            self._credential = AsyncClientSecretCredential(
                client_id=os.environ[EnvironmentVariables.AZURE_CLIENT_ID],
                secret=os.environ[EnvironmentVariables.AZURE_CLIENT_SECRET],
                tenant_id=os.environ[EnvironmentVariables.AZURE_TENANT_ID],
                **kwargs
            )
        elif all(os.environ.get(v) is not None for v in EnvironmentVariables.CERT_VARS):
            self._credential = AsyncCertificateCredential(
                client_id=os.environ[EnvironmentVariables.AZURE_CLIENT_ID],
                tenant_id=os.environ[EnvironmentVariables.AZURE_TENANT_ID],
                certificate_path=os.environ[EnvironmentVariables.AZURE_CLIENT_CERTIFICATE_PATH],
                **kwargs
            )

    async def get_token(self, *scopes: str) -> str:
        if not self._credential:
            message = "Missing environment settings. To authenticate with a client secret, set {}. To authenticate with a certificate, set {}.".format(
                ", ".join(EnvironmentVariables.CLIENT_SECRET_VARS), ", ".join(EnvironmentVariables.CERT_VARS)
            )
            raise AuthenticationError(message)
        return await self._credential.get_token(*scopes)


class AsyncManagedIdentityCredential(object):
    """factory for MSI and IMDS credentials"""

    def __new__(cls, *args, **kwargs):
        if os.environ.get(MSI_SECRET) and os.environ.get(MSI_ENDPOINT):
            return AsyncMsiCredential(*args, **kwargs)
        return AsyncImdsCredential(*args, **kwargs)

    @staticmethod
    def create_config(**kwargs: Dict[str, Any]) -> Configuration:
        pass

    async def get_token(self, *scopes: str) -> str:
        pass


class AsyncTokenCredentialChain(TokenCredentialChain):
    """A sequence of token credentials"""

    async def get_token(self, *scopes: str) -> str:  # type: ignore
        """Attempts to get a token from each credential, in order, returning the first token.
           If no token is acquired, raises an exception listing error messages.
        """
        history = []
        for credential in self._credentials:
            try:
                return await credential.get_token(*scopes)
            except AuthenticationError as ex:
                history.append((credential, ex.message))
            except Exception as ex:  # pylint: disable=broad-except
                history.append((credential, str(ex)))
        error_message = self._get_error_message(history)
        raise AuthenticationError(error_message)
