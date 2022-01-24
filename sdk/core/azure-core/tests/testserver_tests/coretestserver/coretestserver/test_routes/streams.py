# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from flask import (
    Response,
    Blueprint,
)

streams_api = Blueprint('streams_api', __name__)

class StreamingBody:
    def __iter__(self):
        yield b"Hello, "
        yield b"world!"


def streaming_body():
    yield b"Hello, "
    yield b"world!"

def stream_json_error():
    yield '{"error": {"code": "BadRequest", '
    yield' "message": "You made a bad request"}}'

def streaming_test():
    yield b"test"
    
def stream_compressed_header_error():
    yield b'test'

@streams_api.route('/basic', methods=['GET'])
def basic():
    return Response(streaming_body(), status=200)

@streams_api.route('/iterable', methods=['GET'])
def iterable():
    return Response(StreamingBody(), status=200)

@streams_api.route('/error', methods=['GET'])
def error():
    return Response(stream_json_error(), status=400)

@streams_api.route('/string', methods=['GET'])
def string():
    return Response(
        streaming_test(), status=200, mimetype="text/plain"
    )
    
@streams_api.route('/compressed', methods=['GET'])
def compressed():
    return Response(stream_compressed_header_error(), status=300, headers={"Content-Encoding": "gzip"})
    
