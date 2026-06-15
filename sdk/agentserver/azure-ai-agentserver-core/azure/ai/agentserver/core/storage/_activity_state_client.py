# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""HTTP-backed Foundry activity state storage client."""
# pylint: disable=docstring-missing-param,docstring-missing-return,docstring-missing-rtype
# pylint: disable=client-accepts-api-version-keyword

from __future__ import annotations

from typing import Any, Callable

from azure.core import AsyncPipelineClient
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.exceptions import ServiceRequestError, ServiceResponseError
from azure.core.pipeline import PipelineRequest, policies
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.core.rest import HttpRequest

from azure.ai.agentserver.core._platform_headers import PLATFORM_ERROR_TAG
from azure.ai.agentserver.core._version import VERSION

from ._foundry_errors import raise_for_storage_error
from ._foundry_logging_policy import FoundryStorageLoggingPolicy
from ._foundry_serializer import (
    deserialize_read_response,
    deserialize_write_response,
    serialize_delete_request,
    serialize_read_request,
    serialize_write_request,
)
from ._foundry_settings import FoundryActivityStateSettings

_FOUNDRY_TOKEN_SCOPE = "https://ai.azure.com/.default"
_JSON_CONTENT_TYPE = "application/json; charset=utf-8"


class _ServerVersionUserAgentPolicy(SansIOHTTPPolicy):  # type: ignore[type-arg]
    """Pipeline policy that sets the ``User-Agent`` header lazily from a callback."""

    def __init__(self, get_server_version: Callable[[], str]) -> None:
        super().__init__()
        self._get_server_version = get_server_version

    def on_request(self, request: PipelineRequest) -> None:  # type: ignore[type-arg]
        """Set the ``User-Agent`` header before the request is sent."""
        request.http_request.headers["User-Agent"] = self._get_server_version()


class FoundryActivityStateClient:
    """HTTP client for Foundry-managed Activity Protocol state storage."""

    def __init__(
        self,
        credential: AsyncTokenCredential,
        settings: FoundryActivityStateSettings | None = None,
        get_server_version: Callable[[], str] | None = None,
        *,
        api_version: str = "v1",
        **kwargs: Any,
    ) -> None:
        if settings is not None and settings.api_version != api_version:
            raise ValueError("api_version must match settings.api_version when both are supplied")
        self._settings = settings or FoundryActivityStateSettings.from_env(api_version=api_version)

        ua_policy: policies.UserAgentPolicy | _ServerVersionUserAgentPolicy
        if get_server_version is not None:
            ua_policy = _ServerVersionUserAgentPolicy(get_server_version)
        else:
            ua_policy = policies.UserAgentPolicy(sdk_moniker=f"ai-agentserver-core/{VERSION}")

        self._client: AsyncPipelineClient = AsyncPipelineClient(
            base_url=self._settings.storage_base_url,
            policies=[
                policies.RequestIdPolicy(),
                policies.HeadersPolicy(),
                ua_policy,
                policies.AsyncRetryPolicy(),
                policies.AsyncBearerTokenCredentialPolicy(credential, _FOUNDRY_TOKEN_SCOPE),
                FoundryStorageLoggingPolicy(),
                policies.DistributedTracingPolicy(),
            ],
            **kwargs,
        )

    async def aclose(self) -> None:
        """Close the underlying HTTP pipeline client."""
        await self._client.close()

    async def __aenter__(self) -> "FoundryActivityStateClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.aclose()

    async def _send_storage_request(self, request: HttpRequest) -> Any:
        """Send an HTTP request to the Foundry storage API."""
        try:
            http_resp = await self._client.send_request(request)
        except (ServiceRequestError, ServiceResponseError, OSError) as exc:
            setattr(exc, PLATFORM_ERROR_TAG, True)
            raise
        raise_for_storage_error(http_resp)
        return http_resp

    async def read(self, keys: list[str]) -> dict[str, dict[str, Any]]:
        """Read multiple Activity state records by raw M365 storage key."""
        body = serialize_read_request(keys)
        url = self._settings.build_url("activity/state:read")
        request = HttpRequest("POST", url, content=body, headers={"Content-Type": _JSON_CONTENT_TYPE})
        http_resp = await self._send_storage_request(request)
        return deserialize_read_response(http_resp.text())

    async def write(self, changes: dict[str, Any]) -> dict[str, dict[str, Any]]:
        """Upsert multiple Activity state records using last-write-wins semantics."""
        body = serialize_write_request(changes)
        url = self._settings.build_url("activity/state:write")
        request = HttpRequest("POST", url, content=body, headers={"Content-Type": _JSON_CONTENT_TYPE})
        http_resp = await self._send_storage_request(request)
        return deserialize_write_response(http_resp.text())

    async def delete(self, keys: list[str]) -> None:
        """Delete multiple Activity state records. Missing keys are ignored by the service."""
        body = serialize_delete_request(keys)
        url = self._settings.build_url("activity/state:delete")
        request = HttpRequest("POST", url, content=body, headers={"Content-Type": _JSON_CONTENT_TYPE})
        await self._send_storage_request(request)
