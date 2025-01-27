# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# --------------------------------------------------------------------------

import pytest

from corehttp.rest import HttpRequest
from corehttp.streaming import AsyncStream
from corehttp.streaming._decoders import JSONLDecoder


@pytest.fixture
def deserialization_callback():
    def _callback(_, json):
        return json

    return _callback


@pytest.fixture
def stream(client, deserialization_callback):
    async def _callback(request, **kwargs):
        initial_response = await client.send_request(request=request, stream=True, _return_pipeline_response=True)
        return AsyncStream(
            deserialization_callback=deserialization_callback,
            response=initial_response,
        )

    return _callback


@pytest.mark.asyncio
async def test_stream_jsonl_basic(stream):
    jsonl_stream = await stream(HttpRequest("GET", "/streams/jsonl_basic"))
    messages = []
    async for s in jsonl_stream:
        messages.append(s)
    assert messages == [
        {"msg": "this is a message"},
        {"msg": "this is another message"},
        {"msg": "this is a third message"},
        {"msg": "this is a fourth message"},
    ]


@pytest.mark.asyncio
async def test_stream_jsonl_no_final_line_separator(stream):
    jsonl_stream = await stream(HttpRequest("GET", "/streams/jsonl_no_final_line_separator"))
    async for s in jsonl_stream:
        assert s == {"msg": "this is a message"}


@pytest.mark.asyncio
async def test_stream_jsonl_broken_up_data(stream):
    jsonl_stream = await stream(HttpRequest("GET", "/streams/jsonl_broken_up_data"))
    messages = []
    async for s in jsonl_stream:
        messages.append(s)
    assert messages == [
        {"msg": "this is a third message"},
        {"msg": "this is a fourth message"},
    ]


@pytest.mark.asyncio
async def test_stream_jsonl_next(stream):
    jsonl_stream = await stream(HttpRequest("GET", "/streams/jsonl_basic"))
    message = await anext(jsonl_stream)
    assert message == {"msg": "this is a message"}
    message = await anext(jsonl_stream)
    assert message == {"msg": "this is another message"}
    message = await anext(jsonl_stream)
    assert message == {"msg": "this is a third message"}
    message = await anext(jsonl_stream)
    assert message == {"msg": "this is a fourth message"}

    with pytest.raises(StopAsyncIteration):
        await anext(jsonl_stream)
