# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Service constants and the Azure Core policies shared by both clients."""

from typing import Any, Union

from azure.core.configuration import Configuration
from azure.core.exceptions import (
    ClientAuthenticationError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
)
from azure.core.pipeline import policies

from ._version import VERSION

API_VERSION = "2026-09-01-preview"
RERANK_PATH = "/inference/semanticReranking"
DEFAULT_SCOPE = "https://dbinference.azure.com/.default"
SUBSCRIPTION_KEY_HEADER = "Ocp-Apim-Subscription-Key"
ERROR_MAP = {
    401: ClientAuthenticationError,
    404: ResourceNotFoundError,
    409: ResourceExistsError,
    304: ResourceNotModifiedError,
}


def create_configuration(
    authentication_policy: Union[policies.HTTPPolicy, policies.AsyncHTTPPolicy, policies.SansIOHTTPPolicy],
    *,
    asynchronous: bool = False,
    **kwargs: Any,
) -> Configuration:
    kwargs.setdefault("sdk_moniker", f"data-ai/{VERSION}")

    # Azure Core Configuration starts without authentication or retry policies.
    config: Configuration = Configuration(**kwargs)
    config.authentication_policy = kwargs.get("authentication_policy") or authentication_policy

    retry_policy = policies.AsyncRetryPolicy if asynchronous else policies.RetryPolicy
    redirect_policy = policies.AsyncRedirectPolicy if asynchronous else policies.RedirectPolicy
    config.retry_policy = kwargs.get("retry_policy") or retry_policy(**kwargs)
    config.redirect_policy = kwargs.get("redirect_policy") or redirect_policy(**kwargs)
    config.headers_policy = kwargs.get("headers_policy") or policies.HeadersPolicy(**kwargs)
    config.user_agent_policy = kwargs.get("user_agent_policy") or policies.UserAgentPolicy(**kwargs)
    config.proxy_policy = kwargs.get("proxy_policy") or policies.ProxyPolicy(**kwargs)
    config.custom_hook_policy = kwargs.get("custom_hook_policy") or policies.CustomHookPolicy(**kwargs)
    config.logging_policy = kwargs.get("logging_policy") or policies.NetworkTraceLoggingPolicy(**kwargs)
    config.http_logging_policy = kwargs.get("http_logging_policy") or policies.HttpLoggingPolicy(**kwargs)
    return config
