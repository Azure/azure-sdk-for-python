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

import json

import pytest

from corehttp.rest import HttpRequest
from corehttp.streaming import AsyncStream, AsyncJSONLDecoder


@pytest.fixture
def deserialization_callback():
    def _callback(model_json):
        return model_json

    return _callback


@pytest.fixture
def stream(client, deserialization_callback):
    async def _callback(request, **kwargs):
        http_response = await client.send_request(request=request, stream=True)
        return AsyncStream(
            deserialization_callback=deserialization_callback, response=http_response, decoder=AsyncJSONLDecoder()
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
async def test_stream_jsonl_multiple_kv(stream):
    jsonl_stream = await stream(HttpRequest("GET", "/streams/jsonl_multiple_kv"))
    messages = []
    async for s in jsonl_stream:
        messages.append(s)
    assert messages == [
        {"msg": "this is a hello world message", "planet": {"earth": "hello earth", "mars": "hello mars"}},
        {"msg": "this is a hello world message", "planet": {"venus": "hello venus", "jupiter": "hello jupiter"}},
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
        {"msg": "this is a first message"},
        {"msg": "this is a second message"},
    ]


@pytest.mark.asyncio
async def test_stream_jsonl_broken_up_data_cr(stream):
    jsonl_stream = await stream(HttpRequest("GET", "/streams/jsonl_broken_up_data_cr"))
    messages = []
    async for s in jsonl_stream:
        messages.append(s)
    assert messages == [
        {"msg": "this is a first message"},
        {"msg": "this is a second message"},
    ]


@pytest.mark.asyncio
async def test_stream_jsonl_next(stream):
    jsonl_stream = await stream(HttpRequest("GET", "/streams/jsonl_basic"))
    message = await jsonl_stream.__anext__()
    assert message == {"msg": "this is a message"}
    message = await jsonl_stream.__anext__()
    assert message == {"msg": "this is another message"}
    message = await jsonl_stream.__anext__()
    assert message == {"msg": "this is a third message"}
    message = await jsonl_stream.__anext__()
    assert message == {"msg": "this is a fourth message"}

    with pytest.raises(StopAsyncIteration):
        await jsonl_stream.__anext__()


@pytest.mark.asyncio
async def test_stream_jsonl_context_manager(stream):
    jsonl_stream = await stream(HttpRequest("GET", "/streams/jsonl_basic"))
    async with jsonl_stream as streaming:
        async for _ in streaming:
            break
    assert streaming._response.is_closed


@pytest.mark.asyncio
async def test_stream_jsonl_invalid_data(stream):
    jsonl_stream = await stream(HttpRequest("GET", "/streams/jsonl_invalid_data"))

    with pytest.raises(json.decoder.JSONDecodeError):
        async for _ in jsonl_stream:
            ...


@pytest.mark.asyncio
async def test_stream_jsonl_escaped_newline_data(stream):
    jsonl_stream = await stream(HttpRequest("GET", "/streams/jsonl_escaped_newline_data"))

    async for s in jsonl_stream:
        assert s == {"msg": "this is a...\nmessage"}


@pytest.mark.asyncio
async def test_stream_jsonl_escaped_broken_newline_data(stream):
    jsonl_stream = await stream(HttpRequest("GET", "/streams/jsonl_escaped_broken_newline_data"))
    messages = []
    async for s in jsonl_stream:
        messages.append(s)
    assert messages == [
        {"msg": "this is a first message"},
        {"msg": "\nthis is a second message"},
    ]


@pytest.mark.asyncio
async def test_stream_jsonl_incomplete_char(stream):
    jsonl_stream = await stream(HttpRequest("GET", "/streams/jsonl_broken_incomplete_char"))
    messages = []
    async for s in jsonl_stream:
        messages.append(s)
    assert messages == [
        {"msg": "this is a first message"},
        {"msg": "𝜋this is a second message𝜋"},
        {"msg": "this is a third message"},
    ]


@pytest.mark.asyncio
async def test_stream_jsonl_list(stream):
    jsonl_stream = await stream(HttpRequest("GET", "/streams/jsonl_list"))
    messages = []
    async for s in jsonl_stream:
        messages.append(s)
    assert messages == [
        ["this", "is", "a", "first", "message"],
        ["this", "is", "a", "second", "message"],
        ["this", "is", "a", "third", "message"],
    ]


@pytest.mark.asyncio
async def test_stream_jsonl_string(stream):
    jsonl_stream = await stream(HttpRequest("GET", "/streams/jsonl_string"))
    messages = []
    async for s in jsonl_stream:
        messages.append(s)
    assert messages == [
        "this",
        "is",
        "a",
        "message",
    ]
