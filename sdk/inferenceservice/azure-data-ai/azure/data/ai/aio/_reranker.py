# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Asynchronous reranking requests over the client's existing Azure Core pipeline."""

from typing import Any

from azure.core import AsyncPipelineClient
from azure.core.exceptions import map_error
from azure.core.rest import AsyncHttpResponse, HttpRequest
from azure.core.utils import case_insensitive_dict

from .._shared import ERROR_MAP, RERANK_PATH


class _AsyncSemanticReranker:
    """Internal reranking operation; the parent client owns the HTTP pipeline."""

    def __init__(
        self,
        endpoint: str,
        client: AsyncPipelineClient[HttpRequest, AsyncHttpResponse],
        *,
        api_version: str,
    ) -> None:
        self._url = endpoint.rstrip("/") + RERANK_PATH
        self._client = client
        self._api_version = api_version

    async def rerank(self, request: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        headers = case_insensitive_dict({"Accept": "application/json"})
        headers.update(kwargs.pop("headers", {}) or {})
        params = dict(kwargs.pop("params", {}) or {})
        params["api-version"] = self._api_version
        error_map = {**ERROR_MAP, **(kwargs.pop("error_map", {}) or {})}

        http_request = HttpRequest("POST", self._url, headers=headers, params=params, json=request)
        response = await self._client.send_request(http_request, **kwargs)
        map_error(status_code=response.status_code, response=response, error_map=error_map)
        response.raise_for_status()
        return response.json()
