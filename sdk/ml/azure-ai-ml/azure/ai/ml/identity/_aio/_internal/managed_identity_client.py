# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import time
from typing import TYPE_CHECKING, Any

from ..._internal import _scopes_to_resource
from ..._internal.managed_identity_client import ManagedIdentityClientBase
from ..._internal.pipeline import build_async_pipeline
from .._internal import AsyncContextManager

if TYPE_CHECKING:
    from azure.core.credentials import AccessToken
    from azure.core.pipeline import AsyncPipeline


# pylint:disable=async-client-bad-name,missing-client-constructor-parameter-credential
class AsyncManagedIdentityClient(AsyncContextManager, ManagedIdentityClientBase):
    async def __aenter__(self) -> "AsyncManagedIdentityClient":
        await self._pipeline.__aenter__()
        return self

    async def close(self) -> None:
        await self._pipeline.__aexit__()

    async def request_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":
        # pylint:disable=invalid-overridden-method
        resource = _scopes_to_resource(*scopes)
        # pylint: disable=no-member
        request = self._request_factory(resource, self._identity_config)  # type: ignore
        request_time = int(time.time())
        response = await self._pipeline.run(request, retry_on_methods=[request.method], **kwargs)
        token = self._process_response(response=response, request_time=request_time, resource=resource)
        return token

    def _build_pipeline(self, **kwargs: "Any") -> "AsyncPipeline":
        return build_async_pipeline(**kwargs)
