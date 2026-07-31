# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import gzip
import tempfile

from flask import (
    Response,
    Blueprint,
    request,
)

streams_api = Blueprint("streams_api", __name__)


class StreamingBody:
    def __iter__(self):
        yield b"Hello, "
        yield b"world!"


def streaming_body():
    yield b"Hello, "
    yield b"world!"


def stream_json_error():
    yield '{"error": {"code": "BadRequest", '
    yield ' "message": "You made a bad request"}}'


def streaming_test():
    yield b"test"


def stream_compressed_header_error():
    yield b"test"


@streams_api.route("/basic", methods=["GET"])
def basic():
    return Response(streaming_body(), status=200)


@streams_api.route("/iterable", methods=["GET"])
def iterable():
    return Response(StreamingBody(), status=200)


@streams_api.route("/error", methods=["GET"])
def error():
    return Response(stream_json_error(), status=400)


@streams_api.route("/string", methods=["GET"])
def string():
    return Response(streaming_test(), status=200, mimetype="text/plain")


@streams_api.route("/plain_header", methods=["GET"])
def plain_header():
    return Response(streaming_test(), status=200, mimetype="text/plain", headers={"Content-Encoding": "gzip"})


@streams_api.route("/compressed_no_header", methods=["GET"])
def compressed_no_header():
    return Response(compressed_stream(), status=300)


@streams_api.route("/compressed_header", methods=["GET"])
def compressed_header():
    return Response(compressed_stream(), status=200, headers={"Content-Encoding": "gzip"})


@streams_api.route("/compressed", methods=["GET"])
def compressed():
    return Response(stream_compressed_header_error(), status=300, headers={"Content-Encoding": "gzip"})


def compressed_stream():
    with tempfile.TemporaryFile(mode="w+b") as f:
        gzf = gzip.GzipFile(mode="w+b", fileobj=f)
        gzf.write(b"test")
        gzf.flush()
        f.seek(0)
        yield f.read()


@streams_api.route("/decompress_header", methods=["GET"])
def decompress_header():
    return Response(compressed_stream(), status=200, headers={"Content-Encoding": "gzip"})


@streams_api.route("/upload", methods=["POST"])
def upload():
    chunk_size = 1024
    byte_content = b""
    while True:
        chunk = request.stream.read(chunk_size)
        if len(chunk) == 0:
            break
        byte_content += chunk
    return Response(byte_content, status=200)


def stream_jsonl_basic():
    data = [
        b'{"msg": "this is a message"}\n',
        b'{"msg": "this is another message"}\n',
        b'{"msg": "this is a third message"}\n{"msg": "this is a fourth message"}\n',
    ]
    yield from data


def stream_jsonl_multiple_kv():
    data = [
        b'{"msg": "this is a hello world message", "planet": {"earth": "hello earth", "mars": "hello mars"}}\n',
        b'{"msg": "this is a hello world message", "planet": {"venus": "hello venus", "jupiter": "hello jupiter"}}\n',
    ]
    yield from data


def stream_jsonl_no_final_line_separator():
    data = b'{"msg": "this is a message"}'
    yield data


def stream_jsonl_broken_up_data():
    data = [b'{"msg": "this is a first message"}\n{"msg": ', b'"this is a second message"}\n']
    yield from data


def stream_jsonl_broken_up_data_cr():
    data = [b'{"msg": "this is a first message"}\r\n{"msg": ', b'"this is a second message"}\r\n']
    yield from data


def stream_jsonl_invalid_data():
    data = [b'{"msg": "this is a third m']
    yield from data


def stream_jsonl_escaped_newline_data():
    data = b'{"msg": "this is a...\\nmessage"}\n'
    yield data


def stream_jsonl_escaped_broken_newline_data():
    data = [b'{"msg": "this is a first message"}\n{"msg": "\\n', b'this is a second message"}\n']
    yield from data


def stream_jsonl_broken_incomplete_char():
    data = [
        b'{"msg": "this is a first message"}\n{"msg": "\xf0\x9d',
        b"\x9c\x8bthis is a second message\xf0\x9d",
        b'\x9c\x8b"}',
        b'\n{"msg": "this is a third message"}',
    ]
    yield from data


def stream_jsonl_list():
    data = [
        b'["this", "is", "a", "first", "message"]\n',
        b'["this", "is", "a", "second", "message"]\n',
        b'["this", "is", "a", "third", "message"]\n',
    ]
    yield from data


def stream_jsonl_string():
    data = [
        b'"this"\n',
        b'"is"\n',
        b'"a"\n',
        b'"message"\n',
    ]
    yield from data


def stream_jsonl_unicode_line_boundary():
    # \u2028 (line separator), \u2029 (paragraph separator) and \x85 (NEL) are Unicode
    # boundaries that str.splitlines() splits on, but JSONL only delimits records on \n.
    # Each record embeds those characters inside its JSON string value and records are
    # delimited by a real \n, so they must not be split mid-record.
    data = [
        '{"msg": "first\u2028line\u2029boundary\u0085record"}\n'.encode("utf-8"),
        '{"msg": "second\u2028line\u2029boundary\u0085record"}\n'.encode("utf-8"),
    ]
    yield from data


@streams_api.route("/jsonl_basic", methods=["GET"])
def jsonl_basic():
    return Response(stream_jsonl_basic(), status=200, headers={"Content-Type": "application/jsonl"})


