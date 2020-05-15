# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from typing import TYPE_CHECKING

from azure.core.configuration import Configuration
from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import (
    NetworkTraceLoggingPolicy,
    RetryPolicy,
    ProxyPolicy,
    UserAgentPolicy,
    ContentDecodePolicy,
    DistributedTracingPolicy,
    HttpLoggingPolicy,
)

from .aad_client_base import AadClientBase
from .user_agent import USER_AGENT

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, List, Optional, Sequence, Union
    from azure.core.credentials import AccessToken
    from azure.core.pipeline.policies import HTTPPolicy, SansIOHTTPPolicy
    from azure.core.pipeline.transport import HttpTransport

    Policy = Union[HTTPPolicy, SansIOHTTPPolicy]


class AadClient(AadClientBase):
    def obtain_token_by_authorization_code(self, scopes, code, redirect_uri, client_secret=None, **kwargs):
        # type: (str, str, Sequence[str], Optional[str], **Any) -> AccessToken
        request = self._get_auth_code_request(
            scopes=scopes, code=code, redirect_uri=redirect_uri, client_secret=client_secret
        )
        now = int(time.time())
        response = self._pipeline.run(request, stream=False, **kwargs)
        content = ContentDecodePolicy.deserialize_from_http_generics(response.http_response)
        return self._process_response(response=content, scopes=scopes, now=now)

    def obtain_token_by_refresh_token(self, scopes, refresh_token, **kwargs):
        # type: (str, Sequence[str], **Any) -> AccessToken
        request = self._get_refresh_token_request(scopes, refresh_token)
        now = int(time.time())
        response = self._pipeline.run(request, stream=False, **kwargs)
        content = ContentDecodePolicy.deserialize_from_http_generics(response.http_response)
        return self._process_response(response=content, scopes=scopes, now=now)

    # pylint:disable=no-self-use
    def _build_pipeline(self, config=None, policies=None, transport=None, **kwargs):
        # type: (Optional[Configuration], Optional[List[Policy]], Optional[HttpTransport], **Any) -> Pipeline
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
            from azure.core.pipeline.transport import RequestsTransport

            transport = RequestsTransport(**kwargs)

        return Pipeline(transport=transport, policies=policies)


def _create_config(**kwargs):
    # type: (**Any) -> Configuration
    config = Configuration(**kwargs)
    config.logging_policy = NetworkTraceLoggingPolicy(**kwargs)
    config.retry_policy = RetryPolicy(**kwargs)
    config.proxy_policy = ProxyPolicy(**kwargs)
    config.user_agent_policy = UserAgentPolicy(base_user_agent=USER_AGENT, **kwargs)
    return config
