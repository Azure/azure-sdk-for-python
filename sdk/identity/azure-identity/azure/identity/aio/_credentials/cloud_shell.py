# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import os
from typing import TYPE_CHECKING

from .._internal import AsyncContextManager
from .._internal.get_token_mixin import GetTokenMixin
from .._internal.managed_identity_client import AsyncManagedIdentityClient
from ... import CredentialUnavailableError
from ..._constants import EnvironmentVariables
from ..._credentials.cloud_shell import _get_request

if TYPE_CHECKING:
    from typing import Any, Optional
    from azure.core.credentials import AccessToken


class CloudShellCredential(AsyncContextManager, GetTokenMixin):
    def __init__(self, **kwargs: "Any") -> None:
        super(CloudShellCredential, self).__init__()
        url = os.environ.get(EnvironmentVariables.MSI_ENDPOINT)
        if url:
            self._available = True
            self._client = AsyncManagedIdentityClient(
                request_factory=functools.partial(_get_request, url),
                base_headers={"Metadata": "true"},
                _identity_config=kwargs.pop("identity_config", None),
                **kwargs,
            )
        else:
            self._available = False

    async def get_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":
        if not self._available:
            raise CredentialUnavailableError(
                message="Cloud Shell managed identity configuration not found in environment"
            )
        return await super(CloudShellCredential, self).get_token(*scopes, **kwargs)

    async def close(self) -> None:
        await self._client.close()

    async def _acquire_token_silently(self, *scopes: str) -> "Optional[AccessToken]":
        return self._client.get_cached_token(*scopes)

    async def _request_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":
        return await self._client.request_token(*scopes, **kwargs)
