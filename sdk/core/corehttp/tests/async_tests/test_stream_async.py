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
from corehttp.streaming import AsyncStream
from corehttp.streaming._sse import AsyncSSEDecoder, ServerSentEvent


@pytest.fixture
def deserialization_callback():
    def _callback(response, model_json):
        return model_json

    return _callback


@pytest.fixture
def stream(client, deserialization_callback):
    async def _callback(request, **kwargs):
        http_response = await client.send_request(request=request, stream=True)
        return AsyncStream(deserialization_callback=deserialization_callback, response=http_response)

    return _callback


@pytest.fixture
def sse_stream(client, deserialization_callback):
    async def _callback(request, **kwargs):
        http_response = await client.send_request(request=request, stream=True)
        return AsyncStream(deserialization_callback=deserialization_callback, response=http_response)

    return _callback


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "content_type,payload,expected",
    [
        ("application/jsonl", b'{"message": "hello"}\n', [{"message": "hello"}]),
        (
            "text/event-stream; charset=utf-8",
            b"data: hello\n\n",
            [ServerSentEvent(event="message", data="hello")],
        ),
    ],
)
async def test_stream_infers_decoder_from_content_type(content_type, payload, expected):
    class Response:
        headers = {"Content-Type": content_type}

        async def iter_bytes(self):
            yield payload

        async def close(self):
            pass

    stream = AsyncStream(response=Response(), deserialization_callback=lambda _response, event: event)
    assert [event async for event in stream] == expected


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


@pytest.mark.asyncio
async def test_stream_jsonl_unicode_line_boundary(stream):
    # Ensure records are only split on \n and not on other Unicode line boundaries
    # (\u2028, \u2029, \x85) that str.splitlines() would split on.
    jsonl_stream = await stream(HttpRequest("GET", "/streams/jsonl_unicode_line_boundary"))
    messages = []
    async for s in jsonl_stream:
        messages.append(s)
    assert messages == [
        {"msg": "first\u2028line\u2029boundary\u0085record"},
        {"msg": "second\u2028line\u2029boundary\u0085record"},
    ]


async def _collect(sse_stream, path):
    events = []
    stream = await sse_stream(HttpRequest("GET", path))
    async for event in stream:
        events.append(event)
    return events


@pytest.mark.asyncio
async def test_stream_sse_basic(sse_stream):
    events = await _collect(sse_stream, "/streams/sse_basic")
    assert events == [
        ServerSentEvent(event="message", data="hello", id=""),
        ServerSentEvent(event="message", data="world", id=""),
    ]


@pytest.mark.asyncio
async def test_stream_sse_multiline_data(sse_stream):
    events = await _collect(sse_stream, "/streams/sse_multiline_data")
    assert events == [ServerSentEvent(event="greeting", data="line one\nline two")]


@pytest.mark.asyncio
async def test_stream_sse_comments_and_fields(sse_stream):
    events = await _collect(sse_stream, "/streams/sse_comments_and_fields")
    assert events == [ServerSentEvent(event="update", data="payload")]


@pytest.mark.asyncio
async def test_stream_sse_crlf(sse_stream):
    events = await _collect(sse_stream, "/streams/sse_crlf")
    assert events == [ServerSentEvent(event="message", data="crlf-line")]


@pytest.mark.asyncio
async def test_stream_sse_lone_cr(sse_stream):
    events = await _collect(sse_stream, "/streams/sse_lone_cr")
    assert events == [ServerSentEvent(event="message", data="cr-line")]


@pytest.mark.asyncio
async def test_stream_sse_broken_up(sse_stream):
    events = await _collect(sse_stream, "/streams/sse_broken_up")
    assert events == [ServerSentEvent(event="message", data="hello")]


@pytest.mark.asyncio
async def test_stream_sse_id_and_retry(sse_stream):
    events = await _collect(sse_stream, "/streams/sse_id_and_retry")
    assert events == [
        ServerSentEvent(event="message", data="first", id="42", retry=3000),
        ServerSentEvent(event="message", data="second", id="42", retry=3000),
    ]


@pytest.mark.asyncio
async def test_stream_sse_bom(sse_stream):
    events = await _collect(sse_stream, "/streams/sse_bom")
    assert events == [ServerSentEvent(event="message", data="with-bom")]


@pytest.mark.asyncio
async def test_stream_sse_bom_split(sse_stream):
    events = await _collect(sse_stream, "/streams/sse_bom_split")
    assert events == [ServerSentEvent(event="message", data="split-bom")]


@pytest.mark.asyncio
async def test_stream_sse_invalid_utf8(sse_stream):
    events = await _collect(sse_stream, "/streams/sse_invalid_utf8")
    assert events == [ServerSentEvent(event="message", data="caf\ufffd")]


@pytest.mark.asyncio
async def test_stream_sse_oversized_retry_ignored():
    # A retry value of all ASCII digits but longer than CPython's int-string
    # conversion limit must be ignored per spec, not crash the stream.
    payload = b"retry:" + b"1" * 5000 + b"\ndata:hello\n\n"

    async def _bytes():
        yield payload

    events = [event async for event in AsyncSSEDecoder().aiter_events(_bytes())]
    assert events == [ServerSentEvent(event="message", data="hello", retry=None)]
