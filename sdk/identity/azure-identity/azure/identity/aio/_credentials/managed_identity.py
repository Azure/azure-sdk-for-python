# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
import os
from typing import TYPE_CHECKING

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.core.pipeline.policies import AsyncRetryPolicy

from .._authn_client import AsyncAuthnClient
from .._internal import AsyncContextManager
from .._internal.decorators import log_get_token_async
from .._internal.get_token_mixin import GetTokenMixin
from ... import CredentialUnavailableError
from ..._constants import Endpoints, EnvironmentVariables
from ..._credentials.managed_identity import _ManagedIdentityBase

if TYPE_CHECKING:
    from typing import Any, Optional
    from azure.core.configuration import Configuration
    from azure.core.credentials_async import AsyncTokenCredential

_LOGGER = logging.getLogger(__name__)


class ManagedIdentityCredential(AsyncContextManager):
    """Authenticates with an Azure managed identity in any hosting environment which supports managed identities.

    This credential defaults to using a system-assigned identity. To configure a user-assigned identity, use one of
    the keyword arguments.

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
            if (
                os.environ.get(EnvironmentVariables.IDENTITY_HEADER)
                and os.environ.get(EnvironmentVariables.IDENTITY_SERVER_THUMBPRINT)
            ):
                _LOGGER.info("%s will use Service Fabric managed identity", self.__class__.__name__)
                from .service_fabric import ServiceFabricCredential

                self._credential = ServiceFabricCredential(**kwargs)
            elif os.environ.get(EnvironmentVariables.IMDS_ENDPOINT):
                _LOGGER.info("%s will use Azure Arc managed identity", self.__class__.__name__)
                from .azure_arc import AzureArcCredential

                self._credential = AzureArcCredential(**kwargs)
        else:
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


class _AsyncManagedIdentityBase(_ManagedIdentityBase, AsyncContextManager):
    def __init__(self, endpoint: str, **kwargs: "Any") -> None:
        super().__init__(endpoint=endpoint, client_cls=AsyncAuthnClient, **kwargs)

    async def __aenter__(self):
        await self._client.__aenter__()
        return self

    async def close(self):
        """Close the credential's transport session."""

        await self._client.__aexit__()

    @staticmethod
    def _create_config(**kwargs: "Any") -> "Configuration":
        """Build a default configuration for the credential's HTTP pipeline."""
        return _ManagedIdentityBase._create_config(retry_policy=AsyncRetryPolicy, **kwargs)


class ImdsCredential(_AsyncManagedIdentityBase, GetTokenMixin):
    """Asynchronously authenticates with a managed identity via the IMDS endpoint.

    :keyword str client_id: ID of a user-assigned identity. Leave unspecified to use a system-assigned identity.
    """

    def __init__(self, **kwargs: "Any") -> None:
        super().__init__(endpoint=Endpoints.IMDS, **kwargs)
        self._endpoint_available = None  # type: Optional[bool]

    async def _acquire_token_silently(self, *scopes: str) -> "Optional[AccessToken]":
        return self._client.get_cached_token(scopes)

    async def _request_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":  # pylint:disable=unused-argument
        if self._endpoint_available is None:
            # Lacking another way to determine whether the IMDS endpoint is listening,
            # we send a request it would immediately reject (missing a required header),
            # setting a short timeout.
            try:
                await self._client.request_token(scopes, method="GET", connection_timeout=0.3, retry_total=0)
                self._endpoint_available = True
            except HttpResponseError:
                # received a response, choked on it
                self._endpoint_available = True
            except Exception:  # pylint:disable=broad-except
                # if anything else was raised, assume the endpoint is unavailable
                self._endpoint_available = False
                _LOGGER.info("No response from the IMDS endpoint.")

        if not self._endpoint_available:
            message = "ManagedIdentityCredential authentication unavailable, no managed identity endpoint found."
            raise CredentialUnavailableError(message=message)

        if len(scopes) != 1:
            raise ValueError("This credential requires exactly one scope per token request.")

        resource = scopes[0]
        if resource.endswith("/.default"):
            resource = resource[: -len("/.default")]
        params = {"api-version": "2018-02-01", "resource": resource, **self._identity_config}

        try:
            token = await self._client.request_token(scopes, method="GET", params=params)
        except HttpResponseError as ex:
            # 400 in response to a token request indicates managed identity is disabled,
            # or the identity with the specified client_id is not available
            if ex.status_code == 400:
                self._endpoint_available = False
                message = "ManagedIdentityCredential authentication unavailable. "
                if self._identity_config:
                    message += "The requested identity has not been assigned to this resource."
                else:
                    message += "No identity has been assigned to this resource."
                raise CredentialUnavailableError(message=message) from ex

            # any other error is unexpected
            raise ClientAuthenticationError(message=ex.message, response=ex.response) from None
        return token
