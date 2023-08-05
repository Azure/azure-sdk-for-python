# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any

from  urllib.parse import ParseResult, urlparse
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    map_error,
)
from azure.core.pipeline import PipelineResponse
from azure.core.pipeline.transport import HttpResponse
from azure.core.rest import HttpRequest
from azure.core.utils import case_insensitive_dict

from .._generated import models as _models
from .._generated._serialization import Serializer
from .._generated.aio.operations import CallRecordingOperations

_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False


class ContentDownloader(object):
    def __init__(
            self,
            call_recording_client:CallRecordingOperations
        ) -> None:

        self._call_recording_client = call_recording_client

    async def download_streaming(  # pylint: disable=inconsistent-return-statements
        self, source_location: str, offset: int, length: int, **kwargs: Any
    ) -> HttpResponse:
        """Download a stream of the call recording.

        :param source_location: The source location. Required.
        :type source_location: str
        :param offset: Offset byte. Not required.
        :type offset: int
        :param length: how many bytes. Not required.
        :type length: int
        :return: HttpResponse (octet-stream)
        :rtype: HttpResponse (octet-stream)
        """

        if length is not None and offset is None:
            raise ValueError("Offset value must not be None if length is set.")
        if length is not None:
            length = offset + length - 1  # Service actually uses an end-range inclusive index

        error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        parsedEndpoint:ParseResult = urlparse(
            self._call_recording_client._config.endpoint # pylint: disable=protected-access
        )

        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}
        request = _build_call_recording_download_recording_request(
            source_location = source_location,
            headers =_headers,
            params =_params,
            start = offset,
            end = length,
            host = parsedEndpoint.hostname
        )

        pipeline_response: PipelineResponse = await self._call_recording_client._client._pipeline.run(  # pylint: disable=protected-access
            request, stream = True, **kwargs
        )
        response = pipeline_response.http_response

        if response.status_code in [200, 206]:
            return response

        map_error(status_code = response.status_code, response = response, error_map = error_map)
        error = self._call_recording_client._deserialize.failsafe_deserialize(  # pylint: disable=protected-access
            _models.CommunicationErrorResponse, pipeline_response
        )
        raise HttpResponseError(response = response, model = error)

    async def delete_recording(  # pylint: disable=inconsistent-return-statements
        self, recording_location: str, **kwargs: Any
    ) -> None:
        """Delete a call recording.

        :param recording_location: The recording location. Required.
        :type recording_location: str
        """

        error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        parsed_endpoint:ParseResult = urlparse(
            self._call_recording_client._config.endpoint  # pylint: disable=protected-access
        )

        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}
        request = _build_call_recording_delete_recording_request(
            recording_location = recording_location,
            headers =_headers,
            params =_params,
            host = parsed_endpoint.hostname
        )

        pipeline_response: PipelineResponse = await self._call_recording_client.await_client._pipeline.run(  # pylint: disable=protected-access
            request, stream = False, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200]:
            map_error(status_code=response.status_code, response = response, error_map=error_map)
            error = self._call_recording_client._deserialize.failsafe_deserialize( # pylint: disable=protected-access
                _models.CommunicationErrorResponse, pipeline_response
            )
            raise HttpResponseError(response=response, model=error)

def _build_call_recording_delete_recording_request(recording_location: str, host: str, **kwargs: Any) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

    # Construct headers
    _headers["x-ms-host"] = _SERIALIZER.header("x-ms-host", host, "str")
    return HttpRequest(
        method = "DELETE",
        url = recording_location,
        params = _params,
        headers = _headers,
        **kwargs
    )

def _build_call_recording_download_recording_request(source_location: str,
                                                    start:int,
                                                    end:int,
                                                    host:str,
                                                    **kwargs: Any
                                                ) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

    rangeHeader = "bytes=" + str(start)
    if end:
        rangeHeader += "-" + str(end)
    # Construct headers
    _headers["Range"] = _SERIALIZER.header("range", rangeHeader, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", "application/json", "str")
    _headers["x-ms-host"] = _SERIALIZER.header("x-ms-host", host, "str")
    return HttpRequest(method = "GET", url = source_location, params = _params, headers = _headers, **kwargs)
