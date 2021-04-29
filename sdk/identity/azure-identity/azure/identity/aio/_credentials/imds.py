# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
from typing import TYPE_CHECKING

from azure.core.exceptions import ClientAuthenticationError, HttpResponseError

from ... import CredentialUnavailableError
from .._internal import AsyncContextManager
from .._internal.get_token_mixin import GetTokenMixin
from .._internal.managed_identity_client import AsyncManagedIdentityClient
from ..._credentials.imds import get_request, PIPELINE_SETTINGS

if TYPE_CHECKING:
    from typing import Any, Optional
    from azure.core.credentials import AccessToken

_LOGGER = logging.getLogger(__name__)


class ImdsCredential(AsyncContextManager, GetTokenMixin):
    def __init__(self, **kwargs: "Any") -> None:
        super().__init__()

        self._client = AsyncManagedIdentityClient(
            get_request, _identity_config=kwargs.pop("identity_config", None) or {}, **PIPELINE_SETTINGS, **kwargs
        )
        self._endpoint_available = None  # type: Optional[bool]
        self._user_assigned_identity = "client_id" in kwargs or "identity_config" in kwargs

    async def close(self) -> None:
        await self._client.close()

    async def _acquire_token_silently(self, *scopes: str) -> "Optional[AccessToken]":
        return self._client.get_cached_token(*scopes)

    async def _request_token(self, *scopes, **kwargs: "Any") -> "AccessToken":  # pylint:disable=unused-argument
        if self._endpoint_available is None:
            # Lacking another way to determine whether the IMDS endpoint is listening,
            # we send a request it would immediately reject (because it lacks the Metadata header),
            # setting a short timeout.
            try:
                await self._client.request_token(*scopes, connection_timeout=0.3, retry_total=0)
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

        try:
            token = await self._client.request_token(*scopes, headers={"Metadata": "true"})
        except HttpResponseError as ex:
            # 400 in response to a token request indicates managed identity is disabled,
            # or the identity with the specified client_id is not available
            if ex.status_code == 400:
                self._endpoint_available = False
                message = "ManagedIdentityCredential authentication unavailable. "
                if self._user_assigned_identity:
                    message += "The requested identity has not been assigned to this resource."
                else:
                    message += "No identity has been assigned to this resource."
                raise CredentialUnavailableError(message=message) from ex

            # any other error is unexpected
            raise ClientAuthenticationError(message=ex.message, response=ex.response) from None
        return token
