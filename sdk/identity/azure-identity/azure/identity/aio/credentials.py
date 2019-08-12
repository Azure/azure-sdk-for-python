# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Credentials for asynchronous Azure SDK authentication.
"""
import os
from typing import Any, Dict, Mapping, Optional, Union

from azure.core import Configuration
from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
from azure.core.pipeline.policies import ContentDecodePolicy, HeadersPolicy, NetworkTraceLoggingPolicy, AsyncRetryPolicy

from ._authn_client import AsyncAuthnClient
from ._managed_identity import ImdsCredential, MsiCredential
from .._base import ClientSecretCredentialBase, CertificateCredentialBase
from .._constants import Endpoints, EnvironmentVariables
from ..credentials import ChainedTokenCredential as SyncChainedTokenCredential

# pylint:disable=too-few-public-methods


class ClientSecretCredential(ClientSecretCredentialBase):
    """
    Authenticates as a service principal using a client ID and client secret.

    :param str client_id: the service principal's client ID
    :param str secret: one of the service principal's client secrets
    :param str tenant_id: ID of the service principal's tenant. Also called its 'directory' ID.
    """

    def __init__(self, client_id: str, secret: str, tenant_id: str, **kwargs: Mapping[str, Any]) -> None:
        super(ClientSecretCredential, self).__init__(client_id, secret, tenant_id, **kwargs)
        self._client = AsyncAuthnClient(Endpoints.AAD_OAUTH2_V2_FORMAT.format(tenant_id), **kwargs)

    async def get_token(self, *scopes: str) -> AccessToken:
        """
        Asynchronously request an access token for `scopes`.

        :param str scopes: desired scopes for the token
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises: :class:`azure.core.exceptions.ClientAuthenticationError`
        """
        token = self._client.get_cached_token(scopes)
        if not token:
            data = dict(self._form_data, scope=" ".join(scopes))
            token = await self._client.request_token(scopes, form_data=data)
        return token  # type: ignore


class CertificateCredential(CertificateCredentialBase):
    """
    Authenticates as a service principal using a certificate.

    :param str client_id: the service principal's client ID
    :param str tenant_id: ID of the service principal's tenant. Also called its 'directory' ID.
    :param str certificate_path: path to a PEM-encoded certificate file including the private key
    """

    def __init__(self, client_id: str, tenant_id: str, certificate_path: str, **kwargs: Mapping[str, Any]) -> None:
        super(CertificateCredential, self).__init__(client_id, tenant_id, certificate_path, **kwargs)
        self._client = AsyncAuthnClient(Endpoints.AAD_OAUTH2_V2_FORMAT.format(tenant_id), **kwargs)

    async def get_token(self, *scopes: str) -> AccessToken:
        """
        Asynchronously request an access token for `scopes`.

        :param str scopes: desired scopes for the token
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises: :class:`azure.core.exceptions.ClientAuthenticationError`
        """
        token = self._client.get_cached_token(scopes)
        if not token:
            data = self._get_request_data(*scopes)
            token = await self._client.request_token(scopes, form_data=data)
        return token  # type: ignore


class EnvironmentCredential:
    """
    Authenticates as a service principal using a client secret or a certificate, or as a user with a username and
    password, depending on environment variable settings. Configuration is attempted in this order, using these
    environment variables:

    Service principal with secret:
      - **AZURE_CLIENT_ID**: the service principal's client ID
      - **AZURE_CLIENT_SECRET**: one of the service principal's client secrets
      - **AZURE_TENANT_ID**: ID of the service principal's tenant. Also called its 'directory' ID.

    Service principal with certificate:
      - **AZURE_CLIENT_ID**: the service principal's client ID
      - **AZURE_CLIENT_CERTIFICATE_PATH**: path to a PEM-encoded certificate file including the private key
      - **AZURE_TENANT_ID**: ID of the service principal's tenant. Also called its 'directory' ID.

    User with username and password:
      - **AZURE_CLIENT_ID**: the application's client ID
      - **AZURE_USERNAME**: a username (usually an email address)
      - **AZURE_PASSWORD**: that user's password
    """

    def __init__(self, **kwargs: Mapping[str, Any]) -> None:
        self._credential = None  # type: Optional[Union[CertificateCredential, ClientSecretCredential]]

        if all(os.environ.get(v) is not None for v in EnvironmentVariables.CLIENT_SECRET_VARS):
            self._credential = ClientSecretCredential(
                client_id=os.environ[EnvironmentVariables.AZURE_CLIENT_ID],
                secret=os.environ[EnvironmentVariables.AZURE_CLIENT_SECRET],
                tenant_id=os.environ[EnvironmentVariables.AZURE_TENANT_ID],
                **kwargs
            )
        elif all(os.environ.get(v) is not None for v in EnvironmentVariables.CERT_VARS):
            self._credential = CertificateCredential(
                client_id=os.environ[EnvironmentVariables.AZURE_CLIENT_ID],
                tenant_id=os.environ[EnvironmentVariables.AZURE_TENANT_ID],
                certificate_path=os.environ[EnvironmentVariables.AZURE_CLIENT_CERTIFICATE_PATH],
                **kwargs
            )

    async def get_token(self, *scopes: str) -> AccessToken:
        """
        Asynchronously request an access token for `scopes`.

        :param str scopes: desired scopes for the token
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises: :class:`azure.core.exceptions.ClientAuthenticationError`
        """
        if not self._credential:
            message = "Missing environment settings. To authenticate with one of the service principal's client secrets, set {}. To authenticate with a certificate, set {}.".format(
                ", ".join(EnvironmentVariables.CLIENT_SECRET_VARS), ", ".join(EnvironmentVariables.CERT_VARS)
            )
            raise ClientAuthenticationError(message=message)
        return await self._credential.get_token(*scopes)


class ManagedIdentityCredential(object):
    """
    Authenticates with a managed identity in an App Service, Azure VM or Cloud Shell environment.

    :param str client_id: Optional client ID of a user-assigned identity. Leave unspecified to use a system-assigned identity.
    """

    def __new__(cls, *args, **kwargs):
        if os.environ.get(EnvironmentVariables.MSI_ENDPOINT):
            return MsiCredential(*args, **kwargs)
        return ImdsCredential(*args, **kwargs)

    # the below methods are never called, because ManagedIdentityCredential can't be instantiated;
    # they exist so tooling gets accurate signatures for Imds- and MsiCredential
    def __init__(self, client_id: Optional[str] = None, **kwargs: Any) -> None:
        pass

    async def get_token(self, *scopes: str) -> AccessToken:
        """
        Asynchronously request an access token for `scopes`.

        :param str scopes: desired scopes for the token
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises: :class:`azure.core.exceptions.ClientAuthenticationError`
        """
        return AccessToken()


class ChainedTokenCredential(SyncChainedTokenCredential):
    """
    A sequence of credentials that is itself a credential. Its ``get_token`` method calls ``get_token`` on each
    credential in the sequence, in order, returning the first valid token received.

    :param credentials: credential instances to form the chain
    :type credentials: :class:`azure.core.credentials.TokenCredential`
    """

    async def get_token(self, *scopes: str) -> AccessToken:
        """
        Asynchronously request a token from each credential, in order, returning the first token
        received. If none provides a token, raises :class:`azure.core.exceptions.ClientAuthenticationError`
        with an error message from each credential.

        :param str scopes: desired scopes for the token
        :raises: :class:`azure.core.exceptions.ClientAuthenticationError`
        """
        history = []
        for credential in self.credentials:
            try:
                return await credential.get_token(*scopes)
            except ClientAuthenticationError as ex:
                history.append((credential, ex.message))
            except Exception as ex:  # pylint: disable=broad-except
                history.append((credential, str(ex)))
        error_message = self._get_error_message(history)
        raise ClientAuthenticationError(message=error_message)
