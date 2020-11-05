# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import os
from typing import TYPE_CHECKING, Union

from azure.core.pipeline.policies import (
    AsyncHTTPPolicy,
    DistributedTracingPolicy,
    HeadersPolicy,
    HttpLoggingPolicy,
    UserAgentPolicy,
    NetworkTraceLoggingPolicy,
    SansIOHTTPPolicy,
)

from .._internal import AsyncContextManager
from .._internal.managed_identity_client import AsyncManagedIdentityClient, _get_configuration
from .._internal.get_token_mixin import GetTokenMixin
from ... import CredentialUnavailableError
from ..._constants import EnvironmentVariables
from ..._credentials.azure_arc import ArcChallengeAuthPolicyBase, _get_request, _get_secret_key
from ..._internal.user_agent import USER_AGENT

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, List, Optional
    from azure.core.configuration import Configuration
    from azure.core.credentials import AccessToken
    from azure.core.pipeline import PipelineRequest
    from azure.core.pipeline.transport import AsyncHttpResponse

PolicyType = Union[AsyncHTTPPolicy, SansIOHTTPPolicy]


class AzureArcCredential(AsyncContextManager, GetTokenMixin):
    def __init__(self, **kwargs: "Any") -> None:
        super().__init__()

        client_args = _get_client_args(**kwargs)
        if client_args:
            self._client = AsyncManagedIdentityClient(**client_args)
        else:
            self._client = None

    async def get_token(  # pylint:disable=invalid-overridden-method
        self, *scopes: str, **kwargs: "Any"
    ) -> "AccessToken":
        if not self._client:
            raise CredentialUnavailableError(
                message="Service Fabric managed identity configuration not found in environment"
            )

        return await super().get_token(*scopes, **kwargs)

    async def close(self) -> None:
        await self._client.close()  # pylint:disable=no-member

    async def _acquire_token_silently(self, *scopes: str) -> "Optional[AccessToken]":
        return self._client.get_cached_token(*scopes)

    async def _request_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":
        return await self._client.request_token(*scopes, **kwargs)


def _get_policies(config: Configuration, **kwargs: Any) -> List[PolicyType]:
    return [
        HeadersPolicy(**kwargs),
        UserAgentPolicy(base_user_agent=USER_AGENT, **kwargs),
        config.proxy_policy,
        config.retry_policy,
        ArcChallengeAuthPolicy(),
        NetworkTraceLoggingPolicy(**kwargs),
        DistributedTracingPolicy(**kwargs),
        HttpLoggingPolicy(**kwargs),
    ]


def _get_client_args(**kwargs: Any) -> Optional[dict]:
    identity_config = kwargs.pop("_identity_config", None) or {}

    url = os.environ.get(EnvironmentVariables.IDENTITY_ENDPOINT)
    if not url:
        # Azure Arc managed identity isn't available in this environment
        return None

    config = _get_configuration()

    return dict(
        kwargs,
        _identity_config=identity_config,
        base_headers={"Metadata": "true"},
        policies=_get_policies(config),
        request_factory=functools.partial(_get_request, url),
    )


class ArcChallengeAuthPolicy(ArcChallengeAuthPolicyBase, AsyncHTTPPolicy):
    """Policy for handling Azure Arc's challenge authentication"""

    def __init__(self, **kwargs: "Any") -> None:
        super().__init__(**kwargs)

    async def send(self, request: "PipelineRequest") -> "AsyncHttpResponse":
        response = await self.next.send(request)

        if response.http_response.status_code == 401:
            secret_key = _get_secret_key(response)
            request.http_request.headers["Authorization"] = "Basic {}".format(secret_key)
            response = await self.next.send(request)

        return response
