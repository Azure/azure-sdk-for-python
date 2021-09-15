# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any, Callable, Dict, IO, Optional, TypeVar, TYPE_CHECKING
from urllib.parse import urlparse

from azure.core.pipeline import PipelineResponse
from azure.core.pipeline.transport import AsyncHttpResponse, HttpRequest
from azure.core.exceptions import (ClientAuthenticationError, HttpResponseError,
    ResourceExistsError, ResourceNotFoundError, map_error)

from .._generated import models as _models

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Any, Callable, Dict, Generic, Optional, TypeVar

    T = TypeVar('T')
    ClsType = Optional[Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse],
        T, Dict[str, Any]], Any]]

class ContentDownloader():
    def __init__(self, client, config, serializer, deserializer) -> None:
        self._client = client
        self._serialize = serializer
        self._deserialize = deserializer
        self._config = config

    async def download(
        self,
        content_url, #type: str
        http_range = None, #type: Optional[str]
        **kwargs #type: Any
    ) -> IO:
        """The Download operation downloads content.
        :param content_url: The URL where the content is located
        :type content_url: str
        :param http_range: Return only the bytes of the content in the specified range.
        :type http_range: str
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: IO, or the result of cls(response)
        :rtype: IO
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        cls = kwargs.pop('cls', None)  # type: ClsType[IO]
        error_map = {
            409: ResourceExistsError,
            400: lambda response: HttpResponseError(response=response,
                                                    model=self._deserialize(_models.CommunicationErrorResponse,
                                                                            response)),
            401: lambda response: ClientAuthenticationError(response=response,
                                                            model=self._deserialize(_models.CommunicationErrorResponse,
                                                                                    response)),
            403: lambda response: HttpResponseError(response=response,
                                                    model=self._deserialize(_models.CommunicationErrorResponse,
                                                                            response)),
            404: lambda response: ResourceNotFoundError(response=response,
                                                        model=self._deserialize(_models.CommunicationErrorResponse,
                                                                                response)),
            500: lambda response: HttpResponseError(response=response,
                                                    model=self._deserialize(_models.CommunicationErrorResponse,
                                                                            response)),
        }
        error_map.update(kwargs.pop('error_map', {}))
        
        # Construct URL
        uri_to_sign_with = self._get_url_to_sign_request_with(content_url)

        # Construct parameters
        query_parameters = {}  # type: Dict[str, Any]
        # Construct headers
        header_parameters = {}  # type: Dict[str, Any]
        header_parameters['UriToSignWith'] = self._serialize.header("uri_to_sign_with", uri_to_sign_with, 'str')

        path_format_arguments = {
            'url': self._serialize.url("self._config.url", self._config.url, 'str', skip_quote=True),
        }
        url = self._client.format_url(content_url, **path_format_arguments)

        # Construct headers
        header_parameters = {}  # type: Dict[str, Any]
        if http_range is not None:
            header_parameters['x-ms-range'] = self._serialize.header("range", http_range, 'str')

        request = self._client.get(url, query_parameters, header_parameters)
        pipeline_response = await self._client._pipeline.run(request, stream=True, **kwargs)
        response = pipeline_response.http_response

        if response.status_code not in [200, 206]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        deserialized = response.stream_download(self._client._pipeline)

        if cls:
            return cls(pipeline_response, deserialized, {})

        return deserialized

    def _get_url_to_sign_request_with(self, content_url: str):
        path = urlparse(content_url).path
        return self._config.endpoint + path