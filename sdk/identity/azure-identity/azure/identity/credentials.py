# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os

from azure.core import Configuration
from azure.core.pipeline.policies import ContentDecodePolicy, HeadersPolicy, NetworkTraceLoggingPolicy, RetryPolicy

from ._authn_client import AuthnClient
from ._base import ClientSecretCredentialBase, CertificateCredentialBase
from .constants import EnvironmentVariables, IMDS_ENDPOINT, OAUTH_ENDPOINT
from .exceptions import AuthenticationError

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, Iterable, List, Mapping, Optional, Union
    from azure.core.credentials import SupportsGetToken

# pylint:disable=too-few-public-methods


class ClientSecretCredential(ClientSecretCredentialBase):
    """Authenticates with a client secret"""

    def __init__(self, client_id, secret, tenant_id, config=None, **kwargs):
        # type: (str, str, str, Optional[Configuration], Mapping[str, Any]) -> None
        super(ClientSecretCredential, self).__init__(client_id, secret, tenant_id, **kwargs)
        self._client = AuthnClient(OAUTH_ENDPOINT.format(tenant_id), config, **kwargs)

    def get_token(self, scopes):
        # type: (Iterable[str]) -> str
        token = self._client.get_cached_token(scopes)
        if not token:
            data = dict(self._form_data, scope=" ".join(scopes))
            token = self._client.request_token(scopes, form_data=data)
        return token


class CertificateCredential(CertificateCredentialBase):
    """Authenticates with a certificate"""

    def __init__(self, client_id, tenant_id, certificate_path, config=None, **kwargs):
        # type: (str, str, str, Optional[Configuration], Mapping[str, Any]) -> None
        self._client = AuthnClient(OAUTH_ENDPOINT.format(tenant_id), config, **kwargs)
        super(CertificateCredential, self).__init__(client_id, tenant_id, certificate_path, **kwargs)

    def get_token(self, scopes):
        # type: (Iterable[str]) -> str
        token = self._client.get_cached_token(scopes)
        if not token:
            data = dict(self._form_data, scope=" ".join(scopes))
            token = self._client.request_token(scopes, form_data=data)
        return token


class EnvironmentCredential:
    """Authenticates with a secret or certificate using environment variable settings"""

    def __init__(self, **kwargs):
        # type: (Mapping[str, Any]) -> None
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

    def get_token(self, scopes):
        # type: (Iterable[str]) -> str
        if not self._credential:
            message = "Missing environment settings. To authenticate with a client secret, set {}. To authenticate with a certificate, set {}.".format(
                ", ".join(EnvironmentVariables.CLIENT_SECRET_VARS), ", ".join(EnvironmentVariables.CERT_VARS)
            )
            raise AuthenticationError(message)
        return self._credential.get_token(scopes)


class ManagedIdentityCredential:
    """Authenticates with a managed identity"""

    def __init__(self, config=None, **kwargs):
        # type: (Optional[Configuration], Mapping[str, Any]) -> None
        config = config or self.create_config(**kwargs)
        policies = [config.header_policy, ContentDecodePolicy(), config.logging_policy, config.retry_policy]
        self._client = AuthnClient(IMDS_ENDPOINT, config, policies)

    @staticmethod
    def create_config(**kwargs):
        # type: (Mapping[str, str]) -> Configuration
        timeout = kwargs.pop("connection_timeout", 2)
        config = Configuration(connection_timeout=timeout, **kwargs)
        config.header_policy = HeadersPolicy(base_headers={"Metadata": "true"}, **kwargs)
        config.logging_policy = NetworkTraceLoggingPolicy(**kwargs)
        retries = kwargs.pop("retry_total", 5)
        config.retry_policy = RetryPolicy(retry_total=retries, retry_on_status_codes=[404, 429] + list(range(500, 600)), **kwargs)
        return config

    def get_token(self, scopes):
        # type: (List[str]) -> str
        if len(scopes) != 1:
            raise ValueError("Managed identity credential supports one scope per request")
        token = self._client.get_cached_token(scopes)
        if not token:
            resource = scopes[0].rstrip("/.default")
            token = self._client.request_token(
                scopes, method="GET", params={"api-version": "2018-02-01", "resource": resource}
            )
        return token


class TokenCredentialChain:
    """A sequence of token credentials"""

    def __init__(self, credentials):
        # type: (Iterable[SupportsGetToken]) -> None
        if not credentials:
            raise ValueError("at least one credential is required")
        self._credentials = credentials

    @classmethod
    def default(cls):
        return cls([EnvironmentCredential(), ManagedIdentityCredential()])

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
