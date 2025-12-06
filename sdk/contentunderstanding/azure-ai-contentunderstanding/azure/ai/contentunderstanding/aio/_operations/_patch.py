# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

SDK-FIX: Fix copy analyzer endpoint path and status code handling for async operations.
- URL path: Change from ":copyAnalyzer" to ":copy" (emitter generates wrong endpoint path)
- Status codes: Accept both 201 and 202 (service inconsistently returns both status codes)
"""

import json
from collections.abc import MutableMapping
from io import IOBase
from typing import Any, AsyncIterator, IO, Optional, Union

from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    StreamClosedError,
    StreamConsumedError,
    map_error,
)
from azure.core.pipeline import PipelineResponse
from azure.core.utils import case_insensitive_dict

__all__: list[str] = []


def patch_sdk():
    """Patch the SDK to fix async copy analyzer operations.

    This function:
    1. Uses the patched build_content_understanding_copy_analyzer_request (from sync operations)
    2. Wraps _copy_analyzer_initial method to accept both 201 and 202 status codes
    """
    from ..._operations import _operations as sync_operations
    from . import _operations  # pylint: disable=protected-access

    # Note: The request builder is shared between sync and async, so it's already patched
    # by the sync _patch.py. We just need to patch the async _copy_analyzer_initial method.

    # SDK-FIX: Wrap _copy_analyzer_initial to accept both 201 and 202 status codes
    _original_copy_initial = _operations._ContentUnderstandingClientOperationsMixin._copy_analyzer_initial  # pylint: disable=protected-access

    async def _patched_copy_analyzer_initial(  # pylint: disable=protected-access
        self,
        analyzer_id: str,
        body: Union[_operations.JSON, IO[bytes]] = _operations._Unset,
        *,
        source_analyzer_id: str = _operations._Unset,
        allow_replace: Optional[bool] = None,
        source_azure_resource_id: Optional[str] = None,
        source_region: Optional[str] = None,
        **kwargs: Any
    ) -> AsyncIterator[bytes]:
        """Patched version that accepts both 201 and 202 status codes.

        :param analyzer_id: The analyzer ID for the copy operation.
        :type analyzer_id: str
        :param body: The request body.
        :type body: Union[JSON, IO[bytes]]
        :keyword source_analyzer_id: The source analyzer ID.
        :paramtype source_analyzer_id: str
        :keyword allow_replace: Whether to allow replacing an existing analyzer.
        :paramtype allow_replace: Optional[bool]
        :keyword source_azure_resource_id: The source Azure resource ID.
        :paramtype source_azure_resource_id: Optional[str]
        :keyword source_region: The source region.
        :paramtype source_region: Optional[str]
        :return: An async iterator of bytes.
        :rtype: AsyncIterator[bytes]
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: _operations.ClsType[AsyncIterator[bytes]] = kwargs.pop("cls", None)

        if body is _operations._Unset:
            if source_analyzer_id is _operations._Unset:
                raise TypeError("missing required argument: source_analyzer_id")
            body = {
                "sourceAnalyzerId": source_analyzer_id,
                "sourceAzureResourceId": source_azure_resource_id,
                "sourceRegion": source_region,
            }
            body = {k: v for k, v in body.items() if v is not None}
        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            from ..._utils.model_base import SdkJSONEncoder
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = sync_operations.build_content_understanding_copy_analyzer_request(
            analyzer_id=analyzer_id,
            allow_replace=allow_replace,
            content_type=content_type,
            api_version=self._config.api_version,
            content=_content,
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        _request.url = self._client.format_url(_request.url, **path_format_arguments)

        _stream = True
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # type: ignore # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        # SDK-FIX: Accept both 201 and 202 (service inconsistently returns both status codes)
        if response.status_code not in [201, 202]:
            try:
                await response.read()  # Load the body in memory and close the socket
            except (StreamConsumedError, StreamClosedError):
                pass
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        response_headers = {}
        response_headers["Operation-Location"] = self._deserialize("str", response.headers.get("Operation-Location"))
        response_headers["x-ms-client-request-id"] = self._deserialize(
            "str", response.headers.get("x-ms-client-request-id")
        )

        deserialized = response.iter_bytes()

        if cls:
            return cls(pipeline_response, deserialized, response_headers)  # type: ignore

        return deserialized  # type: ignore

    _operations._ContentUnderstandingClientOperationsMixin._copy_analyzer_initial = _patched_copy_analyzer_initial  # pylint: disable=protected-access
