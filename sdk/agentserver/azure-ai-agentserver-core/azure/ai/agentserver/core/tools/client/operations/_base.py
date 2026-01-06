# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from __future__ import annotations

from abc import ABC
from typing import Any, ClassVar, MutableMapping, Type

from azure.core import AsyncPipelineClient
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError, ResourceExistsError, \
    ResourceNotFoundError, ResourceNotModifiedError, map_error
from azure.core.rest import AsyncHttpResponse, HttpRequest

ErrorMapping = MutableMapping[int, Type[HttpResponseError]]


class BaseOperations(ABC):
    DEFAULT_ERROR_MAP: ClassVar[ErrorMapping] = {
        401: ClientAuthenticationError,
        404: ResourceNotFoundError,
        409: ResourceExistsError,
        304: ResourceNotModifiedError,
    }

    def __init__(self, client: AsyncPipelineClient, error_map: ErrorMapping | None = None) -> None:
        self.client = client
        self._error_map = self._prepare_error_map(error_map)

    @classmethod
    def _prepare_error_map(cls, custom_error_map: ErrorMapping | None = None) -> MutableMapping:
        """Prepare error map by merging default and custom error mappings.

        :param custom_error_map: Custom error mappings to merge
        :return: Merged error map
        """
        error_map = cls.DEFAULT_ERROR_MAP
        if custom_error_map:
            error_map = dict(cls.DEFAULT_ERROR_MAP)
            error_map.update(custom_error_map)
        return error_map

    async def send_request(self, request: HttpRequest, *, stream: bool = False, **kwargs: Any) -> AsyncHttpResponse:
        """Send an HTTP request.

        :param request: HTTP request
        :param stream: Stream to be used for HTTP requests
        :param kwargs: Keyword arguments

        :return: Response object
        """
        response: AsyncHttpResponse = await self.client.send_request(request, stream=stream, **kwargs)
        self.handle_response_error(response)
        return response

    def handle_response_error(self, response: AsyncHttpResponse) -> None:
        """Handle HTTP response errors.

        :param response: HTTP response to check
        :raises HttpResponseError: If response status is not 200
        """
        if response.status_code not in [200]:
            map_error(status_code=response.status_code, response=response, error_map=self._error_map)
            raise HttpResponseError(response=response)
