# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Protocol-neutral HTTP transport for Foundry-backed storage clients.

:class:`FoundryStorageClient` owns the :class:`~azure.core.AsyncPipelineClient`,
its policy chain (retry, auth, logging, tracing), and the shared
``_send_storage_request`` helper. Protocol packages subclass it and add their
own resource methods and payload (de)serialization on top.
"""

# pylint: disable=docstring-missing-param,docstring-missing-return,docstring-missing-rtype
# pylint: disable=client-accepts-api-version-keyword

from __future__ import annotations

from typing import Any, Callable

from azure.core import AsyncPipelineClient
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.exceptions import ServiceRequestError, ServiceResponseError
from azure.core.pipeline import policies
from azure.core.rest import AsyncHttpResponse, HttpRequest

from azure.ai.agentserver.core._platform_headers import PLATFORM_ERROR_TAG
from azure.ai.agentserver.core._version import VERSION

from ._endpoint import FoundryStorageEndpoint
from ._errors import raise_for_storage_error
from ._policies import FoundryStorageLoggingPolicy, ServerVersionUserAgentPolicy

#: OAuth scope used to acquire bearer tokens for the Foundry storage API.
FOUNDRY_TOKEN_SCOPE = "https://ai.azure.com/.default"
#: Content type for JSON request bodies sent to the Foundry storage API.
JSON_CONTENT_TYPE = "application/json; charset=utf-8"


class FoundryStorageClient:
    """Base HTTP client for the Foundry storage API.

    :param credential: An async credential used to obtain bearer tokens.
    :type credential: AsyncTokenCredential
    :param endpoint: Resolved Foundry storage endpoint configuration.
    :type endpoint: FoundryStorageEndpoint
    :param get_server_version: Optional callable returning the server version
        string to use as the ``User-Agent`` header, evaluated lazily on each
        request. When ``None``, Azure Core's default ``UserAgentPolicy`` is used.
    :type get_server_version: Callable[[], str] | None
    :param sdk_moniker: SDK moniker for the default ``UserAgentPolicy``. Ignored
        when *get_server_version* is supplied.
    :type sdk_moniker: str | None
    """

    def __init__(
        self,
        credential: AsyncTokenCredential,
        endpoint: FoundryStorageEndpoint,
        *,
        get_server_version: Callable[[], str] | None = None,
        sdk_moniker: str | None = None,
        **kwargs: Any,
    ) -> None:
        self._endpoint = endpoint

        ua_policy: policies.UserAgentPolicy | ServerVersionUserAgentPolicy
        if get_server_version is not None:
            ua_policy = ServerVersionUserAgentPolicy(get_server_version)
        else:
            ua_policy = policies.UserAgentPolicy(sdk_moniker=sdk_moniker or f"ai-agentserver-core/{VERSION}")

        self._client: AsyncPipelineClient = AsyncPipelineClient(
            base_url=endpoint.storage_base_url,
            policies=[
                policies.RequestIdPolicy(),
                policies.HeadersPolicy(),
                ua_policy,
                policies.AsyncRetryPolicy(),
                policies.AsyncBearerTokenCredentialPolicy(credential, FOUNDRY_TOKEN_SCOPE),
                FoundryStorageLoggingPolicy(),
                # NOTE: ``ContentDecodePolicy`` is intentionally NOT included. It
                # eagerly decodes every response body as JSON and crashes with
                # ``UnicodeDecodeError`` on non-UTF-8 bodies (gzip payloads, HTML
                # error pages, transport-corrupted bodies). Serializers call
                # ``http_resp.text()`` directly with defensive error handling.
                policies.DistributedTracingPolicy(),
            ],
            **kwargs,
        )

    async def aclose(self) -> None:
        """Close the underlying HTTP pipeline client."""
        await self._client.close()

    async def __aenter__(self) -> "FoundryStorageClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.aclose()

    async def _send_storage_request(self, request: HttpRequest) -> AsyncHttpResponse:
        """Send an HTTP request to the Foundry storage API.

        Transport-level exceptions are tagged as platform errors before being
        re-raised; non-2xx responses raise a :class:`FoundryStorageError`.
        """
        try:
            http_resp: AsyncHttpResponse = await self._client.send_request(request)
        except (ServiceRequestError, ServiceResponseError, OSError) as exc:
            setattr(exc, PLATFORM_ERROR_TAG, True)
            raise
        raise_for_storage_error(http_resp)
        return http_resp
