# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Credentials for Azure SDK authentication.
"""
import os
import time

from azure.core import Configuration
from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
from azure.core.pipeline.policies import ContentDecodePolicy, HeadersPolicy, NetworkTraceLoggingPolicy, RetryPolicy

from ._authn_client import AuthnClient
from ._base import ClientSecretCredentialBase, CertificateCredentialBase
from ._internal import PublicClientCredential
from ._managed_identity import ImdsCredential, MsiCredential
from .constants import Endpoints, EnvironmentVariables

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, Dict, Mapping, Optional, Union
    from azure.core.credentials import TokenCredential
    EnvironmentCredentialTypes = Union["CertificateCredential", "ClientSecretCredential", "UsernamePasswordCredential"]

# pylint:disable=too-few-public-methods


class ClientSecretCredential(ClientSecretCredentialBase):
    """
    Authenticates as a service principal using a client ID and client secret.

    :param str client_id: the service principal's client ID
    :param str secret: one of the service principal's client secrets
    :param str tenant_id: ID of the service principal's tenant. Also called its 'directory' ID.
    :param config: optional configuration for the underlying HTTP pipeline
    :type config: :class:`azure.core.configuration`
    """

    def __init__(self, client_id, secret, tenant_id, config=None, **kwargs):
        # type: (str, str, str, Optional[Configuration], Mapping[str, Any]) -> None
        super(ClientSecretCredential, self).__init__(client_id, secret, tenant_id, **kwargs)
        self._client = AuthnClient(Endpoints.AAD_OAUTH2_V2_FORMAT.format(tenant_id), config, **kwargs)

    def get_token(self, *scopes):
        # type (*str) -> AccessToken
        """
        Request an access token for `scopes`.

        :param str scopes: desired scopes for the token
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises: :class:`azure.core.exceptions.ClientAuthenticationError`
        """
        token = self._client.get_cached_token(scopes)
        if not token:
            data = dict(self._form_data, scope=" ".join(scopes))
            token = self._client.request_token(scopes, form_data=data)
        return token


class CertificateCredential(CertificateCredentialBase):
    """
    Authenticates as a service principal using a certificate.

    :param str client_id: the service principal's client ID
    :param str tenant_id: ID of the service principal's tenant. Also called its 'directory' ID.
    :param str certificate_path: path to a PEM-encoded certificate file including the private key
    :param config: optional configuration for the underlying HTTP pipeline
    :type config: :class:`azure.core.configuration`
    """

    def __init__(self, client_id, tenant_id, certificate_path, config=None, **kwargs):
        # type: (str, str, str, Optional[Configuration], Mapping[str, Any]) -> None
        self._client = AuthnClient(Endpoints.AAD_OAUTH2_V2_FORMAT.format(tenant_id), config, **kwargs)
        super(CertificateCredential, self).__init__(client_id, tenant_id, certificate_path, **kwargs)

    def get_token(self, *scopes):
        # type (*str) -> AccessToken
        """
        Request an access token for `scopes`.

        :param str scopes: desired scopes for the token
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises: :class:`azure.core.exceptions.ClientAuthenticationError`
        """
        token = self._client.get_cached_token(scopes)
        if not token:
            data = self._get_request_data(*scopes)
            token = self._client.request_token(scopes, form_data=data)
        return token


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

    def __init__(self, **kwargs):
        # type: (Mapping[str, Any]) -> None
        self._credential = None  # type: Optional[EnvironmentCredentialTypes]

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
        elif all(os.environ.get(v) is not None for v in EnvironmentVariables.USERNAME_PASSWORD_VARS):
            self._credential = UsernamePasswordCredential(
                client_id=os.environ[EnvironmentVariables.AZURE_CLIENT_ID],
                username=os.environ[EnvironmentVariables.AZURE_USERNAME],
                password=os.environ[EnvironmentVariables.AZURE_PASSWORD],
                tenant=os.environ.get(EnvironmentVariables.AZURE_TENANT_ID),  # optional for username/password auth
                **kwargs
            )

    def get_token(self, *scopes):
        # type (*str) -> AccessToken
        """
        Request an access token for `scopes`.

        :param str scopes: desired scopes for the token
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises: :class:`azure.core.exceptions.ClientAuthenticationError`
        """
        if not self._credential:
            raise ClientAuthenticationError(message="Incomplete environment configuration.")
        return self._credential.get_token(*scopes)


class ManagedIdentityCredential(object):
    """
    Authenticates with a managed identity in an App Service, Azure VM or Cloud Shell environment.

    :param str client_id: Optional client ID of a user-assigned identity. Leave unspecified to use a system-assigned identity.
    :param config: optional configuration for the underlying HTTP pipeline
    :type config: :class:`azure.core.configuration`
    """

    def __new__(cls, *args, **kwargs):
        if os.environ.get(EnvironmentVariables.MSI_ENDPOINT):
            return MsiCredential(*args, **kwargs)
        return ImdsCredential(*args, **kwargs)

    # the below methods are never called, because ManagedIdentityCredential can't be instantiated;
    # they exist so tooling gets accurate signatures for Imds- and MsiCredential
    def __init__(self, client_id=None, config=None, **kwargs):
        # type: (Optional[str], Optional[Configuration], Any) -> None
        pass

    @staticmethod
    def create_config(**kwargs):
        # type: (Dict[str, str]) -> Configuration
        """
        Build a default configuration for the credential's HTTP pipeline.

        :rtype: :class:`azure.core.configuration`
        """
        return Configuration(**kwargs)

    def get_token(self, *scopes):
        # type (*str) -> AccessToken
        """
        Request an access token for `scopes`.

        :param str scopes: desired scopes for the token
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises: :class:`azure.core.exceptions.ClientAuthenticationError`
        """
        return AccessToken()


class ChainedTokenCredential(object):
    """
    A sequence of credentials that is itself a credential. Its ``get_token`` method calls ``get_token`` on each
    credential in the sequence, in order, returning the first valid token received.

    :param credentials: credential instances to form the chain
    :type credentials: :class:`azure.core.credentials.TokenCredential`
    """

    def __init__(self, *credentials):
        # type: (*TokenCredential) -> None
        if not credentials:
            raise ValueError("at least one credential is required")
        self._credentials = credentials

    def get_token(self, *scopes):
        # type (*str) -> AccessToken
        """
        Request a token from each chained credential, in order, returning the first token received.
        If none provides a token, raises :class:`azure.core.exceptions.ClientAuthenticationError` with an
        error message from each credential.

        :param str scopes: desired scopes for the token
        :raises: :class:`azure.core.exceptions.ClientAuthenticationError`
        """
        history = []
        for credential in self._credentials:
            try:
                return credential.get_token(*scopes)
            except ClientAuthenticationError as ex:
                history.append((credential, ex.message))
            except Exception as ex:  # pylint: disable=broad-except
                history.append((credential, str(ex)))
        error_message = self._get_error_message(history)
        raise ClientAuthenticationError(message=error_message)

    @staticmethod
    def _get_error_message(history):
        attempts = []
        for credential, error in history:
            if error:
                attempts.append("{}: {}".format(credential.__class__.__name__, error))
            else:
                attempts.append(credential.__class__.__name__)
        return "No valid token received. {}".format(". ".join(attempts))


class UsernamePasswordCredential(PublicClientCredential):
    """
    Authenticates a user with a username and password. In general, Microsoft doesn't recommend this kind of
    authentication, because it's less secure than other authentication flows.

    Authentication with this credential is not interactive, so it is **not compatible with any form of
    multi-factor authentication or consent prompting**. The application must already have the user's consent.

    This credential can only authenticate work and school accounts; Microsoft accounts are not supported.
    See this document for more information about account types:
    https://docs.microsoft.com/en-us/azure/active-directory/fundamentals/sign-up-organization

    :param str client_id: the application's client ID
    :param str username: the user's username (usually an email address)
    :param str password: the user's password

    **Keyword arguments:**

    *tenant (str)* - a tenant ID or a domain associated with a tenant. If not provided, the credential defaults to the
        'organizations' tenant.
    """

    def __init__(self, client_id, username, password, **kwargs):
        # type: (str, str, str, Any) -> None
        super(UsernamePasswordCredential, self).__init__(client_id=client_id, **kwargs)
        self._username = username
        self._password = password

    def get_token(self, *scopes):
        # type (*str) -> AccessToken
        """
        Request an access token for `scopes`.

        :param str scopes: desired scopes for the token
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises: :class:`azure.core.exceptions.ClientAuthenticationError`
        """

        # MSAL requires scopes be a list
        scopes = list(scopes)  # type: ignore
        now = int(time.time())

        app = self._get_app()
        accounts = app.get_accounts(username=self._username)
        result = None
        for account in accounts:
            result = app.acquire_token_silent(scopes, account=account)
            if result:
                break

        if not result:
            # cache miss -> request a new token
            result = app.acquire_token_by_username_password(
                username=self._username, password=self._password, scopes=scopes
            )

        if "access_token" not in result:
            raise ClientAuthenticationError(message="authentication failed: {}".format(result.get("error_description")))

        return AccessToken(result["access_token"], now + int(result["expires_in"]))
