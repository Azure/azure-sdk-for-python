# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any, Iterable, Mapping, Optional

from azure.core import Configuration
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.policies import AsyncRetryPolicy, ContentDecodePolicy, HTTPPolicy, NetworkTraceLoggingPolicy
from azure.core.pipeline.transport import AsyncHttpTransport
from azure.core.pipeline.transport.requests_asyncio import AsyncioRequestsTransport

from ..authn_client import _AuthnClientBase


class AsyncAuthnClient(_AuthnClientBase):
    def __init__(
        self,
        auth_url: str,
        config: Optional[Configuration] = None,
        policies: Optional[Iterable[HTTPPolicy]] = None,
        transport: Optional[AsyncHttpTransport] = None,
        **kwargs: Mapping[str, Any]
    ) -> None:
        config = config or self.create_config(**kwargs)
        # TODO: ContentDecodePolicy doesn't accept kwargs
        policies = policies or [ContentDecodePolicy(), config.logging_policy, config.retry_policy]
        if not transport:
            transport = AsyncioRequestsTransport(configuration=config)
        self._pipeline = AsyncPipeline(transport=transport, policies=policies)
        super(AsyncAuthnClient, self).__init__(auth_url, **kwargs)

    async def request_token(
        self,
        scopes: Iterable[str],
        method: Optional[str] = "POST",
        form_data: Optional[Mapping[str, str]] = None,
        params: Optional[Mapping[str, str]] = None,
    ) -> str:
        request = self._prepare_request(method, form_data, params)
        response = await self._pipeline.run(request, stream=False)
        token = self._deserialize_and_cache_token(response, scopes)
        return token

    @staticmethod
    def create_config(**kwargs: Mapping[str, Any]) -> Configuration:
        config = Configuration(**kwargs)
        config.logging_policy = NetworkTraceLoggingPolicy(**kwargs)
        config.retry_policy = AsyncRetryPolicy(
            retry_on_status_codes=[404, 429] + [x for x in range(500, 600)], **kwargs
        )
        return config
