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

from azure.core.rest import HttpRequest
from azure.core.streaming import Stream
from azure.core.streaming._jsonl import JSONLDecoder
from azure.core.streaming._sse import SSEDecoder, ServerSentEvent


@pytest.fixture
def deserialization_callback():
    def _callback(response, model_json):
        return model_json

    return _callback


@pytest.fixture
def stream(client, deserialization_callback):
    def _callback(request, **kwargs):
        http_response = client.send_request(request=request, stream=True)
        return Stream(deserialization_callback=deserialization_callback, response=http_response)

    return _callback


@pytest.fixture
def sse_stream(client, deserialization_callback):
    def _callback(request, **kwargs):
        http_response = client.send_request(request=request, stream=True)
        return Stream(deserialization_callback=deserialization_callback, response=http_response)

    return _callback


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
def test_stream_infers_decoder_from_content_type(content_type, payload, expected):
    class Response:
        headers = {"Content-Type": content_type}

        def iter_bytes(self):
            return iter([payload])

        def close(self):
            pass

    stream = Stream(response=Response(), deserialization_callback=lambda _response, event: event)
    assert list(stream) == expected


def test_stream_explicit_decoder_overrides_content_type():
    class Response:
        headers = {"Content-Type": "text/event-stream"}

        def iter_bytes(self):
            return iter([b'{"message": "hello"}\n'])

        def close(self):
            pass

    stream = Stream(
        response=Response(),
        decoder=JSONLDecoder(),
        deserialization_callback=lambda _response, event: event,
    )
    assert list(stream) == [{"message": "hello"}]


def test_stream_jsonl_basic(stream):
    jsonl_stream = stream(HttpRequest("GET", "/streams/jsonl_basic"))
    messages = []
    for s in jsonl_stream:
        messages.append(s)
    assert messages == [
        {"msg": "this is a message"},
        {"msg": "this is another message"},
        {"msg": "this is a third message"},
        {"msg": "this is a fourth message"},
    ]


def test_stream_jsonl_multiple_kv(stream):
    jsonl_stream = stream(HttpRequest("GET", "/streams/jsonl_multiple_kv"))
    messages = []
    for s in jsonl_stream:
        messages.append(s)
    assert messages == [
        {"msg": "this is a hello world message", "planet": {"earth": "hello earth", "mars": "hello mars"}},
        {"msg": "this is a hello world message", "planet": {"venus": "hello venus", "jupiter": "hello jupiter"}},
    ]


def test_stream_jsonl_no_final_line_separator(stream):
    jsonl_stream = stream(HttpRequest("GET", "/streams/jsonl_no_final_line_separator"))
    for s in jsonl_stream:
        assert s == {"msg": "this is a message"}


def test_stream_jsonl_broken_up_data(stream):
    jsonl_stream = stream(HttpRequest("GET", "/streams/jsonl_broken_up_data"))
    messages = []
    for s in jsonl_stream:
        messages.append(s)
    assert messages == [
        {"msg": "this is a first message"},
        {"msg": "this is a second message"},
    ]


def test_stream_jsonl_broken_up_data_cr(stream):
    jsonl_stream = stream(HttpRequest("GET", "/streams/jsonl_broken_up_data_cr"))
    messages = []
    for s in jsonl_stream:
        messages.append(s)
    assert messages == [
        {"msg": "this is a first message"},
        {"msg": "this is a second message"},
    ]


def test_stream_jsonl_next(stream):
    jsonl_stream = stream(HttpRequest("GET", "/streams/jsonl_basic"))
    message = next(jsonl_stream)
    assert message == {"msg": "this is a message"}
    message = next(jsonl_stream)
    assert message == {"msg": "this is another message"}
    message = next(jsonl_stream)
    assert message == {"msg": "this is a third message"}
    message = next(jsonl_stream)
    assert message == {"msg": "this is a fourth message"}

    with pytest.raises(StopIteration):
        next(jsonl_stream)


def test_stream_jsonl_context_manager(stream):
    jsonl_stream = stream(HttpRequest("GET", "/streams/jsonl_basic"))
    with jsonl_stream as streaming:
        for _ in streaming:
            break
    assert streaming._response.is_closed


def test_stream_jsonl_invalid_data(stream):
    jsonl_stream = stream(HttpRequest("GET", "/streams/jsonl_invalid_data"))

    with pytest.raises(json.decoder.JSONDecodeError):
        for _ in jsonl_stream:
            ...


def test_stream_jsonl_escaped_newline_data(stream):
    jsonl_stream = stream(HttpRequest("GET", "/streams/jsonl_escaped_newline_data"))

    for s in jsonl_stream:
        assert s == {"msg": "this is a...\nmessage"}


def test_stream_jsonl_escaped_broken_newline_data(stream):
    jsonl_stream = stream(HttpRequest("GET", "/streams/jsonl_escaped_broken_newline_data"))
    messages = []
    for s in jsonl_stream:
        messages.append(s)
    assert messages == [
        {"msg": "this is a first message"},
        {"msg": "\nthis is a second message"},
    ]


def test_stream_jsonl_incomplete_char(stream):
    jsonl_stream = stream(HttpRequest("GET", "/streams/jsonl_broken_incomplete_char"))
    messages = []
    for s in jsonl_stream:
        messages.append(s)
    assert messages == [
        {"msg": "this is a first message"},
        {"msg": "𝜋this is a second message𝜋"},
        {"msg": "this is a third message"},
    ]


