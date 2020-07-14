# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from typing import TYPE_CHECKING

from ... import CredentialUnavailableError
from ..._constants import EnvironmentVariables
from .certificate import CertificateCredential
from .client_secret import ClientSecretCredential
from .base import AsyncCredentialBase

if TYPE_CHECKING:
    from typing import Any, Optional, Union
    from azure.core.credentials import AccessToken


class EnvironmentCredential(AsyncCredentialBase):
    """A credential configured by environment variables.

    This credential is capable of authenticating as a service principal using a client secret or a certificate, or as
    a user with a username and password. Configuration is attempted in this order, using these environment variables:

    Service principal with secret:
      - **AZURE_TENANT_ID**: ID of the service principal's tenant. Also called its 'directory' ID.
      - **AZURE_CLIENT_ID**: the service principal's client ID
      - **AZURE_CLIENT_SECRET**: one of the service principal's client secrets

    Service principal with certificate:
      - **AZURE_TENANT_ID**: ID of the service principal's tenant. Also called its 'directory' ID.
      - **AZURE_CLIENT_ID**: the service principal's client ID
      - **AZURE_CLIENT_CERTIFICATE_PATH**: path to a PEM-encoded certificate file including the private key The
        certificate must not be password-protected.
    """

    def __init__(self, **kwargs: "Any") -> None:
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
                **kwargs
            )

    async def __aenter__(self):
        if self._credential:
            await self._credential.__aenter__()
        return self

    async def close(self):
        """Close the credential's transport session."""

        if self._credential:
            await self._credential.__aexit__()

    async def get_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":
        """Asynchronously request an access token for `scopes`.

        .. note:: This method is called by Azure SDK clients. It isn't intended for use in application code.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises ~azure.identity.CredentialUnavailableError: environment variable configuration is incomplete
        """
        if not self._credential:
            message = (
                "EnvironmentCredential authentication unavailable. Environment variables are not fully configured."
            )
            raise CredentialUnavailableError(message=message)
        return await self._credential.get_token(*scopes, **kwargs)
