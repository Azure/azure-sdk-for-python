# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# pylint: disable=unsubscriptable-object
# disabled unsubscriptable-object because of pylint bug referenced here:
# https://github.com/PyCQA/pylint/issues/3882

from typing import Any, IO, Optional, TYPE_CHECKING
from urllib.parse import urlparse

from azure.core.exceptions import HttpResponseError, map_error
from azure.core.pipeline import PipelineResponse
from azure.core.pipeline.transport import AsyncHttpResponse, HttpRequest
from ..utils._utils import CallingServerUtils

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports,unsubscriptable-object
    from typing import Callable, Dict, Generic, TypeVar

    T = TypeVar('T')
    ClsType = Optional[Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse],
        T, Dict[str, Any]], Any]]

class ContentDownloader:
    def __init__(self, client, config, serializer, deserializer) -> None:
        self._client = client
        self._serialize = serializer
        self._deserialize = deserializer
        self._config = config

    async def download(
        self,
        content_url: str,
        http_range: Optional[str] = None,
        **kwargs: Any
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
        error_map = CallingServerUtils.get_error_response_map(
            kwargs.pop('error_map', {}))


        # Construct URL
        uri_to_sign_with = self._get_url_to_sign_request_with(content_url)
        # Construct parameters
        query_parameters = {}  # type: Dict[str, Any]
        # Construct headers
        header_parameters = {}  # type: Dict[str, Any]
        header_parameters['UriToSignWith'] = self._serialize.header("uri_to_sign_with", uri_to_sign_with, 'str')
        if http_range is not None:
            header_parameters['Range'] = self._serialize.header("range", http_range, 'str')

        request = self._client.get(content_url, query_parameters, header_parameters)
        pipeline_response = await self._client._pipeline.run(request, stream=True, **kwargs) # pylint: disable=protected-access
        response = pipeline_response.http_response

        if response.status_code not in [200, 206]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        deserialized = response.stream_download(self._client._pipeline) # pylint: disable=protected-access

        if cls:
            return cls(pipeline_response, deserialized, {})

        return deserialized

    def _get_url_to_sign_request_with(self, content_url: str):
        path = urlparse(content_url).path
        return self._config.endpoint + path
