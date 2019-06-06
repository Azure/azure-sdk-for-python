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


class AsyncMsiCredential:
    def __init__(self, config: Optional[Configuration] = None, **kwargs: Dict[str, Any]) -> None:
        config = config or self.create_config(**kwargs)
        policies = [ContentDecodePolicy(), config.retry_policy, config.logging_policy]
        endpoint = os.environ.get(MSI_ENDPOINT)
        if not endpoint:
            raise ValueError("expected environment variable {} has no value".format(MSI_ENDPOINT))
        self._client = AsyncAuthnClient(endpoint, config, policies, **kwargs)

    async def get_token(self, *scopes: str) -> str:
        if len(scopes) != 1:
            raise ValueError("this credential supports only one scope per request")
        token = self._client.get_cached_token(scopes)
        if not token:
            resource = scopes[0]
            if resource.endswith("/.default"):
                resource = resource[:-len("/.default")]
            secret = os.environ.get(MSI_SECRET)
            if not secret:
                raise AuthenticationError("{} environment variable has no value".format(MSI_SECRET))
            # TODO: support user-assigned client id
            token = await self._client.request_token(
                scopes,
                method="GET",
                headers={"secret": secret},
                params={"api-version": "2017-09-01", "resource": resource},
            )
        return token

    @staticmethod
    def create_config(**kwargs: Dict[str, Any]) -> Configuration:
        timeout = kwargs.pop("connection_timeout", 2)
        config = Configuration(connection_timeout=timeout, **kwargs)
        config.logging_policy = NetworkTraceLoggingPolicy(**kwargs)
        retries = kwargs.pop("retry_total", 5)
        config.retry_policy = AsyncRetryPolicy(
            retry_total=retries, retry_on_status_codes=[404, 429] + list(range(500, 600)), **kwargs
        )
        return config


class AsyncImdsCredential:
    def __init__(self, config: Optional[Configuration] = None, **kwargs: Dict[str, Any]) -> None:
        config = config or self.create_config(**kwargs)
        policies = [config.header_policy, ContentDecodePolicy(), config.retry_policy, config.logging_policy]
        self._client = AsyncAuthnClient(Endpoints.IMDS, config, policies, **kwargs)

    async def get_token(self, *scopes: str) -> str:
        if len(scopes) != 1:
            raise ValueError("this credential supports one scope per request")
        token = self._client.get_cached_token(scopes)
        if not token:
            resource = scopes[0]
            if resource.endswith("/.default"):
                resource = resource[:-len("/.default")]
            token = await self._client.request_token(
                scopes, method="GET", params={"api-version": "2018-02-01", "resource": resource}
            )
        return token

    @staticmethod
    def create_config(**kwargs: Dict[str, Any]) -> Configuration:
        timeout = kwargs.pop("connection_timeout", 2)
        config = Configuration(connection_timeout=timeout, **kwargs)
        config.header_policy = HeadersPolicy(base_headers={"Metadata": "true"}, **kwargs)
        config.logging_policy = NetworkTraceLoggingPolicy(**kwargs)
        retries = kwargs.pop("retry_total", 5)
        config.retry_policy = AsyncRetryPolicy(
            retry_total=retries, retry_on_status_codes=[404, 429] + list(range(500, 600)), **kwargs
        )
        return config


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

    async def get_token(self, *scopes: str) -> str:
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
