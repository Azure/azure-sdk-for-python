# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
import os
from typing import Optional, Union

from azure.core.credentials import AccessToken
from .._internal.decorators import log_get_token_async
from ... import CredentialUnavailableError
from ..._constants import EnvironmentVariables
from .._internal import AsyncContextManager
from .certificate import CertificateCredential
from .client_secret import ClientSecretCredential

_LOGGER = logging.getLogger(__name__)


class EnvironmentCredential(AsyncContextManager):
    """A credential configured by environment variables.

    This credential is capable of authenticating as a service principal using a client secret or a certificate, or as
    a user with a username and password. Configuration is attempted in this order, using these environment variables:

    Service principal with secret:
      - **AZURE_TENANT_ID**: ID of the service principal's tenant. Also called its 'directory' ID.
      - **AZURE_CLIENT_ID**: the service principal's client ID
      - **AZURE_CLIENT_SECRET**: one of the service principal's client secrets
      - **AZURE_AUTHORITY_HOST**: authority of an Azure Active Directory endpoint, for example
        "login.microsoftonline.com", the authority for Azure Public Cloud, which is the default
        when no value is given.

    Service principal with certificate:
      - **AZURE_TENANT_ID**: ID of the service principal's tenant. Also called its 'directory' ID.
      - **AZURE_CLIENT_ID**: the service principal's client ID
      - **AZURE_CLIENT_CERTIFICATE_PATH**: path to a PEM or PKCS12 certificate file including the private key.
      - **AZURE_CLIENT_CERTIFICATE_PASSWORD**: (optional) password of the certificate file, if any.
      - **AZURE_AUTHORITY_HOST**: authority of an Azure Active Directory endpoint, for example
        "login.microsoftonline.com", the authority for Azure Public Cloud, which is the default
        when no value is given.
    """

    def __init__(self, **kwargs) -> None:
        self._credential = None  # type: Optional[Union[CertificateCredential, ClientSecretCredential]]

        if all(os.environ.get(v) is not None for v in EnvironmentVariables.CLIENT_SECRET_VARS):
            self._credential = ClientSecretCredential(
                client_id=os.environ[EnvironmentVariables.AZURE_CLIENT_ID],
                client_secret=os.environ[EnvironmentVariables.AZURE_CLIENT_SECRET],
                tenant_id=os.environ[EnvironmentVariables.AZURE_TENANT_ID],
                **kwargs
            )
        elif all(os.environ.get(v) is not None for v in EnvironmentVariables.CERT_VARS):
            self._credential = CertificateCredential(
                client_id=os.environ[EnvironmentVariables.AZURE_CLIENT_ID],
                tenant_id=os.environ[EnvironmentVariables.AZURE_TENANT_ID],
                certificate_path=os.environ[EnvironmentVariables.AZURE_CLIENT_CERTIFICATE_PATH],
                password=os.environ.get(EnvironmentVariables.AZURE_CLIENT_CERTIFICATE_PASSWORD),
                **kwargs
            )

        if self._credential:
            _LOGGER.info("Environment is configured for %s", self._credential.__class__.__name__)
        else:
            expected_variables = set(EnvironmentVariables.CERT_VARS + EnvironmentVariables.CLIENT_SECRET_VARS)
            set_variables = [v for v in expected_variables if v in os.environ]
            if set_variables:
                _LOGGER.warning(
                    "Incomplete environment configuration. These variables are set: %s", ", ".join(set_variables)
                )
            else:
                _LOGGER.info("No environment configuration found.")

    async def __aenter__(self):
        if self._credential:
            await self._credential.__aenter__()
        return self

    async def close(self):
        """Close the credential's transport session."""

        if self._credential:
            await self._credential.__aexit__()

    @log_get_token_async
    async def get_token(self, *scopes: str, **kwargs) -> AccessToken:
        """Asynchronously request an access token for `scopes`.

        This method is called automatically by Azure SDK clients.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
        :keyword str tenant_id: optional tenant to include in the token request.

        :rtype: :class:`azure.core.credentials.AccessToken`

        :raises ~azure.identity.CredentialUnavailableError: environment variable configuration is incomplete
        """
        if not self._credential:
            message = (
                "EnvironmentCredential authentication unavailable. Environment variables are not fully configured.\n"
                "Visit https://aka.ms/azsdk/python/identity/environmentcredential/troubleshoot to troubleshoot."
                "this issue."
            )
            raise CredentialUnavailableError(message=message)
        return await self._credential.get_token(*scopes, **kwargs)