@streams_api.route("/jsonl_multiple_kv", methods=["GET"])
def jsonl_multiple_kv():
    return Response(stream_jsonl_multiple_kv(), status=200, headers={"Content-Type": "application/jsonl"})


@streams_api.route("/jsonl_no_final_line_separator", methods=["GET"])
def jsonl_no_final_line_separator():
    return Response(stream_jsonl_no_final_line_separator(), status=200, headers={"Content-Type": "application/jsonl"})


@streams_api.route("/jsonl_broken_up_data", methods=["GET"])
def jsonl_broken_up_data():
    return Response(stream_jsonl_broken_up_data(), status=200, headers={"Content-Type": "application/jsonl"})


@streams_api.route("/jsonl_broken_up_data_cr", methods=["GET"])
def jsonl_broken_up_data_cr():
    return Response(stream_jsonl_broken_up_data_cr(), status=200, headers={"Content-Type": "application/jsonl"})


@streams_api.route("/jsonl_invalid_data", methods=["GET"])
def jsonl_invalid_data():
    return Response(stream_jsonl_invalid_data(), status=200, headers={"Content-Type": "application/jsonl"})


@streams_api.route("/jsonl_escaped_newline_data", methods=["GET"])
def jsonl_escaped_newline_data():
    return Response(stream_jsonl_escaped_newline_data(), status=200, headers={"Content-Type": "application/jsonl"})


@streams_api.route("/jsonl_escaped_broken_newline_data", methods=["GET"])
def jsonl_escaped_broken_newline_data():
    return Response(
        stream_jsonl_escaped_broken_newline_data(), status=200, headers={"Content-Type": "application/jsonl"}
    )


@streams_api.route("/jsonl_broken_incomplete_char", methods=["GET"])
def jsonl_broken_incomplete_char():
    return Response(stream_jsonl_broken_incomplete_char(), status=200, headers={"Content-Type": "application/jsonl"})


@streams_api.route("/jsonl_list", methods=["GET"])
def json_list():
    return Response(stream_jsonl_list(), status=200, headers={"Content-Type": "application/jsonl"})


@streams_api.route("/jsonl_string", methods=["GET"])
def json_string():
    return Response(stream_jsonl_string(), status=200, headers={"Content-Type": "application/jsonl"})


@streams_api.route("/jsonl_unicode_line_boundary", methods=["GET"])
def jsonl_unicode_line_boundary():
    return Response(stream_jsonl_unicode_line_boundary(), status=200, headers={"Content-Type": "application/jsonl"})


def stream_sse_basic():
    data = [
        b"data: hello\n\n",
        b"data: world\n\n",
    ]
    yield from data


def stream_sse_multiline_data():
    # Multiple data lines in one event are joined with "\n".
    data = [
        b"event: greeting\n",
        b"data: line one\n",
        b"data: line two\n",
        b"\n",
    ]
    yield from data


def stream_sse_comments_and_fields():
    # Comment lines (":"-prefixed) are ignored; one leading space after ":" is stripped.
    data = [
        b": this is a comment\n",
        b"event: update\n",
        b"data: payload\n",
        b"\n",
    ]
    yield from data


def stream_sse_crlf():
    # SSE allows CRLF line separators.
    data = [
        b"data: crlf-line\r\n\r\n",
    ]
    yield from data


def stream_sse_lone_cr():
    # SSE allows a lone CR as a line separator.
    data = [
        b"data: cr-line\r\r",
    ]
    yield from data


def stream_sse_broken_up():
    # An event split across multiple chunks, including a CRLF split at the chunk boundary.
    data = [
        b"data: hel",
        b"lo\r",
        b"\n\r\n",
    ]
    yield from data


def stream_sse_id_and_retry():
    data = [
        b"id: 42\n",
        b"retry: 3000\n",
        b"data: first\n",
        b"\n",
        b"data: second\n",
        b"\n",
    ]
    yield from data


@streams_api.route("/sse_basic", methods=["GET"])
def sse_basic():
    return Response(stream_sse_basic(), status=200, headers={"Content-Type": "text/event-stream"})


@streams_api.route("/sse_multiline_data", methods=["GET"])
def sse_multiline_data():
    return Response(stream_sse_multiline_data(), status=200, headers={"Content-Type": "text/event-stream"})


@streams_api.route("/sse_comments_and_fields", methods=["GET"])
def sse_comments_and_fields():
    return Response(stream_sse_comments_and_fields(), status=200, headers={"Content-Type": "text/event-stream"})


@streams_api.route("/sse_crlf", methods=["GET"])
def sse_crlf():
    return Response(stream_sse_crlf(), status=200, headers={"Content-Type": "text/event-stream"})


@streams_api.route("/sse_lone_cr", methods=["GET"])
def sse_lone_cr():
    return Response(stream_sse_lone_cr(), status=200, headers={"Content-Type": "text/event-stream"})


@streams_api.route("/sse_broken_up", methods=["GET"])
def sse_broken_up():
    return Response(stream_sse_broken_up(), status=200, headers={"Content-Type": "text/event-stream"})


@streams_api.route("/sse_id_and_retry", methods=["GET"])
def sse_id_and_retry():
    return Response(stream_sse_id_and_retry(), status=200, headers={"Content-Type": "text/event-stream"})
