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

@errors_api.route('/short-data', methods=['GET'])
def get_short_data():
    response = Response(b"X" * 4, status=200)
    response.automatically_set_content_length = False
    response.headers["Content-Length"] = "8"
    return response

@errors_api.route('/non-odatav4-body', methods=['GET'])
def get_non_odata_v4_response_body():
    return Response(
        '{"code": 400, "error": {"global": ["MY-ERROR-MESSAGE-THAT-IS-COMING-FROM-THE-API"]}}',
        status=400
    )

@errors_api.route('/malformed-json', methods=['GET'])
def get_malformed_json():
    return Response(
        '{"code": 400, "error": {"global": ["MY-ERROR-MESSAGE-THAT-IS-COMING-FROM-THE-API"]',
        status=400
    )

@errors_api.route('/text', methods=['GET'])
def get_text_body():
    return Response(
        'I am throwing an error',
        status=400
    )

@errors_api.route('/odatav4', methods=['GET'])
def get_odatav4():
    return Response(
        '{"error": {"code": "501", "message": "Unsupported functionality", "target": "query", "details": [{"code": "301", "target": "$search", "message": "$search query option not supported"}], "innererror": {"trace": [], "context": {}}}}',
        status=400
    )
