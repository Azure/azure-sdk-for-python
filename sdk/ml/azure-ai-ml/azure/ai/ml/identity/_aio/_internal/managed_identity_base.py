# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import abc
from typing import cast, TYPE_CHECKING

from . import AsyncContextManager
from .get_token_mixin import GetTokenMixin
from .managed_identity_client import AsyncManagedIdentityClient
from azure.identity import CredentialUnavailableError

if TYPE_CHECKING:
    from typing import Any, Optional
    from azure.core.credentials import AccessToken


class AsyncManagedIdentityBase(AsyncContextManager, GetTokenMixin):
    """Base class for internal credentials using AsyncManagedIdentityClient"""

    def __init__(self, **kwargs: "Any") -> None:
        super().__init__()
        self._client = self.get_client(**kwargs)

    @abc.abstractmethod
    def get_client(self, **kwargs: "Any") -> "Optional[AsyncManagedIdentityClient]":
        pass

    @abc.abstractmethod
    def get_unavailable_message(self) -> str:
        pass

    async def __aenter__(self):
        if self._client:
            await self._client.__aenter__()
        return self

    async def __aexit__(self, *args):
        if self._client:
            await self._client.__aexit__(*args)

    async def close(self) -> None:
        await self.__aexit__()

    async def get_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":
        if not self._client:
            raise CredentialUnavailableError(message=self.get_unavailable_message())
        return await super().get_token(*scopes, **kwargs)

    async def _acquire_token_silently(self, *scopes: str, **kwargs: "Any") -> "Optional[AccessToken]":
        # casting because mypy can't determine that these methods are called
        # only by get_token, which raises when self._client is None
        return cast(AsyncManagedIdentityClient, self._client).get_cached_token(*scopes)

    async def _request_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":
        return await cast(AsyncManagedIdentityClient, self._client).request_token(*scopes, **kwargs)
