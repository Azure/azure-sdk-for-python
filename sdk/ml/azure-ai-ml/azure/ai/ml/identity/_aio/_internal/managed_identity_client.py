# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import time
from typing import TYPE_CHECKING

from .._internal import AsyncContextManager
from ..._internal import _scopes_to_resource
from ..._internal.managed_identity_client import ManagedIdentityClientBase
from ..._internal.pipeline import build_async_pipeline

if TYPE_CHECKING:
    # pylint:disable=ungrouped-imports
    from typing import Any
    from azure.core.credentials import AccessToken
    from azure.core.pipeline import AsyncPipeline


# pylint:disable=async-client-bad-name,missing-client-constructor-parameter-credential
class AsyncManagedIdentityClient(AsyncContextManager, ManagedIdentityClientBase):
    async def __aenter__(self):
        await self._pipeline.__aenter__()
        return self

    async def close(self) -> None:
        await self._pipeline.__aexit__()

    async def request_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":
        # pylint:disable=invalid-overridden-method
        resource = _scopes_to_resource(*scopes)
        request = self._request_factory(resource, self._identity_config)
        request_time = int(time.time())
        response = await self._pipeline.run(request, retry_on_methods=[request.method], **kwargs)
        token = self._process_response(response, request_time)
        return token

    def _build_pipeline(self, **kwargs: "Any") -> "AsyncPipeline":
        return build_async_pipeline(**kwargs)
