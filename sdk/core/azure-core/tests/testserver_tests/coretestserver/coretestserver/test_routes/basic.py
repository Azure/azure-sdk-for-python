# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from flask import (
    Response,
    Blueprint,
    request,
)
from .helpers import jsonify, get_dict

basic_api = Blueprint('basic_api', __name__)

@basic_api.route('/string', methods=['GET'])
def string():
    return Response(
        "Hello, world!", status=200, mimetype="text/plain"
    )

@basic_api.route('/lines', methods=['GET'])
def lines():
    return Response(
        "Hello,\nworld!", status=200, mimetype="text/plain"
    )

@basic_api.route("/bytes", methods=['GET'])
def bytes():
    return Response(
        "Hello, world!".encode(), status=200, mimetype="text/plain"
    )

@basic_api.route("/html", methods=['GET'])
def html():
    return Response(
        "<html><body>Hello, world!</html></body>", status=200, mimetype="text/html"
    )

@basic_api.route("/json", methods=['GET'])
def json():
    return Response(
        '{"greeting": "hello", "recipient": "world"}', status=200, mimetype="application/json"
    )

@basic_api.route("/complicated-json", methods=['POST'])
def complicated_json():
    # thanks to Sean Kane for this test!
    assert request.json['EmptyByte'] == ''
    assert request.json['EmptyUnicode'] == ''
    assert request.json['SpacesOnlyByte'] == '   '
    assert request.json['SpacesOnlyUnicode'] == '   '
    assert request.json['SpacesBeforeByte'] == '   Text'
    assert request.json['SpacesBeforeUnicode'] == '   Text'
    assert request.json['SpacesAfterByte'] == 'Text   '
    assert request.json['SpacesAfterUnicode'] == 'Text   '
    assert request.json['SpacesBeforeAndAfterByte'] == '   Text   '
    assert request.json['SpacesBeforeAndAfterUnicode'] == '   Text   '
    assert request.json[u'啊齄丂狛'] == u'ꀕ'
    assert request.json['RowKey'] == 'test2'
    assert request.json[u'啊齄丂狛狜'] == 'hello'
    assert request.json["singlequote"] == "a''''b"
    assert request.json["doublequote"] == 'a""""b'
    assert request.json["None"] == None

    return Response(status=200)

@basic_api.route("/headers", methods=['GET'])
def headers():
    return Response(
        status=200,
        headers={
            "lowercase-header": "lowercase",
            "ALLCAPS-HEADER": "ALLCAPS",
            "CamelCase-Header": "camelCase",
        }
    )

@basic_api.route("/anything", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "TRACE"])
def anything():
    return jsonify(
        get_dict(
            "url",
            "args",
            "headers",
            "origin",
            "method",
            "form",
            "data",
            "files",
            "json",
        )
    )
