# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Synchronous reranking requests over the client's existing Azure Core pipeline."""

from typing import Any

from azure.core import PipelineClient
from azure.core.exceptions import map_error
from azure.core.rest import HttpRequest, HttpResponse
from azure.core.utils import case_insensitive_dict

from ._shared import ERROR_MAP, RERANK_PATH


class _SemanticReranker:
    """Internal reranking operation; the parent client owns the HTTP pipeline."""

    def __init__(
        self,
        endpoint: str,
        client: PipelineClient[HttpRequest, HttpResponse],
        *,
        api_version: str,
    ) -> None:
        self._url = endpoint.rstrip("/") + RERANK_PATH
        self._client = client
        self._api_version = api_version

    def rerank(self, request: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        headers = case_insensitive_dict({"Accept": "application/json"})
        headers.update(kwargs.pop("headers", {}) or {})
        params = dict(kwargs.pop("params", {}) or {})
        params["api-version"] = self._api_version
        error_map = {**ERROR_MAP, **(kwargs.pop("error_map", {}) or {})}

        http_request = HttpRequest("POST", self._url, headers=headers, params=params, json=request)
        response = self._client.send_request(http_request, **kwargs)
        map_error(status_code=response.status_code, response=response, error_map=error_map)
        response.raise_for_status()
        return response.json()
