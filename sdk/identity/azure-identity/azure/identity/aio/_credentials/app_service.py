# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

from .._internal import AsyncContextManager
from .._internal.managed_identity_client import AsyncManagedIdentityClient
from .._internal.get_token_mixin import GetTokenMixin
from ... import CredentialUnavailableError
from ..._credentials.app_service import _get_client_args

if TYPE_CHECKING:
    from typing import Any, Optional
    from azure.core.credentials import AccessToken


class AppServiceCredential(AsyncContextManager, GetTokenMixin):
    def __init__(self, **kwargs: "Any") -> None:
        super(AppServiceCredential, self).__init__()

        client_args = _get_client_args(**kwargs)
        if client_args:
            self._available = True
            self._client = AsyncManagedIdentityClient(**client_args)
        else:
            self._available = False

    async def __aenter__(self):
        if self._available:
            await self._client.__aenter__()
        return self

    async def close(self) -> None:
        await self._client.close()

    async def get_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":
        if not self._available:
            raise CredentialUnavailableError(
                message="App Service managed identity configuration not found in environment"
            )

        return await super().get_token(*scopes, **kwargs)

    async def _acquire_token_silently(self, *scopes: str, **kwargs: "Any") -> "Optional[AccessToken]":
        return self._client.get_cached_token(*scopes)

    async def _request_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":
        return await self._client.request_token(*scopes, **kwargs)
