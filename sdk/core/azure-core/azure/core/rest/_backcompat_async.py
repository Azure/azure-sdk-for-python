# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
import asyncio
from collections.abc import AsyncIterator
from ._backcompat import _HttpResponseBackcompatMixinBase
from ..pipeline import PipelineContext, PipelineResponse, PipelineRequest
from ..pipeline._tools_async import await_result as _await_result

class _PartGenerator(AsyncIterator):
    """Until parts is a real async iterator, wrap the sync call.

    :param parts: An iterable of parts
    """

    def __init__(self, response) -> None:
        self._response = response
        self._parts = None

    async def _parse_response(self):
        from ..pipeline.transport._base_async import RestAsyncHttpClientTransportResponse
        responses = self._response._get_raw_parts(  # pylint: disable=protected-access
            http_response_type=RestAsyncHttpClientTransportResponse
        )
        if self._response.request.multipart_mixed_info:
            policies = self._response.request.multipart_mixed_info[
                1
            ]

            async def parse_responses(response):
                http_request = response.request
                context = PipelineContext(None)
                pipeline_request = PipelineRequest(http_request, context)
                pipeline_response = PipelineResponse(
                    http_request, response, context=context
                )

                for policy in policies:
                    await _await_result(
                        policy.on_response, pipeline_request, pipeline_response
                    )

            # Not happy to make this code asyncio specific, but that's multipart only for now
            # If we need trio and multipart, let's reinvesitgate that later
            await asyncio.gather(*[parse_responses(res) for res in responses])

        return responses

    async def __anext__(self):
        if not self._parts:
            self._parts = iter(await self._parse_response())

        try:
            return next(self._parts)
        except StopIteration:
            raise StopAsyncIteration()

class AsyncHttpResponseBackcompatMixin(_HttpResponseBackcompatMixinBase):
    def stream_download(self, pipeline, **kwargs):
        if kwargs.get("decompress"):
            return self.iter_bytes()
        return self.iter_raw()

    def parts(self):
        """Assuming the content-type is multipart/mixed, will return the parts as an async iterator.

        :rtype: AsyncIterator
        :raises ValueError: If the content is not multipart/mixed
        """
        if not self.content_type or not self.content_type.startswith("multipart/mixed"):
            raise ValueError(
                "You can't get parts if the response is not multipart/mixed"
            )

        return _PartGenerator(self)
