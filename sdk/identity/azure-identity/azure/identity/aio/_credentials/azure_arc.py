# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import os
from typing import TYPE_CHECKING

from azure.core.pipeline.policies import AsyncHTTPPolicy

from .._internal import AsyncContextManager
from .._internal.managed_identity_client import AsyncManagedIdentityClient
from .._internal.get_token_mixin import GetTokenMixin
from ... import CredentialUnavailableError
from ..._constants import EnvironmentVariables
from ..._credentials.azure_arc import _get_request, _get_secret_key

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, Optional
    from azure.core.credentials import AccessToken
    from azure.core.pipeline import PipelineRequest, PipelineResponse


class AzureArcCredential(AsyncContextManager, GetTokenMixin):
    def __init__(self, **kwargs: "Any") -> None:
        super().__init__()

        url = os.environ.get(EnvironmentVariables.IDENTITY_ENDPOINT)
        imds = os.environ.get(EnvironmentVariables.IMDS_ENDPOINT)
        self._available = url and imds
        if self._available:
            self._client = AsyncManagedIdentityClient(
                _per_retry_policies=[ArcChallengeAuthPolicy()],
                request_factory=functools.partial(_get_request, url),
                **kwargs
            )

    async def __aenter__(self):
        if self._available:
            await self._client.__aenter__()
        return self

    async def close(self) -> None:
        await self._client.close()

    async def get_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":
        if not self._available:
            raise CredentialUnavailableError(
                message="Service Fabric managed identity configuration not found in environment"
            )

        return await super().get_token(*scopes, **kwargs)

    async def _acquire_token_silently(self, *scopes: str, **kwargs: "Any") -> "Optional[AccessToken]":
        return self._client.get_cached_token(*scopes)

    async def _request_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":
        return await self._client.request_token(*scopes, **kwargs)


class ArcChallengeAuthPolicy(AsyncHTTPPolicy):
    """Policy for handling Azure Arc's challenge authentication"""

    async def send(self, request: "PipelineRequest") -> "PipelineResponse":
        request.http_request.headers["Metadata"] = "true"
        response = await self.next.send(request)

        if response.http_response.status_code == 401:
            secret_key = _get_secret_key(response)
            request.http_request.headers["Authorization"] = "Basic {}".format(secret_key)
            response = await self.next.send(request)

        return response
