# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Credentials for Azure SDK authentication.
"""
import os
import time

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError

from ._authn_client import AuthnClient
from ._base import ClientSecretCredentialBase, CertificateCredentialBase
from ._internal import PublicClientCredential, wrap_exceptions
from ._managed_identity import ImdsCredential, MsiCredential
from ._constants import Endpoints, EnvironmentVariables

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, Callable, Dict, Mapping, Optional, Union
    from azure.core.credentials import TokenCredential

    EnvironmentCredentialTypes = Union["CertificateCredential", "ClientSecretCredential", "UsernamePasswordCredential"]

# pylint:disable=too-few-public-methods


class ClientSecretCredential(ClientSecretCredentialBase):
    """
    Authenticates as a service principal using a client ID and client secret.

    :param str client_id: the service principal's client ID
    :param str secret: one of the service principal's client secrets
    :param str tenant_id: ID of the service principal's tenant. Also called its 'directory' ID.
    """

    def __init__(self, client_id, secret, tenant_id, **kwargs):
        # type: (str, str, str, Mapping[str, Any]) -> None
        super(ClientSecretCredential, self).__init__(client_id, secret, tenant_id, **kwargs)
        self._client = AuthnClient(Endpoints.AAD_OAUTH2_V2_FORMAT.format(tenant_id), **kwargs)

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
    """

    def __init__(self, client_id, tenant_id, certificate_path, **kwargs):
        # type: (str, str, str, Mapping[str, Any]) -> None
        self._client = AuthnClient(Endpoints.AAD_OAUTH2_V2_FORMAT.format(tenant_id), **kwargs)
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

    :param str client_id:
        (optional) client ID of a user-assigned identity. Leave unspecified to use a system-assigned identity.
    """

    def __new__(cls, *args, **kwargs):
        if os.environ.get(EnvironmentVariables.MSI_ENDPOINT):
            return MsiCredential(*args, **kwargs)
        return ImdsCredential(*args, **kwargs)

    # the below methods are never called, because ManagedIdentityCredential can't be instantiated;
    # they exist so tooling gets accurate signatures for Imds- and MsiCredential
    def __init__(self, client_id=None, **kwargs):
        # type: (Optional[str], Any) -> None
        pass

    def get_token(self, *scopes):  # pylint:disable=unused-argument,no-self-use
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
        self.credentials = credentials

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
        for credential in self.credentials:
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


class DeviceCodeCredential(PublicClientCredential):
    """
    Authenticates users through the device code flow. When ``get_token`` is called, this credential acquires a
    verification URL and code from Azure Active Directory. A user must browse to the URL, enter the code, and
    authenticate with Azure Active Directory. If the user authenticates successfully, the credential receives
    an access token.

    This credential doesn't cache tokens--each ``get_token`` call begins a new authentication flow.

    For more information about the device code flow, see Azure Active Directory documentation:
    https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-device-code

    :param str client_id: the application's ID
    :param prompt_callback:
        (optional) A callback enabling control of how authentication instructions are presented.
        Must accept arguments (``verification_uri``, ``user_code``, ``expires_in``):
            - ``verification_uri`` (str) the URL the user must visit
            - ``user_code`` (str) the code the user must enter there
            - ``expires_in`` (int) the number of seconds the code will be valid
        If not provided, the credential will print instructions to stdout.

    Keyword arguments
        - *tenant (str)* - tenant ID or a domain associated with a tenant. If not provided, defaults to the
          'organizations' tenant, which supports only Azure Active Directory work or school accounts.
        - *timeout (int)* - seconds to wait for the user to authenticate. Defaults to the validity period of the device
          code as set by Azure Active Directory, which also prevails when ``timeout`` is longer.

    """

    def __init__(self, client_id, prompt_callback=None, **kwargs):
        # type: (str, Optional[Callable[[str, str], None]], Any) -> None
        self._timeout = kwargs.pop("timeout", None)  # type: Optional[int]
        self._prompt_callback = prompt_callback
        super(DeviceCodeCredential, self).__init__(client_id=client_id, **kwargs)

    @wrap_exceptions
    def get_token(self, *scopes):
        # type (*str) -> AccessToken
        """
        Request an access token for `scopes`. This credential won't cache the token. Each call begins a new
        authentication flow.

        :param str scopes: desired scopes for the token
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises: :class:`azure.core.exceptions.ClientAuthenticationError`
        """

        # MSAL requires scopes be a list
        scopes = list(scopes)  # type: ignore
        now = int(time.time())

        app = self._get_app()
        flow = app.initiate_device_flow(scopes)
        if "error" in flow:
            raise ClientAuthenticationError(
                message="Couldn't begin authentication: {}".format(flow.get("error_description") or flow.get("error"))
            )

        if self._prompt_callback:
            self._prompt_callback(flow["verification_uri"], flow["user_code"], flow["expires_in"])
        else:
            print(flow["message"])

        if self._timeout is not None and self._timeout < flow["expires_in"]:
            deadline = now + self._timeout
            result = app.acquire_token_by_device_flow(flow, exit_condition=lambda flow: time.time() > deadline)
        else:
            result = app.acquire_token_by_device_flow(flow)

        if "access_token" not in result:
            if result.get("error") == "authorization_pending":
                message = "Timed out waiting for user to authenticate"
            else:
                message = "Authentication failed: {}".format(result.get("error_description") or result.get("error"))
            raise ClientAuthenticationError(message=message)

        token = AccessToken(result["access_token"], now + int(result["expires_in"]))
        return token


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

    Keyword arguments
        - *tenant (str)* - tenant ID or a domain associated with a tenant. If not provided, defaults to the
          'organizations' tenant, which supports only Azure Active Directory work or school accounts.

    """

    def __init__(self, client_id, username, password, **kwargs):
        # type: (str, str, str, Any) -> None
        super(UsernamePasswordCredential, self).__init__(client_id=client_id, **kwargs)
        self._username = username
        self._password = password

    @wrap_exceptions
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
