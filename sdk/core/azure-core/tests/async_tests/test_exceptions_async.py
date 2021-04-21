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
import pytest
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.transport import AioHttpTransport, HttpRequest
from azure.core.exceptions import HttpResponseError


@pytest.mark.asyncio
async def test_http_response_error_stream():
    request = HttpRequest("GET", url="https://httpbin.org/get")  # want to actually get a response body
    async with AsyncPipeline(AioHttpTransport()) as pipeline:
        pipeline_response = await pipeline.run(request, stream=True)
        http_response = pipeline_response.http_response
        http_response.status_code = 400
        with pytest.raises(HttpResponseError) as error:
            http_response.raise_for_status()
        e = error.value
        assert e.message == "Operation returned an invalid status 'OK'"
        with pytest.raises(ValueError):
            e.error
        with pytest.raises(ValueError):
            e.model
        await http_response.load_body()
        e.error  # technically not a value here, since I can't figure out how to get an odatav4 error format response
