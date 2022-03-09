# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from copy import copy
from flask import (
    Response,
    Blueprint,
    request,
)
from .helpers import assert_with_message

multipart_api = Blueprint('multipart_api', __name__)

multipart_header_start = "multipart/form-data; boundary="

# NOTE: the flask behavior is different for aiohttp and requests
# in requests, we see the file content through request.form
# in aiohttp, we see the file through request.files

@multipart_api.route('/basic', methods=['POST'])
def basic():
    assert_with_message("content type", multipart_header_start, request.content_type[:len(multipart_header_start)])
    if request.files:
        # aiohttp
        assert_with_message("content length", 258, request.content_length)
        assert_with_message("num files", 1, len(request.files))
        assert_with_message("has file named fileContent", True, bool(request.files.get('fileContent')))
        file_content = request.files['fileContent']
        assert_with_message("file content type", "application/octet-stream", file_content.content_type)
        assert_with_message("file content length", 14, file_content.content_length)
        assert_with_message("filename", "fileContent", file_content.filename)
        assert_with_message("has content disposition header", True, bool(file_content.headers.get("Content-Disposition")))
        assert_with_message(
            "content disposition",
            'form-data; name="fileContent"; filename="fileContent"; filename*=utf-8\'\'fileContent',
            file_content.headers["Content-Disposition"]
        )
    elif request.form:
        # requests
        assert_with_message("content length", 184, request.content_length)
        assert_with_message("fileContent", "<file content>", request.form["fileContent"])
    else:
        return Response(status=400)  # should be either of these
    return Response(status=200)

@multipart_api.route('/data-and-files', methods=['POST'])
def data_and_files():
    assert_with_message("content type", multipart_header_start, request.content_type[:len(multipart_header_start)])
    assert_with_message("message", "Hello, world!", request.form["message"])
    assert_with_message("message", "<file content>", request.form["fileContent"])
    return Response(status=200)

@multipart_api.route('/data-and-files-tuple', methods=['POST'])
def data_and_files_tuple():
    assert_with_message("content type", multipart_header_start, request.content_type[:len(multipart_header_start)])
    assert_with_message("message", ["abc"], request.form["message"])
    assert_with_message("message", ["<file content>"], request.form["fileContent"])
    return Response(status=200)

@multipart_api.route('/non-seekable-filelike', methods=['POST'])
def non_seekable_filelike():
    assert_with_message("content type", multipart_header_start, request.content_type[:len(multipart_header_start)])
    if request.files:
        # aiohttp
        len_files = len(request.files)
        assert_with_message("num files", 1, len_files)
        # assert_with_message("content length", 258, request.content_length)
        assert_with_message("num files", 1, len(request.files))
        assert_with_message("has file named file", True, bool(request.files.get('file')))
        file = request.files['file']
        assert_with_message("file content type", "application/octet-stream", file.content_type)
        assert_with_message("file content length", 14, file.content_length)
        assert_with_message("filename", "file", file.filename)
        assert_with_message("has content disposition header", True, bool(file.headers.get("Content-Disposition")))
        assert_with_message(
            "content disposition",
            'form-data; name="fileContent"; filename="fileContent"; filename*=utf-8\'\'fileContent',
            file.headers["Content-Disposition"]
        )
    elif request.form:
        # requests
        assert_with_message("num files", 1, len(request.form))
    else:
        return Response(status=400)
    return Response(status=200)

@multipart_api.route('/request', methods=["POST"])
def multipart_request():
    body_as_str = (
        "--batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed\r\n"
        "Content-Type: application/http\r\n"
        "Content-ID: 0\r\n"
        "\r\n"
        "HTTP/1.1 202 Accepted\r\n"
        "x-ms-request-id: 778fdc83-801e-0000-62ff-0334671e284f\r\n"
        "x-ms-version: 2018-11-09\r\n"
        "\r\n"
        "--batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed\r\n"
        "Content-Type: application/http\r\n"
        "Content-ID: 2\r\n"
        "\r\n"
        "HTTP/1.1 404 The specified blob does not exist.\r\n"
        "x-ms-error-code: BlobNotFound\r\n"
        "x-ms-request-id: 778fdc83-801e-0000-62ff-0334671e2852\r\n"
        "x-ms-version: 2018-11-09\r\n"
        "Content-Length: 216\r\n"
        "Content-Type: application/xml\r\n"
        "\r\n"
        '<?xml version="1.0" encoding="utf-8"?>\r\n'
        "<Error><Code>BlobNotFound</Code><Message>The specified blob does not exist.\r\n"
        "RequestId:778fdc83-801e-0000-62ff-0334671e2852\r\n"
        "Time:2018-06-14T16:46:54.6040685Z</Message></Error>\r\n"
        "--batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed--"
    )
    return Response(body_as_str.encode('ascii'), content_type="multipart/mixed; boundary=batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed")

