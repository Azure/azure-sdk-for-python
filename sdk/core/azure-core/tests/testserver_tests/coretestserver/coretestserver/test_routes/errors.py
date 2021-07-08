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

errors_api = Blueprint('errors_api', __name__)

@errors_api.route('/403', methods=['GET'])
def get_403():
    return Response(status=403)

@errors_api.route('/500', methods=['GET'])
def get_500():
    return Response(status=500)

@errors_api.route('/stream', methods=['GET'])
def get_stream():
    class StreamingBody:
        def __iter__(self):
            yield b"Hello, "
            yield b"world!"
    return Response(StreamingBody(), status=500)
