# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os
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

def stream_compress():
    file_path = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", "./files/test.tar.gz"))
    with open(file_path, "rb") as fd:
        yield fd.read()

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

@streams_api.route('/compress', methods=['GET'])
def compress():
    return Response(stream_compress(), status=200)
    
@streams_api.route('/compressed', methods=['GET'])
def compressed():
    return Response(stream_compressed_header_error(), status=300, headers={"Content-Encoding": "gzip"})
    
