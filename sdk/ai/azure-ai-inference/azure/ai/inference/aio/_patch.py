# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from io import IOBase
import json
import sys
from typing import List
from .. import models as _models
from ._client import ModelClient as ModelClientGenerated
from typing import Callable, Any, Union, IO, Optional, Dict, TypeVar
from azure.core.utils import case_insensitive_dict
from azure.core.pipeline import PipelineResponse
from azure.core.rest import AsyncHttpResponse, HttpRequest
from azure.core.tracing.decorator_async import distributed_trace_async
from .._model_base import SdkJSONEncoder, _deserialize
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    map_error,
)
from .._operations._operations import build_model_get_chat_completions_request
 
if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports
JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object
_Unset: Any = object()
T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse], T, Dict[str, Any]], Any]]


class ModelClient(ModelClientGenerated):
    @distributed_trace_async
    async def get_streaming_chat_completions(
        self,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        messages: List[_models.ChatRequestMessage] = _Unset,
        model_deployment: Optional[str] = None,
        extras: Optional[Dict[str, str]] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[_models.ChatCompletionsResponseFormat] = None,
        stop: Optional[List[str]] = None,
        tools: Optional[List[_models.ChatCompletionsToolDefinition]] = None,
        tool_choice: Optional[
            Union[str, _models.ChatCompletionsToolSelectionPreset, _models.ChatCompletionsNamedToolSelection]
        ] = None,
        seed: Optional[int] = None,
        **kwargs: Any
    ) -> _models.ChatCompletionsDeltaIterator:

        error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[_models.ChatCompletions] = kwargs.pop("cls", None)

        if body is _Unset:
            if messages is _Unset:
                raise TypeError("missing required argument: messages")
            body = {
                "extras": extras,
                "frequency_penalty": frequency_penalty,
                "max_tokens": max_tokens,
                "messages": messages,
                "presence_penalty": presence_penalty,
                "response_format": response_format,
                "seed": seed,
                "stop": stop,
                "stream": True,
                "temperature": temperature,
                "tool_choice": tool_choice,
                "tools": tools,
                "top_p": top_p,
            }
            body = {k: v for k, v in body.items() if v is not None}
        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_model_get_chat_completions_request(
            model_deployment=model_deployment,
            content_type=content_type,
            api_version=self._config.api_version,
            content=_content,
            headers=_headers,
            params=_params,
        )
        _request.url = self._client.format_url(_request.url)

        kwargs.pop("stream", True) # Remove stream from kwargs (ignore value set by the application)
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # type: ignore # pylint: disable=protected-access
            _request, stream=True, **kwargs
        )
    
        response = pipeline_response.http_response

        if response.status_code not in [200]:
            await response.read()  # Load the body in memory and close the socket
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        return _models.ChatCompletionsDeltaIterator(response.iter_bytes())


__all__: List[str] = ["ModelClient"]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
