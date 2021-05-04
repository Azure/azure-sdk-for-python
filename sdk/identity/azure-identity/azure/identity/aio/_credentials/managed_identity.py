# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
import os
from typing import TYPE_CHECKING

from .._internal import AsyncContextManager
from .._internal.decorators import log_get_token_async
from ... import CredentialUnavailableError
from ..._constants import EnvironmentVariables

if TYPE_CHECKING:
    from typing import Any, Optional
    from azure.core.credentials import AccessToken
    from azure.core.credentials_async import AsyncTokenCredential

_LOGGER = logging.getLogger(__name__)


class ManagedIdentityCredential(AsyncContextManager):
    """Authenticates with an Azure managed identity in any hosting environment which supports managed identities.

    This credential defaults to using a system-assigned identity. To configure a user-assigned identity, use one of
    the keyword arguments.

    See Azure Active Directory documentation for more information about configuring managed identity for applications:
    https://docs.microsoft.com/azure/active-directory/managed-identities-azure-resources/overview

    :keyword str client_id: a user-assigned identity's client ID. This is supported in all hosting environments.
    :keyword identity_config: a mapping ``{parameter_name: value}`` specifying a user-assigned identity by its object
      or resource ID, for example ``{"object_id": "..."}``. Check the documentation for your hosting environment to
      learn what values it expects.
    :paramtype identity_config: Mapping[str, str]
    """

    def __init__(self, **kwargs: "Any") -> None:
        self._credential = None  # type: Optional[AsyncTokenCredential]

        if os.environ.get(EnvironmentVariables.MSI_ENDPOINT):
            if os.environ.get(EnvironmentVariables.MSI_SECRET):
                _LOGGER.info("%s will use App Service managed identity", self.__class__.__name__)
                from .app_service import AppServiceCredential

                self._credential = AppServiceCredential(**kwargs)
            else:
                _LOGGER.info("%s will use Cloud Shell managed identity", self.__class__.__name__)
                from .cloud_shell import CloudShellCredential

                self._credential = CloudShellCredential(**kwargs)
        elif os.environ.get(EnvironmentVariables.IDENTITY_ENDPOINT):
            if os.environ.get(EnvironmentVariables.IDENTITY_HEADER) and os.environ.get(
                EnvironmentVariables.IDENTITY_SERVER_THUMBPRINT
            ):
                _LOGGER.info("%s will use Service Fabric managed identity", self.__class__.__name__)
                from .service_fabric import ServiceFabricCredential

                self._credential = ServiceFabricCredential(**kwargs)
            elif os.environ.get(EnvironmentVariables.IMDS_ENDPOINT):
                _LOGGER.info("%s will use Azure Arc managed identity", self.__class__.__name__)
                from .azure_arc import AzureArcCredential

                self._credential = AzureArcCredential(**kwargs)
        else:
            from .imds import ImdsCredential

            _LOGGER.info("%s will use IMDS", self.__class__.__name__)
            self._credential = ImdsCredential(**kwargs)

    async def __aenter__(self):
        if self._credential:
            await self._credential.__aenter__()
        return self

    async def close(self):
        """Close the credential's transport session."""
        if self._credential:
            await self._credential.__aexit__()

    @log_get_token_async
    async def get_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":
        """Asynchronously request an access token for `scopes`.

        This method is called automatically by Azure SDK clients.

        :param str scopes: desired scope for the access token. This credential allows only one scope per request.
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises ~azure.identity.CredentialUnavailableError: managed identity isn't available in the hosting environment
        """
        if not self._credential:
            raise CredentialUnavailableError(message="No managed identity endpoint found.")
        return await self._credential.get_token(*scopes, **kwargs)
