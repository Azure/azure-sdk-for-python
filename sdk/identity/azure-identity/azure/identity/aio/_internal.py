# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# ------------------------------------------------------------------------
import os
from typing import Any, Dict, Optional

from azure.core import Configuration
from azure.core.pipeline.policies import ContentDecodePolicy, HeadersPolicy, NetworkTraceLoggingPolicy, AsyncRetryPolicy

from ._authn_client import AsyncAuthnClient
from ..constants import Endpoints, MSI_ENDPOINT, MSI_SECRET
from ..exceptions import AuthenticationError


class AsyncImdsCredential:
    def __init__(self, config: Optional[Configuration] = None, **kwargs: Dict[str, Any]) -> None:
        config = config or self.create_config(**kwargs)
        policies = [config.header_policy, ContentDecodePolicy(), config.retry_policy, config.logging_policy]
        self._client = AsyncAuthnClient(Endpoints.IMDS, config, policies, **kwargs)

    async def get_token(self, *scopes: str) -> str:
        if len(scopes) != 1:
            raise ValueError("this credential supports one scope per request")
        token = self._client.get_cached_token(scopes)
        if not token:
            resource = scopes[0]
            if resource.endswith("/.default"):
                resource = resource[:-len("/.default")]
            token = await self._client.request_token(
                scopes, method="GET", params={"api-version": "2018-02-01", "resource": resource}
            )
        return token

    @staticmethod
    def create_config(**kwargs: Dict[str, Any]) -> Configuration:
        timeout = kwargs.pop("connection_timeout", 2)
        config = Configuration(connection_timeout=timeout, **kwargs)
        config.header_policy = HeadersPolicy(base_headers={"Metadata": "true"}, **kwargs)
        config.logging_policy = NetworkTraceLoggingPolicy(**kwargs)
        retries = kwargs.pop("retry_total", 5)
        config.retry_policy = AsyncRetryPolicy(
            retry_total=retries, retry_on_status_codes=[404, 429] + list(range(500, 600)), **kwargs
        )
        return config


class AsyncMsiCredential:
    def __init__(self, config: Optional[Configuration] = None, **kwargs: Dict[str, Any]) -> None:
        config = config or self.create_config(**kwargs)
        policies = [ContentDecodePolicy(), config.retry_policy, config.logging_policy]
        endpoint = os.environ.get(MSI_ENDPOINT)
        if not endpoint:
            raise ValueError("expected environment variable {} has no value".format(MSI_ENDPOINT))
        self._client = AsyncAuthnClient(endpoint, config, policies, **kwargs)

    async def get_token(self, *scopes: str) -> str:
        if len(scopes) != 1:
            raise ValueError("this credential supports only one scope per request")
        token = self._client.get_cached_token(scopes)
        if not token:
            resource = scopes[0]
            if resource.endswith("/.default"):
                resource = resource[:-len("/.default")]
            secret = os.environ.get(MSI_SECRET)
            if not secret:
                raise AuthenticationError("{} environment variable has no value".format(MSI_SECRET))
            # TODO: support user-assigned client id
            token = await self._client.request_token(
                scopes,
                method="GET",
                headers={"secret": secret},
                params={"api-version": "2017-09-01", "resource": resource},
            )
        return token

    @staticmethod
    def create_config(**kwargs: Dict[str, Any]) -> Configuration:
        timeout = kwargs.pop("connection_timeout", 2)
        config = Configuration(connection_timeout=timeout, **kwargs)
        config.logging_policy = NetworkTraceLoggingPolicy(**kwargs)
        retries = kwargs.pop("retry_total", 5)
        config.retry_policy = AsyncRetryPolicy(
            retry_total=retries, retry_on_status_codes=[404, 429] + list(range(500, 600)), **kwargs
        )
        return config
