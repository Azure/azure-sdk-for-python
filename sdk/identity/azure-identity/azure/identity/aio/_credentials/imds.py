# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from typing import Optional, TypeVar, Any

from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.core.credentials import AccessToken
from ... import CredentialUnavailableError
from ..._constants import EnvironmentVariables
from .._internal import AsyncContextManager
from .._internal.get_token_mixin import GetTokenMixin
from .._internal.managed_identity_client import AsyncManagedIdentityClient
from ..._credentials.imds import _get_request, PIPELINE_SETTINGS

T = TypeVar("T", bound="ImdsCredential")


class ImdsCredential(AsyncContextManager, GetTokenMixin):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__()

        self._client = AsyncManagedIdentityClient(_get_request, **dict(PIPELINE_SETTINGS, **kwargs))
        if EnvironmentVariables.AZURE_POD_IDENTITY_AUTHORITY_HOST in os.environ:
            self._endpoint_available: Optional[bool] = True
        else:
            self._endpoint_available = None
        self._error_message: Optional[str] = None
        self._user_assigned_identity = "client_id" in kwargs or "identity_config" in kwargs

    async def __aenter__(self: T) -> T:
        await self._client.__aenter__()
        return self

    async def close(self) -> None:
        await self._client.close()

    async def _acquire_token_silently(self, *scopes: str, **kwargs: Any) -> Optional[AccessToken]:
        return self._client.get_cached_token(*scopes)

    async def _request_token(self, *scopes: str, **kwargs: Any) -> AccessToken:  # pylint:disable=unused-argument
        if self._endpoint_available is None:
            # Lacking another way to determine whether the IMDS endpoint is listening,
            # we send a request it would immediately reject (because it lacks the Metadata header),
            # setting a short timeout.
            try:
                await self._client.request_token(*scopes, connection_timeout=0.3, retry_total=0)
                self._endpoint_available = True
            except HttpResponseError:
                # IMDS responded
                self._endpoint_available = True
            except Exception as ex:  # pylint:disable=broad-except
                # if anything else was raised, assume the endpoint is unavailable
                self._endpoint_available = False
                self._error_message = (
                    "ManagedIdentityCredential authentication unavailable, no response from the IMDS endpoint."
                )
                raise CredentialUnavailableError(message=self._error_message) from ex

        if not self._endpoint_available:
            raise CredentialUnavailableError(message=self._error_message)

        try:
            token = await self._client.request_token(*scopes, headers={"Metadata": "true"})
        except HttpResponseError as ex:
            # 400 in response to a token request indicates managed identity is disabled,
            # or the identity with the specified client_id is not available
            if ex.status_code == 400:
                self._endpoint_available = False
                self._error_message = "ManagedIdentityCredential authentication unavailable. "
                if self._user_assigned_identity:
                    self._error_message += "The requested identity has not been assigned to this resource."
                else:
                    self._error_message += "No identity has been assigned to this resource."
                raise CredentialUnavailableError(message=self._error_message) from ex

            # any other error is unexpected
            raise ClientAuthenticationError(message=ex.message, response=ex.response) from ex
        return token