def test_stream_jsonl_list(stream):
    jsonl_stream = stream(HttpRequest("GET", "/streams/jsonl_list"))
    messages = []
    for s in jsonl_stream:
        messages.append(s)
    assert messages == [
        ["this", "is", "a", "first", "message"],
        ["this", "is", "a", "second", "message"],
        ["this", "is", "a", "third", "message"],
    ]


def test_stream_jsonl_string(stream):
    jsonl_stream = stream(HttpRequest("GET", "/streams/jsonl_string"))
    messages = []
    for s in jsonl_stream:
        messages.append(s)
    assert messages == [
        "this",
        "is",
        "a",
        "message",
    ]


def test_stream_jsonl_unicode_line_boundary(stream):
    # Ensure records are only split on \n and not on other Unicode line boundaries
    # (\u2028, \u2029, \x85) that str.splitlines() would split on.
    jsonl_stream = stream(HttpRequest("GET", "/streams/jsonl_unicode_line_boundary"))
    messages = []
    for s in jsonl_stream:
        messages.append(s)
    assert messages == [
        {"msg": "first\u2028line\u2029boundary\u0085record"},
        {"msg": "second\u2028line\u2029boundary\u0085record"},
    ]


def test_stream_sse_basic(sse_stream):
    events = list(sse_stream(HttpRequest("GET", "/streams/sse_basic")))
    assert events == [
        ServerSentEvent(event="message", data="hello", id=""),
        ServerSentEvent(event="message", data="world", id=""),
    ]


def test_stream_sse_multiline_data(sse_stream):
    events = list(sse_stream(HttpRequest("GET", "/streams/sse_multiline_data")))
    assert events == [ServerSentEvent(event="greeting", data="line one\nline two")]


def test_stream_sse_comments_and_fields(sse_stream):
    events = list(sse_stream(HttpRequest("GET", "/streams/sse_comments_and_fields")))
    assert events == [ServerSentEvent(event="update", data="payload")]


def test_stream_sse_crlf(sse_stream):
    events = list(sse_stream(HttpRequest("GET", "/streams/sse_crlf")))
    assert events == [ServerSentEvent(event="message", data="crlf-line")]


def test_stream_sse_lone_cr(sse_stream):
    events = list(sse_stream(HttpRequest("GET", "/streams/sse_lone_cr")))
    assert events == [ServerSentEvent(event="message", data="cr-line")]


def test_stream_sse_broken_up(sse_stream):
    # An event split across chunks (with a CRLF split at a chunk boundary) yields a
    # single event and no spurious empty event.
    events = list(sse_stream(HttpRequest("GET", "/streams/sse_broken_up")))
    assert events == [ServerSentEvent(event="message", data="hello")]


def test_stream_sse_id_and_retry(sse_stream):
    events = list(sse_stream(HttpRequest("GET", "/streams/sse_id_and_retry")))
    # id and retry persist across subsequent events until overridden.
    assert events == [
        ServerSentEvent(event="message", data="first", id="42", retry=3000),
        ServerSentEvent(event="message", data="second", id="42", retry=3000),
    ]


def test_stream_sse_bom(sse_stream):
    # A single leading UTF-8 BOM is ignored, so the first field is not corrupted.
    events = list(sse_stream(HttpRequest("GET", "/streams/sse_bom")))
    assert events == [ServerSentEvent(event="message", data="with-bom")]


def test_stream_sse_bom_split(sse_stream):
    events = list(sse_stream(HttpRequest("GET", "/streams/sse_bom_split")))
    assert events == [ServerSentEvent(event="message", data="split-bom")]


def test_stream_sse_invalid_utf8(sse_stream):
    # Invalid UTF-8 becomes U+FFFD instead of crashing the stream.
    events = list(sse_stream(HttpRequest("GET", "/streams/sse_invalid_utf8")))
    assert events == [ServerSentEvent(event="message", data="caf\ufffd")]


def test_stream_sse_oversized_retry_ignored():
    # A retry value of all ASCII digits but longer than CPython's int-string
    # conversion limit must be ignored per spec, not crash the stream.
    payload = b"retry:" + b"1" * 5000 + b"\ndata:hello\n\n"
    events = list(SSEDecoder().iter_events(iter([payload])))
    assert events == [ServerSentEvent(event="message", data="hello", retry=None)]


# A payload exercising the trickiest parser boundaries: CRLF and LF line
# endings, a comment, multiple data lines, id/retry fields, and multibyte
# UTF-8 characters (é, 世界) whose bytes may be split across chunk boundaries.
_SSE_SWEEP_PAYLOAD = (
    b"data: first\r\n"
    b"\r\n"
    b": a comment\n"
    b"event: greeting\n"
    b"data: caf\xc3\xa9\n"
    b"data: \xe4\xb8\x96\xe7\x95\x8c\n"
    b"id: 7\n"
    b"retry: 1500\n"
    b"\n"
)

_SSE_SWEEP_EXPECTED = [
    ServerSentEvent(event="message", data="first"),
    ServerSentEvent(event="greeting", data="caf\u00e9\n\u4e16\u754c", id="7", retry=1500),
]


@pytest.mark.parametrize("chunk_size", [1, 2, 3, 5, 7, 13, 512])
def test_stream_sse_chunk_boundary_sweep(chunk_size):
    # Replaying the same payload at many chunk sizes (down to a single byte)
    # ensures the incremental parser handles line separators and multibyte
    # UTF-8 sequences split across arbitrary chunk boundaries.
    chunks = [_SSE_SWEEP_PAYLOAD[i : i + chunk_size] for i in range(0, len(_SSE_SWEEP_PAYLOAD), chunk_size)]
    events = list(SSEDecoder().iter_events(iter(chunks)))
    assert events == _SSE_SWEEP_EXPECTED
