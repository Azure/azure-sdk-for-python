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
