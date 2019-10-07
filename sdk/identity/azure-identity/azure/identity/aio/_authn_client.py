# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from typing import Any, Dict, Iterable, Mapping, Optional

from msal import TokenCache
from azure.core import Configuration
from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.policies import (
    AsyncRetryPolicy,
    ContentDecodePolicy,
    HTTPPolicy,
    NetworkTraceLoggingPolicy,
    ProxyPolicy,
)
from azure.core.pipeline.policies.distributed_tracing import DistributedTracingPolicy
from azure.core.pipeline.transport import AsyncHttpTransport
from azure.core.pipeline.transport.requests_asyncio import AsyncioRequestsTransport

from .._authn_client import AuthnClientBase


class AsyncAuthnClient(AuthnClientBase):  # pylint:disable=async-client-bad-name
    """Async authentication client"""

    # pylint:disable=missing-client-constructor-parameter-credential
    def __init__(
        self,
        auth_url: str,
        config: "Optional[Configuration]" = None,
        policies: Optional[Iterable[HTTPPolicy]] = None,
        transport: Optional[AsyncHttpTransport] = None,
        **kwargs: Mapping[str, Any]
    ) -> None:
        config = config or self._create_config(**kwargs)
        policies = policies or [
            ContentDecodePolicy(),
            config.retry_policy,
            config.logging_policy,
            DistributedTracingPolicy(),
        ]
        if not transport:
            transport = AsyncioRequestsTransport(**kwargs)
        self._pipeline = AsyncPipeline(transport=transport, policies=policies)
        super(AsyncAuthnClient, self).__init__(auth_url, **kwargs)

    async def request_token(
        self,
        scopes: Iterable[str],
        method: Optional[str] = "POST",
        headers: Optional[Mapping[str, str]] = None,
        form_data: Optional[Mapping[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        **kwargs: "Any"
    ) -> AccessToken:
        request = self._prepare_request(method, headers=headers, form_data=form_data, params=params)
        request_time = int(time.time())
        response = await self._pipeline.run(request, stream=False, **kwargs)
        token = self._deserialize_and_cache_token(response=response, scopes=scopes, request_time=request_time)
        return token

    async def obtain_token_by_refresh_token(self, scopes: Iterable[str], username: str) -> Optional[AccessToken]:
        """Acquire an access token using a cached refresh token. Returns ``None`` when that fails, or the cache has no
        refresh token. This is only used by SharedTokenCacheCredential and isn't robust enough for anything else."""

        # find account matching username
        accounts = self._cache.find(TokenCache.CredentialType.ACCOUNT, query={"username": username})
        for account in accounts:
            # try each refresh token that might work, return the first access token acquired
            for token in self.get_refresh_tokens(scopes, account):
                # currently we only support login.microsoftonline.com, which has an alias login.windows.net
                # TODO: this must change to support sovereign clouds
                environment = account.get("environment")
                if not environment or (environment not in self._auth_url and environment != "login.windows.net"):
                    continue

                request = self.get_refresh_token_grant_request(token, scopes)
                request_time = int(time.time())
                response = await self._pipeline.run(request, stream=False)
                try:
                    return self._deserialize_and_cache_token(
                        response=response, scopes=scopes, request_time=request_time
                    )
                except ClientAuthenticationError:
                    continue

        return None

    @staticmethod
    def _create_config(**kwargs: Mapping[str, Any]) -> Configuration:
        config = Configuration(**kwargs)
        config.logging_policy = NetworkTraceLoggingPolicy(**kwargs)
        config.retry_policy = AsyncRetryPolicy(**kwargs)
        config.proxy_policy = ProxyPolicy(**kwargs)
        return config
