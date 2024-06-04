# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Optional, Type
from types import TracebackType
from copy import deepcopy

from corehttp.runtime import AsyncPipelineClient
from corehttp.runtime._pipeline_client_async import _Coroutine


class AsyncMockRestClient(object):
    def __init__(self, port, *, transport=None, **kwargs):
        kwargs.setdefault("sdk_moniker", "autorestswaggerbatfileservice/1.0.0b1")

        self._client = AsyncPipelineClient(endpoint="http://localhost:{}".format(port), transport=transport, **kwargs)

    def send_request(self, request, **kwargs) -> _Coroutine:
        """Runs the network request through the client's chained policies.
        >>> from corehttp.rest import HttpRequest
        >>> request = HttpRequest("GET", "http://localhost:3000/helloWorld")
        <HttpRequest [GET], url: 'http://localhost:3000/helloWorld'>
        >>> response = await client.send_request(request)
        <AsyncHttpResponse: 200 OK>

        :param request: The network request you want to make. Required.
        :type request: ~corehttp.rest.HttpRequest
        :keyword bool stream: Whether the response payload will be streamed. Defaults to False.
        :return: The response of your network call. Does not do error handling on your response.
        :rtype: ~corehttp.rest.AsyncHttpResponse
        """
        request_copy = deepcopy(request)
        request_copy.url = self._client.format_url(request_copy.url)
        return self._client.send_request(request_copy, **kwargs)  # type: ignore

    async def close(self) -> None:
        await self._client.close()

    async def __aenter__(self):
        await self._client.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ) -> None:
        await self._client.__aexit__(exc_type, exc_value, traceback)
