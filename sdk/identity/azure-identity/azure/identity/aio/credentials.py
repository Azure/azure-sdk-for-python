# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Credentials for asynchronous Azure SDK authentication.
"""
import os
from typing import TYPE_CHECKING, Any, Mapping, Optional, Union

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError

from ._authn_client import AsyncAuthnClient
from ._internal import wrap_exceptions
from ._managed_identity import ImdsCredential, MsiCredential
from .._base import ClientSecretCredentialBase, CertificateCredentialBase
from .._constants import Endpoints, EnvironmentVariables
from ..credentials import (
    ChainedTokenCredential as SyncChainedTokenCredential,
    SharedTokenCacheCredential as SyncSharedTokenCacheCredential,
)

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    import msal_extensions
    from ._authn_client import AuthnClientBase

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

    async def get_token(self, *scopes: str, **kwargs: Any) -> AccessToken:  # pylint:disable=unused-argument
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

    async def get_token(self, *scopes: str, **kwargs: Any) -> AccessToken:  # pylint:disable=unused-argument
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

    async def get_token(self, *scopes: str, **kwargs: Any) -> AccessToken:  # pylint:disable=unused-argument
        """
        Asynchronously request an access token for `scopes`.

        :param str scopes: desired scopes for the token
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises: :class:`azure.core.exceptions.ClientAuthenticationError`
        """
        if not self._credential:
            raise ClientAuthenticationError(message="Incomplete environment configuration.")
        return await self._credential.get_token(*scopes, **kwargs)


class ManagedIdentityCredential(object):
    """
    Authenticates with a managed identity in an App Service, Azure VM or Cloud Shell environment.

    :param str client_id:
        (optional) client ID of a user-assigned identity. Leave unspecified to use a system-assigned identity.
    """

    def __new__(cls, *args, **kwargs):
        if os.environ.get(EnvironmentVariables.MSI_ENDPOINT):
            return MsiCredential(*args, **kwargs)
        return ImdsCredential(*args, **kwargs)

    # the below methods are never called, because ManagedIdentityCredential can't be instantiated;
    # they exist so tooling gets accurate signatures for Imds- and MsiCredential
    def __init__(self, client_id: Optional[str] = None, **kwargs: Any) -> None:
        pass

    async def get_token(self, *scopes: str, **kwargs: Any) -> AccessToken:  # pylint:disable=unused-argument,no-self-use
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

    async def get_token(self, *scopes: str, **kwargs: Any) -> AccessToken:  # pylint:disable=unused-argument
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
                return await credential.get_token(*scopes, **kwargs)
            except ClientAuthenticationError as ex:
                history.append((credential, ex.message))
            except Exception as ex:  # pylint: disable=broad-except
                history.append((credential, str(ex)))
        error_message = self._get_error_message(history)
        raise ClientAuthenticationError(message=error_message)


class SharedTokenCacheCredential(SyncSharedTokenCacheCredential):
    """
    Authenticates using tokens in the local cache shared between Microsoft applications.

    :param str username:
        Username (typically an email address) of the user to authenticate as. This is required because the local cache
        may contain tokens for multiple identities.
    """

    @wrap_exceptions
    async def get_token(self, *scopes: str, **kwargs: Any) -> AccessToken:
        """
        Get an access token for `scopes` from the shared cache. If no access token is cached, attempt to acquire one
        using a cached refresh token.

        :param str scopes: desired scopes for the token
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises:
            :class:`azure.core.exceptions.ClientAuthenticationError` when the cache is unavailable or no access token
            can be acquired from it
        """

        if not self._client:
            raise ClientAuthenticationError(message="Shared token cache unavailable")

        token = await self._client.obtain_token_by_refresh_token(scopes, self._username)
        if not token:
            raise ClientAuthenticationError(message="No cached token found for '{}'".format(self._username))

        return token

    @staticmethod
    def _get_auth_client(cache: "msal_extensions.FileTokenCache") -> "AuthnClientBase":
        return AsyncAuthnClient(Endpoints.AAD_OAUTH2_V2_FORMAT.format("common"), cache=cache)
