# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from typing import TYPE_CHECKING

from azure.core.exceptions import ClientAuthenticationError
from ..._constants import EnvironmentVariables
from .client_credential import CertificateCredential, ClientSecretCredential

if TYPE_CHECKING:
    from typing import Any, Optional, Union
    from azure.core.credentials import AccessToken
    from azure.core.pipeline.policies import HTTPPolicy
    from azure.core.pipeline.transport import AsyncHttpTransport


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
    """

    def __init__(self, **kwargs: "Any") -> None:
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

    async def get_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":  # pylint:disable=unused-argument
        """
        Asynchronously request an access token for `scopes`.

        :param str scopes: desired scopes for the token
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises: :class:`azure.core.exceptions.ClientAuthenticationError`
        """
        if not self._credential:
            raise ClientAuthenticationError(message="Incomplete environment configuration.")
        return await self._credential.get_token(*scopes, **kwargs)
