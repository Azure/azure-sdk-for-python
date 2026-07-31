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
from azure.core.streaming import Stream, JSONLDecoder, SSEDecoder, ServerSentEvent


@pytest.fixture
def deserialization_callback():
    def _callback(response, model_json):
        return model_json

    return _callback


@pytest.fixture
def stream(client, deserialization_callback):
    def _callback(request, **kwargs):
        http_response = client.send_request(request=request, stream=True)
        return Stream(deserialization_callback=deserialization_callback, response=http_response, decoder=JSONLDecoder())

    return _callback


@pytest.fixture
def sse_stream(client, deserialization_callback):
    def _callback(request, **kwargs):
        http_response = client.send_request(request=request, stream=True)
        return Stream(deserialization_callback=deserialization_callback, response=http_response, decoder=SSEDecoder())

    return _callback


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
        ServerSentEvent(event="message", data="hello"),
        ServerSentEvent(event="message", data="world"),
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
