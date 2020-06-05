# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from typing import TYPE_CHECKING

from azure.core.configuration import Configuration
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.policies import (
    ContentDecodePolicy,
    ProxyPolicy,
    NetworkTraceLoggingPolicy,
    AsyncRetryPolicy,
    UserAgentPolicy,
    DistributedTracingPolicy,
    HttpLoggingPolicy,
)
from ..._internal import AadClientBase
from ..._internal.user_agent import USER_AGENT

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, List, Optional, Sequence, Union
    from azure.core.credentials import AccessToken
    from azure.core.pipeline.policies import AsyncHTTPPolicy, SansIOHTTPPolicy
    from azure.core.pipeline.transport import AsyncHttpTransport

    Policy = Union[AsyncHTTPPolicy, SansIOHTTPPolicy]


class AadClient(AadClientBase):
    async def __aenter__(self):
        await self._pipeline.__aenter__()
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def close(self) -> None:
        """Close the client's transport session."""

        await self._pipeline.__aexit__()

    async def obtain_token_by_authorization_code(
        self,
        scopes: "Sequence[str]",
        code: str,
        redirect_uri: str,
        client_secret: "Optional[str]" = None,
        **kwargs: "Any"
    ) -> "AccessToken":
        request = self._get_auth_code_request(
            scopes=scopes, code=code, redirect_uri=redirect_uri, client_secret=client_secret
        )
        now = int(time.time())
        response = await self._pipeline.run(request, **kwargs)
        content = ContentDecodePolicy.deserialize_from_http_generics(response.http_response)
        return self._process_response(response=content, scopes=scopes, now=now)

    async def obtain_token_by_refresh_token(
        self, scopes: "Sequence[str]", refresh_token: str, **kwargs: "Any"
    ) -> "AccessToken":
        request = self._get_refresh_token_request(scopes, refresh_token)
        now = int(time.time())
        response = await self._pipeline.run(request, **kwargs)
        content = ContentDecodePolicy.deserialize_from_http_generics(response.http_response)
        return self._process_response(response=content, scopes=scopes, now=now)

    # pylint:disable=no-self-use
    def _build_pipeline(
        self,
        config: Configuration = None,
        policies: "Optional[List[Policy]]" = None,
        transport: "Optional[AsyncHttpTransport]" = None,
        **kwargs: "Any"
    ) -> AsyncPipeline:
        config = config or _create_config(**kwargs)
        policies = policies or [
            config.user_agent_policy,
            config.proxy_policy,
            config.retry_policy,
            config.logging_policy,
            DistributedTracingPolicy(**kwargs),
            HttpLoggingPolicy(**kwargs),
        ]
        if not transport:
            from azure.core.pipeline.transport import AioHttpTransport

            transport = AioHttpTransport(configuration=config)

        return AsyncPipeline(transport=transport, policies=policies)


def _create_config(**kwargs: "Any") -> Configuration:
    config = Configuration(**kwargs)
    config.proxy_policy = ProxyPolicy(**kwargs)
    config.logging_policy = NetworkTraceLoggingPolicy(**kwargs)
    config.retry_policy = AsyncRetryPolicy(**kwargs)
    config.user_agent_policy = UserAgentPolicy(base_user_agent=USER_AGENT, **kwargs)
    return config
